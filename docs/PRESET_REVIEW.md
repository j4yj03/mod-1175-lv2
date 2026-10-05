# Prüfung aller Instrument-Presets — 0.4.1

Stand **2026-10-05**. Basis: `data/presets.json`, `data/parameters.json`,
`data/model.json`, aktuelle Transformatorbank und bestehende Quellenzuordnung.
**38 Presets** nach ausdrücklichem Korrektur-/Erweiterungsauftrag:
21 Kick Weight erhält Attack **2 statt 5**, 22 Snare Crack **3 statt 5**,
damit beide weniger Frontkante abregeln. Die vorherigen 2:1-Vorschläge sind
als **37 Piano Gentle 2:1** und **38 Stereo Bus Subtle 2:1** angehängt.
Nummern/Namen 01–36 bleiben erhalten; neue Varianten haben eigene URIs und
Selektorplätze. Bestehende Hostprojekte behalten gespeicherte Parameter;
erneuter Factory-Recall von 21/22 lädt die neuen Attackwerte.
Diese beabsichtigte Klangänderung ist als **0.4.1** versioniert.

## 1. Tatsächliche Prüfung und Befund

- **76 Zustände:** alle Mono-/Stereo-LV2-Factory-Presets und RPL-Zustände
  gegen sämtliche Werte aus `data/presets.json` abgeglichen, inklusive
  Enabled, Link, Oversampling, Transformer und Custom-Selektorzustand.
- **228 Renderfälle:** jedes Preset in Mono und Stereo bei Off/2x/4x,
  48 kHz, deterministisches Signal, pro Fall frischer Processor.
  Endliche Audio-/GR-Werte; beide Compression-Off-Presets exakt 0 dB GR.
- **12 Zusatzfälle:** Piano Gentle und Stereo Bus Subtle jeweils 4:1/2:1
  bei −18/−12/−6 dBFS Peak. Signalwerte unten.
- Ratioverteilung bei aktiver Compression: **2 × 2:1, 22 × 4:1, 9 × 8:1,
  3 × All Buttons**. Zwei weitere Presets sind Compression Off und speichern
  inaktiv 4:1. Kein Factory-Preset nutzt 12:1 oder 20:1.
- Die sechs Transformatorzuordnungen sind stimmig mit den eigenen Profilen:
  **11/12 → 60s, 13/19/24 → 80s, 20 → 00s**. Alle anderen `None`.
- **25 Toms Body und 30 Percussion Snap** rufen in Stereo Dual Mono auf;
  sinnvoll für unabhängige Kanäle, für zusammengehörige Stereopaare Link aktivieren.
- OS wird über alle Factory-Recall-Wege auf Off gesetzt. Die Referenzwerte
  in der Tabelle beziehen sich auf den Wet-Regler, nicht auf eine Änderung
  der Lautheit durch Mix oder Output.

Messdaten, Quellen-/Probehashes und Bedingungen: [`PRESET_AUDIT.json`](PRESET_AUDIT.json).
Die JSFX-Selector-/RPL-Paritätsprüfung ist zusätzlich in `TESTING.md` beschrieben.
Dies ist eine **Parameter-/Signalprüfung**, kein Hörurteil über Instrumentaufnahmen,
keine Geräteabnahme und keine Bestätigung universeller Ziel-GR-Werte.

### Zusätzlich gefundener Paritätsfehler

Historischer Befund der vorangegangenen 0.4.0-Prüfung; 0.4.1 enthält diese
Korrektur weiterhin. Aktuell 430 allgemeine + **76** Preset-Signalvergleiche.

Der bisherige Test verglich die 72 Bankzustände nur als Sliderwerte mit dem
Selektor und renderte dabei Stille. Der neue Signalvergleich aller Bankwerte
deckte bei **29 Drum Parallel Crush, Mono, 48 kHz/OS Off** eine Abweichung bis
**0,000409722 FS** auf. Alle Factorywerte und zuvor verglichenen Zustände
waren korrekt; der erste abweichende Solverzweig entstand bei Sample 702.

