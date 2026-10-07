# Green Stripe 76 — Projekt, Stand und Übergabe

Einstieg, verbindlicher Umfang, aktueller Prüfstand, Übergabeauftrag und Entwicklungshistorie.

**Konsolidiert am 2026-10-06** aus den bisherigen Einzeldokumenten; Inhalt inhaltlich unverändert, Pfadangaben auf die neue Struktur angepasst.

## Zusammenfassung (Stand 2026-10-07)

- **Produkt 0.4.1:** LV2 Mono/Stereo + JSFX Mono/Stereo, 38 Presets (37/38 als
  2:1-Varianten), hörbare Eingangstransformatoren 60s/80s/00s plus None und
  die lineare Referenz Symmetric. DSP-Kern doppelpfadig (C++11/EEL2) mit
  belegter Bit-Parität (506 Signalvergleiche, max 0 FS).
- **Am Gerät nachgewiesen (2026-10-07):** erste vollständige
  Transformator-Matrix aus digitaler Dwarf-Quelle — Anker exakt,
  Wiederholungsspreizung ≤ 0,01 dB, Sättigungsreihung 60s/80s/00s am
  20-Hz-Klirr (5,53/2,15/0,11 %) gegen Bypass 0,005 %; Symmetric als linear
  flach bestätigt. Messweg: Testton-Dateien auf dem Dwarf
  (`tools/make_dwarf_tones.py`), Aufnahme via REAPER, Import/Aggregation über
  `tools/dwarf_reaper_series.py` (MESSTECHNIK 1a/1b). **Provenanz-Korrektur
  (2026-10-07):** die Zahlen beschreiben dieselbe Bank bei je Lauf
  unbekannter Eingangsdämpfung (INPUT-Knopf aus der Gainmatch-Phase;
  H3/H5-Drive-Verhältnisse belegen 60s −3,5 dB, 00s −9,2 dB) — als Anker
  unbrauchbar, als Trendreihe konsistent (MESSTECHNIK 1c).
- **JSFX-Render-Referenz (2026-10-07):** die vier Typen der aktuellen Bank als
  48-kHz-Render (`reaper/testbench/matrix-*_jsfx_…10_54_15.wav`), bitnah gegen
  den C++-Offline-Render verifiziert (max < 1 LSB, Offset −3 Samples =
  REAPER-PDC der 2x-Latenz) — JSFX↔C++-Parität erstmals am vollen
  Matrixprogramm belegt (MESSTECHNIK 1c,
  `test-results/jsfx-render-ref-20261007`).
- **GUI am Gerät:** Logoquelle auf `/resources/…{{{ns}}}` korrigiert (Grund:
  DOM-Injection löst relative URLs gegen die Seiten-URL auf); Paneel jetzt am
  kompletten Rahmenring ziehbar (vier Leisten + Fußzeilenplatte, Cursor
  `move`); beide Fixes im Build-Stand `7ceaed7`, `.mk` zeigt dorthin,
  Geräte-Sichtprüfung offen.
- **Offene Hauptlinien:** Gerätesichtprüfung GUI + REAPER-/Dwarf-Abnahme
  (PROJEKT Übergabe), Serie-B-Isolationsbench (Ursache je Profil für die
  CPU-Reduktion) und danach Entscheidung über die CPU-Reduktionshebel
  (TODO, Abschnitt CPU-Reduktion Transformator); optional direkte
  20-Hz-Ankermessung von 60s/80s bei −14/−8 dBFS (Stimuluserweiterung).
  Die Ankerinterpretation der Geräteserie ist abgeschlossen (EXTERN).
- **Verbindlich:** keine Hardwaregleichheits-Claims; Portindizes/URIs stabil;
  Bank-Refits ändern bestehende Projektklänge (Revision dokumentieren).

## Inhalt

1. REQUIREMENTS.md — *(Quelle: REQUIREMENTS.md)*
2. Aktueller Stand 0.4.1 — *(Quelle: STATUS.md, Teil 1)*
3. MISSION_STATUS.md — *(Quelle: MISSION_STATUS.md)*
4. STAND_BIS_HIER_HIN.md — *(Quelle: STAND_BIS_HIER_HIN.md)*
5. HANDOFF.md — *(Quelle: HANDOFF.md)*
6. DECISIONS.md — *(Quelle: DECISIONS.md)*
7. Historie: Archive früherer Stände — *(Quelle: STATUS.md, Teil 2)*


---

<!-- ===== Teil 1: Quelle docs/REQUIREMENTS.md ===== -->

# Anforderungen und Abgrenzung

Stand: Benutzerentscheidungen bis 2026-10-05, Produkt 0.4.1.

## Produkt

- Name **Green Stripe 76**; eigenes grünes Erscheinungsbild.
- 1176-inspirierter FET-Kompressor/Limiter; nach letzter Benutzerkorrektur keine
  verbindliche Festlegung auf Rev. A oder D.
- Hohe musikalische Nähe ist Entwicklungsziel; gemessene Hardwaregleichheit ist
  ohne Referenzgerät/kalibrierte Daten kein belegter Lieferstatus.

## Plattformen

| Plattform | Anforderung |
|---|---|
| MOD Dwarf | OS 1.13.5.3315, aarch64/Cortex-A35, Kernel 6.1.15-rt7-moddwarf |
| LV2 | Mono und Stereo, optionale Link-Regelung, keine Meter-GUI/GR-Ports |
| REAPER 7 | JSFX Mono und Stereo, optionale Link-Regelung, GR und Level |
| Testrechner | anderer Rechner; dort Dwarf/REAPER, Docker/MPB und Hörprüfung |

## Bedienfunktionen

Input, Output, Attack 1–7, Release 1–7, Ratio 2/4/8/12/20/All,
Mix, Colour, Compression, Enabled und in Stereo Stereo Link;
Oversampling Off/2x/4x und Transformator None/60s/80s/00s/Symmetric.
Gemeinsame Regler im Dual-Mono-Modus. Eingebaute Instrument-Startwerte und `.rpl`.
38 Factory-Presets; dokumentierte Ziel-GR bezieht sich auf den Wet-Regler vor
Mix und erfordert Input-Abgleich. Ausdrücklich beauftragte Korrekturen in
21/22 und zwei angehängte 2:1-Varianten 37/38; bestehende Nummern erhalten.
Messwerkzeug für Scarlett 2i2 1st Gen: Testton/Frequenz-/Pegelreihe, gleichzeitige
Wiedergabe/Aufnahme, Referenzvergleich und WAV-Auswertung mit dokumentierten Grenzen.

## Technische Eigenschaften

- DSP-C++11, keine Runtime-Abhängigkeit auf JUCE, React, X11 oder NAM.
- Audiopfad float-Ports, double-Zustände, keine Lookahead-Puffer.
- Pro Sample begrenzte numerische Arbeit, keine Audio-Allokationen.
- Off/2x/4x-Verarbeitung für Audiopfad, Transformator und Regelung; Default Off.
- Transformatorbank refit-fähig, gemeinsame validierte Daten für C++/EEL2;
  getrennte Kanalzustände, feste Gainnormalisierung, geglättete Modellwechsel.
- LV2-GUI: spaltfreie innere Paneele, Produktname ohne Schild; bereitgestellte
  Aluminium-/Toggle-/Pilot-Assets, separater Drag-Rand und funktionsfähiger Mode-Schalter.
- Input-Staging, nichtlinearer FET-Divider, post-cell Feedback-Abgriff vor Output,
  programabhängige Entladung und separater All-Modus.
- Geglättete Parameteränderungen und interner Bypass.
- Interner Dry/Wet teilt Resamplingphase, unveränderte Kanalzuordnung.
- Definierte Aktivierung/Reset, beliebige positive Blöcke und `run(0)`.

## Referenzmaterial

Dissertation, UA-Handbücher, DIY-Unterlagen, andere Open-Source-DSPs und
Praxisartikel werden mit Herkunft/Revision/Aussagegrenzen dokumentiert.
Die vier NAM-Dateien dienen als **Offline-Referenzmaterial**, nicht als automatisch
eingebauter Audioprozessor. A1-Abtastrate und Capture-Stellungen sind unbekannt.

## Abnahme

1. Native Build und Signal-/ABI-Tests bestanden.
2. JSFX geladen, gerendert und mit C++ verglichen.
3. Presets gültig, importierbar, dokumentiert.
4. Dwarf-Cross-ABI und reales Laden/CPU/Regler geprüft (extern).
5. REAPER-Meter, Preset-Recall, Routing, Automation geprüft (extern).
6. Klangabgleich und persönliche Bewertung protokolliert (extern).

Punkte 4–6 bleiben separat sichtbar, auch wenn 1–3 bestanden sind.


---

<!-- ===== Teil 2: Quelle docs/STATUS.md ===== -->

# Entwicklungsstand und Übergabe

Stand **2026-10-06**, Projekt **0.4.1**. Benutzerziel: eigener **Green Stripe**,
Hardware-Revision A/D nicht bindend.

## Aktueller Stand 0.4.1

- **GUI korrigiert:** Ratio unverändert auf Höhe der Wertefelder Input/Attack/Mix.
  Der größere Abstand liegt ausschließlich zwischen COMP und Oversampling
  (**40 px**); Oversampling und Stereo Link folgen mit **7 px** Abstand.
  Mono/Stereo geometrisch und mit echten MOD-Widgets geprüft, Vorschauen erneuert.
- **Presetkorrektur auf ausdrücklichen Auftrag:** 21 Kick Weight Attack 5→2,
  22 Snare Crack 5→3 für mehr Anschlag. Neue Varianten **37 Piano Gentle 2:1**
  und **38 Stereo Bus Subtle 2:1** angehängt. Insgesamt **38 Presets**;
  alte Nummern/URIs 01–36 erhalten. Nur erneuter Factory-Recall 21/22 lädt
  deren neue Werte; gespeicherte Projektparameter bleiben erhalten.
- Die übrigen Klangwerte der ersten 36 Presets und der DSP-Kern sind unverändert.
  Modell-/Metadatenversion und JSFX jetzt 0.4.1. Presetprüfung in
  `EXTERN.md`, aktueller Audit in `PRESET_AUDIT.json`.
- **Scarlett-Werkzeug:** `tools/scarlett_test.py` mit `devices`, `generate`,
  `run`, `analyze`. Mono-Testton, gestufter Frequenz-/Pegelsatz, gleichzeitige
  zweikanalige Aufnahme, WAV/JSON-Plan, Synchronisations-/Driftbestimmung,
  Gain/RMS/Peak/DC/THD/THD+N und Referenzvergleich; Berichte als JSON/CSV/Markdown.
  Anleitung/Verkabelung/Treiber-/Kalibriergrenzen in `MESSTECHNIK.md`.
- **Automatisierte Transformator-Matrix (2026-10-06):** `tools/scarlett_matrix.py`
  plus `tools\scarlett_matrix.bat` für die Windows-CMD. Gainmatch-Probe beider
  Kanäle (ersetzt den PluginDoctor-Input-Gain-Abgleich), Anker-Pegelauswahl
  (Stimulus = Anker − Loop-Gewinn, Abbruch bei Loop-Gewinn < +1 dB),
  Bypass-Baseline mit Wiederholungen, Transformator-Matrix mit Prompts für die
  Dwarf-Bedienung, Median/Spreizung in `SUMMARY.md`. 19 Offline-/Mocktests
  PASS (`tests/test_scarlett_matrix.py`, Windows-Python 3.9 und WSL).
- **Erster Live-Einsatz der Matrix (2026-10-06, `test-results/matrix-20261006-161927`):**
  Gainmatch-Probe 3× ausgeführt. Erste Probe: Kanaldifferenz **−0,20 dB** — der
  PluginDoctor-Abgleich der Dwarf-Input-Gains ist durch die reproduzierbare
  Python-Messung bestätigt. Loop-Gewinn −54,3 → −46,8 → −30,6/−35,5 dB nach
  Reglerumstellungen; Ziel (≥ +1 dB für die Anker, mind. −20 dB) noch offen.
  Befunde: (1) Windows-Geräteformat meldet trotz 48-kHz-Panel-Einstellung
  weiter `default_samplerate` 44100; Sync-Marker fiel einmal unter 0,35.
  (2) Im Ch1-Probe kommt das Signal auf beiden Scarlett-Eingängen an und Ch2
  clippt (bis 139k Samples) — Hinweis auf MONO-Board oder abweichende
  Verkabelung; Prüfung offen. (3) Ch2 zuletzt 4,9 dB unter Ch1 — Rebalance
  nötig. Details/Regeln: MESSTECHNIK Abschnitt 21.
- **Umstieg auf Dwarf als Signalquelle (2026-10-07):** Der Dwarf spielt die
  Testtöne selbst (File-Player → GS76 → DAC → nur noch Scarlett-ADC). Der
  Plugin-Eingang ist damit digital exakt pegelbekannt — `--level -2` trifft
  die Anker −14/−8/−2 dBFS ohne Loop-Gain-Arithmetik; die gescheiterte
  Pegelkette (oben) ist obsolet. Neu: `tools/make_dwarf_tones.py`
  (48-kHz/PCM_24-Uploaddateien + MANIFEST), `scarlett_test.py --no-playback`
  (Aufnahme mit 10-s-Vorlauf ohne Wiedergabe, `generate()`-Leveldeckel
  `max_level` nur für diesen Pfad geöffnet) und
  `scarlett_matrix.py --dwarf-source` (fixer Dateipegel, Prompts je Lauf).
  Da die Aufnahme in der Praxis über REAPER läuft, zusätzlich
  `tools/dwarf_reaper_series.py` (Import je Stereo-Aufnahme in die
  Treiber-Index-/Summary-Struktur, beide Kanäle aus einer Wiedergabe;
  `build_summary` ist dwarf-bewusst, Anker werden digital geprüft). Tests:
  17 (scarlett_test) + 21 (Matrix) + 2 (Tongenerator) + 3 (REAPER-Import) PASS.
