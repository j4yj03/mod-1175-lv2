# Green Stripe 76 — Bedienung, Build und Installation

Bedienungsanleitung, Build- und Paketierung, Installation auf Buildrechner, Dwarf und REAPER.

**Konsolidiert am 2026-10-06** aus den bisherigen Einzeldokumenten; Inhalt inhaltlich unverändert, Pfadangaben auf die neue Struktur angepasst.

## Inhalt

1. USER_MANUAL.md — *(Quelle: USER_MANUAL.md)*
2. BUILD.md — *(Quelle: BUILD.md)*
3. INSTALLATION.md — *(Quelle: INSTALLATION.md)*


---

<!-- ===== Teil 1: Quelle docs/USER_MANUAL.md ===== -->

# Bedienungsanleitung — Green Stripe 76

## 1. Zweck und Charakter

Green Stripe 76 ist ein schneller, charaktervoller FET-Kompressor mit
Feedback-Regelung. Er kann Spitzen kontrollieren, Sustain verdichten, Drum-Räume
aufblasen und Signalen Verstärkerfärbung geben. Die Regler orientieren sich am
1176-Bedienprinzip; **das Klangmodell und die grünen Oberflächen sind eigenständig**.

Die Stellung **20:1** ist ein musikalischer Limiter-Modus. Es gibt keinen
Lookahead und keine garantierte True-Peak-/Brickwall-Begrenzung. All Buttons kann
Spitzen durchlassen, obwohl die anschließende GR groß ist.

## 2. Varianten wählen

| Variante | Ein-/Ausgang | Anwendung |
|---|---|---|
| LV2 Mono | 1 → 1 | Dwarf-Gitarre, Bass, einzelne Mikrofonspur |
| LV2 Stereo | 2 → 2 | Stereo-Effektkette oder zwei getrennte Kanäle |
| JSFX Mono | Input L → identischer Output L/R | Monoquelle in REAPER |
| JSFX Stereo | L/R → L/R | Stereoquelle, optional gekoppelte Regelung |

JSFX Mono summiert **nicht** L+R. Eine rein rechts eingespeiste Quelle muss im
REAPER-Pin-Mapping auf Input L gelegt werden. Für echte Stereosignale die
Stereo-Version verwenden. Kanäle oberhalb 1/2 werden von JSFX nicht bearbeitet.

### Stereo Link

- **On:** Ein gemeinsamer Regelverlauf reagiert auf den lauteren Betragspegel.
  L/R behalten denselben dynamischen Gain; gegenphasige Signale lösen weiterhin
  Kompression aus. Kanalabhängige Färbung kann trotzdem das Spektrum verändern.
- **Off:** Dual Mono — L/R regeln unabhängig. Beide verwenden dieselben
  Bedienparameter. Geeignet für zwei unabhängige Monoquellen; bei einem
  Stereo-Raumsignal kann die Balance hörbar wandern.
- Umschaltung und Regleränderungen werden intern über etwa 2 ms geglättet.
  Ab Version 0.1.1 laufen nur die aktiven Regler: Link On einer, Link Off zwei.
  Beim Umschalten wird der bisherige Zustand übernommen und kurz überblendet;
  dadurch muss kein dritter Regler dauerhaft unsichtbar mitlaufen.

## 3. Regler

**Aufbau der LV2-Oberfläche.** Drei senkrechte Bereiche nebeneinander: eine
breite **GAIN/TIME-Platte ohne Gruppenüberschriften**, mit Input/Output in der
linken und Attack/Release in der rechten Spalte, das grüne ENGINE-Feld (Verhältnis, Comp-Kippschalter,
Oversampling, Link) mit dem **Produktnamen als Titel**, und die rechte Platte
ohne Gruppentitel (Mix, Colour, Transformator). Die Bereiche schließen spaltfrei aneinander an; der Titel
steht ohne Namensschild direkt auf Grün. Alle Potis verwenden die
Aluminiumgrafik; alle Beschriftungen einschließlich **Colour** sind neutral.
Die sechs Potiwerte stehen jeweils unter der Beschriftung in einem kleinen
Rechteck mit derselben hellgrauen Fläche wie das Transformer-Dropdown.
Das Dropdown benötigt keine zusätzliche Überschrift: Es zeigt `No Transformer`,
`60s Transformer`, `80s Transformer`, `00s Transformer` oder `Symmetric Transformer`.
Die GAIN/TIME-Trennung reicht von oben bis unten; individuell gedrehte
Phillips-Schrauben sitzen in allen Modulecken. Input und Attack liegen auf
derselben Höhe wie Mix, Output und Release auf derselben Höhe wie Colour.
Dezente Schatten nach rechts
unten und helle Kanten oben links unterstreichen den Rack-Aufbau. Neben jedem
Regler steht sein Stellbereich: `Min.`/`Max.` bei Input, Output, Mix und Colour,
`Slow`/`Fast` bei Attack und Release. Unten rechts steht die **bernsteinfarbene
Betriebslampe (44×44 px) links vom unbeschrifteten Bypass-Kippschalter**;
dessen Tooltip bleibt „Bypass“. Die Lampe zeigt den Bypass-Zustand an
und leuchtet, solange die Kette aktiv ist. Die JSFX-Fassung zeigt dieselben
Zusammenhänge mit GR-, Peak-/RMS- und Host-GR-Anzeige, dort ohne Lampe.
Die gemeinsame Mitte von LED und Schalter liegt unter der Achse des Colour-Potis;
die Fußzeile ist kompakt gehalten.
Zum Verschieben des LV2-Paneels den **freien oberen Rand** greifen.
Drehregler verändern nur ihren Wert. Der Mode-Schieber trägt den aktuellen
Zustand `COMP ON` / `COMP OFF` direkt auf seinem beweglichen Griff; eine
separate Überschrift entfällt. Auch Oversampling und Link benötigen keine
Überschrift: Die Auswahltexte lauten `No Oversampling`, `2x Oversampling`,
`4x Oversampling` beziehungsweise `STEREO LINK` / `DUAL MONO`.
Zwischen COMP-Schieber und Oversampling liegen 40 px Abstand, zwischen
Oversampling und Link nur 7 px. Das Ratio-
Auswahlfeld ist auf derselben Höhe wie die Wertefelder von Input, Attack und Mix.

