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
- [ ] Dwarf-Lasttabelle: Provenienz nachtragen (Messdatum, Tool-Version,
  installierte SHA256 je Serie, Settle/Messfenster).
- [ ] 0.4.1-Bundle mit MPB `moddwarf-new` neu bauen; ABI/Hash dokumentieren;
  danach 21/22 sowie 31/37 und 35/38 im Pedalboard hören, CPU/xruns prüfen.
- [ ] Reale REAPER-7-Abnahme (Recall/Automation/Host-GR/Fonts) und
  Dwarf-Bedienprüfung (PROJEKT, Abschnitt Übergabe P0/P1).
- [ ] Neue Drag-Handles am Gerät ziehen: unterer 9-px-Rand und Fußzeilenplatte
  (Cursor, Panel-Move, keine Reglerberührung). Toolkit-Bindung ist belegt
  (MESSTECHNIK, Abschnitt MOD-GUI-Browsertest); Lauf mit echter MOD-UI-Quelle offen.

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
Solange nichts umgesetzt ist, werden `src/`/`jsfx/` nicht berührt — die
Version bleibt **0.4.1**; aktueller Stand nach der 2:1-Änderung: **0.4.2**.

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
0.4.2-Kennlinie (2:1) tragen muss.

**1. MPB-Build tatsächlich auf Cortex-A35 optimieren** (gemessen −1,2 bis
−3,6 % je Profil, PERFORMANCE „Build-Tuning"):

- [ ] `CXXFLAGS += -mcpu=cortex-a35` in der MPB-Rezeptur
  (`packaging/mod-plugin-builder/green-stripe-76/green-stripe-76.mk`)
  **anhängen**, vorhandene Flags nicht überschreiben; fährt mit dem nächsten
  Pin-Bump mit (0.4.2).
- [ ] Bit-Identität gegen denselben Compiler ohne `-mcpu` über die
  Bench-Checksummen nachweisen (`-ffp-contract=off`, kein Fast-Math bleibt).
- [ ] Stichprobe am Gerät statt sofort 36 Zustände: None/60s/80s/00s/Sym ×
  Colour 0/100, OS 2x; Erwartung −1…−4 %.

**2. `Symmetric`-/No-Hysteresis-Fastpath** (größter bitidentischer Hebel):
Sym hat `hysteresis_enabled=0` und `saturation_strength=0`, zahlt aber
weiterhin 14 Stop-Trials, 14 Clamps, 14 Ableitungsbedingungen, 14
Zustands-Commits plus den u²-Loop in `law()`, der numerisch nach 0
kollabiert.

- [ ] `hysteresis_enabled==0` ⇒ komplette Stop-Bank überspringen
  (Auswertung **und** Commit); Stop-Zustände für Sym nicht fortführen
  (Modellwechsel resettet den Core ohnehin).
- [ ] Zusätzlich `saturation_strength==0` ⇒ direkt `i=λ/Lm`,
  `di/dλ=1/Lm` statt Loop-mal-Null.
- [ ] Bit-Identität nachweisen, nicht annehmen: ±0-Fälle (`0·stop` kann
  ±0 sein), Extremreizen bis ±256 FS, Cap-Pfad (40 Iterationen),
  Modellwechsel Sym↔60s, OS off/2x/4x; Checksummen-A/B am A35.
- [ ] EEL2 `gs_xf_core` spiegelt beide Zweige; Paritätssatz komplett.
- [ ] Isolierten Bench + Plugin-Stichprobe fahren; Erwartung mehrere
  Plugin-Punkte bei Sym (aktuell 52–60 % Median).

**3. Profil-spezialisierte Kennlinien** (klein bis mittel, 60s/80s):

- [ ] p=3/p=5 explizit ausrollen (u², u⁴ sequenziell) mit **exakt
  erhaltener Multiplikationsreihenfolge** des bestehenden Loops (Parität!);
  00s (Fröhlich/Hochfeld) unverändert, Sym linear (siehe 2).
- [ ] Zweigentscheidung je Koeffizientensatz (`prepare()`), nicht pro Sample
  neu; keinen indirekten Funktionszeiger einführen, bevor dessen Kosten
  gemessen sind.
- [ ] A35-Microbench vor Übernahme; nur bei echtem Gewinn umsetzen.

**4. Invariante Größen vorberechnen:**

- [ ] `1/lm_h`, `1/relax_l_h`, `1/((1+relaxation)·relax_l_h)` und die
  00s-Hochfeldkonstanten (Knie, Zielsteigung, Breite) in
  `TransformerCoefficients::prepare()` vorrechnen; EEL2 identisch bei der
  Koeffizientenwahl.
- [ ] Zuerst im MPB-Assemblat prüfen, ob GCC die Divisionen nicht schon
  hoistet (sonst Doppel-Auswertung-Lektion); Vorher/Nachher mit identischer
  Toolchain und Checksummen.

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

**Neue Reihenfolge (ersetzt die unten stehende für die Umsetzungsplanung):**
1) `-mcpu=cortex-a35` in die MPB-Rezeptur (mit dem nächsten Pin-Bump/0.4.2),
2) Sym-/No-Hysteresis-Fastpath, 3) Invarianten + p-Spezialisierung,
4) quellenbewusster Prädiktor, 5) Stop-Bank-NEON, 6) Commit-A/B, 7)
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
- [ ] Kennlinien-LUT für `law()`: nur nach A35-Microbench — softClip-Lektion:
  LUT kann langsamer als analytisch sein (9,7 vs 1,87 ns auf x86), A35-Cache
  schlechter. Die Stop-Zweige sind zustandsabhängig und bleiben
  tabellenuntauglich.

