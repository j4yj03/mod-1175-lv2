# Erster Jensen-Offlinefit und eigene Profile 60s / 80s / 00s

Stand **2026-10-05**, Green Stripe 76 **0.3.0**. Ausgeführt ist eine
eigenständige Offline-Identifikation, anschließend die vom Benutzer gewählte
Abstimmung **„warm → ausgewogen → clean“**.

## 1. Ergebnis

**Ein stabiler, lastgekoppelter erster Referenzkern und drei verwendbare
Offline-Profilentwürfe liegen vor.** Der Jensen-Fit ist ausdrücklich ein
**partieller Datenblattfit**, keine eindeutige Rekonstruktion der Hardware.

- Referenz: historisches Jensen **JT-11P-1**-Datenblatt 1/01, eingebettet
  in Whitlocks *Audio Transformers*, lokale PDF-Seiten 28–29.
- **53 Zielbedingungen**, davon **33 Training / 20 zurückgehalten**.
- Der abschließend ausgewählte vollständige Zustand trifft **18/20
  Validierungsintervalle**, **24/33 Trainingsintervalle**. Ein Treffer ist
  eine Übereinstimmung mit den beschriebenen groben Ablese-/
  Herstellerbereichen, kein unabhängiger Gerätestest.
- Stationärer Jensen-Kandidat: **0,02145 % THD bei +4 dBu / 20 Hz**
  gegenüber typisch 0,025 %. **−2,28468 dB** Gain gegenüber typisch −2,3 dB.
- Der typische **1-%-THD-Punkt** wird bei etwa **+20,49 dBu / 20 Hz**
  erreicht statt genau +20 dBu. Bei +20 dBu sind es etwa **0,591 %**;
  diese verbleibende Abweichung ist sichtbar und nicht als perfekter Fit
  ausgewiesen.
- Die drei eigenen Profile sind mit gemeinsamer digitaler Skalierung
  bei **−14 / −8 / −2 dBFS Peak** auf 1 % THD bei 20 Hz abgestimmt.
- Kausale Wellenformproben bei **768 kHz** gerendert, antialiasgefiltert
  auf **48 kHz** exportiert. Sie liegen unter `audio/` als Float-WAV vor.

Die numerischen Signal-/Konvergenz-/Lastprüfungen sind bestanden. Ein
Hörtest, REAPER-/Dwarf-Prüfung und C++/EEL2-Produktport sind nächste Arbeit.

## 2. Referenz und Herkunft

Originalquelle: `docs/sauce/Audio-Transformers-Chapter.pdf`, SHA256
`0e7a82774a90eee784897962ec3ed8ae17ac26122225a57596ef6c383f3bcc2d`.
Das Original wurde nicht verändert. Quellenkritik und Vorgeschichte:
[`../PARAMETERFIT_GRUNDLAGE.md`](../PARAMETERFIT_GRUNDLAGE.md),
[`../ERREGERSTROM_UND_MODELLVERGLEICH.md`](../ERREGERSTROM_UND_MODELLVERGLEICH.md).

Fixierte Hersteller-/Beschaltungswerte:

| Größe | Wert |
|---|---:|
| Übersetzung | 1:1 |
| Quellenwiderstand | 600 Ω differentiell |
| Primär-DCR | 1450 Ω |
| Sekundär-DCR | 1550 Ω |
| Sekundärlast | 10 kΩ |
| Quellsignal | Sinus, auf gewünschten **Primärklemmen-RMS-Pegel** kalibriert |
| DC-Bias | 0, eigene Erstmodellannahme |
| Sekundärdämpfungsnetz | im 10-kΩ-Testaufbau laut Blatt weggelassen |

Die in der Quelle genannten 98/110 pF sind Schirm-/Gehäusekapazitäten.
Sie wurden nicht ohne Begründung als differentielle HF-Kapazität eingesetzt.
Streuinduktivität und das gesamte kapazitive Netz sind nicht eindeutig
identifiziert; dafür gibt es einen **effektiven HF-Zweipol**.

## 3. Zielaufbereitung und Validierungstrennung

`targets.csv` enthält je Bedingung Quelle, Seite, Größe, Frequenz, Pegel,
Intervall, etwaigen typischen Wert und Training/Validierung.

- Amplitudenpunkte im Bass-/HF-Übergang, absolute Gain-/Impedanzgrenzen.
- DLP (*deviation from linear phase*), mit **einer gemeinsamen
  linearen Phasenreferenz**, nicht mit einer je Frequenz frei gesetzten Phase.
