# DSP-Architektur — Green Stripe 76, 0.4.0

## 1. Status und normative Dateien

Dies ist ein eigenständiges **reduziertes Gray-Box-Modell**. Die Funktionsstruktur
ist durch 1176-Unterlagen motiviert, die konkrete parametrische Gain Law und
Färbung sind eigene Näherungen. Es existiert kein verifizierter transistorweiser
Original-Netlist-/SPICE-Fit und keine automatisch aus NAM gewonnene Kalibrierung.

- `data/model.json`: gemeinsam generierte Konstanten.
- `data/transformers.json`: validierte Transformatorbank; `TransformerModels.hpp`
  und `GreenStripe76-Transformers.jsfx-inc` werden gemeinsam daraus erzeugt.
- `src/dsp/GreenStripe.hpp`: C++11-Implementierung, double-Zustände.
- `jsfx/GreenStripe76-Core.jsfx-inc`: gleichwertige EEL2-Implementierung.
- `tools/generate.py`: generierte Model-Includes, Ports, Presets und Oberflächen.
- `tests/jsfx_parity.cpp`: tatsächliches Rendern beider Kerne, nicht Textvergleich.

### Modus-Tabellen: EEL2-Lookup statt indizierter Globals

Die Halfband-Koeffizienten bleiben in EEL2 indizierte Globals. Die drei
Modus-Tabellen (`ratios`, `thresholds_dbfs`, `knees_db`) werden dagegen als
generierte Lookup-Funktionen `gs_ratio_of`, `gs_threshold_of` und
`gs_knee_of` ausgegeben.

Grund ist ein messbarer Fehler in nseel: Globale in einem `@init`-Funktionsrumpf
teilen sich einen Speicherpool, und ein indizierter Schreibvorgang über die
deklarierte Arraygröße hinaus vergrößert das Array **nicht**, sondern
überschreibt die folgende Variable. Mit sechs Modi las `gs_ratios[5]` dadurch
`gs_thresholds[0]` und `gs_thresholds[5]` `gs_knees[0]`. Der Effekt war
unabhängig von der deklarierten Größe und nicht monoton: 7, 8, 10, 24, 32 und 48
lieferten plausible Werte, 12, 16 und 18 nicht, und eine Vergrößerung aller drei
Tabellen verschob zusätzlich die Basiszeiger (`gs_ratios[0]` las dann `6`). Ein
sentinelbasierter Test bestätigte: Schreibt man `gs_ratios[9]=64`, ist
`gs_ratios[9]` hinterher nicht `64`, sondern der Wert des Nachbarn. Die
Modus-Zuordnung war damit zur Laufzeit kaputt, ohne jeden Compilerfehler.

Die Lookup-Funktionen umgehen das vollständig und sind zur Laufzeit billiger.
Sie verwenden `local(v)` und Zuweisungsanweisungen statt einer
Ternär-Kette, weil EEL2 weder ein negatives Literal noch eine Klammer direkt
nach `?` parst. Die C++-Seite behält ihre Arrays aus `ModelConstants.hpp`; die
Parität zwischen beiden Kernen ist über `tests/jsfx_parity.cpp` belegt.

## 2. Signalfluss

```text
Base-rate L/R
  → Off/2×/4× interpolation (independent states)
  → Input gain
  → selected input transformer (independent L/R flux + memory + HF)
  → input DC/low-frequency colour
  → nonlinear FET divider ← control charge
  → preamp colour ─────────────────┐
  → preamp bandwidth              │ feedback tap BEFORE Output
  → Output gain                   │
  → low-frequency output colour   │
  → asymmetric output amplifier   │
  → output DC correction          │
  → high-rate Dry/Wet + Enabled   │
  → selected-rate decimation      │
  → float output                  │
                                 └→ magnitude detector / mode law
                                    → implicit charge update
                                    → discharge + history
```

Output und der gesamte Ausgangsblock sind **nicht Teil des Detektorabgriffs**.
Die Audiostufen werden pro Sample nur mit definitiven Zuständen fortgeschrieben;
die iterativen Detektorberechnungen benutzen zustandslose `tap()`-Auswertungen.
So wird derselbe Filterzustand nicht mehrfach in einem Solver-Schritt verändert.

## 3. Zeit- und Parametermodell

Abtastrate ist die von Host/REAPER gelieferte Rate, intern
`fs_internal=factor·fs`, `factor=1/2/4` für Off/2x/4x.
Attack und Release werden geometrisch von den Skalen 1–7 abgebildet:

\[
t_A=0.0008(0.00002/0.0008)^{(A-1)/6},\qquad
t_R=1.1(0.05/1.1)^{(R-1)/6}.
\]

Dies sind nominelle Modellzeiten. Die geschlossene Feedback-Antwort, steigende
Flanken, durch Sinuszyklen wieder aufgeladene Zustände und All Buttons können
effektive GR-Zeiten verändern. Eine direkte Gleichsetzung mit 63-%-/10–90-%-
Hardwaremessungen wäre falsch.

