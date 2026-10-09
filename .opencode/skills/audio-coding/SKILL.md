---
name: audio-coding
description: Arbeitsregeln, DSP-Erkenntnisse und Skripte für Audio-DSP-Portierung mit strikter C++/EEL2-Parität, LV2/JSFX-Doppelpfad, generierten Metadaten und ehrlicher Quellenarbeit. Nutzen, wenn an Green Stripe 76 oder vergleichbaren Audio-Projekten mit zwei Sprachpfaden, angehängten Ports, Preset-Bänken oder GUI-Assets gearbeitet wird.
license: MIT
metadata:
  audience: maintainers
  project: green-stripe-76
---

# Audio-Coding

## Wofür dieser Skill steht

Green Stripe 76 ist ein 1176-inspirierter Kompressor, der **denselben DSP in zwei
Sprachen** ausliefert: C++ hinter einer LV2-C-ABI und EEL2 in einem JSFX. Jede
Klangänderung gilt erst als fertig, wenn beide Pfade und alle Prüfungen
zusammenpassen. Aus dieser Doppelstruktur kommen die meisten Fehlerquellen.

## Nicht verhandelbare Regeln

| Regel | Warum |
|---|---|
| `data/parameters.json` und `data/model.json` sind normativ | Alles andere ist generiert; Handedits an TTL/JSFX gehen beim nächsten `generate.py` verloren |
| C++11, LV2-C-ABI, keine GUI-/JUCE-/WebView-Abhängigkeit im DSP | Plugin muss auf dem Zielgerät ohne UI-Laufzeit laden |
| Feedback **vor** dem Output abgreifen | Sonst verändert der Ausgang den GR-Verlauf und der Regler wird instabil |
| `run()`/`@sample`: keine Allokation, kein Dateizugriff, keine unbeschränkte Schleife | Realtime-Thread |
| Intern `double`, Ports `float` | Einheitliche Rechnung, geordnete Ausgabe |
| Kein `-ffast-math`, `-ffp-contract=off` | Sonst ist Float-Parität Zufall |
| DSP rechnet intern in double, Audioports in float | siehe oben |
| Keine implizite Auto-Makeup-Funktion, kein versteckter Limiter | Verdeckte Effekte sind nicht debugbar und nicht dokumentierbar |
| Portindizes, Symbole und URIs nicht ohne begründete Versionierung ändern | Presets und Host-Sessionen hängen daran |
| Keine Produktnamen aus Fremdquellen in die GUI übernehmen | Neutral benennen, Herkunft in `docs/QUELLEN.md` belegen |
| Nicht ausgeführte Geräte-/Hörtests nie als bestanden melden | Einstellungsfehler werden sonst zu falschen Tatsachen |

## Zwei-Sprachen-Parität: die harten Stellen

### Port-Reihenfolge ist ein Dreieck

Ein Parameter wird an **drei** Stellen gleichzeitig registriert: LV2-Portindex,
JSFX-Sliderindex, RPL-State. Der Preset-Selektor ist in JSFX slider11, die
beiden angehängten Ports sind slider12/13. LV2 hat sie **nach** Latenz und
Oversampling. Wer nur eine Seite ändert, bekommt stille Abweichungen.

Deshalb: Ports nie von Hand in TTL oder JSFX schreiben, immer `data/*.json`
ändern und `tools/generate.py` laufen lassen.

### EEL2-Fallstricke

- `==` vergleicht in EEL2 **mit Toleranz**. Für zwei Zweige, die im C++-Pfad
  bitgleich sein sollen, `===` verwenden.
- **NaN-Sanierung niemals** über `(x - x) === 0`: x86-EEL behandelt unordered
  als gleich, `NaN - NaN` ist also `=== 0`. Es braucht eine geordnete
  Vergleichsfunktion plus separaten NaN-Test.
- `pdc_delay`/`pdc_bot_ch`/`pdc_top_ch` gehören bei jedem Oversampling-Wechsel
  mitgezogen.

### Float-Bitgleichheit ist das Ziel

`jsfx_parity` vergleicht C++- und EEL2-Ausgabe und sollte `max=0 FS` melden.
Weicht der Test ab, ist fast immer eine dieser Ursachen schuld:

1. `pow`/`exp`/`log` in anderer Reihenfolge aufgerufen,
2. eine Zwischengröße in `float` statt `double` gerechnet,
3. ein vorzeichenbehafteter Null- oder NaN-Fall,
4. unterschiedliche Verzögerungskompensation am Blockanfang.

`tests/jsfx_parity.cpp` prüft zusätzlich, dass Bank-State, Selektor und
Sliders 12/13 zusammenpassen. Die erwartete Presetzahl liest der Test aus dem
Selektorbereich, nicht aus einer festen Zahl — eine feste Zahl führt dazu, dass
ein neu hinzugefügtes Preset still übersprungen wird.

## Angehängte Ports: Preset-Semantik bewusst unterscheiden

`oversampling` und `transformer` sind beide `lv2_append`, verhalten sich beim
Recall aber **absichtlich unterschiedlich**:

- **Oversampling startet auf Off.** Es ist eine Qualitäts-/CPU-Wahl. Ein Recall
  darf nicht ungefragt die vierfache Rechenzeit aktivieren.
- **Transformator übernimmt den Presetwert**, sonst `None`. Er ist eine
  Klangwahl und gehört zum Instrument.

Beide Wege laufen durch **eine** Funktion (`appended_value()` in
`tools/generate.py`). Niemals an einer Stelle direkt `default` schreiben und an
einer anderen den Presetwert lesen — genau daraus entstehen Klangunterschiede
zwischen LV2-Preset und REAPER-Bank, die niemand bemerkt, weil beide
„funktionieren“.

## DSP-Erkenntnisse

### Kompressor-Grundform

Feedback Gain Law mit statischem Offset, Knie und Verhältnis. Wichtig: höheres
Verhältnis hebt **die Schwelle mit** und macht das Knie härter. Wer nur das
Verhältnis erhöht und die Schwelle konstant hält, verwechselt Limiting mit
Kompression. Ein 1176 hat bewusst **keinen Threshold-Regler** — die Schwelle
hängt am Input. Daraus folgt: Gain-Reduction-Ziele sind Benutzerangaben
(`target_gr`), keine Preset-Felder.

### All Buttons

Kein 20:1-Verhältnis im klassischen Sinn, sondern die Kombination zweier
Kompressionspfade. Die Kennlinie hat ein **Plateau**. „All Buttons“ ist ein
Transientenwerkzeug, kein Brickwall-Limiter — und darf nicht als solcher
implementiert werden.

### Kopplungs-Bassabsenkung

Ein echter Transformator entkoppelt die Wicklungen über einen endlichen
Kern. Diese Kopplung **ist** die Bassabsenkung. Sie ist Nebeneffekt des
Modells, kein Bedienziel, und gehört deshalb **nicht** als eigener Regler
exponiert.

### Sättigungsschwelle aus einem SPICE-Kern ableiten

Für einen Kern der Form `Cc` parallel zu `Bc = a·|φ|^n·sgn(φ)` (Gyrator-
Kapazität) gilt: Sättigung setzt ein, wenn der nichtlineare
Magnetisierungsstrom den linearen Anteil gleicher Größe erreicht.

```
i_lin = C·ω·φ
i_sat = a·|φ|^n·sgn(φ)
Kniefall:  φ_k = (C·ω/a)^(1/(n-1))
```