- THD+N-Pegelkurven bei 20/30/50 Hz und Frequenzkurven bei +4/+14/+20 dBu.
  Das Modell berechnet THD ohne synthetischen Rauschzusatz; Messnoise und
  Kennlinienablesung bleiben als Unsicherheit bestehen.
- Die **30-Hz-Pegelkurve** und die **+14-dBu-Frequenzkurve** wurden
  beim Fit nicht verwendet. Einzelne zusätzliche Amplituden-/Phasenpunkte
  bleiben ebenfalls zurückgehalten.

**Zwei bei genauerer Aufbereitung geklärte Punkte:**

1. Der Verlauf bei 150 kHz verlässt die y-Skala. Er wird nur als
   **einseitige Grenze** verwendet, nicht als erfundener −6,1-dB-Mittelpunkt.
2. Für den Subaudio-Amplitudensweep ist der Signalpegel nicht eindeutig
   angegeben. Die Punkte 0,2–5 Hz werden ausschließlich zur Identifikation
   des **linearen elektrischen Hintergrunds** benutzt. Sie werden nicht
   als nachgewiesene +4-dBu-Großsignalantwort oder als jungfräulicher
   Kleinstsignal-Stopzustand bezeichnet. Vollständige Zustandsmessungen
   mit bekanntem Pegel beginnen bei 20 Hz.

Der 20-Hz-Amplitudenpunkt benutzt die **veröffentlichte garantierte
Spanne −0,15…0 dB** mit schwachem Bezug zum typischen −0,04-dB-Wert.
Die einzelne typische Zahl hat keine erfundene Garantie ±0,025 dB.
Alle THD-Ableseintervalle bleiben grobe eigene Schätzintervalle.

## 4. Modellgleichungen

`core.cpp` ist eine **separate Offline-Referenz**, nicht Produkt-DSP.
`reference.py` bindet sie per `ctypes` ein.

### 4.1 Lastgekoppelter Flux-Zustand

Mit `Ra=Rsource+Rp`, `Rb=Rs+Rload`:

```text
lambda_dot = vcore
vcore = [vsource - Ra·iexc] / [1 + Ra/Rb + Ra·Gcore]
vout_raw = vcore · Rload/Rb

iexc = F(lambda) + (lambda-z)/Lrelax + Sum(wj·sj)
z_dot = omega_relax · (lambda-z)
```

Der Relaxationszweig ist ein dissipatives Serien-RL-Ersatzglied mit
`Rrelax=omega_relax·Lrelax`. Die lineare Leitfähigkeit `Gcore` ist eine
fixierte **Annahme** aus der Vorstudie, kein neu identifizierter Herstellerwert.

### 4.2 Sättigungsfamilien

Verglichen wurden vier glatte Potenzkerne, Fröhlich und vier verallgemeinerte
rationale Kerne, jeweils ohne und mit Stop-Gedächtnis:

```text
Potenz: F(lambda) = lambda/L0 · [1+(|lambda|/lambdaScale)^(p-1)]
         p = 3, 5, 7, 9

Fröhlich erweitert:
F(lambda) = lambda/L0 · [1+s·u/(1-u)] ; u=|lambda|/lambdaScale

Rational erweitert:
F(lambda) = lambda/L0 · [1+s·u^q/(1-u^q)] ; q=2,4,6,8
```

`s=1` ergibt den einfachen Fröhlich-Kern. Ein zusätzlich fitbares `s`
entkoppelt den steilen Hochpegelanstieg etwas vom kleinen Kernstrom;
das ist eine ausdrücklich eigene reduzierte Erweiterung.

### 4.3 Gedächtniszweig

Vierzehn symmetrische **Stop-Operatoren** mit festen Schwellen:

```text
rj = 0.00002, 0.00005, 0.0001, 0.0002, 0.0005, 0.001,
     0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5 V·s
sj_new = clamp(sj_old + lambda_new-lambda_old, -rj, rj)
wj = k_history · (rj/0.001)^beta
```

Das ist ein kleiner **Iwan-/Prandtl–Ishlinskii-artiger** Ersatz für
schmale Gedächtnisschleifen, keine identifizierte Material-Hysterese und
kein behaupteter vollständiger Jiles–Atherton-Kern. Positiv gewichtete
Stopzweige können Energie speichern und beim Gleiten dissipieren.
Ihre Zahl und Schwellen sind Modellannahmen; lediglich Gewichtsmaßstab
und Spektralsteigung werden gefittet.

