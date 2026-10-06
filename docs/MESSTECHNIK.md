# Green Stripe 76 — Prüfungen und Messplätze

Testumfang, Protokollvorlage, Dwarf-Lastmessung, Scarlett-Workflow und Messarchive.

**Konsolidiert am 2026-10-06** aus den bisherigen Einzeldokumenten; Inhalt inhaltlich unverändert, Pfadangaben auf die neue Struktur angepasst.

## Inhalt

1. TESTING.md — *(Quelle: TESTING.md)*
2. TEST_REPORT_TEMPLATE.md — *(Quelle: TEST_REPORT_TEMPLATE.md)*
3. DWARF_LOADTEST.md — *(Quelle: DWARF_LOADTEST.md)*
4. DWARF_RESULTS.md — *(Quelle: DWARF_RESULTS.md)*
5. SCARLETT_TEST.md — *(Quelle: SCARLETT_TEST.md)*
6. SCARLETT_HOWTO.md — *(Quelle: SCARLETT_HOWTO.md)*
7. SCARLETT_COMPREHENSIVE_REPORT.md — *(Quelle: SCARLETT_COMPREHENSIVE_REPORT.md)*
8. scarlett-archive/SCARLETT_RESULTS_TF60S.md — *(Quelle: scarlett-archive/SCARLETT_RESULTS_TF60S.md)*
9. scarlett-archive/SCARLETT_SAFE_COMMANDS.md — *(Quelle: scarlett-archive/SCARLETT_SAFE_COMMANDS.md)*
10. scarlett-archive/SCARLETT_STEREO.md — *(Quelle: scarlett-archive/SCARLETT_STEREO.md)*
11. scarlett-archive/SCARLETT_STEREO_CMDS.md — *(Quelle: scarlett-archive/SCARLETT_STEREO_CMDS.md)*
12. scarlett-archive/SCARLETT_SYNC_GAIN_MAX.md — *(Quelle: scarlett-archive/SCARLETT_SYNC_GAIN_MAX.md)*
13. scarlett-archive/SCARLETT_SYNC_NOTE.md — *(Quelle: scarlett-archive/SCARLETT_SYNC_NOTE.md)*
14. scarlett-archive/SCARLETT_SYNC_QUICK_CMD.md — *(Quelle: scarlett-archive/SCARLETT_SYNC_QUICK_CMD.md)*
15. scarlett-archive/SCARLETT_SYNC_RESULT.md — *(Quelle: scarlett-archive/SCARLETT_SYNC_RESULT.md)*
16. scarlett-archive/SCARLETT_SYNC_TROUBLESHOOTING.md — *(Quelle: scarlett-archive/SCARLETT_SYNC_TROUBLESHOOTING.md)*
17. scarlett-archive/SCARLETT_TRANSFORMER_MATRIX.md — *(Quelle: scarlett-archive/SCARLETT_TRANSFORMER_MATRIX.md)*
18. scarlett-archive/SCARLETT_TRANSFORMER_TEMPLATE.md — *(Quelle: scarlett-archive/SCARLETT_TRANSFORMER_TEMPLATE.md)*
19. scarlett-archive/SCARLETT_WINDOWS_NOTES.md — *(Quelle: scarlett-archive/SCARLETT_WINDOWS_NOTES.md)*
20. PluginDoctor-Sweep am Dwarf (ohne FX) 2026-10-06 — *(Neu; Rohdaten `PluginDoctor messen/scarlett/`)*
21. Automatisierte Transformator-Matrix (`tools/scarlett_matrix.py`) — *(Neu 2026-10-06)*


---

<!-- ===== Teil 1: Quelle docs/TESTING.md ===== -->

# Prüfworkflow und Abnahme

## 1. Prinzip

Messung, musikalische Bewertung und Plattformkompatibilität getrennt protokollieren.
Ein erfolgreicher Native-/Paritätstest ist kein Dwarf-CPU- oder Hardwareklangtest.
Aufnahmepegel, Rate, Blocksize, Pluginhash und Parameter immer zusammen notieren.

## 2. Automatisierte lokale Prüfungen

Aktueller Stand **0.4.1**. Historische Fallzahlen unten bleiben der
Entwicklung zugeordnet; maßgeblich sind jetzt **430 Paritätsfälle / 76
Presetzustände**, ergänzt um Transformator- und MOD-Widget-Prüfungen.

```bash
make test
python3 tools/check_abi.py build/native/green-stripe-76.lv2/green-stripe-76.so
```

`tests/dsp_tests.cpp` prüft:

- Statische Sinus-Sekantenratios im sauberen Pfad.
- Einheitlicher Identitätsgain, interner Bypass und Mix=0.
- Output-unabhängige GR-Trajektorie.
- Dual-Mono-Kanalunabhängigkeit und Link für gegenphasige Signale.
- Stille/Reset, NaN/Inf und extreme Gains/All bei 44,1/48/96 kHz.
- Padé-Symmetrie, Begrenzung und passende analytische Ableitung.

`tests/test_lv2.py` lädt **das gebaute LV2-Binary** über ctypes und prüft:

- Descriptoren und out-of-range-Index.
- Aktivierung und `run(0)` mit gültiger Latenzausgabe; ab 0.2.0 meldet der
  Latenzport 0 (OS Off), 3 (2x) bzw. 4 (4x) Frames und folgt einer
  Oversampling-Umschaltung im laufenden Stream.
- Samplegenau gleiche Ausgabe bei 1/64/128/256/511 Frames, mit OS Off/2x/4x.
- In-place Stereo/Mono ohne Datenüberschreiben.
- Nichtendliche Inputs/Controls ergeben endliche Audioausgabe.
- Mid-Stream-OS-Umschaltung (0→4x und 4x→0) blockinvariant bei 64/128/256/512
  Frames; die Umschaltung blendet über die Länge `ceil(0.002·Rate)` aus und ein.

`transformer/offline_fit/validate.py` prüft generierte Metadaten, alle Presetbereiche, Portlayout, Includes
und GUI-Assets. Mit rdflib zusätzlich Turtle-Syntax. Lilv/MOD-SDK weiterhin als
externen **semantischen** Metadatencheck benutzen.

`tests/transformer_tests.cpp` prüft kausale 20-Hz-Anker, Stille nach Belastung,
Polarität, Kanaltrennung, Output/GR, Dry/Bypass, schnelle Modellwechsel und
Hochfeldbetrieb bei extremen Gains. `tests/test_transformer_model.py` lehnt ungültige
Refit-Banken ab. `tests/test_lv2.py` verbindet zusätzlich den tatsächlichen
Transformatorport und prüft Modellauswahl sowie blockinvariante Wechsel bei
allen OS-Stufen. Die alte optionale Nichtverbindung bleibt geprüft.

### Unabhängiger Transformatorvergleich (NumPy)

```bash
make build/native/transformer_probe.so
c++ -std=c++11 -O3 -fPIC -shared -fno-fast-math -ffp-contract=off \
  docs/transformer/offline_fit/core.cpp -o /tmp/opencode/transformer-reference.so
python3 tests/test_transformer_reference.py \
  --runtime build/native/transformer_probe.so \
  --reference /tmp/opencode/transformer-reference.so
```

Vergleicht Bass-/DC-/Burstverläufe mit dem unabhängigen Offlinekern und echte
gerenderte HF-Antworten mit dem analogen Surrogat. Letzter Lauf: rohe
Abweichung ≤5,42×10⁻¹⁵ FS, HF-Amplitude ≤0,3081 dB; Phase bis 67,91° abweichend.
Dies ist kein Analogphasengleichheits- oder vollständiger Aliasnachweis.

`tests/none_regression.cpp` lässt sich mit
`-DGS76_REFERENCE_HEADER='"/pfad/alter/src/dsp/GreenStripe.hpp"'` gegen einen
separat exportierten 0.3.0-Kern bauen. Tatsächlich geprüft gegen `77a25fd`:
144 Fälle bitgleich, sechs Ratios × drei OS × vier Raten × zwei Varianten,
einschließlich Output-/Link-/OS-/Compression-/Enabled-Wechseln.
Nach der Preset-29-Nennerkorrektur erneut gegen den 0.4.0-Stand `c3153bf`
ausgeführt: ebenfalls 144 Fälle bitgleich; der Test unterstützt nun auch
Referenzheader mit Transformatorbank.

### MOD-GUI-Browsertest und Vorschau

Entwicklungsabhängigkeiten: Playwright, Chromium, Pillow; externe MOD-UI-Quelle:
`mod-audio/mod-ui`, geprüft bei `7a35aac69781af28997aee7e560a92da7146f318`.
Auf dem Dwarf OS 1.13.5.3315 liegt die installierte UI bei
`/usr/share/mod/html/js/modgui.js`, SHA256
`4f516eda640b654fc4c0e204c74e7323cb9541835f5c5ad9e8fb627ace3b2e3e`; Zeile 1250
bindet `element.find('[mod-role=drag-handle]')` — eine Sammlung **aller**
Handle-Elemente — als jQuery-UI-Handle. Mehrere Drag-Handles (oberer Rand,
Fußzeilenplatte, unterer Rand) sind damit am Gerät wirksam.

```bash
python3 tests/test_modgui.py --mod-ui /pfad/mod-ui
python3 tools/make_assets.py
```

Beide akzeptieren `--browser /pfad/chromium`. Der Test lädt die **echten**
MOD-Widgets und jQuery-UI-Draglogik aus dem Checkout: Mode 1→0→1, Filmstrip
mit 65 Frames, endliche Controlwerte, Knopfziehen ohne Paneelbewegung,
separater Drag-Rand, Bypass/Lampe, spaltfreie Paneele und rahmenloser Titel.
Gemessen mit Chromium 153.0.8010.12; Geräte-/Firmwaretest bleibt zusätzlich nötig.

### Vollständige Presetprüfung

```bash
make build/native/preset_probe
python3 tools/audit_presets.py --probe build/native/preset_probe \
  --output docs/PRESET_AUDIT.json
```

76 LV2-/RPL-Zustände gegen normative Parameterwerte; 228 native Fälle
(38 Presets × Mono/Stereo × Off/2x/4x) mit definiertem Multiton-Burst.
Weitere 12 Fälle vergleichen die 2:1-Vorschläge für Piano Gentle und Stereo
Bus Subtle bei drei Sinuspegeln mit 4:1. Endliche Signale und GR-Off geprüft;
Ziel-GR und musikalische Eignung werden nicht aus beliebigem Testpegel bestätigt.
Jeder Fall startet frisch. Bedingungen, Quellenhashes und Kennwerte im JSON,
Bewertung aller Presets in `EXTERN.md`.

