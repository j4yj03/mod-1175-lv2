# SPICE-Auswertung der vier Transformator-Netzmodelle

Stand: **2026-10-05**, Green Stripe 76 **0.3.0**, Ausgangscommit
`77a25fdf895f0bada552426f47d1b6c2d50c84ff`.
Auftrag: [`../SPICE_AUFTRAG.md`](../SPICE_AUFTRAG.md).

## 1. Ergebnis

**Die Simulation bestätigt die bisherige skalare Knie-Herleitung für keine der
vier Stufen. Aus den gelieferten Netzen lässt sich keine belastbare,
zeitunabhängige Transformator-Kalibrierung ableiten.**

Die vollständige Hauptmatrix ist gerechnet: **4 Modelle × 5 Frequenzen ×
13 Pegel = 260 Transientenläufe**, jeweils zusätzlich `.ac dec 200 20 20k`.
Dazu kommen **76 Diagnoseläufe** und **vier dokumentierte Abbruchversuche** mit
der wörtlich eingebundenen Originalbibliothek. Simulator: **ngspice 45.2**.

Wesentliche Befunde:

1. Die Modelle sind laut Kommentar **Audio-Ausgangsübertrager für
   Röhrenverstärker**, keine ZF-Modelle. Ihre tatsächlichen Gleichungen bilden
   jedoch **keinen passiven, reziproken Transformator**: Die Sekundärspannung
   wird durch eine ideale gesteuerte Spannungsquelle ausgegeben; der
   Sekundärstrom wirkt nicht auf den Primärkreis zurück.
2. Alle vier Netze haben um den Nullzustand einen **positiven reellen Pol**.
   Eine Anfangsstörung von nur `10⁻⁷ V` an der modellinternen Kapazität wächst
   bei **Nullsignal** an. Der Effekt bleibt bei halbiertem Zeitschritt und
   anderer Integrationsregel erhalten.
3. Die kurzen Messfenster zeigen überwiegend **Expansion**, keine Sättigungs-
   kompression. Spätere Fenster liefern andere Gains und Gleichanteile.
   Ein optisch glatter Frequenzgang oder ein kurzer nahezu konstanter Sinus
   ist daher kein Nachweis eines eingeschwungenen, stabilen Übertragers.
4. `φ_k`, Kniebreite, ein aus der Übertragung gefitteter Sättigungsexponent
   und stationärer DC-Offset sind **nicht bestimmbar**. In
   [`coefficients.json`](coefficients.json) stehen dafür ausdrücklich `null`
   mit Begründung, keine Ersatzschätzungen.

Die klaren Aussagen je Stufe und der geforderte Vergleich stehen in Abschnitt 7.
Alle 260 Messzeilen sind zusätzlich lesbar in
[`MESSWERTE.md`](MESSWERTE.md); die CSVs enthalten mehr Stellen und sämtliche
Betriebspunkte. Die Ergebnisse sind eigene Rechnungen, keine Gerätemessung.

## 2. Modellprüfung und Korrekturen am Auftragsverständnis

### 2.1 Tatsächliche Ausgangslage

Im aktuellen `src/dsp/GreenStripe.hpp` ist `transformer` nur ein mitgeführter
Steuerwert. Eine aktive skalare Transformator-Sättigung, wie in Abschnitt 0 des
Auftrags beschrieben, existiert dort **nicht**. Die verglichenen `φ_k`-Werte
stammen aus der bisherigen **Architekturplanung**.

`GCSYMETRICAL` bleibt entsprechend dem Originalhinweis **„Only for testing
purposes“** eine Prüfreferenz. Seine Zahlen werden nicht als Klangrevision
interpretiert.

### 2.2 Ports, Bauteile und Herkunft

Die folgenden Zahlen sind **Eingangsdaten aus `xformer.lib`**, keine Messwerte:

| Stufe / Kennung | Primär / Sekundär | `C` | `a` / `n` | `R` | `b` / `m` | `Np` / `Ns` |
|---|---|---:|---|---:|---|---|
| 60s / GCOT-SE-01 | P1–P2 / S1–S2, kein CT | 0,000709428 | 8792,792558 / 13 | 31,39505785 | 58,96858796 / 2 | 2012 / 72 |
| 80s / GCOT-PP-03 | P1–CT und P2–CT / S1–S2 | 0,012790087 | 11683,51058 / 6 | 6,259141117 | 4,89849808 / 3 | 668 / 48 |
| 00s / GCOT-PP-04 | P1–CT und P2–CT / S1–S2 | 0,002610317 | 11434,182 / 8 | 8,860791571 | 10,401883352 / 2 | 1996 / 64 |
| Symmetric / GCSYMETRICAL | P1–CT und P2–CT / S1–S2 | 0,002 | 0,00001 / 25 | 2,3 | 8,4 / 4 | 200 / 100 |