Für ein SPICE-Modell mit vier sehr verschiedenen Bauformen lagen die so
gewonnenen `φ_k` nur um den Faktor 1,58 auseinander. **Ein** absoluter
Schwellwert über alle Bauformen wäre trotzdem falsch, weil genau diese
Reststreuung die unterschiedliche Sättigungshärte ausmacht.

**Getroffene Lösung:** normierter Flux `u = φ/φ_k`, Schwelle bei `u_knee = 1,0`.
Ein gemeinsamer Normierungsparameter, die transformatorspezifischen `n`, `Np`,
`Ns` bleiben erhalten. `ω` bleibt frequenzabhängig — das ist der Modelleffekt
und wird nicht weggeglättet.

**Oberhalb des Knies nicht zusätzlich klemmen.** Bei `n` zwischen 6 und 13 ist
`2^n` schon 64× bis 8192×; der Flux wächst von selbst nicht weiter. Ein
zusätzlicher Clamp auf `u` zerstört die Beziehung `v = N·dφ/dt` und beseitigt
genau den Sättigungscharakter, den man modelliert.

Bei `n = 13` kostet `|φ|^n` eine `pow`-Funktion je Wicklung und Sample. Das ist
der Grund, warum das Modell dort zeitlich zurückgestellt bleibt und erst nach
einer CPU-Messung auf dem Zielgerät gebaut wird.

### Integration statt Ableitung

Das SPICE-Modell arbeitet mit `DDT`, also einer **Ableitung** von `i`. Ein
Differentiator im Audioband ist numerisch unbrauchbar: Verstärkung ∝ 1/f,
Rauschen, Instabilität bei 4× Oversampling. Nötig ist die **integrierte** Form
als zustandsbehafteter Flux-Integrator mit Trapez- oder Bilinearregel —
explizit wird instabil, sobald die Sättigung steil wird.

Resamplerhistorien und Flux-Zustände sind **je Kanal und Richtung** getrennt zu
führen. Stereo-Link benutzt Betragspegel; eine L+R-Summierung darf
gegenphasige Signale nicht aus der Detektion entfernen.

### Latenz als Charakterentscheidung

Eine Transformatorstufe verursacht im Wesentlichen **Phasendrehung im
Tieffrequenzbereich**, keine echte Laufzeitverzögerung. Würde man dafür
zusätzliche Latenz deklarieren, ließe der Host samplegenau phasenkompensieren
und damit genau den Charakter zerstören, den man mit dem Transformator wählt.
Latenz bleibt deshalb bei 0/3/4 Frames für Off/2x/4x; für echte
Phasenverzerrung wäre ein Phasenverzerrungsfilter die Alternative, nicht mehr
Latenz.

## Skripte

### Generator und Konsistenz

```sh
python3 tools/generate.py            # alle generierten Artefakte neu bauen
python3 tools/generate.py --check    # darf nichts ändern
python3 tools/validate.py            # Portlayout, Presetbereiche, Imports
```

`docs/PRESETS.md` ist **generiert**. Zahlen und Labels dort nie von Hand
pflegen, sondern im Generator aus `data/*.json` ableiten — sonst driftet die
Doku, sobald ein Preset dazukommt. Auch hartkodierte Mengenangaben im Generator
(`len(presets)`, Anzahl aktiver Transformer) gehören dynamisch, sonst stimmen sie
nach dem nächsten Preset nicht mehr.

### Versionierung und Revision (Dreistelligen-Schema)

- Die **Revisionsnummer ist die dritte Stelle der Versionsnummer** in
  `data/model.json` (`version`, z. B. 0.4.2 = Revision 2); ein separates
  `revision`-Feld gibt es nicht (früher „0.4.1 rev N" — rev 1 ≙ 0.4.1,
  rev 2 ≙ 0.4.2).
- Mit **jeder Sourcecodeänderung** die dritte Stelle um **+1** erhöhen;
  alle Änderungen zwischen zwei Nutzereingaben gelten als **eine**
  Sourcecodeänderung. Sourcecodeänderung = Dateien unter `src/` oder
  `jsfx/`; `tools/`, Doku, GUI-Assets und reine Metadaten zählen nicht.
  Achtung: `data/*.json`-Änderungen zählen dann, wenn sie generierte
  Artefakte unter `src/`/`jsfx/` verändern (z. B. Kennlinienkonstanten).
- Nach dem Bump immer `python3 tools/generate.py`; die Version erscheint
  **ohne „rev"-Anhang** in der LV2-GUI (Fußzeilenplatte, unter Mono/Stereo)
  und in der JSFX-`@gfx` unten rechts via `#gs_ver` (EEL2-Stringvariable,
  wird im generierten `@init` gesetzt — Strings brauchen `#`-Präfix und
  können nicht als Funktionsparameter übergeben werden).
- `lv2:microVersion` folgt derselben dritten Stelle (`generate.py` parst
  `version`).

### Bauen und Testen im WSL-Sysroot

Ohne Root-Rechte wird gegen ein entpacktes Sysroot gebaut:

```sh
S=/tmp/opencode/sysroot
env PATH="$S/usr/bin:$PATH" \
    GCC_EXEC_PREFIX="$S/usr/lib/gcc/" \
    C_INCLUDE_PATH="$S/usr/include:$S/usr/include/x86_64-linux-gnu" \
    CPLUS_INCLUDE_PATH="$S/usr/include/c++/11:$S/usr/include/x86_64-linux-gnu/c++/11:$S/usr/include/c++/11/backward:$S/usr/include:$S/usr/include/x86_64-linux-gnu" \
    LIBRARY_PATH="$S/usr/lib/x86_64-linux-gnu:$S/usr/lib/gcc/x86_64-linux-gnu/11" \
    LD_LIBRARY_PATH="$S/usr/lib/x86_64-linux-gnu" \
    LDFLAGS="-L$S/libfix" \
    make BUILD_DIR=build/wsl test
```

`make test` umfasst Signaltests, Übergangstests, LV2-ABI-Test und `validate.py`.
Ein PASS hier ersetzt **keinen** Gerätetest.

### JSFX-Parität

```sh
env <siehe oben> cmake --build build/parity-wsl --target jsfx_parity -j4
build/parity-wsl/jsfx_parity \
  jsfx/GreenStripe76-Mono.jsfx jsfx/GreenStripe76-Stereo.jsfx
```

Erwartung: `PASS (232 cases, max=0 FS)` und der Presetblock mit
`<N> preset states`. Fällt einer der beiden Werte aus, ist es kein
Flakiness-Signal, sondern eine echte Abweichung.

### RDF/TTL-Validierung

`rdflib` fehlt in der WSL-Umgebung; `validate.py` sagt dann ausdrücklich
`structural checks only`. Die vollständige RDF-Prüfung läuft auf dem
Testrechner unter Windows-Python:

```sh
python.exe -c "import rdflib,glob,sys
for f in glob.glob('lv2/green-stripe-76.lv2/*.ttl'):
    rdflib.Graph().parse(f, format='turtle')
print('RDF OK')"
```

### AArch64-Cross-Build für den Dwarf

```sh
aarch64-linux-gnu-g++ -std=c++11 -O2 -ffp-contract=off \
  -ffreestanding -fno-exceptions -fno-rtti -shared -fPIC \
  -march=armv8-a+crc -mfpu=neon -mfloat-abi=hard \
  -Wl,--as-needed -Wl,--gc-sections -Wl,-z,relro,-z,now \
  -Wl,--version-script=packaging/green-stripe-76.version \
  -o build/aarch64-gcc9/green-stripe-76.lv2/green-stripe-76.so \
  src/dsp/GreenStripe.hpp src/lv2_plugin.cpp

aarch64-linux-gnu-readelf -d .../green-stripe-76.so | grep NEEDED   # nur libm/libc
aarch64-linux-gnu-readelf --dyn-syms .../green-stripe-76.so \
  | grep -o 'GLIBC_[0-9.]*' | sort -Vu | tail -1                    # Floor
```