Der Stop-`clamp` begrenzt den internen Hysteresezweig entsprechend dessen
Definition. Er ist **kein Audio-Limiter und kein Clamp des Flux-Zustands**.

### 4.4 HF-Ersatzfunktion

```text
HHF(jw) = 1/[1-(f/f0)^2 + j·f/(Q·f0)]
```

Sie wird als **effektive Kaskade** zum gemessenen Ausgang gerechnet.
Ihre innere kapazitive Last-Rückwirkung ist damit nicht vollständig
physikalisch aufgelöst. Die LF-Last-/Kernrückwirkung im Netz ist real
vorhanden; das HF-Netz bleibt ein Gray-Box-Surrogat.

## 5. Fitverfahren und abgeleitete Werte

- Deterministisch gesetzter Zufallsseed, SciPy `least_squares`.
- Acht Starts für die linearen Hintergrundparameter.
- **18 Kernvarianten × 2 Starts = 36 Basis-Fitläufe**, danach
  Verfeinerungen. Ein zusätzlicher Serien-R-Wirbelstrom-/Sättigungszweig
  wurde in vier Läufen untersucht und als unnötiger freier Parameter
  zurückgestellt: er fiel an die untere Grenze und verbesserte den Fit nicht.
- Primärpegel wird je Arbeitspunkt mit realem Quellenwiderstand kalibriert.
- Periodischer Zustand durch symmetrisches **Halbperioden-Shooting**;
  danach Harmonische H1…H31. Das beschleunigt das stationäre Fitting,
  ersetzt aber keine kausale Einschwingprüfung. Die Audio-Renderer verwenden
  **kein Shooting, keine Zustandskorrektur und keinen Reset pro Burst**.
- Trapezintegration, safeguarded Newton mit maximal 40 Schritten,
  deterministische Operationsreihenfolge; kein Fast-Math.
- Hauptresidual: Abstand zum Zielintervall. Innerhalb des Intervalls
  gibt es nur eine **schwache 0,15-Gewichtung** zum typischen/abgelesenen
  Mittelpunkt; einseitige Grenzwerte haben keinen Mittelpunktzwang.

**Ausgewählter Kandidat:** Fröhlich-artig mit schwachem Stop-Gedächtnis.

| Parameter | Abgeleiteter Wert | Aussage |
|---|---:|---|
| `L0` | ca. **3606 H** | effektiver Hauptflusszweig, nicht direkt gemessene Wicklungsinduktivität |
| `Lrelax` | ca. **1333 H** | effektiver Dispersions-/Verlustzweig |
| `frelax` | **0,2657 Hz** | niedrige Relaxationspolstelle |
| `Gcore` | **0,5 µS** | fixierte Vorannahme, 2 MΩ Ersatzverlust |
| `lambdaScale` | **0,09012 V·s** | gefitteter rationaler Kernmaßstab |
| `s` | **0,8372** | gefittete Stärke des nichtlinearen Anteils |
| `k_history` | **8,429×10⁻⁵ A/(V·s)** | Gewichtsstärke des angenommenen Stop-Spektrums |
| `beta` | ca. **0,00109** | nahezu gleiche Gewichte auf logarithmischen Stop-Schwellen |
| `f0_HF` | **108,257 kHz** | effektiver HF-Parameter |
| `Q_HF` | **0,66267** | effektive HF-Dämpfung |

Viele dieser Werte können mit einer anderen Stop-/Verluststruktur
anders ausfallen. Das JSON enthält volle numerische Präzision zur
Reproduktion, keine behauptete Materialgenauigkeit.

## 6. Wie gut passt der Jensen-Kandidat?

| Prüfpunkt | Quellenwert / Ziel | Vollständiges Modell |
|---|---|---:|
| 1 kHz Gain | typisch −2,3 dB, −2,6…−2,0 dB | **−2,28468 dB** |
| 1 kHz Eingangsimpedanz | 12,3…13,7 kΩ | **12,932 kΩ** |
| 20 Hz, +4 dBu THD | typisch 0,025 %, Ablese 0,021…0,031 % | **0,02145 %** |
| 1 kHz, +4 dBu THD | <0,001 % | **0,000342 %** |
| 20 Hz, +20 dBu THD | typisch 1 %, Ablese 0,72…1,30 % | **0,591 % — außerhalb** |
| 20 Hz 1-%-Pegel | typisch +20 dBu | **ca. +20,49 dBu** |
| 20 Hz Amplitude relativ 1 kHz | −0,15…0 dB, typisch −0,04 | **−0,00825 dB** |
| 20 kHz Amplitude relativ 1 kHz | −0,15…0 dB, typisch −0,05 | **−0,04568 dB** |
| 20 Hz DLP | abgelesen 0,4…0,85°, typisch ca. 0,6 | **0,939° — außerhalb der eigenen Ablese**, innerhalb ±2° Herstellergrenze |