- Push-pull benutzt je Halbwicklung `Np/2`, aber **zwei unabhängige
  `CORE_GC`-Blöcke**, nicht einen gemeinsamen Kern.
- `m` ist der Exponent von `b·|V(N3,N4)|^m·sgn(V(N3,N4))`, **kein
  Kopplungsfaktor**. Es gibt kein `K`-Element und keine definierte
  magnetische Kopplungskonstante.
- `Rr N3 N4` und `Br N3 N4` liegen **parallel**. Der Kommentar „resistor in
  series with a nonlinear source“ ist unzutreffend. Dieser Parallelzweig
  liegt hinter der Spannungsquelle `Bc`. `R` ist kein ausgewiesener
  Wicklungs-Serienwiderstand; `b` ist kein weiterer Widerstand.
- `Bc` erzeugt eine **Spannung**, keinen Magnetisierungsstrom.
  Die als „flux“ kommentierte Größe `V(N1,N2)` ist zunächst eine
  Kondensatorspannung in Volt. Eine Abbildung auf Weber ist nicht angegeben.
- Der Quelltext verwendet `Bp = Np·DDT(I(Vp))`, nicht
  `Np·DDT(V(N1,N2))`. `Bs = Ns·I(Bp)` ist eine Transimpedanzbeziehung.
  Der erwartete Spannungsfaktor `Ns/Np` folgt daraus nicht.

Die lokale Begleitschaltung
`../sauce/Push-Pull Transformer (Gyrator-Capacitor).cir` zeigt für `GCOT-PP-04`
zwei `6V6GT`-Modelle, **394 V** am CT und **8 Ω** Sekundärlast.
Der auskommentierte `GCSYMETRICAL`-Test benutzt gegenphasige **150-V-Peak /
30-Hz**-Quellen, **100 Ω je Primärzweig** und **1 kΩ** Last. Das sind
Verwendungsbeispiele, **keine dokumentierten Charakterisierungsmessungen**.
Für SE-01 und PP-03 sind ursprüngliche Quellenimpedanz, Last und Bias unbekannt;
auch für PP-04 liegt keine identifizierte Charakterisierungsquelle vor.

Der Kommentar „5 W, 70 Hz–15 kHz“ steht nur bei SE-01. Die in der bisherigen
Planung verwendeten 20-Hz–20-kHz-Bänder für PP-03/04 sind kein zusätzlicher
Messbeleg aus dieser Bibliothek.

**Einordnung:** Kein Anlass für eine zweite, erfundene ZF-Schaltung. Simuliert
wird die tatsächliche Audio-Verhaltensschaltung. Ein physikalisch reparierter
Übertrager wäre ein neues Modell und ist durch diese Messung nicht abgedeckt.

## 3. Simulationsaufbau

### 3.1 Randbedingungen

| Größe | Verwendete Einstellung / Definition |
|---|---|
| Frequenzen, transient | 20, 100, 1000, 10000, 20000 Hz |
| Pegel | −30 bis +6 dBV in 3-dB-Schritten, 13 Werte |
| Pegelbezug | Effektivwert der **unbelasteten differentiellen Quelle**; Sinuspeak `√2·10^(dBV/20)` |
| Quelle SE | ein Sinus, 200 Ω in Serie, P2 an Masse |
| Quelle PP | zwei gegenphasige Sinusse, jeweils halbe differentielle Amplitude, je 100 Ω in Serie, CT an Masse |
| Sekundärlast | 8 Ω, S2 an Masse |
| DC / Initialisierung | 0 V Quelloffset, SPICE-DC-Arbeitspunkt; separat bezeichnete Störungsprüfung mit `UIC` |
| Temperatur | ngspice-Default 27 °C; keine temperaturabhängigen Bauteile im Netz |
| Basisausgabe | 48 kHz, `TSTEP=1/48000 s`; zusätzlich native adaptive Zeitpunkte |
| Solver | Trapez, `reltol=1e-7`, `abstol=1e-14`, `vntol=1e-12`, SPARSE 1.3 |
| Maximaler Schritt | `min(1/48000, 1/(256·f)) s` |
| Hauptfenster | Start `max(40 ms,20/f)`, Länge `10/f` |
| AC | 601 Frequenzpunkte, `.ac dec 200 20 20k`, Nullarbeitspunkt |

