# Prüfworkflow und Abnahme

## 1. Prinzip

Messung, musikalische Bewertung und Plattformkompatibilität getrennt protokollieren.
Ein erfolgreicher Native-/Paritätstest ist kein Dwarf-CPU- oder Hardwareklangtest.
Aufnahmepegel, Rate, Blocksize, Pluginhash und Parameter immer zusammen notieren.

## 2. Automatisierte lokale Prüfungen

```bash
make test
python3 tools/check_abi.py build/native/green-stripe-76.lv2/green-stripe-76.so
```

`dsp_tests.cpp` prüft:

- Statische Sinus-Sekantenratios im sauberen Pfad.
- Einheitlicher Identitätsgain, interner Bypass und Mix=0.
- Output-unabhängige GR-Trajektorie.
- Dual-Mono-Kanalunabhängigkeit und Link für gegenphasige Signale.
- Stille/Reset, NaN/Inf und extreme Gains/All bei 44,1/48/96 kHz.
- Padé-Symmetrie, Begrenzung und passende analytische Ableitung.

`test_lv2.py` lädt **das gebaute LV2-Binary** über ctypes und prüft:

- Descriptoren und out-of-range-Index.
- Aktivierung und `run(0)` mit gültiger Latenzausgabe; ab 0.2.0 meldet der
  Latenzport 0 (OS Off), 3 (2x) bzw. 4 (4x) Frames und folgt einer
  Oversampling-Umschaltung im laufenden Stream.
- Samplegenau gleiche Ausgabe bei 1/64/128/256/511 Frames, mit OS Off/2x/4x.
- In-place Stereo/Mono ohne Datenüberschreiben.
- Nichtendliche Inputs/Controls ergeben endliche Audioausgabe.
- Mid-Stream-OS-Umschaltung (0→4x und 4x→0) blockinvariant bei 64/128/256/512
  Frames; die Umschaltung blendet über die Länge `ceil(0.002·Rate)` aus und ein.

`validate.py` prüft generierte Metadaten, alle Presetbereiche, Portlayout, Includes
und GUI-Assets. Mit rdflib zusätzlich Turtle-Syntax. Lilv/MOD-SDK weiterhin als
externen **semantischen** Metadatencheck benutzen.

## 3. JSFX-Parität

Siehe Buildbefehle in `BUILD.md`. Pinned ysfx-Fork mit echter EEL2-JIT-Ausführung.

- Mono/Stereo × 44,1/48/96 kHz × 1/64/128/256 Frames × fünf Ratios = 120 Fälle.
- Dazu transparente/BYPASS-Impulse = vier Fälle.
- Regler-/Linkänderung im laufenden Stream und NaN/Inf: zehn weitere Fälle,
  zunächst **134**. Ab 0.1.1 zusätzlich 18 lange Link-/Compression-/Enabled-/
  Colourwechsel-Fälle, zusammen **152**.
- Ab 0.2.0 zusätzlich 72 OS-Fälle (Off/2x/4x × Rate × 64/128 Frames × Ratios
  4:1/12:1/All) und 8 Mid-Stream-OS-Umschaltungen (0→4x, 4x→0), zusammen **232**.
- Double-Kern, float Ports, initial kein Fast-Math/FMA.
- Peak-Abweichung höchstens **2×10⁻⁶ FS** pro Kanal; ab 0.2.0 wird **max=0 FS**
  (bitgleiche Float-Ausgabe) über alle 232 Fälle erreicht.
- Alle 52 RPL-Presets gegen die eingebauten Selektorwerte abgleichen.
- Manuelle Änderung setzt den Selector auf Custom.

**Bindende Implementierungsregel (0.2.0):** Alle transzendentalen Ausdrücke,
die in beide Engines gehören, sind als `seriesLog`/`seriesExp` bzw.
`gs_series_log`/`gs_series_exp` mit **zeilenweise identischer
Operationsreihenfolge** umgesetzt (`src/dsp/GreenStripe.hpp` ↔
`jsfx/GreenStripe76-Core.jsfx-inc`). Hintergrund: EEL2-JIT-`exp`/`log`/`pow`
und libm unterscheiden um ULPs; im Feedback-Solver kippt eine ULP-Differenz
die Newton-/Bisektionsentscheidung und erzeugt hörbare Pfadunterschiede
(gemessen 5.9×10⁻⁴ FS bei 96 kHz/2x/12:1). Attack-/Release-Zeiten und
Koeffizienten werden deshalb nur noch über diese Kernel berechnet;
`std::pow`/`std::exp`/`std::log`/EEL2-`^`/`exp`/`log` sind im DSP-Pfad
verboten. Jede Änderung an den Kerneln braucht den vollständigen
Paritätssatz plus Vorher/Nachher (`cpu_regression`).

