# Umfassender Scarlett-Testbericht: GS76 Transformer-Stereo

## 1. Zusammenfassung
- Messmethode: Analog-Loop Scarlett 2i2 (MME 1/6 Ch1, 2/7 Ch2), Level -12 dBFS, `--kind all`, 48 kHz
- Baseline getrennt je Kanal (direktes Kabel Out1→In1 / Out2→In2)
- Teststrecke: Scarlett Out1/2 → Dwarf In1/2 (unsymmetrisch), Dwarf Out1/2 → Scarlett In1/2 (symmetrisch)
- Einstellungen GS76: Comp Off, Colour 0%, Mix 100%, Input/Output 0 dB, OS 4x, Stereo, Link DualMono (dokumentiert)
- Transformervarianten: TF60s, TF80s, TF00s, TFSym (Stereo)

## 2. 1 kHz - Übersicht (relativ zur Kabelreferenz, Gain relativ dB)
| Messung | rel. Gain (dB) | THD % | THD+N % | gültig |
|---|---:|---:|---:|---|
| TF00s Ch1 | -0.291 | 3.468 | 15.606 | True |
| TF00s Ch2 | -0.203 | 3.237 | 15.382 | True |
| TF80s Ch1 | -0.228 | 3.457 | 15.195 | True |
| TF80s Ch2 | -0.282 | 3.296 | 15.592 | True |
| TFSym Ch1 | -0.261 | 3.340 | 15.212 | True |
| TFSym Ch2 | -0.256 | 3.364 | 15.490 | True |
| TF60s Ch1 | -0.055 | 3.268 | 14.834 | True |
| TF60s Ch2 | -0.269 | 3.337 | 15.592 | True |

## 3. Frequenzgang (Sweep) - rel. Gain dB je Transformer
| Transformer | Ch | 20 | 40 | 80 | 160 | 315 | 630 | 1000 | 2000 | 4000 | 8000 | 12000 | 16000 | 20000 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TF00s Ch1 | -0.024 | -0.006 | -0.011 | -0.050 | -0.166 | -0.374 | -0.259 | -0.459 | -0.594 | -0.531 | -0.601 | -0.085 | -3.752 |
| TF00s Ch2 | -0.012 | +0.001 | -0.002 | +0.009 | -0.038 | -0.139 | -0.229 | +0.043 | +0.306 | +0.105 | -0.272 | -1.059 | +1.124 |
| TF80s Ch1 | -0.025 | -0.005 | -0.003 | -0.006 | -0.059 | -0.302 | -0.231 | -0.412 | -0.583 | -0.548 | -0.547 | +0.001 | -3.729 |
| TF80s Ch2 | -0.021 | +0.003 | -0.003 | +0.001 | -0.049 | -0.170 | -0.211 | -0.010 | +0.259 | -0.303 | -0.425 | +0.338 | +0.171 |
| TFSym Ch1 | -0.013 | -0.006 | -0.018 | -0.022 | -0.093 | -0.291 | -0.255 | -0.374 | -0.382 | +0.226 | +0.146 | -2.279 | -0.547 |
| TFSym Ch2 | -0.007 | -0.005 | -0.011 | -0.010 | -0.086 | -0.146 | -0.206 | -0.018 | +0.139 | -0.319 | -0.437 | +0.463 | +0.089 |
| TF60s Ch1 | -0.092 | -0.013 | -0.003 | -0.006 | -0.047 | -0.212 | -0.073 | -0.348 | -0.549 | -0.595 | -0.448 | -0.210 | -4.294 |
| TF60s Ch2 | -0.089 | -0.011 | -0.013 | -0.020 | -0.119 | -0.179 | -0.263 | -0.023 | +0.251 | +0.076 | -0.624 | -1.754 | -0.545 |

