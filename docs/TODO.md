# Offene Aufgaben

Konsolidiert am **2026-10-06** nach der Dokumentenzusammenfassung. Details zu
jeder Position stehen in den verlinkten Dokumenten. Nicht ausgeführte
Geräte-/Hörtests werden nicht als bestanden geführt.

## Offen — Scarlett (siehe [MESSTECHNIK](MESSTECHNIK.md))

Aktueller Stand 2026-10-07: **Transformator-Matrix am Gerät ausgeführt**
(Dwarf-Quelle, REAPER-Aufnahme, `test-results/matrix-dwarf-20261007`):
Baseline/60s/80s/00s × r1+r2, Sym × r1, je 2 Kanäle, alle gültig; Anker exakt,
Wiederholungs-Spreizung ≤ 0,01 dB, 20-Hz-Klirr-Reihung 60s 5,53 % / 80s 2,15 % /
00s 0,11 % / Sym 0,01 %. OS-Stellung laut Benutzer **2x** (in Index/Label
nachgetragen). Ergebnisse in PROJEKT.md.

**Aktualisierung 2026-10-07 (nachmittags):** Bundle `48ab885` (HEAD) mit MPB
`moddwarf-new` gebaut und installiert. Die **erste** Wiederholung war ungültig
(alle Läufe transparent — Binary-Austausch ohne Audio-Stack-Neustart, alter
Instanzzustand); die **zweite** Serie (`test-results/matrix-dwarf-20261007-b2`,
Digital-Capture + Analog-Loop) ist gültig und deckt sich mit der digitalen
Referenz bis in die 4. Dezimale: 20-Hz-Klirr 60s 12,42 % / 80s 12,28 % /
00s 1,00 % / Sym 0,00 %, relative Gains −0,817/−0,441/−0,016/−0,002 dB.
**Die aktuelle Bank ist am Gerät messtechnisch bestätigt**; die Nachtwerte
(5,53/2,15/0,11 %) sind dieselbe Bank bei je Lauf unbekannter
Eingangsdämpfung (H3/H5-Beleg; die Gerät-Binary trägt die aktuellen
Bankkonstanten bitweise). Auswertung/Interpretation gegen die Modellanker
in `EXTERN.md` ist durchgeführt: 1-%-Anker von 00s (−2 dBFS) exakt
getroffen, 60s/80s by design (Anker −14/−8 dBFS). Vollständige Messwerte
und Grafiken: [MESSERGEBNISSE](MESSERGEBNISSE.md) (generiert).

- [x] Aktuelles Bundle installieren, Matrix wiederholen und gegen die
  digitalen Referenzen prüfen (b2, gültig).
- [x] Colour-Serie am Gerät (Transformer None, Colour 5/10/20/50/75/100):
  deckt sich mit der digitalen Referenz bis in die 4. Dezimale
  (`test-results/colour-dwarf-20261007`); 1-kHz-Klirr/Gain skalieren linear
  mit Colour. JSFX-Render-Referenzen (Colour-Punkte + Typen bei Colour 0)
  bit-exakt gegen C++ verifiziert.
- [x] Bank×Colour-Interaktion: vollständige Matrix (Colour 5–100 % ×
  60s/80s/00s/Sym, 24 Zustände) als JSFX-Render erzeugt und bitgleich gegen
  C++-Referenzen verifiziert (MESSERGEBNISSE 2.5). Direkte Gerätemessung
  **bewusst nicht ausgeführt**: beide Pfade einzeln am Gerät exakt validiert
  (Abschnitte 1/2), JSFX ≡ C++ bitweise, keine zusätzlichen Codepfade in der
  Interaktion — residual dokumentiert als Schlussfolgerung, nicht als
  Gerätemessung.

- [x] Sym-Wiederholung und engere Mediane: durch die b2-Serie (Digital-
  Capture, deterministisch, Sym als eigener Lauf) obsolet — die digitalen
  Captures haben keinen Laufzeit-Spread; die alte Analog-r1/r2-Spreizung
  (≤ 0,01 dB) bleibt als Archivnotiz in Serie 1.
- [x] Dwarf-INPUT-Meter als Referenz: obsolet — mit Dwarf-Quelle ist der
  Plugin-Eingang digital exakt bekannt; entscheidend ist die INPUT-Knopf-
  Stellung (Unity), die je Lauf dokumentiert werden muss (siehe Serie 1).
- [ ] 96-kHz-Messung entfällt für die Dwarf-Quelle (Player läuft mit der
  fester Geräterate 48 kHz); 20 kHz bleibt damit nah an Nyquist gemessen.
- [ ] Windows-Geräteformat abschließen (nur noch relevant, falls der
  Mess-Treiber statt REAPER aufnimmt): mmsys.cpl Aufnahme auf 24 bit/48000 Hz.
- [ ] PluginDoctor-Sweep-Wiederholung zurückgestellt (PD erlaubt hier keine
  Einstellungssteuerung; Marker-Sync über `scarlett_test.py` ist der
  verlässliche Weg).

## Offen — Dwarf/Gerät (siehe [PROJEKT](PROJEKT.md), Abschnitt Übergabe)

