# Scarlett Stereo – Befehle

## Referenzen
### Ch1 Referenz (Out1→In1)
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-ref-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --label "MME Ch1 Direkt"
```

### Ch2 Referenz (Out2→In2)
Kabel umlegen: Out2→In2, dann:
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-ref-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --label "MME Ch2 Direkt"
```

## GS76 Stereo-Teststrecke
GS76 im Dwarf Stereo laden (Link je Test dokumentieren). Verkabelung wie beschrieben.

### Ch1
```cmd
python tools\scarlett_test.py run --output test-results\sc-dwarf-st-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch1\results.json --label "Dwarf GS76 Stereo Ch1; Comp Off; Mix100; Colour0; OS4x; Link DualMono; Ratio 4:1; A7 R7"
```

### Ch2
```cmd
python tools\scarlett_test.py run --output test-results\sc-dwarf-st-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch2\results.json --label "Dwarf GS76 Stereo Ch2; Comp Off; Mix100; Colour0; OS4x; Link DualMono; Ratio 4:1; A7 R7"
```

Für **Stereo Link**: Ch2 kann durch Link beeinflusst sein – unbedingt separat messen und Label "Link On" setzen.