200 Ω / 8 Ω sind **eigene, offengelegte Testbedingungen**. Die
Primärklemmenpegel werden zusätzlich gemessen (`primary_h1_rms_v`,
`gain_primary_db` usw.). Der Unterschied zum Quellenpegel ist erheblich;
die CSV verschweigt die Belastung der Quelle nicht.

Keine Wicklungs- oder Kernkoeffizienten wurden angepasst. Zusätzliche Lasten
4 Ω / 1 kΩ und Quellenimpedanzen 20 Ω / 2 kΩ sind **separate Diagnoseläufe**.
Ein Ruhestrom einer realen Single-ended-Röhrenstufe wurde nicht erfunden.

Die Anweisung `.tran 0 40m 48k` ist keine 48-kHz-Abtastratenangabe:
Der dritte Wert wäre ein Startzeitpunkt von 48000 Sekunden. Außerdem sind
40 ms bei 20 Hz weniger als eine Periode. Deshalb stehen in jeder Netlist
gültige Zeitparameter und frequenzabhängige Beobachtungsfenster.

### 3.2 48-kHz-Ausgabe und Harmonische

Eine analoge SPICE-Transientenanalyse besitzt keine feste Audio-Abtastrate.
Hier ist **48 kHz das Exportgitter**, der Solver arbeitet feiner. Der Export
enthält linear interpolierte **Punktabtastungen ohne Antialiasfilter** und
ist kein fertiger Audio-Render für einen Hörvergleich.

Bei 10 kHz liegen H3/H5 bei 30/50 kHz, bei 20 kHz bei 60/100 kHz.
Diese Harmonischen lassen sich aus einem 48-kHz-Signal nicht unverfälscht
bestimmen. Die angegebenen analogen H3/H5 werden daher an den **nativen,
adaptiven SPICE-Zeitpunkten** gemessen. Die Schrittgrenze entspricht
mindestens 256 Punkten pro Grundperiode; H5 erhält mindestens rund
51 Punkte pro Periode. Werte oberhalb 24 kHz sind entsprechend bezeichnet.

### 3.3 ngspice-Portierung ohne Koeffizientenänderung

1. **Originalbibliothek direkt:** Alle vier Transienten brechen mit
   `singular matrix` / `Timestep too small` ab. Die AC-Ausgabe ergibt dabei
   Ausgang 0 und ist als Referenz unbrauchbar. Netlists und Logs heißen
   `*__literal__f1000__p0dBV.*`. Ein Exitcode 0 wurde nicht mit erfolgreicher
   Simulation verwechselt; der Runner prüft Log, Endzeit und endliche Daten.
2. **Ableitungsrealisierung:** `xformer-ddt.inc` bildet
   `N·dI(Vp)/dt` durch eine stromgesteuerte Stromquelle mit Faktor 1 und
   eine Hilfsinduktivität mit Wert `N` ab. Ihr Strom ist `I(Vp)` und ihre
   Spannung exakt `N·dI(Vp)/dt`. Diese Induktivität ist **keine zusätzlich
   angenommene Wicklungsinduktivität**. Lediglich vier falsche `.ENDS`-Namen
   wurden außerdem berichtigt. Diese Schaltung ermöglicht die unabhängige
   Gegenprüfung, ist bei hohen Frequenzen aber numerisch schlecht konditioniert.
3. **KCL-Zustandsrealisierung:** `xformer-ngspice.inc` eliminiert die
   differenzierende algebraische Schleife mit den **gleichen
   Netzwerkgleichungen**. Damit laufen sämtliche 260 Fälle. Die Herleitung
   folgt in Abschnitt 5; auch das problematische Vorzeichen bleibt erhalten.

Alle acht DDT-Gegenproben bei 20 Hz / −30 und +6 dBV stimmen mit der
KCL-Fassung überein: maximale Gain-Differenz **3,28×10⁻⁹ dB**, maximale
H3-Differenz **1,12×10⁻⁶ dB**. Die 601-Punkte-AC-Kurven unterscheiden sich
höchstens um **6,83×10⁻¹³ V**. Belege:
`diagnostic-manifest.json`, Einträge `ddt_equivalent`.

