# Übergabe an den Agenten auf dem Testrechner

## Einstieg

**Es liegt implementierter Code vor, kein bloßer Plan.**

Aktuell **0.2.0** mit auswählbarem Oversampling (Off/2x/4x, Default Off) und
bitgleicher C++/EEL2-Parität über die gesamte Rate-/OS-Matrix; die Vorher/
Nachher-Werte der 0.1.1-CPU-Optimierung stehen in `CPU_ANALYSIS.md`. Bitte
REAPER-/Dwarf-CPUvergleich mit dieser Fassung, insbesondere OS 2x/4x gegen Off.

1. `AGENTS.md` und `docs/STATUS.md` lesen.
2. SHA256 der übergebenen Archive/Binaries prüfen.
3. `README.md`, `USER_MANUAL.md`, `TESTING.md` lesen.
4. Reales Dwarf-/REAPER-Protokoll mit `TEST_REPORT_TEMPLATE.md` führen.
5. Neue externe Messdaten: `PLUGIN_DOCTOR_EVALUATION.md` lesen. Alle sieben
   ReaJS-/PluginDoctor-Mono-Versuche sind ausgewertet; hohe Delta-Anregung bei
   aktiver GR oder Sättigung nicht als isolierten linearen Filterfrequenzgang
   beurteilen. Besonders Colour-only-Drive und Alias-/Zeitprüfpunkte beachten.

## Vorhandene Artefakte

- `jsfx/GreenStripe76-Mono.jsfx`, `...-Stereo.jsfx` plus vier Includes.
- Zwei `.rpl`-Instrumentbänke, 26 Presets je Variante.
- Native Bundle `build/native/green-stripe-76.lv2` für den Buildrechner.
- AArch64-/Cortex-A35-Bundle `build/aarch64-gcc9/green-stripe-76.lv2`.
- `dist/*-jsfx.zip`, `*-source.zip`, `*-moddwarf.tar.gz`, Herkunftsmanifest,
  SHA256SUMS nach finaler Paketierung.
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
- REAPER beide JSFX inklusive Imports/RPL laden, Routing/Meter/Preset-Recall.
- Kernel/OS/Rate/Frames und Pluginhash notieren.
- Input-Gate/Output-Kompressor des Dwarf für Vergleich abschalten.

### P1 — Realtime und Signal

- Mono, Stereo Link, Dual Mono, Gegenphase, ungleiche Kanäle.
- 128/256 Frames, reale Kette, Peak CPU und xruns über fünf Minuten.
- Regler-/Link-/Bypass-/Compressionwechsel, Snapshots/MIDI/Automation.
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

Details/Versionen in `STATUS.md`: Native Build, CMake/CTest, Signal-/LV2-ABI,
Blockgrößen/In-place, 152 JSFX-Paritätsfälle, 52 Presets, echte GFX-Kompilation/
Render, Turtle-Parsing, AArch64-Symbolfloor, NAM-Dateiinventar.
Zusätzlich CPU-Benchmark und 80 Vorher/Nachher-Burstregressionen.

## Noch nicht belegt

Kein echtes Dwarf-Laden, keine Geräte-CPU-/xrun-Messung, keine reale REAPER-
Host-GR-/Font-/Automation-/Recall-Abnahme, kein Originalhardware- oder
NAM-Core-Färbungsfit. Diese Punkte nach tatsächlicher Ausführung aktualisieren.

## Änderungshinweise

- Quelle aller generierten Dateien: `data/*.json` und `tools/generate.py`.
- Bei eigenem Compilerwechsel neuen BUILD_DIR nutzen.
- Keine originale Elternverzeichnis-Datei überschreiben, keine unklar
  lizenzierten Profile mit Distributionspaketen mitgeben.
- Source-/Runtime-APIs in `PARAMETERS.md`, physikalische versus provisorische
  Annahmen in `DSP_ARCHITECTURE.md`.
- Ohne Commitauftrag nichts committen/pushen. Der initiale Repozustand hat noch
  keine Commits gehabt; inzwischen liegen Implementierungs- und Messdaten-
  Commits vor. Aktuellen Gitstatus vor Weiterarbeit prüfen.