Ein Cross-Compiler-Ergebnis ist **kein** Gerätetest. Der Symbolfloor muss
höher liegen als auf dem Buildrechner, sonst bootet das Plugin auf dem
Zielsystem nicht.

### GUI-Assets

`tools/make_assets.py` rendert die Paneel-PNGs **echt aus dem HTML/CSS in
Chromium** (Playwright; Vorversion mit statischem PIL-Nachzeichnen wurde
abgelöst, weil Textmaße und Bounding-Boxen abweichen). Voraussetzungen:

- `pip install playwright pillow`, dann `python3 -m playwright install chromium`.
- Ohne Root fehlen Systembibliotheken (`libnspr4`, `libnss3`, `libatk*`,
  `libgbm1`, `libXrender1`, …): Ubuntu-.debs laden, per `dpkg-deb -x` nach
  `/tmp/opencode/chromium-debs/root` entpacken und
  `LD_LIBRARY_PATH=/tmp/opencode/chromium-debs/root/usr/lib/x86_64-linux-gnu`
  setzen; `ldd`-Check bis „not found“ leer.
- `page.set_content()` hat **keine Basis-URL**: `<img src="assets/logo.png">`
  bleibt kaputt (Alt-Text gerendert). `gui_preview.page_html()` inlines
  deshalb neben den CSS-Assets auch die HTML-`src`-Attribute als Data-URI.
- **Auf dem Gerät gilt dasselbe:** mod-ui injiziert das Mustache-gerenderte
  Icon-Template in das DOM der Pedalboard-Seite (`modgui.js`,
  `self.icon.html(...)`); relative `src` lösen gegen die Seiten-URL auf
  (404, gebrochenes Bild). HTML-Templates brauchen deshalb dieselbe Form wie
  das CSS: `src="/resources/assets/logo.png{{{ns}}}"`. Der Webserver routet
  `/resources/(.*)` in das `resourcesDirectory` des Plugins (`webserver.py`,
  `EffectResource`), `{{{ns}}}` wird beim Rendern zur Cache-Query
  `?uri=…&v=…` (`getTemplateData`). Die lokale Data-URI-Vorschau kaschiert
  relative Formen — erst `validate.py` (erzwingt die `/resources/…{{{ns}}}`-Form)
  und der Gerätetest zeigen den wahren Zustand.

Die LV2-Oberfläche ist hell, aber die Prüfungen bleiben dieselben:

- Kontrast jedes Textfeldes gegen seinen Hintergrund messen, nicht schätzen
  (Ziel ≥ 7:1; bei `#10161a` auf Stahl 11,6:1 und auf Grün 7,4:1).
- Gruppenmittig und gleichmäßig verteilt heißt: Bounding-Boxen der
  Potentiometer vergleichen, nicht Zeilenpositionen abschätzen.
- Farbflächen an **Leerflächen** abtasten, nicht an Kanten — dort liegen
  Verläufe und Radien.
- Ecken-Schrauben als Ring plus Kreuz prüfen, mit je eigener Bounding-Box.

## Quellenarbeit

Wer Presetwerte aus Artikeln übernimmt, übernimmt **Reglerstellungen**, keine
Messwerte. Deshalb:

1. Quelle vollständig lesen und Fundstelle zitieren, inklusive Autor und Datum.
2. Nur die **Wirkung** übernehmen, die eigene Reglergeometrie aber offenlegen.
   Formulierungen wie „10 o'clock" lassen sich ohne Belege für die
   Uhr-Geometrie des Geräts nicht in eine Zahl übersetzen; stattdessen „langsame
   Attacke, mittlerer Release“ notieren und als Näherung kennzeichnen.
3. Skalen **zuerst** klären. Liest man die Quelle als „höher = langsamer“, aber
   das Gerät als „höher = schneller“, sind alle abgeleiteten Presets
   gespiegelt und fallen beim Hörtest nicht auf, sondern klingen nur „anders“.
4. Fremddateien können Nicht-UTF-8-Bytes enthalten (SPICE-Editorausgaben mit
   typografischen Anführungszeichen). Vor dem Patchen prüfen, sonst zerreißt
   der Editor die Datei.
5. Ein Quellmodell, das im Original ausdrücklich als „only for testing
   purposes“ überschrieben ist, darf nicht als klangliches Ziel verkauft werden.
   Das gehört in die Dokumentation, nicht in den Feature-Text.

### MOD-GUI-Meter über Output-Ports (seit 0.5.0)

Ein GUI-Meter für einen Wert, den es als LV2-Port nicht gibt, ist ein
Portvertrag — kein CSS-Trick. Der komplette, am Gerät verifizierte Pfad:

1. **Output-Port anlegen** (z. B. `gr_db`, −60…0 dB, `connectionOptional`),
   im Generator als eigene Kategorie führen: **kein** `lv2_append`, **kein**
   JSFX-Slider (`jsfx_slider: 0` und im Generator überspringen — sonst
   kollidiert der Default-Index mit slider13/Selektor), **nie** in
   presets.ttl (Outputs sind nicht preset-adressierbar).
