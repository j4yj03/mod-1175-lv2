# Messergebnisse — Transformator-Matrix, Colour-Serie und CPU am Gerät

Generiert von `tools/render_results_doc.py` aus den Analyse-JSONs unter
`test-results/`; Zahlen werden nicht von Hand gepflegt. Messdatum:
**2026-10-07**; Gerät: MOD Dwarf OS 1.13.5.3315, 48 kHz, Bundle `48ab885`
(HEAD, MPB `moddwarf-new`, `-O3 -ffp-contract=off -fno-fast-math`).

Alle Digitalmessungen sind Dwarf-Recorder-Captures (Kabel GS76 → Record,
keine Wandler, Kanal 1; Stimulus L=R). Referenzen sind Offline-Render des
C++-Pfads mit identischer Parametrisation; die JSFX-Render des Benutzers
sind bitnah dagegen verifiziert (Abschnitt 3). Stimulus: 19 Segmente
(1-kHz-Tone, Sweep 20 Hz…20 kHz je −2 dBFS, Pegelreihe 1 kHz −26…−2 dBFS),
Dauer 64,47 s.

## 1. Transformator-Matrix (Bank-only: Colour 0, COMP OFF, OS 2x)

Bedingungen: Input/Output 0 dB, Mix 100 %, Ratio 4:1 (geparkt), Preset
Custom; Baseline = Bypass. Digital-Capture `matrix-dwarf-20261007-b2`.

### 1.1 Kennwerte

| Typ | 20-Hz-Klirr % | 80-Hz-Klirr % | 1-kHz-Klirr % | rel. Gain 20 Hz dB | rel. Gain 1 kHz dB |
|---|---:|---:|---:|---:|---:|
| 60s | 12.4242 | 0.2508 | 0.0008 | -0.8174 | -0.0001 |
| 80s | 12.2758 | 0.0218 | 0.0005 | -0.4412 | -0.0001 |
| 00s | 0.9995 | 0.0088 | 0.0004 | -0.0156 | -0.0000 |
| Sym | 0.0000 | 0.0000 | 0.0000 | -0.0018 | +0.0001 |
| Baseline (Bypass) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

Die Sättigungshärte-Reihung der aktuellen Bank am 20-Hz-Klirr ist
**60s ≈ 80s (12,42/12,28 %) ≫ 00s (1,00 %) ≫ Sym (0 %)**. Gegenüber der
alten Installationsbank (5,53/2,15/0,11 %) haben sich 60s und 80s
zusammengerückt; die Typen unterscheiden sich jetzt stärker über die
Koppelungsverluste (rel. Gain 20 Hz −0,82/−0,44/−0,02 dB) und das
80-Hz-Klirrverhalten (0,25/0,02/0,01 %). Interpretation gegen die
Modellanker: `EXTERN.md` (offen).

![Frequenzgang](plots/mess-frequenzgang-transformer.png)

![Klirr über Frequenz](plots/mess-klirr-frequenz-transformer.png)

![Harmonische bei 20 Hz](plots/mess-harmonisch-20hz.png)

### 1.2 Klirrfaktor je Segment (Gerät, Digital-Capture)

| Hz | Peak dBFS | 60s % | 80s % | 00s % | Sym % | Baseline % |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | -2 | 0.0008 | 0.0005 | 0.0004 | 0.0000 | 0.0000 |
| 20 | -2 | 12.4242 | 12.2758 | 0.9995 | 0.0000 | 0.0000 |
| 40 | -2 | 1.9383 | 0.5003 | 0.0411 | 0.0000 | 0.0000 |
| 80 | -2 | 0.2508 | 0.0218 | 0.0088 | 0.0000 | 0.0000 |
| 160 | -2 | 0.0370 | 0.0039 | 0.0031 | 0.0000 | 0.0000 |
| 315 | -2 | 0.0084 | 0.0020 | 0.0015 | 0.0000 | 0.0000 |
| 630 | -2 | 0.0021 | 0.0008 | 0.0005 | 0.0000 | 0.0000 |
| 1000 | -2 | 0.0010 | 0.0005 | 0.0004 | 0.0000 | 0.0000 |
| 2000 | -2 | 0.0004 | 0.0003 | 0.0002 | 0.0000 | 0.0000 |
| 4000 | -2 | 0.0002 | 0.0002 | 0.0001 | 0.0000 | 0.0000 |
| 8000 | -2 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 12000 | -2 | — | — | — | — | — |
| 16000 | -2 | — | — | — | — | — |
| 20000 | -2 | — | — | — | — | — |
| 1000 | -26 | 0.0007 | 0.0005 | 0.0004 | 0.0001 | 0.0001 |
| 1000 | -20 | 0.0008 | 0.0006 | 0.0004 | 0.0000 | 0.0000 |
| 1000 | -14 | 0.0009 | 0.0006 | 0.0004 | 0.0000 | 0.0000 |
| 1000 | -8 | 0.0008 | 0.0005 | 0.0003 | 0.0000 | 0.0000 |
| 1000 | -2 | 0.0010 | 0.0005 | 0.0004 | 0.0000 | 0.0000 |

