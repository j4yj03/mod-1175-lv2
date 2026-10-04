# DSP-Architektur — Green Stripe 76, 0.3.0

## 1. Status und normative Dateien

Dies ist ein eigenständiges **reduziertes Gray-Box-Modell**. Die Funktionsstruktur
ist durch 1176-Unterlagen motiviert, die konkrete parametrische Gain Law und
Färbung sind eigene Näherungen. Es existiert kein verifizierter transistorweiser
Original-Netlist-/SPICE-Fit und keine automatisch aus NAM gewonnene Kalibrierung.

- `data/model.json`: gemeinsam generierte Konstanten.
- `src/dsp/GreenStripe.hpp`: C++11-Implementierung, double-Zustände.
- `jsfx/GreenStripe76-Core.jsfx-inc`: gleichwertige EEL2-Implementierung.
- `tools/generate.py`: generierte Model-Includes, Ports, Presets und Oberflächen.
- `tests/jsfx_parity.cpp`: tatsächliches Rendern beider Kerne, nicht Textvergleich.

## 2. Signalfluss

```text
Base-rate L/R
  → 4× interpolation (independent states)
  → Input gain
  → input DC/low-frequency colour
  → nonlinear FET divider ← control charge
  → preamp colour ─────────────────┐
  → preamp bandwidth              │ feedback tap BEFORE Output
  → Output gain                   │
  → low-frequency output colour   │
  → asymmetric output amplifier   │
  → output DC correction          │
  → high-rate Dry/Wet + Enabled   │
  → 4× decimation                 │
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

Abtastrate ist die von Host/REAPER gelieferte Rate, intern `fs_internal=4 fs`.
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

Je Kanal eigene Up/Down-States. 4× umfasst **nicht nur** Sättigung, sondern auch
den Regler. Eine zweite/variabel schaltbare Qualitätsstufe ist in 0.1.1 nicht
enthalten, damit Kalibrierung, CPU und Parität nachvollziehbar bleiben.

Dry-Abgriff vor Input; Mischung und Enabled erfolgen vor derselben Decimation.
So entsteht bei internem Bypass keine abrupte Phase-/Latenzumschaltung. Externes
Host-Bypass kann sich anders verhalten. Vier Frames gemeldete Nominal-PDC,
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

## 11. Transformator — Steuergerüst vorhanden, Klangmodell offen

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

Für Echtzeit ist das **nicht direkt** übertragbar. Ein Differentiator im
Audioband ist numerisch unbrauchbar (Verstärkung ∝ 1/f, Rauschen, Instabilität
bei 4× Oversampling). Nötig ist stattdessen die **integrierte** Form, also ein
zustandsbehafteter Flux-Integrator:

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

### Festlegung: Sättigungsschwelle

Die Sättigung setzt ein, wenn der nichtlineare Magnetisierungsstrom den linearen
Anteil derselben Größe erreicht. Das ist die klassische Knie-Definition
(permeability fällt auf den linearen Wert). Für den Magnetisierungszweig aus
`CORE_GC` heißt das:

```
i_lin   = C · ω · φ              // linearer Anteil bei Frequenz ω
i_sat   = a · |φ|^n · sgn(φ)     // Sättigungsanteil
Kniefall:  a · φ_k^n = C · ω · φ_k   →   φ_k = (C · ω / a)^(1/(n-1))
```

Ausgewertet für die vier Subckte aus `xformer.lib`, jeweils beim geometrischen
Mittel des angegebenen Übertragungsbands:

| Typ | Subckt | Band | `f_mitte` | `n` | `Np` | `φ_k` |
|---|---|---|---|---|---|---|
| `60s` | `GCOT-SE-01` | 70 Hz–15 kHz | 1025 Hz | 13 | 2012 | **0,532** |
| `80s` | `GCOT-PP-03` | 20 Hz–20 kHz | 633 Hz | 6 | 668 | **0,337** |
| `00s` | `GCOT-PP-04` | 20 Hz–20 kHz | 633 Hz | 8 | 1996 | **0,368** |
| `Symmetric` | `GCSYMETRICAL` | — | 633 Hz | 25 | 200 | **1,761** |

Ergebnis der Auswertung: die drei echten Modelle liegen zwischen **0,337** und
**0,532**, also nur um den Faktor **1,58**. Ein einziger absoluter Schwellwert über
alle Typen wäre trotzdem falsch, weil die Reststreuung genau die unterschiedliche
Sättigungshärte der Bauarten ausmacht.

**Getroffene Festlegung:** Der Schwellwert wird als **normierter Flux**
`u = φ / φ_k` geführt, und die Schwelle liegt bei **`u = 1,0`**. Damit gilt

```
i_mag(u) = C · ω · φ_k · u  +  a · φ_k^n · |u|^n · sgn(u)
```

Ein **gemeinsamer** Normierungsparameter für alle vier Modelle, die
transformatorspezifischen Größen `n`, `Np`, `Ns` bleiben erhalten. `ω` bleibt
im Kern frequenzabhängig, das ist der Modelleffekt und wird nicht
weggeglättet — die Abschwächung ist echt.

**Kein zusätzlicher Clamp.** Oberhalb des Knies ist die Steigung sehr hoch
(`2^n` ist 64× bis 8192× bei `u = 2`), der Flux wächst also von selbst nicht
weiter. Eine zusätzliche Begrenzung auf `u` wäre falsch, weil sie die
DDT-Beziehung `v = N·dφ/dt` zerstört und genau den Sättigungscharakter
beseitigt, den wir modellieren.

Noch zu prüfen, wenn der Kern gebaut wird: Stabilität der Integrationsregel bei
`n = 13`, CPU-Kosten der `pow`-Funktion und der Hysteresezweig, und ob die
Kopplungsabsenkung im hörbaren Bereich liegt.

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