### Input — −36 bis +24 dB

Erhöht den Pegel vor Audiopfad und Regelung. Mehr Input verursacht mehr
Kompression **und** mehr Aussteuerung/Färbung. Es gibt keinen frei einstellbaren
Threshold-Regler. Ein höherer Ratio-Modus verschiebt zusätzlich den internen
Kompressionseinsatz; bei einem Ratio-Wechsel kann die GR daher zurückgehen.

Die Input-Zahlen sind **digitale Gain-dB**, keine originalen 1176-T-Pad-Skalen.
Alle Preset-Inputs sind Startwerte, nicht universelle Pegelvorgaben.

### Output — −36 bis +24 dB

Gleicht den Ausgangspegel aus und verändert die Aussteuerung der Ausgangsfärbung.
Der Detektor greift **davor** ab: Output verändert den GR-Verlauf nicht.
Es gibt keine automatische Makeup-Kompensation. Zu lautes Output kann im
nachfolgenden Signalweg clippen; es wird kein versteckter Ausgangslimiter benutzt.

### Attack — 1 bis 7

**1 = langsamer, 7 = schneller.** Die nominelle Zuordnung ist geometrisch:

\[
t_A = 800\,\mu s\,(20/800)^{(A-1)/6}.
\]

Auch Attack 1 ist schnell. Ein niedriger Wert erhält mehr Frontkante eines
Schlags oder einer Silbe. Ein hoher Wert glättet Peaks stärker und kann den
Klang nach hinten versetzen. Der effektive Verlauf hängt von Feedback, Pegel,
Ratio und All Buttons ab; die Zahl ist keine garantierte gemessene Anstiegszeit.

### Release — 1 bis 7

**1 = längere Erholung, 7 = kürzere Erholung.** Nominell:

\[
t_R = 1100\,ms\,(50/1100)^{(R-1)/6}.
\]

Nach langer/tiefer Kompression bleibt die Erholung länger. Release dem Rhythmus
anpassen: ein Drum-Schlag sollte vor dem nächsten sinnvoll zurückkehren, ohne
unbeabsichtigtes Pumpen. Auf Bass können sehr schnelle Zeiten absichtlich rau
werden, weil die Regelung Teile einzelner Schwingungen mitverfolgt.

### Ratio

- **2:1:** sanfte eigene Erweiterung für geringe Regelung.
  Factory-Presets **37 Piano Gentle 2:1** und **38 Stereo Bus Subtle 2:1**
  bereitgestellt. Input auf etwa 1–2 dB bzw. 0–2 dB Wet-GR einstellen und
  Output pegelgleichen; 31/35 sind die erhaltenen 4:1-Vergleiche.
- **4:1:** offener Ausgangspunkt, breiteres Knie.
- **8:1:** kräftigere Kontrolle für dynamische Quellen.
- **12:1 / 20:1:** hohe nominale Kompression für Peaks und Effektpfade.
- **All Buttons:** eigener Bias-/Kennlinien-/Dynamikzustand, wechselnder
  wirksamer Ratio-Bereich, anfänglicher Lag und zusätzliche Färbung.

Die Zahlen sind Ziel-/Nominalbezeichnungen. Tatsächliche Steigungen können
pegel- und zeitabhängig abweichen; siehe Prüfbericht. All ist nicht einfach eine
unendliche Ratio.

### Mix — 0 bis 100 %

- 100 %: vollständig bearbeiteter Pfad.
- 0 %: resamplingangepasster trockener Pfad **vor** Input/Output/Färbung.
- Dazwischen: lineare Mischung auf der hohen internen Rate.

Trocken und Wet teilen die Resamplingphase. Die zusätzliche Audiopfadfärbung
hat weiterhin ihre eigene Filterphase; `Mix` garantiert daher keinen Nulltest
gegen eine externe, unbearbeitete Parallelspur.

Für Dwarf-Parallelkompression den **internen Mix** bevorzugen. Eine separate
Pedalboard-Abzweigung kann wegen fehlender Host-Kompensation anders phasenliegen.

### Colour — 0 bis 100 %

Dosiert die Audiopfadfärbung: nichtlinearen FET-Anteil, DC-/Bandbegrenzung,
asymmetrische Verstärkerkennlinien und niederfrequente Sättigungszustände.
0 % ist der saubere Colour-Pfad; ein gewählter Transformator und die Feedback-Kompression bleiben
aktiv. Der Regler ist eine eigene Erweiterung und kein originaler Hardwareknopf.

### Compression

- **On:** dynamische FET-Regelung.
- **Off:** Audioverstärker-/Färbungspfad bleibt aktiv, dynamische Abschwächung
  ist aus. Input und Output können weiter Färbung erzeugen.

Ab Version 0.1.1 wird der vollständig ausgeschaltete Controller geparkt und
zurückgesetzt, um CPU zu sparen. Beim Einschalten baut er die GR mit seiner
Attack wieder auf; die Steuerung wird geglättet. Färbungszustände laufen bei
Compression Off weiterhin normal. Das ist eine digitale Betriebsentscheidung.

### Oversampling — Off / 2x / 4x

Separate Qualitäts-/CPU-Auswahl ab Version 0.2.0, Standard **Off**:

- **Off:** interne Verarbeitung mit der Hostrate; der CPU-günstigste Referenzpfad.
- **2x/4x:** Audiopfad **und** Regelkreis laufen mit der zwei- bzw. vierfachen
  Rate; das reduziert Aliasing der Färbung und des FET-Teilers, kostet aber
  entsprechend Rechenzeit.
- Die nominal gemeldete Latenz beträgt **0 Frames (Off), 3 Frames (2x),
  4 Frames (4x)**; die IIR-Phase ist frequenzabhängig und bleibt auch im
  internen Bypass erhalten.
- Eine Umschaltung im laufenden Signal blendet über etwa 2 ms aus, wechselt
  dann die Filterzustände und blendet wieder ein; der Latenzport folgt nach
  Abschluss der Ausblendung. Kurze Pegelschwankungen während des Wechsels sind
  möglich; Knackfreiheit im realen Host wird extern geprüft.