**OS-Wechsel 2026-10-08: MOD Dwarf läuft auf 1.14 RC4 (build 3366)** —
Testbuild („Evelyn, a Modified Dog"; Forum-Thread 13493). Neuer
Audio-Stack (jack2, mod-host), neue Frameworks; **Gerät-Stand 1.14 RC4
ist kein Release-Verifikationsstand** — die 1.13.5-Ergebnisse bleiben
die releasegebundenen Referenzen, bis 1.14 stable ist.

- [ ] Install-Verifikation auf 1.14: SHA256 des installierten Binaries
  nach dem nächsten Install prüfen (Thread-Warnung betrifft den Duo,
  trotzdem am Rechner verifizieren, nicht nur am Gerät); Plugin-Mapping
  und Load prüfen (`dwarf_loadtest.py --expect-instances`).
- [ ] modgui-Pfad neu verifizieren: `grep setOutputPortValue
  /usr/share/mod/html/js/modgui.js` auf 1.14 ausführen (mod-ui wurde
  aktualisiert; die 0.5.0-VU-Nadel hängt an diesem Pfad), dann
  VU-Funktionssichtprüfung am Gerät.
- [x] **Port-Gruppen am Gerät prüfen:** 1.14 zeigt „Grouped plugin
  controls" (gruppiert + farbcodiert in der Settings-View). **Umsetzung
  2026-10-08 abgeschlossen:** normative `data/port_groups.json` + `group`-Feld
  in `data/parameters.json`; Generator gibt `pg:group`, Gruppenressourcen
  (`Compressor`, `Levels`, `Colour`, `System`, `Meter` als `pg:OutputGroup`,
  Audio-Paare als `pg:StereoGroup`/`pg:MonoGroup` + `pg:mainInput`/
  `mainOutput`) aus; `validate.py` prüft Zuordnung, Symbolfreiheit
  (pg-Namensraum geteilt mit Ports), Mono/Stereo-Typen. Indizes/Symbole/
  URIs unverändert, JSFX/RPL/Presets unberührt, keine src/jsfx-Änderung
  (keine Revision). **Offen: Sichtprüfung der Gruppierung am 1.14-Gerät**
  (nach dem nächsten Paket-Install).
- [ ] CPU-Spotcheck auf 1.14: neue Engine kann die Medianwerte
  verschieben — keine 1.13.5-CPU-Zahlen unkommentiert auf 1.14 übernehmen;
  Messwerte künftig immer mit OS-Build labeln (AGENTS).
- [ ] Thread-Regressionen im Blick behalten: Snapshot-Stille-Ausfälle
  laut Changelog gefixt; `atom:String`-Parameter-Regression (PR 179, in
  RC2 gefixt — betrifft uns nicht, GS76 hat keine String-Ports);
  xruns-Verhalten beim ersten 1.14-Lauf beobachten und mit den
  1.13.5-Messreihen vergleichen.

- [x] Plugin-level CPU-Matrix am Dwarf (36 Zustände, je voller Neustart):
  Bypass 22 %, None+Colour 28–36 %, Typen 48–56 %, Interaktionen 56–68 %
  (20-Hz-Sinus, OS 2x, COMP OFF, 128 Frames, 0 xruns). **Sym und 00s sind
  die teuersten Profile** — Profilreihung für die Stop-Zweig-Spezialisierung
  belegt (`test-results/cpu-matrix-dwarf`, MESSTECHNIK 1f).
- [x] `transformer_bench` Serie B auf dem Dwarf ausgeführt (2026-10-07,
  Cross-Build GCC 11 statisch, per SSH; Provenanz und Zahlen:
  `test-results/serie-b`, PERFORMANCE Serie B). Vorher/Nachher der
  Doppel-Auswertung bitgleich (Checksummen), Gewinn ~0 %. Offen: Wiederholung
  mit der MPB-Toolchain, falls absolute MPB-komparable Zahlen gebraucht werden.
- [x] Dwarf-Lasttabelle: Provenienz nachträglich dokumentiert (2026-10-08,
  MESSTECHNIK Teil 4): Messdatum 2026-10-05/06, Tool-Stand 2026-10-06,
  Messfenster 15–20 s, 128/256 Frames; **Binary-SHA256 für Serie A nicht
  mehr rekonstruierbar** (SHA-Protokollierung erst ab der CPU-Matrix
  2026-10-07) — Serie A gilt nur noch als Trendreihe; alle folgenden
  Serien tragen Datum/Tool/SHA im Archiv.
- [x] 0.5.1-Bundle mit MPB `moddwarf-new` gebaut und installiert
  (Binary `c936aca6…`, Pin `bb46e86`); CPU-Matrix 36 Zustände am Gerät
  bestätigt (Abschnitt CPU-Reduktion, `cpu-matrix-051-20261008`).
- [ ] ~~0.5.2-Bundle mit MPB `moddwarf-new` neu bauen: dafür zuerst den
  0.5.2-Stand (Kehrwerte, siehe „Ausstehende Verifikationen — 0.5.2")
  committen und den Pin darauf setzen (Arbeitsexemplar-Pin `dbaf48f`
  enthält 0.5.1-DSP + VU-Hub, noch **ohne** 0.5.2); Install-SHA
  verifizieren;~~ *(überholt: 0.5.2 ist committet `b09364e`, als Pin
  gesetzt, mit MPB gebaut und installiert — Geräte-SHA `d94d3121…`,
  2026-10-08; siehe „Ausstehende Verifikationen — 0.5.2".)* **Offen ist
  noch der Rest:** 21/22 sowie 31/37 und 35/38 im Pedalboard hören,
  CPU/xruns prüfen.
- [ ] Reale REAPER-7-Abnahme (Recall/Automation/Host-GR/Fonts) und
  Dwarf-Bedienprüfung (PROJEKT, Abschnitt Übergabe P0/P1).
- [ ] Korrigierte Drag-Handles am Gerät prüfen: MODs globale
  `.mod-drag-handle`-Regel hatte die Fußzeilenplatte auf das gesamte Paneel
  aufgezogen und beim rechten Rand `left:0` vererbt. CSS setzt nun alle Kanten
  der vier Leisten und der Platte explizit zurück; lokaler Test mit den echten
  MOD-Basisregeln PASS. Gerätelauf offen (Cursor, Panel-Move, keine
  Reglerberührung). Dabei auch ENGINE-Ausrichtung (Ratio zu OUTPUT/RELEASE,
  COMP zu Transformer), helles VU-Face bei COMP ON sowie die neue
  VU-Nachpflege (Beschriftung näher am Bogen, Lagerabdeckung am Drehpunkt)
  visuell bestätigen.

## Offen — Klangmodell und Analyse

- [ ] **Verstärkung der Transformatorwirkung** (Hörprobe 2026-10-07: Wirkung
  sehr subtil): Klangziel entschieden — **stärkerer eigener Green-Stripe-
  Charakter**. Detaillierter Arbeitsplan im Abschnitt „Eigenständiger
  Green-Stripe-Charakter" (unten); die Optionenliste in EXTERN bleibt als
  Hintergrund (Option 1 dort ursprünglich mit falscher Ankerrichtung — im
  Sofortblock korrigiert).

- [ ] SPICE-Befund umsetzen: konsistente Übertrager-Netzform klären, neu
  simulieren (QUELLEN, Abschnitt SPICE-Bericht); bisherige Schwellenzahlen
  sind kein freigegebener Fit.
- [ ] de-Paiva-Referenzmodell (Abb. 6(b)/Tabelle 1) als unabhängige
  Offline-Referenz gegen die WDF-Näherung prüfen (QUELLEN).
- [ ] Hammond-140TEX-/560Q-Ziele: Quelle/Last- und Volt-Skalierung festlegen,
  Amplituden-/Phasen-Fit (QUELLEN, Abschnitt Hersteller-Kennlinien).
- [ ] Weitere Jensen-Refits mit neuen Referenzdaten und dokumentierter
  Bankrevision; partialen Fit nicht als Hardwarekalibrierung ausgeben.
- [ ] PluginDoctor-GR (8:1-Schwäche): DSP-Gegenprobe steht aus; die
  Modellinterpretation (Knee/Threshold-Design) ist in
  [EXTERN](EXTERN.md) dokumentiert.
- [ ] Alias-Konvergenz und Hören der ~21,45-kHz-H9-Kandidatenlinie bei hohem
  Colour-only-Drive (EXTERN).
- [ ] **CPWL-Kennlinien-Studie** (Quelle Giampiccolo 2021, Bewertung in
  DSP.md Plan 2a): Offline-Fit kanonisch piecewise-lineare Kennlinien
  (J ∈ {4, 8, 12, 16}) an eigene Kurvenentwürfe und Messreihen, Fehlerziel
  1e-4 gegen die heutigen Profile, A35-Microbench gegen p=3/p=5, dann
  voller Zyklus (Parität/Übergänge/Anker). Kandidat für Punkt 5 unten
  (Mechanismus ersetzt die Tabelle, Klangformungsprojekt, keine
  CPU-Motivation).
- [ ] Rateabhängige Hysterese (Quelle Massi 2023, Preisach-RNN): **kein**
  Laufzeitkandidat (784 ms/Periode auf x86; A35 + Bit-Parität) —
  zurückgestellt; höchstens Offline-Referenzgenerator für einen leichten
  rateabhängigen Term bei ausdrücklichem Klangzielnachweis.
- [ ] Musik-Hörtests: alle 38 Presets auf geeignetem Material; pegelgleiche
  4:1/2:1-Vergleiche (31↔37, 35↔38); Attackkorrektur 21/22 hören
  (EXTERN, Abschnitt Presetbewertung).

## Offen — Eigenständiger Green-Stripe-Charakter (Klangziel 2026-10-07)

**Entscheidung (Benutzer):** das Klangziel ist ein **stärkerer, eigener
Green-Stripe-Charakter** — Jensen/Hammond/de-Paiva und alle Messreihen sind
Leitplanken und Validierungswerkzeuge, kein Hardwareidentitätsziel. Die
Produktvariante (Drive-Regler / dauerhaft heißere Bank / beides) bleibt
zuerst offen: **Offline-Kandidatenvergleich vor jeder Laufzeitänderung.**
Detaillierter Plan (Phasen, Messdatensätze, LUT-Formeln und Laufzeitdetails):
**`DSP.md`, Abschnitt „Klangmodell-Verfeinerung und Kennlinien-LUT — Plan
(2026-10-07)"**; Optionenliste und Hörbefund: `EXTERN.md`.
~~Solange nichts umgesetzt ist, werden `src/`/`jsfx/` nicht berührt — die
Version bleibt 0.4.1; aktueller Stand nach der 2:1-Änderung: 0.4.2.~~
*(Überholt: 0.5.0–0.5.2 sind inzwischen umgesetzt und am Gerät bestätigt
(VU-Meter, Sym-Fastpath, Kehrwerte); der Klangmodellplan selbst ist
weiterhin offen — aktueller Stand **0.5.2**, keine geplanten Kandidaten-
änderungen ohne Offline-Vergleich.)*

### 0. Sofortblock Dokumentation — erledigt in diesem Arbeitsblock

- [x] Ankerrichtung in EXTERN (Option 1) korrigiert: Stärkung heißt
  **negativere** 1-%-Anker (z. B. −20/−14/−8 dBFS); eine Verschiebung auf
  −8/−2/+4 dBFS hätte die Wirkung geschwächt.
- [x] Historische Solver-Stände im CPU-Reduktionsblock aktualisiert
  (Toleranz 1e-6 ist aktiv und bestätigt; Toleranzoption gestrichen,
  Prädiktor zweiter Ordnung neu gefasst).
- [x] MESSERGEBNISSE 6.2: Peak-Spalte liest `process_percent_peak` statt
  `process_percent_max` (nan beseitigt; Generator gefixt, Doku neu erzeugt).
- [x] DSP.md: historische „keine Klangwirkung"-Aussage als überholt markiert.
- [x] EXTERN: „Lösungsfehler ≈ −120 dB" präzisiert (Größenordnung des
  Solver-Residuums, keine globale Fehlergarantie über den Regelkreis).
- [x] PROJEKT.md: Klangzielentscheidung dokumentiert.

### 1. Baseline und Werkzeuge

- [ ] Vergleichsbasis dokumentieren: Bank `gs76-input-2026-10-05-v1` +
  Stand 0.4.1 (Binary `ed05032b…`); Anker-, Geräte-, Render- und
  CPU-Werte als unveränderliche Referenz für alle Kandidaten.
- [ ] Offline-Kandidatenrenderer: Werkzeug, das die Bank offline rendert und
  modifizierte Profile/Drive-Vorstufen **ohne Produktänderung** auswertet
  (Basis `tools/render_lv2.py` + Offline-Bankimport; Ausgabe WAV + JSON).

### 2. Offline-Kandidatenvergleich (keine DSP-Änderung, keine Revision)

- [ ] **A — Drive-Regler (Vorschau):** Feedforward `y = T(g·x)/g`,
  g ∈ {0, +3, +6, +9, +12 dB}; `None` exakt transparent, `Symmetric` linear.
- [ ] **B-Moderate — heißere Bank:** 1-%-Anker −18/−12/−6 dBFS
  (60s/80s/00s), offline Refit aus der bestehenden Fitkette.
- [ ] **B-Bold — noch heißere Bank:** Anker −20/−14/−8 dBFS.
- [ ] **C — Kombination** aus A und B-Moderate/B-Bold.
- [ ] Matrix je Kandidat: 60s/80s/00s × Stufen × Colour 0/50/100 % ×
  OS 2x/4x, COMP OFF; zusätzlich ausgewählte COMP-ON-Fälle.
- [ ] Signale: 20/40/80/160-Hz-Pegelreihen, Zweiton 60 Hz + 1 kHz,
  997-Hz-Sinus, kurze/lange Bassbursts, Kick/Snare/Bass/Gitarre/Stimme/
  Mixbus, ein ungesehener Validierungstitel.
- [ ] Auswertung: Gain/Phase, H2/H3/H5/THD, IMD, Burst-Nachlauf/Remanenz,
  Aliasenergie gegen High-Rate-Referenz; Plots.
- [ ] Pegelgleiche Hördateien mit fester Kleinsignalnormalisierung
  (keine Peak-/LUFS-Normalisierung je Render); blind gereichte Reihenfolge.
- [ ] Profilidentität gegenprüfen: 60s früh/weich/dicht (deutlich warm),
  80s straff/punchig mit weniger Tiefbassverlust, 00s offen, bei Drive
  verdichtend; Sym bleibt lineare Referenz.

### 3. Entscheidung

- [ ] Benutzerentscheidung A / B / C auf Grundlage der Hördateien und Plots.

### 4. Produktumsetzung (vollständiger Zyklus; `src/`+`jsfx/` = Revision +1)

- [ ] **A:** neuer angehängter Port `transformer_drive` 0…12 dB, Default 0,
  angehängt nach `transformer` (LV2-Index-Erwartung 17 Stereo / 14 Mono,
  JSFX slider14 — vor Umsetzung im generierten TTL verifizieren); über
  `data/parameters.json` + `generate.py` (Port-Dreieck LV2/JSFX/RPL),
  GUI-/Preset-/Automationserweiterung, Presets tragen Drive 0; Minor-Bump
  **0.5.0**.
- [ ] **B:** `data/transformers.json` Refit mit neuen Ankern, neue
  Bankrevision (z. B. `gs76-input-…-v2`); Geräte-/Renderanker komplett
  erneuern (Transformator-Matrix, 20-Hz-Pegelreihe, Bursts); bestehende
  Projektklänge mit aktivem Transformator ändern sich — Übergang in
  PROJEKT dokumentieren.
- [ ] **C:** Reihenfolge Bank vor Port (oder umgekehrt je Hörbefund), beide
  Zyklen getrennt dokumentiert.
- [ ] Gates je Umsetzung: make test, Parität 430+76 gegen neue Bit-Basis,
  Übergangstests, `cpu_regression` Vorher/Nachher, None-Recall,
  Blockinvarianz, REAPER-Vollmatrix, Dwarf-Transformator-Matrix,
  Dwarf-CPU-Matrix, pegelgleicher Musikvergleich.

### 5. Transformer-law()-LUT (nur falls die gewünschte Kurvenform analytisch nicht erreichbar ist)

**Mechanismus-Update 2026-10-08:** als Fitmechanik ist **CPWL
(Giampiccolo 2021) der Tabelle vorzuziehen** — explizit, stückweise
konstante Steigung, tabellenfrei; Bewertung und Verträge: `DSP.md`,
Plan-Abschnitt 2a. Die folgenden Punkte gelten sinngemäß für beide
Mechanismen (Wertequelle, Fitvertrag, Microbench).

Nur sinnvoll, wenn eine gemessene oder neu gefittete Magnetisierungskurve
die heutigen Potenz-/Fröhlich-Familien ersetzen soll. Tabelliert wird

$$f(u), \qquad u=\frac{|\lambda|}{\lambda_\text{scale}},$$

mit

$$i(\lambda)=\operatorname{sgn}(\lambda)\,
\frac{\lambda_\text{scale}}{L_m}f(u),
\qquad
\frac{di}{d\lambda}=\frac{f'(u)}{L_m}.$$

- [ ] Normative Quelle `data/transformer_luts.json`; Generator erzeugt
  `src/dsp/TransformerLawLut.hpp` und
  `jsfx/GreenStripe76-TransformerLawLut.jsfx-inc` (EEL2 über `gs_alloc`,
  keine globalen Arrays).
- [ ] Nur drei nichtlineare Profile; `Symmetric` analytisch direkt lösen.
- [ ] Odd-Symmetrie exakt per Betrag/Vorzeichen (eine positive Tabelle).
- [ ] Werte **und konsistente Steigung** bereitstellen; monotone
  Hermite-Interpolation oder lineare Interpolation mit exakt daraus
  abgeleiteter Steigung (Newton-Nenner konsistent); keine kubischen
  Überschwinger.
- [ ] Dichter Bereich um das Knie: 257 Knoten × 3 Profile ×
  (Wert, Steigung) ≈ 12 KiB; Stückelung 33/161/65 für
  u = 0–0,5 / 0,5–1,2 / 1,2–u_max.
- [ ] Tabellenbereich erst aus realen Trajektorien und Extremtests
  bestimmen; außerhalb **niemals klemmen** — analytischer Fallback oder
  C¹-passende Hochfeldfortsetzung; Extremtests bis ±256 FS.
- [ ] Stop-/Hysteresezustände bleiben separat analytisch — sie sind nicht
  statisch tabellierbar.
- [ ] A35-Microbench **vor** Übernahme: die analytischen p=3/p=5-Kerne sind
  sehr billig; ein Cachezugriff kann langsamer sein (softClip-Lektion).

### 6. Kompressor-Gain-Law-LUT (eigene spätere Phase)

**Tabelle je diskretem Ratio-Modus:**

```text
Achse:    over_db = detector_db - threshold_db
Bereich:  etwa -12 … +48 dB
Schritt:  0,25 dB
Tabellen: 2:1, 4:1, 8:1, 12:1, 20:1, All
Wert:     gewünschte Feedback-Abschwächung in dB
```

Das ergibt etwa 241 × 6 double-Werte, rund **12 KiB**. Laufzeit:

```text
index      = floor((over_db - min_db) * inv_step)
fraction   = (over_db - min_db) * inv_step - index
desired_db = y[index] + fraction * (y[index+1] - y[index])
slope      = (y[index+1] - y[index]) * inv_step
```

Die Intervallsteigung ersetzt im impliziten Solver den heutigen Ausdruck
aus Ratio und `kneeSlope()` — Newton-Schritt und LUT bleiben so
mathematisch konsistent.

- [ ] Offline-Fit gegen den **geschlossenen Feedback-Regelkreis**, nicht
  direkt gegen eine Input→Output-Kurve.
- [ ] Unter dem unteren Tabellenende exakt 0 dB GR; oberhalb linear
  fortsetzen und bei 60 dB begrenzen.
- [ ] Keine Interpolation zwischen Ratio-Tasten; All Buttons erhält eine
  eigene Tabelle (Plateau/Slam); 2:1 bleibt eigene Green-Stripe-Erweiterung.
- [ ] Monotone lineare Interpolation, keine kubischen Überschwinger.
- [ ] Werte aus einer normativen JSON-Datei generieren (`tools/generate.py`);
  C++ als konstante Arrays; EEL2 über reservierten `gs_alloc`-Speicher,
  nicht über riskante globale Arrays; dieselbe Index- und
  Interpolationsreihenfolge in beiden Engines.
- [ ] Motiv ist hier die Klangformung (gemessene Kennlinie), nicht CPU.

### 7. Dynamikverfeinerung (nach der Kennlinienphase)

- [ ] Release mit zwei gekoppelten Zeitanteilen; Gewichtung nach GR-Tiefe
  und Vorbelastungsdauer; maximal 2 zusätzliche Zustände ohne
  Identifikationsnachweis.
- [ ] Attack-Burstdaten zuerst auswerten (Protokoll MESSTECHNIK 7);
  All-Buttons-Zeitverhalten separat prüfen.

### Ausdrücklich nicht verfolgen

`fet()`-LUT (264,8 MiB, verworfen), `softClip()`-LUT (langsamer als die
Padé-Form), Colour×Transformer-Kopplung (zerlegt validierte Pfade),
verdeckte Auto-Makeup-/Limiterfunktionen.

## Offen — CPU-Reduktion Transformator (Skizze, nach Risiko sortiert)

~~Grundlage: PERFORMANCE 5c (x86) — nicht die Iterationszahl ist der Hebel
(2,0–2,6 je Probe, 0 % am 40er-Limit), sondern die **14 Stop-Zweige je
Auswertung**; OS multipliziert (4× ≈ ×4).~~
*(Widerlegt 2026-10-07: die Stop-Zweig-Spezialisierung bringt nur 1–2 % —
die Zweige 12/13 klemmen nie; die Iterationszahl ist über die Toleranz doch
ein Hebel — 1e-6 umgesetzt, −10–12 % bei 00s/Sym.)*
**A35-Bestätigung (2026-10-07, CPU-Matrix, MESSTECHNIK 1f):** die
Profilreihung am Gerät ist Sym ≈ 00s > 80s ≈ 60s (66/63/57/57 % Median bei
20 Hz-Volldreher, +20–28 Punkte über None) — der „lineare" Sym ist am
teuersten, die Stop-Zweig-Struktur dominiert die *Kostenverteilung*, nicht
die *Reduktionshebel*. Entscheidungsbasis: Serie B (gemessen) und die
Toleranz-Messung (PERFORMANCE).

**Neu 2026-10-07 (nach der 1e-6-CPU-Matrix und MPB-Build-Log; ausführliche
Vorschläge):** Ausgangslage nach den erneuerten Messungen — 00s/Sym sind
durch die Toleranz bereits gefallen (56–60 % Median), 60s/80s bleiben
strukturell bei ~2 Iterationen, und der MPB-Buildlog zeigt, dass die schon
gemessene `-mcpu=cortex-a35`-Empfehlung **noch nicht** in der Rezeptur
ankam (`CXXFLAGS … -O3 -O3` ohne `-mcpu`). Alle neuen Kandidaten werden
zuerst **isoliert am A35 gemessen**; der volle Zyklus (Parität/REAPER/
Gerät) läuft nur für Kandidaten mit **≥ 3 % Transformerblock oder ≥ 2
Plugin-Prozentpunkten** (Lektion Doppel-Auswertung: erst messen, dann
umbauen). Alles ride-along mit dem nächsten MPB-Build, der ohnehin die
~~0.4.2-Kennlinie (2:1)~~ *(überholt: seit 0.5.2 umgesetzt und am Gerät
installiert)* aktuelle Kennlinie tragen muss.

**1. MPB-Build tatsächlich auf Cortex-A35 optimieren** (gemessen −1,2 bis
−3,6 % je Profil, PERFORMANCE „Build-Tuning"):

- [x] `$(TARGET_CXXFLAGS)` in der MPB-Rezeptur bei Build und Install um
  `-mcpu=cortex-a35` ergänzt; die projektseitigen Flags bleiben angehängt
  (2026-10-08).
- [x] Bit-Identität gegen denselben A35-Crosscompiler ohne `-mcpu` über die
  Bench-Checksummen nachgewiesen (`-ffp-contract=off`, kein Fast-Math; frühere
  Build-Tuning-Serie). Offizieller MPB-Neubau/Installhash bleibt Teil der
  Geräte-Stichprobe.
- [x] Stichprobe am Gerät: **volle 36-Zustände-Matrix statt Stichprobe**
  (2026-10-08, `test-results/cpu-matrix-051-20261008`): −mcpu-Effekt am
  plugin level nicht von der 1–2-Punkte-Granularität trennbar
  (60s/80s Δ 0,0, 00s −0,5, None +1,0, Bypass 0) — konsistent mit der
  Cross-Bench-Erwartung −1…−4 % s/s.

**2. `Symmetric`-/No-Hysteresis-Fastpath** (größter bitidentischer Hebel):
Sym hat `hysteresis_enabled=0` und `saturation_strength=0`, zahlt aber
weiterhin 14 Stop-Trials, 14 Clamps, 14 Ableitungsbedingungen, 14
Zustands-Commits plus den u²-Loop in `law()`, der numerisch nach 0
kollabiert.

- [x] `hysteresis_enabled==0` ⇒ komplette Stop-Bank überspringen
  (Auswertung **und** Commit); Stop-Zustände für Sym nicht fortführen
  (Modellwechsel resettet den Core ohnehin). C++ und EEL2 umgesetzt 2026-10-08.
- [x] Zusätzlich `saturation_strength==0` ⇒ direkt `i=λ/Lm`,
  `di/dλ=1/Lm` statt Loop-mal-Null.
- [x] Lokale Bit-Identität nachgewiesen: Diagnoseausgabe vor/nach über 60 Fälle
  und 90 000 Samples bytegleich; `make test` und Parität 430+76, max 0 FS.
  Abgedeckt sind Modellwechsel und OS off/2x/4x; `transformer_tests` deckt
  ±0/Extremreizen bis ±256 FS ab. Der 40-Iterations-Cap wurde nicht erreicht
  (0 % in den Messläufen). A35-Checksummen folgen mit dem MPB-Lauf.
- [x] EEL2 `gs_xf_core` spiegelt beide Zweige; Paritätssatz komplett.
- [x] Gerätebestätigung: **volle CPU-Matrix (36 Zustände) mit 0.5.1**
  (2026-10-08, `test-results/cpu-matrix-051-20261008`): Sym **−10…−16
  Punkte** (c0 52→36, ×Colour 56–60 → 46), 60s/80s/00s/None/Bypass
  unverändert, Spitzen unverändert, 0 xruns. Lokaler x86-Bench:
  Symmetric 0,04870 → 0,03956 s/s (−18,8 % gesamt; Mehrkosten gegen None
  etwa −56 %). Isolierte A35-Bench-Wiederholung für den Fastpath entbehrlich.

**3. Profil-spezialisierte Kennlinien** (klein bis mittel, 60s/80s):

- [ ] p=3/p=5 explizit ausrollen (u², u⁴ sequenziell) mit **exakt
  erhaltener Multiplikationsreihenfolge** des bestehenden Loops (Parität!);
  00s (Fröhlich/Hochfeld) unverändert, Sym linear (siehe 2).
- [ ] Zweigentscheidung je Koeffizientensatz (`prepare()`), nicht pro Sample
  neu; keinen indirekten Funktionszeiger einführen, bevor dessen Kosten
  gemessen sind.
- [ ] A35-Microbench vor Übernahme; nur bei echtem Gewinn umsetzen.

**4. Invariante Größen vorberechnen:**

- [x] `1/lm_h`, `1/relax_l_h`, `1/((1+relaxation)·relax_l_h)` und die
  00s-Hochfeldkonstanten (Knie, Zielsteigung, Breite) in
  `TransformerCoefficients::prepare()` vorrechnen; EEL2 identisch bei der
  Koeffizientenwahl. **Umgesetzt 2026-10-08 (0.5.2)**: zusätzlich
  `1/denominator`; die pro-Iteration-Divisionen durch lm_h/relax_l_h/
  denominator sind Kehrwert-Multiplikationen (Rundung ~1 ULP je Division),
  die 00s-Hochfeldkonstanten sind reine bitidentische Hoists; EEL2-Zellen
  46–54, Stride 48→56.
- [x] Die Frage „hoistet GCC schon?" ist empirisch beantwortet: unter
  strengem FP (`-ffp-contract=off`, kein Fast-Math) wandelt GCC
  `x/c` nicht in `x*(1/c)` — der gepaarte x86-Bench misst **−12,4 %
  (60s) / −13,2 % (80s) / −11,7 % (00s) / −18,5 % (Sym)** am
  Transformatorblock (gegen None derselben Messung korrigiert,
  PERFORMANCE).make test + Parität 430+76 (max 0 FS) PASS; Anker auf
  Druckgenauigkeit unverändert.

**5. Quellenbewusster Startwert-Prädiktor** (aussichtsreichster
60s/80s-Hebel, mittleres Numerikrisiko; konkretisiert den offenen Punkt
„Prädiktor zweiter Ordnung" unten):

- [ ] Letzten `source` und letzten Jacobian-Kehrwert je Kanal speichern;
  Startwert um die bekannte Quelländerung korrigieren
  (Δλ ≈ h·Δsource/denominator · J⁻¹_vorher); **keine** zusätzliche
  `law()`-Auswertung vor dem Solver — sonst wird nur Arbeit verschoben.
- [ ] Solver bleibt unveränderter Fallback; Toleranz bleibt 1e-6.
- [ ] Prüfmatrix: 20 Hz/997 Hz, Input −48…+48 dB bis zum Clamp ±256 FS,
  OS off/2x/4x, Bursts kurz/lang, Stille, Polaritätswechsel, schnelle
  Modellwechsel; Parität 430+76 gegen die neue Bit-Basis.
- [ ] Ziel: 60s/80s öfter nach der ersten Auswertung konvergent — CPU am
  A35 messen, nicht nur den Iterationszähler.

**6. Ausgabebezogene Konvergenzdiagnose statt blinder Toleranz:**

- [ ] Offline messen, wie ein Flux-Residual in Ausgangsfehler übersetzt
  (Δy, H2/H3/H5, Folgesamplefehler) — je Profil.
- [ ] Erst dann prüfen, ob eine **ausgangsbezogene** Toleranz besser ist
  als das einheitliche `1e-6·(1+|x|)`; immer gegen 1e-10-Referenzrender
  und mit Hörprobe. Kein pauschales 1e-5.

**7. NEON über die Stop-Bank statt über L/R:**

- [ ] Die 14 Stop-Operatoren **eines Kanals** als 7 `float64x2_t`-Paare
  (trial, clamp, |·|, Zustandsupdate vektorisiert); die gewichtete Summe
  lane-weise in ursprünglicher Reihenfolge addieren — **keine** horizontale
  Reduction (Parität).
- [ ] Skalarer Fallback für x86/Nicht-NEON; Mono und Stereo profitieren;
  keine L/R-Lockstep-Probleme (die Konvergenz divergiert je Kanal).
- [ ] A35-Microbench zuerst; danach voller Paritätssatz.
- [ ] Die alte L/R-NEON-Idee (unten) bleibt wegen des Maskierungsrisikos
  zurückgestellt; diese Variante ersetzt sie als bevorzugter Weg.
  *(Vertieft 2026-10-08: siehe Abschnitt „NEON 2×fp64 — Vertiefung" — dort
  steht die L/R-Maskierung im Detail und die gegenseitige Ausschließlichkeit
  beider Lanes-Achsen; die Vorzugsentscheidung bleibt beim Bench.)*

**8. Zustands-Commit der Stop-Bank A/B-messen:**

- [ ] Heute läuft nach Konvergenz die 14er-Schleife erneut (Commit).
  Kandidat: Kandidatenwerte in `current()` cachen und bei Konvergenz
  kopieren.
- [ ] MPB-Assemblat auf Registerdruck/Stack-Spills prüfen — 14 temporäre
  Doubles können den Gewinn umkehren; nur bei eindeutigem A35-Gewinn und
  Bit-Identität übernehmen.

**9. Reduzierte Stop-Bank (14→10→8→6) nur als Modelländerung:**

- [ ] Separate Offline-Studie; fitten gegen volle aktuelle
  Modelltrajektorien, Bassbursts, Polaritätswechsel, Vorbelastung/
  Wiederanlauf und (sobald vorhanden) Minor-Loop-Daten — nicht gegen
  wenige Sinustöne.
- [ ] H2/H3/H5, Rohsignal, Restzustände und Ausklingen vergleichen; nur
  weiterverfolgen, wenn der Klangmodellauftrag (Eigenständiger
  Green-Stripe-Charakter) die Abweichung erlaubt; voller Zyklus,
  Geräteanker, Hörprüfung, neue Bankrevision.
- [ ] Einordnung im Klangmodellplan: nach dem Offline-Kandidatenvergleich,
  nicht davor.

**Neue Reihenfolge (Stand 2026-10-08, gemessene Abarbeitung):**
1) `-mcpu=cortex-a35` in der MPB-Rezeptur — **erledigt, am Gerät bestätigt**
(CPU-Matrix 051: Typen/None unverändert, Effekt unter Granularität),
2) Sym-/No-Hysteresis-Fastpath — **erledigt, am Gerät bestätigt** (−10…−16
Punkte), 3) Invarianten — **erledigt lokal** (0.5.2, −12–13 % Block);
p-Spezialisierung offen, 4) quellenbewusster Prädiktor — offen (60s/80s
strukturell bei ~2 Iterationen), 5) Stop-Bank-NEON, 6) Commit-A/B, 7)
reduzierte Stop-Bank nur als bewusste Modelländerung. Weiterhin
zurückgestellt: OS-Entkopplung (Benutzer will oversampled), Host-Rate,
adaptives OS, float statt double, `-ffast-math`, Auto-Deaktivierung bei
Compression Off, `softClip()`/`fet()`-LUT, `law()`-LUT aus CPU-Gründen.

