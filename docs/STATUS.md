# Entwicklungsstand und Übergabe

Stand **2026-10-04**, Projekt **0.3.0**. Code und Dokumentation sind umgesetzt.
Dies ist keine bloße Planungsantwort. Benutzerziel: eigener **Green Stripe**,
Hardware-Revision A/D nicht mehr bindend.

## 1. Implementiert

- Frameworkfreier C++11-DSP und identischer EEL2-Kern.
- 4×-Polyphasen-IIR-Verarbeitung von Audiopfad **und** Feedback-Regelung.
- Nichtlinearer FET-Divider, impliziter begrenzter Regler, programabhängige
  Erholung, All Buttons, asymmetrische Färbung und Output nach Detektor.
- LV2-Mono-/Stereo-Deskriptoren in einem Bundle, Enabled/Compression/Mix/Colour,
  optionaler Link, separate Kanal-/Controllerzustände, keine Meterports.
- MOD-GUI ab 0.3.0 als querformatiges **Edelstahl-Paneel** mit vier senkrechten
  Feldern: GAIN (Input/Output) und TIME (Attack/Release) als dunklere Stahlfelder,
  der **grüne ENGINE-Feld** (Verhältnis, Comp-Kippschalter COMP ON/OFF,
  Oversampling, Link) als „The Green Stripe", COLOUR (Mix silbern, Colour,
  Transformator) wieder in Stahl. Namenszug „Green Stripe 76 / FET COMPRESSOR/
  LIMITER EMULATION / MONO oder STEREO" unten links, Bypass als **Kippschalter**
  unten rechts. Bays sind dunkler als das Paneel, damit die Gruppierung nicht nur
  über Farbe trägt; bewusst ohne GR-/Level-Meter. Screenshots/Thumbnails aus
  `tools/make_assets.py` im selben Layout.
- Transformator-Auswahl ab 0.3.0: Port `transformer` (LV2 Enum, **Index 16
  Stereo / 13 Mono**, angehängt nach Latenz und Oversampling, `connectionOptional`,
  Default `None`), JSFX slider13, fünf Stufen `None / 60s / 80s / 00s /
  Symmetric` aus `docs/sauce/xformer.lib`. **Ohne Klangwirkung** — der Wert läuft
  durch den Parameterpfad und ist preset-adressierbar, ist aber nicht mit dem
  Audiopfad verbunden. Echtzeitform und Alternativen in `DSP_ARCHITECTURE.md`
  Abschnitt 11.
- Der Transformator ist eine **Klangwahl und wandert mit dem Preset**. Er wird
  deshalb anders behandelt als das Oversampling: `tools/generate.py` führt beide
  angehängten Ports über `appended_value()`, aber Oversampling startet nach jedem
  Recall auf Off (Qualitäts-/CPU-Wahl), während das Transformatorfeld aus dem
  Preset gelesen wird. Belegt sind 3 von 31 Presets — 28 *Bass Mojo Bite* (`80s`),
  29 *Vintage Blue Grit* (`60s`), 30 *Huge Sub Weight* (`00s`); die übrigen 28
  stehen auf `None`. LV2, JSFX-Selektor und RPL-Bänke sind gegen denselben Helper
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
| Presetbereiche/Assets/Includes | PASS: 31 Presets, beide Varianten |
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
`-O3 -mcpu=cortex-a35`, `check_abi.py --dwarf` PASS (GLIBC-Floor 2.17).

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
`CPU_ANALYSIS.md`, Abschnitt 5b.

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
  `DSP_ARCHITECTURE.md` Abschnitt 11.
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
   nur libm/libc mit tieferem Floor. Das Buildroot-Rezept ist auf den
   Cloud-Builder-Fluss umgestellt (git-Quelle mit Commit-SHA statt
   `SITE_METHOD = local` mit `/root/source`); ein erfolgreicher
   Cloud-Build und eine Geräteinstallation stehen noch aus.
5. 0.2.0-Pakete erzeugen (`tools/package.py`) und Herkunft festhalten.
6. Ergebnisse mit `TEST_REPORT_TEMPLATE.md`; gezielte Änderungen nur anhand
   Befund, C++/EEL2/Tests/Modelldoku gemeinsam.
7. **Transformator-Klangstufe (offen; die Bauentscheidungen sind jetzt getroffen,
   der Code fehlt noch).** Port und Oberfläche stehen. Festgelegt ist:

   - integrierter, **kanalgetrennter** Flux-Zustand nach dem Vorbild von
     `CORE_GC`, an der **Eingangsseite**;
   - **Sättigungsschwelle entschieden:** normierter Flux `u = φ/φ_k` mit
     `u_knee = 1,0`; `φ_k` je Typ aus `φ_k = (C·ω/a)^(1/(n-1))` am geometrischen
     Bandmittel — 0,532 (`60s`), 0,337 (`80s`), 0,368 (`00s`). Ein gemeinsamer
     Wert statt vier absoluter, weil die Modelle nur 1,58 auseinanderliegen
     und die Reststreuung die Sättigungshärte der Bauarten ausmacht. Herleitung
     und Tabelle in `DSP_ARCHITECTURE.md` Abschnitt 11;
   - die **Kopplungs-Bassabsenkung entsteht aus dem gemeinsamen Kern** und wird
     **nicht** als eigener Regler exponiert;
   - die `flux`-/`Lowpass`-Färbung in `Colour` bleibt **unverändert**;
   - Latenz unverändert 0/3/4 Frames.

   Danach zwingend: Parität C++/EEL2, Dwarf-CPU-Messung und Hörtest, weil
   `ABS(v)^n` bis `n = 13` eine `pow`-Funktion je Wicklung und Sample verlangt
   und die Integrationsregel bei dieser Steilheit erst erprobt werden muss.
8. **Route 3 (Kennlinien-LUT) bleibt zurückgestellt.** Die in
   `docs/LUT_REFERENCE.md` geforderte Vorstudie ist abgeschlossen und gegen den
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
   `CPU_ANALYSIS.md` 5b). Sie zeigen **keinen CPU-Engpass**, der eine LUT
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