- Historische Last ohne Transformator (0.2.0, x86-Referenzbuild, Stereo, 48 kHz, Bestwert
  über fünf Durchläufe, keine Dwarf-Aussage): Off/Colour 0 = 1,0×;
  Off/Colour 100 ≈ 2,1×; 2x/Colour 100 ≈ 4,2×; 4x/Colour 100 ≈ 7,7×. Die
  Färbung enthält den nichtlinearen Kern (FET-Teiler mit Wurzeloperation plus
  drei Sättigungspolynome) und verdoppelt die Last gegenüber Colour 0; das
  Oversampling vervielfacht die Subframenzahl entsprechend der Rate. Für
  sparsamen Betrieb Colour und OS zurücknehmen; auf dem Dwarf vor Ort messen.
  Die zusätzliche 0.4.0-Transformatorlast ist separat in `PERFORMANCE.md` gemessen.
- JSFX-Selektor, importierte Factory-Bänke und LV2-Factory-Presets setzen
  Oversampling auf Off.
- Anders ist der **Transformator**: er ist eine Klangwahl und wandert mit dem
  Preset. Beim Recall startet er also auf dem Wert des Presets und sonst auf
  `None`. Belegt in 6 von 38 Presets — *Guitar Colour Only* (`60s`), *Vintage Blue Grit* (`60s`), *Guitar Cruncher* (`80s`), *Bass Mojo Bite* (`80s`), *Huge Sub Weight* (`00s`), *Snare Saturated Parallel* (`80s`).

### Transformator — None / 60s / 80s / 00s / Symmetric

Ab 0.4.0 hörbar **nach Input und vor der Kompressorstufe**, unabhängig von Colour:

- **None:** kein Transformator; bisheriger Klangpfad.
- **60s:** warm, weiche/frühe Tiefbasssättigung, stärker abgerundete Höhen.
- **80s:** ausgewogene Zwischenstufe mit moderater Tiefbasssättigung.
- **00s:** clean, größter Tiefbass-Headroom und geringe HF-Färbung.
- **Symmetric:** lineare technische Referenz, keine weitere Vintage-Stufe.

Input bestimmt die Anregung; Output anschließend zum Pegelvergleich einstellen.
Compression Off lässt die Stufe aktiv, Mix 0/Enabled Off umgehen sie.
Der Modellwechsel blendet über den Eingang aus/ein (je etwa 2 ms).
OS Off/2x/4x gilt auch für den Transformator; nominale Latenz bleibt 0/3/4 Frames.
Die Stufe ist ein partiell datenblattgefittetes Gray-Box-Modell. HF-Phase und
Aliasverhalten sind nicht mit analoger Hardware gleichzusetzen.

Spätere Bank-Refits können den Klang gespeicherter Projekte verändern.
Für reproduzierbare Projekte die verwendete Plugin-/JSFX-Version behalten;
technischer Refit-Weg: `DSP.md`.

### Enabled / Bypass

- `Enabled=On`: normaler Betrieb.
- `Enabled=Off`: interner, geglätteter Bypass auf den resamplingangepassten
  trockenen Pfad. Input und Output werden dabei umgangen.

Im vollständigen internen Bypass rechnet ab 0.1.1 nur noch die identische
Resamplingkette; Audiopfad-/Controllerzustände werden einmal zurückgesetzt.
Die IIR-Phase und nominelle Latenz bleiben dadurch auch im Bypass erhalten.

Beim Dwarf bedient der normale Bypass-Schalter diesen `lv2:enabled`-Port.
REAPERs äußerer Host-Bypass ist eine andere Funktion: dessen Phase, Zustände und
PDC-Verhalten entscheidet REAPER. Für konsistente Vergleiche den **internen**
Enabled-Regler verwenden.

## 4. Anzeigen der JSFX-Fassung

Die LV2-Fassung hat absichtlich keine GR-/Level-Anzeige. JSFX zeigt:

- **MAX:** in jeder Gruppenkopfzeile stehender Maximal-Peak (Peak-Hold) in
  dBFS, über den Peak-Indikatoren. Die Zahlen aktualisieren sich bewusst
  nur etwa drei Mal pro Sekunde; der Hold selbst hält zwei Sekunden.
- **IN:** Peak dBFS vor Input, RMS-Linie, Hold-Marker und Clip-Flag des Eingangs.
- **GR:** tatsächlicher dynamischer Regelgain in dB, vor Mix und Output.
  Ein kleiner Mixwert macht die angezeigte Wet-GR nicht kleiner.
- **OUT:** Peak dBFS, RMS-Linie und goldene Peak-Hold-Linie.
- **Skala:** −60 bis **0 dBFS**; 0 dBFS ist digitales Clipping, über 0 gibt es
  nichts. Farbzonen: unter −30 dunkelgrün, ab −30 hellgrün, **ab −12 orange,
  ab −3 rot**; das Clip-Flag und die rote Leuchtmeldung greifen erst bei
  Samplewert ≥ 0 dBFS. Keine True-Peak-Messung.
- **PK-Zahlen zeigen den Peak-Hold**, nicht den schnell fallenden Peak: der
  Hold bleibt etwa **2 s** stehen und fällt danach weich ab. Der Peak selbst
  fällt im Balken nach etwa 350 ms, der RMS-Zustand folgt nach etwa 300 ms.
- Kopfbereich zeigt rechts die aktive OS-Stufe (OS OFF / 2x / 4x).

RMS wird mathematisch als `20 log10(sqrt(mean(x²)))` dargestellt. Ein Sinus mit
0 dBFS **Peak** hat daher ungefähr **−3,01 dBFS RMS**. Es gibt keinen versteckten
AES17-Offset und keine LUFS-Anzeige.

REAPER 7 erhält zusätzlich `ext_gr_meter` als negative GR des vorherigen Blocks,
bei Dual Mono die stärkste Kanalabschwächung. Die Hostanzeige folgt nicht dem
Output-Makeup oder der Färbung-Lautheit. Die Grafik liest Momentaufnahmen;
Öffnen/Schließen verändert den Audiokern nicht.

Titel und OS-Stufe stehen in der Fußzeile und in der Kompaktansicht hinten;
im MCP-/Mixer-Embedding von REAPER ist nur der obere UI-Streifen sichtbar,
deshalb beginnen die Kennzahlenzeilen (IN/GR/OUT) direkt am oberen Rand.

## 5. Erster Arbeitsablauf

1. Das richtige Mono-/Stereo-Routing wählen. Extrem heißen Eingangspegel vorher
   im Track-/Pedalboard-Signalweg reduzieren.
