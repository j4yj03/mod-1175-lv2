# Sync-Fehler bei minimalem Input-Gain

Beobachtung (Windows native):
- Input-Gain Scarlett minimal: Marker-Erkennung scheitert (correlation ~0.024–0.027)
- Level -15 ebenfalls zu schwach
- Hinweis: "Input am Interface war mittlerweile schon übersteuert" – Pegelwahl sensibel

Empfehlung:
- Input-Gain **sehr leicht anheben** (nur wenige Grad), bis Signal sauber ankommt, aber kein Clipping. Ziel: -18 dBFS Peak im Rückkanal.
- Falls immer noch < 0.35: temporär Schwelle in `correlation_marker` auf 0.15/0.20 absenken für Debug, dann wieder auf 0.35 für finale Validierung.
- Sicherstellen: direktes Kabel Out1→In1, Direct Monitor aus, keine DAW, 48 kHz.
