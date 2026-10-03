# Entwicklungsstand und Übergabe

Stand **2026-10-03**, Projekt **0.1.0**. Code und Dokumentation sind umgesetzt.
Dies ist keine bloße Planungsantwort. Benutzerziel: eigener **Green Stripe**,
Hardware-Revision A/D nicht mehr bindend.

## 1. Implementiert

- Frameworkfreier C++11-DSP und identischer EEL2-Kern.
- 4×-Polyphasen-IIR-Verarbeitung von Audiopfad **und** Feedback-Regelung.
- Nichtlinearer FET-Divider, impliziter begrenzter Regler, programabhängige
  Erholung, All Buttons, asymmetrische Färbung und Output nach Detektor.
- LV2-Mono-/Stereo-Deskriptoren in einem Bundle, Enabled/Compression/Mix/Colour,
  optionaler Link, separate Kanal-/Controllerzustände, keine Meterports.
- Original-Green-Stripe-MOD-GUI mit Knobs/Schaltern, Ports und Illustrations-PNGs.
- JSFX Mono/Stereo mit GR/Peak/RMS/Hold/Clip und Host-GR-Meldung für REAPER 7.
- 26 Instrumentpresets, zwei `.rpl`-Bänke, eingebauter Selector und Custom-Erkennung.
- Native Make/CMake-Builds, offizielles MPB-Skript/Rezept, zusätzlicher AArch64-
  Cross-Build, Archiv-/Hash-/ABI-Werkzeuge.
- Proben-/Offline-WAV-Renderer, NAM-Inventar und vollständige Markdown-Doku.
- `AGENTS.md` und `HANDOFF.md` für andere Session/Testrechner.

## 2. Tatsächlich ausgeführte Prüfungen

| Prüfung | Stand / Ergebnis |
|---|---|
| Native GNU15 Build | PASS, C++11, Warnflags, no-fast-math/FP-contract off |
| `make test` | PASS nach letzter Divideroptimierung |
| Native Signaltests | PASS: Gain, Bypass/Mix, Ratios, Output/GR, Link/Dual-Mono, Gegenphase, Extremwerte, Reset, KCL-Residual |
| Actual LV2 ABI | PASS: beide Deskriptoren, run(0), in-place, block 1/64/128/256/511 bei 44,1/48/96k |
| CMake/CTest | PASS: unabhängiger Buildweg und Signaltest |
| CMake-ysfx-Testintegration | PASS: gepinnter Host als Unterprojekt inkl. SHA512-Prüfung, 134 Renderfälle |
| Generierte Textdateien | PASS, 15 Artefakte check-generated |
| Turtle/RDF | PASS mit rdflib 7.6.0, alle Bundle-TTL |
| Presetbereiche/Assets/Includes | PASS: 26 Presets, beide Varianten |
| EEL2-Compile | PASS mit gepinntem ysfx, einschließlich tatsächlicher GFX-Sektion |
| Audio-C++/JSFX-Parität | **PASS: 134 Fälle**, größte float-Port-Abweichung **4,17233×10⁻⁷ FS** |
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

### Native Durchsatzmessung

`make benchmark`, x86_64/WSL-Session, 48k, 1 Sekunde Ton, Colour=100, Input=6:
nach rationalisierter Dividerlösung etwa **0,058–0,066 s Mono** und
**0,136 s Stereo** pro Audiosekunde. Nur lokaler Durchsatz, **keine Dwarf-CPU-Aussage**.
Frühere per-Tap-Newton-Fassung kostete deutlich mehr; geschlossene Lösung
verifiziert über KCL-Residual und Parität.

## 3. Binäridentität dieses Stands

| Datei | Bytes | SHA256 |
|---|---:|---|
| `build/native/green-stripe-76.lv2/green-stripe-76.so` | 37240 | `415a20fefd6e5573ccf0b69710432c493bbe6135a063195cee20b67e51212b1b` |
| `build/aarch64-gcc9/green-stripe-76.lv2/green-stripe-76.so` | 27616 | `5417191ada1c2c59bdeb448b62f44077bd52e53d021cf2d8addd72f21dc40e81` |

Bei erneutem Build können Pfad/Toolchain/Metadaten Binärhash verändern. Maßgeblich
für die transferierten Archive ist deren mitgelieferter Herkunftsmanifest und
`dist/SHA256SUMS`.

## 4. Noch nicht ausgeführt

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
- 4-Sample-PDC nominal, IIR-Phase frequenzabhängig. Internes Mix/Bypass matched,
  externes paralleles Routing muss getestet werden.
- Alle drei Stereo-Controller laufen warm: Umschaltqualität gegen CPU prüfen.
- `slider_next_chg` nicht genutzt; derzeit geglättete Block-/Slidersteuerung.
- JSFX Mono nimmt linken Eingang auf beide Ausgangspins; keine automatische Summe.
- Kein Lookahead, kein garantierter True-Peak-/Brickwall-Limiter.
- NAM-Profilrate A1 unbekannt, Positionsdaten fehlen; nicht als reiner statischer
  Shaper oder kompletter steuerbarer Kompressor behauptet.
- Capturegewichte/WAVs nicht in Distribution.

## 6. Nächste konkrete Arbeit

1. Pakete/Hashes auf Testrechner übernehmen, `HANDOFF.md` abarbeiten.
2. Dwarf SDK-Install und REAPER JSFX-/RPL-Install.
3. Erst Routing/Link/Bypass/Recall, dann Realtime und pegelgleiche Musik.
4. MPB-Zweitbuild erzeugen und Herkunft festhalten.
5. Ergebnisse mit `TEST_REPORT_TEMPLATE.md`; gezielte Änderungen nur anhand
   Befund, C++/EEL2/Tests/Modelldoku gemeinsam.

## 7. Git / Originaldateien

Initiales Repository hatte keine Commits. Die neuen Projektdateien sind untracked;
es wurde kein Commit/Push/PR angelegt. `build/` und `dist/` sind absichtlich
ignoriert. Elternverzeichnis-Originale wurden nicht verändert.