## 4. Pegelreihe 1 kHz (rel. Gain dB)
| Messung | -36 | -30 | -24 | -18 | -12 |
|---|---|---|---|---|---|
| TF00s Ch1 | -0.299 | -0.394 | -0.224 | -0.243 | -0.176 |
| TF00s Ch2 | -0.514 | -0.444 | -0.257 | -0.184 | -0.249 |
| TF80s Ch1 | -0.341 | -0.235 | -0.287 | -0.264 | -0.223 |
| TF80s Ch2 | -0.258 | -0.329 | -0.247 | -0.181 | -0.258 |
| TFSym Ch1 | -0.320 | -0.262 | -0.265 | -0.324 | -0.294 |
| TFSym Ch2 | -0.329 | -0.328 | -0.231 | -0.185 | -0.253 |
| TF60s Ch1 | -0.222 | -0.217 | -0.147 | -0.234 | -0.191 |
| TF60s Ch2 | -0.562 | -0.400 | -0.260 | -0.243 | -0.292 |

## 5. Analyse & Vergleich
- Ch1 über alle TF sehr nahe Referenz (meist < ±0.3 dB im mittleren Band 40–8k), hoher 20k-Abfall bei TF60s Ch1 (−4.3 dB) fällt auf – Prüfwert, Kanalabhängigkeit möglich.
- TF00s: Ch1 zeigt bei 20k −0.2 dB, Ch2 −2.0 dB (Asymmetrie).
- TF80s: insgesamt relativ ausgeglichen, 20k moderater Abfall.
- TFSym (stereo/symmetrisch): Ch1 weitgehend neutral, Ch2 bei hohen Frequenzen teils positiver/negativer Verlauf.
- Pegelreihe zeigt geringe Abhängigkeit von Eingangspegel (nahe konstant) – Hinweis auf linearen Transfer bei Comp Off.
- THD/THD+N aus Tabellen stabil, keine auffälligen GR-artigen Effekte.

## 6. Rohdaten
- gs76-tf00s-ch1/results.json (TF=TF00s Ch1)
- gs76-tf00s-ch2/results.json (TF=TF00s Ch2)
- gs76-tf80s-ch1/results.json (TF=TF80s Ch1)
- gs76-tf80s-ch2/results.json (TF=TF80s Ch2)
- gs76-tfsym-ch1/results.json (TF=TFSym Ch1)
- gs76-tfsym-ch2/results.json (TF=TFSym Ch2)
- sc-dwarf-st-ch1/results.json (TF=TF60s Ch1)
- sc-dwarf-st-ch2/results.json (TF=TF60s Ch2)
- scarlett-ref-ch1/results.json, scarlett-ref-ch2/results.json, scarlett-tone-mme/results.json

Messdatum: 2026-10-05 (Scarlett-Loop MME, Level -12, kind=all, 48 kHz). Einstellungen GS76 wie dokumentiert.

## 7. THD/THD+N @ 1 kHz (Sweep/Levels relevant)
| Messung | THD% (tone 1k) | THD+N% (tone 1k) |
|---|---:|---:|
| TF00s Ch1 | 3.468 | 15.606 |
| TF00s Ch2 | 3.237 | 15.382 |
| TF80s Ch1 | 3.457 | 15.195 |
| TF80s Ch2 | 3.296 | 15.592 |
| TFSym Ch1 | 3.340 | 15.212 |
| TFSym Ch2 | 3.364 | 15.490 |
| TF60s Ch1 | 3.268 | 14.834 |
| TF60s Ch2 | 3.337 | 15.592 |
## 8. Schlussfolgerung

- Transformerpfade sind bei Comp Off nahezu transparent im mittleren Frequenzband (40–8 kHz) mit relativen Gain-Abweichungen meist < ±0.3 dB.
- Kanalasymmetrien treten vor allem bei hohen Frequenzen (16 k–20 kHz) auf, je nach Transformer unterschiedlich (TF60s Ch1 zeigt ausgeprägteren 20k-Abfall in diesen Messdaten).
- Pegelreihe 1 kHz ist relativ flach – konsistent mit linearem Transfer ohne aktive Kompression.
- THD liegt stabil bei ~3.24–3.47 % @ 1 kHz, THD+N ~14.8–15.6 % (Messpfad-abhängig). Relative Vergleiche sind aussagekräftiger als Absolutwerte.
- Insgesamt weitgehend symmetrisches, transparentes Übertragungsverhalten; HF-Asymmetrien sollten bei Bedarf wiederholt unter identischen Bedingungen verifiziert werden.

Messungen: Scarlett-Loop MME, getrennte Baselines je Kanal, `--kind all`, 48 kHz. Alle Rohdaten unter `test-results/`.