## 4. Messdefinitionen und Ergebnisse

### 4.1 Definitionen

- `H1 = Vout,1 / Vsource,1`, zusätzlich `H1,port = Vout,1 / Vprimary,1`.
- `M = |H1|/|H_ac|`; **K = 20·log10(1/M)**. Positive K bedeuten
  Kompression, negative K Expansion. `−20·log10(|H1|)` allein wäre nur
  Einfügedämpfung und kein Kompressionsmaß.
- Harmonische: zeitgewichtete Least-Squares-Anpassung von DC,
  linearer/quadratischer Drift sowie H1…H9 an sämtliche nativen Punkte
  des Beobachtungsfensters. `H3/H1`, `H5/H1` in dBc. `H3−H5` ist die
  Differenz dieser dB-Werte, kein separates Intermodulationsprodukt.
- Berichtsschwelle **−120 dBc**. Darunter stehen in der CSV rohe
  Diagnosezahlen mit `below_reporting_floor`; daraus wird keine
  Kniehärte abgeleitet.
- DC: zeitgewichteter Fenstermittelwert. Weil SPICE `TSTART` geringfügig
  überschreiten kann, ist das native Fenster leicht kürzer als zehn volle
  Perioden. Zusätzlich gespeichert: DC-Fit, Drift, Min/Max und Fitresidual.
  Sehr kleine DC-Zahlen sind **keine nachgewiesene Gleichrichtung**.
- Gruppenlaufzeit: `−d unwrap(arg H_ac)/dω` nur für die formale
  AC-Linearisierung. Die Phase eines einzelnen driftenden Großsignals
  liefert keine belastbare allgemeine Gruppenlaufzeit.
- `within_thresholds` prüft nur das jeweilige kurze Fenster: Änderung
  des Gains zwischen Hälften <0,01 dB, Ausgangsdrift <10⁻⁴ der
  Ausgangsgrundwelle, Cc-Drift <10⁻³ seiner Grundwelle. **Keine Aussage
  über Langzeitstabilität.**

Die Schwäche einer reinen Polynom-Driftentfernung wird gerade beim langsamen
`Symmetric`-Versuch sichtbar: bei 20 Hz / +6 dBV gibt der Fit H3 ≈ −87,69 dBc
aus, bei 1 kHz dagegen ≈ −107,91 dBc. Der langsame wachsende Anteil kann in
einem endlichen Fenster in Harmonische hineinprojizieren. Auch ein
zeitschrittkonvergenter Fit ist deshalb nicht automatisch stationärer Klirr.

### 4.2 Hauptfenster bei 1 kHz / +6 dBV

Messfenster 40–50 ms. Je Zeile `*-results.csv`, Fall
`<Kennung>__main__f1000__p6dBV`, gleichnamige Netlist in `netlists/`.

| Stufe | H Quelle→Out dB | Phase ° | K dB | H3/H1 dBc | H5/H1 dBc | H3−H5 dB | DC-Fenstermittel V |
|---|---:|---:|---:|---:|---:|---:|---:|
| 60s | −8,925879 | 0,000013 | **−1,214553** | −61,61 | −68,62 | 7,00 | 4,90×10⁻⁶ |
| 80s | −12,866654 | <0,000001 | **−0,056448** | −54,84 | −75,31 | 20,48 | 8,92×10⁻⁷ |
| 00s | −10,110006 | −0,000002 | **−0,524425** | −51,25 | −59,38 | 8,13 | 2,36×10⁻⁶ |
| Symmetric | −6,218032 | <0,000001 | **−0,000082** | −107,91 | <−120 | nicht bestimmbar | 4,90×10⁻⁵ |

Die drei eigentlichen Typen liefern **mehr Gain als ihre
Kleinsignal-Linearisierung**, nicht die erwartete komprimierende Kniekurve.
Bei `60s` sinkt H3 mit steigendem Pegel im 1-kHz-Fenster sogar von etwa
−46,67 dBc bei −30 dBV auf −61,61 dBc bei +6 dBV. Eine Ableitung von `n`
aus einer angenommenen monotonen Sättigung wäre hier unbegründet.

![Pegel und Klirr](plots/pegel_und_klirr.svg)

### 4.3 Gleiche Anregung, andere Beobachtungszeit

