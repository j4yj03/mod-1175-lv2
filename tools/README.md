# tools/ — Generator, Build- und Messwerkzeuge

`generate.py` (generiert TTL/JSFX/GUI aus `data/*.json`), `render_lv2.py`
(Offline-Render), `transformer_bench.cpp` (A35-Bench), `dwarf_loadtest.py` /
`run_cpu_matrix.py` (Dwarf-Last), `scarlett_*.py` + `make_dwarf_tones.py`
(Messreihe), `testbench_rpp.py` (REAPER-Testbench-Generator),
`render_results_doc.py` (generiert `docs/MESSERGEBNISSE.md`),
`make_vumeter.py` (VU-Meter-Asset: GR-Skala 0…30 dB als Face **ohne Nadel**
in zwei Zuständen — `--state on` beleuchtet/warm (COMP ON) und `--state
off` gedimmt (COMP OFF), Ausgaben `assets/vumeter-on.png`/`-off.png`; die
Nadel wird später per CSS rotiert — `--needle-output` liefert die
transparente Nadel-Ebene, `--needle-db` ihre Position. Assets sind
vorbereitend, in keinem Template eingebunden).
