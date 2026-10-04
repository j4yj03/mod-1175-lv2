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
| Keine Produktnamen aus Fremdquellen in die GUI übernehmen | Neutral benennen, Herkunft in `docs/SOURCES.md` belegen |
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

`tools/make_assets.py` rendert die Paneel-PNGs statisch mit PIL aus demselben
Layout wie das HTML. PIL hat **keine** Browser-Engine: Textmaße, Zeilenumbrüche
und Bounding-Boxen weichen ab. Für Unicode (Umlaute, `–`, `·`) wird ein Font
mit voller Latin-1-/CP437-Abdeckung gebraucht, sonst erscheinen Ersatzkästen.

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