Die zurückgehaltene 30-Hz-Pegelkurve wird **5/6** innerhalb der
Intervalle getroffen. Der fehlende 0-dBu-Punkt liegt nur knapp darüber:
0,01517 % gegenüber oberer Ablesegrenze 0,015 %. Die +14-dBu-
Frequenzbedingungen liegen **3/4** innerhalb; der 160-Hz-Punkt
ebenfalls minimal darüber. Ein dort guter Fit hebt die bleibenden
Trainingsfehler nicht auf.

Die größten sichtbaren Trainingsfehler liegen am steilen Hochpegelanstieg
und in einigen Kleinpegel-/Frequenzbereichen. Ein zusätzlicher rationaler
oder polynomialer Kandidat verbessert nicht alle zugleich. Die vielen
Pixelintervalle rechtfertigen keine unbeschränkte Modellkomplexität.

![Linearer Fit](plots/linear-fit.svg)
![Nichtlinearer Fit](plots/nonlinear-fit.svg)

**Kein perfektes PASS des gesamten Datenblattfits.** Die Signal-/
Numerikprüfungen bestehen; die Referenz gilt als erster brauchbarer,
ausdrücklich unvollständiger Gray-Box-Kandidat.

## 7. Eigene Profile nach Benutzerentscheidung

Die Profilnamen bedeuten musikalische Abstimmung, **keine Jahrzehnt-,
Hersteller- oder 1176-Revisionsidentität**. Die alten Gitarrentrafo-
Koeffizienten aus `xformer.lib` werden nicht weiterverwendet.

Gemeinsam: 1:1, gleiche Quelle/Last/DCR, gleiche digitale Eingangszuordnung,
symmetrisch, Null-DC, getrennte Zustände je gerendertem Signal.

| Eigenschaft | 60s | 80s | 00s |
|---|---:|---:|---:|
| Ziel | warm, weich/früh | ausgewogen | clean/Jensen-nah |
| Kennlinie | glattes Potenzgesetz `p=3` | glattes Potenzgesetz `p=5` | Fröhlich-artig wie Jensen |
| `L0` | 2344 H | 2885 H | 3606 H |
| `lambdaScale` | 0,007552 V·s | 0,024349 V·s | 0,085107 V·s |
| Hysteresestärke gegen Referenz | 2× | 1,5× | 1× |
| HF-`f0` | 26 kHz | 48 kHz | 108,257 kHz |
| HF-`Q` | 0,7071 | 0,7071 | 0,6627 |
| 20-kHz-Abweichung, linear rel. 1 kHz | **−1,304 dB** | **−0,129 dB** | **−0,046 dB** |
| 20-Hz-1-%-THD-Anker, digital Peak | **−14 dBFS** | **−8 dBFS** | **−2 dBFS** |
| Primärpegel an diesem Anker | ca. +7,99 dBu | ca. +13,99 dBu | ca. +19,99 dBu |
| THD bei +4 dBu / 20 Hz | **0,407 %** | **0,0289 %** | **0,0220 %** |
| THD bei +4 dBu / 50 Hz | **0,0406 %** | **0,0128 %** | **0,00969 %** |

Die Flussschwellen verschiedener Kennlinien sind nicht direkt als
gleiche physikalische Kniegrößen zu vergleichen. Die **einheitlichen
gemessenen 1-%-THD-Anker** sind der Vergleichsmaßstab.

`00s` ist leicht gegenüber dem partiellen Jensen-Fit nachkalibriert,
damit der eigene digitale Referenzanker genau erreicht wird. `60s`
verwendet bewusst einen weicheren p=3-Kern: ein früh erreichter
rationaler Grenzfluss führte zu unnötig abruptem Bassklirr. `80s`
liegt mit p=5 und höherem Maßstab dazwischen.