Regler-Zielwerte werden mit
`c=1-exp(-1/(0.002 fs_internal))` geglättet. Erster Parametersatz nach Reset wird
direkt übernommen, damit Preset-Start/Referenzmessung keine Input-Anfahrrampe
enthält. Keine pro Block erneut zurückgesetzten Zeitglieder.
Ab 0.1.1 rasten die Zielwerte bei 10⁻¹² absolut/relativ ein; dann wird die
Sample-Glättung übersprungen. Das ermöglicht exakte 0/1-Fastpaths.

## 4. FET-Spannungsteiler

Der physikalische Bezug ist ein Serienwiderstand plus FET als Shunt. Im
ohmischen Modell erzeugt derselbe Abschwächer Gain und pegelabhängige Verzerrung.
Green Stripe verwendet eine **regularisierte** dimensionslose Knotenform:

\[
u=0.08x,\quad C=B-1+q,\quad B=10^{1/20},\quad
F(v)=v-k\frac{v^2}{1+|v|},
\]

\[
v+C F(v)-u=0,\quad k=Colour(0.24+0.08 All).
\]

Die 0.08-Volt-/Skalierungswahl ist eine eigene Normalisierung, keine ermittelte
FET-Drainspannung eines Capture-Geräts. Die kleine Ruheabschwächung von nominell
1 dB ist über `B` kalibriert und am Ausgang wieder normalisiert. Bei Colour=0:

\[
y=x\,\frac{B}{B+q},\qquad g(q)=\frac{B}{B+q}.
\]

Nach Multiplikation mit `1+|v|` ist die Knotenform auf jeder Polarität ein
Quadratpolynom. Mit `U=|u|`, `s=sign(u)` lautet die stabile positive Wurzel:

\[
a=1+C(1-sk),\quad b=1+C-U,\quad
v=\frac{2u}{b+\sqrt{b^2+4aU}}.
\]

Die rationalisierte Lösung vermeidet Wurzelsubtraktions-Auslöschung und ersetzt
drei frühere per-Tap-Newton-Schritte. Steigung bleibt für die Krümmung positiv;
beliebig große Extrapolation des reinen JFET-Quadratgesetzes wird vermieden.
Der Funktionszweig modelliert weder
Gate-Leckstrom noch ein vollständiges Shichman–Hodges-/Halbleiterkennfeld.

`fetcomp-dsp` zeigt alternativ eine geschlossene quadratische Divider-Lösung
inklusive LN-Gatefeedback. Das ist eine wertvolle Vergleichsquelle, aber deren
JUCE-Struktur, Potentiometertabellen, Plugin-Fit und Transformerzustände sind
hier **nicht übernommen**. Green Stripe ist kein Port dieser Bibliothek.

## 5. Feedback Gain Law

Für das zustandslose FET-/Preamp-Tap-Signal wird

\[
L=20\log_{10}(\max(|tap(L,q)|,|tap(R,q)|)),\quad d=L-T
\]

berechnet. Das weiche Knie nutzt die übliche stetige quadratische Überleitung:
unter `−K/2` null, über `K/2` `d`, dazwischen `(d+K/2)^2/(2K)`.

Die gewünschte Abschwächung gegen den **Feedback-Pegel** ist `(R-1) knee(d)`.
`R−1` ist wesentlich: der Feed-forward-Koeffizient `1−1/R` würde in derselben
Feedback-Struktur nicht die gewünschte statische Ratio ergeben. Überleitung in
den positiv begrenzten Charge-/Conductance-Zustand:

\[
q_{target}=B\left(10^{\min(60,(R-1)knee(d))/20}-1\right).
\]

Das ist eine bewusst gewählte **Verhaltenskennlinie**, kein rekonstruierter
AC-/DC-Widerstands-/Diodenblock. Ratio-abhängige T/K-Werte:

| Modus | nominale Ratio | Threshold dBFS am Tap | Knie dB |
|---|---:|---:|---:|
| 2 | 2 | −24 | 6 |
| 4 | 4 | −24 | 6 |
| 8 | 8 | −21 | 4 |
| 12 | 12 | −19,5 | 3 |
| 20 | 20 | −18 | 2 |
| All | 12…20 | −22 | 1,5 |

Diese Tabellen sind **provisorische Green-Stripe-Abstimmung**, nicht aus der
Dissertationsgrafik digitalisierte oder vom NAM abgeleitete Messdaten.

## 6. Regelkreis: Aufladung und Entladung

Aufladung benutzt einen impliziten Backward-Euler-Schritt:

\[
(1+\alpha)q_{n+1}-q_n-\alpha q_{target}(x_{n+1},q_{n+1})=0,\quad
\alpha=\frac1{fs_{internal}\,t_A\,R\,(1+0.3All)}.
\]

Die zusätzliche Ratio-Skalierung hält die nominale geschlossene Zeit näher am
Reglerbereich. Sie ist eine Modellentscheidung, keine RC-Bauteilidentifikation.
Kein explizites Base-rate-`z^-1` im Detektorpfad.