Ursache war die EEL2-Auswertung von `1+alpha-alpha*deriv`: Bei identischen
Operanden unterschied sich der Newton-Vorschlag um wenige ULP. Die strikte
Intervallprüfung wählte daraufhin Newton statt Bisektion, bei nur acht
Iterationen sichtbar im Ausgang. Der Nenner wird nun in C++ und EEL2 mit
expliziten Zwischenschritten ausgewertet. Toleranzen, Iterationszahl und
Presetparameter sind unverändert. **430 allgemeine plus 72 Preset-Signal-
vergleiche sind jetzt bitgleich (max. 0 FS)**; `make test` ebenfalls PASS.
Die JSFX kann in diesem Randfall dadurch anders als die frühere JSFX rendern;
das ist eine Paritätskorrektur, keine Preset-Neuabstimmung.
Der C++-Vorher-/Nachhervergleich gegen `c3153bf` besteht in **144 Fällen
bitgleich für Audio/GR/Latenz**; zusätzlich bestehen CMake/CTest 3/3.

### Messsignal für alle Presets

1,2 Sekunden: links 53/997/6011 Hz mit Gewichten 0,6/0,3/0,1;
rechts bei Stereo 79/313 Hz mit 0,4/0,2. Gemeinsame Amplitudenskalierung
−12 dBFS als **Spitzenobergrenze**, nicht normalisierter tatsächlicher Peak.
Hüllkurve 0,125 bis 0,15 s, 1 bis 0,65 s, 0,125 bis 0,8 s, danach Stille.
Messfenster für Mittelwerte 0,4–0,6 s; Spitzen-GR über die ganzen 1,2 s.

Der Input muss zur Quelle passen: Bereits **01 Neutral Start** erreicht in
dieser Probe ca. **8,46 dB** Spitzen-GR statt seiner Zielspanne 2–5 dB;
**31 Piano Gentle** ca. **6,04 dB**, **35 Stereo Bus Subtle** ca. **4,11 dB**.
Das ist kein falscher Presetindex, sondern die Folge von Pegel und
tiefer Detektorschwelle. Erst Input auf die Ziel-GR einstellen, dann Output
pegelgleichen und zuletzt Mix dosieren. Eine kleine Mixzahl reduziert nicht
die interne GR oder die Transformatoraussteuerung.

## 2. Einzelbewertung aller 38 Presets

„Stimmig“ bedeutet konsistente Absicht/Parameter, mit erforderlichem Input-
und Hörabgleich. Alle genannten GR-Ziele beziehen sich auf den Wet-Pfad.

