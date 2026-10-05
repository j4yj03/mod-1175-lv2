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
| Alle 36 Presets: Input-Abgleich / Wet-GR / pegelgleiche Musik | | | |
| 31 Piano Gentle und 35 Stereo Bus Subtle: 4:1 gegen 2:1 | | | |
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
- `docs/STATUS.md` aktualisiert:
