# PluginDoctor GR vs Ratio – Auswertung

## Rahmenbedingungen
- Input Gain 0 dB, Output Gain 0 dB
- Attack 7, Release 7
- Comp On, Colour 100%, Mix 100%, Colour auf 0% (kein Unterschied)
- Messreihe unter `docs/sauce/gain - 0, atk - 7, rls - 7 - 100 - 100/*.txt`

## Ausgewertete GR-Werte (Input → Output, angenähert GR = Input - Output)
Tabelle zeigt geschätzte Gain Reduction in dB.

| Ratio | -20 dB In | -10 dB In | -6 dB In | -3 dB In | 0 dB In |
|---|---:|---:|---:|---:|---:|
| 2:1 | ~2.05 | ~7.02 | ~9.03 | ~10.55 | ~12.07 |
| 4:1 | ~3.34 | ~10.49 | ~13.49 | ~15.75 | ~18.00 |
| 8:1 | ~1.63 | ~9.66 | ~13.12 | ~15.74 | ~18.37 |
| 12:1 | ~0.49 | ~8.79 | ~12.39 | ~15.12 | ~17.87 |
| 20:1 | ~0.04 | ~7.71 | ~11.44 | ~14.26 | ~17.10 |
| All Buttons | ~0.67 | ~9.61 | ~13.41 | ~16.29 | ~19.18 |

## Beobachtung (Benutzer)
"Gainreduktion nimmt ab 8:1 aufwärts ab. [...]"

Aus Daten: 8:1 liefert bei 0 dB In ~18.37 dB, 12:1 ~17.87 dB, 20:1 ~17.10 dB – also **abnehmende Max-GR** bei höheren Ratios. Auch im mittleren Bereich (-10/-6 dB) fällt GR für 12:1/20:1 gegenüber 8:1 ab.

## Mögliche Ursachen (zu prüfen)
- Nichtlinearer Detektor/Knie (soft knee) beeinflusst effektive Ratio je Pegel
- Feedforward/Feedback-Topologie, Timing (Attack/Release) bei schnellen Pegelsprüngen
- Levelabhängiger Threshold/Makeup-Logik
- Messumgebung/PluginDoctor-Implementierung (z. B. Sweep vs Step) – Attack/Release 7 sind relativ moderat
- Internes Meter vs. externer Transfer (hier: In→Out über Loop)

## Nächste Schritte
- Gegen Referenz-1176-Verhalten (klassisch: höhere Ratio → höhere GR, typ. harte Knie) abgleichen
- DSP-Code prüfen: `src/dsp/GreenStripe.hpp`, Ratio-Handling, Detector (RMS/Peak?), Knee
- Gegebenenfalls mit anderen Attack/Release oder steilerer Anregung testen (Scarlett-Loop liefert präzisen Transfer)

## Anmerkung
Werte zeigen starken Anstieg ab ~-15 dB bis 0 dB; Peak-GR liegt um 8:1, nicht bei 20:1/All Buttons.
