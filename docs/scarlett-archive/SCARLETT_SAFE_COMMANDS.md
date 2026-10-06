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