- **Erste vollständige Transformator-Matrix aus Dwarf-Quelle (2026-10-07,
  `test-results/matrix-dwarf-20261007`):** Aufnahme via REAPER (48 kHz/24 bit,
  lange Takes, Schnitt aus den Sync-Markern), Import je Kanal über
  `tools/dwarf_reaper_series.py`. 18 gültige Läufe: Baseline/60s/80s/00s × r1+r2,
  Sym × r1, je zwei Kanäle. Anker −14/−8/−2 dBFS exakt (Dateipegel =
  Plugin-Eingang), Aufnahmepeaks ≈ −4 dBFS ohne Clipping, Kanaldifferenz
  stabil −0,39 dB, Spreizung der Wiederholungen ≤ 0,01 dB. Befunde relativ zur
  Bypass-Baseline: 60s −1,30 dB @ 20 kHz (−0,59 @ 16k), 80s −0,13 dB,
  00s −0,05 dB, Sym −0,04 dB; 20-Hz-Klirr 60s **5,53 %**, 80s 2,15 %,
  00s 0,11 %, Sym 0,01 % (Bypass 0,005 %) — Sättigungshärte-Reihung der
  Profile am Gerät bestätigt. Digitale Dwarf-Recorder-Querreferenz (48 kHz)
  bestätigt Sym als linear flach (≤ 0,05 dB, THD 0,005 %); der
  Recorder-Zweig hat einen eigenen Offset (−4,3 bis −5,4 dB), der Player
  selbst ist laut Benutzer Unity. Ein erster Sym-Analoglauf war um +4,8 dB
  übersteuert (ungültig, verworfen); `playback1` der ersten Take war ein
  abgebrochener Versuch (ignoriert). OS-Stellung der Runde laut Benutzer
  **2x** (im Index/Label nachgetragen); die Plugin-Latenz (nominal 3 Frames
  bei 2x) ist aus den Takes nicht ableitbar, weil der Wiedergabestart manuell
  erfolgte (der DUT−Baseline-Latenzcheck gilt nur bei Skript-gesteuerter
  Wiedergabe). 96-kHz-Messung ist über den Dwarf-Player nicht möglich (feste
  48 kHz); Auswertung/Interpretation in `EXTERN.md` folgt.

  **Provenanz-Korrektur (2026-10-07, nachgehend):** Vergleich gegen die
  aktuelle Modellbank zeigt Unvereinbarkeit. Digitale JSFX-Render-Referenz
  (MESSTECHNIK 1c, `test-results/jsfx-render-ref-20261007`): 1-kHz-Transparenz
  der Geräteserie ⇒ Colour ≈ 0; der 20-Hz-Klirr der aktuellen Bank ist
  colour-invariant (60s 12,4 %, Grundwelle und Klirr skalieren gemeinsam),
  die Serie maß 5,53 %; Gains matchen Bank-only (80 Hz −0,05 dB, 00s −0,016 dB),
  Klirrmagnituden 2,25×/9× zu hoch, Harmonischenstruktur identisch (H3 ≫ H5 ≫
  H2). **Aufgelöst (2026-10-07 nachmittags):** Bundle `48ab885` (HEAD) via MPB
  neu gebaut und installiert; erste Wiederholung ungültig (Parameterwechsel
  ohne Wirkung — Sitzungszustand), zweite Serie gültig
  (`matrix-dwarf-20261007-b2`): 20-Hz-Klirr 60s **12,42 %** / 80s 12,28 % /
  00s 1,00 % / Sym 0,00 %, relative Gains −0,817/−0,441/−0,016/−0,002 dB —
  deckt sich mit der digitalen Referenz bis in die 4. Dezimale. **Die aktuelle
  Bank ist am Gerät messtechnisch bestätigt** (A35, aarch64, −O3,
  `-ffp-contract=off`). Die Nachtwerte (5,53/2,15/0,11 %) erklären sich als
  **dieselbe Bank bei eingangsgedämpfter Messung** (INPUT-Knopf aus der
  Gainmatch-Phase; H3/H5-Drive-Verhältnisse 60s −3,5 dB, 00s −9,2 dB); die
  Gerät-Binary (`e6b4e55…`) trägt die aktuellen Bankkonstanten bitweise
  (87/87 double-Konstanten) — die frühere „Refit-Zwischenstand"-Deutung ist
  widerlegt. Interpretation gegen `EXTERN.md` durchgeführt (Anker von 00s
  exakt getroffen; 60s/80s by design).
  **Colour-Stufen ebenfalls validiert (2026-10-07):** Transformer None,
  Colour 5–100 %, deckungsgleich mit der Referenz bis in die 4. Dezimale
  (`colour-dwarf-20261007`); 1-kHz-Klirr/Gain linear in Colour. JSFX-Render
  der Colour-Punkte und der Typen (Colour 0) bit-exakt gegen C++ verifiziert
  (max < 1 LSB, PDC-Offset −3). Vollständige Messwerte, Grafiken und
  Provenanz: [MESSERGEBNISSE](MESSERGEBNISSE.md) (generiert).
  **Bank×Colour-Interaktion** als JSFX-Render-Matrix (24 Zustände,
  Colour 5–100 % × alle Typen) bitverifiziert; direkte Gerätemessung
  bewusst nicht ausgeführt — Abdeckung über die einzeln am Gerät validierten
  Pfade plus Bit-Parität (MESSERGEBNISSE 2.5). **CPU-Matrix am Gerät
  (36 Zustände, je voller Neustart):** Bypass 22 %, None+Colour 28–36 %,
  Typen 48–56 %, Interaktionen 56–68 % Median (20-Hz-Sinus, OS 2x,
  COMP OFF, 128 Frames, 0 xruns); Sym/00s am teuersten — Profilreihung für
  die CPU-Reduktion belegt (MESSERGEBNISSE 6, MESSTECHNIK 1f).

### Scarlett-Liveaufnahme 2026-10-05: Auswertung und Grenzen (2026-10-06)

Die Liveaufnahme wurde auf dem Testrechner ausgeführt (TF60s/80s/00s/Sym,
Stereo, MME, `--kind all`, −12 dBFS; Rohdaten `test-results/`, Bericht
`MESSTECHNIK.md`). Nachbetrachtung gegen Rohdaten und ein
Offline-Render des Plugins ergab:

- **Baseline war Dwarf mit GS76-Bypass** (Betriebsangabe; durch die Daten
  belegt): DUT−Baseline-Marker-Delay **+3,2…+4,5 Frames** ≈ nominale
  Plugin-Latenz bei OS 4x — die physische Strecke war in Baseline und DUT
  identisch, die relativen Werte isolieren also tatsächlich das Plugin.
- **Loop-Gewinn −63 dB** (Aufnahme −78 dBFS RMS bei −12 dBFS Anregung,
  Leerlaufrauschen −95,2/−95,4 dBFS): SNR 5–17 dB. Die Referenz allein zeigt
  2,85 % THD/~14,8 % THD+N — die berichteten ~3,2–3,5 %/~15 % sind
  Rausch-/Pfadartefakte, kein Plugin-Klirr. Pegelreihe −36/−30 dBFS lag am/
  unter dem Rauschboden. Die Profilanker (−14/−8/−2 dBFS am Plugin-Eingang)
  wurden um ~50 dB verfehlt; die Profile waren nicht im nichtlinearen Bereich.
- **Sweep-Spalten ab ~2 kHz nicht trennscharf:** Baseline↔Baseline (identische
  Physik) streut ±0,18 dB (1 kHz) bis ±2,56 dB (20 kHz); erwartete
  Modellunterschiede sind kleiner. Offline-Render (None/OS 4x gegen Bypass:
  **0,0000 dB** in allen Spalten) belegt, dass OS-Kette und Plugin flacher
  sind als die gemessene Streuung — die HF-Muster sind Messketten-Effekte
  (Kandidat: Windows-Mixer-Resampling, `default_samplerate` 44100 in
  `recording.json`), keine Plugin-Eigenschaften.
- **Werkzeug gehärtet:** `tools/scarlett_test.py` meldet jetzt `level_check`
  (Loop-Gewinn ≥ −20 dB) und warnt bei Geräteraten-Mismatch im `REPORT.md`;
  12/12 Offline-Tests PASS (zuvor 10/10).

Nächste Schritte am Messplatz: Pegel anheben, Geräte auf 48 kHz festlegen,
≥ 3 Wiederholungen, 20 kHz bei 96 kHz, Bypass-Stabilitätsvorablauf, danach
erst die Transformer-Matrix mit Pegelankern wiederholen. Konsolidierte
offene Punkte: `TODO.md`.

### Transformator-Last: Werkzeuge bereit, x86-Vorhersage ausgeführt (2026-10-05)

Anlass war die Rückmeldung, die Transformatorstufe sei sehr kostspielig. Die
vorige Dwarf-Serie 5b stammt von vor dieser Stufe und beantwortet die Frage
nicht. Neu sind deshalb zwei Werkzeuge und ein Protokoll:

- `tools/transformer_bench.cpp` rechnet den **Produktkern unverändert** direkt
  auf dem Gerät, ohne jackd und ohne Bedienung: Profil, OS-Stufe, Kanalzahl,
  Instanzzahl und Pegel sind frei einstellbar. Ohne `-DGS76_TRANSFORMER_STATS`
  reine Zeitmessung; das Makro zählt Solveriterationen ohne Audioänderung.
- `tools/dwarf_loadtest.py` misst auf dem Gerät die jackd-Prozess- und
  Threadlast, verifiziert Instanzzahl und Binärhash und bildet die
  xrun-Differenz über das Messfenster aus `dmesg`/Kernel-Journal.
- `docs/MESSTECHNIK.md` beschreibt Serie A (Boards `GS76x0…GS76x4` bei 128
  und 256 Frames, je ein Vollstart) und Serie B (Profilkosten).
- `tests/test_dwarf_loadtest.py` läuft mit `make test` mit: **13 Tests PASS**.
- `tests/diag_macro_parity.cpp` belegt zweimal gebaut (mit/ohne
  `-DGS76_TRANSFORMER_STATS`) und per `cmp` verglichen **byteidentische**
  Ausgabe über 60 Fälle und 90 000 Samples: der Diagnosezähler ist
  audioneutral. `make test` und `make check-generated` PASS.

Ausgeführt wurde ein **x86_64-Lauf** (GCC 11.4, 48 kHz, 0 dBFS, Median aus drei
Läufen), Prozent eines Kerns, plus Delta gegen None derselben OS-Stufe:

| OS | None | 60s | 80s | 00s |
|---|---:|---:|---:|---:|
| Off | 1,75 | 3,07 (+75 %) | 2,88 (+64 %) | 2,99 (+71 %) |
| 2x | 3,45 | 5,79 (+68 %) | 5,64 (+64 %) | 5,77 (+68 %) |
| 4x | 6,58 | 10,71 (+63 %) | 10,79 (+64 %) | 10,93 (+66 %) |

Daraus: die Transformatorstufe **verdoppelt** den Kernaufwand, das
**Oversampling ist der größere Hebel** (4× allein vervierfacht gegenüber Off),
beide multiplizieren sich. Der Aufwand steckt nicht in der Iterationszahl:
gemessen 2,0–2,6 Iterationen je Probe und **0 %** am 40er-Limit. Ein
Iterationslimit wäre keine wirksame Sparmaßnahme.

**Ausdrücklich keine Gerätemessung.** Über den in Serie 5b gemessenen Faktor
(≈13 % eines A35-Kerns für None/OS Off gegen 1,75 % hier) ergibt sich als
Orientierung ~23 % je Instanz für 60s/OS Off und ~81 % für 00s/OS 4x. Vier
solcher Instanzen wären danach nicht unterzubringen. Das ist eine Hochrechnung
aus zwei x86-/A35-Anteilen, keine Abnahme. Details und Protokoll in
`PERFORMANCE.md` Abschnitt 5c.

### Tatsächlich geprüft für 0.4.1

| Prüfung | Ergebnis |
|---|---|
| `make test` | Native DSP, Übergänge, Transformator, reale LV2-ABI, Refit-/RDF-Prüfung PASS |
| Generierte Dateien | 17 Artefakte, `make check-generated` PASS |
| Preset-Audit | 76 LV2/RPL-Wertezustände, 228 Presetfälle + 12 Ratiovergleiche PASS |
| C++/JSFX | 430 allgemeine + 76 Preset-Signalvergleiche, **max. 0 FS**, Recall/Custom PASS |
| GUI | Mode/Drag/Bypass/Filmstrip PASS; Ratio-Ausrichtung 0 px Abweichung, Lücken 40/7 px |

### GUI-Nachpflege 2026-10-06: Logo und Drag-Handles

- **Logo 5 px nach unten:** `.gs-brand` top 14→19 px (CSS-Quelle; HTML generiert,
  PNGs neu gerendert). Geometrie lokal verifiziert: Logo-Bounding-Box +5 px,
  Paneelhöhe unverändert 375 px, keine Kollision mit RATIO.
- **Unteres Paneel verschiebbar:** zusätzlich zum oberen Rand sind jetzt die
  **Fußzeilenplatte** (FET-COMPRESSOR-Label) und ein **unterer 9-px-Rand**
  Drag-Handles (`mod-role="drag-handle"`). Bypass/Lampe und alle Regler bleiben
  außerhalb der Handles.
- **Kompletter Rahmen ziehbar (2026-10-06):** vier Leisten kacheln den
  sichtbaren Rahmenring exakt entlang des Panel-Paddings (26 px oben, 30 px
  seitlich, 8 px unten): `gs-drag-top` (volle Breite, 26 px), `gs-drag-left`/
  `gs-drag-right` (30 px breit, zwischen den Leisten), `gs-drag-bottom`
  (volle Breite, 9 px). Cursor `move` (Pfeilkreuz) auf allen Leisten; die
  Eckschrauben sind `pointer-events:none` und gehören damit zur Ziehfläche.
  Kein Leistenstück überlappt Bays, Footer, Bypass/Lampe oder Jacks
  (hit-test-geprüft).
- **Gerätebeleg:** `modgui.js` des Dwarf (OS 1.13.5.3315) bindet in Zeile 1250
  `element.find('[mod-role=drag-handle]')` als jQuery-UI-Handle-Sammlung —
  mehrere Handles sind auf dem Gerät wirksam. `tests/test_modgui.py` prüft jetzt
  alle fünf Handles (vier Rahmenleisten + Platte: Drag bewegt Paneel, keine
  Parameteränderung, Ring-Kachelung, Regler unbedeckt) und läuft lokal gegen
  die mod-ui-Quelle von GitHub master (modgui.js SHA256 `49ef2446…`); der Lauf
  gegen die exakte modgui.js des Dwarf und der Gerätetest bleiben offen.
- **Testrobustheit:** der Platten-Klickpunkt mit +24 px konnte je nach
  Schriftmetrik unterhalb der ~21 px hohen Platte liegen; Klickpunkt auf
  +8 px korrigiert. Pluginverhalten unverändert.
- **Logo-Fehler auf dem Gerät (2026-10-06):** das `logo.png` erschien im
  Dwarf-Webinterface nicht. Ursache: der Icon-Template-HTML nutzte relatives
  `src="assets/logo.png"`. mod-ui injiziert das Mustache-gerenderte Template in
  das DOM der Pedalboard-Seite (`modgui.js`, `self.icon.html(...)`); relative
  URLs lösen dann gegen die Seiten-URL (`http://<dwarf>/assets/...` → 404) auf,
  nicht gegen das Bundle. Die CSS-Hintergründe funktionieren, weil sie die
  Form `/resources/assets/…{{{ns}}}` nutzen: der Webserver routet
  `/resources/(.*)` in das `resourcesDirectory` des Plugins (mod-ui
  `webserver.py`, `EffectResource`), und `{{{ns}}}` wird beim Rendern zur
  Cache-Query `?uri=…&v=…` aufgelöst (`getTemplateData`). Fix: `img src`
  im Generator auf dieselbe Form umgestellt
  (`src="/resources/assets/logo.png{{{ns}}}"`), `gui_preview.py` inlined die
  neue Form als Data-URI, `validate.py` erzwingt die `/resources/…{{{ns}}}`-Form
  für alle `img src`. Lokal verifiziert (Playwright): Logo 290×47 px rendert in
  Mono und Stereo, Regler-/Lampen-Hintergründe unverändert. Geräteprüfung
  offen (benötigt Commit + `_VERSION`-Bump in der `.mk`, siehe TODO).
| Scarlett-Skript | **12 Offline-/simulierte Backendtests PASS** (Gain, H2, DC, FIR, Taktabweichung, Delay, Fehler, Routing/Stop, HF-Grenze, Pegel-Gate, Raten-Mismatch) |
| Scarlett-CLI | `generate --kind all` + `analyze` auf identischer WAV, 19 Segmente PASS |
| Scarlett-Live | 2026-10-05 ausgeführt (TF60s/80s/00s/Sym, Stereo, MME −12 dBFS); Auswertung oben — Pegel-/SNR- und HF-Grenzen, Wiederholung offen |
| Dwarf-Last Serie A | GS76x0–x4, 128/256 Frames, Median 46–48 %, Spitzen ~66 %, **0 xruns**, Binary-SHA256 in `MESSTECHNIK.md` |
| Lastwerkzeuge | `make transformer-bench` baut; x86-Sweep und Instanzlinearität ausgeführt; `--self-test` PASS; **Serie B (Gerät) offen** |
| Diagnosemakro | `diag_parity` gegen `diag_parity_stats` byteidentisch, `cmp` PASS |
| Paketierung | Source-/JSFX-ZIP 0.4.1, Integrität und Scarlett-Skript/Anleitung/Requirements PASS; Diagnoseaudio/NAM/PDF/NPZ ausgeschlossen |