### Transformator-Lastwerkzeuge (offline prüfbar)

```bash
python3 tools/dwarf_loadtest.py --self-test
python3 tests/test_dwarf_loadtest.py
make transformer-bench
```

`tests/diag_macro_parity.cpp` wird zweimal gebaut, mit und ohne
`-DGS76_TRANSFORMER_STATS`, und `make test` vergleicht beide Ausgaben mit `cmp`:
60 Fälle über fünf Transformatoren, drei OS-Stufen, Mono/Stereo und
Mid-Stream-Wechsel müssen **byteidentisch** sein. Damit ist der Diagnosezähler
nachweislich audioneutral und kein Messfehler in CPU-Läufen.

`tests/test_dwarf_loadtest.py` läuft in `make test` mit und prüft die
`/proc`-Auswertung ohne Gerät: `comm` mit Leerzeichen und Klammern,
Prozentstatistik gegen gelesenen `CLK_TCK`, Instanzzählung aus den `r-xp`
Mappings, unlesbare Binaries, xrun-Differenz zählt nur das Messfenster und
Anhängen an einen Bericht mit Schemaprüfung. Der Selbsttest von
`tools/dwarf_loadtest.py` nutzt eine synthetische Fixture ohne echten jackd.
`transformer_bench` ist ein reines Zeitmesswerkzeug über die Produktheader;
es prüft keine Klang- oder Echtzeiteigenschaft. Anleitung und Geräteprotokoll
in `MESSTECHNIK.md`.

### Scarlett-Testtonwerkzeug

```bash
python -m pip install -r tools/requirements-scarlett.txt
python tests/test_scarlett_test.py
```

Offlineprüfungen: definierter Gain/Delay, Polarität, 1-%-H2, DC, Taktabweichung,
analytischer FIR-Frequenzgang, Clipping, fehlende/falsche/verkürzte Aufnahme,
Referenzvalidierung; simulierter Backend für Routing und Streamfehler/Stop.
Geräteliste, Liveaufnahme und Kalibrierung gemäß `MESSTECHNIK.md` extern.
Hardware-GR oder Pluginlatenz nicht aus Gesamtpfad-Pegel/Verzögerung behaupten.

## 3. JSFX-Parität

Siehe Buildbefehle in `BETRIEB.md`. Pinned ysfx-Fork mit echter EEL2-JIT-Ausführung.

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
- Historisch 52/72, aktuell 76 RPL-Presetzustände gegen die eingebauten Selektorwerte abgleichen.
- Ab 0.4.0: sechs Ratios im Basissatz, 144 zusätzliche statische
  Transformatorfälle (vier Profile × drei OS × drei Raten × zwei Varianten ×
  zwei Betriebspunkte) und 30 Transformator-/OS-/Bypass-/NaN-/Modellwechsel-Fälle.
  Insgesamt **430** allgemeine Audiofälle; ab 0.4.1 **76** Presetzustände aus 38 Presets je Variante.
- Manuelle Änderung setzt den Selector auf Custom.
- Zusätzlich zu den 430 allgemeinen Fällen rendert der reale ysfx-Banklader
  alle **76 Presetzustände mit Signal** gegen einen frischen C++-Prozessor;
  der Recall-Abgleich mit Selector/Custom bleibt erhalten.
  Hierdurch wurde der All-Buttons-Randfall von Preset 29 erkannt und die
  EEL2-Auswertungsreihenfolge des Newton-Nenners korrigiert. Die Abnahmegrenze
  wurde nicht gelockert; aktuell alle 506 Signalvergleiche erreichen max. 0 FS.

**Bindende Implementierungsregel (0.2.0):** Alle transzendentalen Ausdrücke,
die in beide Engines gehören, sind als `seriesLog`/`seriesExp` bzw.
`gs_series_log`/`gs_series_exp` mit **zeilenweise identischer
Operationsreihenfolge** umgesetzt (`src/dsp/GreenStripe.hpp` ↔
`jsfx/GreenStripe76-Numeric.jsfx-inc`). Hintergrund: EEL2-JIT-`exp`/`log`/`pow`
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
Zustandsübernahme und Parken. Details/Ergebnisse in `PERFORMANCE.md`.

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
   über mindestens fünf Minuten je Szenario notieren. Für die Board-Serie
   `GS76x0…GS76x4` und die isolierten Transformatorkosten das Protokoll in
   `MESSTECHNIK.md` verwenden: `tools/dwarf_loadtest.py` je Bedingung nach
   **vollständigem** Neustart, `tools/transformer_bench.cpp` ohne Bedienung.
   Ohne Binärhash und Board/Transformator/OS/Block/Pegelangabe gilt keine Zahl
   als Gerätemessung.
8. Bufferwechsel, Plugin-Neuladen, Reboot und Snapshot-Recall.
9. Externen parallelen Zweig versus internen Mix vergleichen; PDC nicht annehmen.
10. Gegen REAPER-renderte Referenz hören; Unterschiede nicht durch Pegel kaschieren.

## 7. Klang-/Modellkalibrierung

### PluginDoctor: Delta ist mit aktiver GR kein isolierter Frequenzgang

Die Auswertung von `evaluation_plugindoc` steht in
`EXTERN.md`. Ein hoher Deltaimpuls durch einen arbeitenden
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


---

<!-- ===== Teil 2: Quelle docs/TEST_REPORT_TEMPLATE.md ===== -->

# Prüfbericht — Green Stripe 76

Datum / Agent / Rechner:

## Artefakte

- Projektversion/Commit oder Source-ZIP-Hash:
- LV2-Binärhash:
- Toolchain / Image-Digest / Compileflags:
- JSFX-/RPL-Stand:
- Transformatorbankrevision / SHA256 (`data/transformers.json`):
- Architektur und benötigte GLIBC-/GLIBCXX-Versionen:

## Umgebung

- Dwarf OS / Kernel / Machine:
- REAPER-Version / OS / Audiointerface:
- Rate / Blocksize / Jack-Puffer:
- Dwarf Input-Gain / Output-Gain:
- Eingebaute Gate-/Kompressor-Funktionen ausgeschaltet?:
- Peak/RMS→Volt/dBu-Kalibrierung falls vorhanden:

## Ausgeführte Prüfungen

| Test | Variante/Parameter | Ergebnis | Beleg/Datei |
|---|---|---|---|
| Native make test | | | |
| ysfx Parität | | | |
| TTL/Lilv/SDK | | | |
| Geräte-Laden | | | |
| Mono-/Stereo-Routing | | | |
| Link / Dual Mono / Gegenphase | | | |
| Compression Off / Enabled / Mix | | | |
| Presets und Projekt-Recall | | | |
| Alle 38 Presets: Input-Abgleich / Wet-GR / pegelgleiche Musik | | | |
| Attackkorrektur 21/22 und 2:1-Paare 31/37 sowie 35/38 | | | |
| Scarlett 2i2: direkte Referenz / Teststrecke / Streamstatus / Pegelkalibrierung | | | |
| Meter / Host-GR | | | |
| GUI offen/geschlossen | | | |
| Regler-/Automationswechsel | | | |
| Transformator None/60s/80s/00s/Symmetric, OS Off/2x/4x | | | |
| Modellwechsel / None-Recall / sechs Transformatorpresets | | | |
| MOD Mode / Knopf ohne Paneelbewegung / Drag-Rand / SVG-Lampe | | | |
| 128 Frames / 256 Frames | | | |
| 5-Minuten-CPU/xruns | | | |
| 0.1.0/0.1.1 CPUvergleich, identische Rate/Blöcke/Quelle | | | |
| Parken/Wiedereinschalten und Link-Zustandsübernahme | | | |
| Mehrere Instanzen | | | |
| Frequenz-/Kennlinienproben | | | |
| Kurzer/langer Burst | | | |
| NAM-Core-Vergleich | | | |
| Musikalischer A/B | | | |

## CPU

Vergleichsplugins/Versionen/Qualitätseinstellungen benennen. GUI geschlossen/
geöffnet getrennt messen. Lokale ysfx-Benchmarks sind kein REAPER-/Dwarf-
CPU-Prozentwert; Vorher und Nachher im gleichen Setup vergleichen.

| Szenario | Rate/Frames | Peak CPU | mittlere CPU | xruns / Dauer |
|---|---|---|---|---|
| Mono allein | | | | |
| Stereo Link | | | | |
| Stereo Dual Mono | | | | |
| reales Pedalboard | | | | |

## Hörbewertung

- Testinstrument / Spielweise / Pegel:
- Preset / vollständige Reglerwerte:
- Levelmatching-Methode:
- Transienten / Body / Release / Färbung:
- Gewünschte Änderung:
- Referenzgerät/-plugin/-NAM (inkl. Rate und Capture-/Knopfbedingungen):

## Fehler

Reproduktionsschritte, erwartetes/tatsächliches Verhalten, Log, Audiodateien:

## Übergabe

- Bestanden:
- Nicht ausgeführt:
- Blocker:
- Nächste Änderung und passende Wiederholungsprüfungen:
- `docs/PROJEKT.md` aktualisiert:


---

<!-- ===== Teil 3: Quelle docs/DWARF_LOADTEST.md ===== -->

# Dwarf-Lasttest — Anleitung und Messprotokoll (Produkt 0.4.1)

Zwei Werkzeuge, zwei Aussagen. Beide sind **nur auf dem Dwarf aussagekräftig**;
x86-Läufe sind eine Vorhersage, keine Gerätemessung.

| Werkzeug | Frage | Wer misst |
|---|---|---|
| `tools/dwarf_loadtest.py` | Wie viel Last kostet das **Pedalboard** `GS76x0…GS76x4`? | jackd-Threads auf dem Gerät |
| `tools/transformer_bench.cpp` | Was kostet die **Transformatorstufe** selbst, je Profil und OS-Stufe? | DSP-Kern, direkt auf dem Gerät ausgeführt |

Die Boards stehen laut Vorgabe auf **Transformer None / Oversampling Off**. Für
die reine Frage „wie skaliert eine Instanz" ist das die richtige Einstellung.
Für die Frage „ist der Transformator teuer" reicht diese Serie **nicht** aus:
`None` überspringt die Transformatorrechnung vollständig. Diese Frage beantwortet
Serie B (`transformer_bench`), weil sie die Transformatorstufe ohne Bedienung
über das Pedalboard durchrechnet.

## Serie A — Pedalboard-Last, GS76x0 bis GS76x4

Voraussetzung vor dem ersten Lauf:

1. Bundle **0.4.x mit Transformatorstufe** installiert, Pluginname in der
   Oberfläche sichtbar. Ein Bundle vor 0.4.0 misst einen anderen Kern.