2. `01 Neutral Start` oder ein Instrument-Preset laden.
   „Neutral“ ist hier ein allgemeiner Startpunkt mit Colour 100 %, kein
   transparenter Pfad. Für reine Dynamik Colour 0 und Transformer None wählen.
3. Input langsam erhöhen, bis typische Spitzen die gewünschte GR zeigen.
   Auf dem Dwarf nach Gehör und Pegelvergleich arbeiten.
4. Attack so einstellen, dass Frontkante und Körper zusammenpassen.
5. Release im Songtempo hören: atmet der Klang, bleibt er zu lange gedrückt,
   oder kehrt er zu hektisch zurück?
6. Output so einstellen, dass Enabled On/Off ähnlich laut wahrgenommen wird.
7. Erst danach Colour und gegebenenfalls Mix abstimmen.
8. Im vollständigen Mix vergleichen. Lauter klingt oft scheinbar besser;
   bei einem lauteren Preset zunächst Output reduzieren.

Die Beschreibung der NAM-Captures `~−21 dBFS = 0 dBu` ist lediglich eine
provisorische Referenz. Green Stripe setzt keine universelle Dwarf-/Interface-
Spannungskalibrierung voraus und verändert nicht automatisch Pegel danach.

## 6. Instrument-Workflows

### Vocals

Ein natürliches Vocal-Preset als Start: 4:1, langsamerer Attack, mittlerer/schnellerer
Release. 3–5 dB GR hält den Pegel zusammen, ohne Atem und Satzenden unnötig
aufzuziehen. Für Peaks ein Peak-Catch-Preset, bei Rock stärkere Regelung wählen.

Laut der Vocal-Praxisquelle kann man zu Lernzwecken absichtlich übertreiben:
Attack schnell, Release langsam und Input bis 12–15 dB GR. Danach Attack wieder
langsamer stellen und hören, wie Frontkante zurückkommt. Diese Übung ist kein
Standard-Preset für jede Stimme. All Buttons/7-7 ist ein ausdrücklicher Effekt.

### Bass

Ein Finger-Bass-Preset erhält den Körper; ein Pick-Bass-Preset bewahrt mehr
Anschlag. Bei Tieftonknattern Release verlängern oder Input/Colour reduzieren.
Grit-Presets nutzen diese Rauheit absichtlich. Unterschiedlich gespielte
Noten benötigen Input-Anpassung; kein Preset kann die Aufnahme ersetzen.

### Kick, Snare, Toms

Attack niedriger, um Frontkante zu erhalten; Release so wählen, dass zwischen
Schlägen Erholung möglich ist. Die Kick-, Snare- und Tom-Presets
sind Ausgangspunkte. Dual Mono ist für getrennte Quellen gedacht, nicht als
automatisch bessere Stereobehandlung.

### Overheads und Raum

Für natürlichere Overheads ein sanftes Preset, Link On und kleine GR.
All Buttons ist ein starker Raum-Effekt. Für die gesamte Drumgruppe
Parallel-Crush wählen: Input im Wet-Pfad kräftig, Output pegelgleichen,
Mix zunächst etwa 25 %. Transienten können trotz hoher GR herausragen.

### Elektrische und akustische Gitarre

Clean-Sustain nach Amp/Cab ausprobieren. Bereits verzerrte Gitarren
haben oft wenig verbleibende Dynamik: Rhythmuskompression zurückhaltend dosieren.
`Guitar Colour Only` nutzt nur den Audiopfad samt 60s-Transformator.
Strumming/Fingerpicking haben eigene Startwerte; Pickgeräusche und Raumrauschen kontrollieren.

### Piano, Rhodes, Synths und Bus

Piano bewusst vorsichtig komprimieren; All Buttons ist hier selten ein neutraler
Start. Rhodes und Synth-Leads können mehr Körper bekommen. Synthbass braucht
auf langen tieffrequenten Noten ruhige Release. Subtile Stereo-Bus-Einstellungen
sind kreative Startpunkte, keine Mastering-Empfehlung.

Die verbindlichen aktuellen Namen, Gruppen und Nummern aller 38 Presets
stehen in der generierten Tabelle `PRESETS.md`.
Ab 0.4.1 verwenden **21 Kick Weight** und **22 Snare Crack** langsamere
Attackwerte 2 bzw. 3 statt 5. Erneuter Factory-Recall lädt diese Korrektur;
gespeicherte eigene Projekte behalten ihre Parameterwerte. 37/38 sind
angehängt, damit sich die ersten 36 Selektorpositionen nicht verschieben.
Die erneute Einzelprüfung steht in `EXTERN.md`: Ziel-GR gilt immer
vor Mix und erst nach Input-Abgleich. Auch „Gentle“ kann bei heißer Quelle
kräftig regeln. Preset **08 Vocal Transformer** bezeichnet den quelleninspirierten
Colour-only-Trick; der separate Transformator steht dort bewusst auf None.

## 7. Presets laden und speichern

### Eingebauter Selektor

`Instrument preset` lädt alle Klangregler einschließlich Enabled, Stereo Link und
Transformator. Das Oversampling wird bewusst **nicht** übernommen und startet auf
Off, weil es eine Qualitäts-/CPU-Wahl ist. Beim anschließenden manuellen
Verändern wird die Auswahl auf **Custom** gesetzt.
Zum erneuten Laden zuerst Custom, dann denselben Preset wählen, falls die
Auswahlliste bereits dessen Namen zeigt. REAPER speichert die eigentlichen
Reglerwerte mit dem Projekt.

### REAPER-Presetbank

Die zwei `.rpl`-Dateien sind vollständig mitgeliefert. In REAPER im FX-Presetmenü
**Import preset library (.rpl)** wählen und die passende Mono-/Stereo-Datei
laden. Die Bänke wurden zusätzlich mit dem ysfx-RPL-Lader überprüft; REAPERs
Import und Projekt-Recall werden auf dem anderen Rechner abgenommen.

Eigene Ergebnisse unter neuen Namen speichern. Die eingebauten Presets sind
Ausgangspunkte, keine automatischen Instrument-Erkenner.

## 8. Fehlersuche