**Nicht ausgeführt:** REAPER-/Dwarf-Abnahme (Laden, Bedienung, Recall), Serie B
`transformer_bench` auf dem Gerät und Musik-Hörtest. Die Scarlett-Liveaufnahme
(2026-10-05) und die Dwarf-Lastmessung Serie A (GS76x0–x4) sind ausgeführt;
beide brauchen nach der Auswertung Folgeläufe (Pegel/SNR bzw. Serie B). Nächster
Schritt auf dem Audio-Rechner: Pegel anheben und Geräte auf 48 kHz festlegen,
dann Teststrecke mit gleichen Pegelstellungen; Plan, Aufnahme und Berichte
gemeinsam zurückgeben. Aktuelles Dwarf-Bundle mit MPB neu bauen, danach 21/22
und die Paare 31/37, 35/38 hören und CPU/xruns im echten Pedalboard prüfen.


---

<!-- ===== Teil 3: Quelle docs/MISSION_STATUS.md ===== -->

# Mission Status

## Aktueller Stand
- Dwarf-Messungen Serie A (128/256 Frames, GS76x0–x4): 46–48 % Median, Spitze bis ~66 %, 0 xruns — Tabelle und Binary-SHA256 in `MESSTECHNIK.md`, Provenienz (Datum/Tool-Version) noch zu ergänzen.
- Scarlett-Tests durchgeführt (TF60s/80s/00s/TFSym, Stereo, MME −12 dBFS, 2026-10-05). Nachbetrachtung: Loop-Gewinn −63 dB → THD/THD+N und HF-Spalten nicht Plugin-tauglich; Latenzbestätigung (4 Frames/OS 4x) gültig. Wiederholung mit angehobenem Pegel offen.
- Scarlett-Loop-Analyse dokumentiert (`MESSTECHNIK.md` Abschnitt 9, Protokoll `MESSTECHNIK.md`).

## Stand bis hier hin
Siehe `PROJEKT.md`

## Offene Punkte
Konsolidiert in `TODO.md`.

## Statusdetails
Siehe `PROJEKT.md`


---

<!-- ===== Teil 4: Quelle docs/STAND_BIS_HIER_HIN.md ===== -->

# Stand bis hier hin

Dieser Abschnitt fasst den aktuellen Arbeitsstand zusammen (Dwarf-Messungen, Python-3.4-Portierung, Web-API-Einschränkung, PluginDoctor-Hinweis). Wird als Referenz abgelegt, um später nahtlos fortfahren zu können.

## 1) Dwarf-Messungen (LV2-Gesamtlast, 48 kHz)
- **Gerät**: MOD Dwarf OS 1.13.5.3315, Kernel `6.1.15-rt7-moddwarf`, AArch64 (4 Kerne), `jackdmp` 1.9.14 (PID 404), Blockgrößen 128/256, Periods n=2, RT-Priorität 80.
- **Messmatrix**: Boards `GS76Measure`, `GS76x0`–`GS76x4`, je 128 + 256 Frames, Messfenster 15–20 s, `expect-instances = 1` (Stereo-Instanz).
- **CPU-Last (Median/Spitze)**: Prozess-Median **46–48 %** eines Kerns pro Stereo-Instanz, Spitzen bis **~66 %**. Schwerster Thread durchgehend `jackd` (~21 % eines Kerns). **0 xruns** in allen Fenstern.
- **Plugin-Identität**: Installierte Binary `/root/.lv2/green-stripe-76.lv2/green-stripe-76.so`
  - SHA256: `e6b4e55da1f164db817d9fc083f0d7f5fad78ecaf3364650cd88a371e92e8d32`
  - MD5:    `4669363f1c2b781a6b162ea7f05bbd33`
- **Ergebnisse (lokal)**: `docs/MESSTECHNIK.md` (vollständige Tabelle), Auszug in `docs/PROJEKT.md` übernommen. Rohdaten: `/tmp/opencode/dwarf_results/auto/*.json, *.md` (je Messlauf). Boardwechsel für diese Runs erfolgte manuell/mit last.json+Neustart (HTTP-API unzuverlässig).

## 2) `tools/dwarf_loadtest.py` – Python 3.4-Kompatibilität (Dwarf)
- Vollständige Portierung für Buildroot/Python 3.4: `io.open` statt `Path.read_text/write_text/read_bytes`, `subprocess.Popen` statt `subprocess.run` (kein `subprocess.run` in 3.4), Zeitstempel via `strftime('%Y-%m-%dT%H:%M:%SZ')` statt `isoformat(timespec=…)` (Python 3.6+).
- Self-Test lokal: **13/13 OK** (`python3 tests/test_dwarf_loadtest.py`). Skript aktuell auf Dwarf unter `/root/lt/dwarf_loadtest.py`.
- CLI: `--report/--markdown` genutzt, optionale Pfade `--output-json/--output-markdown` vorbereitet (Rückwärtskompatibel). Kompatibilitätspatches für Pfad-API (PosixPath an `open/io.open`) abgeschlossen.

## 3) Web-API (MOD OS 1.13.5.3315)
- `effect/parameter/set` und `pedalboard/load_web`/`load_bundle` lieferten bei POST/Form/JSON überwiegend **500 Internal Server Error** (kein stabiler, reproduzierbarer Pfad). Boardwechsel daher **via `last.json` + Neustart des Audio-Stacks** (`jackd`/`mod-host`) vorgesehen (robuster auf 1.13.x). Skriptgerüst `switch_and_measure.sh` erstellt, aber unterbrochener Lauf dokumentiert.

## 4) Offlinetests / Parität
- `make BUILD_DIR=build/wsl test`: **PASS** (13 Dwarf-Offline-Tests + weitere Suite).
- `make check-generated`: **PASS** (`Verified 17 files`).
- Diagnose-Makro-Parität: `diag_macro_parity` byteidentisch (60 Fälle, 90.000 Samples) – Nachweis Audionneutralität bei Diagnosepfad.

## 5) Messdaten PluginDoctor (GR vs Ratio)
- Messwerte vorliegend unter `docs/sauce/gain - 0, atk - 7, rls - 7 - 100 - 100/` (TXT-Dateien je Ratio: `2-1.txt`, `4-1.txt`, `8-1.txt`, `12-1.txt`, `20-1.txt`, `AllButtons.txt` im Ordner `docs/sauce/gain - 0, atk - 7, rls - 7 - 100 - 100/`). Beobachtung: **Gain Reduction nimmt ab 8:1 aufwärts ab** (bei 0 dB In/Out, Attack/Release 7, Comp On, Colour/Mix 100%, Colour 0% ohne Unterschied). Auswertung/Einordnung erfolgt separat (Dokumentation + Prüfung DSP-Detektor/Knie/Ratio-Handling).

## 6) Offene Punkte (Fortsetzung später)
- Vollständige automatische Matrix (GS76x0–x4, 128/256) via `last.json`+Restart abschließen (Skript liegt auf Dwarf).
- Transformatorprofile isoliert (Solver-Kosten) via `transformer_bench` AArch64 (MPB/moddwarf-new) auf Dwarf erfassen (CPU_ANALYSIS 5c).
- GR-Kurven aus PluginDoctor auswerten, gegen erwartetes 1176-ähnliches Ratio/Detector-Verhalten abgleichen und dokumentieren.


---

<!-- ===== Teil 5: Quelle docs/HANDOFF.md ===== -->

# Übergabe an den Agenten auf dem Testrechner

## Einstieg

**Es liegt implementierter Code vor, kein bloßer Plan.**

Aktuell **0.4.1** mit hörbaren, refit-fähigen Eingangstransformatoren und
überarbeiteter MOD-GUI. `DSP.md` beschreibt Bankrevision,
Modellwechsel, feste Gainnormalisierung und HF-Phasengrenzen. Lokal 430
allgemeine plus 76 Preset-Signalvergleiche bitgleich, 76 Recall-Zustände
und echter MOD-Widget-Browsertest. Preset 29 deckte einen nun korrigierten
EEL2-Solver-Rundungsfall auf; mit dem neuen Include-Stand testen.
Bitte Geräte-CPU mit **None/60s/80s/00s und Off/2x/4x** neu messen. Dafür liegen
jetzt `tools/dwarf_loadtest.py` (Pedalboard `GS76x0…GS76x4`, jackd-Threadlast,
Instanz-/Hashprüfung, xruns) und `tools/transformer_bench.cpp` (Profilkosten
ohne Bedienung) vor; Ablauf und Grenzen in **`MESSTECHNIK.md`**. Beide
Werkzeuge sind lokal auf x86 gelaufen, das ist eine Vorhersage und **keine
Gerätemessung**.

1. `AGENTS.md` und `docs/PROJEKT.md` lesen.
2. SHA256 der übergebenen Archive/Binaries prüfen.
3. `README.md`, `BETRIEB.md`, `MESSTECHNIK.md` lesen.
4. Reales Dwarf-/REAPER-Protokoll mit `MESSTECHNIK.md` führen.
5. Neue externe Messdaten: `EXTERN.md` lesen. Alle sieben
   ReaJS-/PluginDoctor-Mono-Versuche sind ausgewertet; hohe Delta-Anregung bei
   aktiver GR oder Sättigung nicht als isolierten linearen Filterfrequenzgang
   beurteilen. Besonders Colour-only-Drive und Alias-/Zeitprüfpunkte beachten.

## Vorhandene Artefakte

- `jsfx/GreenStripe76-Mono.jsfx`, `...-Stereo.jsfx` plus sieben Includes.
- Zwei `.rpl`-Instrumentbänke, 38 Presets je Variante; 37/38 hinten angehängt.
- `tools/scarlett_test.py`, `tools/requirements-scarlett.txt` und
  `MESSTECHNIK.md` für den Scarlett-Testrechner. Baseline = **Dwarf mit
  GS76-Bypass**; erste Liveaufnahme vom 2026-10-05 ist ausgewertet
  (`MESSTECHNIK.md` Abschnitt 9): Loop-Gewinn −63 dB →
  THD/SNR und HF-Spalten nicht verwertbar, Latenzbestätigung (4 Frames/OS 4x)
  gültig. Nächste Runde erst mit angehobenem Pegel und Geräterate 48 kHz.
- Aktuell geprüfter Native Build: `build/wsl/green-stripe-76.lv2` (x86_64).
- Historische Bundles `build/native/green-stripe-76.lv2` und
  `build/aarch64-gcc9/green-stripe-76.lv2`: vor Übergabe von 0.4.1 neu bauen.
- `dist/*-jsfx.zip`, `*-source.zip`, `*-moddwarf.tar.gz`, Herkunftsmanifest,
  SHA256SUMS nach finaler Paketierung.
- `tools/dwarf_loadtest.py` mit `tests/test_dwarf_loadtest.py` (läuft in
  `make test`) und `tools/transformer_bench.cpp` mit Ziel `make transformer-bench`;
  Protokoll und Auswertungsregeln in `MESSTECHNIK.md`, Zahlen in
  `PERFORMANCE.md` Abschnitt 5c.
- C++-/JSFX-Paritätsprogramme, Offscreen-GFX-Test, PCM-Proben-/Rendererwerkzeuge.
- MPB-Rezept und `tools/build_dwarf.sh` für offiziellen Zweitbuild.

## Benutzerentscheidung

Eigenständiger **Green Stripe**, nicht mehr verbindlich Revision A/D.
Mono/Stereo mit optionalem Link, gemeinsame Regler bei Dual Mono.
LV2 ohne Meter; JSFX mit GR/Levels. Dwarf OS 1.13.5.3315, aarch64,
Kernel 6.1.15-rt7-moddwarf, REAPER 7. Presets je Instrument als Startwerte.

## Priorisierte Arbeit vor Ort

### P0 — Laden und Bedienung

- Dwarf-Bundle installieren; JSON-`ok`, beide Pluginnamen/Ports, GUI/Knobs testen.
- Neu: Mode klicken, jeden Aluminiumknopf ziehen (Paneel muss stehenbleiben),
  Paneel am oberen Rand verschieben, Bypass und beide SVG-Lampenzustände prüfen.
- REAPER beide JSFX inklusive Imports/RPL laden, Routing/Meter/Preset-Recall.
- Kernel/OS/Rate/Frames und Pluginhash notieren.
- Input-Gate/Output-Kompressor des Dwarf für Vergleich abschalten.

### P1 — Realtime und Signal

- Mono, Stereo Link, Dual Mono, Gegenphase, ungleiche Kanäle.
- 128/256 Frames, reale Kette, Peak CPU und xruns über fünf Minuten.
- **Transformatorlast nach `MESSTECHNIK.md`:** Serie A (Boards
  `GS76x0…GS76x4`, 128/256 Frames) wurde **am Gerät gemessen** — Tabelle in
  `MESSTECHNIK.md`, Median 46–48 %, Spitzen ~66 %, 0 xruns. **Serie B fehlt
  noch:** `transformer_bench` im MPB-/Arm-Build auf dem Gerät ausführen,
  `--transformer 0,1,2,3 --oversampling 0,1,2 --channels 1,2 --level-dbfs
  <Wert>`. Das ist die einzige Möglichkeit, die Transformatorkosten zu messen,
  weil die Boards auf None/OS Off stehen und `None` den Solver vollständig
  überspringt. Hoher Eingangspegel erhöht die Last, deshalb den Pegel immer angeben.
- Die x86-Vorhersage in `PERFORMANCE.md` 5c sagt: Transformatorstufe rund
  doppelte Kernlast, 4× OS allein etwa vervierfacht, Solver nur 2,0–2,6
  Iterationen und 0 % am Limit. Diese Zahlen **widerlegen oder bestätigen**,
  nicht als Gerätewert zitieren.
- Regler-/Link-/Bypass-/Compressionwechsel, Snapshots/MIDI/Automation.
- Alle fünf Transformatorstufen, schnelle Modell-/OS-Wechsel, None-Recall und
  sechs farbige Factory-Presets bei pegelgleichem A/B prüfen.
- `EXTERN.md` nutzen: alle 38 Presets auf geeignetem Musikmaterial;
  31 gegen 37 und 35 gegen 38 mit 4:1/2:1 vergleichen; Attackkorrektur 21/22 hören.
  Erst gleiche Inputwerte vergleichen, danach Ziel-GR über Input und Lautheit
  über Output anpassen. Mix nicht als GR-Einstellung verwenden.
- Kurzer/langer Burst, Bass, Schlagzeug, Sänger, Guitar, Piano bei pegelgleichem A/B.

### P2 — Build-/Modellabgleich

- Nach Möglichkeit offizieller MPB-`moddwarf-new`-Build, ABI/Hash dokumentieren.
- Nicht offizielles Arm-GCC9-Binary ist hier ABI-geprüft, nicht device-geprüft.
- Höhere Ratios messen: im sauberen 1-kHz-Test wurden etwa 4,00 / 7,41 / 9,96 /
  14,73 gemessen, nominale Labels sind keine harte Brickwall-Garantie.
- Neuer Versuch 6 fährt 20:1 überwiegend unterhalb des Knies; für Ratio-Abnahme
  geeigneten höheren Input wählen. Versuch 7 ist ein Frequenzvergleich, keine
  Attack-/Release-Zeitkurve.
- Starke Colour-only-Sättigung ist gemessen (etwa 3,5–20 % THD nahe 0 dBFS).
  Gefaltete H9-Kandidatenlinie ~21,45 kHz/−72 dBc bei hohem Drive: Alias-
  Konvergenz und Hören prüfen, nicht nur nominalen THD-Wert vergleichen.
- Klang-/Zeitkalibrierung bei Bedarf zuerst anhand dokumentierter Signale,
  dann C++ **und** EEL2 zusammen ändern, Parität neu ausführen.

### P3 — NAM-Färbungsreferenz

- Vier `.nam` plus `desc.txt` separat besorgen; nicht im Codepaket enthalten.
- A2 48 kHz/Full explizit, A1 Rate unbekannt; Profile nicht im Oversamplingloop
  naiv höher takten und nicht hinter GR kaskadieren.
- Zuerst offizielle NAM-Core-Inferenz verifizieren, dann Frequency/Harmonics/
  Burst/Polarity/Gainstaging messen. Keine „Capture = Hardwaretruth“-Behauptung.