2. SHA256 der installierten Binary notieren und bei jedem Lauf prüfen:

   ```bash
   sha256sum /root/.lv2/green-stripe-76.lv2/green-stripe-76.so
   ```

   Ohne diesen Schritt ist eine Zahl nicht zuordenbar — in Serie 5b wurde
   während eines Durchgangs unbemerkt eine ältere Binary durch eine
   UI-Installation ersetzt und die Messung musste verworfen werden.
3. Board-Blockgröße auf **128** bzw. **256** Frames stellen und notieren.
4. Input-Gate/Output-Kompressor des Dwarf für den Vergleich ausschalten.

Pro Bedingung ein **vollständiger Gerätestart**. `systemctl restart jack2`
genügt nicht: die Hardware-Controlchain übernimmt das Pedalboard aus
`/root/data/last.json` erst beim Vollstart.

```bash
# Board GS76x0 laden, neu starten, dann messen (ein Aufruf je Bedingung)
python3 tools/dwarf_loadtest.py --label GS76x0 --frames 128 \
    --seconds 20 --expect-instances 0 \
    --report dwarf-load.json --markdown dwarf-load.md
```

`--expect-instances` ist die **gemessene** Anzahl gemappter `r-xp`-Segmente
der Plugin-`so`, nicht die Board-Beschriftung. Passt sie nicht, warnt das
Werkzeug, statt eine Zahl zu liefern, die zu einem anderen Board gehört.
Optional `--expect-sha256 <hex>` prüft die Binary zusätzlich.

Nach **jedem** Board: Board `GS76x1`, `GS76x2`, `GS76x3`, `GS76x4` laden,
neu starten, gleicher Aufruf mit passendem `--label`/`--expect-instances`.
Danach dieselbe Serie mit `--frames 256`. Die Datei `dwarf-load.json` wird
je Aufruf um eine Bedingung ergänzt; `--markdown` schreibt die Tabelle neu.

### Was das Werkzeug misst und was nicht

- **Prozesslast:** jackd `utime+stime` gegen gelesenen `SC_CLK_TCK`, 40 Samples
  je 20 s, Abstand 0,5 s; berichtet Mittel, Median, Spitze. Prozent **eines**
  Kerns, jackd inklusive — direkt vergleichbar mit Serie 5b.
- **Threadlast:** alle Threads des jackd-Prozesses, gerankt. Der schwerste
  Thread ist in der Regel der Audio-Thread; das trennt die DSP-Last von
  Logging, Controlchain und Web-UI.
- **Instanzzahl und Binary** aus `/proc/<pid>/maps`.
- **xruns:** Anzahl der Zeilen mit `xrun` in `dmesg` und im Kernel-Journal vor
  und nach dem Fenster; die Differenz ist der Befund im Messfenster. Fehlt der
  Zugang (kein `root`, kein Journal), steht das als `available: false` im
  Bericht — **keine** xrun-Aussage ohne Eintrag im Fenster.

Grenzen: keine Latenzmessung, kein Hörtest, keine REAPER-Aussage. xruns ohne
Gegenstelle bleiben eine Indizienlage; die Plugin-Host-API antwortet auf dem
Gerät nicht (Serie 5b).

Bekannte Schwäche: Linux kann identische Textmappings derselben `so` zusammenlegen.
Die Zahl der `r-xp`-Segmente ist deshalb eine **gemessene** Größe und kann von
der Anzahl echter Instanzen abweichen. Stimmt sie nicht mit dem Board überein,
ist das Ergebnis nicht zu verwenden; dann über den JACK-Graph oder den
MOD-State gegenprüfen und `--expect-instances` weglassen. Der Bericht nennt die
gemesene Zahl in jedem Fall, damit das nachvollziehbar bleibt.

## Serie B — Transformatorstufe ohne Bedienung

Baut den Produktkern (`-Isrc`, unveränderte Header) als eigenständiges
Programm und rechnet direkt auf dem Gerät. Kein jackd, kein Pedalboard, keine
GUI — dadurch sind Profil, OS-Stufe, Kanalzahl und Instanzzahl exakt
einstellbar.

```bash
# Im MPB-Container (siehe BETRIEB.md) oder mit dem Arm-GCC9-Crosscompiler
make BUILD_DIR=build/moddwarf transformer-bench

# Auf dem Dwarf ausführen; Werte in Prozent eines Kerns
./build/moddwarf/transformer_bench \
    --transformer 0,1,2,3 --oversampling 0,1,2 --channels 1,2 \
    --instances 1 --repeats 3 --seconds 3 --level-dbfs 0 \
    --json dwarf-transformer.json --markdown dwarf-transformer.md
```

Wichtige Optionen:

- `--transformer 0,1,2,3,4` — None, 60s, 80s, 00s, Symmetric.
- `--oversampling 0,1,2` — Off, 2x, 4x.
- `--channels 1` Stereo, `--channels 2` Mono. Beachten: der Mono-Deskriptor
  nimmt im Plugin beide Kanäle, der Kern rechnet dann einen Kanal.
- `--instances 1,2,4` — Linearitätsprüfung im selben Prozess.
- `--level-dbfs` — **der** Pegelparameter: die Solveriterationen und damit die
  Last steigen mit dem Pegel. Ohne diese Angabe ist eine Zahl nicht
  übertragbar.
- `--input-db`, `--ratio`, `--attack`, `--colour` — Reglerzustand mitprotokollieren.

Der Lauf gibt mittlere Solveriterationen je Probe und den Anteil der Proben am
40er-Limit aus. Das ist die eigentliche Kostenursache: `None` läuft nie in den
Solver, ein Modell mit etwa zwei bis drei Iterationen, ein Signal mit hohem
Pegel mehr.

Der Standalone-Bench umgeht LV2-Wrapper und jackd. Für die **gesamte**
Kettenlast bleibt Serie A maßgeblich; Serie B ist die zerlegte Komponentenmessung.

## Was als Ergebnis gelten darf

- Nur eine Zahl mit Gerät, Build, Compiler, Blockgröße, Board, Transformator-,
  OS-, Kanal- und Pegelangabe sowie Binary-Hash.
- „Auf dem Dwarf gemessen" nur mit Gerätemessung; ein x86-Bench ist eine
  Hochrechnung.
- „Echtzeitfähig" erst mit xruns über mehrere Minuten je Zustand.
- Nichts davon ist eine Hör- oder Klangabnahme.

Ergebnisse nach `docs/PERFORMANCE.md` Abschnitt 5c, Abweichungen der
Vorhersage bitte dort eintragen statt die Vorhersage zu ersetzen.

## Offline-Prüfung beider Werkzeuge

```bash
python3 tools/dwarf_loadtest.py --self-test
python3 tests/test_dwarf_loadtest.py
make transformer-bench
```

`make test` baut zusätzlich dieselbe Quelle zweimal, mit und ohne
`-DGS76_TRANSFORMER_STATS`, und vergleicht die Ausgaben: der Diagnosezähler
darf den Audiowert nicht verändern.

`tests/test_dwarf_loadtest.py` prüft die `/proc`-Auswertung (inklusive `comm`
mit Leerzeichen und Klammern), die Prozentstatistik, die Instanzzählung, den
xrun-Differenzzähler, unlesbare Binaries und das Anhängen an einen Bericht.
Der Selbsttest braucht kein Gerät.


---

<!-- ===== Teil 4: Quelle docs/DWARF_RESULTS.md ===== -->

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


---

<!-- ===== Teil 5: Quelle docs/SCARLETT_TEST.md ===== -->

# Scarlett-Test — Messprotokoll, Verkabelung und Auswertungsgrenzen

Dieses Dokument beschreibt den analog-loopbasierten Plugin-Messworkflow mit der
Scarlett 2i2 (1st Gen) und dem MOD Dwarf. Werkzeug: `tools/scarlett_test.py`
(`devices`, `generate`, `run`, `analyze`), optionale Python-Abhängigkeiten in
`tools/requirements-scarlett.txt`. Kurzbefehle: [SCARLETT_HOWTO](MESSTECHNIK.md),
erster ausgedruckter Messbericht: [SCARLETT_COMPREHENSIVE_REPORT](MESSTECHNIK.md),
historische Einzelschritte im Archiv `scarlett-archive/`.

**Grenzen:** Offline- und simulierte Backendtests sind keine Prüfung des realen
Focusrite-Treibers oder der analogen Wandler. Das Werkzeug misst den
**Gesamtpfad**; keine Kalibrierung in Volt/dBu, keine Hardwaregleichheit, keine
interne FET-GR- oder Hörabnahme.

## 1. Verkabelung und Baseline-Varianten

Verkabelung der Teststrecke (so wurde die Messung vom 2026-10-05 ausgeführt):

- Scarlett Out1/2 → Dwarf In1/2 (unsymmetrisch),
- Dwarf Out1/2 → Scarlett In1/2 (symmetrisch),
- Direct Monitor OFF, 48 V OFF, INST/LINE korrekt, 48 kHz.

Es gibt zwei sinnvolle Baseline-Varianten; beide sind gültig, aber sie beantworten
verschiedene Fragen:

| Baseline | Pfad | Beantwortet |
|---|---|---|
| **Dwarf mit GS76-Bypass** | Scarlett → Dwarf → Scarlett, Plugin überbrückt | Plugin-Effekt gegen die **identische** Geräte-/Verkabelungsstrecke (so die Läufe vom 2026-10-05, Label „Direkt“ dort = „unbearbeitet durch den Dwarf“) |
| Direktes Kabel Out→In | Scarlett-Loop ohne Dwarf | Zustand der Scarlett-Loop allein; Dwarf-Pfad bleibt Teil der Differenz |

Regeln:

1. Baseline und DUT müssen **denselben physischen Pfad** benutzen; nur dann
   hebt sich die Geräteantwort in `relative_gain_db` heraus.
2. Regler am Scarlett und am Dwarf zwischen Baseline und DUT nicht verändern.
3. Der Sync-Verzögerungsunterschied `delay_at_first_marker_frames` (DUT minus
   Baseline) ist ein kostenloser Plausibilitätscheck: Bei OS 4x soll er der
   nominalen Plugin-Latenz von **4 Frames** entsprechen (gemessen: +3,2…+4,5).
   Bei OS Off/2x entsprechend 0/3.

## 2. Systemvoraussetzungen (Windows, nativ)