| Symptom | Prüfen |
|---|---|
| Mono-JSFX bleibt stumm | Quelle muss auf Input L liegen |
| Wenig GR | Input erhöhen, Compression/Enabled prüfen, Ratio-Einsatz beachten |
| Zu rau/knatternd | Input, Colour und schnelle Release reduzieren |
| Sterebild wandert | Stereo Link On; Routing und unterschiedliche Kanalquellen prüfen |
| GR groß, Effekt klein | Mix-Wet-Anteil prüfen; GR wird vor Mix angezeigt |
| Bypass nullt nicht mit roher Spur | IIR-Phase und nominelle, nicht exakte PDC |
| Preset wirkt anders als erwartet | Aufnahmepegel und Input/Output pegelgleichen |
| Dwarf lädt Plugin nicht | aarch64- und glibc/GLIBCXX-ABI, TTL und Bundlepfad prüfen |
| Geräte-CPU zu hoch | Andere Plugins isolieren, 256 Frames vergleichen, Prüfbericht erstellen |

Für reproduzierbare Tests siehe `MESSTECHNIK.md`. Färbungs-/Hörabgleich mit einem
Originalgerät oder NAM-Core ist noch kein bestandener Teil dieser Anleitung.
Ein ausführbarer Loopback-/Testtonworkflow für die **Scarlett 2i2 1st Gen**
steht in `MESSTECHNIK.md`: Mess-WAV erzeugen, aufnehmen und Pegel,
Frequenzgang sowie THD/THD+N mit direkter Kabelreferenz auswerten.


---

<!-- ===== Teil 2: Quelle docs/BUILD.md ===== -->

# Build, ABI und Paketierung

## 1. Native Linux-Entwicklung

Benötigt: C++11-Compiler, GNU Make, Python 3. Bereits generierte Metadaten und
PNG-Assets sind enthalten; Nutzer benötigen weder Playwright/Pillow noch ysfx.

```bash
make
make test
python3 tools/check_abi.py build/native/green-stripe-76.lv2/green-stripe-76.so
python3 tools/package.py --bundle build/native/green-stripe-76.lv2 --toolchain "native compiler/version"
```

Optional stärkere TTL-Validierung:

```bash
python3 -m pip install rdflib
python3 tools/validate.py
```

Alternativer CMake-Build:

```bash
cmake -S . -B build/cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build/cmake
ctest --test-dir build/cmake --output-on-failure
```

Der CMake-Wrapper ist Linux-zielorientiert. DSP-Tests können auch unter Windows
gebaut werden; native Windows-/macOS-LV2-Metadatennamen sind nicht Teil des
Dwarf-Lieferziels. Für REAPER auf diesen Systemen JSFX verwenden.

### WSL ohne Root

Falls in einer WSL-Distribution kein Compiler installiert ist und `sudo` kein
Passwort akzeptiert, lässt sich eine funktionierende Toolchain **ohne Root**
aus Paketarchiven in ein eigenes Präfix legen. Die Debian/Ubuntu-Archive
lassen sich mit `apt-get download` (ohne privileges) und `dpkg-deb -x` entpacken.

```bash
mkdir -p /tmp/debs /tmp/sysroot && cd /tmp/debs
for p in make g++ gcc cpp gcc-11-base libgcc-11-dev libstdc++-11-dev \
         libc6-dev linux-libc-dev libisl23 libmpc3 cmake cmake-data \
         libarchive13 librhash0 libjsoncpp25; do
  dpkg -s $p >/dev/null 2>&1 || { apt-get download $p && dpkg-deb -x ${p}_*.deb /tmp/sysroot; }
done
```

Drei Feinheiten sind dabei zwingend, sonst findet der Build nichts:

1. **`make` nutzt `g++`, nicht `c++`.** `CXX ?= c++` im Makefile überschreibt
   den Make-Default nicht, weil Built-in-Variablen als *gesetzt* gelten. Es
   müssen daher Symlinks `g++`, `gcc`, `cc`, `c++` im Präfix liegen.
2. **Multiarch-Include fehlt in der Standardsuche.** `bits/wordsize.h` und
   `linux/errno.h` liegen unter `usr/include/x86_64-linux-gnu`, das weder
   `C_INCLUDE_PATH` noch `CPLUS_INCLUDE_PATH` von sich aus abdecken.
3. **`libc.so` ist ein Linker-Script mit absolutem Pfad.** Es verweist auf
   `/usr/lib/x86_64-linux-gnu/libc_nonshared.a`, das ohne Root nicht angelegt
   werden kann. Abhilfe: das Script im Präfix auf den Präfixpfad umschreiben und
   dieses Verzeichnis per `-L` **vor** die Systempfade zu legen.

```bash
S=/tmp/sysroot
for l in g++-11:g++ gcc-11:gcc gcc-11:cc g++-11:c++ cpp-11:cpp; do
  ln -sf "$S/usr/bin/${l%%:*}" "$S/usr/bin/${l##*:}"
done
mkdir -p "$S/libfix"
sed "s#/usr/lib/x86_64-linux-gnu/libc_nonshared.a#$S/usr/lib/x86_64-linux-gnu/libc_nonshared.a#" \
  "$S/usr/lib/x86_64-linux-gnu/libc.so" > "$S/libfix/libc.so"
export PATH="$S/usr/bin:$PATH" GCC_EXEC_PREFIX="$S/usr/lib/gcc/"
export C_INCLUDE_PATH="$S/usr/include:$S/usr/include/x86_64-linux-gnu"
export CPLUS_INCLUDE_PATH="$S/usr/include/c++/11:$S/usr/include/x86_64-linux-gnu/c++/11:$S/usr/include/c++/11/backward:$S/usr/include:$S/usr/include/x86_64-linux-gnu"
export LIBRARY_PATH="$S/usr/lib/x86_64-linux-gnu:$S/usr/lib/gcc/x86_64-linux-gnu/11"
export LD_LIBRARY_PATH="$S/usr/lib/x86_64-linux-gnu"
export LDFLAGS="-L$S/libfix"
make BUILD_DIR=build/wsl test
```

Für die Paritätsprüfung zusätzlich cmake im Präfix, dann Abschnitt 5 mit
`cmake -S tests -B build/parity-wsl -DYSFX_SOURCE_DIR=/tmp/opencode/ysfx`.