- Startintervall aus statischer Feed-forward-Näherung.
- Maximal vier Intervallerweiterungen.
- Maximal acht safeguarded Newton-Schritte; andernfalls Bisektion des Intervalls.
- Charge begrenzt auf 0…1000, GR-Computer auf 60 dB.
- Ableitung des sauberen Divider-Gains dient als monotone Näherung bei Colour.

Bei geschlossenem Gleichrichter entlädt sich der Zustand exponentiell:

\[
q_{n+1}=q_n e^{-1/(fs_{internal}t_R(1+0.75m+0.2All))}.
\]

Ab 0.1.1 wird exp(−s) im kleinen zulässigen Schrittbereich kubisch ausgewertet:
`1−s+s²/2−s³/6`, Koeffizientenfehler <7×10⁻¹⁵ im schlechtesten unterstützten
Fall (8k/4×/50 ms). Der GR-Logarithmus wird beim Entladen über ein kubisches
`log(1−z)`-Inkrement fortgeführt und beim Aufladen exakt neu verankert.
Damit entfallen zwei häufige Transzendentalaufrufe; Fehlergrenzen und 80
Vorher/Nachher-Fälle sind in `CPU_ANALYSIS.md` dokumentiert.

`m∈[0,1]` verfolgt die GR-Historie mit etwa 80 ms Lade-/400 ms Erholungszeit.
Durch die nichtlineare Zuordnung `q→g` ist die GR-Erholung schon vor dieser
Historie nicht identisch mit einer einfachen exponentiellen dB-GR-Hüllkurve.
Die Zusatzhistorie ist eine **programabhängige Näherung**, kein belegter optischer
oder thermischer Speicher eines 1176. Eichas' Mehrzustands-Fitting motiviert
den Nutzen längerer Dynamik, nicht diese konkreten Zahlen.

## 7. All Buttons

- Getrennte Threshold-/Knie-/Färbungswerte.
- Ratio folgt `12+8m`.
- Unkomprimierter Betragspegel lädt ein etwa 60-µs-Lagglied.
- Detektor mischt im All-Zustand den normalen Feedback-Tap mit
  `lagged * g(q)`; das erzeugt eine anfängliche besondere Transientenantwort.
- Attack-/Release-Skalierungen ändern sich.

AXT zeigt, dass die echte Taste sowohl Bias/Pegel **als auch Thevenin-Impedanzen**
ändert. Green Stripe bildet diese Gesamtwirkung parametrisch ab, nicht als
exaktes Schalter-Netzwerk. Im Status als Näherung beibehalten.

Die Taste ist der letzte Modus, Index 5. Bis 0.3.0 stand sie auf Index 4;
durch das Einfügen von `2:1` an erster Stelle (siehe `docs/PARAMETERS.md`) sind
alle Preset-Indizes um eins gewandert, das Verhalten selbst ist unverändert.

## 8. Verstärker- und tieffrequente Färbung

Eingang: 8-Hz-DC-Zustand, 35-Hz-Lowpass-Zustand und konservative niederfrequente
Amplitudenkrümmung. Vorverstärker: asymmetrische Kennlinie, 45-kHz-Bandbegrenzung.
Ausgang: Output Gain, eigener 35-Hz-Zustand, asymmetrische Verstärkerkennlinie,
5-Hz-DC-Korrektur. Input-/Output-States sind kanalgetrennt.

Diese Zustände **sind kein Jiles–Atherton-Hysteresemodell**. Sie stellen eine
geringe, pegel-/frequenzabhängige Klangfärbung dar. Behauptungen über einen
bestimmten 5002-/Lundahl-Core, Wicklung oder B-H-Kurve wären nicht gerechtfertigt.

### Was `Colour` tatsächlich imitiert

Der Regler `colour` (0…100, intern `0…1`) ist **kein** Transformator- und auch
kein Röhrenmodell. Er ist ein generischer Regler für **Nichtlinearitäts- und
Bandbegrenzungs-Textur** und wirkt an genau vier Stellen der Kette. Das ist
absichtlich so: er soll den Charakter einer analogen Übertragungsstufe
veränderbar machen, ohne ein einzelnes Gerät zu imitieren.

| Ort | Wirkung | Quelle |
|---|---|---|
| FET-Kennlinie | `curvature = colour · (0.24 + 0.08·all)` im Divider; asymmetrische Kompression der positiven Halbwelle | `GreenStripe.hpp`, `fet()` |
| Tap-Sättigung | `softClip` um einen kleinen, über `clipSlope` normierten Bias; Kleinsignal-Gain bleibt ≈ 1 | `tap()` |
| Eingang | `flux`-Lowpass, dessen Differenz `softClip`-begrenzt wird: leichte HF-Dichte/-Kompression | `Channel::input()` |
| Ausgang | Lowpass-Mix, zweiter `flux`-`softClip`, asymmetrisch nachgeführte `softClip`-Stufe um +0,04, plus mit `colour` verschobene DC-Eckfrequenz | `Channel::output()` |