- Python nativ (nicht WSL): `python -m pip install -r tools/requirements-scarlett.txt`.
- **Windows-Sounddialog:** Wiedergabe- und Aufnahmegerät des Focusrite
  ausdrücklich auf **48 kHz / 24 bit** setzen und „Signalverbesserungen“/EQ
  deaktivieren. Andernfalls resampelt der Windows-Mixer; die Metadatai
  (`recording.json`, Feld `default_samplerate`) zeigte beim Lauf 2026-10-05
  **44100 Hz** — solche Läufe haben Instabilität nahe Nyquist gezeigt (Abschnitt 5).
- MME ist auf diesem Setup mit stabiler Synchronisation erprobt: In 1/2
  (`Analogue 1 + 2`), Out 6/7 (`Lautsprecher`); Device-IDs mit
  `python tools\scarlett_test.py devices` gegenlesen (Historie:
  `MESSTECHNIK.md`).
- `run` verlangt für Input und Output dieselbe Host-API; der Output-Kanal und
  der analysierte Input-Kanal werden getrennt gewählt (`--output-channel`,
  `--input-channel`).

## 3. Pegel- und SNR-Vorschrift

Der Lauf 2026-10-05 hatte eine Loop-Verstärkung von **−63 dB** (Aufnahme
−78 dBFS RMS bei −12 dBFS Anregung, Leerlaufrauschen −95,2/−95,4 dBFS). Folgen:
SNR nur 5–17 dB, THD/THD+N wurde Rauschen, die Pegelreihe bei −36/−30 dBFS lag
am/unter dem Rauschboden. Deshalb gilt ab sofort:

1. **Ziel:** Aufnahmepeak im Tone-Segment ≥ −24 dBFS; Loop-Gewinn ≥ −20 dB.
   `analyze` schreibt `level_check` in `results.json` und markiert in
   `REPORT.md` mit „ÜBERSCHRIETTEN“, wenn der Loop-Gewinn zu niedrig ist.
   Solche Läufe für Klirr-/SNR-Aussagen nicht verwenden.
2. Loop-Pegel anheben über: Windows-App-Volume der Playback-Quelle 100 %,
   Scarlett-Monitor/Output-Pegel hoch, Dwarf-Eingangspegel moderat; Clipping
   (Proben ≥ 0,999) macht Segmente ungültig.
3. **Kalibrierebene für die Profile:** Im Bypass-Run ist die Rückkanal-Ebene
   näherungsweise die Ebene am Plugin-Eingang. Erste Stufe stimmt Pegel so, dass
   der Bypass-Return bei 1 kHz im Zielbereich liegt; dann erreicht man die
   Profilanker (−14/−8/−2 dBFS am Plugin-Eingang) über den **Input-Regler**
   (0…+24 dB), nicht über den Stimulus allein. Der Ausgabeweg wird im Bypass
   mitgemessen; die Rückrechnung auf dBu ist ohne Volt-Kalibrierung nicht zulässig.
4. Jeder Bericht muss den Loop-Gewinn (Tone-Segment) mit angeben.

## 4. Standardablauf

```cmd
cd C:\Users\Sidney\Desktop\GreenStripe\mod-1175-lv2
python tools\scarlett_test.py devices
python tools\scarlett_test.py run --output test-results\scarlett-ref-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --label "<Baseline-Variante, OS, Kabel>"
python tools\scarlett_test.py run --output test-results\gs76-tf60s-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch1\results.json --label "TF60s; Comp Off; Mix100; Colour0; OS4x"
```

- Je Kanal eigene Baseline (Kabel/Kanal wechseln), Label enthält Transformer,
  Comp, Mix, Colour, OS, Link, Ratio, Attack/Release.
- `analyze` kann getrennt laufen (`--session`, `--recording`, `--baseline`,
  `--report-dir`); die Baseline darf nicht mit ihrem eigenen `--report-dir`
  überschrieben werden.
- **Wiederholungen:** Je Bedingung ≥ 3 Läufe, Median der relativen Werte und
  Spreizung berichten. Einzelläufe sind bei diesem Loop im oberen Band
  nicht belastbar (Abschnitt 5).
- **Stabilitätsvorablauf:** Zwei Baseline-Läufe (oder ch1 gegen ch2) definieren
  die Untergrenze. Erst wenn diese unter der erwarteten Plugin-Differenz liegt,
  sind Transformer-/OS-Vergleiche trennscharf.
- **20 kHz:** bei 48 kHz zu nah an Nyquist; Bandkanten mit
  `--rate 96000` messen (20 kHz liegt dort weit unter Nyquist).

## 5. Interpretationsgrenzen

Aus dem Lauf 2026-10-05 belegte Grenzen (Details und Zahlen im
[Comprehensive Report](MESSTECHNIK.md), Abschnitt 9):

- **THD/THD+N:** Enthalten DAC-, ADC- und Testpfad; Baseline wird nicht
  subtrahiert. Bei Loop-Gewinn −63 dB ist THD+N (~15 %) Rauschen; die
  „H2“-Linien lagen unter dem Leerlaufrauschen. Erst ab Loop-Gewinn ≥ −20 dB
  sind Klirrwerte Plugin-nahe Aussagen.
- **Sweep-Spaltierung:** Selbst Baseline↔Baseline (identische Physik) zeigte
  ±0,18 dB bei 1 kHz, ±1 dB bei 2–4 kHz und ±2,6 dB bei 20 kHz. Die erwarteten
  Profilunterschiede (Modell: max. ~0,6 dB bei 16 kHz) liegen darunter —
  Einzellauf-Spalten ab ~2 kHz sind daher nicht trennscharf.
- **Pegelreihe:** −36/−30-dBFS-Segmente lagen am/unter dem Rauschboden; nur
  −24…−12 sind auswertbar.
- **Keine Attribuierung ohne Gegenprobe:** Mid-Band-Differenzen von ~−0,3 dB
  sind innerhalb der Instabilität; ein Offline-Render des Plugins (OS 4x,
  None-Transformer) ist exakt 0,0000 dB gegen Bypass — gemessene Abweichungen
  in dieser Größenordnung sind also Messketten-, nicht Plugin-Effekte.

## 6. Provenienz und Ablage

- `test-results/` ist **git-ignored**; Rohdaten bleiben lokal. Berichte müssen
  deshalb die relevanten Zahlen **samt** Synchronisations-/Pegel-/Hashwerten
  enthalten; `results.json` führt `stimulus_sha256`, `recording_sha256`,
  `plan_sha256`, `script_sha256`, `baseline_sha256`.
- Label und `recording.json` sind die einzige Parameterdokumentation der
  Gerätebedienung — vollständig ausfüllen (auch Transformer und OS des
  Baseline-Boards).
- `analyze` verknüpft `stream_status` nur mit dem exakt passenden
  `recording_sha256`; ein fehlerhafter Stream macht den Lauf ungültig.


---

<!-- ===== Teil 6: Quelle docs/SCARLETT_HOWTO.md ===== -->

# Scarlett-Test – Kurzanleitung

Vollständiges Protokoll, Pegel-/SNR-Vorschrift und Auswertungsgrenzen:
[SCARLETT_TEST](MESSTECHNIK.md). Erster ausgedruckter Bericht:
[SCARLETT_COMPREHENSIVE_REPORT](MESSTECHNIK.md).

## 1. Setup (Windows, nativ)
- Scarlett 2i2 1st Gen, 48 kHz (Windows-Sounddialog: Wiedergabe **und** Aufnahme
  auf 48 kHz/24 bit, „Signalverbesserungen“ aus), Direct Monitor OFF, 48V OFF,
  INST/LINE korrekt
- Teststrecke: Out1/2 → Dwarf In1/2 (unsymmetrisch), Dwarf Out1/2 → Scarlett In1/2 (symmetrisch)
- Baseline: **Dwarf mit GS76-Bypass** (misst das Plugin gegen die identische
  Strecke); alternativ direktes Kabel Out→In für die Scarlett-Loop allein
- MME empfohlen (stabile Sync): Input 1/2, Output 6/7 (IDs mit
  `python tools\scarlett_test.py devices` gegenlesen; Historie im Archiv
  `MESSTECHNIK.md`)

## 2. Schnellstart
```cmd
cd C:\Users\Sidney\Desktop\GreenStripe\mod-1175-lv2
python tools\scarlett_test.py devices
```

## 3. Typischer Ablauf (Stereo)
1. Ch1 Referenz: `--kind all --level -12 --rate 48000 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1`
2. Ch2 Referenz: entsprechend Kanal 2
3. Dwarf-Teststrecke mit `--baseline` je Kanal, Label mit Parametern (TF, Comp, Mix, OS, Link)

## 4. Pflichtprüfungen vor Auswertung
- `REPORT.md`: Loop-Gewinn ≥ −20 dB („OK“) und kein Geräteraten-Mismatch;
  andernfalls Pegel/Rate korrigieren und wiederholen (siehe MESSTECHNIK.md Abschnitt 3).
- Sync-Differenz DUT minus Baseline ≈ nominale Plugin-Latenz (0/3/4 Frames).
- Pro Bedingung ≥ 3 Läufe; Median und Spreizung berichten.


---

<!-- ===== Teil 7: Quelle docs/SCARLETT_COMPREHENSIVE_REPORT.md ===== -->

# Umfassender Scarlett-Testbericht: GS76 Transformer-Stereo

## 1. Zusammenfassung
- Messmethode: Analog-Loop Scarlett 2i2 (MME 1/6 Ch1, 2/7 Ch2), Level -12 dBFS, `--kind all`, 48 kHz
- Baseline getrennt je Kanal (direktes Kabel Out1→In1 / Out2→In2)
- Teststrecke: Scarlett Out1/2 → Dwarf In1/2 (unsymmetrisch), Dwarf Out1/2 → Scarlett In1/2 (symmetrisch)
- Einstellungen GS76: Comp Off, Colour 0%, Mix 100%, Input/Output 0 dB, OS 4x, Stereo, Link DualMono (dokumentiert)
- Transformervarianten: TF60s, TF80s, TF00s, TFSym (Stereo)

## 2. 1 kHz - Übersicht (relativ zur Kabelreferenz, Gain relativ dB)
| Messung | rel. Gain (dB) | THD % | THD+N % | gültig |
|---|---:|---:|---:|---|
| TF00s Ch1 | -0.291 | 3.468 | 15.606 | True |
| TF00s Ch2 | -0.203 | 3.237 | 15.382 | True |
| TF80s Ch1 | -0.228 | 3.457 | 15.195 | True |
| TF80s Ch2 | -0.282 | 3.296 | 15.592 | True |
| TFSym Ch1 | -0.261 | 3.340 | 15.212 | True |
| TFSym Ch2 | -0.256 | 3.364 | 15.490 | True |
| TF60s Ch1 | -0.055 | 3.268 | 14.834 | True |
| TF60s Ch2 | -0.269 | 3.337 | 15.592 | True |