20 Hz / +6 dBV, K jeweils auf dieselbe AC-Referenz bezogen.
Quelle: Haupt-CSVs und `diagnostic-results.csv`, Tags `late5`, `late20`.

| Stufe | K bei 1,0–1,5 s dB | K bei 5,0–5,5 s dB | K bei 20,0–20,5 s dB | DC bei 1,0–1,5 s V | DC bei 20,0–20,5 s V |
|---|---:|---:|---:|---:|---:|
| 60s | −1,212935 | −1,132837 | +0,278806 | 0,005138 | 0,000327 |
| 80s | −0,056447 | −0,056430 | −0,008167 | 0,001589 | 0,001646 |
| 00s | −0,524421 | −0,508830 | −0,037990 | 0,003707 | 0,000452 |
| Symmetric | +0,000875 | +11,609387 | +25,035808 | 0,210561 | 0,000801 |

Alle späten Fenster sind als driftend erkannt. Besonders aufschlussreich:
bei **−30 dBV** hat `60s` nach 20 s bereits **+1,711672 dB** K, also mehr
als bei +6 dBV. Bei `Symmetric` sind es **+24,155641 dB**. Das ist keine
brauchbare monotone, nur von Amplitude/Frequenz bestimmte Sättigungskennlinie.

![Zeitabhängigkeit](plots/zeitabhaengigkeit.svg)
![Wellenformen](plots/wellenformen.svg)

### 4.4 AC, Phase und Last

Die formalen AC-Gains bei 20 Hz → 20 kHz betragen:

| Stufe | H(20 Hz) dB | H(20 kHz) dB | AC-Phase / Gruppenlaufzeit |
|---|---:|---:|---|
| 60s | −10,140817 | −10,140432 | numerisch 0° / 0 s |
| 80s | −12,923230 | −12,923101 | numerisch 0° / 0 s |
| 00s | −10,634641 | −10,634430 | numerisch 0° / 0 s |
| Symmetric | −6,220862 | −6,218113 | numerisch 0° / 0 s |

Quelle: vier `*-ac.csv`, jeweils 601 Punkte mit komplexen Spannungen und
numerischer Phasenableitung. Das ist die erzwungene AC-Lösung um einen
**instabilen Arbeitspunkt**, kein stabiler LTI-Frequenzgang eines realen
Übertragers. Aus der verschwindenden Phase folgt hier keine Minimalphasigkeit.

Lastwechsel 4 Ω ↔ 8 Ω ↔ 1 kΩ bei 20 Hz / +6 dBV ändern den gemessenen
Gain um höchstens **2,7×10⁻¹⁵ dB**. Das bestätigt die fehlende
Last-Rückwirkung. Quellenimpedanz wirkt dagegen stark, z. B. `60s`:
**+3,0840 dB** mit 20 Ω versus **−28,8901 dB** mit 2 kΩ.
Netlists: `*__load4__*`, `*__load1000__*`, `*__rs20__*`, `*__rs2000__*`.

## 5. Warum die Zustände instabil sind

**Eigene algebraische Herleitung aus der Originalnetlist**, keine empirisch
angepasste Ersatzgleichung.

Für eine Halbwicklung sei

- `u = V(C1,C2)` bei SE bzw. `V(C1,C3)` / `V(C2,C4)` bei PP,
- `S(u) = a·|u|^n·sgn(u)`,
- `q = v_primary − S(u)` gegen P2 bzw. CT,
- `j = q/R + b·|q|^m·sgn(q)` der Strom im Rr/Br-Parallelzweig,
- `N_h = Np` bei SE, `Np/2` bei PP,
- `w = −I(Vp)` für SE/erste PP-Hälfte bzw. `+I(Vp2)` für die zweite Hälfte.

KCL und die Spannungsquelle `Bp` ergeben exakt:

```text
C · du/dt = j + w
N_h · dw/dt = u

vout_SE = Ns · (j + w)
vout_PP = Ns/2 · [(j1 + w1) − (j2 + w2)]
```

Die zweite Gleichung hat das **positive** Vorzeichen. Da `n>1` und `m>1`,
verschwindet die Ableitung von `S` im Nullpunkt. Ohne Eingang gilt dort
`j=0`, unabhängig vom Quellenwiderstand. Damit:

```text
d²u/dt² = u / (C · N_h)
p_± = ±1 / sqrt(C · N_h)
```

Ein Pol liegt in der rechten Halbebene. Mit kleiner Cc-Anfangsspannung und
`w(0)=0` wächst `u` zunächst wie `cosh(t/sqrt(C·N_h))`.