| Nr. / Preset | Bewertung und Prüfpunkt |
|---|---|
| 01 Neutral Start | 4:1 als allgemeiner Einstieg stimmig. „Neutral“ ist kein transparenter Bypass: Colour 100 %, Compression On; Notiz präzisiert. |
| 02 Dr Pepper Inspired | 4:1, relativ langsamer Attack und flotter Release passen zur Idee; Input +3 ist eigene digitale Zuordnung, keine Uhrzeitkalibrierung. |
| 03 Vocal Natural | 4:1, Attack 3, Release 5 und Colour 75 plausibel; Atem/Endsilben und Input auf 3–5 dB abstimmen. |
| 04 Vocal Peak Catch | 8:1 und Attack 5,5 sinnvoll für Spitzen; kein Lookahead/Brickwall, nachfolgende langsamere Stufe möglich. |
| 05 Vocal Rock Forward | 8:1, Input +7, schnelle Zeiten und Colour 100 konsistent mit dichterem Effekt. |
| 06 Vocal Grit Parallel | All, hohe Anregung, 30 % Mix konsistent; 10–18 dB Ziel-GR gilt vor Mix. |
| 07 Vocal Squashed | 4:1 und 7/7 bleiben passend; Quellbeispiel ist Anregung, kein Nachweis gleicher Verformung im eigenen Modell. |
| 08 Vocal Transformer | Compression Off, Colour 100, Transformer None sind beabsichtigt. Quellen-Trickname wird ausdrücklich vom neuen Modellselektor abgegrenzt; Output-Abgleich nötig. |
| 09 Guitar Clean Sustain | 4:1, 80 % Mix, Colour 90 passen zur Sustain-Idee; „Clean“ bezeichnet die Quelle, nicht verfärbungsfreie Verarbeitung. |
| 10 Guitar Rhythm Tight | Geringere Anregung und 80 % Mix plausibel; bei bereits verzerrtem Material nur wenig GR zulassen. |
| 11 Guitar Colour Only | Compression Off mit 60s/Colour 100 stimmig. Input +6/Output −6 gleicht nicht automatisch sämtliche Sättigungsverluste aus. |
| 12 Vintage Blue Grit | 8:1, 60s und 70 % Mix passen zum warmen Grit-Ziel, ohne Blue-Stripe-Revisionsbehauptung. |
| 13 Guitar Cruncher | 4:1, +15 dB Input, 7/7, 80s und 65 % Mix ausdrücklich aggressive eigene Interpretation. 80s kann vor dem Regler kräftig sättigen. |
| 14 Acoustic Strum | 4:1, relativ langsamer Attack 2, 80 % Mix/Link stimmig; Plektrum und Stereoabbildung hören. |
| 15 Acoustic Finger | Mehr Input und Wet-Anteil als Strum plausibel für Details; Raum-/Spielgeräusche mitprüfen. |
| 16 Bass Finger Level | 4:1 und 4/4 als Leveler plausibel; Tieftöne können trotz mittlerer Skalenstellung schnell geregelt werden. |
| 17 Bass Pick Punch | 8:1/4/4 und 85 % Mix stimmig; Attack 4 entspricht ca. 126 µs. Gemeinsame Resamplingphase ist keine vollständige Wet/Dry-Phasengleichheit. |
| 18 Bass Fast Grit | 8:1/7/7, +8 Input, 70 % Mix passen bewusst zu schneller rauer Regelung. |
| 19 Bass Mojo Bite | 8:1/7/7 plus 80s ergänzt den Grit-Pfad; moderate Profilbezeichnung bedeutet bei +9 Input nicht automatisch wenig Klirr. |
| 20 Huge Sub Weight | 8:1/4/4 plus 00s plausibel für relativ mehr Headroom; keine Bassanhebung. Bei +8 Input kann auch 00s kräftig angeregt werden. |
| 21 Kick Weight | Korrigiert auf Attack 2, ca. 433 µs statt 68 µs. Für das Weight-/Klick-Ziel mehr Frontkante; im Testsignal Spitzen-GR 11,19 statt 11,71 dB. |
| 22 Snare Crack | Korrigiert auf Attack 3, ca. 234 µs statt 68 µs. Weiterhin schneller als Preset 23; im Testsignal Spitzen-GR 11,65 statt 11,94 dB. |
| 23 Snare Slow Attack | Attack 2 (ca. 433 µs) relativ langsam und zur Absicht passend. Unbelegte pauschale Verzerrungsbegründung gegen Attack 1 entfernt; externer HP bleibt optionaler Quellentipp. |
| 24 Snare Saturated Parallel | 80s, Colour 100, 30 % Mix konsistent. 10–18 dB ist eigene aggressive Parallel-Abstimmung, nicht GR-Vorgabe von MTM-SNARE. |
| 25 Toms Body | 4:1/4/6 und Dual Mono für getrennte Toms stimmig; Stereosumme gegebenenfalls linken. |
| 26 Overheads Gentle | 4:1/1/4,5, 75 % Mix und Link plausibel; bei −12-dBFS-Probe bereits ca. 6,62 dB GR, deshalb Input senken. |
| 27 Room All Buttons | All, +12 Input, 3/6 und voller Wet-Pfad konsequenter Raumeffekt; Überschwinger beabsichtigt möglich. |
| 28 Drum Room Smasher | 4:1/7/7 und 75 % Mix passend; Ratio bleibt ausdrücklich eigene Wahl zur Quelle. |
| 29 Drum Parallel Crush | All, +14 Input, Release 7 und 25 % Mix stimmige starke Parallelstufe. |
| 30 Percussion Snap | Langsamerer Attack 1,3, schneller Release und 75 % Mix plausibel; Dual Mono nur für unabhängige Kanäle. |
| 31 Piano Gentle | 4:1 mit 60 % Mix/Colour 50 bleibt erhalten; zusätzliche 2:1-Variante unter 37. |
| 32 Rhodes Body | 4:1/2,5/5 und Colour 90 schlüssig für Körper/Sustain; Chorus-/Stereoeffekte mithören. |
| 33 Synth Bass Control | 8:1/3,5/4, geringere Colour und hoher Wet-Anteil schlüssig; tiefe Dauertöne/Release prüfen. |
| 34 Synth Lead Sustain | 4:1/3/5,5 und 85 % Mix passen zu Sustain; Delay/Reverb-Routing beeinflusst Pumpen. |
| 35 Stereo Bus Subtle | Niedrige Anregung, 40 % Mix/Colour, Link und None bleiben erhalten; zusätzliche 2:1-Variante unter 38. |
| 36 Mix Bus Light Glue | 4:1 bleibt wegen des ausdrücklichen Quellenbezugs. 1–2 dB Wet-GR wird über Input eingestellt, nicht über Mix; Notiz korrigiert. |
| 37 Piano Gentle 2:1 | Neu: bis auf Ratio identisch mit 31; Ziel 1–2 dB Wet-GR. Bei derselben Probe ca. 3,96 statt 6,04 dB Spitzen-GR, Input weiterhin abstimmen. |
| 38 Stereo Bus Subtle 2:1 | Neu: bis auf Ratio identisch mit 35; Ziel 0–2 dB Wet-GR. Bei derselben Probe ca. 2,62 statt 4,11 dB Spitzen-GR. |