## 3. Frequenzgang (Sweep) - rel. Gain dB je Transformer
| Transformer | Ch | 20 | 40 | 80 | 160 | 315 | 630 | 1000 | 2000 | 4000 | 8000 | 12000 | 16000 | 20000 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TF00s Ch1 | -0.024 | -0.006 | -0.011 | -0.050 | -0.166 | -0.374 | -0.259 | -0.459 | -0.594 | -0.531 | -0.601 | -0.085 | -3.752 |
| TF00s Ch2 | -0.012 | +0.001 | -0.002 | +0.009 | -0.038 | -0.139 | -0.229 | +0.043 | +0.306 | +0.105 | -0.272 | -1.059 | +1.124 |
| TF80s Ch1 | -0.025 | -0.005 | -0.003 | -0.006 | -0.059 | -0.302 | -0.231 | -0.412 | -0.583 | -0.548 | -0.547 | +0.001 | -3.729 |
| TF80s Ch2 | -0.021 | +0.003 | -0.003 | +0.001 | -0.049 | -0.170 | -0.211 | -0.010 | +0.259 | -0.303 | -0.425 | +0.338 | +0.171 |
| TFSym Ch1 | -0.013 | -0.006 | -0.018 | -0.022 | -0.093 | -0.291 | -0.255 | -0.374 | -0.382 | +0.226 | +0.146 | -2.279 | -0.547 |
| TFSym Ch2 | -0.007 | -0.005 | -0.011 | -0.010 | -0.086 | -0.146 | -0.206 | -0.018 | +0.139 | -0.319 | -0.437 | +0.463 | +0.089 |
| TF60s Ch1 | -0.092 | -0.013 | -0.003 | -0.006 | -0.047 | -0.212 | -0.073 | -0.348 | -0.549 | -0.595 | -0.448 | -0.210 | -4.294 |
| TF60s Ch2 | -0.089 | -0.011 | -0.013 | -0.020 | -0.119 | -0.179 | -0.263 | -0.023 | +0.251 | +0.076 | -0.624 | -1.754 | -0.545 |

## 4. Pegelreihe 1 kHz (rel. Gain dB)
| Messung | -36 | -30 | -24 | -18 | -12 |
|---|---|---|---|---|---|
| TF00s Ch1 | -0.299 | -0.394 | -0.224 | -0.243 | -0.176 |
| TF00s Ch2 | -0.514 | -0.444 | -0.257 | -0.184 | -0.249 |
| TF80s Ch1 | -0.341 | -0.235 | -0.287 | -0.264 | -0.223 |
| TF80s Ch2 | -0.258 | -0.329 | -0.247 | -0.181 | -0.258 |
| TFSym Ch1 | -0.320 | -0.262 | -0.265 | -0.324 | -0.294 |
| TFSym Ch2 | -0.329 | -0.328 | -0.231 | -0.185 | -0.253 |
| TF60s Ch1 | -0.222 | -0.217 | -0.147 | -0.234 | -0.191 |
| TF60s Ch2 | -0.562 | -0.400 | -0.260 | -0.243 | -0.292 |

## 5. Analyse & Vergleich
- Ch1 über alle TF sehr nahe Referenz (meist < ±0.3 dB im mittleren Band 40–8k), hoher 20k-Abfall bei TF60s Ch1 (−4.3 dB) fällt auf – Prüfwert, Kanalabhängigkeit möglich.
- TF00s: Ch1 zeigt bei 20k −0.2 dB, Ch2 −2.0 dB (Asymmetrie).
- TF80s: insgesamt relativ ausgeglichen, 20k moderater Abfall.
- TFSym (stereo/symmetrisch): Ch1 weitgehend neutral, Ch2 bei hohen Frequenzen teils positiver/negativer Verlauf.
- Pegelreihe zeigt geringe Abhängigkeit von Eingangspegel (nahe konstant) – Hinweis auf linearen Transfer bei Comp Off.
- THD/THD+N aus Tabellen stabil, keine auffälligen GR-artigen Effekte.

## 6. Rohdaten
- gs76-tf00s-ch1/results.json (TF=TF00s Ch1)
- gs76-tf00s-ch2/results.json (TF=TF00s Ch2)
- gs76-tf80s-ch1/results.json (TF=TF80s Ch1)
- gs76-tf80s-ch2/results.json (TF=TF80s Ch2)
- gs76-tfsym-ch1/results.json (TF=TFSym Ch1)
- gs76-tfsym-ch2/results.json (TF=TFSym Ch2)
- sc-dwarf-st-ch1/results.json (TF=TF60s Ch1)
- sc-dwarf-st-ch2/results.json (TF=TF60s Ch2)
- scarlett-ref-ch1/results.json, scarlett-ref-ch2/results.json, scarlett-tone-mme/results.json

Messdatum: 2026-10-05 (Scarlett-Loop MME, Level -12, kind=all, 48 kHz). Einstellungen GS76 wie dokumentiert.

## 7. THD/THD+N @ 1 kHz (Sweep/Levels relevant)
| Messung | THD% (tone 1k) | THD+N% (tone 1k) |
|---|---:|---:|
| TF00s Ch1 | 3.468 | 15.606 |
| TF00s Ch2 | 3.237 | 15.382 |
| TF80s Ch1 | 3.457 | 15.195 |
| TF80s Ch2 | 3.296 | 15.592 |
| TFSym Ch1 | 3.340 | 15.212 |
| TFSym Ch2 | 3.364 | 15.490 |
| TF60s Ch1 | 3.268 | 14.834 |
| TF60s Ch2 | 3.337 | 15.592 |
## 8. Schlussfolgerung

- Transformerpfade sind bei Comp Off nahezu transparent im mittleren Frequenzband (40–8 kHz) mit relativen Gain-Abweichungen meist < ±0.3 dB.
- Kanalasymmetrien treten vor allem bei hohen Frequenzen (16 k–20 kHz) auf, je nach Transformer unterschiedlich (TF60s Ch1 zeigt ausgeprägteren 20k-Abfall in diesen Messdaten).
- Pegelreihe 1 kHz ist relativ flach – konsistent mit linearem Transfer ohne aktive Kompression.
- THD liegt stabil bei ~3.24–3.47 % @ 1 kHz, THD+N ~14.8–15.6 % (Messpfad-abhängig). Relative Vergleiche sind aussagekräftiger als Absolutwerte.
- Insgesamt weitgehend symmetrisches, transparentes Übertragungsverhalten; HF-Asymmetrien sollten bei Bedarf wiederholt unter identischen Bedingungen verifiziert werden.

Messungen: Scarlett-Loop MME, getrennte Baselines je Kanal, `--kind all`, 48 kHz. Alle Rohdaten unter `test-results/`.

## 9. Nachbetrachtung 2026-10-06 (Analyse; keine neue Messung)

Ergänzende Auswertung der Rohdaten in `test-results/` und ein Offline-Vergleich
des Plugins; Protokollverbesserungen und Folgeaufträge in
[SCARLETT_TEST](MESSTECHNIK.md). Die Abschnitte 1–8 bleiben historisch
stehen; wo sie widersprochen werden, gilt diese Nachbetrachtung.

### 9.1 Baseline klargestellt: Dwarf mit GS76-Bypass

Die Baselines (`scarlett-ref-ch1/ch2`, Label „Direkt“) gingen laut
Betriebsangabe durch den **Dwarf mit überbrücktem GS76**, nicht über ein
direktes Kabel. Die Daten belegen das: Die DUT-Läufe liegen im
Marker-Delay **+3,2…+4,5 Frames** über der Baseline — genau die nominale
Plugin-Latenz bei OS 4x (4 Frames); die absoluten Pegel stimmen ansonsten
überein. Wäre die Baseline ein reines Kabel gewesen, hätte der Dwarf-Graph
(128er-Perioden) weitaus mehr Verzögerung sichtbar gemacht. Damit isolieren
die relativen Werte tatsächlich das **Plugin**, nicht den Dwarf.

### 9.2 Loop-Gewinn −63 dB: THD/THD+N nicht Plugin-tauglich

Bei −12 dBFS Anregung wurde −78 dBFS RMS fundamental aufgenommen
(Loop-Verstärkung ≈ −63 dB, Leerlaufrauschen −95,2/−95,4 dBFS): SNR nur
5–17 dB. Die Kabel-/Bypass-Referenz allein zeigt 2,85 % THD und ~14,8 % THD+N;
die gemeldeten ~3,2–3,5 %/~15 % sind folglich Messpfad-/Rauschartefakte, kein
Plugin-Klirr. Die Pegelreihe −36/−30 dBFS misst Fundamentalwerte von
−100,5/−95,6 dBFS — am/unter dem Rauschboden (THD+N ~195 %). Zudem war der
Signalpegel am Plugin-Eingang damit rund 50 dB unter den Profilankern
(−14/−8/−2 dBFS): Die Profile wurden in dieser Messreihe nicht in ihren
nichtlinearen Bereich gefahren.

### 9.3 Offline-Gegenprobe: Plugin ist flacher als die Messung

Derselbe Stimulus wurde offline durch das echte x86-LV2 gerendert
(Baseline = Bypass/OS Off; DUT = aktiv/OS 4x) und mit demselben Analyzer
ausgewertet:

| Hz | 60s | 80s | 00s | Sym |
|---|---:|---:|---:|---:|
| 20 | −0,050 | −0,019 | −0,012 | −0,002 |
| 1000 | 0,000 | 0,000 | 0,000 | 0,000 |
| 12000 | −0,193 | −0,017 | −0,015 | −0,015 |
| 16000 | −0,582 | −0,053 | −0,028 | −0,028 |
| 20000 | −1,303 | −0,129 | −0,046 | −0,046 |

None/OS 4x gegen Bypass: **0,0000 dB in allen Spalten** — die OS-Kette ist
transparent. Die gemessenen Abweichungen (Tabelle 3 oben) liegen darüber: Bei
1 kHz messen alle DUT-Läufe −0,05…−0,29 dB (Modell: 0 dB), bei 20 kHz −0,5…
−4,3 dB (Modell: −0,05…−1,3 dB) und TF00s Ch2 sogar +1,12 dB — eine
Anhebung gegenüber dem Bypass ist für ein Passivmodell physikalisch
auszuschließen.

### 9.4 Instabilitätsuntergrenze des Messpfads