**Diese Variante ersetzt kein `sudo apt install build-essential cmake`**, wenn
das möglich ist: sie ist ein Notbehelf für Gate-Läufe in einer gesperrten
Umgebung. Der Buildroot-Rezept für das Dwarf-Ziel bleibt davon unberührt.

## 2. Reproduzierbarkeit

- Alle Tabellen/Ports/Presets aus `data/*.json`.
- `python3 tools/generate.py` aktualisiert die Textartefakte.
- `make check-generated` erkennt Abweichungen.
- `python3 tools/make_assets.py` rendert HTML/CSS und die bereitgestellten
  Assets in Chromium (Playwright und Pillow nur für diesen Entwicklungsschritt).
  Optional `--browser /pfad/zu/chromium`; es entstehen lokale Vorschauen,
  keine Dwarf-Screenshots.
- `data/model.json` referenziert die versionierte `data/transformers.json`.
  Refit-Import/Validierung und gemeinsame C++-/EEL2-Generierung:
  `DSP.md`. Neue Bank erfordert Neubuild bzw. neue JSFX-Includes.
- Je Buildziel **eigenes BUILD_DIR** verwenden. Make kann einen Compilerwechsel
  nicht allein an Binär-Zeitstempeln erkennen.
- MPB-/Compilerrevision und Compileflags im externen Prüfprotokoll festhalten.

## 3. Bevorzugter Dwarf-Build: offizieller MOD Plugin Builder

Ziel `moddwarf-new`: GCC 9.4, glibc 2.27, AArch64/Cortex-A35. Das ältere
`moddwarf` nutzt GCC 7.5. Der reale Kernel 6.1.15 des Geräts bedeutet **nicht**,
dass mit der glibc eines aktuellen Ubuntu gebaut werden darf.

Auf Linux/WSL einen MPB-Checkout auf einem Dateisystem **ohne Leerzeichen**
vorbereiten, beispielsweise `/home/user/mod-plugin-builder`:

```bash
git clone https://github.com/mod-audio/mod-plugin-builder.git /home/user/mod-plugin-builder
docker buildx build --load -t mpb-moddwarf-new \
  --build-arg platform=moddwarf-new --build-arg target=minimal \
  /home/user/mod-plugin-builder/docker
```

Dann Projekt nach `/root/source` mounten:

```bash
docker run --rm -it \
  --mount "type=bind,source=/absolute/path/mod-1175-lv2,target=/root/source" \
  mpb-moddwarf-new
```

Im Container:

```bash
bash /root/source/tools/build_dwarf.sh
```

Das Skript sourced `local.env moddwarf-new`, baut in `build/moddwarf`, prüft
Architektur/GLIBC-Floor und schreibt Distributionspakete. Es veröffentlicht oder
installiert nicht auf dem Gerät. Docker-Engine/WSL-Integration müssen funktionieren.

Das aktuelle MPB-Dockerfile klont upstream selbst. Für einen freigegebenen Build
den resultierenden Checkout-Commit und Image-Digest festhalten; Image-Tag alleine
garantiert keine unveränderliche Toolchain.

### Buildroot-Rezept

`packaging/mod-plugin-builder/green-stripe-76/green-stripe-76.mk` ist für den
**MOD Cloud Builder** (`builder.mod.audio`, Pfad `/buildroot`) und für ein
lokales MPB geeignet. Dort gilt:

- Es wird **genau eine Datei** akzeptiert: die `.mk`. Es kann **kein Sourcearchiv**
  hochgeladen werden. Die Quelle muss daher über `_SITE` bezogen werden; ein
  lokales `SITE_METHOD = local` mit `/root/source` schlägt dort mit
  `ERROR: /root/source does not exist` fehl.
- `_VERSION` ist der **Commit-SHA**, nicht `0.2.0`. Buildroot klont diesen Stand.
  Vor jedem Build den gewünschten Commit pushen und den SHA in der `.mk` eintragen;
  der Builder baut ausschließlich den committeten Zustand, nie den Working Tree.
- Die erste Zeile der `.mk` muss ein Kommentar sein. Der Builder leitet den
  Paketnamen aus dem Text **vor** dem ersten `_VERSION = ` ab; beginnt die Datei
  direkt mit `PRAEVERSION_`, lehnt er das Rezept als "Invalid package version" ab.
- Der Builder benennt das Paket selbst um (temporärer Verzeichnisname als
  Prefix). Der eigene Variablenname ist daher frei wählbar; entscheidend sind nur
  `_VERSION`, `_BUNDLES` und `$(eval $(generic-package))`.
- `_BUNDLES` bleibt einzeilig und enthält genau ein Bundle.

Für einen lokalen MPB-Lauf genügt dasselbe Rezept:

```bash
mkdir -p mod-plugin-builder/plugins/package/green-stripe-76
cp packaging/mod-plugin-builder/green-stripe-76/green-stripe-76.mk \
   mod-plugin-builder/plugins/package/green-stripe-76/
cd mod-plugin-builder
./build moddwarf-new green-stripe-76
./build moddwarf-new green-stripe-76-rebuild
```

Bei großen Buildsystemänderungen `-dirclean` erwägen.
`DESTDIR/PREFIX=/usr` wird eingehalten. Der DSP braucht keine LV2-Dev-Library:
enthalten ist nur der schmale C-ABI-Header. MPB reicht `CC`/`CXX`/`CPPFLAGS`/
`CXXFLAGS`/`LDFLAGS` als Make-Commandline-Variablen durch; die `+=`-Zeilen der
Projekt-Makefile werden dadurch überstimmt, `PROJECT_CXXFLAGS` steht weiterhin
zuletzt und setzt explizit `-fno-fast-math` und `-ffp-contract=off` gegen das
`-ffast-math` aus `BR2_TARGET_OPTIMIZATION`.

## 4. Zusätzlich erzeugter AArch64-GCC9-Build

In dieser Session war Docker nicht erreichbar. Als separates, klar markiertes
Artefakt wurde die offizielle **Arm GNU-A 9.2-2019.12**-Toolchain verwendet:

- Download: `https://developer.arm.com/-/media/Files/downloads/gnu-a/9.2-2019.12/binrel/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu.tar.xz`
- SHA256: `8dfe681531f0bd04fb9c53cf3c0a3368c616aa85d48938eebe2b516376e06a66`
- Compiler: `aarch64-none-linux-gnu-g++` 9.2.1.