Für `00s` wird oberhalb **0,98·lambdaScale** ein monotoner C¹-
Hochfeldanschluss mit endlicher Steigung benutzt. Der angenommene
Hochfeld-L-Anteil ist `1e-4·L0`. Das verhindert eine unphysikalische
unendliche Kernstrompolstelle bei Stressproben; es ist **keine gefittete
Luftkerninduktivität**. Unterhalb dieses Anschlusses bleibt die
ausgewertete rational-förmige Kennlinie erhalten. `60s/80s` brauchen
diesen Anschluss nicht.

![Profile](plots/profiles.svg)

## 8. Digitale Skalierung und Gain

Gemeinsame Zuordnung: **−18 dBFS Peak des 1-kHz-Sinus → +4 dBu RMS
an den Primärklemmen** unter der Referenzbeschaltung. Der Quellmaßstab
liegt etwa bei 14,435 V pro digitaler Sampleeinheit.

Die Rohnetze enthalten ihre Einfügedämpfung. Für die mitgelieferten
Hörproben wird zusätzlich eine **explizite feste 1-kHz-/+4-dBu-
Normalisierung** verwendet, ungefähr Faktor **1,3612** je Profil.
Sie wird im Profil-JSON gespeichert. **Keine pegeldynamische
Auto-Makeup-Funktion**, keine Peaknormalisierung nach dem Rendern,
kein verdeckter Limiter.

Die Tabellen/CSVs dokumentieren Rohgain und Grundtonkompression weiter.
Die Normalisierung soll die Charaktere vergleichbar hörbar machen,
nicht die frequenz- oder pegelabhängige Abschwächung entfernen.

## 9. Numerische und kausale Prüfungen

Tatsächlich ausgeführt, Ergebnisse in `validation.json`:

| Prüfung | Befund |
|---|---|
| Periodisches Shooting / Newton-Residual | endliche Lösungen, Symmetrieabschluss <5×10⁻¹³ Größenordnung |
| 2048 gegen 8192 Punkte/Periode, 6 Fälle | größte THD-Differenz **<0,00008 dB**, Gain **<3×10⁻⁸ dB** |
| Unabhängiges DOP853-ODE-Verfahren, glatter Kern ohne Stops | THD-Differenz etwa **−0,000050 dB** |
| 30-s-Einschwingen dieser Gegenprobe | nötig, weil LF-Zustand langsam; frühes 8-s-Fenster wurde nicht als stationär akzeptiert |
| 3 Profile × 48/96/192 kHz, kausale Bassbursts/Stille | endlich, ausklingend, kein Zustandsshifting im Renderer |
| Positive/negative Eingangsprobe | gemessene Odd-Symmetrieabweichung **0 V** |
| Quellen-/Lastvariation | THD wächst bei höherem Quellenwiderstand; Lastabsenkung verändert Gain deutlich |
| Periodische Rohnetz-Leistungsbilanz | Quelle = Kupfer + Last + Kern; Kern-Zyklusmittel nicht negativ |
| 10-kHz-Kausalton 192/384/768 kHz | größte Gainänderung 384→768 kHz **0,00063 dB** |

Die Leistungsprüfung betrifft das **physikalisch gekoppelte Kern-/
Widerstandsnetz**, nicht eine vollständige Energieidentifikation des
nachgeschalteten HF-Surrogats. Jedes einzelne Power-Residual zu null
allein wäre nur KCL/KVL; zusätzlich wurden tatsächlich positiver
Kern-Zyklusverlust, Quell-/Lastverhalten und Konvergenz geprüft.

Die direkte 48-kHz-Tustin-HF-Näherung ist **nicht als produktionsreif
aliasfrei qualifiziert**. Bei HF-Polen oberhalb Nyquist bildet sie die
analoge Funktion nicht im ganzen Band unverzerrt ab. Die Audio-
Vorschauen werden deshalb bei 768 kHz erstellt und antialiasgefiltert
heruntergerechnet. Ein späterer Off/2×/4×-Port benötigt eine eigene
Rate-/Antialias-/Paritätsentscheidung.

## 10. Hörproben und Artefakte

Alle Proben: **12 s / 48 kHz / IEEE-Float**, 576000 Frames, ungeclippt.
Eingang: kurze 20-/50-/100-Hz-Töne bei −18/−8/−2 dBFS Peak und ein
80/240/1200-Hz-Multitone. Keine Musik-Hardwareaufnahme und kein bereits
durchgeführter Hörtest.