Vergleich der beiden Baseline-Läufe (identische Physik, verschiedene Kanäle):
±0,18 dB bei 1 kHz, ±0,74/±0,99 dB bei 2/4 kHz, ±0,99 dB bei 12 kHz,
±1,0 dB bei 16 kHz, **±2,56 dB bei 20 kHz**. Die DUT-Kanäle zeigen dieselbe
Größenordnung (z. B. TF00s ch1−ch2: +0,26 dB bei 1 kHz, ±2 dB bei 16/20 kHz).
Die Spalten ab ~2 kHz sind deshalb von Einzelläufen nicht trennscharf; die
beobachteten HF-Muster sind Messketten-Effekte (Kandidaten: Windows-Mixer-
Resampling — `recording.json` zeigte `default_samplerate` 44100 — bzw.
Wandler-Toleranzen), nicht Plugin-Eigenschaften.

### 9.5 Was aus der Reihe trotzdem gilt

- **Latenz:** DUT−Baseline-Delay ≈ nominale Plugin-Latenz bei OS 4x — bestätigt.
- **Mid-Band:** Die relativen Werte widersprechen dem Modell nicht; sie sind
  innerhalb der ±0,2…±0,6-dB-Instabilität mit „nahezu transparent“ verträglich.
  Sie **belegen** die Profilunterschiede nicht (Modell-Differenzen sind kleiner
  als die Instabilität).
- **THD/Frequenzgang-Spalten:** Nicht verwertbar; die Schlussfolgerungen in
  Abschnitt 8 sind mit dieser Einschränkung zu lesen.

### 9.6 Folgeaufträge

1. Loop-Pegel anheben (Windows-Volume/Enhancements, Monitor-Pegel, Dwarf-Eingang):
   Loop-Gewinn ≥ −20 dB; das gehärtete `tools/scarlett_test.py` markiert unzulässige
   Läufe (`level_check`, Warnung bei Geräteraten-Mismatch).
2. Windows-Sounddialog: Geräte auf 48 kHz festlegen; `default_samplerate` in
   `recording.json` prüfen (soll 48000 sein).
3. ≥ 3 Wiederholungen je Bedingung; Median/Spreizung berichten; 20 kHz bei
   96 kHz messen.
4. Bypass-Stabilitätsvorablauf als Trennschärferferenz; danach erst die
   Transformer-Matrix (60s/80s/00s/Sym × Pegelanker) wiederholen.


---

<!-- ===== Teil 8: Quelle docs/scarlett-archive/SCARLETT_RESULTS_TF60S.md ===== -->

# Scarlett-Ergebnisse – TF60s, Stereo (Symmetrisch)

## Setup
- MME: Ch1 In=1 Out=6, Ch2 In=2 Out=7 (entsprechend)
- Level -12 dBFS, `--kind all`, 48 kHz
- GS76 Stereo, TF60s, Comp Off, Colour 0, Mix 100, Input/Output 0, OS4x, Link DualMono (laut Label)
- Baseline: separate Referenzen `scarlett-ref-ch1`, `scarlett-ref-ch2`

## Ausgewählte Werte (relativ zur Kabelreferenz)

| Kanal | 1kHz (tone) rel. Gain dB | THD% @1k | THD+N% @1k | Level -12 rel. Gain dB | THD% @-12 | THD+N% @-12 |
|---|---:|---:|---:|---:|---:|---:|
| Ch1 (TF60s) | -0.055 | 3.27 | 14.83 | -0.191 | 3.40 | 15.34 |
| Ch2 (TF60s) | -0.269 | 3.34 | 15.59 | -0.292 | 3.35 | 15.66 |

## Frequenzgang (Sweep, rel. Gain dB)
| Hz | 20 | 40 | 80 | 160 | 315 | 630 | 1000 | 2000 | 4000 | 8000 | 12000 | 16000 | 20000 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ch1 | -0.092 | -0.013 | -0.0030 | -0.0059 | -0.047 | -0.212 | -0.073 | -0.348 | -0.549 | -0.595 | -0.448 | -0.210 | -4.29 |
| Ch2 | -0.089 | -0.011 | -0.0127 | -0.0203 | -0.119 | -0.179 | -0.263 | -0.023 | +0.251 | +0.076 | -0.624 | -1.75 | -0.545 |

## Pegelreihe (1kHz, rel. Gain dB)
| Peak dBFS | -36 | -30 | -24 | -18 | -12 |
|---:|---:|---:|---:|---:|
| Ch1 | -0.222 | -0.217 | -0.147 | -0.234 | -0.191 |
| Ch2 | -0.562 | -0.400 | -0.260 | -0.243 | -0.292 |

## Auswertung
- Sehr geringe relative Verstimmungsänderung (nahe 0 dB) im mittleren Band – Transformatorpfad nahezu transparent bei TF60s (Stereo, Comp Off).
- Ch2 zeigt leichte Asymmetrie bei sehr tiefen (20–80 Hz) und bei hohen Frequenzen (4k–20k) im Sweep, insgesamt sehr geringfügig.
- THD/THD+N relativ stabil über Kanäle.


---

<!-- ===== Teil 9: Quelle docs/scarlett-archive/SCARLETT_SAFE_COMMANDS.md ===== -->

# Sichere Befehle (Windows-native)

## 1) Tone-Test
Falls Ordner existiert: neuen Namen nehmen (z. B. -2)
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-tone --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -18 --rate 48000 --label "Scarlett 2i2 WASAPI Gain min direkt"
```

## 2) Referenz (direktes Kabel Out1→In1), feste Regler
Vorher Sample Rate 48 kHz am Scarlett/Windows kontrollieren.
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-reference --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind all --level -18 --settle 2 --measure 1 --label "Direktes Kabel, feste Regler"
```

## 3) Dwarf-Strecke
Regler am Scarlett **nicht** verändern.
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-dwarf --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind all --level -18 --settle 2 --measure 1 --baseline test-results\scarlett-reference\results.json --label "Dwarf 48k GS76 dokumentiert"
```


---

<!-- ===== Teil 10: Quelle docs/scarlett-archive/SCARLETT_STEREO.md ===== -->

# Scarlett – Stereo-Messung

## Verkabelung Stereo
- Scarlett Out 1 → Dwarf In 1 (unsymmetrisch)
- Scarlett Out 2 → Dwarf In 2 (unsymmetrisch)
- Dwarf Out 1 → Scarlett In 1 (symmetrisch)
- Dwarf Out 2 → Scarlett In 2 (symmetrisch)

## Skript: Stereo-Loop (beide Kanäle gleichzeitig)
`tools/scarlett_test.py` spielt ausgewählten Ausgang (`--output-channel`) und zeichnet **beide Eingänge** auf. Für Stereo-Teststrecke über Dwarf werden beide Kanäle durchlaufen.

Variante A: Kanal 1 messen, dann Kanal 2 getrennt (mit Baseline je Kanal) oder Kanal 2 mit gleicher Referenz (Loop symmetrisch). Für Stereo Link relevant.

Variante B: Analyse Kanal 2 separat mit `--channel 2`:
```cmd
python tools\scarlett_test.py analyze --directory test-results\scarlett-dwarf-stereo --recording test-results\scarlett-dwarf-stereo\recording.wav --channel 2 --baseline test-results\scarlett-reference-mme\results.json --report-dir test-results\scarlett-dwarf-stereo-ch2
```

Aber besser: jeweils eigenen Lauf pro Kanal oder Dokumentation. Einfacher: Zwei separate Runs (Kanal 1 + Kanal 2) mit identischer Referenz, Label ergänzt "Ch1/Ch2".

## Empfehlung (Stereo, getrennt ausgewertet)
1. Referenz Out1→In1 (Ch1) + optional Out2→In2 Referenz
2. Dwarf Stereo aktiv, Messung Ch1: `--input-channel 1 --output-channel 1`, Label "Stereo, Ch1"
3. Dwarf Stereo aktiv, Messung Ch2: `--input-channel 2 --output-channel 2`, Label "Stereo, Ch2" (gleiche Referenz oder separate)
Mit GS76 Stereo Link beachten (Link beeinflusst Detektion).

## Live-Run Stereo (MME, -12)
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-dwarf-stereo-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-reference-mme\results.json --label "Dwarf 48k; GS76 Stereo; Ch1; Comp dokumentieren..."
```

```cmd
python tools\scarlett_test.py run --output test-results\scarlett-dwarf-stereo-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-reference-mme\results.json --label "Dwarf 48k; GS76 Stereo; Ch2; ..."
```

Hinweis: Referenz für Ch2 ggf. separat erstellen (Out2→In2).


---

<!-- ===== Teil 11: Quelle docs/scarlett-archive/SCARLETT_STEREO_CMDS.md ===== -->

# Scarlett Stereo – Befehle

## Referenzen
### Ch1 Referenz (Out1→In1)
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-ref-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --label "MME Ch1 Direkt"
```

### Ch2 Referenz (Out2→In2)
Kabel umlegen: Out2→In2, dann:
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-ref-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --label "MME Ch2 Direkt"
```

## GS76 Stereo-Teststrecke
GS76 im Dwarf Stereo laden (Link je Test dokumentieren). Verkabelung wie beschrieben.

### Ch1
```cmd
python tools\scarlett_test.py run --output test-results\sc-dwarf-st-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch1\results.json --label "Dwarf GS76 Stereo Ch1; Comp Off; Mix100; Colour0; OS4x; Link DualMono; Ratio 4:1; A7 R7"
```

### Ch2
```cmd
python tools\scarlett_test.py run --output test-results\sc-dwarf-st-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch2\results.json --label "Dwarf GS76 Stereo Ch2; Comp Off; Mix100; Colour0; OS4x; Link DualMono; Ratio 4:1; A7 R7"
```

Für **Stereo Link**: Ch2 kann durch Link beeinflusst sein – unbedingt separat messen und Label "Link On" setzen.


---

<!-- ===== Teil 12: Quelle docs/scarlett-archive/SCARLETT_SYNC_GAIN_MAX.md ===== -->

# Sync-Problem bei maximalem Input-Gain

Szenario: Input-Gain bereits maximal, trotzdem `correlation 0.024–0.027` (Marker zu leise).

## Mögliche Ursachen
- Kabel/Loop invertiert oder ungeeignet (TRS–TS?) – Symmetrie beeinflusst Pegel
- Ausgangspegel Scarlett zu niedrig? (Monitor/Main nicht relevant, Line Out fest)
- Sample-Rate nicht exakt 48 kHz (Treiber)
- Host-API Pufferung (MME vs WASAPI) – WASAPI bevorzugt, teste MME/DirectSound ggf.
- Marker-Chirp wird gedämpft (Gerätepfad)

## Gegenmaßnahmen
1. **Pegel umkehren testen**: `--level -12` statt `-15/-18` (höherer Stimulus)
   ```cmd
   python tools\scarlett_test.py run --output test-results\scarlett-tone-m12 --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -12 --rate 48000 --label "Level -12"
   ```