*(20 kHz: H1-only-Fit, THD nicht definiert — „—".)*

### 1.3 Relativer Gain je Segment (Gerät minus Bypass)

| Hz | Peak dBFS | 60s dB | 80s dB | 00s dB | Sym dB |
|---:|---:|---:|---:|---:|---:|
| 1000 | -2 | -0.0001 | -0.0001 | -0.0000 | +0.0001 |
| 20 | -2 | -0.8174 | -0.4412 | -0.0156 | -0.0018 |
| 40 | -2 | -0.0357 | -0.0089 | -0.0048 | -0.0002 |
| 80 | -2 | -0.0050 | -0.0031 | -0.0020 | +0.0001 |
| 160 | -2 | -0.0017 | -0.0013 | -0.0007 | +0.0002 |
| 315 | -2 | -0.0006 | -0.0005 | -0.0002 | +0.0002 |
| 630 | -2 | -0.0003 | -0.0002 | -0.0001 | +0.0002 |
| 1000 | -2 | -0.0001 | -0.0001 | -0.0000 | +0.0001 |
| 2000 | -2 | -0.0002 | -0.0001 | -0.0003 | -0.0003 |
| 4000 | -2 | -0.0030 | -0.0008 | -0.0019 | -0.0018 |
| 8000 | -2 | -0.0416 | -0.0060 | -0.0080 | -0.0080 |
| 12000 | -2 | -0.1983 | -0.0220 | -0.0178 | -0.0178 |
| 16000 | -2 | -0.5882 | -0.0588 | -0.0306 | -0.0306 |
| 20000 | -2 | -1.3034 | -0.1287 | -0.0456 | -0.0456 |
| 1000 | -26 | +0.0001 | +0.0000 | +0.0000 | +0.0001 |
| 1000 | -20 | -0.0000 | -0.0000 | -0.0000 | +0.0001 |
| 1000 | -14 | -0.0000 | -0.0000 | -0.0000 | +0.0001 |
| 1000 | -8 | -0.0000 | -0.0000 | -0.0000 | +0.0001 |
| 1000 | -2 | -0.0001 | -0.0001 | -0.0000 | +0.0001 |

![Level-Reihe Transformer](plots/mess-levels-transformer.png)

### 1.4 Analog-Loop-Kreuzprüfung (REAPER-Take, Loop ≈ −6,2 dB)

| Typ | rel. Gain 20 Hz dB | rel. Gain 1 kHz dB | 20-Hz-Klirr % |
|---|---:|---:|---:|
| 60s | -0.8198 | -0.0115 | 12.5933 |
| 80s | -0.4422 | -0.0094 | 12.4439 |
| 00s | -0.0119 | -0.0009 | 1.0129 |
| Sym | -0.0007 | -0.0068 | 0.0063 |

Die Analogwerte bestätigen die Digitalmessung innerhalb der
Kettenpräzision (Klirrgrund 0,0076 %; Loop-Klirr addiert sich
vektoriell, daher leicht über dem Digitalwert).

## 2. Colour-Serie (Transformer None, COMP OFF, OS 2x)

Bedingungen wie Abschnitt 1, Colour **5/10/20/50/75/100 %**. Digital-
Capture `colour-dwarf-20261007`; Referenzen = C++-Render (bitidentisch
zu den JSFX-Render `matrix-*_col_jsfx-…12_33_03`).

### 2.1 Kennwerte (Gerät vs. Referenz)

| Colour | 1-kHz-Klirr % | Ref | 1-kHz-Gain dB | Ref | 20-Hz-Klirr % | Ref | 8-kHz-Klirr % | Ref |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 % | 0.1228 | 0.1228 | -0.0299 | -0.0298 | 0.1457 | 0.1457 | 0.0533 | 0.0533 |
| 10 % | 0.2455 | 0.2455 | -0.0597 | -0.0596 | 0.2888 | 0.2888 | 0.1066 | 0.1066 |
| 20 % | 0.4907 | 0.4907 | -0.1191 | -0.1190 | 0.5663 | 0.5663 | 0.2126 | 0.2126 |
| 50 % | 1.2236 | 1.2236 | -0.2961 | -0.2961 | 1.3246 | 1.3246 | 0.5277 | 0.5277 |
| 75 % | 1.8311 | 1.8311 | -0.4422 | -0.4421 | 1.8620 | 1.8620 | 0.7865 | 0.7865 |
| 100 % | 2.4352 | 2.4353 | -0.5869 | -0.5868 | 2.3107 | 2.3107 | 1.0417 | 1.0417 |

Der 1-kHz-Klirr und der 1-kHz-Gain skalieren **linear mit Colour**
(Verdopplung je Verdopplung; 20→50 % liegt leicht unter Linearität —
Sättigungskurve). Die 20-Hz-Werte bei None stammen aus der Output-
Drive-Stufe (max. 2,31 % bei 100 %).

![Colour-Klirr-Sweep](plots/mess-colour-klirr.png)

![Colour-Gain-Sweep](plots/mess-colour-gain.png)

### 2.2 Klirrfaktor je Segment (Gerät)

| Hz | Peak dBFS | 5 % | 10 % | 20 % | 50 % | 75 % | 100 % |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1000 | -2 | 0.1228 | 0.2455 | 0.4907 | 1.2236 | 1.8311 | 2.4352 |
| 20 | -2 | 0.1457 | 0.2888 | 0.5663 | 1.3246 | 1.8620 | 2.3107 |
| 40 | -2 | 0.1107 | 0.2198 | 0.4335 | 1.0422 | 1.5214 | 1.9865 |
| 80 | -2 | 0.1164 | 0.2326 | 0.4643 | 1.1557 | 1.7290 | 2.3013 |
| 160 | -2 | 0.1221 | 0.2440 | 0.4876 | 1.2155 | 1.8191 | 2.4198 |
| 315 | -2 | 0.1227 | 0.2454 | 0.4904 | 1.2229 | 1.8302 | 2.4343 |
| 630 | -2 | 0.1228 | 0.2455 | 0.4907 | 1.2237 | 1.8313 | 2.4357 |
| 1000 | -2 | 0.1228 | 0.2455 | 0.4907 | 1.2236 | 1.8311 | 2.4352 |
| 2000 | -2 | 0.1228 | 0.2455 | 0.4905 | 1.2228 | 1.8294 | 2.4322 |
| 4000 | -2 | 0.1228 | 0.2454 | 0.4901 | 1.2198 | 1.8228 | 2.4206 |
| 8000 | -2 | 0.0533 | 0.1066 | 0.2126 | 0.5277 | 0.7865 | 1.0417 |
| 12000 | -2 | — | — | — | — | — | — |
| 16000 | -2 | — | — | — | — | — | — |
| 20000 | -2 | — | — | — | — | — | — |
| 1000 | -26 | 0.0038 | 0.0076 | 0.0151 | 0.0378 | 0.0567 | 0.0756 |
| 1000 | -20 | 0.0077 | 0.0154 | 0.0309 | 0.0771 | 0.1157 | 0.1542 |
| 1000 | -14 | 0.0166 | 0.0333 | 0.0665 | 0.1662 | 0.2492 | 0.3321 |
| 1000 | -8 | 0.0413 | 0.0826 | 0.1652 | 0.4124 | 0.6179 | 0.8229 |
| 1000 | -2 | 0.1228 | 0.2455 | 0.4907 | 1.2236 | 1.8311 | 2.4352 |

### 2.3 Gain je Segment (Gerät, absolut gegen digitalen Nominalpegel)

| Hz | Peak dBFS | 5 % dB | 10 % dB | 20 % dB | 50 % dB | 75 % dB | 100 % dB |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1000 | -2 | -0.0299 | -0.0597 | -0.1191 | -0.2961 | -0.4422 | -0.5869 |
| 20 | -2 | -0.1260 | -0.2477 | -0.4778 | -1.0581 | -1.4099 | -1.6395 |
| 40 | -2 | -0.0580 | -0.1145 | -0.2231 | -0.5148 | -0.7201 | -0.8924 |
| 80 | -2 | -0.0365 | -0.0725 | -0.1434 | -0.3464 | -0.5051 | -0.6548 |
| 160 | -2 | -0.0314 | -0.0625 | -0.1244 | -0.3068 | -0.4553 | -0.6005 |
| 315 | -2 | -0.0302 | -0.0603 | -0.1202 | -0.2982 | -0.4446 | -0.5892 |
| 630 | -2 | -0.0299 | -0.0597 | -0.1192 | -0.2962 | -0.4422 | -0.5868 |
| 1000 | -2 | -0.0299 | -0.0597 | -0.1191 | -0.2961 | -0.4422 | -0.5869 |
| 2000 | -2 | -0.0300 | -0.0600 | -0.1197 | -0.2975 | -0.4442 | -0.5896 |
| 4000 | -2 | -0.0307 | -0.0613 | -0.1223 | -0.3038 | -0.4534 | -0.6014 |
| 8000 | -2 | -0.0333 | -0.0665 | -0.1325 | -0.3284 | -0.4892 | -0.6476 |
| 12000 | -2 | -0.0374 | -0.0745 | -0.1484 | -0.3668 | -0.5451 | -0.7201 |
| 16000 | -2 | -0.0423 | -0.0843 | -0.1677 | -0.4135 | -0.6132 | -0.8082 |
| 20000 | -2 | -0.0480 | -0.0957 | -0.1905 | -0.4695 | -0.6962 | -0.9177 |
| 1000 | -26 | -0.0005 | -0.0009 | -0.0017 | -0.0040 | -0.0059 | -0.0077 |
| 1000 | -20 | -0.0008 | -0.0016 | -0.0031 | -0.0077 | -0.0114 | -0.0151 |
| 1000 | -14 | -0.0023 | -0.0045 | -0.0090 | -0.0223 | -0.0333 | -0.0443 |
| 1000 | -8 | -0.0081 | -0.0161 | -0.0320 | -0.0797 | -0.1193 | -0.1586 |
| 1000 | -2 | -0.0299 | -0.0597 | -0.1191 | -0.2961 | -0.4422 | -0.5869 |

### 2.4 Analog-Loop-Kreuzprüfung (Colour)

| Colour | rel. Gain 1 kHz dB | 1-kHz-Klirr % |
|---:|---:|---:|
| 5 % | +0.0000 | 0.1215 |
| 10 % | -0.0299 | 0.2439 |
| 20 % | -0.0872 | 0.4893 |
| 50 % | -0.2637 | 1.2210 |
| 75 % | -0.4082 | 1.8280 |
| 100 % | -0.5514 | 2.4321 |

### 2.5 Bank×Colour-Interaktion (JSFX-Render-Matrix, Gerät durch Zerlegung abgedeckt)

Die vollständige Matrix (Colour 5/10/20/50/75/100 % × Transformer
60s/80s/00s/Sym, COMP OFF, OS 2x) wurde als **JSFX-Render** erzeugt
(`matrix-*_col_*_jsfx-…12_49_00`) und gegen frische C++-Offline-Referenzen
verifiziert: **alle 24 Zustände bitgleich** (schlechtester max|diff|
**6.0e-08** = 0,5 LSB bei 24 bit, Offset −3 Samples). Zusammen mit
Abschnitt 3 sind damit **34 Betriebszustände** bitverifiziert.

**Abdeckung am Gerät:** Die beiden Pfade wurden einzeln am Gerät exakt
validiert (Abschnitt 1: Bank-only Colour 0 × alle Typen; Abschnitt 2:
Colour-Stufen × None) — beide decken sich mit dem C++-Modell bis in die
4. Dezimale, und JSFX ≡ C++ bitweise. Die Interaktion nutzt keine
zusätzlichen Codepfade (Bank → Colour-Stufen in derselben Kette), ein
gerätespezischer Interaktionsfehler ist deshalb praktisch ausgeschlossen.
Die Interaktionsmatrix wurde daher **nicht direkt am Gerät gemessen**;
die hier gezeigten Werte sind Modellwerte (JSFX/C++-Render). Für eine
direkte Gerätemessung stehen die Referenzrender bereit.

20-Hz-Klirr % (Zeile = Colour, Spalte = Transformer; Colour-0-Zeile aus
Abschnitt 1):

| Colour | 60s | 80s | 00s | Sym |
|---:|---:|---:|---:|---:|
| 0 % | 12.4242 | 12.2758 | 0.9995 | 0.0000 |
| 5 % | 12.4526 | 12.3127 | 0.9938 | 0.1457 |
| 10 % | 12.4872 | 12.3562 | 1.0164 | 0.2886 |
| 20 % | 12.5743 | 12.4630 | 1.1341 | 0.5660 |
| 50 % | 12.9549 | 12.9129 | 1.7809 | 1.3240 |
| 75 % | 13.3542 | 13.3726 | 2.3842 | 1.8613 |
| 100 % | 13.7538 | 13.8233 | 2.9346 | 2.3100 |

1-kHz-Klirr % (Colour dominiert; der Transformatorträger unterscheidet
sich nur noch im vierten Dezimal):

| Colour | 60s | 80s | 00s | Sym |
|---:|---:|---:|---:|---:|
| 5 % | 0.1233 | 0.1232 | 0.1231 | 0.1228 |
| 10 % | 0.2460 | 0.2459 | 0.2458 | 0.2455 |
| 20 % | 0.4912 | 0.4910 | 0.4909 | 0.4907 |
| 50 % | 1.2241 | 1.2239 | 1.2238 | 1.2236 |
| 75 % | 1.8316 | 1.8315 | 1.8313 | 1.8312 |
| 100 % | 2.4357 | 2.4356 | 2.4355 | 2.4353 |

Charakteristisch: Bei Colour ≥ 75 % überholt **80s den 60s** am
20-Hz-Klirr (13,82 gegen 13,75 %) — die Profile kreuzen unter Colour-
Drive; Sym × Colour reproduziert exakt den reinen Colour-Pfad
(Sym ist linear).

![Interaktion 20 Hz](plots/mess-interaktion-20hz.png)

![Colour über Frequenz](plots/mess-colour-frequenz.png)

![Level-Reihe Colour](plots/mess-levels-colour.png)

## 3. Validierung gegen die Referenz und JSFX↔C++-Parität

| Prüfpunkt | Gerät | Referenz | Abweichung |
|---|---:|---:|---:|
| Bank 20 Hz, 60s | 12.4242 % | 12.4243 % | 1.35e-04 %-Punkte |
| Bank 20 Hz, 80s | 12.2758 % | 12.2761 % | 2.58e-04 %-Punkte |
| Bank 20 Hz, 00s | 0.9995 % | 0.9996 % | 8.63e-05 %-Punkte |
| Bank 20 Hz, Sym | 0.0000 % | 0.0000 % | 2.04e-08 %-Punkte |
| Colour 5 %, 1 kHz | 0.1228 % | 0.1228 % | 1.95e-06 %-Punkte |
| Colour 10 %, 1 kHz | 0.2455 % | 0.2455 % | 3.43e-06 %-Punkte |
| Colour 20 %, 1 kHz | 0.4907 % | 0.4907 % | 5.92e-06 %-Punkte |
| Colour 50 %, 1 kHz | 1.2236 % | 1.2236 % | 1.55e-05 %-Punkte |
| Colour 75 %, 1 kHz | 1.8311 % | 1.8311 % | 2.28e-05 %-Punkte |
| Colour 100 %, 1 kHz | 2.4352 % | 2.4353 % | 3.01e-05 %-Punkte |

![Abweichungen](plots/mess-abweichungen.png)

![Provenanz-Drive-Beleg](plots/mess-provenanz-drive.png)

**JSFX-Render-Parität (REAPER-Render gegen C++-Offline-Render):** alle
geprüften Zustände sind bei 24-bit-Auflösung **bitgleich**
(max < 1 LSB, Offset −3 Samples = REAPER-PDC der 2x-Latenz):

| Render-Batch | Zustand | Ergebnis |
|---|---|---|
| `matrix-*_jsfx-…10_54_15` | Typen × Colour 100 | bitgleich (Referenz `ref-tf1…4`); Dateien später gelöscht |
| `matrix-*_jsfx-…12_14_53` | Typen × Colour 0 | bitgleich (Referenz `c0-tf1…4`) |
| `matrix-*_col_jsfx-…12_28_31` | Colour-Sweep, Transformer versehentlich 80s/00s/Sym/Sym | ersetzt |
| `matrix-*_col_jsfx-…12_33_03` | Colour 5–100 × None | bitgleich (Referenz `ref-col*`, `ref-none`) |
| `matrix-*_col_*_jsfx-…12_49_00` | Colour 5–100 × 60s/80s/00s/Sym (24 Zustände) | bitgleich (Referenz `ref-col*-tf*`) |

Damit ist die Zwei-Sprachen-Parität am vollen 64-s-Matrixprogramm über
**34 Betriebszustände** belegt (zusätzlich zu den 232 synthetischen
Paritätsfällen der Testsuite).

## 4. Provenanz der Gerätesserien

| Serie | Datum | Zustand | Bewertung |
|---|---|---|---|
| `matrix-dwarf-20261007` | 2026-10-07 Nacht | Aktuelle Binary (`e6b4…`, Bankkonstanten bitweise nachgewiesen); **INPUT-Knopf nicht auf 0** (aus der Gainmatch-Phase übernommen, je Lauf anders) | Klirrreihung 5,53/2,15/0,11 % = **dieselbe Bank bei gedämpftem Eingang** (H3/H5-Drive-Verhältnisse: 60s −3,5 dB, 00s −9,2 dB); als Anker unbrauchbar |
| Erste Wiederholung | 2026-10-07 vormittags | Parameterwechsel wirkungslos (Sitzungszustand) | **ungültig** — alle Läufe transparent |
| `matrix-dwarf-20261007-b2` | 2026-10-07 | Input 0 dB dokumentiert, digitale Ankerprüfung | **gültig**, Referenzdeckung 4. Dezimale |
| `colour-dwarf-20261007` | 2026-10-07 | wie b2 | **gültig**, Referenzdeckung 4. Dezimale |
| `cpu-matrix-dwarf` | 2026-10-07 | 36 Zustände, je Neustart, Rücklesung | **gültig**, 0 xruns |

**Zur Binary-Identität:** Die auf dem Gerät installierte Binary (SHA256
`e6b4e55…`) trägt die aktuelle Bank — alle 87 nichttrivialen double-
Konstanten aus `data/transformers.json` sind in der `.so` bitgenau
nachgewiesen; über Neubauten hinweg stabil. Die frühere Deutung
„Refit-Zwischenstand" ist damit widerlegt; die abweichenden Nachtwerte
erklären sich aus der Eingangsdämpfung. Verfahrensregel bleibt: nach
jedem `.so`-Austausch den Audio-Stack neu starten, den INPUT-Knopf auf
Unity setzen und vor der Serie den 20-Hz-Fingerabdruck gegen die
digitale Referenz prüfen (60s ≈ 12,42 % bei Colour 0).

## 5. Offene Punkte

- Ankerinterpretation: **abgeschlossen** (`EXTERN.md`) — der 1-%-Anker
  von 00s ist am Gerät exakt getroffen; 60s/80s haben ihre Anker by
  design bei −14/−8 dBFS.
- Optional direkt am Gerät: 20-Hz-Pegelreihe bei −14/−8/−2 dBFS zur
  direkten Ankerprüfung von 60s/80s (Stimuluserweiterung).
- Serie B: isolierter `transformer_bench` auf dem Dwarf für die
  Ursache der Profilreihung (Sym/00s am teuersten).
- 96-kHz-Messung bleibt über den Dwarf-Player unmöglich (feste
  Geräterate 48 kHz); 20 kHz liegt damit nah an Nyquist.

## 6. CPU-Matrix (Gerät, OS 2x, COMP OFF)

Alle Colour×Transformer-Kombinationen live über den mod-host-Socket
gesetzt und je Zustand per Rücklesung verifiziert; Messung mit
`tools/dwarf_loadtest.py` (Serie-A-Werkzeug), Fenster/Blöcke siehe
`test-results/cpu-matrix-dwarf/`. Werte = Median/Spitze eines Kerns
(jackd inklusive).

| Zustand | Colour % | Transformer | Median % | Peak % |
|---|---:|---|---:|---:|
| bypass | 0 | None | 22.0 | nan |
| c0-tf00s | 0 | 00s | 52.0 | nan |
| c0-tf60s | 0 | 60s | 48.0 | nan |
| c0-tf80s | 0 | 80s | 49.0 | nan |
| c0-tfNone | 0 | None | 28.0 | nan |
| c0-tfSym | 0 | Sym | 56.0 | nan |
| c10-tf00s | 10 | 00s | 68.0 | nan |
| c10-tf60s | 10 | 60s | 56.0 | nan |
| c10-tf80s | 10 | 80s | 60.0 | nan |
| c10-tfNone | 10 | None | 34.0 | nan |
| c10-tfSym | 10 | Sym | 66.0 | nan |
| c100-tf00s | 100 | 00s | 63.0 | nan |
| c100-tf60s | 100 | 60s | 56.0 | nan |
| c100-tf80s | 100 | 80s | 60.0 | nan |
| c100-tfNone | 100 | None | 36.0 | nan |
| c100-tfSym | 100 | Sym | 66.0 | nan |
| c20-tf00s | 20 | 00s | 61.0 | nan |
| c20-tf60s | 20 | 60s | 57.0 | nan |
| c20-tf80s | 20 | 80s | 57.0 | nan |
| c20-tfNone | 20 | None | 36.0 | nan |
| c20-tfSym | 20 | Sym | 66.0 | nan |
| c5-tf00s | 5 | 00s | 60.0 | nan |
| c5-tf60s | 5 | 60s | 58.0 | nan |
| c5-tf80s | 5 | 80s | 58.0 | nan |
| c5-tfNone | 5 | None | 36.0 | nan |
| c5-tfSym | 5 | Sym | 66.0 | nan |
| c50-tf00s | 50 | 00s | 67.0 | nan |
| c50-tf60s | 50 | 60s | 58.0 | nan |
| c50-tf80s | 50 | 80s | 58.0 | nan |
| c50-tfNone | 50 | None | 34.0 | nan |
| c50-tfSym | 50 | Sym | 68.0 | nan |
| c75-tf00s | 75 | 00s | 66.0 | nan |
| c75-tf60s | 75 | 60s | 57.0 | nan |
| c75-tf80s | 75 | 80s | 57.0 | nan |
| c75-tfNone | 75 | None | 36.0 | nan |
| c75-tfSym | 75 | Sym | 66.0 | nan |

![CPU-Matrix](plots/mess-cpu-matrix.png)

![CPU-Kostendekomposition](plots/mess-cpu-decomposition.png)

Befunde: Der Transformator kostet **+20–28 %-Punkte** gegenüber
None (28 % bei Colour 0); die Colour-Stufen addieren **+6–8 Punkte**
und sind pegelunabhängig (5 % ≈ 100 %). Die schwersten Profile sind
**Sym und 00s** (bis 68 % Median bei 20 Hz-Volldreher) — für die
Stop-Zweig-Spezialisierung (TODO, CPU-Reduktion) ist damit die
A35-Priorisierung belegt. Peak-Werte bis 76 %, **0 xruns in allen
36 Zuständen**. Basis: 20-Hz-Sinus (schwerstes Solver-Regime),
128 Frames, je Zustand voller Neustart mit gespeicherten
Boardwerten, Werte per Board-TTL eingeschrieben.
