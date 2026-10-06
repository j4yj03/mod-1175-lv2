# Transformer-Test – Template

## Einstellungen Dwarf GS76 (Stereo)
- Comp: Off
- Colour: 0% | Mix: 100%
- Input: 0 | Output: 0
- OS: 4x
- Link: DualMono / On (dokumentieren)
- Ratio: 4:1 (oder neutral) – dokumentieren
- Attack/Release: 7/7
- Transformer: TF60s / TF80s / TF00s / None

## Referenzen
Ch1: `test-results/scarlett-ref-ch1/results.json`
Ch2: `test-results/scarlett-ref-ch2/results.json`

## Ch1
```cmd
python tools\scarlett_test.py run --output test-results\gs76-tf<XX>-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch1\results.json --label "MME Dwarf GS76 Stereo Ch1 TF<XX> CompOff Mix100 Col0 OS4x Link<XX> Ratio4 A7 R7"
```

## Ch2
```cmd
python tools\scarlett_test.py run --output test-results\gs76-tf<XX>-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-ref-ch2\results.json --label "MME Dwarf GS76 Stereo Ch2 TF<XX> CompOff Mix100 Col0 OS4x Link<XX> Ratio4 A7 R7"
```

Ersetze `<XX>` durch 60s/80s/00s und Link durch DualMono/On.