## Bereits lokal belegt

Details/Versionen in `PROJEKT.md`: Native Build, CMake/CTest, Signal-/LV2-ABI,
Blockgrößen/In-place, 430 JSFX-Paritätsfälle, 76 Presetzustände, historische GFX-Kompilation/
Render, Turtle-Parsing, AArch64-Symbolfloor, NAM-Dateiinventar.
Zusätzlich CPU-Benchmark und 80 Vorher/Nachher-Burstregressionen.

## Noch nicht belegt

Für 0.4.1 kein echtes Dwarf-Laden, keine reale REAPER-Host-GR-/Font-/-
Automation-/Recall-Abnahme, kein Originalhardware- oder NAM-Core-Färbungsfit.
Serie A der Lastmessung ist am Gerät gemessen (`MESSTECHNIK.md`); Serie B
(`transformer_bench` am Gerät) steht aus. Diese Punkte nach tatsächlicher
Ausführung aktualisieren. Historische Dwarf-Leerlaufmessungen stehen in
`PERFORMANCE.md`; sie gelten nicht als Abnahme der neuen Transformatorstufe.
Vorhandene alte Cross-Binaries vor Installation neu bauen, Versionsnummer und
Hash prüfen.
Scarlett-Liveaufnahme vom 2026-10-05 ist ausgeführt, aber wegen Loop-Gewinn
−63 dB nur für Latenz-/Mid-Band-Plausibilität verwertbar; Klirr-/HF-Aussagen
brauchen die Folgeläufe nach `MESSTECHNIK.md` (Pegel, 48-kHz-Geräteraten,
Wiederholungen, 96 kHz für 20 kHz).

## Änderungshinweise

- Quelle aller generierten Dateien: `data/*.json` und `tools/generate.py`.
- Bei eigenem Compilerwechsel neuen BUILD_DIR nutzen.
- Keine originale Elternverzeichnis-Datei überschreiben, keine unklar
  lizenzierten Profile mit Distributionspaketen mitgeben.
- Source-/Runtime-APIs in `DSP.md`, physikalische versus provisorische
  Annahmen in `DSP.md`.
- Ohne Commitauftrag nichts committen/pushen. Der initiale Repozustand hat noch
  keine Commits gehabt; inzwischen liegen Implementierungs- und Messdaten-
  Commits vor. Aktuellen Gitstatus vor Weiterarbeit prüfen.


---

<!-- ===== Teil 6: Quelle docs/DECISIONS.md ===== -->

# Entscheidungen und Entwicklungshistorie

## D15 — GUI, Preseterweiterung und Scarlett-Testwerkzeug, 0.4.1

Ausdrücklicher Benutzerauftrag erlaubt jetzt Klangwertkorrekturen: Kick Weight
Attack 5→2 und Snare Crack 5→3, weil ihre Namen/Absichten mehr Frontkante
nahelegen. Neue 2:1-Presets 37/38 werden angehängt, 31/35 bleiben 4:1.
Die erste 36er-Reihenfolge bleibt erhalten, Factory-Recall 21/22 ändert den
Klang bewusst. Version deshalb 0.4.1. Alle übrigen Klangwerte erhalten.

Die größere GUI-Lücke liegt vollständig zwischen COMP und Oversampling
(40 px), OS und Link folgen mit 7 px. Ratio bleibt bündig zu den oberen Potiwerten.

Scarlett 2i2 1st Gen: explizite Gerätewahl, Stereoaufnahme bei einseitiger
Wiedergabe, neuer Messordner je Lauf. PCM24-Stimulus plus JSON-Plan,
Float-Aufnahme und separate WAV-Analyse. Zwei unterschiedliche Chirps
identifizieren Zeitversatz und Taktabweichung. Frequenzangepasster Sinusfit
statt unkontrollierter FFT-Bin-Ablesung; direkte Kabelreferenz für relativen
Gain, keine Subtraktion von Verzerrung. dBu nur mit eigener ADC-Kalibrierung.
Keine Hardwarebedienung durch das Skript, keine reale Scarlett-Abnahme lokal.

## D13 — Refit-fähige Eingangstransformatoren, 0.4.0

Die instabile frühere xformer.lib ist als Laufzeitgrundlage verworfen.
Eigener partieller Jensen-Datenblattfit mit gemeinsamer Quelle/Last,
Flussverkettung und positivem Stop-Gedächtnis; Profile 60s warm, 80s
ausgewogen, 00s clean. `Symmetric` wird zur linearen technischen Referenz.
Bankrevision und Fit-/Importhashes in `data/transformers.json`, gemeinsamer
Generator und validierter Import statt eingebetteter handgepflegter Tabellen.
Keine Dateiladung im Audiothread; Refit bedeutet neuen Build/JSFX-Include-Stand.

Input vor Transformator, Dry davor, Colour unabhängig, Output hinter Detektor.
Modellwechsel über Eingang aus/ein, OS umfasst den Kern, PDC bleibt 0/3/4.
HF mit angepassten Polen statt ungeeigneter Base-rate-Tustin-Nullstelle;
Amplitude und bekannte Phasendifferenz ausdrücklich in `DSP.md`.

## D14 — MOD-GUI mit Hostwidgets und Asset-Vorlagen

Spaltfreie Paneele und Titel direkt auf Grün nach Benutzerwunsch. Alle Potis
nutzen `lv2/green-stripe-76.lv2/modgui/assets/aluminium.png` als 65-Frame-Filmstrip, Bypass die zwei vertikalen Frames
von `lv2/green-stripe-76.lv2/modgui/assets/toggle.png`, Status SVG zunächst 28×28 px. Mode ausdrücklich `mod-widget="switch"`
mit MOD-Klassen `on/off`. Nur der obere Rand ist Drag-Handle. Echter
MOD-Widget-/jQuery-UI-Browsertest statt bloßer Prüfung der HTML-Zeichenketten.

GUI-Nacharbeit auf Benutzerwunsch: Orange für die Colour-Beschriftung verworfen,
rechte Platte ohne Gruppentitel. GAIN/TIME mit vollhohen Sektionen, durchgehender
Trennlinie und identischem Schraubenabstand an den Modulecken. Die 20
Phillips-Kreuze haben feste individuelle Winkel; nur die Schlitze drehen sich,
die Beleuchtung der Köpfe bleibt oben links. Sechs kleine Wertefelder in
Dropdown-Grau, Bypass ohne gedruckte Beschriftung, Pilot-SVG zuletzt auf 44×44 px.
Leichte Schatten nach rechts unten auf Paneel, Modulkanten und Bedienelementen;
PNG-Vorschauen schließen den äußeren Schatten auf transparentem Rand mit ein.
Weitere Verdichtung: Transformer ohne Überschrift, ausgeschriebene Auswahltexte
mit „Transformer“. Fußbereich 12 px kürzer; LED und Bypass mit gemeinsamer
Mitte auf der Colour-Poti-Achse. Module und Fußzeile nutzen dasselbe 2:1:1-Raster,
gleich breite Plätze gleichen unterschiedliche LED-/Schalterbreiten aus.
ENGINE-Bedienung weiter vereinfacht: keine Überschriften für Mode, Oversampling
und Link. Mode zeigt `COMP ON` / `COMP OFF` im beweglichen Griff, gesteuert
durch die tatsächlichen MOD-Widgetklassen `on/off`. Die Auswahlfelder tragen
`No Oversampling` / `2x Oversampling` / `4x Oversampling` sowie `STEREO LINK` /
`DUAL MONO`; ihre numerische Zuordnung bleibt 0/1/2 bzw. 1/0.
GAIN/TIME ebenfalls ohne Gruppenüberschriften. Alle drei Potimodule verwenden
dasselbe Zeilenraster einschließlich reservierter unterer Dropdown-Zeile:
Input/Attack/Mix und Output/Release/Colour sind dadurch exakt höhengleich.
Auch ENGINE nutzt das gemeinsame Zeilenraster: Ratio-Auswahl und obere
Potiwerte sind bündig, unabhängig von Mono/Stereo. COMP und Oversampling
bildeten zunächst eine Gruppe mit 16 px Innenabstand, ab 0.4.1 40 px vor
Oversampling und 7 px danach; die Schiebertexte enthalten
Leerzeichen statt Unterstrichen.

## D01 — Eigener Green Stripe

Anfangs gewünschte Rev.-A-/Blue-Stripe-Nähe, anschließend eigene Green-Stripe-
Gestaltung, zuletzt ausdrückliche Korrektur: **Revision A oder D egal**.
Die jetzige Implementierung ist deshalb eine eigene, dokumentierte Adaption.
Quellen behalten ihre tatsächliche Revision, Pluginname verspricht keine.

## D02 — Gemeinsamer, frameworkfreier Kern

C++11 und EEL2 mit identischen mathematischen Operationen. Kein JUCE/WebView-
Runtime für Dwarf; nur C-ABI-Deskriptoren/float Ports. ysfx als unabhängiger
Testhost, nicht als Runtime-Abhängigkeit. 0.1.0: 134 Audiofälle; 0.1.1: 152
mit zusätzlichen langen Übergängen tatsächlich verglichen.

## D03 — Implizite Feedback-Regelung

Abgriff nach nichtlinearem FET/Preamp, vor Output. Bounded Backward Euler statt
Base-rate-Einzelsampledelay. Analytische saubere Gain-Law-Ableitung plus
safeguarded Newton/Bisektion. Eine vollständige Schaltungs-ODE ist nicht
vorausgesetzt und nicht behauptet.

## D04 — 4× feste Rate

Gesamte Regelung und Färbung oversampled. Kurze Polyphasen-IIR-Kette; keine
variable Qualität in 0.1.0, damit Zustände/Latenz/Parität kontrollierbar bleiben.
Inputrate verändert interne Koeffizienten. 4 Frames nominale PDC ausdrücklich
nicht als linearphasiger exakter Delay beworben.

## D05 — Interner Mix/Bypass auf hoher Rate

Beide Wege teilen Resamplingphase, Dry vor Input. Vermeidet zusätzliches
IIR-Phasenproblem eines völlig ungefilterten Dryzweigs. Farbfilterphase verbleibt
Teil des Wetcharakters. Externer Dwarf-Parallelzweig erfordert eigenen Test.

## D06 — Link ein/aus

Ursprünglich L/R und gemeinsamer Betrags-Max-Controller warmgehalten.
Ab 0.1.1 nur aktive Controller, beim Umschalten Zustandsübernahme und temporäre
Gain-Crossfadeberechnung aller drei. Kein L+R-Detektor und keine elektrische
1176-SA-Identität. So entfällt unnötige dreifache Regelarbeit im stabilen Link.

## D07 — Meter nur JSFX

LV2 technisch nur Latency-Output; keine GR-/Level-Controloutputs oder GUI-Meter.
JSFX Peak/RMS/Hold/GR getrennt vom Core, atomare Block-Snapshots, GFX read-only.
Mono verarbeitet Input L auf beide Outputs; keine unbemerkte L/R-Summierung.

## D08 — Presets sind Startwerte

Anfangs 26, aktuell 36 eigene Instrumentvarianten auf Grundlage zugänglicher Praxisquellen. Keine
universellen Input-/Outputwerte; Ziel-GR zum Abstimmen. `.rpl`-Bänke plus
eingebauter Selector, Custom nach manuellem Eingriff. Keine „garantierte“
Klanggleichheit mit originalen Clock-/T-Pad-Stellungen.

Prüfung 2026-10-05: alle 36 gegen Portdaten, LV2/RPL und echte Signalverarbeitung
abgeglichen. Factory-Klangwerte/Nummern bleiben erhalten; widersprüchliche
Attack-, Mix-/GR- und Quellenbeschreibungen korrigiert. Piano Gentle und Stereo
Bus Subtle sind die zwei empfohlenen **eigenen 2:1-Varianten**, keine historische
1176-Einstellung. Die Drittel-GR-Behauptung bei gleichem Eingang ist korrigiert:
festes Feedback-Tap-Niveau und festes Eingangsniveau sind nicht dasselbe.
Vollständige Einzelbewertung und gemessener Ratiovergleich in `EXTERN.md`.
Die erweiterte reale Signalparität fand bei Preset 29 einen EEL2-Rundungsfall
im Newton-Nenner. Explizite, gespiegelte Zwischenschritte beheben die
abweichende Intervallwahl; 430 allgemeine und 72 Presetfälle nun bitgleich,
144 native Vorher-/Nachherfälle ebenfalls. Keine neue Solver-Toleranz.

## D09 — NAM offline

Vier Capturemodelle analysiert, aber Rate/Settings/Bypass teilweise unbekannt.
Kein Kaskadieren oder Modellrate-Oversampling ohne Prüfung. Profile separat,
Hashes und Metadaten in Doku. Für kleinen gemeinsamen Runtimekern keine
WaveNet-/Eigen-/NAM-Loader-Abhängigkeit.

## D10 — Neue DSP-Referenzen

Paulllux' Divider/LN-Modell und Erläuterungen gelesen. Keine fremden
JUCE-/Transformer-/Pot-Tabellen importiert, weil eigener Kernel und
Referenzplugin-Kalibrierung eine klare Provenienz brauchen.
Schroeders tanh-Artikel führte zur präziseren gemeinsamen Padé-[7/6]-Funktion
inklusive analytischer Bias-Normalisierung. Kein Fast-Math/Float-Bit-Hack.

## D11 — Externe Praxistests, lokale Prüfungen trotzdem ausführen

Benutzer hat Dwarf/REAPER auf anderem Rechner. Hier native C++-/ABI-/Turtle-/
JSFX-Paritäts-/Grafik-/Presetprüfung. Cross-Build mit offizieller Arm-GNU-A9-
Toolchain, ursprüngliche glibc-2.17-libm-Symbolbindung; keine behauptete echte
Dwarf-Ausführung. MPB-Zweitbuild und Echtzeitlast im Übergabeauftrag.

## Noch zu entscheiden nach externen Ergebnissen

- Feinabstimmung hoher Ratio/Attack-/Releasebereiche anhand klarer Proben.
- Echte Farbkalibrierung gegen verifizierte NAM-Core-/Hardwaredaten.
- Weiter reduzierte Control-/LUT-Struktur nach Eichas, falls CPU nach den
  belegten 0.1.1-Optimierungen noch zu hoch ist; zuerst Zeitdaten/Fitting.
- Samplegenaue REAPER-Automation versus jetzige geglättete Blocksteuerung.
- Falls externe Parallelphasigkeit nötig: linearphasige oder zusätzliche
  Kompensationsvariante statt unerklärter Änderungen am jetzigen Bundle.

## D12 — CPU-Optimierung mit Dissertation-Abgleich, 0.1.1

Operationcounts zeigen 97 % Entladefälle, aber vorher exp/log-Zielauswertung
und dreifachen Stereo-Regler. Optimiert: gecachte Bias/Kniekonstanten, begrenzte
kubische Release-exp/log-Inkremente, Endpunktfastpaths, ausgerollte EEL2-
Resampler, letzte Subphase-Meter, Regler-Einrasten, aktive Controller und Parken.
Keine Oversamplingreduktion wegen bereits sichtbarer Alias-Kandidaten.

80 stationäre Burstfälle sind praktisch numerisch gleich; bewusste Änderungen
nur im Off-/Link-Startzustand, zusätzliche Übergangstests. Ein Feed-forward-
LUT-/Dreifiltermodell aus der Dissertation wäre eine weitere Kalibrierstufe,
nicht ungeprüft dieselbe Klangimplementierung. `PERFORMANCE.md` erläutert
Messzahlen, Seitenbelege und Grenzen.


---

<!-- ===== Teil 7: Quelle docs/STATUS.md ===== -->

# Historie: Archive früherer Stände

## Archiv: letzter Stand 0.4.0

Die nachfolgenden 36-/72-Presetzahlen, unveränderten Factorywerte und die
frühere 16-px-GUI-Lücke beschreiben den vorherigen Stand. Maßgeblich ist oben
0.4.1 mit 38/76 und den ausdrücklich beauftragten Änderungen.

