# Scarlett – Stereo-Messung

## Verkabelung Stereo
- Scarlett Out 1 → Dwarf In 1 (unsymmetrisch)
- Scarlett Out 2 → Dwarf In 2 (unsymmetrisch)
- Dwarf Out 1 → Scarlett In 1 (symmetrisch)
- Dwarf Out 2 → Scarlett In 2 (symmetrisch)

## Skript: Stereo-Loop (beide Kanäle gleichzeitig)
`tools/scarlett_test.py` spielt ausgewählten Ausgang (`--output-channel`) und zeichnet **beide Eingänge** auf. Für Stereo-Teststrecke über Dwarf werden beide Kanäle durchlaufen.

Variante A: Kanal 1 messen, dann Kanal 2 getrennt (mit Baseline je Kanal) oder Kanal 2 mit gleicher Referenz (Loop symmetrisch). Für Stereo Link relevant.

Variante B: Analyse Kanal 2 separat mit `--channel 2`:
```cmd
python tools\scarlett_test.py analyze --directory test-results\scarlett-dwarf-stereo --recording test-results\scarlett-dwarf-stereo\recording.wav --channel 2 --baseline test-results\scarlett-reference-mme\results.json --report-dir test-results\scarlett-dwarf-stereo-ch2
```

Aber besser: jeweils eigenen Lauf pro Kanal oder Dokumentation. Einfacher: Zwei separate Runs (Kanal 1 + Kanal 2) mit identischer Referenz, Label ergänzt "Ch1/Ch2".

## Empfehlung (Stereo, getrennt ausgewertet)
1. Referenz Out1→In1 (Ch1) + optional Out2→In2 Referenz
2. Dwarf Stereo aktiv, Messung Ch1: `--input-channel 1 --output-channel 1`, Label "Stereo, Ch1"
3. Dwarf Stereo aktiv, Messung Ch2: `--input-channel 2 --output-channel 2`, Label "Stereo, Ch2" (gleiche Referenz oder separate)
Mit GS76 Stereo Link beachten (Link beeinflusst Detektion).

## Live-Run Stereo (MME, -12)
```cmd
python tools\scarlett_test.py run --output test-results\scarlett-dwarf-stereo-ch1 --input-device 1 --output-device 6 --input-channel 1 --output-channel 1 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-reference-mme\results.json --label "Dwarf 48k; GS76 Stereo; Ch1; Comp dokumentieren..."
```

```cmd
python tools\scarlett_test.py run --output test-results\scarlett-dwarf-stereo-ch2 --input-device 1 --output-device 6 --input-channel 2 --output-channel 2 --kind all --level -12 --settle 2 --measure 1 --baseline test-results\scarlett-reference-mme\results.json --label "Dwarf 48k; GS76 Stereo; Ch2; ..."
```

Hinweis: Referenz für Ch2 ggf. separat erstellen (Out2→In2).