2. **Andere Host-API**: MME (IDs 1 In, 6 Out) statt WASAPI – manchmal stabiler für Sync
   ```cmd
   python tools\scarlett_test.py run --output test-results\scarlett-tone-mme --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -15 --rate 48000 --label "MME -15"
   ```
3. **Schwelle reduzieren (Debug)**: nur vorübergehend `tools/scarlett_test.py` Zeile ~130 `quality < 0.20` oder `0.15`. Nach erfolgreichem Sync-Test **wieder auf 0.35** zurücksetzen.
4. **Kurzer Check**: Aufnahme in Audacity öffnen – Marker (Chirp) sichtbar/leise?

## Hinweis
Wenn Gain bereits maximal und Marker trotzdem nicht erkannt wird, ist temporäres Absenken der Sync-Schwelle der pragmatischste Weg für diese Hardware-Konfiguration. Skript prüft hauptsächlich für robuste Synchronisation; bei sauberer Aufnahme funktioniert Analyse auch bei niedrigerer Markerqualität.


---

<!-- ===== Teil 13: Quelle docs/scarlett-archive/SCARLETT_SYNC_NOTE.md ===== -->

# Sync-Fehler bei minimalem Input-Gain

Beobachtung (Windows native):
- Input-Gain Scarlett minimal: Marker-Erkennung scheitert (correlation ~0.024–0.027)
- Level -15 ebenfalls zu schwach
- Hinweis: "Input am Interface war mittlerweile schon übersteuert" – Pegelwahl sensibel

Empfehlung:
- Input-Gain **sehr leicht anheben** (nur wenige Grad), bis Signal sauber ankommt, aber kein Clipping. Ziel: -18 dBFS Peak im Rückkanal.
- Falls immer noch < 0.35: temporär Schwelle in `correlation_marker` auf 0.15/0.20 absenken für Debug, dann wieder auf 0.35 für finale Validierung.
- Sicherstellen: direktes Kabel Out1→In1, Direct Monitor aus, keine DAW, 48 kHz.


---

<!-- ===== Teil 14: Quelle docs/scarlett-archive/SCARLETT_SYNC_QUICK_CMD.md ===== -->

# Kurzbefehl für Debug-Schwelle

Temporär in `tools/scarlett_test.py`, Zeile ~130 ändern:
```python
if quality < .15:  # statt .35
```

Dann testen, danach **wieder auf .35** zurücksetzen.

Teste danach z. B.:
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-tone-debug --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -15 --rate 48000 --label "debug sync 0.15"
```


---

<!-- ===== Teil 15: Quelle docs/scarlett-archive/SCARLETT_SYNC_RESULT.md ===== -->

# Scarlett Sync – erfolgreich (MME)

## Ergebnis
Test `test-results/scarlett-tone-mme/`:
- Sync erfolgreich mit MME (Input 1, Output 6), Level -12 dBFS
- Synchronisation: ~247.6 ms Roundtrip, Drift ~0.13 ppm
- Valid: True, Noise ~ -95.2 dBFS
- Gain -62.8 dB (digital → Rückkanal über direktes Kabel) – typisch je Interface/Pegel

## Empfehlung für weitere Messungen
- Verwende **MME** (1 In, 6 Out) statt WASAPI bei diesem Setup (stabilere Marker-Erkennung)
- Level **-12 dBFS** für Marker ausreichend, Referenz/Tests mit gleichen Einstellungen
- Weiter mit Referenz `--kind all` unter MME


---

<!-- ===== Teil 16: Quelle docs/scarlett-archive/SCARLETT_SYNC_TROUBLESHOOTING.md ===== -->

# Scarlett-Test: Sync-Marker-Fehler (correlation < 0.35)

## Fehler
`Measurement failed: No reliable sync marker (correlation 0.024); check routing/level`

## Ursachen
- Verkabelung falsch (Out1 nicht mit In1 verbunden, Loop offen)
- Direct Monitor aktiv
- Monitoring umgeleitet (DAW spielt zurück)
- Pegel zu niedrig (Input-Gain auf Minimum kann Marker zu leise machen)
- Falsche Sample-Rate oder Host-API
- Pufferung/Offset

## Sofortprüfung
1. **Kabel prüfen**: Scarlett Line Out 1 → Scarlett Line In 1 (direktes Kabel, TRS)
2. Scarlett: Direct Monitor **OFF**, 48V **OFF**, INST/LINE korrekt
3. Input-Gain am Scarlett **minimal**, aber versuche kurz **+6 dB** oder Level `-15` statt `-18`
4. Keine DAW geöffnet (die Aufnahme zurückspielt)
5. Windows Sound: Ausgabe nicht umgeleitet

## Test mit höherem Pegel (Marker stärker)
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-tone-15 --input-device 18 --output-device 14 --input-channel 1 --output-channel 1 --kind tone --frequency 1000 --level -15 --rate 48000 --label "Gain -15"
```

## Test mit niedrigerer Correlation-Schwelle (Debug, nur zum Prüfen)
Nur temporär in `tools/scarlett_test.py`, Zeile ~130: `if quality < .15:` statt `.35` – **nicht für endgültige Messungen** verwenden.

## Empfehlung
Meist liegt es an **Input-Gain zu niedrig** bei direktem Loop. Scarlett 1st Gen braucht oft etwas mehr Gain für Marker-Erkennung bei minimaler Stellung. Erhöhe Input-Gain **ganz wenig** (ca. 10–20%) und probiere erneut.


---

<!-- ===== Teil 17: Quelle docs/scarlett-archive/SCARLETT_TRANSFORMER_MATRIX.md ===== -->

# Scarlett – Transformer-Testmatrix

## Getestet
- Transformer: 60s (separat gemessen), jetzt 80s, 00s
- Symmetrisch (Stereo)

## Vorgehen
Je Transformer + Stereo (mit/ohne Link je Bedarf):
1. Ch1 Ref + Ch2 Ref (Out1→In1, Out2→In2), MME 1/6 bzw. 2/7 je Kanal, Level -12, `--kind all`
2. Dwarf Stereo, Transformer gesetzt, Parameter dokumentieren
3. Ch1 + Ch2 Runs mit jeweiliger Baseline

## Befehlsmuster (Ch1/Ch2)
Siehe `MESSTECHNIK.md`. Label immer erweitern um `TF 60s/80s/00s`, `Sym`, `Link ...`

## Parameter (Vorgabe Transfer)
Comp Off, Colour 0, Mix 100, Input/Output 0, OS4x, Stereo Link dokumentieren (DualMono vs Link), Ratio/Attack/Release falls variiert ebenfalls notieren.

## Ergebnisablage
Ordnerstruktur z. B.:
- `test-results/scarlett-ref-ch1/`, `test-results/scarlett-ref-ch2/`
- `test-results/gs76-tf60s-stereo-ch1/`, `-ch2/`
- `test-results/gs76-tf80s-stereo-ch1/`, `-ch2/`
- `test-results/gs76-tf00s-stereo-ch1/`, `-ch2/`

## Notiz
Symmetrisch = Stereo-Modus, ggf. Link-Einfluss prüfen (Ch2 bei Link anders).


---

<!-- ===== Teil 18: Quelle docs/scarlett-archive/SCARLETT_TRANSFORMER_TEMPLATE.md ===== -->

# Transformer-Test – Template

## Einstellungen Dwarf GS76 (Stereo)
- Comp: Off
- Colour: 0% | Mix: 100%
- Input: 0 | Output: 0
- OS: 4x
- Link: DualMono / On (dokumentieren)
- Ratio: 4:1 (oder neutral) – dokumentieren
- Attack/Release: 7/7
- Transformer: TF60s / TF80s / TF00s / None

## Referenzen
Ch1: `test-results/scarlett-ref-ch1/results.json`
Ch2: `test-results/scarlett-ref-ch2/results.json`

## Ch1
```cmd
python tools\scarlett_test.py run --output test-results\gs76-tf<XX>-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch1\results.json --label "MME Dwarf GS76 Stereo Ch1 TF<XX> CompOff Mix100 Col0 OS4x Link<XX> Ratio4 A7 R7"
```

## Ch2
```cmd
python tools\scarlett_test.py run --output test-results\gs76-tf<XX>-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch2\results.json --label "MME Dwarf GS76 Stereo Ch2 TF<XX> CompOff Mix100 Col0 OS4x Link<XX> Ratio4 A7 R7"
```

Ersetze `<XX>` durch 60s/80s/00s und Link durch DualMono/On.


---

<!-- ===== Teil 19: Quelle docs/scarlett-archive/SCARLETT_WINDOWS_NOTES.md ===== -->

# Scarlett-Test unter Windows (Hinweise)

## Device-Liste (deine Ausgabe)
Focusrite erscheint u.a. als:
- Input: `1 Analogue 1 + 2 (Focusrite USB Audio), MME`
- Input: `8 ... DirectSound`
- Input: `18 ... Windows WASAPI`
- Output: `6 Lautsprecher (Focusrite USB Audio), MME`
- Output: `13 ... DirectSound`
- Output: `14 ... Windows WASAPI`

## Empfehlungen
- **WASAPI bevorzugen** (14 Out, 18 In) – stabiler, weniger Pufferprobleme.
- Input/Output **gleiche Host-API** wählen (Script prüft das).
- Sample Rate 48 kHz überall (Host + Treiber).

## Ausführung
Nativ in CMD/PowerShell, nicht WSL. Projektverzeichnis:
```cmd
cd C:\Users\Sidney\Desktop\GreenStripe\mod-1175-lv2
python tools\scarlett_test.py devices
```
(Backslashes oder forward slashes funktionieren in Windows-Python)

<!-- ===== Teil 20: Quelle docs/PluginDoctor messen/scarlett/ (2026-10-06, Neueingang) ===== -->

# PluginDoctor-Sweep am Dwarf (ohne FX) 2026-10-06

Kette: PluginDoctor → Scarlett-Interface (Output 1+2) → MOD Dwarf **ohne FX** →
Scarlett-Interface (Input 1+2) → PluginDoctor. Frequenzgangdaten:
`docs/PluginDoctor messen/scarlett/1.txt`–`5.txt` (je 16 382 Punkte,
2,69 Hz…22 050 Hz — PD lief mit **44,1 kHz**, der Dwarf mit 48 kHz).

## Auswertung (numerisch verifiziert gegen die Rohdateien)