### Erneute Presetprüfung und 2:1-Vorschläge, 2026-10-05

Vollständige Einzelbewertung aller **36 Presets** in
[`EXTERN.md`](EXTERN.md), reproduzierbare Signalwerte und Hashes
in `PRESET_AUDIT.json`. Alle gespeicherten Klangwerte, Namen, Zielspannen,
Nummern und Reihenfolgen sind gegenüber `c3153bf` unverändert. Factory-TTL,
RPL-Bänke und JSFX-Preset-Include bleiben bytegleich.

- Korrekte Ratio-Indizes: aktiv 22 × 4:1, 9 × 8:1, 3 × All; zwei
  Compression-Off-Presets. Sechs Transformatorzuordnungen weiterhin passend.
- Notizen zu Neutral, Vocal Transformer, Kick/Snare, Parallel-GR und Mixbus
  präzisiert. Attack 5 ist ca. **68 µs**, nicht langsam; Ziel-GR ist Wet-GR
  **vor Mix** und wird vorrangig über Input/Ratio/Regelzeiten eingestellt.
  Colour/Transformer können die Detektoranregung ebenfalls verändern; ihre
  eigenen Pegelverluste sind jedoch kein FET-GR-Meterwert.
- Zwei 2:1-Empfehlungen: **31 Piano Gentle** (1–2 dB Wet-GR) und
  **35 Stereo Bus Subtle** (0–2 dB Wet-GR). Zunächst nur Ratio ändern,
  danach Input/Output abstimmen; keine automatische Bank-Neuabstimmung.
- Die frühere „ein Drittel GR“-Aussage bei gleichem Eingang wurde in
  `DSP.md` korrigiert; fester Tap-Pegel ist nicht fester Eingang.
- **72 LV2/RPL-Zustände** gegen normative Werte geprüft, **216 native
  Presetfälle + 12 Ratiovergleiche** gerendert: endliche Signale, beide
  Compression-Off-Presets exakt 0 dB GR. Keine Musik-/Hörabnahme daraus ableiten.
- Der neue echte Preset-Signal-Paritätssatz fand bei **29 Drum Parallel Crush
  Mono** eine bisher ungetestete EEL2-Nenner-Rundung mit abweichender
  Newton-/Bisektionswahl (max. **0,000409722 FS** vor Korrektur).
  C++/EEL2-Nennerauswertung explizit angeglichen, keine Toleranz gelockert.
- Abschließend **430 allgemeine + 72 Preset-Signalvergleiche bitgleich**,
  `make test`, Generator/RDF und CMake/CTest 3/3 PASS. C++-Regression gegen
  `c3153bf`: **144 Fälle bitgleich Audio/GR/Latenz**. Die korrigierte JSFX kann
  im genannten Randfall vom alten JSFX-Render abweichen.
- Paketierung geprüft: `EXTERN.md` und `PRESET_AUDIT.json` liegen
  neben `PRESETS.md` im JSFX-ZIP, ZIP-Integrität PASS.

Noch offen: geeignete Musikquellen, pegelgleiches 4:1-/2:1-Hören und reale
REAPER-/Dwarf-Abnahme. Die folgenden technischen Implementierungsangaben und
archivierten älteren Messberichte bleiben ihren jeweiligen Ständen zugeordnet.

### Implementierter Produktstand

- **Transformator hörbar in C++ und JSFX:** None / 60s warm / 80s ausgewogen /
  00s clean / Symmetric als lineare technische Referenz. Eigener lastgekoppelter
  Flux-/Stop-Kern aus dem partiellen Jensen-Offlinefit, keine Übernahme der
  instabilen xformer.lib. Input treibt den Kern; Colour bleibt eigenständig.
- **Refit ohne DSP-Umbau:** versionierte normative `data/transformers.json`,
  Referenz aus `data/model.json`, validierter Import über
  `tools/transformer_model.py`, gemeinsam generierte C++-/EEL2-Daten.
  Bankrevision `gs76-input-2026-10-05-v1`; Herkunftshashes in der Bank.
  Refit-Vertrag, unterstützte Parameter und Projektkompatibilität in
  [`DSP.md`](DSP.md).
- Kanalgetrennte Historien, gewählte OS-Rate auch im Kern, 2-ms-Modellblenden
  über den Eingang, Dry/Bypass und Latenz 0/3/4 Frames erhalten.
- **LV2-GUI:** Paneele spaltfrei, Titel ohne Schild direkt auf Grün,
  Aluminium-Filmstrip für alle sechs Potis, Toggle-Bitmap für Bypass,
  Pilot-On/Off-SVG auf 44×44 px. Mode verwendet jetzt das echte Switch-Widget
  und dessen `on/off`-Klassen. Nur der obere freie Rand ist Drag-Handle.
- Vorschau-PNGs werden aus echtem HTML/CSS in Chromium gerendert;
  vorhandene statische Nachzeichnung abgelöst. 36 Presets / 72 Bankzustände.
  Veraltete xformer.lib-Aussagen in Presetnotizen durch die neuen Klangprofile
  ersetzt. Alle Factory-Recall-Wege setzen Oversampling auf Off.

### GUI-Nacharbeit — Rack-Optik, 2026-10-05

- Colour-Beschriftung neutral wie die übrigen Potis; Orange verworfen.
  Rechte Modulplatte ohne „COLOUR“-Gruppentitel.
- GAIN/TIME-Sektionen füllen die volle innere Höhe. Durchgehende Trennlinie
  und vier Phillips-Schrauben je Modul mit denselben Eckabständen wie im
  grünen und rechten Feld; alle 20 Schraubenkreuze individuell orientiert.
- Sechs eingerahmte Wertefelder unter den Potibeschriftungen mit gemeinsamer
  Farbe `#e0e5e7` wie das Transformer-Dropdown.
- Bypass ohne gedruckte Beschriftung (Tooltip/zugänglicher Name erhalten),
  Pilot von 28 über 36 auf 44 px vergrößert. Dezente Schatten nach rechts unten,
  Licht von oben links; Schraubenkopf-Beleuchtung unabhängig vom Schlitzwinkel.
- Transformer-Auswahl ohne eigene Überschrift, mit selbsterklärenden LV2-GUI-
  Texten `No Transformer`, `60s Transformer`, `80s Transformer`, `00s Transformer`
  und `Symmetric Transformer`. Fußbereich um 12 px gekürzt (Paneel 375 px hoch).
  LED und Bypass teilen eine mittig unter dem Colour-Poti angeordnete Gruppe;
  gemeinsame Rasterspalten für Module/Fußzeile und gleich breite Steuerplätze.
  In Mono und Stereo geometrisch geprüft: Mittelpunkt der beiden Bedienelemente
  exakt auf der Poti-Achse (0 px Abweichung).
- ENGINE ohne Überschriften für Mode, Oversampling und Link. `COMP ON` bzw.
  `COMP OFF` sitzt direkt im beweglichen Schiebergriff und folgt den MOD-
  Schaltzuständen. Oversampling zeigt `No Oversampling`, `2x Oversampling`,
  `4x Oversampling`; Stereoauswahl `STEREO LINK` / `DUAL MONO`.
  Beide Schiebertexte in Mono/Stereo per echtem MOD-Widget 1→0→1 geprüft:
  richtige Sichtbarkeit, vollständig innerhalb des Griffs, Controlwerte 0/1.
- GAIN/TIME-Gruppentitel entfernt. Gemeinsames Zeilenraster für alle Potimodule,
  mit reservierter Dropdown-Zeile auch links: Input/Attack/Mix sowie
  Output/Release/Colour jeweils auf derselben Höhe. Mono/Stereo geometrisch
  geprüft: 0 px Reihenabweichung; LED-/Bypass-Mittelpunkt weiterhin auf der
  Colour-Achse, Paneelhöhe weiterhin 375 px.
- Ratio-Auswahl auf Höhe der Wertefelder Input/Attack/Mix, gleiche Feldhöhe
  20 px und 0 px vertikale Abweichung in beiden Varianten. Zwischen COMP und
  Oversampling 16 px Abstand. Texte mit Leerzeichen (`COMP ON` / `COMP OFF`)
  per echtem MOD-Widget und erneuertem Mono-/Stereo-Rendering geprüft.
- Mono-/Stereo-Browsertest mit echten MOD-Widgets bestanden; `make
  check-generated` (17 Artefakte) und `tools/validate.py` einschließlich
  RDF-Parsing bestanden. Gerätebedienung/-darstellung weiterhin extern offen.

### In dieser Umsetzung tatsächlich ausgeführt

| Prüfung | Ergebnis |
|---|---|
| GNU 15.2, C++11, no-fast-math/FP-contract off | Native Build PASS (`build/wsl`) |
| `make test` | DSP, Übergänge, Transformator, reale LV2-ABI, Refit-Validierung, Metadaten PASS |
| Generator | 17 Textartefakte konsistent |
| Refit-Import | Bank aus archiviertem `transformer/offline_fit/profiles.json` bytegleich reproduziert; ungültige Modelle abgelehnt |
| Source-/JSFX-Paketierung | ZIP-Integrität, sieben Includes/Bank und Ausschluss von Audioarchiven/PDF/NPZ/NAM PASS; Prüfarchive unter `/tmp/opencode/gs76-packages` |
| RDF | Turtle-Parsing mit rdflib 7.6.0 PASS |
| C++/EEL2 | **430 allgemeine + 72 Preset-Signalvergleiche, max. 0 FS**, echte ysfx-Ausführung |
| None gegen vorherigen Commit | **144 Fälle bitgleich**, Audio/GR/Latenz einschließlich OS-/Bypass-Wechsel |
| CMake/CTest | Unabhängiger Build, **3/3 Tests PASS** |
| Native ELF | x86_64, nur libm/libc, GLIBC bis 2.4, kein GLIBCXX |
| RPL/Selector/Custom | **72 Presetzustände PASS**, zusätzlich 72 Werteabgleiche mit LV2/Quelldaten |
| Transformatoranker 20 Hz/48 kHz | 60s **1,00009 %**, 80s **1,00271 %**, 00s **1,00001 %** THD an −14/−8/−2 dBFS |
| Unabhängige Offline-Referenz | Rohsignalabweichung max. **5,42×10⁻¹⁵ FS**, Bass/DC/Bursts bei 44,1/48/96/192 kHz |
| HF-Surrogat gegen analog | Amplitude max. **0,3081 dB**, Phase max. **67,91°** abweichend; keine Phasengleichheit |
| MOD-Widgets in Chromium | Beide Varianten: Mode, Filmstrip, Drag-Trennung, Bypass/Lampe, Paneelfugen PASS |
| Lokale Durchsatzmessung | C++ Stereo Off ca. 0,020 s/s None bzw. 0,032–0,034 s/s mit Modell; EEL2-Matrix in `PERFORMANCE.md` |

Testhost ysfx `5c3452fee62583aa3d1b7e877d0c758c4024af89`; MOD-UI
`7a35aac69781af28997aee7e560a92da7146f318`, Chromium 153.0.8010.12.
Die lokale Native-Toolchain ist kein Dwarf-Artefakt. Frühere Build-/Gerätewerte
im Archiv unten gelten nicht als erneute Abnahme von 0.4.0.

### Offene Punkte und nächste konkrete Arbeit

1. 0.4.0 mit MPB `moddwarf-new` bauen, aktuelle AArch64-ABI/Hashes und Pakete
   erzeugen; vorhandene alte Cross-Binaries nicht als neuen Build übertragen.
2. `PROJEKT.md`: MOD Dwarf 1.13.5.3315, reale Mode-/Regler-/Drag-/Bypass-
   Bedienung und neue Assetanzeige prüfen; REAPER 7 Recall/Automation/Host-GR.
3. Transformator-/OS-Matrix mit Eingangssignal, 128/256 Frames, mehreren
   Instanzen und mindestens fünf Minuten CPU/xruns je Zustand messen.
4. Pegelgleiche Musik-/Transientenprüfung und Alias-/Phasenvergleich.
   Hochfrequente Analogphasengleichheit ist beim aktuellen HF-Surrogat nicht
   gegeben; Low-rate-Aliasing bleibt zu bewerten.
   `EXTERN.md`: Ziel-GR nach Input-Abgleich; Piano Gentle und Stereo
   Bus Subtle mit 2:1 gegen ihre ursprünglichen 4:1-Werte hören.
5. Weitere Fits mit neuen Referenzdaten und dokumentierter Bankrevision;
   vorhandenen partiellen Datenblattfit nicht als Hardwarekalibrierung ausgeben.

**Keine Geräte-/Hörtests für 0.4.0 in dieser Arbeitsumgebung ausgeführt.**

## Archiv: Entwicklung bis 0.3.0

Die folgenden Implementierungsbeschreibungen, Prüfstände und „nächsten Schritte“
sind historisch. Insbesondere „Transformator ohne Klangwirkung“, alte GUI-
Namensschilder, Fallzahlen, Binärhashes und frühere Modellplanung beschreiben
den damaligen Stand; der aktuelle Status steht oben.

## 1. Implementiert

- Frameworkfreier C++11-DSP und identischer EEL2-Kern.
- 4×-Polyphasen-IIR-Verarbeitung von Audiopfad **und** Feedback-Regelung.
- Nichtlinearer FET-Divider, impliziter begrenzter Regler, programabhängige
  Erholung, All Buttons, asymmetrische Färbung und Output nach Detektor.
- LV2-Mono-/Stereo-Deskriptoren in einem Bundle, Enabled/Compression/Mix/Colour,
  optionaler Link, separate Kanal-/Controllerzustände, keine Meterports.
- Zwei Fehler in der Werkzeugkette gefunden und behoben, die nur auf einem der
  beiden Rechner sichtbar waren: `tools/generate.py` benutzte
  `Path.write_text(..., newline='\n')`, und dieses Schlüsselwort gibt es erst ab
  Python 3.10 — auf der Testmaschine mit **3.9** konnte der Generator überhaupt
  nicht schreiben und brach mit `TypeError` ab. Und `Path.read_text()` ohne
  `encoding` nutzt die **Locale**, unter Windows also cp1252; die UTF-8-Dachs in
  `data/presets.json` wurden dadurch zu `â€“` und `make check-generated` meldete je
  nach Rechner eine andere Datei als veraltet. Beides ist behoben: der
  Schreibpfad geht über `open(..., newline='')`, alle `read_text()`-Aufrufe in
  `tools/` setzen `encoding='utf-8'`. Der Nachweis ist der Bytevergleich: Windows
  Python 3.9 und WSL-Python erzeugen `docs/PRESETS.md`, `lv2/green-stripe-76.lv2/presets.ttl` und
  `GreenStripe76-Presets.jsfx-inc` jetzt identisch. Ohne diesen Test wäre eine
  der beiden Plattformen still die falsche gewesen.