2. **modgui.ttl** braucht beides: `modgui:javascript <modgui/xxx.js>` und
   `modgui:monitoredOutputs [ lv2:symbol "..." ]`. Ohne monitoredOutputs
   sendet mod-ui kein `monitor_output` an mod-host und es kommt **nie** ein
   Wert an — die Ontologie dafür liegt in `/usr/lib/lv2/modgui.lv2/modgui.ttl`
   („A monitored output MUST have exactly one lv2:symbol").
3. **Datenpfad:** mod-host → `output_set <inst> <sym> <val>` (WebSocket) →
   `host.js` → pedalboard `setOutputPortValue` → `gui.setOutputPortValue` →
   `triggerJS({type:'change', symbol, value})`. Es gibt **keine**
   `output-control-value`-CSS-Rolle — Werte erreichen die GUI ausschließlich
   über das Plugin-JS.
4. **Plugin-JS-Datei:** mod-ui lädt sie per `/effect/file/javascript` und
   evalt `method = <code>` — die Datei muss also **ein einziger
   Funktionsausdruck** sein (`function (event, funcs) { ... }`). Fehler im
   JS werden still abgefangen (`jsCallback = null`, nur console.log) — die
   GUI fällt dann auf den CSS-Default zurück, deshalb ohne JS einen
   sinnvollen Zustand (Nadel in Ruhe, gedimmtes Face) via CSS vorbereiten.
5. **`event.icon` ist der `.mod-pedal`-Wrapper**, nicht die eigene
   Wurzelklasse — Zustandsklassen über `event.icon.find('.eigeneklasse')`
   setzen und die CSS-Selektoren von der eigenen Wurzel aus bauen. Das
   generierte `{{{cns}}}` wird an Klassennamen angehängt; JavaScript darf
   deshalb nicht nach der unsuffixierten Basisklasse suchen. Für JS einen
   zweiten, statischen Hook verwenden (z. B. `class="gs76{{{cns}}} gs76-root"`)
   und ausschließlich `.gs76-root` selektieren. Das `'start'`-Event trägt
   alle Input-Portwerte + Monitored-Outputs;
   `'change'` feuert für UI- **und** Host-seitige Änderungen (nicht bei
   Quelle „from-js").
6. **Gerätecheck vorher:** die OS-Version des Geräts kann älteres mod-ui
   haben — `grep setOutputPortValue /usr/share/mod/html/js/modgui.js` per
   SSH bestätigt JS-Support und Output-Pfad, bevor man 0.x.y daran aufbaut.
7. **Darstellung:** Layer-Images mit dem `padding-bottom`-Aspekt-Hack
   stapeln (aspect-ratio ist auf dem Geräte-WebKit unsicher); Reihenfolge
   Face on/off (statisch) → Nadel (rotiert) → Lagerabdeckung (statisch,
   eigene Ebene ÜBER der Nadel). **Niemals in der Nadel-Ebene zeichnen**:
   selbst ein „rotationsinvarianter" voller Kreis rotiert mit, sobald eine
   Kappung (Bezel-Freihaltung) eine flache Kante erzeugt — Fehlversuch
   2026-10-08, der Halbkreis drehte sichtbar mit. `transform-origin` am
   Pivot in Prozent des Canvas; CSS-
   Transition für die Glättung — und im Browsertest **Wartezeit nach dem
   Klassentoggle**, sonst misst man mitten in der 60-ms-Opacity-Transition.
   Dasselbe gilt für erzeugte Screenshots: Varianten nacheinander ohne feste
   Settling-Zeit aufzunehmen lässt die erste Variante halb gedimmt und die
   zweite korrekt erscheinen, obwohl beide denselben Zustand haben.
8. **VU-Ballistik:** Eine `transform 300ms ease-out`-Transition liefert eine
   ungefähr VU-artige sichtbare Trägheit, verändert aber weder den blockweisen
   Output-Port noch den DSP. Bei häufigen Portupdates startet CSS die Transition
   jeweils vom aktuellen Zwischenstand neu; das ist eine Anzeigecharakteristik,
   keine normgerechte IEC-VU-Integration. Tests müssen `transitionDuration`
   prüfen und vor der Endpositionsprüfung länger als 300 ms warten.
9. **MODs globale Drag-Handle-Regel beachten:**
   `.mod-pedal .mod-drag-handle` setzt `position:absolute`, alle vier Kanten
   auf `0` und `z-index:20`. Ein Footer mit dieser Klasse wird ohne vollständige
   Gegenregel zum unsichtbaren Vollflächen-Overlay. Für jeden eigenen Rail
   **alle** relevanten Kanten setzen, inklusive `left:auto`, `right:auto` oder
   `bottom:auto`; einen Footer explizit auf `position:relative`, alle Kanten
   `auto` und normalen Z-Index zurücksetzen. Sonst kann z. B. der „rechte“ Rail
   wegen geerbtem `left:0` links liegen. Der Browsertest muss die GUI in einen
   `.mod-pedal`-Wrapper setzen und diese echte Basisregel reproduzieren; eine
   isolierte Template-Vorschau kaschiert den Fehler.

**Portindizes:** neue Ports **anhängen** (nach den angehängten Inputs),
bestehende Indizes bleiben stabil; Portzahl-Assertions in validate.py und
test_lv2.py mitführen (validate zählt Control-Inputs + Latency + Outputs
getrennt — Outputs doppelt zu zählen ist der naheliegende Fehler).

## Typische Fallen, die mich Zeit gekostet haben

| Falle | Wirkung | Gegenmaßnahme |
|---|---|---|
| Harte Zahl im Test (`preset_count != 26`) | Neues Preset wird still übersprungen, Test bleibt grün | Erwartung aus dem Artefakt selbst ableiten |
| Blinde Ersetzung `ae/oe/ue → ä/ö/ü` | Zersteckt *Blue* zu *Blü* und *tieffrequente* zu *tieffreqünte* | Immer gegen echte Wortliste prüfen, danach Diff lesen |
| Anzahl im Generator hartkodiert | Doku stimmt nach dem nächsten Preset nicht | Aus `len(presets)` ableiten |
| `appended_value()` an einer Stelle umgangen | LV2 und REAPER klingen unterschiedlich | Einen Helper für alle drei Pfade benutzen |
| Nur die ersten 10 Slider im Paritätstest prüfen | Angehängte Ports bleiben ungetestet | Indexliste explizit, Selektor ausgenommen |
| Asymmetrische Vertikalverteilung | Gruppen wirken trotz gleicher Mittelwerte schief | Bounding-Box-Zentren vergleichen |
| Kontrast/Geometrie geschätzt statt gemessen | Fehler fällt erst auf dem Gerät auf | Messen und den Wert in die Prüfung schreiben |
| `ImageFont.load_default(size=…)` | wirft vor Pillow 10.1 `TypeError`; ein `except TypeError` auf `load_default()` rendert **jede** Größe als ~11px-Bitmap. Ein 17px-Titel wird 9px hoch und 61px breit statt 116px | Skalierbare TTF laden, `getlength()` zum Zentrieren benutzen, Ergebnis am PNG messen |
| `Path.read_text()` ohne `encoding` | nutzt die **Locale**: unter Windows cp1252, das UTF-8-Dachs in `data/*.json` wird zu `â€“`. `make check-generated` meldet dann je nach Rechner eine andere Datei als veraltet | immer `encoding='utf-8'`, Generatortest unter **beiden** Interpretern laufen lassen und Ausgaben byteweise vergleichen |
| `Path.write_text(..., newline=…)` | wirft vor Python 3.10 `TypeError`; der Generator läuft auf der Testmaschine mit 3.9 und kann dort gar nicht schreiben | `open('w', encoding='utf-8', newline='')` und den Text selbst schreiben |
| Ein-/Ausgabe-Puffer mit `newline=""` schreiben | Mixed Line Endings, diff über ganze Datei | Auf `

` oder `
` normalisieren, Zeilenzahl vergleichen |
| Beschriftung **unter** den Regler | Zweiter Text macht einen Bay höher als einen Select-Bay; bei vertikal zentrierten Inhalten liegen die Bays nicht mehr auf einer Linie | Legende seitlich setzen |
| ASCII-Ersatzschreibweise in deutschen Notizen | Sieht nach Übertragungsfehler aus | Korrekte Umlaute, Diff kontrollieren |
| Native Bench als Dwarf-Aussage formuliert | Falsche Leistungsaussage | Relativen Trend nennen, Messort dazusagen |
| JS sucht `.gs76`, Template nutzt `.gs76{{{cns}}}` | Zustandsklasse wird am Gerät nie gesetzt; lokaler Preview ohne Namespace bleibt fälschlich grün | Zusätzliche statische JS-Hook-Klasse verwenden und echtes Plugin-JS im Browsertest ausführen |
| `.mod-drag-handle` auf Footer/mehreren Rails ohne vollständigen CSS-Reset | Unsichtbares `inset:0`-/z-index-Overlay macht das ganze Plugin ziehbar; rechte Leiste kann links landen | MOD-Basisregel im Test laden/reproduzieren und Position, vier Kanten sowie Z-Index je Handle explizit setzen |
| Screenshot direkt nach COMP-Klassentoggle | Erste Variante sieht trotz COMP ON gedimmt aus | Nach `default_controls()` länger als die Face-Transition warten; Zustand und berechnete Opacity separat prüfen |

| PIL `ImageDraw.Draw(img)` ersetzt Pixel **inklusive Alphakanal** — halbtransparente Fills löschen den Untergrund (Face wurde unsichtbar); auch `Draw(img, 'RGBA')` blendet Ellipsen nicht zuverlässig | halbtransparente Meter-Faces wurden weiß/unsichtbar | radiale Glows auf **separater Ebene** von außen nach innen zeichnen und mit `Image.alpha_composite` einfügen |

## Reihenfolge einer Änderung

1. `data/*.json` ändern — Parameter oder Preset.
2. `tools/generate.py` laufen lassen.
3. `make test` im Sysroot.
4. `jsfx_parity` neu bauen und laufen lassen; `max=0 FS` muss bleiben.
5. Assets neu rendern, wenn das GUI betroffen ist, und messen.
6. Betroffene Markdown-Dateien anpassen; generierte Doku nicht von Hand pflegen.
7. Cross-Build und Symbolfloor prüfen.
8. `git status` prüfen, generierte Artefakte mit committen.

Kein Push und keine Veröffentlichung ohne ausdrücklichen Auftrag. Geräte- und
Hörtests laufen auf einem anderen Rechner und werden erst dort als bestanden
geführt, wo sie wirklich stattgefunden haben.
## MOD Dwarf — Feldpraktische Erkenntnisse (2026-10-05)

**OS-Stand (2026-10-08):** Gerät läuft auf **1.14 RC4 (build 3366)** —
Testbuild; Release-Verifikation bleibt an 1.13.5.3315 gebunden. 1.14
bringt „Grouped plugin controls" (pg-Gruppen in der Settings-View,
gruppiert + farbcodiert), neuen Audio-Stack (jack2/mod-host) und
mod-ui-Änderungen — **Gerätchecks (modgui-JS-Grep, CPU-Matrix,
Install-SHA256) sind OS-gebunden und nach jedem Wechsel neu zu fahren**;
Messwerte immer mit OS-Build labeln. Thread-Regressionen: atom:String-
Parameter (PR 179, RC2 gefixt).

### Zugriff & Umgebung
- SSH: `root@192.168.51.1:22`, Passwort `mod` (laut MOD Wiki). Buildroot 2016.02, Kernel `6.1.15-rt7-moddwarf` (PREEMPT_RT), AArch64 Cortex-A35, 4 Kerne, Python 3.4.3.
- Dateisystem standardmäßig read-only; Remount nur gezielt `mount / -o remount,rw`.
- jackd läuft typ. als: `jackd -R -P 80 -t 200 -C /etc/jack-internal-session.conf -c system -d alsa -d hw:DWARF -r 48000 -p 128 -n 2 -X seq` (PID via `pgrep -x jackd`).
- Pedalboards unter `/root/.pedalboards/*.pedalboard`, aktiver Zustand in `/root/data/last.json` (z. B. `{"supportsDividers": true, "pedalboard": "/root/.pedalboards/GS76Measure.pedalboard", "bank": -1}`).

### Web-API (MOD OS 1.13.5.3315)
- UI unter `http://192.168.51.1/`, Version `?v=1.13.5.3315`.
- Effekt-/Pedalboard-Routen teils instabil: `effect/parameter/set` und `pedalboard/load_web`/`pedalboard/load_bundle` liefern bei POST/Form/JSON häufig **500 Internal Server Error** (kein reproduzierbarer, robuster Pfad). GET/Trailing-Slash-Verhalten inkonsistent.
- WebSocket/REST zum Live-Laden von Boards/Parametern auf dieser Firmware nicht zuverlässig für automatisierte Messreihen. Keine Annahme treffen, erst verifizieren.

### Boardwechsel & Neustart (robuster Weg)
- **Empfohlen**: Boardwechsel via `last.json` + Neustart des Audio-Stacks (`mod-host` + `jackd`), nicht über HTTP-REST `load_web/load_bundle`.
- Ablauf: `last.json` auf Ziel-`.pedalboard` schreiben, `pkill -9 mod-host && pkill -9 jackd`, 1–2 s warten, bis `jackd` wieder läuft (pollen, max ~15 s), 0.5–1 s Settling für Graph/LV2.
- Dieser Weg ist reproduzierbar auf MOD OS 1.13.x und vermeidet 500er.
- Originalzustand immer sichern (`/root/data/last.json` kopieren) und nach Messreihe restaurieren + neu starten.

### CPU-Messung (LV2)
- `tools/dwarf_loadtest.py` (Python 3.4-kompatibel): misst `/proc` CPU-Ticks (utime+stime), Threadlast (Taskliste), Plugin-Mappings (`/proc/<pid>/maps`, r-xp-Segmente mit `green-stripe-76.so`), SHA256/MD5, xrun-Hinweise (`dmesg`, `journalctl -k --no-pager`) über Fenster. Argumente `--frames`, `--seconds`, `--interval`, `--expect-instances`, `--report/--markdown`.
- Erkenntnisse GS76 Stereo (48 kHz, 128/256 Frames, 1 Instanz): **46–48 %** Median eines A35-Kerns, Spitzen **~66 %**, **0 xruns**, Top-Thread `jackd` ~21 %. Überhead dominiert (JACK+Host), Solverkosten isolierter via standalone Bench.
- SHA256 installierter Binary gesichert (z. B. `e6b4e55da1…`), immer mit Report mitschreiben.

### Python 3.4 (Buildroot) – Stolperfallen
- `pathlib.Path.read_text/write_text/read_bytes` fehlen. Ersatz: `io.open(str(path), mode, encoding=..., errors='replace')`.
- `subprocess.run` fehlt (3.5+). Ersatz: `subprocess.Popen(...); out,err = proc.communicate()` + `proc.returncode`.
- `datetime.isoformat(timespec=...)` fehlt (3.6+). Ersatz: `strftime('%Y-%m-%dT%H:%M:%SZ')` (UTC).
- `path.open(...)` vermeiden, immer `io.open(str(path), ...)`. Auch `open(path, ...)` mit `Path`-Objekt kann Typprobleme geben – konsequent `str(path)`.
- Self-Tests (lokal Python 3.x) und Geräte-Python 3.4 getrennt prüfen; Kompatibilität früh erzwingen.

### Filesystem/Tools
- LV2-Bundle: `/root/.lv2/green-stripe-76.lv2/green-stripe-76.so`, TTL unter `.lv2/*.ttl` (Portindizes/-symbole nicht ohne Versionierung ändern).
- Backup vor größeren Messreihen: z. B. `/root/backup-lt-YYYYMMDD-HHMMSS/`, lokal gespiegelt.
- `pgrep -x jackd`, `pkill -9 jackd/mod-host`, Polling bis jackd läuft. Keine Annahmen über Sofortverfügbarkeit nach Kill.

### Praktische Empfehlung
- LV2-Gesamtlastmessungen sauber per last.json+Restart (statt HTTP). Für isolierte Transformator-/Solver-Kosten bevorzugt standalone `transformer_bench` (AArch64, MPB/moddwarf-new Toolchain) direkt auf A35, um Host/JACK-Overhead zu trennen.

## Scarlett-Messplatz — automatisierte Transformator-Matrix (2026-10-06)

### Werkzeuge
- `tools/scarlett_matrix.py` + `tools\scarlett_matrix.bat` (Windows-CMD):
  Treiber über `scarlett_test.py`; Subcommands `devices`, `gainmatch`,
  `baseline`, `matrix`, `full`, `summary`. Geräte-Autoerkennung (Host-API
  wählbar, Standard MME, Name enthält „Focusrite“) — Portnummern können sich
  zwischen Sitzungen ändern, deshalb nie hardkodieren.
- **Resume:** `--root` mit `index.json` macht die Reihe fortsetzbar: fertige
  Läufe werden übersprungen, unvollständige Verzeichnisse gelöscht, fertige
  mit Fehler verweigert. Gainmatch-Proben überschreiben sich selbst (sie sind
  Wegwerfproben); `loop_gain_for`/`current_loop_gains` nehmen bevorzugt die
  **aktuellen** Gainmatch-Werte, nicht den Median alter Proben.
- **Anker-Semantik:** Stimulus-Pegel = Anker − Loop-Gewinn; die Pegelreihe
  (−24/−18/−12/−6/0 dB relativ zum Stimulus) trifft dann alle Anker
  −14/−8/−2 dBFS, weil Anker- und Serienabstand beide 6 dB sind — Alignment
  ist alles-oder-nichts. Bedingung: **Loop-Gewinn ≥ +1 dB** (Stimulus-
  Obergrenze −3 dBFS); sonst bricht der Lauf mit Anweisung ab.
  `--relax-anchors` misst mit abweichenden Pegeln und weist die erreichten
  Pegel mit Abweichung aus. Rückkanalpegel im Bypass ist Proxy für den
  Plugin-Eingang (Doku MESSTECHNIK Abschnitte 3/21).
- Tests: `tests/test_scarlett_matrix.py` (19 Fälle, simuliertes Backend),
  Windows-Python 3.9 und WSL-Python. CLI-Fehlerpfaden mit `SystemExit` +
  `redirect_stderr` testen — `parser.exit` legt den Fehlertext in stderr,
  nicht in die Exception.

### Feldbefunde (2026-10-06, erste Proben)
- **Gainmatch bestätigt den PluginDoctor-Abgleich:** Kanaldifferenz −0,20 dB.
  Die Probe überschreibt sich — mehrfach laufen lassen, während der Benutzer
  Regler dreht, und die Zahlen als Rückmeldung geben. Das ist der Ersatz für
  PD, wenn PD keine Einstellungen annimmt.
- **Loop-Gewinn ist das harte Tor:** −54,3 → −46,8 → −30,6/−35,5 dB nach zwei
  Umstellrunden; Ziel ≥ +1 dB (Anker) bzw. ≥ −20 dB (THD). Der große
  Resthebel liegt auf der **Return-Seite** (Scarlett-INPUT-Gains bis ~+50 dB,
  Dwarf-OUTPUT-Knopf). Der **Dwarf-INPUT-Knopf** setzt den Plugin-Eingangspegel
  (Anker) — einmal matchen, danach nicht mehr anfassen, sonst verschieben sich
  die Anker.
- **Scarlett-Panel ≠ Windows-Geräteformat:** Die Panel-Einstellung (48 kHz,
  SYNCED) ändert `default_samplerate` nicht; das folgt dem Windows-Geräteformat
  (`mmsys.cpl`, Wiedergabe **und** Aufnahme getrennt). Solange dort 44100
  steht, resampelt der Mixer; beobachtet: Sync-Marker-Korrelation 0,319 <
  Schwelle 0,35. Kontrolle über `recording.json` (`rate_mismatch`).
- **Signal auf beiden Eingängen im Ein-Kanal-Probe + Clipping auf dem stillen
  Kanal (bis 139k Samples bei 0,0 dBFS):** Verdacht MONO-Board (Mono verarbeitet
  Input L auf beide Outputs) oder abweichende Verkabelung — als Befund melden,
  nicht als Fakt; Board/Routing über den Benutzer klären, bevor die Matrix
  läuft. Clip-Zähler je Segment stehen in `results.json`.
- SSH auf den Dwarf (root/mod) scheitert in dieser Umgebung ohne sshpass/expect
  (kein askpass) — Board-Status also über den Benutzer erfragen, nicht
  annehmen.

### Erste Matrix am Gerät — Praxiserkenntnisse (2026-10-07)

- **REAPER statt PortAudio-Treiber:** die Serie lief als lange kontinuierliche
  Take (48 kHz/24 bit, beide Kanäle) mit mehreren Wiedergaben dazwischen;
  `tools/dwarf_reaper_series.py` importiert je Wiedergabe beide Kanäle in die
  Treiber-Struktur. Import-Specs: `gainmatch | baseline:rN | 60s:rN`.
- **Schnitt statt Render:** Wiedergabe-Startpunkte über die Marker-Chirps in
  der Take finden (normierte FFT-Korrelation über gleitende Fenster;
  Zweikanal-**Mittelung** hebt die Korrelation von ~0,52 auf ~0,99 —
  Einzelkanalanalysen grenzen knapp an die 0,35-Grenze). REAPER-Renderdialog
  hat eine **eigene Sample-Rate** unabhängig von der Projekt-Rate — zwei
  Renderläufe fielen auf 44,1 kHz zurück; immer aus der Original-Take
  schneiden.
- **Bedingungen fingerabdrücken statt raten:** Bypass = flacher Sweep; Profile
  über die 20-Hz-Klirr-Reihung (60s > 80s > 00s ≫ Bypass/Sym). Deckte sich
  mit der Benutzerreihenfolge; bei Unstimmigkeit Fingerabdruck vor Label
  trauen.
- **Dwarf-Recorder als digitale Querreferenz:** parallel im Board mitlaufen
  lassen; gegen dieselben Pläne analysierbar. Der Recorder-Zweig hat einen
  eigenen Offset (gemessen −4,3…−5,4 dB), der File-Player ist laut Benutzer
  Unity — Offset nie als Player-Gain interpretieren.
- **Stille Übersteuerung:** eine um +4,8 dB heißere Aufnahme clippte komplett
  (recorded_peak 0,0 dBFS in allen Segmenten → alle Läufe ungültig, Sync
  sah normal aus). Nach jeder Regleränderung kurze Probe vor der Serie.
- **OS-Provenienz:** der DUT−Baseline-Latenzcheck gilt nur bei
  Skript-gesteuerter Wiedergabe; bei manuellem Start überlagert der Start-
  jitter (±Sekunden) die 0/3/4-Frame-Latenz. OS-Stellung pro Runde vom
  Benutzer erfragen und ins `--settings-label` schreiben.
- **Anker in der Dwarf-Quelle:** Dateipegel = Plugin-Eingang; `build_summary`
  prüft Anker jetzt digital (Index-Flag `dwarf_source`), Aufnahmepegel nur
  noch als SNR-Diagnose.
- **CPU-Bild des Transformators (x86-Bench 5c):** Iterationszahl kein Hebel
  (2,0–2,6/Sample, 0 % am 40er-Limit); die 14 Stop-Zweige je Auswertung
  dominieren; OS multipliziert. Hebel-Skizze (paritätsneutral →
  Paritätspreis → Vertragsfragen) in TODO, Abschnitt CPU-Reduktion.

### Remote-Betrieb, Solver-Änderungen und EEL2-Scope-Fallen (2026-10-07, spät)

**SSH ohne Passwortinteraktion (öffnet die Gerätetest-Automatisierung):**
OpenSSH ≥ 8.4 erlaubt `SSH_ASKPASS_REQUIRE=force` mit einem Mini-askpass
(`echo mod`) — kein sshpass/expect nötig. Damit: Bench pushen/ausführen,
Screenshots der installierten GUI ziehen (Sichtprüfung remote möglich!),
`sha256sum` verifizieren. Achtung: der Erfolgs-Check eines Push-Loops muss
auf die Erfolgszeile matchen — die Fehlerzeile `! [remote rejected] main ->
main` enthält ebenfalls „main -> main". GitHub kann pushes zeitweise mit
`Internal Server Error` ablehnen (Retry-Loop, `git fsck` prüfen).

**EEL2-Instanz-Scope (kritische Falle, hat eine volle Render-Serie
verursacht):** `instance()`-Listen binden Variablennamen pro Objekt; eine
Funktion, die eine Objektvariable ansieht, muss sie in ihrer eigenen
`instance()`-Liste deklarieren — sonst resolved EEL2 den Namen auf die
GLOBALE Variable (stiller Korruption, kein Crash). Konkret: der
konvergierte Zustands-Commit in `gs_xf_core` schrieb `stops[j]`, ohne
`stops` zu binden (das Array lebt in `gs_xf_init` per `gs_alloc`);
`gs_xf_current` bindet es korrekt — der Alt-Code fasste `stops` in
`gs_xf_core` nie direkt an. Symptom-Muster: C++↔EEL2 auf den
Paritätssignalen bitgleich, das volle Programm weicht erst ab der ersten
breitbandigen Transiente. Debug-Reihenfolge: erste Divergenzstelle
lokalisieren (Sample-Index → Stimulus-Regime), dann C++-alt /
C++-neu / EEL2-neu getrennt rendern und gegen die Referenzen stellen —
die Trennung EEL2-gegen-C++ vor der Mikrosuche im Code.

**Commit-Hygiene bei Bisektionen:** die Bisektionsvariante darf nie im
Commit landen. Der MPB-Build-Log entlarvt den committierten Stand:
`warning: variable 'converged' set but not used` hieß, der Sparpfad fehlte
im gebauten Code. Vor jedem Pin-Bump: `git show HEAD:<datei>` gegen die
beabsichtigte Fassung prüfen. Und: **Install-Verifikation** — die
Geräte-SHA256 nach jedem Install prüfen (ein Install griff einmal nicht,
die Datei blieb wochenalt); der `.mk`-Pin muss den Code-Commit enthalten
(Pin-Commit NACH dem Code-Commit pushen).

**CPU-Matrix per Boardkopien (robuste Methodik):** 36 Boardverzeichnisse
mit eingeschriebenen Werten (Template mit Transformer-Port aus der
bestehenden RPP, SWH-Oszillator 20 Hz als Signalquelle — schwerstes
Solver-Regime), je Zustand `last.json` + voller Neustart (Controlchain
übernimmt last.json erst beim Vollstart), Warten auf das Plugin-Mapping in
`/proc/*/maps`, dann `dwarf_loadtest.py --expect-instances 1`. Die Werte
stehen in der Board-TTL — der gemessene Zustand ist das eingeschriebene
Board. `load.json` auf dem Gerät akkumuliert Bedingungen über Läufe — die
Auswertung nimmt je Label den letzten Eintrag; zwei Serien in einer Datei
= zwei Binaries (an den SHA-Klassen erkennen).

**Solver-Optimierung: messen vor dem Umbauen.** Die TODO-Schätzung
„Stop-Zweige 30–50 %" war um den Faktor 20 daneben (12/13 Zweige klemmen
nie — Diagnosezähler je Zweig + Extremreizen bis zum Input-Clamp ±256 FS);
die „finale Doppel-Auswertung" hatte der Compiler bei −O3 bereits
eliminiert (~0 % gemessen). Der wirksame Hebel war die Konvergenztoleranz
(1e-14 → 1e-6 relativ, Lösung ≈ −120 dB): die sauberen Profile (00s/Sym)
fallen auf ~1,5 Iterationen (−10–12 % CPU), die tief saturierenden
(60s/80s) bleiben bei ~2 — die Iterationszahl ist strukturell gebunden
(quadratische Konvergenz, die Quellstufe des neuen Samples ist a-priori
unbekannt). Bench mit `-DGS76_TRANSFORMER_STATS` meldet Iter/Probe direkt —
Kandidaten am Gerät gegeneinander messen, nicht theoretisieren.
`transformer_bench`-Semantik: `--channels` war invertiert (1=stereo —
gefixt), `--oversampling` nimmt den Wert (1=2x, 2=4x).

