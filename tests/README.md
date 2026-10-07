# tests/ — Prüfungen

`make test` fährt die Kette: DSP-Acceptance (Signal/Stress/Übergänge),
Transformer-Tests, Diagnose-Makro-Parität, LV2-ABI (Blockgrößen/In-place/
Latenz/Modellwechsel), Bankvalidierung, Loadtest-Selbsttests, `validate.py`.
`jsfx_parity` vergleicht C++/EEL2 bitweise (430 + 76 Fälle, max 0 FS).