### SPICE-Nachweis mit Nullsignal

Die Tabelle enthält **gemessene** Wachstumsraten aus logarithmischem Fit,
daneben den unabhängig berechneten Pol. Fit vor Sättigung, nach der
anfänglichen `cosh`-Überleitung. Daten: `diagnostic-manifest.json`,
`check=unstable_zero_input`; Kurven: `diagnostic-waveforms.npz`.
Netlists: `<Kennung>__zero_initial__f20__m30dBV.cir`; trotz des formalen
Dateinamens setzen diese Decks **`AMP=0`**.

| Stufe | Pol aus Netzgleichung s⁻¹ | SPICE-Wachstum s⁻¹ | gemessene e-Faltungszeit s | `u` nach 20 s V |
|---|---:|---:|---:|---:|
| 60s | +0,837012 | +0,836965 | 1,19479 | 0,412421 |
| 80s | +0,483827 | +0,483798 | 2,06698 | 0,000796961 |
| 00s | +0,619567 | +0,619532 | 1,61412 | 0,0120353 |
| Symmetric | +2,236068 | +2,235942 | 0,447239 | 1,79437 |

Größte relative Differenz zwischen Messfit und Pol: **0,0061 %**.
Die Nichtlinearität bremst später das Wachstum; daraus folgt **kein
stabiler ursprünglicher Nullarbeitspunkt**. Ein Verschweigen des Einschwingens
oder bloßes Umdrehen des Vorzeichens wäre eine Modelländerung.

![Nullsignal-Instabilität](plots/nullsignal_instabilitaet.svg)

Auch die AC-Werte sind algebraisch prüfbar:

```text
H_SE(s) = Ns/(Rs + R)   · (C·Np·s²)/(C·Np·s² − 1)
H_PP(s) = Ns/(Rs + 2R)  · (C·(Np/2)·s²)/(C·(Np/2)·s² − 1)
```

Bei `s=jω` wird der letzte Faktor `C·N_h·ω²/(C·N_h·ω²+1)`, rein reell.
Die Formel reproduziert die gemessenen AC-Gains mit maximal
**5,4×10⁻¹⁵ dB** Differenz. Der unauffällige AC-Betrag verdeckt also gerade
den instabilen Pol.

## 6. Numerische Gegenprüfungen

Die Grenzen unten gelten für die ausgeführten **24 Verfeinerungsläufe**
(vier Modelle × 20/1000/20000 Hz × −30/+6 dBV). Nicht für ungeprüfte
beliebige Spannungen extrapolieren.

| Prüfung | Ergebnis / Artefakt |
|---|---|
| Alle 260 Haupttransienten bis zur vorgesehenen Endzeit, endlich | bestanden, `run-manifest.json`, Logs |
| Maximaler Schritt halbiert, `reltol` halbiert | max. Gainänderung **1,55×10⁻⁷ dB** |
| Phasenänderung dieser Verfeinerung | max. **1,68×10⁻⁵ Grad** |
| H3/H5-Verfeinerung oberhalb −120 dBc | max. **0,00071 dB** |
| Gear statt Trapez, 8 Fälle | max. Gainänderung **5,88×10⁻⁸ dB** |
| Unabhängige DDT-/Induktorrealisierung, 8 Fälle | max. Gainfehler **3,28×10⁻⁹ dB** |
| Lastwechsel, 8 Fälle | erwartete fehlende Rückwirkung bestätigt |
| Quellenimpedanz, 8 Fälle | deutliche Abhängigkeit dokumentiert |
| Längere Fenster, 16 Fälle | **keine stationäre Kalibrierung erreicht** |
| Nullsignal-Anfangsstörung, 4 Fälle | **Instabilität bestätigt** |

Ein numerisch bestandener Lauf qualifiziert die Schaltung nicht als
physikalisch richtigen Transformator. Die Modellinstabilität ist das
inhaltliche Ergebnis, kein übergangener Testfehler.

## 7. Geforderte Knieparameter und klare Aussage je Stufe

Die alten Zahlen lassen sich **arithmetisch** aus `(C·ω/a)^(1/(n−1))`
reproduzieren. Das ist aber nicht ihre Verifikation durch Simulation:
In der Netlist ist `a·|u|^n` eine **Spannung**, während `C·ω·u` einen
**Strom** beschreibt. Deren Gleichsetzung ist ohne zusätzliche
Normalisierung dimensionswidrig. Weiterhin ist `u` nicht als physikalischer
Fluss identifiziert. Die im Auftrag verlangte Abweichung „unter 10 %“
ist deshalb nicht sinnvoll auswertbar.