| Datei | Zweck |
|---|---|
| `audio/00-input.wav` | unveränderter synthetischer Eingang |
| `audio/60s-output.wav`, `80s-output.wav`, `00s-output.wav` | feste gainnormalisierte Profilausgänge |
| `audio/*-AB-input-output.wav` | Stereo: Eingang links / Profilausgang rechts; nicht phasenausgerichtet |
| `profile-matrix.csv` | **168 Arbeitspunkte**: 3 × 7 Frequenzen × 8 Primärpegel |
| `profile-waveforms.npz` | native periodische Roh-Kernwellenformen und gefilterte Ausgangsharmonische getrennt |
| `preview-waveforms.npz` | 48-kHz-Vorschauen und Flux-Auszüge |
| `targets.csv`, `fixture.json` | Original-/Ableseziel und Bedingungen |
| `linear-fit.json`, `fit-progress.json`, `jensen-fit.json` | Fitläufe, Auswahl, Starts und Parameter |
| `jensen-evaluation.csv`, `jensen-sweep.csv` | sämtliche Einzelabweichungen und Kurven |
| `profiles.json` | reproduzierbare eigene Profilparameter und Anker |
| `validation.json`, `artifact-audit.json`, `SHA256SUMS` | Signalprüfungen, Provenienz und Integrität |
| `plots/*.svg` | alle vier Abbildungen im Bericht |

Die WAVs sind absichtlich von der allgemeinen `*.wav`-Ignore-Regel
ausgenommen, ausschließlich in diesem Diagnoseordner. Sie gehören
nicht zu einem Plugin-Distributionspaket.

## 11. Reproduktion

Python-Abhängigkeiten unter `requirements.txt`; tatsächlich verwendet
Python 3.14.4, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2.
C++11, GNU g++ 15.2.0, `-O3 -ffp-contract=off`, kein Fast-Math.
Compiler und SciPy wurden für diese Umgebung unprivilegiert unter
`/tmp/opencode` bereitgestellt.

Bei vorhandener Standardtoolchain aus dem Repositoryroot:

```bash
g++ -std=c++11 -O3 -fPIC -shared -ffp-contract=off -Wall -Wextra \
  docs/transformer/offline_fit/core.cpp -o /tmp/opencode/transformer-reference.so

OPENBLAS_NUM_THREADS=1 python3 docs/transformer/offline_fit/fit.py \
  --library /tmp/opencode/transformer-reference.so --steps 1024 --max-nfev 60
OPENBLAS_NUM_THREADS=1 python3 docs/transformer/offline_fit/fit.py \
  --library /tmp/opencode/transformer-reference.so --resume-linear --refine-only --steps 2048 --max-nfev 40
OPENBLAS_NUM_THREADS=1 python3 docs/transformer/offline_fit/create_profiles.py \
  --library /tmp/opencode/transformer-reference.so
OPENBLAS_NUM_THREADS=1 python3 docs/transformer/offline_fit/render_and_plot.py \
  --library /tmp/opencode/transformer-reference.so
OPENBLAS_NUM_THREADS=1 python3 docs/transformer/offline_fit/validate.py \
  --library /tmp/opencode/transformer-reference.so
OPENBLAS_NUM_THREADS=1 python3 docs/transformer/offline_fit/finalize.py \
  --library /tmp/opencode/transformer-reference.so
```

`--dynamic-saturation` reproduziert die optionalen zusätzlichen
Serien-R-Experimente; sie wurden nicht zum benötigten Modellbestandteil.
Mehrfache Refinements lassen die gespeicherten Iterationshistorien wachsen,
ohne dass daraus eine neue unabhängige Datenbasis entsteht.

## 12. Nächster Schritt

1. Die drei WAV-Varianten auf dem Hörrechner vergleichen, insbesondere
   warme p=3-Bassfärbung und HF-Rundung des 60s-Profils.
2. Entscheiden, ob der erreichte **partielle Jensen-Fit** für eine eigene
   Klangstufe genügt oder ob die genannten Restfehler weitere
   Magnetisierungs-/Harmonischenmessungen rechtfertigen.
3. Für einen Produktport die Stop-Spektrum-Komplexität und interne
   Rate/HF-Approximation beurteilen, dann C++/EEL2 gemeinsam bauen.
4. Link-/Bypass-/Mix-/Preset-/Latencyverhalten und Dwarf-CPU nach den
   bestehenden Vorgaben prüfen. Kein Produkt-DSP wurde in diesem Fitauftrag
   geändert.