Paritätsneutral (bit-identisch machbar):

- [x] Finale Doppel-Auswertung in `Transformer.hpp`/`current()` einsparen:
  **umgesetzt** (C++ und EEL2 gemeinsam); Bit-Identität über
  Checksummen-A/B mit identischem Compiler auf x86 und A35 belegt
  (`test-results/serie-b/`). **Ergebnis: ~0 % auf dem A35** — der Compiler
  hatte die Redundanz bei −O3 vermutlich bereits eliminiert; die
  TODO-Erwartung „25–30 %“ war zu optimistisch. Änderung bleibt (Code
  explizit, Nachweis beigelegt).
- [x] Build-Tuning für den MPB-Build prüfen: **gemessen** (Cross-Bench,
  997 Hz): `-mcpu=cortex-a35` bringt −1,2 bis −3,6 % je Profil, LTO keinen
  messbaren Zusatznutzen. Empfehlung: `-mcpu=cortex-a35` in die
  MPB-Rezeptur aufnehmen (CXXFLAGS-Append im `.mk`); Bit-Identität über
  die Bench-Checksummen je Variante prüfen.
- [ ] NEON 2-Lane für Stereo in `src/dsp/Transformer.hpp`: L/R-Zustände sind
  vertragsgemäß getrennt; 2×double mit identischer Operationsreihenfolge je
  Lane und ohne horizontale Ops bleibt bit-identisch (max 0 FS hält), EEL2
  bleibt skalar. Erwartung ~2× auf den Transformerblock für Stereo-Instanzen,
  Mono ohne Gewinn; Paritätssatz trotzdem komplett laufen lassen.
  **Risiko (Serie B):** der Solver verzweigt datenabhängig (Konvergenz je
  Kanal) — Lockstep braucht Maskierung von x/hi/lo und den Zustands-Commit;
  deshalb erst nach der Stop-Zweig-Frage entscheiden.
  *(Vertieft 2026-10-08: siehe Abschnitt „NEON 2×fp64 — Vertiefung" — die
  seriesExp-Befürchtung entfällt, die Maskierung ist im Detail durchgearbeitet;
  Kostenmodell max(L,R) gegen L+R entscheidet am Bench.)*