| Datei | LF-Mittel ≤ 250 Hz | tiefstes LF-Minimum | Mitten/Höhen 200 Hz–20 kHz |
|---|---:|---|---|
| 1.txt | +0,26 dB | −7,4 dB bei 51,2 Hz | flach ±0,1 dB |
| 2.txt | +0,38 dB | −6,8 dB bei 29,6 Hz | flach; Nyquist-Kante ab ~21 kHz (−26 dB @ 22,05 kHz) |
| 3.txt | +0,45 dB | −4,0 dB bei 56,5 Hz | flach; Nyquist-Kante wie 2.txt (−22,7 dB) |
| 4.txt | +0,20 dB | −5,3 dB bei 72,7 Hz | flach |
| 5.txt | +0,42 dB | −5,3 dB bei 67,3 Hz | flach |

- **Kein echter Bassfehler:** Der **Mittelwert** der oszillierenden Bassregion
  liegt in allen fünf Läufen bei +0,2…+0,45 dB — die tatsächliche Übertragung
  der Kette ist bis ~20 Hz eben (±1 dB). Was „sehr schlecht“ aussieht, ist die
  **Interferenz-Oszillation** (Minima −2…−7,4 dB, Spitzen +6…+7,3 dB), nicht
  eine Roll-off- oder Pegelcharakteristik.
- **Die Muster sind laufweise verschieden** (Notch-Positionen 13,5/19/29,6/51,1/
  67,3/72,7 Hz je Datei unterschiedlich; scheinbare Verzögerungen ~19,5/31/46 ms).
  Eine physische Frequenzgangantwort wäre reproduzierbar und würde den
  **Mittelwert** verschieben — beides tritt nicht auf. Das Muster ist ein
  **Messartefakt des PD-Sweeps** (Zeit-Frequenz-Verschmierung über die
  Schleifenlatenz bzw. überlagerte verzögerte Kopie), keine Eigenschaft von
  Dwarf, Kabel oder Scarlett.
- **Nyquist-Kante** in 2/3.txt: glatter −3-dB-Übergang ab ~21 kHz — Bandende
  der 44,1-kHz-Einstellung, normal; bei 48 kHz würde sie oberhalb 20 kHz liegen.

## Einordnung gegen die eigen Messreihe

Die marker-synchronisierten Läufe vom 2026-10-05 (Abschnitt Scarlett, Tabelle
oben) messen dieselbe physische Kette: relative Werte 20 Hz–8 kHz innerhalb
±0,3 dB gegen das Offline-Modell, dazu bestätigte 4-Frame-Latenz bei OS 4x.
Beide Datensätze widersprechen sich nicht — der PD-Sweep misst nur ohne
Synchronisation, deshalb zeigt er die Interferenz, die das Tonprotokoll
ausmittelt.

## Folgerungen für künftige PD-Läufe

1. **Latenzkompensation an** bzw. PD-Messmodus mit Tonschritten statt
   fortlaufendem Sweep; Fenster größer als die Schleifenlatenz wählen.
2. Alles auf **48 kHz** stellen (PD lief mit 44,1 kHz — die Kante bei 22,05 kHz
   verkleinert zudem den prüfbaren Bereich).
3. Echopfade ausschließen: Scarlett **Direct Monitor OFF**, Windows „Dieses
   Gerät hören“ aus, Windows-Signalverbesserungen aus.
4. Für Belastbarkeitssätze (Absoluteffekt) bleibt `tools/scarlett_test.py` die
   verlässliche Route (Marker-Sync, Drift-Kompensation, 2 s Settle, 1 s
   Messfenster); PD ist für Sichtprüfung nützlich, aber ohne
   Latenzkompensation für den Bassbereich nicht verwertbar.


---

<!-- ===== Teil 21: Automatisierte Transformator-Matrix (2026-10-06) ===== -->

# Automatisierte Transformator-Matrix — `tools/scarlett_matrix.py`

Treiber über `tools/scarlett_test.py` für die Wiederholungsmessung der
Transformatorprofile (None/60s/80s/00s/Sym) am LV2-Plugin im Dwarf. Start aus
der Windows-CMD; Geräte werden per Autoerkennung gewählt (MME, Name enthält
„Focusrite“), Gerätelisten-IDs können sich ändern — bei Bedarf
`--input-device/--output-device` überschreiben.

```cmd
cd C:\Users\Sidney\Desktop\GreenStripe\mod-1175-lv2
tools\scarlett_matrix.bat devices
tools\scarlett_matrix.bat gainmatch
tools\scarlett_matrix.bat full --repeats 3 --settings-label "Comp Off; Mix100; Colour0; OS4x; Link DualMono; Ratio 4:1; A7 R7"
tools\scarlett_matrix.bat summary --root test-results\matrix-YYYYMMDD-HHMMSS
```

## Ablauf (`full`)

1. **Gainmatch:** je Kanal ein 1-kHz-Ton-Probe (`--level`, Standard −12 dBFS)
   über Out1→In1 bzw. Out2→In2; berichtet Loop-Gewinn je Kanal und die
   Kanaldifferenz (Toleranz ±1 dB). Damit ist der PluginDoctor-Abgleich der
   beiden Dwarf-Input-Gain-Regler ersetzbar und reproduzierbar. Nachstellen
   heißt: beide Dwarf-Input-Gains **gleich** verändern, dann `gainmatch`
   erneut (die Probe überschreibt sich selbst).
2. **Ankerpegel:** der Stimulus-Pegel wird aus dem gemessenen Loop-Gewinn
   abgeleitet: Stimulus = Anker − Loop-Gewinn. Die Pegelreihe (`--kind all`,
   Stufen −24/−18/−12/−6/0 dB relativ zum Stimulus-Pegel) trifft dann die
   Anker −14/−8/−2 dBFS am Plugin-Eingang. Bedingung:
   **Loop-Gewinn ≥ +1 dB** (Stimulus-Obergrenze −3 dBFS); sonst bricht der
   Lauf mit dieser Anweisung ab. `--relax-anchors` erlaubt abweichende
   Ankerpegel mit Ausweis der erreichten Pegel in der Auswertung.
3. **Baseline:** Dwarf mit **GS76-Bypass**; je Kanal `--baseline-repeats`
   (Standard 2) Läufe. Daraus Stabilitätsreferenz (Wiederholungsspreizung,
   Ch1↔Ch2-Asymmetrie) und die Ankerzuordnung.
4. **Matrix:** je Transformator ein Prompt (Dwarf umstellen, Bypass aus),
   dann `--repeats` (Standard 3) Läufe je Kanal mit der Kanal-Baseline.
5. **Auswertung:** `SUMMARY.md`/`summary.json` im Messwurzelverzeichnis:
   Frequenzgang relativ zur Bypass-Baseline (Median/Spreizung über die
   Wiederholungen), Pegelanker-Tabelle mit THD/THD+N, Stabilitätsreferenz,
   Hinweisliste (ungültige Läufe, Raten-Mismatch, Loop-Gewinn unter −20 dB,
   Loop-Gewinn-Drift zwischen Läufen).

## Regeln und Grenzen

- Zwischen Baseline und DUT-Läufen **keine** Regler am Dwarf/Scarlett
  verändern; der Treiber meldet Loop-Gewinn-Drift > 1 dB als Hinweis.
- Fortsetzung: gleiche `--root` wiederholen; fertige Läufe werden übersprungen,
  unvollständige Verzeichnisse gelöscht, fertige mit Fehler verweigert.
- Offline-/Mocktests: `tests/test_scarlett_matrix.py` (19 Fälle, simuliertes
  Backend). Eine simulierte Umgebung ist keine Geräteabnahme.
- Die Aussagegrenzen von Abschnitt Scarlett (THD = Gesamtpfad, 20 kHz bei
  48 kHz nicht trennscharf, keine interne FET-GR) gelten unverändert; 20 kHz
  bei Bedarf mit `--rates 48000 96000` nachmessen (Geräteraten vorher
  umstellen).

## Erster Live-Einsatz der Matrix (2026-10-06, nicht abgeschlossen)

Messreihe `test-results/matrix-20261006-161927` (Gainmatch-Proben; Baseline/
Matrix noch offen). Ursache des Abbruchs: Pegelkette/Routing, keine
Software-Probleme. Verlauf:

| Probe | Ch1 Loop-Gewinn | Ch2 Loop-Gewinn | Differenz | Befund |
|---|---:|---:|---:|---|
| 1 | −54,26 dB | −54,46 dB | −0,20 dB | Kanäle gematcht (PD-Abgleich bestätigt); Pegel zu niedrig; beide Geräte `default_samplerate` 44100 |
| 2 | −46,77 dB | −45,94 dB | +0,83 dB | +7,5 dB angehoben; Raten-Mismatch aktiv; Sync-Marker im Ch2-Teil nicht möglich (Korrelation 0,319 < 0,35), Aufnahme zeigt Ch2-Clipping (138 662 Samples bei 0,0 dBFS) im Ch1-Probe |
| 3 | −30,60 dB | −35,53 dB | −4,93 dB | Raten-Mismatch aktiv (Windows-Geräteformat weiterhin 44100 trotz 48-kHz-Panel); Ch2 clippt erneut (104 880 Samples) im Ch1-Probe |

Interpretation:

- **Kanalmatch:** Der frühere PluginDoctor-Abgleich der beiden Dwarf-Input-
  Gains ist mit −0,20 dB Differenz durch das Skript bestätigt; die Probe ist
  die reproduzierbare Ersatz-Methode.
- **Raten-Mismatch:** Die Scarlett-Panel-Einstellung (48 kHz, SYNCED) ändert
  das **Windows-Geräteformat** nicht; PortAudio `default_samplerate` folgt
  dem Format in `mmsys.cpl` (Wiedergabe **und** Aufnahme getrennt prüfen).
  Solange dort 44100 steht, resampelt der Windows-Mixer und der Sync-Marker
  fällt unter 0,35.
- **Signal auf beiden Eingängen im Ein-Kanal-Probe + Clipping auf dem
  „stillen“ Kanal:** Hinweis auf ein aktives **MONO-Board** (Mono verarbeitet
  Input L auf beide Outputs) oder eine abweichende Verkabelung. Vor den
  Messreihen klären (STEREO-Board laden, Kabel prüfen); der Clip-Zähler in
  `results.json` zeigt es je Lauf sofort.
- **Pegelsplit:** Gain vor dem Plugin-Eingang (Dwarf-INPUT-Knopf) setzt den
  Plugin-Eingangspegel (Anker); Gain danach (Dwarf-OUTPUT, Scarlett-INPUT-
  Gains) hebt nur den Rückkanal/SNR. Der große Rest (+46 dB) liegt hauptsächlich
  auf der Return-Seite (Scarlett-INPUT-Gains bis ~+50 dB). Dwarf-INPUT einmal
  matchen, danach nicht mehr verändern; die Probe meldet Kanaldrift sofort.