MOD-GUI ab 0.3.0 als querformatiges Paneel mit **drei senkrechten Bereichen**:
  eine **breite GAIN/TIME-Platte** (349 px, fast exakt die Fläche der früheren
  beiden Bays zusammen) als zweispaltiges Raster mit Haarlinie in der Mitte,
  sodass jeder Regler seine eigene GAIN- bzw. TIME-Überschrift behält; das
  **grüne ENGINE-Feld** (Verhältnis, Comp-Kippschalter COMP ON/OFF, Oversampling,
  Link) als „The Green Stripe"; COLOUR (Mix, Colour, Transformator). Die
  GAIN/TIME- und die COLOUR-Fläche sind bewusst **glatt**: ein einheitliches Grau
  `#aeb5b8` ohne Verlauf, ohne Innenkante und ohne Bürstung. Ein Verlauf über ein
  hohes schmales Feld liest sich als gebürstetes Metall, das war dort nicht
  gewollt; das Außenpaneel behält seine Bürstung, damit sich die Flächen weiter
  unterscheiden. **Produktname „Green Stripe 76" in Weiß auf einem eigenen
  dunkelgrünen Namensschild** `#1c5a39`, 8 px vom Bay-Rand, Text 116 px breit und
  15 px hoch mit 20/21 px seitlichem und 4 px vertikalem Innenabstand. Das Schild
  ist keine Geschmacksentscheidung allein: Weiß direkt auf dem hellen Grün wäre
  nur **2,33:1**, auf dem Schild sind es **7,75:1**, und nur so bleibt die
  Kontrastregel des Paneels (helle Flächen, fast schwarze Schrift) für alle
  übrigen Beschriftungen intakt. `#206440` erreichte nur 6,74:1 und wurde
  verworfen.
  Jeder Poti trägt seine **Endanschlag-Markierung** daneben: `Min.`/`Max.` auf
  Input, Output, Mix und Colour, `Slow`/`Fast` auf Attack und Release. Die Legende
  steht bewusst **neben** statt unter dem Regler: eine zweite Textzeile würde einen
  Zweiregler-Bay höher machen als einen Bay mit Select, und weil die Bay-Inhalte
  vertikal zentriert sind, lägen die Bays dann nicht mehr auf einer Linie.
  Regler 48 → 50 px nominal. **Mix** wieder in Stahl wie die übrigen,
  **Colour** als einzige orange Fläche, farblich verwandt mit der
  **bernsteinfarbenen Betriebslampe** (13 → 17 px) **vor** dem Bypass-Kippschalter,
  11 px links davon. Im DOM bleibt die Lampe **hinter** dem Bypass und wird nur
  über `order:1` optisch vorgezogen: es gibt keinen Rückwärts-Geschwister-
  Selektor und `:has()` ist auf diesem WebKit nicht verlässlich. So liest der
  Selektor `.gs-bypass.mod-active ~ .gs-lamp` weiterhin den Bypass-Zustand; die
  Lampe zeigt also den Bypass, nicht den `enabled`-Port. Bays sind dunkler als das
  Paneel, damit die Gruppierung nicht nur über Farbe trägt; bewusst ohne GR-/Level-
  Meter. Screenshots/Thumbnails aus `tools/make_assets.py` im selben Layout.
  Nachgemessen: kleinster Textkontrast 7,55:1, Lampe 13 px mit 49/49 Bernstein-
  pixeln im Kern, Regler-Durchmesser 51 px.
- Transformator-Auswahl ab 0.3.0: Port `transformer` (LV2 Enum, **Index 16
  Stereo / 13 Mono**, angehängt nach Latenz und Oversampling, `connectionOptional`,
  Default `None`), JSFX slider13, fünf Stufen `None / 60s / 80s / 00s /
  Symmetric` aus `docs/sauce/xformer.lib`. **Ohne Klangwirkung** — der Wert läuft
  durch den Parameterpfad und ist preset-adressierbar, ist aber nicht mit dem
  Audiopfad verbunden. Echtzeitform und Alternativen in `DSP.md`
  Abschnitt 11.
- Der Transformator ist eine **Klangwahl und wandert mit dem Preset**. Er wird
  deshalb anders behandelt als das Oversampling: `tools/generate.py` führt beide
  angehängten Ports über `appended_value()`, aber Oversampling startet nach jedem
  Recall auf Off (Qualitäts-/CPU-Wahl), während das Transformatorfeld aus dem
  Preset gelesen wird. Belegt sind 6 von 36 Presets — 11 *Guitar Colour Only*
  (`60s`), 12 *Vintage Blue Grit* (`60s`), 13 *Guitar Cruncher* (`80s`),
  19 *Bass Mojo Bite* (`80s`), 20 *Huge Sub Weight* (`00s`),
  24 *Snare Saturated Parallel* (`80s`); die übrigen 30 stehen auf `None`. LV2, JSFX-Selektor und RPL-Bänke sind gegen denselben Helper
  erzeugt, können also nicht auseinanderlaufen; `tests/jsfx_parity.cpp` prüft
  Slider 12 und 13 jetzt mit und liest die erwartete Presetzahl aus dem
  Selektorbereich statt aus einer festen Zahl.
- `compression` trägt ab 0.3.0 explizite Scale-Points `COMP OFF` / `COMP ON`
  (vorher `lv2:toggled` ohne Beschriftung), damit der Kippschaltertext nicht von
  undokumentiertem `mod-active`-Verhalten abhängt.
- JSFX-Meter: Skala −60 bis 0 dBFS (0 = Clipping), Orange ab −12 dBFS,
  Rot ab −3 dBFS, breitere Balken, Peak-Hold 2 s; MAX-Peak in der
  Gruppenkopfzeile; alle Zahlen als ~3-Hz-Snapshots in @gfx (Display-
  Globals, kein Audiozustand); Kopfzeile in die Fußzeile verlagert
  (REAPER-MCP zeigt nur den oberen Streifen), Kennzahlenzeilen oben,
  Legende entfernt.
- JSFX Mono/Stereo mit GR/Peak/RMS/Hold/Clip und Host-GR-Meldung für REAPER 7.
- 26 Instrumentpresets, zwei `.rpl`-Bänke, eingebauter Selector und Custom-Erkennung.
- Native Make/CMake-Builds, offizielles MPB-Skript/Rezept, zusätzlicher AArch64-
  Cross-Build, Archiv-/Hash-/ABI-Werkzeuge.
- Proben-/Offline-WAV-Renderer, NAM-Inventar und vollständige Markdown-Doku.
- `AGENTS.md` und `PROJEKT.md` für andere Session/Testrechner.
- CPU-Optimierung 0.1.1: gecachte Bias-/Kniekonstanten, Release-exp/log-Inkremente,
  ausgerollter EEL2-Resampler, aktive Controller statt dauerhaft dreifach,
  Parken bei Off, Regler-Einrasten und letzte-Subphase-Meterumrechnung.
- Oversampling 0.2.0: Off/2x/4x als neuer Regler (JSFX slider12, LV2-Port nach
  Latenzausgabe, `lv2:connectionOptional`), Default Off; Latenzport meldet
  0/3/4 Frames; Umschaltung blendet über `ceil(0.002·Rate)` Samples aus und
  ein (Sample-Zähler, keine Float-Akkumulation), drei vorberechnete
  Koeffizientensätze, Resampler-Reset und Release-Cache-Invalidierung beim
  Wechsel; OS betrifft Audiopfad und Regelkreis, Presets und Factory-Bänke
  setzen Off; MOD-GUI-Selektor und JSFX-UI-OS-Anzeige.
- Paritätsrobustheit 0.2.0: shared Series-Kernel `seriesLog`/`seriesExp` ↔
  `gs_series_log`/`gs_series_exp` (Attack-/Release-Zeiten, Koeffizienten,
  Detector-`gainDb`/`dbGain`) mit gespiegelter Operationsreihenfolge;
  `std::pow`/`std::exp`/`std::log`/EEL2-`^` im DSP-Pfad entfernt; NebenEffect:
  keine GLIBC-2.29-Symbolreferenzen mehr.

## 2. Tatsächlich ausgeführte Prüfungen

### SPICE-Transformatorprüfung 2026-10-05

Der Auftrag `docs/QUELLEN.md` ist als eigene Offline-Untersuchung
ausgeführt. Ergebnisse unter **[`docs/spice_sim/`](QUELLEN.md)**:
Bericht, vier Einstiegsnetlists, vollständige Mess-CSVs, Wellenformauszüge,
340 Laufnetlists/-logs, Hash-/Herkunftsmanifeste und Reproduktionsskripte.

- **ngspice 45.2:** 260 Hauptarbeitspunkte (vier Modelle × fünf Frequenzen ×
  13 Pegel), 76 Diagnosefälle und vier protokollierte Original-Include-Abbrüche.
  `C/a/n/R/b/m/Np/Ns` unverändert; 48-kHz-Punktabtastungen, analoge H3/H5
  zusätzlich aus feineren adaptiven Solverzeiten.
- **Numerisch reproduzierbar:** KCL-Zustandsform gegen unabhängige
  DDT-/Hilfsinduktorform, Zeitschritthalbierung und Gear/Trapez abgeglichen.
  Max. Gainänderung bei Zeitschritthalbierung **1,55×10⁻⁷ dB**.
  Abschließende Wiederholung der vier Einstiegsnetlists: **bitgleiche
  vollständige Messarrays**. `spice_sim/verify_results.py` bestätigt Betriebspunktmatrix,
  unveränderte Modellparameter, Provenienz und 668 endliche Wellenformarrays;
  `SHA256SUMS` enthält 722 geprüfte Artefakte.
- **Inhaltliches Ergebnis:** Alle vier Netze besitzen einen instabilen
  Nullzustand; Nullsignal mit `10⁻⁷ V` Anfangsstörung bestätigt die positiven
  Pole. Keine Rückwirkung der Sekundärlast, kurze Fenster überwiegend
  Expansion, spätere Fenster driftend. Die bisherige `φ_k`-Herleitung ist
  dimensionswidrig und **nicht bestätigt**; neue Klang-Kniekoeffizienten,
  Kniebreite und stationärer DC-Offset sind nicht bestimmbar.
- **Nächster Schritt:** Netzform, Vorzeichen, Einheiten, gemeinsamer Kern und
  Last-Rückwirkung klären, anschließend neu simulieren. Die bisherigen
  Schwellenzahlen sind kein freigegebener DSP-Fit. `Symmetric` bleibt
  ausschließlich Prüfreferenz. In dieser Arbeit wurden keine DSP-/JSFX-/
  Presetänderungen und keine Geräte-/Hörtests ausgeführt.

### Ergänzung: Transformator-Paper ausgewertet, 2026-10-05

Die lokale PDF *Real-Time Audio Transformer Emulation for Virtual Tube
Amplifiers* (de Paiva et al., 2011, DOI 10.1155/2011/347645) wurde vollständig
gelesen; zentrale Schaltbilder, Formeln und Tabelle 1 zusätzlich visuell
geprüft. Bericht: [`QUELLEN.md`](QUELLEN.md).

- **Nutzbare neue Grundlage:** bidirektionales GC-/WDF-Modell mit gemeinsamem
  Kern, Leerlauf-Strom-/Spannungsmessung und zweistufigem Parameterfit;
  vollständiger publizierter Fender-NSC041318-Parametersatz in Tabelle 1.
- **Einordnung des SPICE-Befunds:** Die lokale `xformer.lib` bildet diese
  Struktur nicht korrekt ab; ihre Instabilität widerlegt nicht die
  veröffentlichte GC-Methode.
- **Offen vor Umsetzung:** `b`-Normierung der Gl. 17/18, Sekanten-/
  Differentialpermeanz sowie Stabilität der im Paper verwendeten
  Ein-Sample-Verzögerungen. Periodischer 80-Hz-Fit ist kein Transiententest;
  historische 96-kHz-PC-Messung ist kein Dwarf-CPU-Nachweis.
- **Nächster Schritt:** separate Offline-Referenz nach Abb. 6(b)/Tabelle 1
  aufbauen, gegen WDF-Näherung prüfen, danach Green-Stripe-Skalierung und
  eigene Stufen bestimmen. Dieser Schritt war Literaturauswertung;
  keine neue Simulation des Paper-Modells und keine DSP-Änderung.

### Ergänzung: Hersteller-Kennlinien gelesen, 2026-10-05

Alle drei PDFs in `docs/transformer/` (sechs Seiten, acht Diagramme) sind
als Text und Bild ausgewertet. Bericht:
[`QUELLEN.md`](QUELLEN.md), dazu
47 ausdrücklich grobe visuelle Ableseintervalle in
`transformer/KENNLINIEN_ABLESUNG.csv`; PDF-Hashes, CSV-Struktur und
Seiten-/Intervallbezüge geprüft.

- Hammond **140TEX und 560Q sind 1:1**; Lundahl **LL1930 ist regulär
  5,8:1/11,6:1** und enthält keine grafischen Kennlinien.
- Belegt sind vor allem Tiefbass-Nichtlinearität sowie beim 560Q
  HF-Anhebung und pegelabhängige Phase. Das sind passende Zielkurven
  für eine Line-Stufe, keine Begründung für starken Breitbandklirr.
- Offene Quellenfragen: 140TEX-Last 1000 Ω im Frequenzgang versus
  100 Ω bei THD+N; dBm-Pegelbezug/Normalisierung; L-/Impedanz- und
  Anschlusskonventionen beim 560Q. THD+N enthält Rauschen, keine
  getrennten H2/H3/H5 und keine Hystereseschleifen.
- Nächster Schritt: dokumentierte Quelle/Last und elektrische
  Volt-Skalierung festlegen, Amplituden-/Phasenziele gemeinsam fitten,
  anschließend Tiefbass-Nichtlinearität mit geklärter Referenz bewerten.
  Dies war Datenblattarbeit, keine neue Simulation oder Hardwaremessung.

### Ergänzung: Fitgrundlage und Schätzbereiche, 2026-10-05

Die zusätzlich genannten PDFs und der GroupDIY-Thread sind ausgewertet.
Bericht: [`QUELLEN.md`](QUELLEN.md).
Whitlock und Lundahl-Whitepaper vollständig; McLyman gezielt zu
Magnetisierung/Materialien/Parasiten; GroupDIY alle 22 Beiträge.

- **Neue konkrete 1:1-Referenz:** das in Whitlock enthaltene Jensen
  JT-11P-1-Datenblatt, Stand 1/01, mit 600-Ω-Quelle / 10-kΩ-Last,
  DCR und THD über Pegel/Frequenz. Typischer 1-%-THD-Punkt bei
  **+20 dBu / 20 Hz**. Für den ersten sauberen Line-Eingangsfit empfohlen.
- **Schätzen ist für einen ersten Gray-Box-Fit möglich:** effektives
  LF-L, HF-`f0/Q`, Flux-Skala, schwaches Gedächtnis und explizite digitale
  Pegelzuordnung. Feste Quellenwerte und eigene Suchbereiche stehen in
  `transformer/FIT_STARTWERTE.json`; Rechenweg
  `transformer/estimate_fit_start.py` ausgeführt und plausibilisiert.
- **Noch fehlend für Eindeutigkeit:** Magnetisierungsstrom, einzelne
  Harmonische, Transienten/Remanenz und zusätzliche Quellen-/Lastbedingung.
  Niedriger relativer Pegelklirr kann Hysterese oder Noise enthalten;
  keine pauschale Noise-Subtraktion. DLP nicht als rohe Phase verwenden.
- **Nächster Schritt:** Jensen-Kurven mit Intervallen aufbereiten und den
  eingeschränkten Offline-Fit ausführen; unterschiedliche plausible
  Parametersätze und zurückgehaltene Messkurven prüfen. Bisher nur
  Literatur-/Rechenarbeit, kein Jensen-Fitlauf, DSP-Port oder Hörtest.

### Ergänzung: Erregerstrom und weitere Modellquellen, 2026-10-05

Alle sechs HiFiHaven-Seiten / 110 Beiträge, StackExchange-Frage 606060
mit drei Antworten (offizielle API nach HTTP 403 der Webseite) und die
vier neu genannten PDFs sind ausgewertet. Bericht:
[`QUELLEN.md`](QUELLEN.md).

- Erregerstrom ist nicht ohne Weiteres reiner Magnetisierungsstrom;
  Verlust-/Parasitenanteile und Phase/Wirkleistung beim Fit berücksichtigen.
- `05_e.pdf` liefert einen relevanten Audiovergleich Fröhlich/J-A.
  Als Baseline zunächst dynamische Sättigung mit korrekter Lastkopplung,
  dann schwaches Gedächtnis vergleichen; kein Materialparametersatz des
  Gitarrenausgangsübertragers wird zum Jensen-Eingangsmodell erklärt.
- Die anderen Papers betreffen 40-kHz-Stromwandler, Wicklungsfehler-FRA
  und statischen NN-Kennwertfit eines 500-kV-Modells. Verwendbare Methoden,
  aber keine neuen 1:1-Audiofitdaten. Gedruckte Zeitdivisions-/Statistik-
  fehler im FRA-Paper und unklare NN-Grafikskalierung dokumentiert.