Vertragsfragen OS-Entkopplung (2026-10-07 diskutiert, **zurückgestellt**):
der Transformator soll laut Benutzer **oversampled bleiben** — die
Host-Rate-Option würde das Sättigungs-Oversampling abschalten und ist damit
klanglich fraglich. Falls später als explizit gekennzeichnete „Eco"-Option
wieder aufgenommen: (a) neuer angehängter Port `transformer_rate`
{OS folgen, Host-Rate}, Index 17/14, Default „OS folgen" (Recall-neutral),
Minor-Bump 0.5.0; (b) gemessene Alias-Grenze statt Schwelle raten
(Zweitton-/10-kHz-Anregung bei −2 dBFS, Host-Rate vs OS 2x); (c) volle Kette
(generate.py, Übergangstests, Parität, CPU-Nachweis). Priorität liegt auf
Konvergenz-Toleranz/Startwert (Vorschlag 3) und Stop-Zweig-Spezialisierung.

Mit vollem Paritätspreis (C++/EEL2 gemeinsam, `generate.py`, 430+76 Fälle
gegen neue Bit-Basis, `cpu_regression` Vorher/Nachher, Übergangstests,
Gerätevergleich):

- [x] Stop-Zweig-Reachability gemessen (2026-10-07, Diagnosezähler je Zweig,
  Extremreizen bis zum Input-Clamp ±256 FS, 20 Hz/997 Hz, alle Profile):
  **60s/80s/00s klemmen max. Zweige 0–11 — 12/13 klemmen nie**; Sym (linear)
  klemmt bei 20 Hz alle 14. Das Potenzial der Spezialisierung ist damit nur
  **2 von 14 Zweigen ≈ 1–2 % Gesamt-CPU** — die TODO-Schätzung 30–50 % war
  zu optimistisch (die kleinen Schwellen haben die großen Gewichte und
  klemmen ständig). Rohdaten: `test-results/serie-b` (bench_stats).
  Umsetzung nur noch gemeinsam mit dem Startwert-Prädikator lohnend.
