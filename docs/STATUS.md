# Entwicklungsstand und Übergabe

Stand **2026-10-03**, Projekt **0.2.0**. Code und Dokumentation sind umgesetzt.
Dies ist keine bloße Planungsantwort. Benutzerziel: eigener **Green Stripe**,
Hardware-Revision A/D nicht mehr bindend.

## 1. Implementiert

- Frameworkfreier C++11-DSP und identischer EEL2-Kern.
- 4×-Polyphasen-IIR-Verarbeitung von Audiopfad **und** Feedback-Regelung.
- Nichtlinearer FET-Divider, impliziter begrenzter Regler, programabhängige
  Erholung, All Buttons, asymmetrische Färbung und Output nach Detektor.
- LV2-Mono-/Stereo-Deskriptoren in einem Bundle, Enabled/Compression/Mix/Colour,
  optionaler Link, separate Kanal-/Controllerzustände, keine Meterports.
- MOD-GUI ab 0.2.0 als 1176-inspiriertes Gray-Box-Layout nach Pedalvorlage:
  Portrait-Faceplate (Silber, schwarze Regler), INPUT/OUTPUT oben mit
  Bypass-LED zwischen den Reglern, ATTACK/RELEASE/RATIO-Reihe, Gray-Box-
  Erweiterungsgruppe (Mix/Colour/Compression/Link/Oversampling), grünes
  GS76-Banner, BYPASS als Footswitch, bewusst ohne GR-/Level-Meter;
  Illustrations-PNGs im selben Layout.
- JSFX-Meter 0.2.1-feinheiten: Skala −60 bis 0 dBFS (0 = Clipping),
  Orange ab −12 dBFS, Rot ab −3 dBFS, breitere Balken, Peak-Hold 2 s,
  PK-Zahlen zeigen den Hold statt des schnell fallenden Peaks.
- JSFX Mono/Stereo mit GR/Peak/RMS/Hold/Clip und Host-GR-Meldung für REAPER 7.
- 26 Instrumentpresets, zwei `.rpl`-Bänke, eingebauter Selector und Custom-Erkennung.
- Native Make/CMake-Builds, offizielles MPB-Skript/Rezept, zusätzlicher AArch64-
  Cross-Build, Archiv-/Hash-/ABI-Werkzeuge.
- Proben-/Offline-WAV-Renderer, NAM-Inventar und vollständige Markdown-Doku.
- `AGENTS.md` und `HANDOFF.md` für andere Session/Testrechner.
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
| Presetbereiche/Assets/Includes | PASS: 26 Presets, beide Varianten |
| EEL2-Compile | PASS mit gepinntem ysfx, einschließlich tatsächlicher GFX-Sektion |
| Audio-C++/JSFX-Parität | **PASS: 232 Fälle** (ab 0.2.0 inkl. 72 OS- und 8 OS-Umschaltfälle), größte float-Port-Abweichung **0 FS** (bitgleich) |
| 0.1.0/0.1.1 Burstregression | PASS: 80 stationäre Fälle (neu@4x gegen Altstand), max Audio ~7,1×10⁻¹⁴ FS, GR ~2,4×10⁻¹¹ dB |
| OS-Umschaltterminierung | PASS: Probe über ~2700 Raten 8k–384k, Auf/Ab/Rapid-Toggle, Latenz folgt, endliche Signale |
| LV2-OS-Latenz/Umschaltung | PASS: 0/3/4 Frames, blockinvariante Mid-Stream-Wechsel bei 64–512 Frames |
| Release-Approximation | PASS: analytische exp/log-Fehlergrenzen bei 8/44,1/48/96/384k; Series-Kernel ≤ ~1,2×10⁻¹⁴ relativ zu libm |
| Native Benchmark 0.2.0 | Mono mode0 0,0146 s/s (+5 % gegen 0.1.1-Stand), Stereo mode0 0,0223 s/s (+10 %); Checksummen stabil; keine Dwarf-Aussage |
| CPU-Matrix 0.2.0 | Stereo 48k, Bestwert/5: Off+C0 0,0091 s/s; Off+C100 0,0191 (2,1×); 2x+C100 0,0385 (4,2×); 4x+C100 0,0704 (7,7×). Colour verdoppelt wegen nichtlinearem Kern, OS skaliert mit Subframenzahl; keine Dwarf-Aussage |
| Echte JSFX-CPU-Messung | Uninstrumentiert ysfx: normal Mono ~42 %, Stereo Link ~50 %, clean Stereo ~76 % weniger Zeit |
| `.rpl`/Selector/Custom | PASS: **52 Presets**, echter ysfx-Banklader/Rendering |
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
Ursachen, Dissertationseiten und Betriebsänderungen: `CPU_ANALYSIS.md`.

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
ausgewertet. Bericht: `docs/PLUGIN_DOCTOR_EVALUATION.md`, Kennwerte/Hashes:
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
- NAM-Profilrate A1 unbekannt, Positionsdaten fehlen; nicht als reiner statischer
  Shaper oder kompletter steuerbarer Kompressor behauptet.
- Capturegewichte/WAVs nicht in Distribution.

## 6. Nächste konkrete Arbeit

1. Pakete/Hashes auf Testrechner übernehmen, `HANDOFF.md` abarbeiten.
2. Dwarf SDK-Install und REAPER JSFX-/RPL-Install; OS-Regler in beiden
   Umgebungen gegen Off/2x/4x hören und auf CPU messen.
3. Routing/Link/Bypass/Recall, Realtime und pegelgleiche Musik; nach den neuen
   Mono-Versuchen Zeitbereichs-Bursts und Alias-Konvergenz besonders priorisieren.
   OS-Umschaltung im laufenden Programm (Transport läuft) auf Knackfreiheit prüfen.
4. 0.2.0-Cross-Build (MPB moddwarf-new) und Symbolfloor neu bestümen; der
   Series-Umbau hat die GLIBC-2.29-Referenzen entfernt, Erwartung weiterhin
   nur libm/libc mit tieferem Floor.
5. 0.2.0-Pakete erzeugen (`tools/package.py`) und Herkunft festhalten.
6. Ergebnisse mit `TEST_REPORT_TEMPLATE.md`; gezielte Änderungen nur anhand
   Befund, C++/EEL2/Tests/Modelldoku gemeinsam.

## 7. Git / Originaldateien

Das initiale Repository hatte keine Commits. Inzwischen liegen die vom Benutzer
übernommenen Implementierungs-/Messdaten-Commits vor; Messdatenstand
`424501a` („Plugindoctor auswertung“). In der aktuellen Analysesession wurde
kein Commit/Push/PR angelegt. `dist/` und `.so`-Dateien sind ignoriert; das
aktuelle `.gitignore` ignoriert `build/` nicht pauschal. Neue Diagnose-Binaries
sollten außerhalb des Versionsbestands bleiben. Elternverzeichnis-Originale und
externe Messdateien wurden nicht verändert.
