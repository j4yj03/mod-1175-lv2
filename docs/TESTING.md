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
- Aktivierung und `run(0)` mit gültiger Latenzausgabe.
- Samplegenau gleiche Ausgabe bei 1/64/128/256/511 Frames.
- In-place Stereo/Mono ohne Datenüberschreiben.
- Nichtendliche Inputs/Controls ergeben endliche Audioausgabe.

`validate.py` prüft generierte Metadaten, alle Presetbereiche, Portlayout, Includes
und GUI-Assets. Mit rdflib zusätzlich Turtle-Syntax. Lilv/MOD-SDK weiterhin als
externen **semantischen** Metadatencheck benutzen.

## 3. JSFX-Parität

Siehe Buildbefehle in `BUILD.md`. Pinned ysfx-Fork mit echter EEL2-JIT-Ausführung.

- Mono/Stereo × 44,1/48/96 kHz × 1/64/128/256 Frames × fünf Ratios = 120 Fälle.
- Dazu transparente/BYPASS-Impulse = vier Fälle.
- Regler-/Linkänderung im laufenden Stream und NaN/Inf: zehn weitere Fälle,
  zusammen **134**.
- Double-Kern, float Ports, initial kein Fast-Math/FMA.
- Peak-Abweichung höchstens **2×10⁻⁶ FS** pro Kanal.
- Alle 52 RPL-Presets gegen die eingebauten Selektorwerte abgleichen.
- Manuelle Änderung setzt den Selector auf Custom.

ysfx hat `slider_next_chg` nur als Stub und kennt REAPER-Host-GR nicht vollständig.
Diese Prüfung deckt deshalb keine samplegenaue REAPER-Automation ab.

GFX-Test mit `tests/jsfx_ui.cpp` (ysfx-GFX-Build): echte Offscreen-Grafik erzeugen,
mehrfach zeichnen und prüfen, dass der Control-Loop-Zustand identisch bleibt.
Der lokale Host hat gegebenenfalls nur Bitmapfonts. REAPER-HIDPI/Fonts extern prüfen.

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