- [x] Startwert-Prädikator + Konvergenz-Toleranz 1e-14 → 1e-10: **umgesetzt**
  (C++ und EEL2; Prädikator = Spannungsschritt + gemessener letzter
  Flux-Inkrement, px2-Zustand). Gemessen am A35: Iterationen 2,55 → 2,01 in
  den harten Fällen (60s/997 Hz), sonst 2,00–2,07; CPU −0,5 bis −1,5 %.
  make test + Parität (430+76, max 0 FS) PASS; 1-%-Anker unverändert.
  **Strukturbefund:** die Iterationszahl ist durch die quadratische
  Konvergenz bei 2 strukturell gebunden (der Startfehler müsste ≤ 1e-10
  liegen, die Quellstufe ist a-priori unbekannt). ~~Option für 1 Iteration:
  Toleranz 1e-6 (Lösungsfehler ≈ −120 dB, hörbar unsicher) — Qualitäts-
  entscheidung, nicht umgesetzt. Checksummen/Baselines verschieben sich
  (Rundung) — Render- und Gerätevergleiche erneuern.~~ *(Überholt
  2026-10-07: die Toleranz 1e-6 ist umgesetzt (`fc1f083`), per Hörprobe
  bestätigt, 28 REAPER-Render bitgleich und die Geräte-CPU-Matrix erneuert
  — siehe „Ausstehende Verifikationen" sowie MESSERGEBNISSE 6.3/7.)*
- [ ] Startwert-/Steigungsverbesserung (Prädiktor zweiter Ordnung);
  ~~gelockerte Konvergenztoleranz (aktuell 1e-14 relativ)~~ **die 1e-6-
  Toleranz ist aktiv** — verbleibender Hebel nur noch für 60s/80s, die
  strukturell bei ~2 Iterationen liegen (PERFORMANCE, Abschnitt Toleranz
  1e-6).

Vertragliche Hebel (nur mit Gerätedaten und begründeter Modelländerung):

- [ ] OS-Entkopplung „Transformator rechnet in Host-Rate" als explizite
  Option: größter Hebel, aber Modelländerung (Aliasing der Sättigung), neuer
  Port = Versionierung, Übergangstests; nur wenn Serie B genau das als
  Engpass zeigt.
- [x] Kennlinien-LUT für `law()` als CPU-Hebel: **2026-10-08 analysiert und
  abgelehnt** — das heutige `law()` nutzt kein `pow` mehr (p=3/p=5
  sequentielle Multiplikationen, 00s Fröhlich closed-form); der einzige
  LUT-fähige Anteil (Divisionen) ist seit 0.5.2 durch die invarianten
  Kehrwerte abgedeckt; die dominante 14er-Stop-Bank bleibt
  zustandsabhängig und tabellenuntauglich. softClip-Lektion bleibt
  gültig (LUT kann langsamer sein als analytisch, 9,7 vs 1,87 ns auf
  x86; A35-Cache schlechter). Eine law()-LUT bleibt nur noch als
  Klangformungs-Projekt relevant (Abschnitt „Eigenständiger
  Green-Stripe-Charakter", Punkt 5), nicht für CPU.

Nicht wirkksam (dokumentiert, nicht verfolgen): Iterationslimit senken
(0 % am Cap); kanalübergreifende Zustandsnutzung (Vertrag);
Auto-Deaktivierung bei Compression Off (bewusst nicht vorgesehen).

~~Vorgeschlagene Reihenfolge (aktualisiert nach Serie B + Build-Tuning):
Build-Tuning (`-mcpu=cortex-a35` in die MPB-Rezeptur, −1,2 bis −3,6 %,
jetzt umsetzbar) → Stop-Zweig-Spezialisierung (30–50 % des Blocks)
gemessen 1–2 % (12/13 Zweige klemmen nie — nur mit dem
Startwert-Prädikator zusammen sinnvoll) → NEON (Maskierungsrisiko, erst
danach bewerten) → OS-Entkopplung (Vertragsfrage, zurückgestellt —
Transformator bleibt oversampled). Doppel-Auswertung verfeuert (~0 %),
Toleranz 1e-6 umgesetzt (−10–12 % bei 00s/Sym).~~
*(Abgelöst 2026-10-08 durch die „Neue Reihenfolge" oben mit
Abarbeitungsstand: `-mcpu` erledigt, Sym-Fastpath erledigt, Kehrwerte
erledigt (0.5.2); verbleibend p-Spezialisierung, Prädiktor (60s/80s
strukturell bei ~2 Iterationen), NEON, Commit-A/B, reduzierte Stop-Bank.)*

## Offen — CPU-Reduktion Colour-Pfad (2026-10-08, nach Hebel sortiert)

**Datenlage:** der Colour-Block kostet am Gerät ca. **+10 Prozentpunkte**
(0.5.1-CPU-Matrix: Sym×Colour 46 gegen Sym c0 36 Median; `test-results/
cpu-matrix-051-20261008`). Der überwiegende Teil davon ist Klangsubstanz
(3× `softClip`, `fet()`-Wurzel im Detector); die strukturellen Hebel sind
deshalb klein — hier gilt die Transformator-Lektion besonders: **erst
isoliert messen, dann umbauen** (Schwelle für den Vollzyklus: ≥ 2
Plugin-Prozentpunkte; EEL2 immer gepaart).

**Kandidat 1 — Tote Zustandsfilter bei Colour 0 parken** (sauberster Hebel,
Gewinner sind die c0-Zustände):

- [ ] Befund: bei `colour == 0.0` laufen aktuell **5 One-Pole-Filter pro
  Kanal ins Leere** — `inDC`/`inFlux` in `Channel::input()` und
  `preLP`/`outFlux`/`outDC` in `Channel::output()`
  (src/dsp/GreenStripe.hpp, Channel-Struct ~:255-286; EEL2
  `gs_ch_input`/`gs_ch_output`, GreenStripe76-Core.jsfx-inc ~:108-121).
  Alle fünf werden je Sample aktualisiert, aber nur vom Colour-Pfad
  gelesen (`hp`/`iron` bzw. `preLP`-Mischung, `outDC`-Abzug).
- [ ] Umsetzung nach dem 0.1.1-Parkmuster (`parked_`-Flag für Controller,
  „nur aktive Controller rechnen"): Colour-Zustand parken, wenn
  `running_.colour == 0.0` exakt; parken = Filterzustände `reset()` und
  Updates überspringen. Aufwachen verhält sich wie der Initial-Pfad —
  die Crossfades `x + colour·(iron−x)` starten bei ≈ 0 und walken ein,
  ohne Klick.
- [ ] Grundlage ist garantiert: `approach()` snappt exakt auf das Ziel
  (`≤ 1e-12·max(1,|goal|)`, GreenStripe.hpp ~:556) — `colour == 0.0`
  feuert also real im stationären Zustand, nicht nur als Absicherung.
- [ ] **Übergangstests Pflicht** (Reglerwechsel): Colour 0→100→0 und
  0→5→0 mit Smoothing, Klickfreiheit und Zustandsvergleich gegen den
  heutigen Stand (der heutige Code hält die Filter „warm" — der neue
  startet beim Aufwachen frisch; das muss als bewusste Verhaltensänderung
  dokumentiert und dem hörtest unterzogen werden, nicht still).
- [ ] EEL2-Seite identisch (`gs_ch_input`/`gs_ch_output` um die
  Colour-Verzweigung herum umstellen); Paritätssatz komplett; Geräte-
  Messung c0-Zustände (None/Bypass + alle ×Bank-c0) vor/nach.
- [ ] Erwartung: klein (5 One-Poles ≈ 1–2 % Plugin) — deshalb Bench
  zuerst, nur bei ≥ 2 Punkten in den Vollzyklus.

**Kandidat 2 — `fet()`-Snap für kleine Krümmung** (Detector-Tap, nur wenn
Kandidat 1 nichts bringt):

- [ ] Befund: `fet()` zahlt pro Tap sqrt+div sobald
  `curvature = colour·(0.24+0.08·all) > 0` — auch bei Colour 5 %
  (curvature 0,012) und für 1–2 Taps je Sample (bei All 100 % entfällt
  das bereits). Ein Snap „curvature < ε ⇒ linearer Zweig" (Vorbild: der
  0.5.1-Fastpath `saturation_strength==0 ⇒ i=λ/Lm`) würde das verbilligen.
- [ ] **Vertragspreis:** das ist eine numerische Einrastschwelle — laut
  AGENTS nur mit Vorher-/Nachher- und Übergangstests; die Bit-Parität zu
  früheren Device-Renders bricht im Bereich 0 < curvature < ε (hörsch
  irrelevant, aber dokumentationspflichtig); EEL2 gepaart, Paritätssatz
  gegen die neue Bit-Basis.
- [ ] ε nur aus der Messung ableiten (größter curvature-Wert, dessen
  Ergebnisabweichung unter der Messflur bleibt), nicht raten.
- [ ] Erwartung: 1–2 % Plugin; nur verfolgen, wenn Kandidat 1 unter der
  Schwelle bleibt und der Bench den Tap-Anteil isoliert bestätigt.

**Kandidat 3 — NEON 2-Lane für die kanalentkoppelten Colour-Filter**
(backlog; ausführliche Begründung im Abschnitt „NEON 2×fp64 — Vertiefung"
unten):

- [ ] `Channel::input()`/`output()` sind kanalentkoppelt (Link betrifft
  nur den Detector) und **datenunabhängig verzweigungsfrei** — anders als
  der Solver braucht es hier keine Konvergenz-Maskierung; 2×double-Lanes
  (vmul/vadd, **kein** vfma) mit identischer Operationsreihenfolge je Lane
  sind paritätsneutral machbar. Der Detector (Taps, Link-Summierung)
  bleibt skalar.
- [ ] A35-NEON ist 128-bit (2×fp64 je Op) — Gewinn begrenzt; nur
  verfolgen, wenn der isolierte Bench zeigt, dass die Filter-/softClip-
  Anteile ≥ 3–4 Punkte tragen, und nach den Transformator-NEON-Kandidaten
  (gleiche Intrinsics-Grundarbeit, doppelter Nutzen dort).

**Zurückgestellt / tabu (bewusst, nicht vergessen):**
- `colour == 1.0`-Sonderweg (Crossfade überspringen): spart ~8 FLOPs,
  bricht aber die Bitidentität (`x + 1.0·(iron−x) ≠ iron` in FP-Rundung)
  gegen alle bisherigen Renders — Vertrag nicht antasten.
- `softClip()`/`fet()`-Mathematik selbst und LUT-Varianten: ist Klang
  bzw. stehen schon aus CPU-Gründen auf der Rückstellliste (siehe
  Reihenfolge-Liste im Transformator-Abschnitt).
- Die immerlaufenden Filter sind bei Colour > 0 alle benötigt — dort ist
  außer 2/3 nichts strukturell einsparbar, ohne den Klang zu ändern.

**Protokoll für alle Kandidaten:** isolierter x86-Bench des Colour-Blocks
zuerst (analog `transformer_bench`, Überschneidung mit dem geplanten
Standalone-Transformator-Plugin beim Bench-Aufbau beachten); Kandidaten
nur bei ≥ 2 Plugin-Prozentpunkten in den Vollzyklus (C++/EEL2 gepaart,
`generate.py`, `make test` + Parität, Übergangstests, Geräte-Matrix
c0 gegen ×Colour); jedes Mal Revisionsbump prüfen (src/Änderung).

## NEON 2×fp64 — Vertiefung (2026-10-08)

Aarch64-NEON ist 128-bit breit = **genau 2 fp64-Lanes**. Damit gibt es
genau zwei mögliche Lanes-Achsen, und sie schließen sich gegenseitig aus
(eine Funktion kann nicht gleichzeitig über Operatoren und über Kanäle
parallelisiert werden):

- **Achse „Operatoren"** (Kandidat 7 oben): die 14 Stop-Operatoren *eines
  Kanals* als 7 Paare. Geradliniger Code, keine Maskierung nötig — aber
  der Gewinn ist auf den Stop-Bank-Anteil begrenzt (die Bank ist ein
  Bruchteil der Iterationsarbeit; `law()` und die Newton-Arithmetik
  bleiben skalar).
- **Achse „Kanäle"** (L/R-2-Lane): die *gesamte* per-Sample-Arbeit beider
  Kanäle in einem Registerpaar: Potenzial bis ~2× auf dem jeweiligen Block
  für Stereo-Instanzen; braucht Maskierung überall dort, wo der Code
  datenabhängig verzweigt.

**Grundregel Parität (alle Varianten):** nur IEEE-exakte Ops
(vadd/vsub/vmul/vdiv/vsqrt — fsqrt ist korrekt gerundet), **kein vfma**
(Kontraktion! auch `-ffp-contract=off` deckt Intrinsics nicht ab, weil die
Kontraktion im Intrinsics-Aufruf explizit passiert), Verzweigungen werden
zu Selects (`bsl`/`vbsl` oder compare+select), **keine horizontale
Reduction** in wertbestimmten Summen (Reihenfolge!), EEL2 bleibt skalar und
ist der Paritätsrichter (430+76 Fälle, max 0 FS). Selects sind
bit-sicher: die nicht gewählte Lane produziert zwar Werte, aber nur die
gewählten Bits überleben — solange die nicht gewählte Berechnung selbst
keine Ausnahme erzeugt (fp kann das nicht außer Traps, die aus sind).

**Ort 1 — Colour-Pfad (`Channel::input()`/`output()`), der einfache Fall:**

- Struktur: 5 One-Pole-Filter + 3 `softClip` + Crossfades — **verzweigungs-
 frei bis auf uniforme Schwellen** (`colour == 0.0` ist ein
  Parameterzustand, keine Datenverzweigung — beide Lanes treffen sie
  gleich). `softClip`-Kanten (|x| ≥ 5) sind Datenzweige, aber sauber als
  Select abbildbar: Polynom für beide Lanes rechnen, Ergebnis per
  Vergleichsmaske wählen (das Polynom bleibt auch für |x| > 5 endlich —
  nur die Bits werden weggewählt).
- `zap()`-Schwelle (|x| < 1e-30) ebenfalls Select. Kein Zustands-
  Commit-Problem: alle Zustände (inDC, inFlux, preLP, outFlux, outDC)
  sind je Kanal und werden lane-weise geführt.
- Der Detector bleibt skalar (Taps + Link-Summierung sind gekoppelt).
- Gewinnmodell: die Filter-/softClip-Anteile des Colour-Blocks (~von
  +10 Punkten Gesamtkosten) halbieren sich für Stereo → grob 2–4 Punkte
  Plugin. Bench-Entscheidung wie im Colour-Abschnitt beschrieben.

**Ort 2 — Transformator-Solver über L/R (der große, risky Fall):**

Kostenmodell als Kernargument: heute kostet ein Stereo-Sample
`iterL + iterR` Solver-Iterationen; als 2-Lane kostet es
`max(iterL, iterR)` + Maskierungs-Overhead. L/R sind in der Praxis
pegelkorreliert → die Iterationszahlen liegen meist nahe beieinander
(benachbart, nicht identisch) → realistischer Gewinn **1,5–1,9× auf den
Solverblock** für Stereo, nicht die vollen 2×. Der Solverblock ist der
größte Einzelblock der CPU-Matrix — das wäre der größte verbliebene
Einzelhebel überhaupt, deshalb ist die Vertiefung es wert, trotz Risiko.

Divergenzstellen im Loop (`TransformerCore::process`, src/dsp/
Transformer.hpp ~:155-205) und ihre Behandlung:

- [ ] **Iterationszahl:** Schleife läuft `max(iterL, iterR)`-mal; die
  konvergierte Lane friert `x` ein (Select aus Konvergenzmaske) und
  überspringt Newton-Update/Bisektion via Maske. Die Konvergenzmaske
  (boolx2) wandert durch alle nachfolgenden Schritte.
- [ ] **Bisektionszweig** (`residual > 0 ? hi=x : lo=x`): reines Select.
- [ ] **`law()`-Verzweigungen:** `saturation_strength==0` (Sym-Fastpath)
  und `family==1` sind **Profilkonstanten** — beide Lanes haben dasselbe
  Modell (der Transformer-Port ist plugin-global), also uniforme Zweige,
  kein Maskierungsproblem. Der Datenzweig `u > 0.98` (Hochfeld-Knie,
  00s) wird zum Select; **uniforme Abkürzung erlaubt:** wenn *keine*
  Lane im Kniebereich ist (OR-Reduktion der Maske — lane-uniforme
  Entscheidung, deshalb legal), wird `seriesExp` komplett übersprungen;
  ist eine Lane drin, rechnen beide Lanes die exp und wählen aus.
- [ ] **`seriesExp` (nicht libm!) vektorisierbar:** eigene Horner-Folge
  mit Bereichsreduktion (k = floor(x/ln2 + 0,5)) — Horner ist reine
  mul/add-Kette ✓; `k` wird je Lane mit FRINTM gebildet; die
  Skalierung `result += result` (k-mal) bzw. `·0,5` ist **exakt**
  (reine Exponentenverschiebung, auch im Denormalbereich rundungsfrei)
  und lässt sich bit-identisch durch die Exponentenfeld-Manipulation
  ersetzen (vreinterpretq_u64_f64 + Integer-Add auf dem Exponentenfeld;
  Bereich k ≤ ±87, Unter-/Überlauf ausgeschlossen — vorher mit dem
  tatsächlichen Wertebereich verifizieren). Alternativ maskierte
  While-Schleife bis max(|k|) — einfacher, kostet im Knie-Fall einige
  Takte mehr.
- [ ] **Exponent-Schleife family==0** (`nonlinear *= u`, p−1 fest
  wiederholte Multiplikationen): datenunabhängige Anzahl ✓ direkt
  vektorisierbar — synergetisch mit dem offenen Kandidaten „p=3/p=5
  explizit ausrollen" (derselbe Code, dann nur 1–2 Vektor-Ops).
- [ ] **Stop-Bank im Loop** (advance=false): 14× (trial, clamp, |·|,
  konditionale Derivativ-Akkumulation) — alles Selects, identisch zur
  Achse-„Operatoren"-Arbeit, nur als Lanes-Version.
- [ ] **Zustands-Commit:** für konvergierte Lanes z/Stops maskiert
  schreiben; nicht konvergierte Lanes (40er-Cap) nehmen den
  Advance-Zweig maskiert. Der 40er-Cap wurde in den Messläufen nie
  erreicht (0 %) — der Advance-Zweig ist Hot-Path-irrelevant, muss aber
  bitidentisch mitwandern.
- [ ] **Ausgangs-Biquad:** b0/b1/a1/a2 sind für beide Kanäle identisch,
  x1/y1/y2 je Kanal → 2-Lane direkt vektorisierbar (keine Divergenz).
- [ ] **Registerdruck:** Zustandssatz je Kern = flux, relax, voltage,
  stops[14], x1, y1, y2, px2 ≈ 20 Doubles = 10 q-Register *nur
  Zustand*, plus Arbeitsregister — A35 hat 32 q-Register; eng, aber
  machbar. MPB-Assemblat auf Spills prüfen (gleiche Prüfung wie
  Kandidat 8 Commit-A/B); Spills fressen den Gewinn.
- [ ] **Diagnose:** `GS76_TRANSFORMER_STATS` bleibt Compile-time-guard,
  Zähler aus dem Skalarpfad übernehmen (Summe je Lane).

**Entscheidungsreihenfolge (bindend, bis ein Bench etwas anderes zeigt):**

1. Isolierter A35-Bench je Ort (Colour-Block, Stop-Bank-Achse,
   L/R-Solver-Achse) mit identischer Rechenarbeit wie der Skalarpfad —
   keine theoretischen Op-Zählungen (Lektion Doppel-Auswertung).
2. Achse „Operatoren" (Kandidat 7) vor Achse „Kanäle" beim Solver:
   kleinerer, sicherer Gewinn ohne Maskierung; L/R-Solver nur anfassen,
   wenn (a) der Bench die Maskierungs-Overhead-Schätzung ≤ ~15 %
   bestätigt und (b) der Stop-Bank-Gewinn allein unter der 2-Punkte-
   Schwelle bleibt.
3. Colour-NEON nur nach dem Solver-NEON (gleiche Intrinsics-Grundarbeit,
   dort größerer Nutzen; Colour-Bench entscheidet über die 3–4-Punkte-
   Schwelle).
4. Jede Umsetzung: skalarer Fallback im Build behalten (Compile-Flag),
   Paritätssatz gegen EEL2 komplett, CPU-Matrix am Gerät c0/×Colour ×
   None/60s/80s/00s/Sym, Mono muss unverändert bleiben (kein Gewinn, aber
   keine Verschlechter).

**Gemeinsame Vorarbeit (alle drei Orte):**
- [ ] NEON-Hilfsheader (Select-Bausteine, seriesExp-Vektor, zap/softClip-
  Lane-Versionen) einmal bauen und unit-testen — die drei Orte teilen
  dieselben Primitive; kein dreifacher Code.
- [ ] x86-Fallback-Pfad automatisch im CI/Testlauf mitkompilieren, damit
  die Paritätssätze beide Pfade decken.

## Offen — Cross-DAW-Variante des LV2-Plugins (2026-10-07 diskutiert)

Ausgangslage: der DSP-Kern ist frameworkfrei (C++11, nur libm, kein UI-/OS-Code);
der Host-Anteil steckt nur im dünnen LV2-Wrapper `src/lv2_plugin.cpp`. Drei
Wege, aufsteigend nach Aufwand:

- [ ] **Weg 1 — LV2 direkt in REAPER laden** (nativ seit 6.x, auch Windows):
  es fehlt nur ein Windows-Build des Bundles (`.dll` statt `.so`, MinGW-w64);
  kleine Toolchain-Arbeit. Risikopunkt: Windows-libm rundet stellenweise
  anders als glibc → C++↔EEL2-Bit-Parität auf Windows neu verifizieren
  (`-ffp-contract=off`, kein fast-math bleiben Pflicht; Paritätssatz komplett
  laufen lassen, kein neuer Fall nötig). Damit wäre REAPER zusätzlich zum
  JSFX-Pfad auch mit dem C++-Kern bedient.
- [ ] **Weg 2 — CLAP-Wrapper** um denselben Kern: C-API ähnlich LV2,
  überschaubarer Wrapper; Presets als State-Chunk statt TTL einbetten; Ports
  in `tools/generate.py` als weitere „Ecke" des Parameter-Dreiecks
  (LV2/JSFX/RPL → +CLAP) erzeugen, keine Handports. GUI zunächst die
  generische Host-UI. CLAP-Verbreitung prüfen, bevor VST3 angefasst wird.
- [ ] **Weg 3 — VST3/AU**: deutlich mehr Protokoll (Processor/Controller-Split,
  IDs, State) plus eigener GUI-Aufwand; nur sinnvoll, wenn CLAP nicht reicht
  (AU wäre macOS-only).
- [ ] Vor allen Wegen klären: Ziel-DAWs/Hosts konkret benennen (Benutzer);
  Portindizes/-symbole/-URIs bleiben unverändert, neue Formate erhalten
  eigene Descriptoren — keine Versionsbump-Pflicht für bestehende Pfade.
  Revisionstreue nur mit belegter Parität behaupten; kein Cross-Build als
  Geräteabnahme ausgeben.

## Offen — Eigenständiges Transformator-Plugin (LV2 + JSFX) (2026-10-08 diskutiert)

Ausgangslage: der Transformator-Solver (Fluss-Integrator, Sättigungsgesetz,
Bank `data/transformers.json` mit 00s/60s/80s/Sym, Kanal-/Richtungs-Zustände,
Oversampling) existiert, ist in C++/EEL2 bitgleich und am Gerät validiert —
er muss **nicht neu gebaut**, sondern nur umgebettet werden. GUI-Asset steht
bereits: `lv2/green-stripe-76.lv2/modgui/assets/transformer-front.png`
(500×500, Frontansicht ohne Fremd-Branding, gezeichnet von
`tools/make_transformer_asset.py`, als Vorlage für die HTML/CSS-Fassung).
Hintergrund: MESSERGEBNISSE 12/12.3 (Bank zeigt Kern-Signaturen, SSL nicht),
MESSTECHNIK 1k.2, docs/DSP.md (Transformator-Laufzeit/Refit-Vertrag).

**Voraussetzung vor dem Start:**
- [ ] **Sym-DC-Pumpen klären** (Punkt oben): akkumulierender Zustand unter
  DC (−0,058 → −0,165 FS). Wenn das eine Modellkorrektur braucht, zuerst
  fixen — sonst erbt das neue Plugin den Defekt mit (Bank ist gemeinsam).
- [ ] **Benutzerentscheidungen einholen (blockierend):**
  1. Umfang: Mono + Stereo? Regler — Modellwahl (Bank inkl. `None`),
     Input-/Output-Gain oder Drive-/Load-Semantik, Oversampling (angehängt,
     startet Off), Bypass. Meter ja/nein? Presets ja/nein?
  2. **Bank-Politik (Weichenstellung):** `data/transformers.json` geteilt
     (Refits wirken dann auf GS76 *und* das neue Plugin — jede Bank-Änderung
     muss künftig beide Revisionspfade bedenken) oder Kopie mit eigener
     Pflege? Geteilt ist weniger Duplikation, Kopie entkoppelt die
     Projektklänge.
  3. Name: neutral (kein Hammond-/Fremd-Bezug im Produktnamen; die
     optische Inspiration kann in `docs/QUELLEN.md` belegt werden).
  4. Provenanz-Aussage: weiter „reduziertes Gray-Box-Modell mit
     provisorischen Kennlinien, keine zertifizierte Hardwaregleichheit".

**Arbeitsschritte (geschätzt 3–5 Arbeitssitzungen bis zur Abnahme):**
- [ ] **Generator für zweites Plugin-Ziel** (größter Posten): eigene
  Bundle-URI, eigenes `model.json`/`parameters.json` (oder konfigurierbares
  Mehrfachziel in `tools/generate.py`), TTL/JSFX-Erzeugung, Presetpfad,
  `validate.py`-Regeln je Bundle (Portzahl-Assertions erweitern). Portlayout
  von Anfang an sauber: neue Ports anhängen, Latency/OS-Muster wie GS76.
- [ ] **DSP-Umbettung:** in→Transformator→out ohne Kompressorpfad (kein
  GR/Detektion, kein Feedback-Abgriff); Regler-Mapping auf den Solver
  (Pegel-/Drive-Skalierung vor dem Kern, kompensierender Output-Gain,
  Bypass exakt transparent inkl. OS-Wechsel); Stereo = zwei unabhängige
  Kanalzustände (kein Link nötig); Latenz 0/3/4 Frames für Off/2x/4x
  beibehalten; C++11, kein `-ffast-math`, `-ffp-contract=off`.
- [ ] **JSFX-Standalone:** EEL2-Solver aus GreenStripe76-Stereo auskoppeln,
  Slider-/State-Mapping, PDC-Deklaration (`pdc_delay`/`pdc_bot_ch`/
  `pdc_top_ch` bei OS-Wechsel), GS76-Caveats übernehmen (`===` für
  gleichartige Zweige, NaN-Geordnete-Vergleichsfunktion beibehalten).
- [ ] **Parität + Tests:** `jsfx_parity`-Struktur auf das neue Paar
  richten (Erwartungen aus dem Artefakt ableiten, keine hartkodierten
  Zahlen); Signaltests: Bypass-Transparenz, DC-Block (00s/60s/80s),
  20-Hz-Pegelreihe gegen die Bankanker, Burst-/Remanenzverhalten,
  Blockinvarianz, OS-Wechselübergänge — die Diskriminierungsprobes aus
  `tools/make_probes.py` sind genau der richtige Testumfang; 1k.2-Werte
  (MESSERGEBNISSE 12) als Referenzkanziffern einpflegen.
- [ ] **GUI:** neue modgui aus dem CSS-Template (PNG als Basis); Meter nur
  wenn entschieden — sonst das 0.5.0-Muster (Output-Port +
  monitoredOutputs) unverändert nachschlagen, erst nach Gerätecheck des
  mod-ui-Stands bauen. `validate.py` erzwingt die `/resources/…{{{ns}}}`-Form.
- [ ] **Doku/Provenanz:** docs/DSP.md (Solver, Refit-Vertrag, CPU-Regime),
  QUELLEN (Modellherkunft, optische Inspiration), MESSTECHNIK
  (Testplan/Messplätze), README/PROJEKT (neues Plugin im Umfang).
- [ ] **Build/Abnahme:** Native Build + `make test`; Cross-Build
  (aarch64, Symbolfloor) für den Dwarf; CPU-Messung am Gerät (nur
  Transformator ist billiger als GS76, OS multipliziert weiterhin);
  REAPER-Verifikation (PDC, OS-Wechsel, Presets) auf dem Testrechner.

**Risiken/offene Punkte:**
- Generator-Mehrfachziel ist der unbekannteste Umbau — erst dort anfangen,
  Datenmodell (geteilte vs. kopierte Bank) vorher festlegen.
- Keine Portänderungen an GS76 als Nebeneffekt; Revisionsnummern der
  beiden Plugins unabhängig führen (jeweils dritte Stelle der eigenen
  `version`).
- CPU: 4x OS am A35 vor dem Feature-Freeze messen, nicht theoretisieren.
- Veröffentlichung/Commit erst nach ausdrücklichem Auftrag (AGENTS).

## Offen — Projektinfrastruktur

- [x] Revisionszähler eingeführt (2026-10-07, AGENTS): `data/model.json`
  `version` + `revision`; jede Sourcecodeänderung (= alle Änderungen zwischen
  zwei Nutzereingaben) ⇒ `revision` +1 und `tools/generate.py`; Anzeige in der
  LV2-GUI unter Mono/Stereo (Fußzeilenplatte) und in der JSFX-GFX unten rechts
  (`#gs_ver`; die Revisionsnummer ist die dritte Stelle der Versionsnummer).
  ~~Aktueller Stand: 0.4.2 (0.4.1 rev 1/rev 2 wurden zum Dreistelligen
  Schema zusammengeführt).~~ *(Aktuell: **0.5.2** — 0.5.0 VU-Meter/GR-Port,
  0.5.1 Sym-Fastpath, 0.5.2 Kehrwerte; alle am Gerät bestätigt.)*

## Ausstehende Verifikationen — Solver-Stand 1e-6 (2026-10-07)

Der Solver-Stand (Prädikator + Toleranz 1e-6, Commits `fc1f083`/`3c26259`)
ist getestet (make test + Parität 430+76, max 0 FS, 1-%-Anker unverändert)
und gepusht; Pin zeigt darauf. Offen in dieser Reihenfolge:

- [x] MPB-Build des 1e-6-Stands installieren, **SHA ≠ `66c835e8`** auf dem
  Gerät verifizieren, Audio-Stack neu starten. **Erledigt (2026-10-07):**
  installiert ist `ed05032b…` (Commit `2d0aff6`, 0.4.1, MPB-Pin
  `e5a1099`), Bundle-Generation per modgui-HTML verifiziert.
- [x] REAPER-Renders (JSFX ist per Symlink aktuell): 28 Zustände
  (Colour 0 × Typen + 24 Kombinationen) — **bestanden (2026-10-07, Batch
  `19_15_06`)**: alle 28 Zustände gegen die 1e-6-C++-Referenzen
  (`/tmp/opencode/ref1e6`) bitgleich, Offset +3 Samples (REAPER-PDC der
  2x-Latenz), schlechtester max|diff| 5,96×10⁻⁸ = 0,5 LSB. Die letzten
  Transformator-Änderungen (Prädikator + Toleranz 1e-6) sind damit auch in
  REAPER am vollen 64-s-Matrixprogramm bestätigt. Archiv:
  `test-results/jsfx-render-1e6-20261007/`; die früheren Batches 16_17_10
  und 16_57_58 sind Bisektionsläufe zur EEL2-`instance()`-Scope-Falle und
  nicht Teil der Verifikation.
- [x] CPU-Matrix (36 Zustände) mit der 1e-6-Binary neu fahren und gegen die
  94ab2fa-Basis vergleichen; Erwartung: 00s/Sym −10–12 %, 60s/80s ~0.
  **Bestätigt (2026-10-07, `test-results/cpu-matrix-1e6-20261007`):** 00s
  −7 Punkte Median (56–57 % statt 58–66 %), Sym −5,5 Punkte (56–60 % statt
  64 %), 60s/80s Δ 0,0, Bypass/None/Colour unverändert, 0 xruns, Spitzen
  unverändert (max 76 %). Relativ zum Zustand ≈ −9…−11 %, konsistent mit
  dem isolierten Bench (−10–12 %) inkl. plugin-level Verwässerung durch
  Host-Overhead.
- [x] `tools/render_jsfx.cpp` (ysfx-Offline-Renderer, Alternative zu den
  REAPER-Renders): der WAV-Schreibfehler war das fehlende
  Ausgabeverzeichnis — **mkdir ergänzt und verifiziert (2026-10-08)**:
  CMake-Target `render_jsfx`; ysfx ↔ C++-Referenz bitgleich (0 LSB,
  Offset 0), ysfx ↔ REAPER-Render 0,5 LSB bei PDC-Offset −3 (dieselbe
  Größenordnung wie die akzeptierte REAPER↔C++-Parität; REAPER-24-bit-
  Dither). Nachweis: `test-results/ysfx-render-20261008/verify.json`
  (MESSTECHNIK 1l). ysfx ist der gepinnte Referenz-Host.
- [x] 1e-6-Qualitätsentscheidung final bestätigen (Lösungsfehler ≈ −120 dB;
  Hörprobe optional). **Bestätigt (2026-10-07):** Benutzer-Hörprobe meldet
  den Unterschied als sehr subtil (erwartungsgemäß, Lösungsfehler liegt
  unter dem 24-bit-LSB); Messnachweise bleiben die Parität/Anker. Einordnung
  und Erläuterung: EXTERN (Abschnitt Hörprobe).

- [x] Dwarf-GUI: Logo-Renderfix auf dem Gerät verifiziert (2026-10-07):
  Screenshot aus der installierten Bundle-GUI per SSH gezogen — Logo weiß auf
  dem grünen ENGINE-Feld, Paneel vollständig; `.mk`-Pin folgt dem HEAD.
  Letzte live Sichtprüfung im Web-UI kann der Benutzer bestätigen.
- [x] README-Verzeichnisse auf ersten beiden Stufen erstellt (2026-10-07):
  data/, docs/, jsfx/, lv2/, packaging/, reaper/, src/, test-results/, tests/,
  tools/ mit Kurzübersicht; Haupt-README nach der benannten Struktur.
- [x] REAPER-JSFX per Symlink installierbar (2026-10-07): `jsfx/make-reaper-links.cmd`
  (Admin/UAC) setzt Links für alle jsfx-Dateien nach
  `%APPDATA%\REAPER\Effects\GreenStripe`; README dort weist darauf hin, die
  Links nach neuen/umbenannten/gelöschten Dateien zu erneuern. Erste Ausführung
  durch den Benutzer zu prüfen.

## Ausstehende Verifikationen — 0.5.2, invariante Kehrwerte (2026-10-08)

Der 0.5.2-Stand (Kehrwerte + 00s-Hochfeldkonstanten in `prepare()`,
Revision 0.5.2) ist **lokal getestet, committet (`b09364e`) und als MPB-Pin
gesetzt**; ~~Gerätetests laufen~~ **Gerätetests bestätigt** (Geräteserie
`device-052-20261008` + REAPER-Batch `14_14_41`, 2026-10-08). Offen in
dieser Reihenfolge:

- [x] 0.5.2 committen; MPB-Pin auf den 0.5.2-Commit setzen; MPB
  `moddwarf-new` bauen, installieren, **SHA ≠ `c936aca6…`** verifizieren,
  Audio-Stack vollständig neu starten. **Erledigt (2026-10-08):** Pin
  `b09364e`, Geräte-SHA `d94d3121…`, installiert Okt 08.
- [x] Geräteanker erneuern: Transformator-Matrix und Colour-Stufen gegen
  frische 0.5.2-Referenzrenders. **Bestätigt (2026-10-08,
  `test-results/device-052-20261008`, digitale Dwarf-Recorder-Serie
  Referenz/GROUP 1/GROUP 2):** Anker exakt (20-Hz-Klirr
  12,424/12,276/1,014/0,001 %, relative Gains −0,8174/−0,4412/−0,0156/
  −0,0013 dB), max |Δ Gain| ≤ 0,02 mdB über 10 Zustände × 19 Segmente,
  Samplevergleich nach Gain-Fit: lineare Pfade auf float32-LSB, Solver-
  Profile ULP-Rest (max 1,1×10⁻⁴ ≈ −79 dBFS) — Verschiebung wie erwartet
  auf Rundungsniveau. GROUP 1 × 2 am Gerät bewusst nicht aufgenommen
  (Benutzerentscheid); Plots im Manifest. **Nebenbefund:** `render_lv2.py`
  verband seit 0.5.0 den Output-Port `gr_db` als Eingangs-Control — alle
  damit erzeugten Renders liefen mit OS Off; Tool gefixt (tools, keine
  Revisionspflicht), 34 Referenzrenders neu erzeugt und gegen den
  verifizierten 1e-6-REAPER-Batch bitgleich bestätigt (34/34 + Reference,
  max 0,5 LSB, PDC ±3).
- [x] REAPER-Renders (JSFX per Symlink) der 28 Vollmatrix-Zustände gegen
  frische 0.5.2-C++-Referenzen bitgleich prüfen (Abgleich mit PDC-Offset
  ±3 Samples). **Erledigt (2026-10-08, 14:14):** nach REAPER-Neustart/
  FX-Reload neues Batch `2026-10-08 14_14_41` — erweitert auf **34 Zustände
  + Referenzlauf**: alle 34 bitgleich (Offset −3, max 0,5 LSB), `no_fx`
  sampleidentisch zum Stimulus; damit auch die 24 GROUP 1 × 2-Kombinationen
  in REAPER abgedeckt. GUI zeigt 0.5.2. Archiv:
  `test-results/jsfx-render-052-20261008/` (MESSTECHNIK 1j, MESSERGEBNISSE 9).
- [ ] CPU-Stichprobe am Gerät: Erwartung Typen −1…−3 Punkte gegenüber
  `cpu-matrix-051-20261008` (54–56 %), Sym zusätzlich −1…−2 (46 %);
  1–2-Punkte-Granularität einkalkulieren, Bypass/None unverändert.
  Benutzerwahrnehmung 2026-10-08: „weiterhin gut ausgelastet" — verträglich
  mit der kleinen erwarteten Differenz, Messung steht noch aus.
- [x] 1-%-Anker und `make test` im 0.5.2-Stand lokal bestätigt
  (2026-10-08, nativer x86-Build, Compiler jetzt im WSL-Host verfügbar —
  Sysroot entfiel): make test PASS (DSP/Transformer/LV2-ABI/GR-Port/
  Refit/Bundle), Parität 430+76 max 0 FS, 1-%-Anker 1,01…1,10 % je Rate.
  Danach Preset-Hörprüfung 21/22 sowie 31/37 und 35/38 am Gerät (Punkt
  oben) offen.
- [x] `tools/render_results_doc.py` um die 0.5.2-Geräteserie erweitert
  (`device-052-20261008`, Abschnitt 8 mit Digital-/Analog-Deltas und
  Samplevergleich) und `docs/MESSERGEBNISSE.md` inkl. Plot
  `mess-device052-delta.png` neu generiert (2026-10-08).
- [x] Kleine Unit-Tests für `tools/dwarf_matrix_session.py` (2026-10-08,
  `tests/test_dwarf_matrix_session.py`, 8 Fälle): Chirp-Erkennung
  (block_correlate mit Rauschen/Trefferzusammenfassung), Ratenprüfung,
  Positions-/Reihenfolgezuordnung (find_playbacks), Schnittgrenzen und
  Warnpfad von do_cut; do_analyze/do_report bleiben über die
  scarlett_test-Tests abgedeckt.

## PluginDoctor-Vergleich Transformer-Harmonics (2026-10-08) — Auswertung abgeschlossen

**Gültige Serie 14:00–14:52 ausgewertet** (`tools/analyze_pd_transformer.py` →
`test-results/pd-transformer-20261008/analysis.json`; MESSERGEBNISSE 10,
MESSTECHNIK 1i). GS76-Captures (60s/80s/00s/Sym) und SSL Fusion Transformer
MIN/STOCK/MAX; GS76-Panelsellungen benutzerbelegt (**COMP OFF, 4x OS,
Colour 0 %, Mix 100 %**). Kernbefunde: Klirrsumme aus der FFT-Momentaufnahme
stimmt mit der THD(f)-Kurve auf Δ ≤ 0,08 dB (Gültigkeitsnachweis); SSL
verzerrt im Tieftönen massiv stärker (MAX 8–30 Hz ≈ 55 %, STOCK ≈ 69 %
gegen GS76 60s/80s 18/22 % bei 20 Hz) — stützt das Klangziel quantitativ;
bei 1 kHz liegt GS76 60s zwischen SSL STOCK und MAX; PD-Reihung 80s ≈ 00s >
60s weicht von der Gerätetreihung ab (heißere Anregung trifft das 00s-Knie);
Kopplungsverlust sichtbar (Grundwelle −7,5/−3,5 dB unter Anregung).

- [x] GS76-FFTs/THD-Kurven erneut exportieren mit sichtbarem Re-Trigger —
  gültig (2026-10-08), Exportprobleme behoben (Crosscheck ≤ 0,08 dB).
- [x] Numerische GS76↔SSL-Auswertung und Vergleich mit den Bankankern —
  durchgeführt (Charaktervergleich, unkalibriert; Plots in MESSERGEBNISSE 10).
- [x] **Kalibrierter Vergleich auf anderem Weg erbracht (2026-10-08):**
  SSL Fusion Transformer als REAPER-Render über dasselbe Matrixprogramm
  (AMOUNT 0/50/100/150/200, −2 dBFS, digital, paddgenau,
  `test-results/ssl-amount-20261008/`, MESSTECHNIK 1k, MESSERGEBNISSE 11):
  20 Hz A50 7,72 % @ −1,02 dB (zwischen GS76 00s und 60s), A100 51,3 % @
  −6,31 dB, A200 27,4 % @ −15,90 dB; 1 kHz ≤ 0,011 % bei allen
  Stellungen; AMOUNT 0 kein Bypass (+0,71 dB @ 8 kHz fest). **SSL A ≈ 50
  ist der nächste kalibrierte Referenzpunkt fürs Klangziel im Bass.**
- [ ] SSL-Knopfprovenanz nachtragen (SHINE/MIX/TRIM als Panel-Screenshot
  beim nächsten Renderlauf mitarchivieren); PD-Wiederholung mit statischen
  Einzeltönen nur noch optional (kalibrierte Serie existiert).
- [x] **Diskriminierungstests SSL-Plugin (Hypothese „kein physikalisches
  Kernmodell", MESSTECHNIK 1k.1/1k.2):** ausgeführt 2026-10-08 — SSL
  AMOUNT 0/50/100/150/200 und GS76-JSFX 00s/60s/80s/Sym über das
  Kombiprogramm gerendert und ausgewertet
  (`tools/analyze_discrimination.py`,
  `test-results/diskriminierung-20261008/`). **Urteil: SSL = Effektmodell
  bestätigt** (Bursts ohne Remanenz, IM symmetrisch/unter Vorhersage,
  A200-Verlust als linearer Fix-Shelf, DC-Durchlass 4–37 %); GS76-Bank
  zeigt die Kern-Signaturen (DC-Block, 80s-Remanenz-Shift, H2 unter DC).
  Details: MESSERGEBNISSE 12, MESSTECHNIK 1k.2 (Durchführung). Eine
  kontaminierte Vorserie (−3 dB) wurde erkannt und verworfen.
- [ ] Sym-Transformator: DC-Pumpverhalten klären (Nachlauf nach
  DC-Zyklen akkumuliert −0,058 → −0,165 FS; Verdacht Integrator-Drift im
  Sym-Modell) und ggf. gegen den Modellvertrag prüfen — DSP-Änderung
  würde C++/EEL2-Parität + Revision erfordern.
- [ ] Optional: no_fx-Negativkontrolle des Diskriminierungsprogramms
  rendern (sampleidentisch) und die Auswertekette damit formell
  verifizieren; SSL-Knopfprovenanz bei der Gelegenheit mitarchivieren.
- [ ] PD-Klärung der 00s-Reihungsabweichung (gleicher Ton/Pegel wie die
  Gerätetreihe, 2x OS statt 4x OS fahren, Stellung protokollieren).

## Erledigt (zur Erinnerung, nicht mehr offen)

- [x] `.opencode/skills/audio-coding/SKILL.md` um MOD-Dwarf-Erkenntnisse erweitert.
- [x] modgui-Logo im grünen Rechteck ersetzt (Commit `1262999`).
- [x] Dwarf-Messreihe GS76x0–x4, 128/256 Frames: Tabelle in MESSTECHNIK
  (Abschnitt Dwarf-Lastmessung); STATUS/HANDOFF 2026-10-06 aktualisiert.
- [x] PluginDoctor-GR-Daten dokumentiert (EXTERN).
- [x] Scarlett-Liveaufnahme 2026-10-05 ausgeführt; Auswertung zeigt
  Pegel-/SNR- und HF-Grenzen → Wiederholung offen (oben).
- [x] Dokumentation auf 7 Konsolidierungsdokumente + TODO zusammengefasst
  (2026-10-06); generiertes `PRESETS.md` bleibt als Generator-Artefakt.
- [x] modgui-Assets neu gerendert (2026-10-06, Chromium/Playwright): Logo wird
  dargestellt; `gui_preview.page_html()` inlined HTML-`src`-Assets als
  Data-URI (Basis-URL-Problem von `set_content()` behoben).
