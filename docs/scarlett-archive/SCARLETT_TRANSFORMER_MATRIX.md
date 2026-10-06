# Scarlett – Transformer-Testmatrix

## Getestet
- Transformer: 60s (separat gemessen), jetzt 80s, 00s
- Symmetrisch (Stereo)

## Vorgehen
Je Transformer + Stereo (mit/ohne Link je Bedarf):
1. Ch1 Ref + Ch2 Ref (Out1→In1, Out2→In2), MME 1/6 bzw. 2/7 je Kanal, Level -12, `--kind all`
2. Dwarf Stereo, Transformer gesetzt, Parameter dokumentieren
3. Ch1 + Ch2 Runs mit jeweiliger Baseline

## Befehlsmuster (Ch1/Ch2)
Siehe `SCARLETT_STEREO_CMDS.md`. Label immer erweitern um `TF 60s/80s/00s`, `Sym`, `Link ...`

## Parameter (Vorgabe Transfer)
Comp Off, Colour 0, Mix 100, Input/Output 0, OS4x, Stereo Link dokumentieren (DualMono vs Link), Ratio/Attack/Release falls variiert ebenfalls notieren.

## Ergebnisablage
Ordnerstruktur z. B.:
- `test-results/scarlett-ref-ch1/`, `test-results/scarlett-ref-ch2/`
- `test-results/gs76-tf60s-stereo-ch1/`, `-ch2/`
- `test-results/gs76-tf80s-stereo-ch1/`, `-ch2/`
- `test-results/gs76-tf00s-stereo-ch1/`, `-ch2/`

## Notiz
Symmetrisch = Stereo-Modus, ggf. Link-Einfluss prüfen (Ch2 bei Link anders).
