# Stand bis hier hin

Dieser Abschnitt fasst den aktuellen Arbeitsstand zusammen (Dwarf-Messungen, Python-3.4-Portierung, Web-API-Einschränkung, PluginDoctor-Hinweis). Wird als Referenz abgelegt, um später nahtlos fortfahren zu können.

## 1) Dwarf-Messungen (LV2-Gesamtlast, 48 kHz)
- **Gerät**: MOD Dwarf OS 1.13.5.3315, Kernel `6.1.15-rt7-moddwarf`, AArch64 (4 Kerne), `jackdmp` 1.9.14 (PID 404), Blockgrößen 128/256, Periods n=2, RT-Priorität 80.
- **Messmatrix**: Boards `GS76Measure`, `GS76x0`–`GS76x4`, je 128 + 256 Frames, Messfenster 15–20 s, `expect-instances = 1` (Stereo-Instanz).
- **CPU-Last (Median/Spitze)**: Prozess-Median **46–48 %** eines Kerns pro Stereo-Instanz, Spitzen bis **~66 %**. Schwerster Thread durchgehend `jackd` (~21 % eines Kerns). **0 xruns** in allen Fenstern.
- **Plugin-Identität**: Installierte Binary `/root/.lv2/green-stripe-76.lv2/green-stripe-76.so`
  - SHA256: `e6b4e55da1f164db817d9fc083f0d7f5fad78ecaf3364650cd88a371e92e8d32`
  - MD5:    `4669363f1c2b781a6b162ea7f05bbd33`
- **Ergebnisse (lokal)**: `docs/DWARF_RESULTS.md` (vollständige Tabelle), Auszug in `docs/STATUS.md` übernommen. Rohdaten: `/tmp/opencode/dwarf_results/auto/*.json, *.md` (je Messlauf). Boardwechsel für diese Runs erfolgte manuell/mit last.json+Neustart (HTTP-API unzuverlässig).

## 2) `tools/dwarf_loadtest.py` – Python 3.4-Kompatibilität (Dwarf)
- Vollständige Portierung für Buildroot/Python 3.4: `io.open` statt `Path.read_text/write_text/read_bytes`, `subprocess.Popen` statt `subprocess.run` (kein `subprocess.run` in 3.4), Zeitstempel via `strftime('%Y-%m-%dT%H:%M:%SZ')` statt `isoformat(timespec=…)` (Python 3.6+).
- Self-Test lokal: **13/13 OK** (`python3 tests/test_dwarf_loadtest.py`). Skript aktuell auf Dwarf unter `/root/lt/dwarf_loadtest.py`.
- CLI: `--report/--markdown` genutzt, optionale Pfade `--output-json/--output-markdown` vorbereitet (Rückwärtskompatibel). Kompatibilitätspatches für Pfad-API (PosixPath an `open/io.open`) abgeschlossen.

## 3) Web-API (MOD OS 1.13.5.3315)
- `effect/parameter/set` und `pedalboard/load_web`/`load_bundle` lieferten bei POST/Form/JSON überwiegend **500 Internal Server Error** (kein stabiler, reproduzierbarer Pfad). Boardwechsel daher **via `last.json` + Neustart des Audio-Stacks** (`jackd`/`mod-host`) vorgesehen (robuster auf 1.13.x). Skriptgerüst `switch_and_measure.sh` erstellt, aber unterbrochener Lauf dokumentiert.

## 4) Offlinetests / Parität
- `make BUILD_DIR=build/wsl test`: **PASS** (13 Dwarf-Offline-Tests + weitere Suite).
- `make check-generated`: **PASS** (`Verified 17 files`).
- Diagnose-Makro-Parität: `diag_macro_parity` byteidentisch (60 Fälle, 90.000 Samples) – Nachweis Audionneutralität bei Diagnosepfad.

## 5) Messdaten PluginDoctor (GR vs Ratio)
- Messwerte vorliegend unter `docs/sauce/gain - 0, atk - 7, rls - 7 - 100 - 100/` (TXT-Dateien je Ratio: `2-1.txt`, `4-1.txt`, `8-1.txt`, `12-1.txt`, `20-1.txt`, `AllButtons.txt`). Beobachtung: **Gain Reduction nimmt ab 8:1 aufwärts ab** (bei 0 dB In/Out, Attack/Release 7, Comp On, Colour/Mix 100%, Colour 0% ohne Unterschied). Auswertung/Einordnung erfolgt separat (Dokumentation + Prüfung DSP-Detektor/Knie/Ratio-Handling).

## 6) Offene Punkte (Fortsetzung später)
- Vollständige automatische Matrix (GS76x0–x4, 128/256) via `last.json`+Restart abschließen (Skript liegt auf Dwarf).
- Transformatorprofile isoliert (Solver-Kosten) via `transformer_bench` AArch64 (MPB/moddwarf-new) auf Dwarf erfassen (CPU_ANALYSIS 5c).
- GR-Kurven aus PluginDoctor auswerten, gegen erwartetes 1176-ähnliches Ratio/Detector-Verhalten abgleichen und dokumentieren.
