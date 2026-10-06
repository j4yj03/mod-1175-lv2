# Scarlett-Test – Kurzanleitung

## 1. Setup (Windows, nativ)
- Scarlett 2i2 1st Gen, 48 kHz, Direct Monitor OFF, 48V OFF, INST/LINE korrekt
- Verkabelung: Out1/2 → Dwarf In1/2 (unsymmetrisch), Dwarf Out1/2 → Scarlett In1/2 (symmetrisch)
- Für Loop-Referenz: Out1→In1 (Ch1), Out2→In2 (Ch2)
- MME empfohlen (stabile Sync): Input 1/2, Output 6/7 je nach Liste prüfen (siehe `SCARLETT_RECOMMENDED_IDS.md`)

## 2. Schnellstart
```cmd
cd C:\Users\Sidney\Desktop\GreenStripe\mod-1175-lv2
python tools\scarlett_test.py devices
```

## 3. Typischer Ablauf (Stereo)
1. Ch1 Referenz: `--kind all --level -12 --rate 48000 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1`
2. Ch2 Referenz: entsprechend Kanal 2
3. Dwarf-Teststrecke mit `--baseline` je Kanal, Label mit Parametern (TF, Comp, Mix, OS, Link)

Siehe Archiv für exakte Befehle. Troubleshooting/Details im Archiv `docs/scarlett-archive/`.
