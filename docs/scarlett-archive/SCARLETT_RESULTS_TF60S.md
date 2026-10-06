# Scarlett-Ergebnisse – TF60s, Stereo (Symmetrisch)

## Setup
- MME: Ch1 In=1 Out=6, Ch2 In=2 Out=7 (entsprechend)
- Level -12 dBFS, `--kind all`, 48 kHz
- GS76 Stereo, TF60s, Comp Off, Colour 0, Mix 100, Input/Output 0, OS4x, Link DualMono (laut Label)
- Baseline: separate Referenzen `scarlett-ref-ch1`, `scarlett-ref-ch2`

## Ausgewählte Werte (relativ zur Kabelreferenz)

| Kanal | 1kHz (tone) rel. Gain dB | THD% @1k | THD+N% @1k | Level -12 rel. Gain dB | THD% @-12 | THD+N% @-12 |
|---|---:|---:|---:|---:|---:|---:|
| Ch1 (TF60s) | -0.055 | 3.27 | 14.83 | -0.191 | 3.40 | 15.34 |
| Ch2 (TF60s) | -0.269 | 3.34 | 15.59 | -0.292 | 3.35 | 15.66 |

## Frequenzgang (Sweep, rel. Gain dB)
| Hz | 20 | 40 | 80 | 160 | 315 | 630 | 1000 | 2000 | 4000 | 8000 | 12000 | 16000 | 20000 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ch1 | -0.092 | -0.013 | -0.0030 | -0.0059 | -0.047 | -0.212 | -0.073 | -0.348 | -0.549 | -0.595 | -0.448 | -0.210 | -4.29 |
| Ch2 | -0.089 | -0.011 | -0.0127 | -0.0203 | -0.119 | -0.179 | -0.263 | -0.023 | +0.251 | +0.076 | -0.624 | -1.75 | -0.545 |

## Pegelreihe (1kHz, rel. Gain dB)
| Peak dBFS | -36 | -30 | -24 | -18 | -12 |
|---:|---:|---:|---:|---:|
| Ch1 | -0.222 | -0.217 | -0.147 | -0.234 | -0.191 |
| Ch2 | -0.562 | -0.400 | -0.260 | -0.243 | -0.292 |

## Auswertung
- Sehr geringe relative Verstimmungsänderung (nahe 0 dB) im mittleren Band – Transformatorpfad nahezu transparent bei TF60s (Stereo, Comp Off).
- Ch2 zeigt leichte Asymmetrie bei sehr tiefen (20–80 Hz) und bei hohen Frequenzen (4k–20k) im Sweep, insgesamt sehr geringfügig.
- THD/THD+N relativ stabil über Kanäle.
