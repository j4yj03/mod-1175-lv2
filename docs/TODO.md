
## Offen (2026-10-05)

- [ ] LV2 GUI: Titel "Green Stripe 76" im grünen Rechteck durch Logo `lv2/green-stripe-76.lv2/modgui/assets/logo.png` ersetzt (HTML + CSS angepasst). Assets neu rendern (screenshot-mono/stereo, thumbnail-mono/stereo) via `tools/make_assets.py` (benötigt PIL). Aktuell PIL nicht installiert im WSL-Environment; Rendering noch ausstehend.
- [ ] README-Verzeichnisse auf ersten beiden Stufen erstellen (jedes Parent- und erste Child-Verzeichnis erhält `README.md`), Haupt-README nur Überblick + Referenzen.
- [ ] `.opencode/skills/audio-coding/SKILL.md` um MOD-Dwarf-Erkenntnisse erweitert (SSH, Web-API, last.json+Restart, CPU-Messung, Python 3.4-Stolperfallen, Praxis) – done.
- [ ] Dwarf-Messreihe via `last.json` + Restart abschließen: `GS76x0–x4`, 128/256 Frames, 20s, Reports nach `/tmp/dwarf_gs76_matrix/` holen und in `docs/DWARF_RESULTS.md`/`docs/STATUS.md` einpflegen.
- [ ] `transformer_bench` AArch64 (MPB/moddwarf-new) auf Dwarf bauen/ausführen zur isolierten Erfassung Solver-/Transformer-Kosten (CPU_ANALYSIS 5c).
- [ ] PluginDoctor-GR-Daten (`docs/sauce/gain - 0, atk - 7, rls - 7 - 100 - 100/*.txt`) auswerten: GR sinkt ab 8:1 aufwärts – gegen Ratio/Detector/Knie-Verhalten abgleichen, Dokumentation in `docs/` ergänzen.