| Stufe | Alte Zahl, nur nachgerechnete Formel | Neues `φ_k(f)` | Kniebreite / gefittetes `n` | DC-Offset | Aussage |
|---|---:|---|---|---|---|
| 60s | 0,532471 bei 1024,695 Hz | nicht bestimmbar | nicht bestimmbar; vorgegebenes `n=13` ist kein Fit | nur zeitabhängige Fenstermittel | **Skalar nicht bestätigt:** Expansion, instabiler Zustand, sogar stärkere späte K beim leiseren Signal |
| 80s | 0,337056 bei 632,456 Hz | nicht bestimmbar | nicht bestimmbar; `n=6` nur Eingangsdaten | driftend | **Skalar nicht bestätigt:** kein komprimierendes Knie in der Hauptmatrix; positive Eigenmode trotz zunächst kleiner Effekte |
| 00s | 0,367608 bei 632,456 Hz | nicht bestimmbar | nicht bestimmbar; `n=8` nur Eingangsdaten | driftend | **Skalar nicht bestätigt:** Expansion und Beobachtungszeit-/Quellenabhängigkeit |
| Symmetric | 1,761341 bei 632,456 Hz | nicht bestimmbar | nicht bestimmbar; `n=25` nur Eingangsdaten | stark zeitabhängig | **Prüfreferenz fällt als stabiler Referenzkern durch:** bei Nullsignal schnellste Eigenmode, nach 20 s rund 25 dB K bei +6 dBV |

Das bedeutet nicht, dass jede denkbare skalare Klangfärbung ungeeignet wäre.
Es bedeutet konkret: **Diese Netzmodelle liefern weder eine Bestätigung noch
einen belastbaren Zahlenersatz für den geplanten Green-Stripe-Kern.**

In `coefficients.json` werden die messbaren Diagnosekoeffizienten
(Wachstumsrate und deren Zeitkonstante) von rein algebraischen
Zustandskoeffizienten und nicht identifizierbaren Klangparametern getrennt.
Es gibt keine neu freigegebene DSP-Parametertabelle.

## 8. Artefakte und Reproduktion

Der vom Benutzer gewünschte Ordner **`docs/spice_sim/`** ersetzt die im
Auftragsdokument beispielhaft genannten Ausgabepfade `docs/sauce/sim/`.

| Datei / Ordner | Inhalt |
|---|---|
| `<Kennung>.cir` | vier direkt ausführbare Einstiegsdecks, 1 kHz / 0 dBV und AC |
| `netlists/` | 340 exakt parametrierte Haupt-/Diagnose-/Originalversuchsdecks |
| `xformer-ngspice.inc` | KCL-äquivalente, tatsächlich verwendete Realisierung |
| `xformer-ddt.inc` | unabhängige Realisierung mit Hilfsinduktivitäten |
| `<Kennung>-results.csv` | je 65 vollständige Messzeilen mit Quellen-/Primärbezug |
| `<Kennung>-ac.csv` | je 601 komplexe AC-Messpunkte |
| `MESSWERTE.md` | alle 260 Hauptmessungen als lesbare Tabellen |
| `*-waveforms.npz` | float64-Wellenformauszüge: erster und letzter ausgewerteter Zyklus, native Zeitpunkte und 48-kHz-Punktabtastung |
| `diagnostic-waveforms.npz` | wie oben; Nullsignal zusätzlich über volle 20 s mit etwa 1-ms-Abstand, echte Solverpunkte |
| `<Kennung>-literal.npz` | AC-Ausgabe der fehlgeschlagenen Originalversuche, keine gültigen Transienten |
| `logs/` | unveränderte Simulatorlogs aller 340 Läufe |
| `run-manifest.json`, `diagnostic-manifest.json` | Betriebspunkte, Version, Hashes, Endstatus, Gegenprüfungen |
| `coefficients.json` | ausdrücklich bezeichnete Diagnosekoeffizienten und nicht bestimmbare Parameter |
| `quality-summary.json` | numerische Prüfergebnisse |
| `plots/` | vier SVG-Abbildungen aus den Messdateien |
| `analysis-provenance.json` | Analyseversionen und Eingabehashes |
| `verify_results.py`, `verification.json` | Konsistenz- und Reproduktionsprüfung |
| `SHA256SUMS` | Integrität der abgelegten Artefakte |