**Cross-Toolchain ohne root:** `apt-get download <paket>` + `dpkg-deb -x`
+ `LD_LIBRARY_PATH` auf die privaten binutils-Libs
(`libopcodes-2.38-arm64.so` aus x86_64-linux-gnu) — aarch64-GCC ohne
Installation. Statisch linken (`-static`) umgibt den
glibc-Symbolfloor-Zielsystem-Vorlauf; die Zahlen sind dann
Compiler-spezifisch (nicht MPB-komparabel) — Vorher/Nachher nur mit
demselben Compiler.

**ysfx als Offline-Renderer (Alternative zu REAPER-Renders):** der
gepinnte Fork rendert JSFX offline — `ysfx_slider_set_value(fx, index,
value, notify)` ist 0-basiert (sliderN → index N−1), Stereo muss in EINEM
`ysfx_process_float`-Aufruf laufen (Channel-Pointer-Arrays; getrennte
L/R-Aufrufe brechen Stereo Link). Ausgabeverzeichnis anlegen (fopen
schweigt sonst mit „WAV-Schreibfehler"). Der Host ist der gepinnte
Referenzstand des Projekts (QUELLEN); REAPER-Engine-Äquivalenz wurde am
vollen Programm bitweise bestätigt.

**Markdown-Konsolidierung bei widerlegten Aussagen:** refutierte/veraltete
Passagen werden ~~durchgestrichen~~ (nicht gelöscht) und direkt durch den
Messbefund mit Datum ersetzt — die Widerlegung bleibt lesbar, der
Dokumentenstand bleibt current.

### Dwarf als Signalquelle (2026-10-07)

- Der Dwarf spielt die Testtöne selbst (File-Player → GS76 → DAC → Scarlett-ADC
  nur für die Aufnahme). Damit ist der Plugin-Eingang **digital**: die
  Dateipegel SIND die Ankerpegel. `--level -2` in einer 'all'-Datei legt die
  Pegelstufen auf −26…−2 dBFS und trifft die Anker −14/−8/−2 exakt — der
  Loop-Gewinn betrifft nur noch den Aufnahmepegel (Dwarf-OUTPUT-Knopf), die
  alte ≥+1-dB-Ankerregel ist obsolet.
- Werkzeuge: `tools/make_dwarf_tones.py` (24-bit-PCM-WAVs + MANIFEST,
  Parameter identisch zur Treibergenerierung: settle 2, measure 1, 1 kHz),
  `scarlett_test.py record(..., play=False, pad_seconds=10)` bzw. CLI
  `run --no-playback --pad 10`, `scarlett_matrix.py --dwarf-source`
  (fixer Level, kein Anchor-Guard-Abbruch, `analyze` mit `max_delay=pad`),
  und für REAPER-Aufnahmen `tools/dwarf_reaper_series.py` (Import beider
  Kanäle je Stereo-Wiedergabe in die Treiberstruktur, siehe oben).
- Ablauf je Lauf: Enter → **sofort** Wiedergabe starten; die Aufnahme hat
  10 s Vorlauf. Achtung: `generate()` kappt den Peak standardmäßig bei −3 dBFS
  (ADC-Schutz der alten Kette); die Dwarf-Quelle überschreibt das bewusst mit
  `max_level=-0.1` — nicht als allgemeine Aufweichung des Limits verwenden.
- Dwarf- und Scarlett-Clock sind jetzt zwei Taktquellen; die Analyse gleicht
  linearen Drift bis 2000 ppm aus. Das alte 44,1-kHz-Resampling-Problem
  (Marker-Korrelation 0,319) entfällt, solange beide Seiten nominal 48 kHz
  fahren.
- Level-Auswahl der Upload-Datei und Treiberaufruf müssen zusammenpassen
  (settle/measure/frequency/level) — `make_dwarf_tones.py` schreibt die
  passenden Befehle in `MANIFEST.md`; Abweichungen verschieben die
  Marker-/Segmentpositionen und machen die Auswertung unbrauchbar.

### Ablaufmuster mit dem Benutzer am Gerät
1. Probe starten (`gainmatch`), Zahlen berichten, konkrete Regleranweisung
   geben, zwischen den Phasen mit dem `question`-Tool synchronisieren.
2. Phasen einzeln ausführen (`gainmatch`/`baseline`/`matrix --yes`) statt
   interaktivem `full`, weil die Prompts im Agentenkontext nicht beantwortet
   werden können. `--yes` nur für Skript-/Agentenläufe; der interaktive
   Benutzer hat die Prompts als Bedienhinweise.
3. **Nie** Regler nur in einem Kanal ändern — die Probe zeigt Kanaldrift sofort
   (beobachtet −4,93 dB nach asymmetrischer Umstellung) und Clipping auf der
   Aufnahme erkennt Übersteuerung ohne Hören.

## Fremdplugin-Referenz und PluginDoctor-Exporte (2026-10-08)

### PluginDoctor-Exportformate entziffern (ReaJS-Backend)

- **`THD.txt`** = THD-über-Frequenz-Kurve des Sweeps (Graph #0, dB relativ
  zur jeweiligen Grundwelle) plus zweite Kurve (Graph #1 — bei GS76 flacher
  Boden −100 dB, bei SSL Grundwellen-Tracking; Bedeutung nicht kalibriert).
- **`data.txt`** = FFT-Momentaufnahme (2 × 8191 Punkte, Raster 2,692 Hz =
  44,1-kHz-Backend); die Momentaufnahme landet je Export an einer
  **anderen Tonfrequenz** (Sweep-Position beim Export) — Fundamentale
  8,08/13,46/70/161/334 Hz sind also kein Benutzermuster, sondern Zufall.
- **Gültigkeitsnachweis ohne Gerät:** die Peak-Bin-Harmonikensumme
  (H2…H41) der Momentaufnahme muss mit dem Kurvenwert an derselben
  Frequenz übereinstimmen. Passte auf ±0,08 dB → Kurve und Snapshot sind
  dieselbe Messung. Frühere Fehlschläge (nur Anzeigeboden; viermal
  byte-identische Datei) so erkennbar und abgrenzbar.
- **Fremdplugin-Kurven können Treppenzüge sein** (7–10 Stufen, z. B. SSL):
  Werte nur **stufentreu** abrufen (Wert innerhalb eines Plateaus, sonst
  nächster Exportpunkt) — **niemals über Klippen interpolieren**, sonst
  erfindet man Messwerte (beobachtet: −57 dB „bei 1 kHz", real Steilklippe
  939→1034 Hz).
- **Funktionsrezept für gültige Exporte:** vor jedem Export Anzeige sichtbar
  neu triggern (Ton aus/ein), Dateigrößen müssen divergieren
  (byte-identisch = Fehlalarm), je Capture Screenshot + data.txt + THD.txt,
  Zustand in den Verzeichnisnamen.

### Kalibrierte Fremdplugin-Referenz statt PD-Screenshots

Der bessere Weg: **Fremdplugin in die REAPER-Testbench** laden und über
dasselbe Matrixprogramm rendern (gleicher Stimulusplan, −2 dBFS, digital,
paddgenau, Kanaldifferenz prüfen). Damit sind die Werte **direkt** mit den
eigenen Bankankern vergleichbar — kein Stellungs-/Pegelraten. Analyse
`tools/analyze_ssl_amount.py` als Muster (Stimulusplan mit SHA wiederverwenden).

### Physik-Plausibilität fremder „Transformator"-Modelle prüfen

Drei Hebel, alle aus Magnitudenspektren allein:

1. **Verlust-vs-Verzerrung:** deep bass loss (−6…−16 dB bei −2 dBFS) ohne
   massiv begleitende THD ist Kernphysik unwahrscheinlich (kollabierendes
   Lm erzeugt beides gleichzeitig und lastabhängig).
2. **Energiebilanz:** Sättigung **wandelt** Grundtonenergie in Obertöne
   (Rechteck-Limit ≈ 19 % der Restleistung); verschwindet die Grundwelle,
   ohne dass Harmonische sie tragen (≠ „gelöschte" Leistung), liegt eine
   entworfene Pegelabsenkung vor. Caveat: THD-Werkzeuge zählen oft nur
   H2…H10 — bei 1/n-Obertonschwänzen die höhere Ordnung grob
   mitrechnen, bevor man „Energie fehlt" behauptet.
3. **Effektmodell-Signatur:** „Bypass"-Stellung mit festem EQ-Tilt,
   nichtmonotone THD über den Regler, Klirr nur unter ~160 Hz (∝ V/f).

**Ehrliche Alternative mitdenken:** ein getreues Modell eines absichtlich
überfahrenen Mini-Kerns produziert dieselben Zahlen — trennbar nur durch
Diskriminierungstests: Bassburst/Remanenz (Hysterese-Nachlauf, Operating-
Point-Shift), Zweiton-IM (AM-Seitenbänder um den Mittelton),
20-Hz-Pegelreihe (Knie-/Verlustform), DC-/Polaritätsasymmetrie
(Even-Harmonics unter Offset). Konsequenz für Anker: heiße Stellungen
solcher Plugins niemals als Kalibrierziel; niedrige Stellungen höchstens
als Intensitätsanker.

### Werkzeug-Lektionen dieser Session

- **`scarlett_test.analyze()` schreibt `results.json` in den Stimulus-
  ordner**, wenn kein `report_dir` übergeben wird — bei wiederverwendeten
  Plandateien (z. B. `test-results/dwarf-tones/runs/*`) immer
  `report_dir=` setzen, sonst Überschreibrisiko.
- **POSIX-mkdir rekursiv nur an `/`-Grenzen:** ein zeichenweiser mkdir über
  Pfadpräfixe scheitert mit EACCES am Root-Präfix (`mkdir("/t")`) und
  erzeugt sonst Namensmüll. Komponentenweise an Slash-Grenzen +
  Abschluss-mkdir.
- **/tmp/opencode wird zwischen Sessions geleert:** Sysroot und geklonte
  Repos können weg sein; `ref052`-Renders überlebten. Gepinnte Forks
  (ysfx `5c3452f…`) frisch klonen **inklusive Submodule**
  (`git submodule update --init --recursive` — dr_wav fehlt sonst).
  Der WSL-Host hat inzwischen einen nativen gcc 11.4 — der Sysroot-Env-
  Block ist überflüssig; make/ctest laufen direkt.
- **Pilot-Chirp-Position ist designstabil:** im scarlett_test-Stimulus
  liegt der Marker-Chirp fest bei Frame 24000 (0,5 s Vorstille + 0,12 s
  Chirp), unabhängig von settle/measure — Unit-Tests können deshalb mit
  kurzen Scratch-Stimuli echte Erkenndefunktionen fahren
  (`tests/test_dwarf_matrix_session.py`, 8 Fälle).
- **Mehrere Proben als ein Programm rendern:** für Fremdplugin-
  Diskriminierungsserien die Einzelsignale zu **einer WAV** mit
  Sync-Marker (Pilot-Chirp an Start/Ende) und 0,5-s-Trennstille
  zusammenfassen (`tools/make_discrimination_program.py` — Generatoren
  **importiert**, nicht kopiert; Timeline + SHA in `manifest.json`,
  Anleitung als `README.md` neben der Datei). Fünf Renders des
  Gesamtprogramms schlagen 20 Einzeldateien; Segmentgrenzen kommen aus
  dem Manifest, Offset-/Ratenprüfung über die Chirps. Verbindliche
  Ausgabennamen (`<programm>-<variante>.wav`) im README festlegen, damit
  die Auswertung parsebar bleibt.