Der wichtigste Punkt ist der erste: Bei `Colour = 0` ist der Divider
**symmetrisch**. Mit steigendem `Colour` wird die positive Halbwelle stärker
komprimiert als die negative. Das erzeugt die charakteristische asymmetrische
Kompression und damit **geradzahlige Verzerrungsanteile**. Die beiden
`softClip`-Stufen liefern zusätzlich die klassische „driven"-Kompression, und die
`flux`-Glieder verdichten das obere Ende.

**Was `Colour` ausdrücklich nicht ist:**

- kein Transformator (keine Magnetisierungsinduktivität, keine Hysterese, keine
  Wicklungserscheinungen, keine Kopplungs-Bassabsenkung, kein Brummen)
- kein Röhrenmodell (die Trioden-Kennlinie aus `docs/sauce/tube.lib` ist nicht
  Teil des DSP)
- kein Jiles–Atherton-Kern und kein Core-/Wicklungsbehauptungsmodell

`MIX` ist bewusst **nicht** Teil dieses Reglers, sondern ein separater
Dry/Wet-Anteil. Im Panel sitzt der `MIX`-Knopf deshalb silbern und nicht im
grünen ENGINE-Bay: er ist ein Utilities-Regler, kein Färbungsregler.

### Gemeinsame `tanh`-Näherung

Audio und Bias-Korrektur benutzen exakt dieselbe [7/6]-Padé-Formel:

\[
S(x)=\frac{x(135135+x^2(17325+x^2(378+x^2)))}
 {135135+x^2(62370+x^2(3150+28x^2))}.
\]

Für `|x|≥5` wird auf ±1 begrenzt. Die kleine Restdiskontinuität am Rand ist
numerisch gering, aber das Antialiasing bleibt erforderlich. Analytische
Ableitung derselben Funktion normiert die Kleinsignalverstärkung bei Bias:

\[
A(x)=H\frac{S(x/H+b)-S(b)}{S'(b)}.
\]

Keine Vermischung von std::tanh und Approximation; das vermeidet DC-Fehler durch
unterschiedliche Bias-Referenzen. Keine Float-Bit-Hacks, damit double-EEL2 und
C++ dieselben Operationen nutzen können. Approximationseffizienz ist nicht
gleich Hardwaretreue; diese Abgrenzung aus den neuen Quellen bleibt wichtig.

## 9. Oversampling, Dry/Wet und Bypass

Zwei kaskadierte 2×-Halfband-Polyphasen-IIR-Stufen, skalare Allpass-Rekursion:

`y=(x-y_previous)*a+x_previous`.

Koeffizientenprovenienz: HIIR-Designer-Prinzip, Übergangsargumente 0.04 und 0.27,
acht beziehungsweise vier Koeffizienten (fest in Model-JSON). Interpolation
erhält DC-Gain ohne zusätzliche ×4-Multiplikation. Decimation tauscht die
chronologischen Paarhälften gemäß dem Polyphasenschema und mittelt mit 0.5.

Je Kanal eigene Up/Down-States. Die ausgewählte Rate umfasst Sättigung,
Transformator und Regler. Seit 0.2.0 Off/2x/4x mit Default Off; Umschaltung
blendet samplegezählt über je 2 ms aus/ein und setzt die Rate-Historien zurück.

Dry-Abgriff vor Input; Mischung und Enabled erfolgen vor derselben Decimation.
So entsteht bei internem Bypass keine abrupte Phase-/Latenzumschaltung. Externes
Host-Bypass kann sich anders verhalten. 0/3/4 Frames gemeldete Nominal-PDC,
nicht frequenzunabhängige Filterverzögerung. External parallel routing prüfen.

## 10. Stereo und RT

Zwei unabhängige Controller plus ein gemeinsamer Link-Controller sind vorhanden.
Ab 0.1.1 rechnen bei stabilem Link nur die benötigten Zustände: Link On einer,
Off zwei. Bei Umschaltung werden Zustände übernommen; während der kurzen
Glättung laufen alle drei. Link-Umschaltung mischt dynamische **Gains**, dann
wird in Charge zurückgerechnet. Vollständig abgeschaltete Compression/Enabled
parkt Controller; Bypass überspringt auch den Audiopfad. Die Resamplinghistorie
läuft für identische Phase weiter. Kein Audiosummen-Sidechain/Kanalfaltung.

Core-Allokationen nur bei Host-Instanziierung. Speichergröße unabhängig vom
Block; kein Worker/Thread nötig. Ausnahmebehandlung/RTTI im LV2-Binary aus.
Inputs NaN/Inf → 0; endliche Inputs auf ±256 begrenzt. Die Begrenzung ist
Robustheit für fehlerhafte Hosts, kein musikalischer Limiter. Extrem kleine
rekursive Zustände werden auf null gesetzt; keine künstliche Rauschquelle.

## 11. Transformator — Laufzeitmodell ab 0.4.0

**Aktueller Vertrag:** [`TRANSFORMER_RUNTIME.md`](TRANSFORMER_RUNTIME.md).
Die gefitteten 60s/80s/00s-Profile sind in C++ und EEL2 integriert, nach Input
Gain und vor der bisherigen Eingangsfärbung. `None` ist exakt transparent;
`Symmetric` ist eine lineare lastgekoppelte Referenz ohne Stop-Gedächtnis.
Modellwechsel blenden über den Eingang, Stereo-Historien bleiben unabhängig.
Die normative Bank lässt sich mit `tools/transformer_model.py` neu importieren.

**Die folgenden Abschnitte dokumentieren die frühere 0.3.0-Planung und deren
Widerlegung.** Aussagen „noch nicht eingebaut“ beziehen sich auf diesen
historischen Arbeitsstand. Die alten xformer.lib-Zuordnungen/Knieformeln
werden in 0.4.0 nicht verwendet. Laufzeitkoeffizienten, neue Symmetric-Semantik,
HF-Diskretisierung und gemessene Grenzen stehen im aktuellen Vertrag oben;
die Offlineberichte behalten ihre ursprünglichen Messbedingungen.

**SPICE-Befund 2026-10-05:** Die unten dokumentierte frühere GC-/Knie-Planung
ist durch die inzwischen ausgeführte Simulation **nicht bestätigt**. Die vier
Netzmodelle besitzen einen instabilen Nullzustand und keine Rückwirkung der
Sekundärlast. Die Formel für `φ_k` setzt zudem eine Spannung der `Bc`-Quelle
mit einem Strom gleich. Sie ist damit keine belastbare Schwellenkalibrierung.
Maßgeblicher neuer Befund und nächster Schritt:
[SPICE-Bericht](spice_sim/BERICHT.md) und der Abschluss dieses Abschnitts.

Seit 0.3.0 gibt es einen Control-Port `transformer` und ein Dropdown im Panel.
**Die Auswahl hat derzeit keine Klangwirkung.** Der Wert wird im Parameterpfad
geführt, von Presets adressiert und im `mod-active`-Zustand gespeichert, ist aber
noch nicht mit dem Audiopfad verbunden.

### Auswahl

| Wert | Bezeichnung | Herkunft `docs/sauce/xformer.lib` | Topologie |
|---:|---|---|---|
| 0 | `None` | kein Transformator | — |
| 1 | `60s` | `GCOT-SE-01`, 5 W, 70 Hz–15 kHz | single-ended |
| 2 | `80s` | `GCOT-PP-03` | push-pull |
| 3 | `00s` | `GCOT-PP-04` | push-pull |
| 4 | `Symmetric` | `GCSYMETRICAL`, **nur für Testzwecke** | push-pull |

Die Bezeichnungen sind bewusst **neutral** und nennen kein Produkt. Die
Herkunft, die Gerätebezeichnungen des Originals und die Parameter stehen in
`docs/SOURCES.md`. Ein Produktname in unserer Oberfläche wäre eine
Hardwarebehauptung, die `AGENTS.md` ausschließt. `Symmetric` ist in der Quelle
ausdrücklich als Testschaltung markiert und gehört so gekennzeichnet in die
Liste.

### Was ein Echtzeit-Port des Modells braucht

Das SPICE-Modell arbeitet mit `DDT`, also einer **Ableitung**:

```
Bp  P1 C1 V = {Np} * DDT(I(Vp))
Cc  N1 N2   {C}                       // magnetische Kapazität = Permeanz
Bc  N2 N3 V = {a} * (ABS(V(N1,N2)))**{n} * SGN(V(N1,N2))   // Sättigung
Br  N3 N4 I = {b} * (ABS(V(N3,N4)))**{m} * SGN(V(N3,N4))   // Hysterese
```

Ein direkter diskreter Differentiator verstärkt hohe Frequenzen
(Betrag ∝ f, nicht 1/f). Für einen physikalisch konsistenten Echtzeit-Port ist
eine integrierte Zustandsform zu prüfen. Die folgenden Überlegungen stammen
aus der Planung **vor** dem SPICE-Befund und identifizieren noch kein gültiges
Flux-Modell der vorhandenen Netlist:

- magnetischer Zustand `φ` mit `v = N·dφ/dt`, integriert mit Trapez- oder
  Bilinearregel (nicht explizit, sonst instabil bei steiler Sättigung)
- `i(φ)` mit Sättigung `|φ|^n·sgn(φ)` und Hysterese über einen geschlossenen
  Schleifenpfad, nicht über die ungedämpfte `Br`-Quelle
- Kopplung: das Übersetzungsverhältnis `Ns/Np` wirkt auf die Wicklungsspannung,
  die Kopplung selbst verursacht die Bassabsenkung — **das ist genau der
  Klangeffekt, der interessiert**, und er entsteht nur, wenn beide Wicklungen
  über denselben Kern geführt werden
- Kanaltrennung: Flux-Zustand je Kanal/Richtung, analog zu den Resamplerhistorien

Das Modell hat außerdem zwei Eigenschaften, die Prüfung brauchen: Es ist
**nichtlinear und damit nicht LTI**, und `ABS(V)^n` mit `n` bis 13 verlangt eine
`pow`-Funktion pro Sample je Wicklung. Beides trifft direkt die Paritäts- und
CPU-Zusagen dieses Projekts.

### Latenzentscheidung

**Getroffene Festlegung:** Der Latenz-Port meldet **unverändert** 0/3/4 Frames,
abhängig von Oversampling. Eine GC-Kern-Stufe wird bewusst **nicht** als
zusätzliche Latenz deklariert.

Begründung: Der Kern verursacht vor allem **Phasendrehung im Tieffrequenzbereich**,
keine echte Laufzeitverzögerung. Eine deklarierte zusätzliche Latenz würde im Host
eine Sample-genaue Phasenkompensation auslösen, die genau den Charakter zerstört,
den man mit einem Transformator wählt. Für Gütekommunikation gilt: das Signal
ist minimalphasig; ein Phasenverzerrungsfilter wäre die Alternative, nicht mehr
Latenz.

Ab jetzt nicht mehr offen sind:

- Der Einbauort ist die **Eingangsseite**, vor der Kompressorstufe, mit einem
  **kanalgetrennten** Flux-Zustand pro Kanal nach dem Vorbild von `CORE_GC`.
- Die Kopplungs-Bassabsenkung entsteht **aus dem gemeinsamen Kern** und wird
  **nicht** als eigener Regler exponiert. Sie ist Nebeneffekt, nicht Bedienziel.
- Die `flux`-/Lowpass-Färbung in `Colour` bleibt **unverändert**. Der Kern soll den
  Kopplungs- und Sättigungseffekt liefern, nicht eine zweite, parallele
  Bassabsenkung modellieren.

### Frühere Festlegung: Sättigungsschwelle — durch SPICE nicht bestätigt

Die frühere Planung setzte einen nichtlinearen Magnetisierungsstrom mit einem
linearen Anteil gleich. Diese Zuordnung ist durch die tatsächlichen Elemente
von `CORE_GC` **nicht gedeckt**: `Bc` erzeugt eine Spannung. Die damalige,
hier nur zur Nachvollziehbarkeit erhaltene Rechnung lautete:

```
i_lin   = C · ω · φ              // linearer Anteil bei Frequenz ω
i_sat   = a · |φ|^n · sgn(φ)     // Sättigungsanteil
Kniefall:  a · φ_k^n = C · ω · φ_k   →   φ_k = (C · ω / a)^(1/(n-1))
```

Arithmetisch ausgewertet für die vier Parametersätze aus `xformer.lib`, beim
geometrischen Mittel des damals angenommenen Übertragungsbands (nur das
SE-Band steht im Originalkommentar):

| Typ | Subckt | Band | `f_mitte` | `n` | `Np` | `φ_k` |
|---|---|---|---|---|---|---|
| `60s` | `GCOT-SE-01` | 70 Hz–15 kHz | 1025 Hz | 13 | 2012 | **0,532** |
| `80s` | `GCOT-PP-03` | 20 Hz–20 kHz | 633 Hz | 6 | 668 | **0,337** |
| `00s` | `GCOT-PP-04` | 20 Hz–20 kHz | 633 Hz | 8 | 1996 | **0,368** |
| `Symmetric` | `GCSYMETRICAL` | — | 633 Hz | 25 | 200 | **1,761** |

Die drei Zahlen liegen zwischen **0,337** und **0,532**, Faktor **1,58**.
Daraus folgt nach dem SPICE-Befund keine verifizierte Sättigungshärte der
Bauarten und kein physikalischer Flux-Schwellwert.

**Frühere, ausgesetzte Festlegung:** Schwellwert als **normierter Flux**
`u = φ / φ_k`, Schwelle bei **`u = 1,0`**, mit dem vorgesehenen Ausdruck:

```
i_mag(u) = C · ω · φ_k · u  +  a · φ_k^n · |u|^n · sgn(u)
```

Vorgesehen waren ein gemeinsamer Normierungsparameter, unveränderte
`n`/`Np`/`Ns` und kein zusätzlicher Clamp. Die frühere Annahme, eine steile
Kennlinie verhindere weiteres Flux-Wachstum automatisch, ist durch die
unstabilen Originalzustände widerlegt. Vor einer solchen Umsetzung müssen
zuerst die Netzgleichungen und die Bedeutung des Zustands geklärt werden;
numerische Integrationsstabilität allein repariert das Modell nicht.

### Einordnung des vierten Modells

`GCSYMETRICAL` ist in `xformer.lib` ausdrücklich mit
`* IMPORTANT: Only for testing purposes` überschrieben. Die GUI-Bezeichnung
`Symmetric` ist deshalb **kein** Vintage-Transformator, sondern eine Referenz mit
hoher Sättigungsschwelle und steiler Nichtlinearität (`n = 25`). Das ist in der
Dokumentation so zu führen und darf nicht als klangliches Ziel verkauft werden.

### Mögliche Alternativen zum GC-Kern

Falls sich der GC-Kern als zu teuer, zu schwer paritätisch zu halten oder klanglich
zu ähnlich zu `Colour` erweist, sind diese Wege geprüft worden:

| Alternative | Vorteil | Nachteil |
|---|---|---|
| **Nur Kopplungstiefpass** (LC-Tiefpass je Wicklung, ohne Sättigung) | sehr billig, linear, exakt paritätisch, kein `pow` | keine Sättigung, kein Hysteresepfad; wird ein reiner Bassfilter |
| **Statische Sättigung ohne Zustand** (`softClip` im Transformatorpfad) | billig, bereits im Kern vorhanden | keine Hysterese, kein Pegel-/Zeitverlauf; ähnelt `Colour` und würde mit ihm kollidieren |
| **Gedämpfter Oszillator-Nachlauf** als Resonanzmodell | billig, gibt das „Nachsummen" großer Wandler | modeliert Resonanz, nicht Sättigung |
| **Trapezintegrierter GC-Kern** (geplanter Weg) | echte Sättigung + Hysterese + Kopplung | höchster Aufwand: `pow`, Zustand, Parität, CPU neu messen |

### Vorgesehene Einbauposition

Die Eingangsseite, **vor** der Eingangsstufe. Begründung: Der Eingangstransformator
prägt den Kompressions-Charakter über die gesamte Kette — der Kompressor „sieht"
das bereits gesättigte/kopplungsgedämpfte Signal. Eine Ausgangsstufe würde nur
das fertige Signal färben. Für die Versuche mit Transformatoren am Ausgang wäre
eine zweite, getrennte Option nötig; das ist bewusst nicht Teil des ersten Schritts.

### Nächster Schritt nach der SPICE-Simulation

Die eigene Offline-Rechnung in `docs/spice_sim/` umfasst 260 Hauptarbeitspunkte,
76 Diagnoseläufe und vier dokumentierte Abbrüche mit direktem Original-Include.
Alle Eingangswerte `C`, `a`, `n`, `R`, `b`, `m`, `Np`, `Ns` sind erhalten.
ngspice 45.2 löst die KCL-äquivalente Zustandsform; eine unabhängige
DDT-/Hilfsinduktorrealisierung bestätigt sie.

**Die Simulation liefert keine neuen Klang-Kniekoeffizienten.** Sie liefert
gemessene instabile Wachstumsraten von **0,836965 / 0,483798 / 0,619532 /
2,235942 s⁻¹** für 60s/80s/00s/Symmetric. Der zugehörige positive Pol folgt
aus `C·du/dt=j+w`, `N_h·dw/dt=u`, mit `N_h=Np` bzw. `Np/2`.
Die Hauptfenster zeigen überwiegend Expansion; spätere Fenster sind
weiterhin zeitabhängig. `φ_k`, Kniebreite, gefittetes `n` und stationärer
DC-Offset bleiben in `spice_sim/coefficients.json` deshalb `null` mit Begründung.

Vor einem DSP-Umbau müssen eine konsistente Netzform, magnetische Einheiten,
Vorzeichen, gemeinsamer Kern und Last-Rückwirkung sowie Quellen-/Last-/Biaswerte
geklärt werden. In der gelieferten Netlist ist `m` ein Exponent, `Rr` liegt
parallel zu `Br`, und `Bc` liefert eine Spannung statt eines Stroms; die
bisherige Schwellenformel ist daher keine aus diesem Netz abgeleitete
physikalische Gleichung. Eine reparierte Netzform wäre ein neues Modell und
müsste erneut vermessen werden. Erst dessen stabile Daten könnten die
Eingangsstufe kalibrieren; anschließend C++/EEL2 gemeinsam und Parität prüfen.

**Neue Literaturgrundlage:** de Paiva et al. (2011), *Real-Time Audio
Transformer Emulation for Virtual Tube Amplifiers*, liefert eine
bidirektionale GC-/WDF-Struktur, elektrischen Parameterfit und einen
Referenzparametersatz. Die lokale Netlist ist kein korrekter Port dieser
Struktur. Als nächster Offline-Kandidat ist Abb. 6(b) mit Tabelle 1 zu
untersuchen; insbesondere Verlustzweig-Normierung, Sekanten-/
Differentialpermeanz und verzögerte WDF-Nichtlinearitäten sind vor einer
Echtzeitentscheidung zu klären. Details und Seitenbelege in
[`TRANSFORMER_PAPER_REVIEW.md`](TRANSFORMER_PAPER_REVIEW.md).

**Reale 1:1-Zielkurven:** Die später gelesenen Hammond-Datenblätter
140TEX/560Q in `docs/transformer/` liefern einen passenderen Line-
Anwendungsbezug als der Paper-Ausgangsübertrager. Besonders der 560Q zeigt
Amplitude, Phase und THD+N bei mehreren Pegeln und zwei Verschaltungen.
Auswertung und Ablesebereiche: [`transformer/AUSWERTUNG.md`](transformer/AUSWERTUNG.md).
Die Kurven ersetzen keine H-Φ-Identifikation; Quellen-/Lastbedingungen,
dBm-Bezug und tabellierte L-/Impedanzwerte müssen gemeinsam interpretiert
werden. Der ebenfalls abgelegte LL1930 ist regulär 5,8:1/11,6:1 und keine
direkt 1:1 qualifizierte Referenz.

**Eingegrenzter Fit mit Schätzungen:** Whitlocks zusätzlich untersuchtes
Kapitel enthält eine besser bezeichnete 1:1-Line-Eingangsreferenz
(Jensen JT-11P-1, Quelle 600 Ω, Last 10 kΩ, THD über Pegel/Frequenz).
`transformer/PARAMETERFIT_GRUNDLAGE.md` empfiehlt diese als ersten
Fitdatensatz, mit effektiver Flussverkettung statt unidentifizierter
Kerngeometrie. `FIT_STARTWERTE.json` enthält veröffentlichte Werte und
ausdrücklich **nicht gefittete** Suchwerte; keine neue normative Modellbank.
Hysterese, komplexe Magnetisierung und Transienten bleiben ohne neue
Messungen mehrdeutig. Ein erster Offline-Fit ist mit diesen offengelegten
Annahmen möglich; die bisherigen GC-Koeffizienten werden daraus nicht
automatisch übernommen.

**Ergänzende Modellauswahl:** `05_e.pdf` (Macak/Schimmel, DAFx-11)
motiviert eine einfache dynamische Sättigungsbaseline (Fröhlich oder
glattes Potenzgesetz) neben einem gedächtnisbehafteten Kandidaten.
„Ohne Hysterese“ bedeutet dabei weiterhin einen integrierten
Flussverkettungszustand im lastgekoppelten Netz, nicht statisches
Audio-Waveshaping. Verlustanteile des gemessenen Erregerstroms dürfen
bei einem bereits dissipativen Hysteresemodell nicht doppelt gezählt
werden. Messmethodik und Quellenkritik:
[`transformer/ERREGERSTROM_UND_MODELLVERGLEICH.md`](transformer/ERREGERSTROM_UND_MODELLVERGLEICH.md).

### Erster ausgeführter Offlinefit — noch kein Produktport

Am 2026-10-05 wurde die Jensen-JT-11P-1-Referenz tatsächlich gegen
53 Datenblatt-/Ablesebedingungen gefittet. Der ausgewählte partielle
Gray-Box-Kandidat erreicht 18/20 zurückgehaltene Intervalle; Restfehler
und 24/33 Trainingstreffer in `transformer/offline_fit/BERICHT.md`.
Die mitgelieferte Offline-C++-Datei gehört **nicht** zu `src/dsp/` und
ist nicht Teil des gebauten Plugins.

Die reduzierte Zustandsform arbeitet mit Flussverkettung `lambda`,
monotoner Fröhlich-/Potenzkennlinie, positiv gewichteten Stop-Zweigen
und einer linearen RL-Relaxation. Quelle/Last werden gemeinsam gelöst;
ein effektiver HF-Zweipol ist nachgeschaltet und nicht als vollständig
identifiziertes Wicklungsnetz ausgegeben. Gedächtnis-/Materialparameter
bleiben ohne Strom-/Transientenreferenzen mehrdeutig.

**Benutzerwahl umgesetzt:** `60s` warm, früh/weich (p=3), `80s`
ausgewogen (p=5), `00s` clean/Jensen-artig. `profiles.json` enthält
die eigenständige Offline-Abstimmung mit 20-Hz-1-%-THD-Ankern bei
−14/−8/−2 dBFS Peak und HF-`f0` 26/48/108,257 kHz. Diese Werte
ersetzen erst bei einem gesonderten Produktport die früheren
unbestätigten Gitarrentrafo-Koeffizienten; Port/UI-Zuordnung allein
macht sie noch nicht hörbar.

Für die WAV-Proben existiert eine ausdrücklich feste Mittelband-
normalisierung. Ein späterer Produktport muss Gainpolitik,
gemeinsame Kanalregler und getrennte Zustände, Bypass/Mix/Recall,
Hochfeldfortsetzung des 00s-Kerns und ein geeigneteres Rate-/HF-
Antialiasverfahren festlegen. Die jetzige Tustin-Offlinenäherung
bei 48 kHz ist nicht als fertiger OS-Off-Produktpfad qualifiziert.
Erst danach C++/EEL2 gemeinsam, Parität, Übergänge und Geräte-CPU testen.

---

## 12. Grenzen und Ausbau

- Native und JSFX-Parität ist belegt, Hardwaregleichheit nicht.
- Controller-Attack/Knie/Release abhängig von Betriebszustand; vollständige
  quantitative Probe-Matrix bleibt zur musikalischen Abstimmung sinnvoll.
- Hohe nominelle Ratios können auf schnelleren Sinuszyklen schwächer erscheinen.
- Aktive Controller plus Solver: tatsächliche Dwarf-CPU messen; der lokale
  JSFX-Vergleich ist kein Gerätelastnachweis.
- Modelldaten und mathematische Struktur bei Änderung versionieren; beide
  Implementierungen und Tests gemeinsam nachziehen.
- NAM-Färbungsfit erst nach verifizierter Core-Auswertung und Peak/RMS-
  Kalibrierung; nicht direkt in die Laufzeit kaskadieren.
