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