## 3. Zwei umgesetzte 2:1-Erweiterungen

### 37 Piano Gentle 2:1 — Variante von 31

- Factory-Variante mit **Ratio 2:1**, übrige Werte wie 31:
  Input −3 dB, Output +1 dB, Attack 1, Release 3,5, Mix 60 %, Colour 50 %,
  Link On, Transformer None, OS Off.
- Hörziel: weniger Verdichtung langer Anschläge, mehr Anschlagsdynamik.
  Input danach auf etwa **1–2 dB Wet-GR** einstellen, Output neu pegelgleichen.
- Nominal Attack **800 µs**, Release **303 ms**. Auch die langsamste
  Attack bleibt FET-schnell; 2:1 macht aus dem Modell keinen langsamen Leveler.

### 38 Stereo Bus Subtle 2:1 — Variante von 35

- Factory-Variante mit **Ratio 2:1**: Input −6 dB, Output +1 dB,
  Attack 1,5, Release 3, Mix 40 %, Colour 40 %, Link On, None, OS Off.
- Hörziel: kleine Verdichtung bei höherer interner Durchlässigkeit;
  Ziel **0–2 dB Wet-GR**, anschließend pegelgleicher Bypass-/Ratiovergleich.
- Nominal Attack **588 µs**, Release **393 ms**. Bei 40 % Mix ist der
  hörbare Unterschied kleiner als der Unterschied der internen GR.

### Gemessener isolierter Ratiovergleich

1-kHz-Sinus, Stereo Link, R=−L, 48 kHz/OS Off, Original-Presetwerte außer Ratio,
Mittel der FET-GR von 0,4–0,6 s. Inputpegel bezeichnet den Hosteingang **vor**
dem Preset-Input-Gain. Kein Nachregeln von Input/Output in dieser Messung.

| Preset | Eingang Peak | 4:1 GR | 2:1 GR |
|---|---:|---:|---:|
| 31 Piano Gentle | −18 dBFS | 2,6181 dB | 1,5566 dB |
| 31 Piano Gentle | −12 dBFS | 6,6720 dB | 4,4165 dB |
| 31 Piano Gentle | −6 dBFS | 11,1249 dB | 7,3967 dB |
| 35 Stereo Bus Subtle | −18 dBFS | 0,9560 dB | 0,4930 dB |
| 35 Stereo Bus Subtle | −12 dBFS | 4,5981 dB | 2,9496 dB |
| 35 Stereo Bus Subtle | −6 dBFS | 8,9146 dB | 5,9342 dB |

2:1 regelt in diesen Fällen weniger, aber weder allgemein halb so stark noch
allgemein ein Drittel so stark. Die frühere Drittel-Aussage verwechselte
festen Feedback-Tap-Pegel mit festem Eingang. Herleitung in `PARAMETERS.md`.
Quelle für die beiden Varianten ist **eigene Modell-/Signalbewertung**,
kein historischer 1176-Tipp. 31/35 bleiben bei 4:1, 37/38 ergänzen die Bank
am Ende. Die ersten 36 Plätze bleiben dadurch abrufkompatibel; nur 21/22
haben die oben begründete Attackkorrektur. Eigene Feinabstimmungen separat speichern.

## 4. Wiederholung und Dokumentationsstand

```bash
make build/native/preset_probe
python3 tools/audit_presets.py --probe build/native/preset_probe \
  --output docs/PRESET_AUDIT.json
make check-generated
```

Zusätzlich die reale ysfx-Parität mit RPL-/Selector-Lader nach `TESTING.md`
ausführen. `PRESETS.md` wird weiterhin aus `data/presets.json` generiert.
Die projektweite Markdown-Konsistenzprüfung berücksichtigt Preset-, Ratio-,
GR- und GUI-Aussagen; aktuelle Anleitungen, Quellenzuordnung und Übergabe sind
abgeglichen. Historische Mess-/Fitberichte und ihre Hashmanifeste behalten
ihre damaligen Bedingungen und Fallzahlen. Der aktuelle Bericht ersetzt
keine dort noch offene Geräte-, NAM- oder Hörprüfung.
