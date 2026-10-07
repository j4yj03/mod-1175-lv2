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
  liegen, die Quellstufe ist a-priori unbekannt). Option für 1 Iteration:
  Toleranz 1e-6 (Lösungsfehler ≈ −120 dB, hörbar unsicher) — Qualitäts-
  entscheidung, nicht umgesetzt. Checksummen/Baselines verschieben sich
  (Rundung) — Render- und Gerätevergleiche erneuern.
- [ ] Startwert-/Steigungsverbesserung (Prädiktor zweiter Ordnung) bzw.
  gelockerte Konvergenztoleranz (aktuell 1e-14 relativ) prüfen; Ziel
  Iterationen < 2 je Probe.

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

## Offen — Projektinfrastruktur

## Ausstehende Verifikationen — Solver-Stand 1e-6 (2026-10-07)

Der Solver-Stand (Prädikator + Toleranz 1e-6, Commits `fc1f083`/`3c26259`)
ist getestet (make test + Parität 430+76, max 0 FS, 1-%-Anker unverändert)
und gepusht; Pin zeigt darauf. Offen in dieser Reihenfolge:

- [ ] MPB-Build des 1e-6-Stands installieren, **SHA ≠ `66c835e8`** auf dem
  Gerät verifizieren, Audio-Stack neu starten.
- [ ] REAPER-Renders (JSFX ist per Symlink aktuell): 28 Zustände
  (Colour 0 × Typen + 24 Kombinationen) — die Bit-Verifikation läuft gegen
  die fertigen C++-Referenzen (1e-6, Cross-Build-matching,
  `/tmp/opencode/ref1e6` bzw. neu erzeugen).
- [ ] CPU-Matrix (36 Zustände) mit der 1e-6-Binary neu fahren und gegen die
  94ab2fa-Basis vergleichen; Erwartung: 00s/Sym −10–12 %, 60s/80s ~0.
- [ ] `tools/render_jsfx.cpp` (ysfx-Offline-Renderer, Alternative zu den
  REAPER-Renders): der WAV-Schreibfehler war das fehlende
  Ausgabeverzeichnis — mkdir ergänzen und gegen eine REAPER-Render
  bitverifizieren; ysfx ist der gepinnte Referenz-Host.
- [ ] 1e-6-Qualitätsentscheidung final bestätigen (Lösungsfehler ≈ −120 dB;
  Hörprobe optional).

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