Reproduktionsbefehl nach Installation dieses Archivs:

```bash
make BUILD_DIR=build/aarch64-gcc9 \
  CXX=/absolute/arm-toolchain/bin/aarch64-none-linux-gnu-g++ \
  CPPFLAGS="-Isrc -DGS_GLIBC_217" \
  CXXFLAGS="-O3 -mcpu=cortex-a35 -mtune=cortex-a35" \
  LDFLAGS="-Wl,--no-undefined -Wl,--as-needed"
python3 tools/check_abi.py build/aarch64-gcc9/green-stripe-76.lv2/green-stripe-76.so --dwarf
```

Diese Toolchain hat neuere Default-libm-Symbolversionen. `GS_GLIBC_217` bindet
**nur auf AArch64/Linux** exp/log/pow an deren ursprüngliche glibc-2.17-Versionen.
Es werden keine beliebigen Symbols verschleiert. Das erzeugte Binary benötigt
laut ELF nur `libm.so.6`, `libc.so.6`, **GLIBC_2.17**, kein GLIBCXX.

Dieser Build ist **kein offizieller MPB-Build und nicht auf Dwarf geladen**.
Für die endgültige Übergabe nach Möglichkeit zusätzlich MPB bauen und beide
Hashes/Verhalten vergleichen. Die ABI-Prüfung alleine ist kein Gerätetest.

## 4a. Standalone-Transformatorbench für den Dwarf

Reines Messprogramm ohne jackd, LV2 und Bedienung; es benutzt mit `-Isrc` die
unveränderten Produktheader. Gedacht für den Lauf direkt auf dem Gerät, siehe
`MESSTECHNIK.md`. Je nach Toolchain:

```bash
# Im MPB-Container
make BUILD_DIR=build/moddwarf transformer-bench

# Oder mit dem Arm-GCC9-Crosscompiler aus Abschnitt 4
make BUILD_DIR=build/aarch64-gcc9 transformer-bench \
  CXX=/absolute/arm-toolchain/bin/aarch64-none-linux-gnu-g++ \
  CPPFLAGS="-Isrc -DGS_GLIBC_217" \
  CXXFLAGS="-O3 -mcpu=cortex-a35 -mtune=cortex-a35"
```

Nur für die Diagnose wird zusätzlich `-DGS76_TRANSFORMER_STATS` gesetzt; das
Makro zählt Solveriterationen, ändert aber keinen Audiowert. Ein x86-Lauf ist
eine Vorhersage, keine Gerätemessung.

## 5. JSFX-Paritätsprüfung

Entwicklungsabhängigkeit: JoepVanlier/ysfx, Commit
`5c3452fee62583aa3d1b7e877d0c758c4024af89`. Runtime-Plugins benötigen ysfx nicht.

```bash
git clone https://github.com/JoepVanlier/ysfx.git /absolute/ysfx
git -C /absolute/ysfx checkout 5c3452fee62583aa3d1b7e877d0c758c4024af89
git -C /absolute/ysfx submodule update --init thirdparty/dr_libs
cmake -S tests -B build/parity -DYSFX_SOURCE_DIR=/absolute/ysfx -DCMAKE_BUILD_TYPE=Release
cmake --build build/parity
build/parity/jsfx_parity jsfx/GreenStripe76-Mono.jsfx jsfx/GreenStripe76-Stereo.jsfx
build/parity/benchmark_jsfx jsfx/GreenStripe76-Mono.jsfx jsfx/GreenStripe76-Stereo.jsfx 2 7
```

Die GFX-Smoke-Testdatei `tests/jsfx_ui.cpp` kann gegen ein ysfx mit
`YSFX_GFX=ON` gelinkt werden. Sie schreibt ein PPM und prüft unveränderten
Controllerzustand nach GFX-Frames. Fonts sind optional; authoritative REAPER-
Darstellung weiterhin extern prüfen.

Das Test-CMake überprüft selbst denselben upstream-Assembly-SHA512, bevor es
den falsch auf `CMAKE_SOURCE_DIR` zeigenden eingebetteten ysfx-Checksumtarget
deaktiviert. Keine Prüfsumme wird ungeprüft umgangen.

## 6. Pakete

```bash
python3 tools/package.py \
  --bundle build/moddwarf/green-stripe-76.lv2 --dwarf \
  --toolchain "MPB moddwarf-new COMMIT / compiler version"
```

- JSFX-ZIP: alle `.jsfx`, sieben Includes, `.rpl`, Anleitung, Lizenz und
  Transformatorbank/Runtime-Vertrag zur Herkunfts- und Refit-Dokumentation,
  außerdem Presetprüfung/2:1-Vorschläge (`EXTERN.md`, `PRESET_AUDIT.json`).
  Scarlett-Anleitung und separates Skript/Requirements unter `tools/` sind
  ebenfalls enthalten; dessen Pythonpakete werden nicht mitgeliefert.
- Source-ZIP: DSP, Metadaten, Werkzeuge, Tests, Doku und AGENTS.
- LV2-tar.gz: Bundle direkt im Archivroot, ideal für SDK-Upload.
- Herkunftsmanifest: Architektur, DT_NEEDED, Symbolversionen, Binärhash,
  Toolchainbeschreibung und `device_tested=false`.
- `SHA256SUMS`: Übertragungsprüfung.

NAM-/WAV-Dateien, gepackte Offline-Hördateien, Hersteller-PDFs, NPZ-Rohdaten,
`.git`, temporäre Toolchains und Buildartefakte werden nicht im Source-/JSFX-
Paket verteilt. `--dwarf` verweigert x86_64 oder glibc >2.27.
Aktuelle Projektversion **0.4.1** mit 38 Presets und korrigierter Attack in 21/22.
Transformatorprofile sind seit 0.4.0 hörbar. Version und Bankrevision prüfen.
Vorhandene alte Cross-Binaries sind kein 0.4.1-Build. Die lokale Prüfung
verwendet GCC 15.2 auf x86_64; der aktuelle MPB-/Dwarf-Build ist extern offen.

Audiointerface-Messwerkzeug separat: `python -m pip install -r tools/requirements-scarlett.txt`.
NumPy/SoundFile für Offlineanalyse, sounddevice/PortAudio für Live-I/O;
keine neue Plugin-Laufzeitabhängigkeit. Workflow in `MESSTECHNIK.md`.