ysfx hat `slider_next_chg` nur als Stub und kennt REAPER-Host-GR nicht vollständig.
Diese Prüfung deckt deshalb keine samplegenaue REAPER-Automation ab.

GFX-Test mit `tests/jsfx_ui.cpp` (ysfx-GFX-Build): echte Offscreen-Grafik erzeugen,
mehrfach zeichnen und prüfen, dass der Control-Loop-Zustand identisch bleibt.
Der lokale Host hat gegebenenfalls nur Bitmapfonts. REAPER-HIDPI/Fonts extern prüfen.

### CPU- und Vorher/Nachher-Regressionsprüfung

`benchmark_jsfx` im Test-CMake mitgebaut: identische Vektoren, 48k/128 Frames,
Warmup, Median aus mehreren Durchläufen, GFX/Compile getrennt.
`tools/profile_jsfx_copy.py` erzeugt eine separate instrumentierte Kopie für
Controller-/Target-/Iterationscounts; deren Timings nicht mit normalem Code
vergleichen. `tools/compare_cpu.py` kombiniert zwei normale Runs mit Sourcehashes.

`tests/cpu_regression.cpp` kann mit `GS76_REFERENCE_HEADER` gegen eine
unabhängig gespeicherte vorherige C++-Fassung laufen. 80 Burstfälle bei
8/44,1/48/96k und Modes/Colour/Kanälen; stationäre Audio-/GR-Trajektorien
vergleichen. Neue Übergangstests in `tests/transitions.cpp` prüfen Link-
Zustandsübernahme und Parken. Details/Ergebnisse in `CPU_ANALYSIS.md`.

## 4. Reproduzierbare Signaldateien

```bash
python3 tools/make_probes.py test-results/probes --rate 48000
python3 tools/render_lv2.py \
  build/native/green-stripe-76.lv2/green-stripe-76.so \
  test-results/probes/short-long-bursts.wav test-results/bursts-output.wav \
  --mono --preset 3 --set colour=0
```

Renderer liest PCM16/24/32 und schreibt IEEE-float-WAV, ohne Normalisierung oder
Samplealignment. Mono nimmt linken Kanal. Capture von float WAVE als Eingang
zunächst in REAPER zu PCM konvertieren. Nicht versehentlich Dwarf-AArch64-Binary
im x86_64-Python laden.

Acht Probearten: Stille, Impuls, Pegelstufen, kurzer/langer Burst, Bassburst,
Stereo-Ungleichgewicht, Gegenphase, deterministisches Rauschen. Zusätzlich eigene
Musiksignale als **ungesehene** Testquellen nehmen.

## 5. REAPER-7-Abnahme auf dem anderen Rechner

1. Beide JSFX inklusive `.rpl`/Includes laden, Fehlerkonsole prüfen.
2. Monoquelle nur rechts einspeisen: Mono muss nach dokumentierter Zuordnung
   Input L benötigen; Stereo bearbeitet R normal.
3. Stille, 1-kHz-Sinus −21 dBFS Peak, Bassburst und Drumtransienten abspielen.
4. Input-Meter vor Input, Output-Meter nach Mix, GR vor Mix kontrollieren.
5. Mit 0 dBFS-Peak-Sinus sollten RMS ungefähr −3,01 dBFS und Peak 0 dBFS sein.
6. Link On: lauteren linken Kanal erzeugen; R erhält dieselbe GR. Gegenphase
   darf Kompression nicht abschalten. Link Off: unabhängige GR.
7. GUI geschlossen/geöffnet: identisch rendern/nullen; Farben/Skalierung prüfen.
8. Presetbanken importieren, alle Gruppen wählen, manuelle Änderung → Custom.
9. Projekt speichern/restarten: Parameter und keine überraschende Neuanwendung.
10. Enabled, Compression und Mix unterscheiden; Levelmatching mit Bypass.
11. Große Regler-/Linkwechsel und Automation: keine Knackser/Runaways.
12. Native Rate 44,1/48/96 kHz, Block 64/128/256/1024, Offline-Render/Freeze.
13. `ext_gr_meter` in REAPER-7-Hostanzeige mit eigener GR vergleichen.
14. Verbrauch CPU je Mono/Stereo aufzeichnen, keine Tests mit bloßem Screenshot
    als komplette Audioabnahme melden.

## 6. Dwarf-Abnahme

1. Bundlehash und ELF-ABI überprüfen; bevorzugt MPB-Zweitbuild anlegen.
2. SDK-Installation: Rückgabe `ok`, beide Pluginvarianten sichtbar.
3. Ports und GUI-Knobs/Ratio/Compression/Link ohne Meter prüfen.
4. Audioinput-Gates und Output-Kompressor ausschalten, Gain-Staging dokumentieren.
5. Mono→Mono, Stereo→Stereo, Nullsignal, Gegenphase und ungleiche Pegel prüfen.
6. Hardwarezuweisung, Preset/Snapshot, MIDI-/Encoderänderungen und Bypass prüfen.
7. 128/256 Frames, mehrere Instanzen, reales Pedalboard. Peak CPU und xruns
   über mindestens fünf Minuten je Szenario notieren.