- Nächster Schritt bleibt der eingeschränkte Jensen-Offlinefit mit
  Modellvergleich und Anfangszustands-/Burstprüfungen. Diese Arbeit war
  Quellenanalyse und algebraische Prüfung, keine neue DSP-/Geräteabnahme.

### Erster Jensen-Offlinefit und drei eigene Profile, 2026-10-05

Der anschließend beauftragte **Fit wurde tatsächlich ausgeführt**.
Ergebnisse, Skripte und Hörproben:
[`transformer/offline_fit/`](QUELLEN.md),
Detailbericht [`QUELLEN.md`](QUELLEN.md).
Benutzerentscheidung: **60s warm → 80s ausgewogen → 00s clean**.

- **Jensen JT-11P-1, reduzierter Datenblattfit:** 53 Zielbedingungen,
  33 Training / 20 zurückgehalten, 18/20 Validierungsintervalle getroffen.
  Das vollständige Modell trifft 24/33 Trainingsintervalle; Restfehler
  bleiben ausdrücklich sichtbar. Fröhlich-artiger Flux-Kern mit schwachem
  positivem Stop-Gedächtnis, Lastkopplung und effektivem HF-Surrogat.
- **Gemessene Modellwerte:** −2,28468 dB Gain; 0,02145 % THD bei
  +4 dBu / 20 Hz; 1 % THD bei ca. **+20,49 dBu**. Der typische
  Herstelleranker +20 dBu wird nicht exakt getroffen (dort ca. 0,591 %).
  Keine identifizierte Hardware-/Hysteresegleichheit behauptet.
- **Profile tatsächlich abgeleitet:** 20-Hz-1-%-THD bei **−14/−8/−2
  dBFS Peak**, gemeinsame Skalierung; 60s weiches p=3-Potenzmodell,
  80s p=5, 00s Jensen-artig. 20-kHz-Abweichung ungefähr
  **−1,304/−0,129/−0,046 dB**. `transformer/offline_fit/profiles.json` enthält vollständige
  Offlineparameter, eigene Zielwahl und feste Gainnormalisierung.
- **Verifikation PASS:** Schrittweitenverfeinerung, unabhängiger
  DOP853-Solver, kausale 48/96/192-kHz-Bursts, Symmetrie,
  Kern-Leistungsbilanz und reale Modell-Last-/Quellenrückwirkung.
  High-rate-HF-Vergleich bis 768 kHz. Das ist kein PASS des gesamten
  Datenblattfits; dessen Abweichungen sind in der CSV dokumentiert.
- **Artefakte:** 168 Profil-Arbeitspunkte, Fit-/Vergleichsdiagramme,
  native Wellenformdaten und sieben 12-s-/48-kHz-Float-WAV-Proben
  (bei 768 kHz gerendert, antialiasgefiltert). 35 Artefakte gehasht,
  wiederholte 1-%-Anker und Float-WAV-Struktur geprüft.
- **Nächster Schritt:** Proben hören und die Profilabstimmung bewerten;
  bei akzeptiertem partiellen Fit Produktport C++/EEL2 gemeinsam,
  Rate-/Oversampling-/Übergangskonzept und Dwarf-CPU prüfen.
  Noch kein Transformator im Laufzeit-DSP und kein Hör-/Gerätetest.

**Revalidierung 2026-10-04:** Die nachfolgend als PASS geführten Kernergebnisse
wurden in dieser Arbeitsumgebung erneut ausgeführt, nachdem eine Toolchain ohne
Root bereitstand und ysfx `5c3452f…` wiederhergestellt war: `make test` PASS,
`jsfx_parity` **PASS mit 232 Fällen und max = 0 FS**, `.rpl`/Selector/Custom
**PASS mit 62 Presetzuständen**. Damit sind diese Zeilen heute gemessen und nicht nur
übernommen. `tools/validate.py` lief dabei nur **strukturell** (kein `rdflib`);
die Zeile „Turtle/RDF PASS mit rdflib 7.6.0" stammt aus dem Testrechner und
wurde heute **nicht** wiederholt.

| Prüfung | Stand / Ergebnis |
|---|---|
| Native GNU15 Build | PASS, C++11, Warnflags, no-fast-math/FP-contract off |
| `make test` | PASS nach letzter Divideroptimierung |
| Native Signaltests | PASS: Gain, Bypass/Mix, Ratios, Output/GR, Link/Dual-Mono, Gegenphase, Extremwerte, Reset, KCL-Residual |
| Übergangstests 0.1.1 | PASS: lange Link-/Off-Umschaltung, endliche Signale, zero-GR im geparkten Zustand |
| Actual LV2 ABI | PASS: beide Deskriptoren, run(0), in-place, block 1/64/128/256/511 bei 44,1/48/96k |
| CMake/CTest | PASS: unabhängiger Buildweg und Signaltest |
| CMake-ysfx-Testintegration | PASS: gepinnter Host als Unterprojekt inkl. SHA512-Prüfung, 232 Renderfälle und Benchmarkziel |
| Generierte Textdateien | PASS, 15 Artefakte check-generated |
| Turtle/RDF | PASS mit rdflib 7.6.0, alle Bundle-TTL |
| Presetbereiche/Assets/Includes | PASS: 36 Presets, beide Varianten |
| EEL2-Compile | PASS mit gepinntem ysfx, einschließlich tatsächlicher GFX-Sektion |
| Audio-C++/JSFX-Parität | **PASS: 232 Fälle** (ab 0.2.0 inkl. 72 OS- und 8 OS-Umschaltfälle), größte float-Port-Abweichung **0 FS** (bitgleich) |
| 0.1.0/0.1.1 Burstregression | PASS: 80 stationäre Fälle (neu@4x gegen Altstand), max Audio ~7,1×10⁻¹⁴ FS, GR ~2,4×10⁻¹¹ dB |
| OS-Umschaltterminierung | PASS: Probe über ~2700 Raten 8k–384k, Auf/Ab/Rapid-Toggle, Latenz folgt, endliche Signale |
| LV2-OS-Latenz/Umschaltung | PASS: 0/3/4 Frames, blockinvariante Mid-Stream-Wechsel bei 64–512 Frames |
| Release-Approximation | PASS: analytische exp/log-Fehlergrenzen bei 8/44,1/48/96/384k; Series-Kernel ≤ ~1,2×10⁻¹⁴ relativ zu libm |
| Native Benchmark 0.2.0 | Mono mode0 0,0146 s/s (+5 % gegen 0.1.1-Stand), Stereo mode0 0,0223 s/s (+10 %); Checksummen stabil; keine Dwarf-Aussage |
| CPU-Matrix 0.2.0 | Stereo 48k, Bestwert/5: Off+C0 0,0091 s/s; Off+C100 0,0191 (2,1×); 2x+C100 0,0385 (4,2×); 4x+C100 0,0704 (7,7×). Colour verdoppelt wegen nichtlinearem Kern, OS skaliert mit Subframenzahl; keine Dwarf-Aussage |
| Echte JSFX-CPU-Messung | Uninstrumentiert ysfx: normal Mono ~42 %, Stereo Link ~50 %, clean Stereo ~76 % weniger Zeit |
| `.rpl`/Selector/Custom | PASS: **62 Presetzustände** (31 je Variante), echter ysfx-Banklader/Rendering; prüft auch die angehängten Slider 12/13 |
| GFX-Offscreen | PASS: Mono/Stereo tatsächlich gezeichnet, Controllerzustand unverändert |
| NaN/Inf | PASS: native und JSFX-Eingangssanierung; EEL2-NaN-Vergleichsfall korrigiert |
| Probe-Werkzeuge | PASS: acht PCM24-Proben generiert, 336000-Frame-LV2-Render als float WAV |
| NAM-Dateien | Alle vier JSON/Weights finite, Metadaten/Hashes/Lookback dokumentiert |
| AArch64 Cross-Build | PASS: Arm GNU-A GCC9.2, Cortex-A35, ELF64/AArch64 |
| AArch64 Symbolfloor | PASS: nur **libm/libc, GLIBC_2.17**, kein GLIBCXX, kein X11/WebView |
| Übergabepakete | JSFX-/Source-ZIP und Dwarf-tar.gz, Integrität und SHA256 geprüft; keine NAM/WAV/Build-Reste |

Gepinnter Testhost: JoepVanlier/ysfx
`5c3452fee62583aa3d1b7e877d0c758c4024af89`; Library/JIT wirklich gebaut und benutzt.
Die Probes/Fremdtoolchain lagen unter `/tmp/opencode`, keine Systeminstallation.

### Gemessene statische Sekantenratios

Core colour=0, Attack=7, Release=1, 1-kHz-Sinus, Inputamplituden 0,3→0,6,
48000 Hz, nach Einschwingen:

| Label | gemessen |
|---|---:|
| 4:1 | 3,99946 |
| 8:1 | 7,40713 |
| 12:1 | 9,95998 |
| 20:1 | 14,7262 |

Hohe Ratio wird im vollständigen zyklisch ladenden/entladenden Regler schwächer
als das statische algebraische Nominalmodell. Das ist **bekannt**, kein beweisbar
originaler Hardwareeffekt. Gezielt beim externen Klang-/Dynamikabgleich bewerten.

### CPU-Messungen

Historisch 0.1.0: `make benchmark`, x86_64/WSL-Session, 48k, 1 Sekunde Ton, Colour=100, Input=6:
nach rationalisierter Dividerlösung etwa **0,058–0,066 s Mono** und
**0,136 s Stereo** pro Audiosekunde. Nur lokaler Durchsatz, **keine Dwarf-CPU-Aussage**.
Frühere per-Tap-Newton-Fassung kostete deutlich mehr; geschlossene Lösung
verifiziert über KCL-Residual und Parität.

0.2.0 nativer Benchmark (`make benchmark`, gleiche Maschine): Mono mode0
0,01464 s/s, Stereo mode0 0,02230 s/s — gegen den 0.2.0-Stand vor dem
Series-Umbau (+5 % Mono, +10 % Stereo). Ursache sind die Series-Kernel statt
libm exp/log im Detector-/Solver-Pfad; der Release-Pfad bleibt seriesbasiert
wie in 0.1.1. Absolute Kosten weiter klein gegen Realtime.

### CPU-Messung auf dem Zielcodecortex-A35 (MOD Dwarf)

Erstmals auf dem **eigentlichen Zielprozessor** gemessen, nicht nur auf x86_64.
Gerät: MOD Dwarf, OS 1.13.5.3315, Kernel 6.1.15-rt7-moddwarf, aarch64
Cortex-A35 (`0xd04`), 4 Kerne, jackd 48 kHz. Build: Arm GNU 9.2-2019.12,
`-O3 -mcpu=cortex-a35`, `tools/check_abi.py --dwarf` PASS (GLIBC-Floor 2.17).

Der Plugin-Host läuft als Threads im jackd-Prozess; die Last wurde daher über
jackds `utime+stime` mit gelesenem `CLK_TCK` (100) erfasst, 40 Samples je 20 s,
**ein Vollstart pro Bedingung** (ein jackd-Neustart genügt nicht, die
Hardware-Controlchain behält ihren Zustand). Pro Bedingung geprüft: `.so` in
`/proc/<jackd>/maps` und Binär-md5.

| Block | 0 Instanzen | 1× Stereo | 2× Stereo | je Instanz |
|---|---:|---:|---:|---:|
| 128 | 10,91 % | 24,66 % | 37,66 % | **+13,4–13,8 %** |
| 256 | 7,57 % | 19,98 % | 32,59 % | **+12,4–12,5 %** |

Prozent eines Kerns, jackd inklusive. 4 Instanzen bei 128 Frames: +13,2 % je
Instanz. Das Verhalten ist linear und nahezu blockgrößenunabhängig, wie es für
eine feste 4×-Sample-Verarbeitung erwartbar ist. Eine Stereo-Instanz kostet
damit etwa **3,4 % der vierkernigen Gesamtleistung**.

**Offen und ausdrücklich nicht behauptet:** keine xruns (Plugin-Host-API auf
diesem Gerät defekt), keine Messung mit Eingangssignal (Detektor praktisch
stumm, also untere Schranke), kein Hörtest, kein REAPER-Vergleich. Beim ersten
Durchgang wurde die Binär-md5 durch eine UI-Installation auf eine ältere Binary
geändert; diese Serie wurde **verworfen** und mit dem HEAD-Build wiederholt.

Für die LUT-Frage ist das entscheidend: Es gibt auf dem Zielgerät keinen
CPU-Engpass, der eine `softClip`-LUT rechtfertigen würde. Details in
`PERFORMANCE.md`, Abschnitt 5b.

### Paritätsbefund 0.2.0 (ULP-Untersuchung)

Der erweiterte OS-Paritätssatz deckte auf: Bei 96 kHz Hostrate, OS 2x und
12:1 mit heftigem Attack-Transienten wichen EEL2 und C++ bis 5,9×10⁻⁴ FS
(sechs Stufen über der bisherigen 2×10⁻⁶-Grenze), während GR/Charge am
Streamende übereinstimmten. Ursachenkette, empirisch belegt:

1. `std::pow` (C++) und EEL2-`^` liefern für die Attack-/Release-Zeiten
   ULP-unterschiedliche Werte → 1-ULP-`alpha`-Differenz.
2. EEL2-JIT-`exp`/`log` und libm unterscheiden für einzelne Argumente um
   1 ULP (nachgewiesen u. a. an `amplifierLP`, seit 0.1.0 vorhanden, dort
   harmlos unter Float-Auflösung).
3. Im impliziten Regler-Solver kippt eine solche ULP-Differenz die
   Newton-vs-Bisektion-Entscheidung (`next>low && next<high`); ein
   Intervall von ~10⁻² ergibt dann Chunks von ~10⁻³ im Charge und
   ~10⁻⁴ FS im Audio, konvergiert aber wieder auf denselben Festpunkt.

Fix: alle transzendentalen Ausdrücke des DSP-Pfads über shared Series-Kernel
mit identischer Operationsreihenfolge (atanh-Reihe für log mit 2er-Exponenten-
zerlegung, Taylor mit 2^k-Skalierung für exp; Loop-Zählungen sind wegen
bitgleicher Eingänge deterministisch gleich). Damit sind alle 232
Paritätsfälle **bitgleich** (max=0 FS). Der Randfall „`sample()` vor dem
ersten `setParameters()`" bleibt wie in 0.1.1: unkalibrierte Detektorschwelle
führt zu NaN, das `finiteOr` zu 0 maskiert; reale Hostpfade rufen immer
zuerst `update()`/`gs_set`. Nicht Teil dieser Änderung.

0.1.1: tatsächliche JSFX-JIT-Ausführung mit identischen Vektoren, 48k/128 Frames,
Warmup und Median aus sieben zweisekündigen Läufen. Normal Mono ~42 % weniger
CPU-Zeit, Stereo Link ~50 %, Clean Stereo ~76 %, Dual Mono ~47 %.
Ausgeschaltete Regelung/Bypass spart deutlich mehr. Diese Werte sind **keine
REAPER-/Dwarf-Gesamt-CPU-Prozente** und kein Beweis für einen bestimmten Faktor
gegenüber anderen unbekannten JSFX. Sourcehashes: `CPU_BENCHMARK.json`;
Ursachen, Dissertationseiten und Betriebsänderungen: `PERFORMANCE.md`.

## 3. Binäridentität dieses Stands

| Datei | Bytes | SHA256 |
|---|---:|---|
| `build/native/green-stripe-76.lv2/green-stripe-76.so` | 49560 | `1f6df9981a67bdd95fce7f0dd8b6638d047fc7cd67a77390e20b80a03159083d` |
| `build/aarch64-gcc9/green-stripe-76.lv2/green-stripe-76.so` | 31816 | `6c7ea9ff5c45ff457f66d3926afc9a9125c0c0c475469401dbbe9fab45561a3a` |