Die vollständigen nativen Fenster wurden ausgewertet; archiviert sind deren
erste und letzte Periode. Die **Zeitlücke ist an der Zeitspalte erkennbar**,
die Auszüge dürfen nicht zu einer zusammenhängenden FFT verkettet werden.
Die Manifeste enthalten Hashes vollständiger Haupt-/Zustands-Diagnosearrays.
Alle vollständigen Fenster sind mit den Netlists erneut erzeugbar.

Spalten der NPZ-Arrays:
`time_s, source_v, primary_v, output_v, cap1_v, cap2_v, primary_current_a`.
SE hat `cap2_v=0`. Schlüssel: `<case_id>__native` / `<case_id>__48k`.

Benötigt: Python ≥3.9, NumPy, Matplotlib und ngspice mit den verwendeten
B-Quellenfunktionen. Tatsächlich verwendet: Python 3.14.4, NumPy 2.5.3,
Matplotlib 3.11.2, Ubuntu-Paket ngspice `45.2+ds-1`.

Aus dem Repository-Hauptverzeichnis:

```bash
OPENBLAS_NUM_THREADS=1 python3 docs/spice_sim/run_simulations.py --ngspice /pfad/zu/ngspice
OPENBLAS_NUM_THREADS=1 python3 docs/spice_sim/run_diagnostics.py --ngspice /pfad/zu/ngspice
OPENBLAS_NUM_THREADS=1 python3 docs/spice_sim/analyze_results.py
OPENBLAS_NUM_THREADS=1 python3 docs/spice_sim/verify_results.py --ngspice /pfad/zu/ngspice
```

Ein einzelnes Einstiegsdeck kann aus `docs/spice_sim/` direkt laufen:

```bash
ngspice -n -b GCOT-SE-01.cir
```

Es schreibt `GCOT-SE-01-ac.txt` und `GCOT-SE-01-transient.txt`. Ein Fall aus
`netlists/` wird entsprechend mit diesem Ordner als Arbeitsverzeichnis gestartet.
Die Originalversuche benötigen weiterhin `../sauce/xformer.lib`; die
generierten Zustands-/DDT-Decks sind über ihre Includes eigenständig.

In dieser Umgebung wurde ngspice samt Laufzeitpaketen **unprivilegiert unter
`/tmp/opencode/ngspice-root/`** entpackt und mit
`LD_LIBRARY_PATH=/tmp/opencode/ngspice-root/usr/lib/x86_64-linux-gnu` gestartet.
Es wurden nur Simulatorpakete beschafft, keine neuen Bauteilmodelle.
Die Meldung über ein fehlendes `spinit` ist protokolliert; die Decks benötigen
keine externen Code-Modelle oder Benutzer-Initialisierungsdatei (`-n`).

Original `xformer.lib`, SHA256:
`8b5c6ce4015c34abe57ef133063cf4afb1d049f30475c46d8f6b91e6cb0f37ca`.
Das Original wurde nicht überschrieben. Versions- und Binärhash im Manifest.

## 9. Nächster Schritt

Vor einem DSP-Port braucht es eine **konsistente Übertrager-Netzform** mit
geklärten Vorzeichen, Einheiten, gemeinsamem Kern bei Push-pull und
Last-Rückwirkung sowie dokumentierten Quellen-/Last-/Biasbedingungen.
Ob das vorhandene Netz korrigiert oder ein eigenes reduziertes Modell gewählt
wird, ist eine neue Modellentscheidung; ein stillschweigender Vorzeichenfix
wäre keine Umsetzung der jetzigen Simulation.

Erst danach sind `φ_k(f)`, Kompression, H3/H5, ein stabiles Knie und eine
etwaige Hysterese neu zu identifizieren. Ein späterer Echtzeit-Umbau braucht
dann C++/EEL2 gemeinsam, Parität und die Projektprüfungen.

**Prüfabschluss:** Alle vier reproduzierbaren Simulationsaufbauten, Tabellen,
Netlists, Logs und Einzelbewertungen liegen vor. Der gewünschte
**physikalische Koeffizientenfit ist aufgrund des nachgewiesenen Modellbefunds
nicht möglich** und wird nicht als bestanden ausgewiesen.
