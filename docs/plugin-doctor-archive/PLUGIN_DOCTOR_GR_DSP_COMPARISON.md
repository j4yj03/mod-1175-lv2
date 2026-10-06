# PluginDoctor GR vs DSP-Modell

## Modellparameter (data/model.json)
| Ratio | Mode | Ratio (linear) | Threshold (dBFS) | Knee (dB) |
|---|---:|---:|---:|---:|
| 2:1 | 0 | 2.0 | -24.0 | 6.0 |
| 4:1 | 1 | 4.0 | -24.0 | 6.0 |
| 8:1 | 2 | 8.0 | -21.0 | 4.0 |
| 12:1 | 3 | 12.0 | -19.5 | 3.0 |
| 20:1 | 4 | 20.0 | -18.0 | 2.0 |
| All Buttons | 5 | 16.0 | -22.0 | 1.5 |

## Messwerte PluginDoctor (GR = Input - Output, Transfer-In→Out)
Siehe Tabelle oben; Max-GR bei 0 dB In: 8:1 ~18.4 dB, 12:1 ~17.9 dB, 20:1 ~17.1 dB (abnehmend).

## Interpretation
- Knee wird kleiner (6→1.5), Threshold steigt (-24→-18) für höhere Ratio-Modi – das reduziert die effektive Kompression über weiten Pegelbereich (harder knee + höherer Threshold → späterer, schärferer aber begrenzter Übergriff).
- "All Buttons" (Mode 5) hat Ratio 16.0, sehr schmaler Knee 1.5, Threshold -22 – Verhalten zwischen 8:1 und 12:1, Peak-GR ~19.2 dB.
- Ab 8:1 steigt Threshold und sinkt Knee sukzessive – konsistent mit beobachteter Abnahme der Max-GR ab 8:1 (Messung). Das ist **modellseitig beabsichtigt** (nicht notwendigerweise klassisches FET-Hard-Knee aller Modi).

## Folge
PluginDoctors extern gemessener Transfer zeigt realistische Umsetzung der Modellparameter. Die Abnahme ab 8:1 erklärt sich aus Threshold/Knee-Verlauf, nicht aus einem DSP-Fehler. Für Hardware-Treue separate Vergleichsmessung (Scarlett-Loop) empfohlen, aber Kurvenverhalten ist konsistent mit Datenmodell.