Bei erneutem Build können Pfad/Toolchain/Metadaten Binärhash verändern. Maßgeblich
für die transferierten Archive ist deren mitgelieferter Herkunftsmanifest und
`dist/SHA256SUMS`.

## 4. Ergänzende externe Prüfung und weiterhin offene Abnahme

### Ergänzung: externe PluginDoctor-/ReaJS-Auswertung

Die jetzt vorhandenen **55 Dateien aus Versuch 1–7** in `evaluation_plugindoc` wurden vollständig
ausgewertet. Bericht: `docs/EXTERN.md`, Kennwerte/Hashes:
`docs/PLUGIN_DOCTOR_EVALUATION.json`.

- Externes **JSFX Mono in ReaJS**, PluginDoctor 2.3.2, sichtbare Green-Stripe-UI.
- Aus den Rastern abgeleitet 44,1 kHz, Dynamics-Sinus 2516,7 Hz.
- Standardkurve etwa **4,0045:1**; starker All-Modus etwa **19,9:1**.
- Vergleich Colour 100/0 verändert gerade Harmonische, fast nicht die Kennlinie.
- Delta-Spektren bei +6,45 dB/aktiver GR zeigen pegel-/zeitabhängige Impulsreaktion,
  keinen isolierten LTI-Frequenzgang. Native periodische Probe reproduziert die
  Daten mit **0,003–0,007 dB** maximaler FFT-Abweichung.
- Aktuelle native Identitäts-Resamplingkette ohne GR/Colour: praktisch eben,
  maximale Gain-Abweichung etwa **2×10⁻⁹ dB** über 20 Hz…20 kHz.

Dies ist **keine direkte REAPER-7-/Dwarf-/Stereo-Link-Abnahme**. In den
vorliegenden Dynamics-Exporten fehlen Attack-/Release-Zeitverläufe. Es wurden
in der Messauswertung selbst keine DSP- oder Presetwerte geändert. Danach
erfolgte die separat dokumentierte CPU-Optimierung 0.1.1; keine Änderung der
Threshold-/Knie-/Preset-/Oversamplingwerte. Die Messungen sind mit dem
optimierten Core nochmals reproduziert worden.

Erweiterung Versuch 4–7:

- Compression Off / Colour 100: Kleinsignal nahezu Unity, bei Sinusinput
  −0,32 dBFS etwa **3,52 % THD**; Input +15,6/Output −15,6 etwa **19,63 %**.
  Output-Absenkung kompensiert nicht die Vorverstärker-Sättigung.
- Clean-Pfad Versuch 6 (Input −15,6, Output +15,6, Colour 0): Delta-Spektrum
  im Audioband etwa −0,02…−0,071 dB, Spanne **0,04978 dB**. 20:1-Ramp liegt
  überwiegend unter dem Knie; daraus keine Nominal-Ratio-Abnahme ableiten.
- Versuch 7 ist LinearAnalysis in Hz, keine Zeit-/Attack-Release-Kurve.
  All und 4:1 haben bei identischem Impuls unterschiedliche Mittelband-GR.
- Alle fünf neuen Delta-Szenarien werden mit dem unveränderten Code auf
  **0,00003–0,00275 dB** maximale FFT-Abweichung reproduziert. Kohärente
  Sinusproben reproduzieren Grundtöne bis ~0,0022 dB und sinnvolle Partialwerte
  bis ~0,017 dB; auch kleine zusätzliche Linien werden reproduziert.
- Neuer Alias-Prüfpunkt: starkes Colour-only zeigt eine gefaltete-H9-
  Kandidatenlinie um **21,45 kHz / −72,33 dBc**. Weitere kleine Linien in
  schnellster GR. 4×-Oversampling ist damit nicht als allgemein aliasfrei
  zertifiziert; höhere Raten-/Oversampling-Konvergenz und Hören stehen aus.
- Analysewerkzeuge decken **alle 29 Textdateien** ab, optional fehlende IRs und
  die zwei separaten Linear-only-Graphen. Export- und Probe-/Codehashes im JSON.

### Weiterhin offen

- Reales Laden/Abspielen auf MOD Dwarf 1.13.5.3315.
- Device-CPU/xruns bei 128/256, mehrere Instanzen/echte Kette.
- Offizieller MOD-Plugin-Builder-GCC9.4-Zweitbuild: Docker-Engine hier nicht
  erreichbar. Vorhanden ist eigenständig ABI-geprüfter Arm-GCC9.2-Build.
- Reale REAPER-7-Host-GR, Fonts/HIDPI, Projekt-Recall, Automation/Freeze.
- MOD-Browser/SDK semantischer GUI-/Metadatencheck. PNGs sind eigene statische
  Illustrationen, kein Gerät-Screenshot.
- Originalhardware-Kalibrierung/ABX, verifizierter NAM-Core-Färbungsfit.
- Vollständige Alias-/Frequenz-/Transientenfehler-Matrix gegen High-rate-Referenz.

Diese Punkte führt der Agent auf dem anderen Rechner aus. Kein „auf Dwarf
getestet“ oder „hardwareidentisch“ aus den lokalen Ergebnissen ableiten.

## 5. Bekannte Modell-/Produktgrenzen

- Eigene Threshold-/Knie-/Färbungstabellen, keine Originalgerät-Parameterbank.
- OS-abhängige PDC: 0 (Off), 3 (2x) oder 4 (4x) Frames nominal, IIR-Phase
  frequenzabhängig. OS-Umschaltung blendet kurz aus/ein; Latenzport folgt
  erst nach Abschluss der Ausblendung. Externes paralleles Routing muss
  getestet werden.
- Ab 0.1.1 nur aktive Controller; Linkzustandsübernahme und Parken bei Off
  verändern Wiedereinschalt-/Linkübergänge bewusst. Reale Hör-/Hostprüfung offen.
- `slider_next_chg` nicht genutzt; derzeit geglättete Block-/Slidersteuerung.
- JSFX Mono nimmt linken Eingang auf beide Ausgangspins; keine automatische Summe.
- Kein Lookahead, kein garantierter True-Peak-/Brickwall-Limiter.
- **Transformator 0.3.0 ohne Klangwirkung.** Die Auswahl `60s/80s/00s/Symmetric`
  entspricht `GCOT-SE-01`, `GCOT-PP-03`, `GCOT-PP-04` und `GCSYMETRICAL` aus
  `docs/sauce/xformer.lib`, aber nichts davon ist mit dem Audiopfad verbunden.
  Die vierte Stufe ist keine Vintage-Variante: `xformer.lib` überschreibt
  `GCSYMETRICAL` mit `IMPORTANT: Only for testing purposes`. Sie ist eine Referenz
  mit hoher Schwelle und `n = 25`, keine Bauform.
  Die Dropdown-Beschriftungen sind neutral gewählt; die Gerätenamen der Fremdquelle
  erscheinen bewusst nicht in der Oberfläche. `Symmetric` ist laut Original
  Quelltext nur für Tests bestimmt.
- Das SPICE-Modell benutzt `DDT` (Ableitung) und ist nicht direkt echtzeitfähig.
  Vorgesehen ist ein integrierter Flux-Zustand; Alternativen und Latenzhaltung in
  `DSP.md` Abschnitt 11.
- NAM-Profilrate A1 unbekannt, Positionsdaten fehlen; nicht als reiner statischer
  Shaper oder kompletter steuerbarer Kompressor behauptet.
- Capturegewichte/WAVs nicht in Distribution.

## 6. Nächste konkrete Arbeit

1. Pakete/Hashes auf Testrechner übernehmen, `PROJEKT.md` abarbeiten.
2. Dwarf SDK-Install und REAPER JSFX-/RPL-Install; OS-Regler in beiden
   Umgebungen gegen Off/2x/4x hören und auf CPU messen.
3. Routing/Link/Bypass/Recall, Realtime und pegelgleiche Musik; nach den neuen
   Mono-Versuchen Zeitbereichs-Bursts und Alias-Konvergenz besonders priorisieren.
   OS-Umschaltung im laufenden Programm (Transport läuft) auf Knackfreiheit prüfen.
4. 0.2.0-Cross-Build (MPB moddwarf-new) und Symbolfloor neu bestümen; der
   Series-Umbau hat die GLIBC-2.29-Referenzen entfernt, Erwartung weiterhin
   nur libm/libc mit tieferem Floor. Das Buildroot-Rezept ist auf den
   Cloud-Builder-Fluss umgestellt (git-Quelle mit Commit-SHA statt
   `SITE_METHOD = local` mit `/root/source`); ein erfolgreicher
   Cloud-Build und eine Geräteinstallation stehen noch aus.
5. 0.2.0-Pakete erzeugen (`tools/package.py`) und Herkunft festhalten.
6. Ergebnisse mit `MESSTECHNIK.md`; gezielte Änderungen nur anhand
   Befund, C++/EEL2/Tests/Modelldoku gemeinsam.
7. **Transformator-Klangstufe (offen; Netzmodell nach SPICE-Befund neu klären).**
   Port und Oberfläche stehen. Die bisherige Planung lautete:

   - integrierter, **kanalgetrennter** Flux-Zustand nach dem Vorbild von
     `CORE_GC`, an der **Eingangsseite**;
    - **Frühere, jetzt unbestätigte Sättigungsschwelle:** normierter Flux `u = φ/φ_k` mit
     `u_knee = 1,0`; `φ_k` je Typ aus `φ_k = (C·ω/a)^(1/(n-1))` am geometrischen
     Bandmittel — 0,532 (`60s`), 0,337 (`80s`), 0,368 (`00s`). Ein gemeinsamer
     Wert statt vier absoluter, weil die Modelle nur 1,58 auseinanderliegen
     und die Reststreuung die Sättigungshärte der Bauarten ausmacht. Herleitung
     und Tabelle in `DSP.md` Abschnitt 11;
   - die **Kopplungs-Bassabsenkung entsteht aus dem gemeinsamen Kern** und wird
     **nicht** als eigener Regler exponiert;
   - die `flux`-/`Lowpass`-Färbung in `Colour` bleibt **unverändert**;
   - Latenz unverändert 0/3/4 Frames.

   **Neuer Vorrang:** `QUELLEN.md` auswerten und eine konsistente
   Übertrager-Netzform festlegen. Die vorhandenen Modelle sind um Null
   instabil; eine direkte Übernahme oder die frühere Knieformel liefert
   keinen belastbaren Klangkern. Danach erst neue Koeffizienten ableiten.
   Die inzwischen ausgewertete Arbeit de Paiva et al. (2011) liefert dafür
   eine konkrete Struktur und Tabelle 1 als Referenz; Vorgehen und offene
   Konventionen stehen in `QUELLEN.md`.
   Für ein 1:1-Line-Klangziel zusätzlich `QUELLEN.md`
   verwenden: Hammond 140TEX/560Q mit Amplituden-/Phasen-/THD+N-Zielen,
   deren Quellen-/Last- und Pegelkonventionen vor dem Zahlenfit zu klären sind.
   Die neue `QUELLEN.md` empfiehlt zunächst den
   besser bezeichneten Jensen-JT-11P-1-Datensatz aus Whitlock und enthält
   explizite Startschätzungen; damit kann ein eigener eingeschränkter Fit
   auch ohne zusätzliche Hardwaremessung beginnen.
   **Inzwischen ausgeführt:** Der erste Jensen-Offlinefit und die drei
   eigenen Profile liegen in `transformer/offline_fit/` vor. Maßgeblich
   sind `QUELLEN.md`, Fitrestfehler und `transformer/offline_fit/profiles.json`, nicht die
   früheren ungetesteten Schwellen oder Gitarrentrafo-Koeffizienten.
   Als Nächstes Hörbewertung der WAV-Proben und ein eigener Produktport-
   Auftrag mit C++/EEL2-Parität und Rate-/CPU-Prüfung.

   Bei späterer Umsetzung zwingend: Parität C++/EEL2, Dwarf-CPU-Messung und Hörtest, weil
   `ABS(v)^n` bis `n = 13` eine `pow`-Funktion je Wicklung und Sample verlangt
   und die Integrationsregel bei dieser Steilheit erst erprobt werden muss.
8. **Route 3 (Kennlinien-LUT) bleibt zurückgestellt.** Die in
   `docs/DSP.md` geforderte Vorstudie ist abgeschlossen und gegen den
   C++-Originalkern abgeglichen (bit-exakt, max. rel. Abweichung 0.0). Ein LUT
   für `fet()`/`gs_fet()` braucht drei kontinuierliche Achsen (input, charge,
   curvature) und zwei Polaritätstabellen, weil `fet` nicht ungerade ist
   (0,342 % bei x = 3). Der Fehler konvergiert sauber mit O(h²) und erreicht
   das Ziel 10⁻⁴ erst bei **264,8 MiB**; eine praxistaugliche Tabelle von
   16,7 MiB verfehlt es um Faktor 6. Ein LUT für `softClip()`/`gs_soft()`
   erreicht dagegen mit N = 1025 auf logarithmischer Achse 2,84×10⁻⁵ bei
   16 KiB. **Kein DSP wurde geändert.**
   Stand nach der Dwarf-Messung: Die **Dwarf-Zeitdaten liegen jetzt vor**
   (~13 % eines A35-Kerns je Stereo-Instanz, linear skalierend, siehe
   `PERFORMANCE.md` 5b). Sie zeigen **keinen CPU-Engpass**, der eine LUT
   rechtfertigen würde; zusammen mit dem x86-Befund, dass eine
   `softClip`-Log-LUT **langsamer** ist als die analytische Form und erst N = 2049
   die Genauigkeitsgrenze erreicht, ist die LUT-Frage als CPU-Maßnahme
   **entschieden abgelehnt**. Sie bleibt allenfalls eine Modell- und
   Färbungsfrage. Vor einer Umsetzung fehlen weiterhin REAPER-Zeitdaten, ein
   Hörtest und die Entscheidung, ob die Feedback- oder die Färbungsgenauigkeit
   überhaupt Priorität bekommen soll.

## 7. Git / Originaldateien

Das initiale Repository hatte keine Commits. Inzwischen liegen die vom Benutzer
übernommenen Implementierungs-/Messdaten-Commits vor; Messdatenstand
`424501a` („Plugindoctor auswertung“). In der aktuellen Analysesession wurde
kein Commit/Push/PR angelegt. `dist/` und `.so`-Dateien sind ignoriert; das
aktuelle `.gitignore` ignoriert `build/` nicht pauschal. Neue Diagnose-Binaries
sollten außerhalb des Versionsbestands bleiben. Elternverzeichnis-Originale und
externe Messdateien wurden nicht verändert.
| Label | Frames | p_median % | p_peak % | xrun | top thread (median % of core) |
|---|---:|---:|---:|---:|---|
| GS76M128 | 128 | 48.0 | 48.0 | 0 | jackd:20.9 |
| GS76Measure-f128 | 128 | 48.0 | 64.0 | 0 | jackd:21.266666666666666 |
| GS76Measure-f256 | 256 | 48.0 | 54.0 | 0 | jackd:21.066666666666666 |
| GS76x0-f128 | 128 | 48.0 | 50.0 | 0 | jackd:21.05 |
| GS76x0-f256 | 256 | 46.0 | 50.0 | 0 | jackd:20.9 |
| GS76x1-f128 | 128 | 47.0 | 52.0 | 0 | jackd:20.85 |
| GS76x1-f256 | 256 | 48.0 | 50.0 | 0 | jackd:20.95 |
| GS76x2-f128 | 128 | 47.0 | 50.0 | 0 | jackd:20.85 |
| GS76x2-f256 | 256 | 48.0 | 62.0 | 0 | jackd:21.05 |
| GS76x3-f128 | 128 | 46.0 | 50.0 | 0 | jackd:20.85 |
| GS76x3-f256 | 256 | 50.0 | 64.0 | 0 | jackd:21.4 |
| GS76x4-f128 | 128 | 48.0 | 50.0 | 0 | jackd:20.95 |
| GS76x4-f256 | 256 | 48.0 | 66.0 | 0 | jackd:21.35 |