8. Bufferwechsel, Plugin-Neuladen, Reboot und Snapshot-Recall.
9. Externen parallelen Zweig versus internen Mix vergleichen; PDC nicht annehmen.
10. Gegen REAPER-renderte Referenz hören; Unterschiede nicht durch Pegel kaschieren.

## 7. Klang-/Modellkalibrierung

### PluginDoctor: Delta ist mit aktiver GR kein isolierter Frequenzgang

Die Auswertung von `evaluation_plugindoc` steht in
`PLUGIN_DOCTOR_EVALUATION.md`. Ein hoher Deltaimpuls durch einen arbeitenden
Kompressor verändert seine eigene GR-Historie und damit die FFT der Antwort.
Audiopfad-Frequenzmessungen zuerst bei Compression Off und niedrigem Pegel,
den arbeitenden Kompressor über Fundamental-Sweeps und Burst-Zeitverläufe prüfen.
Die `Dynamics`-Ramp misst Input→Output, nicht Attack/Release.

Reproduzierbare Auswertung der Originaldaten:

```bash
make measurement-probe
python3 tools/analyze_plugindoctor.py \
  --probe build/native/measurement_probe \
  --output docs/PLUGIN_DOCTOR_EVALUATION.json
```

Pythonanalyse benötigt nur stdlib für Kennlinien/Harmonic-Peakwerte; mit numpy
zusätzlich IR-FFT-Vergleich und die optionale native Gegenprobe. Der native
Diagnoseprozessor unterstützt Versuch 1–6 und die zwei Linear-only-Fälle von
Versuch 7, fehlende IRs werden nicht ergänzt/erfunden. Die Option `tone` erlaubt
eingeschwungene kohärente Sinusvergleiche; Delta/Pegel und Normalisierung stehen
im Bericht.

Aus Versuch 4–7 abgeleitete nächste Prüfungen:

- Colour only bei **niedrigen** Delta-/Sinuspegeln und gleichem Input/Output-
  Summengain: feste Filterfärbung vom saturierenden hohen Drive unterscheiden.
- Oberhalb des Knies genügend Punkte für 20:1 sammeln (Versuch 6 ist fast
  vollständig unkomprimiert).
- Attack/Release-Zeitdaten exportieren (Versuch 7 hat Hz-x-Achse).
- Gefaltete/zusätzliche Spektrallinien bei starkem Drive und schneller GR
  separat von direktem H2…H8-THD ausweisen. Gegen höhere Verarbeitung-/Hostraten
  messen; gleiche physische Zeitparameter und eindeutige Bezugsgains behalten.

### Messplan

- **Statische Kennlinien:** alle Ratios, Input sweeps, identische Outputwerte,
  ausreichend Einschwingzeit. GR immer gegen Compression-Off-Referenz bestimmen.
- **Attack:** Carrier-/Multitone-Burst mit mehreren Pegelsprüngen, Definition
  der Hüllkurvenmessung nennen. 1-kHz-Peakpicking kann 20 µs nicht auflösen.
- **Release:** kurze versus lange Vorbelastung, Stille versus leiser Carrier,
  unterschiedliche GR-Tiefen und Tempo.
- **Nichtlinearität:** mehrere Frequenzen/Levels, H2/H3/THD, IMD, Polarität,
  Colour/Compression getrennt.
- **Aliasing:** 4× gegen höhere Offline-Rate/Referenz und Nyquist-nahe Töne,
  Filterstopband nicht mit gesamtem Nonlinear-Aliasfloor verwechseln.
- **NAM:** nur mit dokumentierter Modellrate/Headwahl; Core-Renderer verifizieren,
  keine Output/Input-RMS-Schätzung als echte GR interpretieren.
- **Hören:** pegelgleiche A/B mit Stimme, Bass, Guitar, Piano, Drums;
  mehrere Stücke/Spielweisen/ungesehene Einstellungen.

## 8. Akzeptanz und offene Kriterien

Lokale deterministische Tests/Parität sind harte Gates. Gerät darf nicht crashen,
dropouten oder unendlich/non-finite werden. Musikalische Nähe und Originalgeräte-
Fehlergrenzen sind erst nach brauchbarer Referenz gemeinsam zu definieren.
Die aktuelle hohe-Ratio-Abweichung ist offen dokumentiert; bei musikalischer
Unzufriedenheit dynamische Kennlinie verbessern und beide Implementierungen
erneut prüfen, nicht nur die Testgrenzen lockern.