Nicht wirkksam (dokumentiert, nicht verfolgen): Iterationslimit senken
(0 % am Cap); kanalübergreifende Zustandsnutzung (Vertrag);
Auto-Deaktivierung bei Compression Off (bewusst nicht vorgesehen).

Vorgeschlagene Reihenfolge (aktualisiert nach Serie B + Build-Tuning):
Build-Tuning (`-mcpu=cortex-a35` in die MPB-Rezeptur, −1,2 bis −3,6 %,
jetzt umsetzbar) → ~~Stop-Zweig-Spezialisierung (30–50 % des Blocks)~~
**gemessen 1–2 %** (12/13 Zweige klemmen nie — nur mit dem
Startwert-Prädikator zusammen sinnvoll) → NEON (Maskierungsrisiko, erst
danach bewerten) → OS-Entkopplung (Vertragsfrage, zurückgestellt —
Transformator bleibt oversampled). Doppel-Auswertung verfeuert (~0 %),
Toleranz 1e-6 umgesetzt (−10–12 % bei 00s/Sym).

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

## Offen — Projektinfrastruktur

- [x] Revisionszähler eingeführt (2026-10-07, AGENTS): `data/model.json`
  `version` + `revision`; jede Sourcecodeänderung (= alle Änderungen zwischen
  zwei Nutzereingaben) ⇒ `revision` +1 und `tools/generate.py`; Anzeige in der
  LV2-GUI unter Mono/Stereo (Fußzeilenplatte) und in der JSFX-GFX unten rechts
  (`#gs_ver`; die Revisionsnummer ist die dritte Stelle der Versionsnummer).
  Aktueller Stand: **0.4.2** (0.4.1 rev 1/rev 2 wurden zum Dreistelligen Schema
  zusammengeführt).

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
- [ ] `tools/render_jsfx.cpp` (ysfx-Offline-Renderer, Alternative zu den
  REAPER-Renders): der WAV-Schreibfehler war das fehlende
  Ausgabeverzeichnis — mkdir ergänzen und gegen eine REAPER-Render
  bitverifizieren; ysfx ist der gepinnte Referenz-Host.
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