---

<!-- ===== Teil 3: Quelle docs/INSTALLATION.md ===== -->

# Installation und Übergabe auf den anderen Rechner

## 1. Dateien übertragen

Den vollständigen Projektordner oder `dist/*-source.zip` übertragen. Zum direkten
JSFX-Test `*-jsfx.zip`; für Dwarf das explizite `*-moddwarf.tar.gz` verwenden.
Dateien und `SHA256SUMS` gemeinsam mitnehmen.
Für diesen Stand **0.4.1** verwenden. Alte 0.1.x/0.2.x/0.3.x-Binaries enthalten
die neue Transformatorstufe nicht. Bei Refits zusätzlich Bankrevision aus
`data/transformers.json` festhalten; sie verändert den Klang gespeicherter Profilnummern.

```bash
sha256sum -c SHA256SUMS
```

Source enthält `AGENTS.md`, Testtools und Dokumentation. Die vier lokalen NAM-
Profile müssen für spätere Referenzmessungen separat bereitgestellt werden,
idealerweise mit `desc.txt`; sie sind nicht im Plugin-Paket.

## 2. REAPER 7

1. **Options → Show REAPER resource path in explorer/finder**.
2. Unter `Effects` einen Ordner `GreenStripe76` anlegen.
3. Aus dem JSFX-ZIP den **Inhalt** des GreenStripe76-Ordners vollständig kopieren.
4. FX-Liste neu scannen oder REAPER neu starten.
5. `JS: Green Stripe 76 Mono/Stereo` auf einer Testspur einfügen.
6. Instrumentpreset am Slider wählen oder im normalen Presetmenü die passende
   `.rpl`-Bibliothek importieren.

Keine separate SWS-/ReaPack-/NAM-/JUCE-Installation nötig. Includes müssen neben
den Hauptdateien liegen. Auf der Stereo-Version ist Link sichtbar; Mono zeigt
ihn nicht und verarbeitet nur linken Input.

Erst Routing, 0/100-%-Mix und GR-/Level-Funktion testen. Danach Projekt speichern,
schließen, wieder öffnen; Klangregler und Presetwerte müssen erhalten bleiben.
Die 2:1-Varianten aus `EXTERN.md` stehen jetzt als Factory-Presets 37/38
bereit. 21/22 haben neue Attackwerte beim Recall; alte Projektwerte bleiben
gespeichert. Die Prüfung enthält auch den
absichtlichen Transformer-None-Zustand von „08 Vocal Transformer“.

## 3. MOD Dwarf

Geräteangaben für das Protokoll:

```text
OS: 1.13.5.3315
Machine: aarch64
Kernel: 6.1.15-rt7-moddwarf
Version: #6 SMP PREEMPT_RT
```

Prüfen, dass es ein AArch64-Bundle ist. Kein `native-x86_64`-Archiv installieren.
MPB-Build bevorzugen; zusätzlich gelieferter Arm-GCC9-Build ist ABI-geprüft,
aber extern noch zu laden.

USB-/Netzverbindung zur Web-GUI herstellen. Standardadresse
`http://192.168.51.1`, alternativ `http://moddwarf.local`. Installationsprotokoll
der MOD-SDK-Schnittstelle: **Base64 des gzip-Tarballs als Multipart package**.

```bash
base64 < "green-stripe-76-0.4.1-moddwarf.tar.gz" | \
  curl --fail --show-error -F 'package=@-' http://192.168.51.1/sdk/install
```

Zusätzlich den JSON-Rückgabewert `ok` prüfen. Normaler erfolgreicher Upload
rescannt die Plugins; bereits aktive Instanzen bei Binary-Austausch neu anlegen.
In der Pluginliste sollten **Green Stripe 76 Mono** und **Stereo** erscheinen.

`tools/package.py` legt im tar.gz nur das Bundle im Root an, nicht Dokumentation
oder Herkunftsmanifest. Letzteres liegt neben dem Archiv.

### Pedalboard

- Mono: ein In-/Out-Port.
- Stereo: beide Kanalports verbinden. Link ist ein normaler adressierbarer
  Toggle; Off entspricht unabhängiger Regelung.
- Input/Output/Attack/Release/Ratio/Compression/Mix/Colour an Hardware-Regler
  zuweisen, Snapshot speichern und Recall testen.
- Transformator/OS zuweisen und Wechsel prüfen; Paneel am oberen Rand bewegen,
  Mode und Bypass klicken, Aluminiumregler ohne Paneelbewegung bedienen.
- Das UI enthält **keine Meter**; auch die Firmware-LCD-GR-Anzeige ist kein Ziel.
- Für Messungen eingebautes Dwarf-Input-Noise-Gate und Output-Kompressor
  deaktivieren, Pedalboard-Output-Gain und Input-Gain dokumentieren.
- 128 und 256 Frames vergleichen. Eine neue Instanz sollte bei Umschaltung
  korrekt zurücksetzen; die verbundenen Ports müssen erhalten bleiben.

## 4. Native Linux-LV2 zum Vergleich

```bash
make install PREFIX="$HOME/.local"
```

Installation nach `~/.local/lib/lv2/green-stripe-76.lv2`; Hostscan durchführen.
Gegebenenfalls `LV2_PATH` ergänzen. Alternativ Bundle nach `~/.lv2/` kopieren.
Nicht mit dem Dwarf-Binary auf x86 testen.

## 5. Ergebnisübergabe an die nächste Session

Für die Scarlett-Messung auf dem Audio-Rechner die Entwicklungsabhängigkeiten
aus `tools/requirements-scarlett.txt` installieren, `devices` aufrufen und
`MESSTECHNIK.md` abarbeiten. Das Plugin selbst benötigt diese Pakete nicht.

`docs/MESSTECHNIK.md` ausfüllen, in beispielsweise
`test-results/2026-10-03-dwarf-reaper.md` speichern und dem Agenten übergeben.
Rate/Blocksize/Architektur, Binärhash, Preset, Rohinput und Output festhalten.
Screenshots und Audio nur mit klaren Dateinamen/Reglerangaben beifügen.
Dann `docs/PROJEKT.md` gezielt aktualisieren — Geräte-/Hörtest erst nach Ausführung
als bestanden markieren.
