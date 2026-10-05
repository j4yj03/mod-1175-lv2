# Transformator-Modell nach de Paiva et al. (2011)

Auswertung **2026-10-05** für Green Stripe 76. Quelle: *Real-Time Audio
Transformer Emulation for Virtual Tube Amplifiers*, Rafael Cauduro Dias de
Paiva, Jyri Pakarinen, Vesa Välimäki und Miikka Tikander, EURASIP Journal on
Advances in Signal Processing, 2011, Artikel 347645,
DOI **10.1155/2011/347645**.

## 1. Ergebnis für unser Projekt

**Diese Arbeit liefert einen konkreten, brauchbaren Ausgangspunkt:** ein
bidirektionales Gyrator-Kapazitäts-Modell, einen Mess-/Identifikationsablauf
und einen veröffentlichten Referenzparametersatz. Die Anwendung auf Green
Stripe muss deshalb nicht mit frei erfundenen Kennlinien beginnen.

Der negative Befund aus [`spice_sim/BERICHT.md`](spice_sim/BERICHT.md) gilt für
die vorhandene `xformer.lib`. Er widerlegt **nicht** die GC-Methode der Arbeit.
Das Paper verbindet beide Wicklungen über **einen gemeinsamen Kern und
leistungsgekoppelte Gyratoren**. Genau diese bidirektionale Kopplung fehlt
unserer gelieferten Netlist.

Empfehlung: Zuerst die Paper-Topologie und den Parametersatz aus Tabelle 1 als
**separate Offline-Referenz** rekonstruieren. Danach die WDF-Näherung gegen
diese Referenz untersuchen; erst anschließend Green-Stripe-Klangvarianten
und Echtzeitparameter festlegen.

## 2. Zugriff und Provenienz

- Lokale Datei:
  `docs/sauce/Real-Time_Audio_Transformer_Emulation_for_Virtual_.pdf`.
- SHA256 der tatsächlich gelesenen Datei:
  `2eec0c710e8d3927e5f412032cbe1b5bc2a5e17b3d57e01b6a44fe4428b35dd5`.
- **16 PDF-Seiten**, davon eine vorgeschaltete Bereinigungsseite und
  **15 Artikelseiten**. Gedruckte Seite **+1 = lokale PDF-Seite**.
- Vollständiger extrahierbarer Text gelesen mit `pypdf`. Abbildung 6,
  Abbildung 7, Gleichungen 16–33 und Tabelle 1 zusätzlich an gerenderten
  Seitenbildern geprüft (Poppler 26.01.0). Die Normaltext-Extraktion ist
  hier zuverlässiger als der Layoutmodus.
- Der Hash auf der vorgeschalteten Bereinigungsseite bezeichnet eine andere,
  hier nicht vorliegende Originalfassung; er ist nicht der Hash dieser Datei.
- Die Titelseite nennt eine **Creative Commons Attribution License**;
  eine konkrete Lizenzversion wird dort nicht angegeben.

Diese Auswertung ist Literaturarbeit und algebraische Plausibilitätsprüfung.
Das Paper-Modell wurde in diesem Schritt **nicht implementiert oder simuliert**.
Die gemessenen SPICE-Ergebnisse der vorherigen Untersuchung bleiben getrennt
und unverändert archiviert.

## 3. Was das Modell tatsächlich beschreibt

### 3.1 Aufbau — S. 6–9, Abb. 5–7

Je Wicklung:

- Gyrator zur Umrechnung zwischen elektrischem und magnetischem Modellbereich,
- Wicklungswiderstand `R_w`,
- elektrische Wicklungskapazität `C_w`,
- Streuflussanteil als magnetische Kapazität `C_lw`.

Gemeinsam für alle Wicklungen:

- Kernpermeanz `C`,
- nichtlineare Sättigungsbeziehung mit `a` und `n`,
- nichtlinearer Verlustzweig mit `r`, `b` und `m` zur Annäherung von
  Hystereseschleifen.

Die Sekundärlast beeinflusst die vom Treiber gesehene Impedanz. Bei Sättigung
steigt vor allem der Magnetisierungsstrom; daraus entstehen in Wechselwirkung
mit Treiber und Quellenimpedanz weitere Veränderungen der Ausgangsspannung.
Die Arbeit zeigt eine stärkere Verzerrung des Eingangsstroms als der
Ausgangsspannung (S. 11).

Die GC-Analogie ordnet magnetischen Fluss einer **Ladungsgröße** und
Flussänderung einem **Strom** zu. Die GC-Kondensatorspannung entspricht einer
magnetischen Anregungsgröße; sie ist nicht unmittelbar der Fluss.
Die Gyratorgleichungen und die Orientierung der Ports müssen zusammen
übernommen werden, damit Energieübertragung und Vorzeichen stimmen.

**Notation beachten:** Das Paper schreibt `H = N·i`. Ohne magnetische
Weglänge ist das eine Durchflutung/MMK-artige Größe, nicht unmittelbar die
übliche SI-Feldstärke in A/m. Ein Fit in dieser Normierung ist möglich;
eine absolute Material-B-H-Kurve folgt daraus noch nicht.

### 3.2 Abgleich mit der lokalen `xformer.lib`

| Eigenschaft | Paper | Gelieferte lokale Netlist |
|---|---|---|
| Wicklungskopplung | zwei leistungsgekoppelte Gyratoren | Ableitung einer Messstromquelle und einseitig gesteuerte Ausgangsspannung |
| Rückwirkung der Sekundärlast | Bestandteil des Modells | fehlt, durch Lastvariation nachgewiesen |
| Magnetischer Kern | gemeinsam, auch im Mehrwicklungsmodell | bei Push-pull zwei unabhängige `CORE_GC`-Blöcke |
| Wicklungs-/Streu-/Kapazitätsparasiten | explizit je Wicklung | die entsprechenden elektrischen Zweige fehlen |
| Sättigung | Fluss-/Anregungsrelation, GC-Zustand | lokale Gleichungen besitzen einen instabilen Nullzustand |
| Parameterbedeutung | `n` Sättigungsform, `m` Verlustkennlinienexponent | `m` bleibt ebenfalls Exponent, kein Kopplungsfaktor |

Die ähnlichen Potenzausdrücke sind kein Nachweis dafür, dass die Bibliothek
die Paper-Schaltung korrekt implementiert. Eine Herkunft des lokalen
Tabellengenerators aus diesem Paper ist nicht belegt.

## 4. Konkrete Parameterbestimmung — S. 7–8, Gl. 19–33

### 4.1 Leerlaufmessung

Sinus an einer Wicklung, zweite Wicklung unbelastet. Gemessen werden:

- Strom `i_1` in der angeregten Wicklung,
- Spannung `V_2` an der offenen Wicklung.

In der Modellkonvention der Arbeit:

\[
H=N_1i_1,\qquad
\Phi=-\frac{1}{N_2}\int V_2\,dt.
\]

Das ergibt eine `H–Φ`-Schleife. Vorzeichen folgen der Wicklungsorientierung.
Bei einer eigenen Messauswertung sind Kanalphase, Offset und
Integrationsdrift zu kontrollieren; ein ungeprüfter DC-Offset würde den
integrierten Fluss verfälschen. Das ist eine praktische Ergänzung zur
beschriebenen Methode, kein aus dem Paper übernommener Messwert.

Die Versuche der Autoren speisen wegen der verfügbaren Verstärkerspannung
die **Niederspannungswicklung** des Ausgangsübertragers. Der elektrische
Versuch ist somit gegenüber der normalen Röhrenanwendung umgekehrt
angeschlossen. Die Zuordnung von Messkanal und `N_1/N_2` darf dabei nicht
versehentlich vertauscht werden.

### 4.2 Sättigungsfit

Zunächst wird die Mittellinie der gemessenen Hystereseschleife bestimmt.
An diese statische Kurve wird angepasst:

\[
H_s=\frac{\Phi_s}{C}
 +a\left|\frac{\Phi_s}{C}\right|^n
      \operatorname{sgn}(\Phi_s/C).
\]

Für ein festes `n` ist das linear in zwei Hilfsparametern:

```text
X = [Φ_s, |Φ_s|^n · sign(Φ_s)]
α = [1/C, a/C^n]
```

Die Autoren benutzen gewichtete kleinste Quadrate, probieren mehrere `n`
und wählen den kleinsten Fehler. Sie empfehlen stärkere Gewichtung des
Kniebereichs und vorherige Normalisierung für gute numerische Kondition.
Rückrechnung: `C=1/α₀`, `a=α₁·C^n`.

Für unsere Umsetzung wäre eine QR-/SVD-Lösung statt der expliziten
Matrixinversen aus Gl. 27 sinnvoll. Positive Parameter und Prüfung an
zurückgehaltenen Pegeln/Frequenzen sind zusätzliche eigene Fit-Kriterien.

### 4.3 Verlust-/Hysteresefit

Anschließend werden Remanenz, Koerzitivpunkte und Flussänderung verwendet,
um den nichtlinearen Widerstandszweig zu bestimmen (Gl. 29–32).
Die Auswahl von `m` wird nicht so ausführlich als Suchverfahren spezifiziert
wie die Auswahl von `n`; Tabelle 1 verwendet `m=4`.

Für einen neuen Datensatz wäre ein gemeinsamer Fit an mehreren
Schleifenpegeln und Frequenzen robuster als das Auswerten einzelner Punkte.
Vorher ist die unten beschriebene `b`-/Vorzeichenkonvention zu klären.

### 4.4 Übersetzung und parasitäre Elemente

- Verhältnis im Paper: `k=N₂/N₁=√(L₂/L₁)` aus gemessenen Induktivitäten.
  Für eigene Messungen zusätzlich mit einem Kleinsignal-Spannungsverhältnis
  plausibilisieren; parasitäre Beiträge und Messfrequenz berücksichtigen.
- Unbekannte tatsächliche Windungszahlen sind kein Hindernis: `N₁` kann
  als Modellnormierung gewählt werden, `N₂=kN₁`.
- Wicklungswiderstände direkt messen.
- Streuinduktivität mit kurzgeschlossener anderer Wicklung bestimmen;
  Umrechnung ins GC-Modell: `C_lw=L_lw/N_w²` (Gl. 33).
- Wicklungskapazitäten gehören in den Frequenzgangabgleich. Dafür liefert
  die Arbeit keine ebenso detaillierte separate Identifikationsanleitung.

**Folge der freien Windungsnormierung:** `C`, `a`, Flusszahlen und weitere
magnetische Parameter sind nicht unabhängig von `N₁/N₂` zu übernehmen.
Zum Beispiel erhält `L≈N²C` denselben Wert, wenn `N` mit Faktor `s`
und `C` mit Faktor `1/s²` skaliert werden. Ein direkter Vergleich der
`C`-Zahlen verschiedener Parametertabellen allein ist daher wenig aussagekräftig.

## 5. Veröffentlichter Referenzparametersatz

**Tabelle 1, gedruckte S. 11 / lokale PDF-Seite 12.** Das sind veröffentlichte
Modellparameter für den untersuchten **Fender NSC041318**, keine eigenen
Messungen und keine Green-Stripe-/1176-Kalibrierung.

| Parameter | Paperwert | Bedeutung im Modell |
|---|---:|---|
| `N₁` | 100 | gewählte Windungsnormierung |
| `N₂` | 6,47 | Übersetzung zur zweiten Wicklung; keine Behauptung über reale Windungszahl |
| `C` | **24,7 mF** | GC-Kernkapazität / normierte Permeanz |
| `a` | 900 | Sättigungskoeffizient |
| `n` | 7 | Sättigungsexponent |
| `r` | 0,077 Ω | GC-Verlustzweig, kein Kupferwiderstand |
| `b` | 4,46 | nichtlinearer Verlustkoeffizient, Konvention prüfen |
| `m` | 4 | Verlustkennlinienexponent |
| `C_l1`, `C_l2` | je **500 nF** | magnetische Streufluss-Ersatzkapazitäten |
| `R₁` | 206 Ω | elektrischer Wicklungswiderstand |
| `R₂` | 0,7 Ω | elektrischer Wicklungswiderstand |
| `C₁`, `C₂` | je **1 nF** | elektrische parasitäre Wicklungskapazitäten |

Die Unterscheidung `C_lw` versus `C_w` ist wesentlich. Beispielsweise sind
500 nF hier nicht als 500-nF-Kondensator direkt an einer Audiowicklung
anzuschließen.

Für den **Hammond T1750V** werden Vergleichsmessungen gezeigt, aber kein
zweiter vollständiger Parameterfit in einer Tabelle veröffentlicht. Die
Arbeit liefert somit **einen** konkreten Referenzsatz, keine vier
Klangstufenparameterbanken.

## 6. Was sich an unserer Knie-Herleitung ändert

Gl. 20 verwendet `v_c=Φ/C` und `H_s=v_c+a|v_c|^n·sgn(v_c)`.
Definiert man das Knie **selbst** als Gleichheit des linearen und
nichtlinearen Anteils, folgt:

\[
a|v_{c,k}|^{n-1}=1,\qquad
|v_{c,k}|=a^{-1/(n-1)},\qquad
|\Phi_k|=C\,a^{-1/(n-1)}.
\]

**Eigene algebraische Ableitung, keine gemessene Knieschwelle des Papers.**
Für Tabelle 1 ergibt das `v_c,k≈0,321830` und `Φ_k≈0,00794920`
in dessen gewählter Normierung. Es ist kein universeller Wb- oder dBFS-Wert
und nicht automatisch der Punkt von 1 dB Audiokompression.

Anders als die alte Projektformel `(C·ω/a)^(1/(n−1))` benötigt diese
statische Kernrelation **kein ω**. Die Frequenzabhängigkeit bei
Spannungsanregung entsteht durch die Integration:

\[
|\Phi_\text{Peak}|\approx \frac{|V_\text{Wicklung,Peak}|}{2\pi f N}.
\]

Die Näherung setzt eine passende Wicklungsspannung und vernachlässigte
weitere Spannungsabfälle voraus. Quellenimpedanz, Last und Verluste
entscheiden weiter darüber, welche hörbare Übertragungsänderung entsteht.

## 7. Stellen, die vor einer Umsetzung geklärt werden müssen

Die folgenden Punkte wurden am gerenderten PDF bestätigt; sie sind keine
bloßen Text-Extraktionsartefakte.

### 7.1 Sekanten- und differentielle Kapazität

Gl. 16 lautet:

```text
C_e = C / (1 + a·|v_c|^(n−1))
```

Aus Gl. 20 ist dies das Verhältnis `Φ/H_s`, also eine **Sekantenpermeanz**.
Die Ableitung derselben statischen Beziehung ergibt dagegen:

```text
dΦ/dH_s = C / (1 + n·a·|v_c|^(n−1))
```

Die beiden Größen sind verschieden. Die WDF-Konstruktion benutzt Gl. 16
mit zeitveränderlichem Übersetzer und verzögertem Zustand. Ein impliziter
Zustandsport der ursprünglichen Serienkapazität/-spannungsquelle darf
deshalb nicht ohne Vergleich als identisch zu dieser WDF-Näherung gelten.

### 7.2 `b`-Normierung des Verlustzweigs

Gedruckt stehen:

```text
Gl. 17: I_R(v_r) = b·|v_r|^m·sign(v_r)
Gl. 18: R_c(v_r) = r / (1 + b·|v_r|^(m−1))
```

Zählt man die Parallelströme von `r` und der Quelle aus Gl. 17 in derselben
passiven Richtung, ergibt sich algebraisch stattdessen:

```text
i_total = v_r/r + b·|v_r|^m·sign(v_r)
v_r/i_total = r / (1 + r·b·|v_r|^(m−1))
```

Ohne zusätzliche Normierung von `b` sind die gedruckten Ausdrücke somit
nicht identisch. Außerdem müssen Quellpfeil, Flussrichtung und Vorzeichen
der Remanenz-/Koerzitivformeln 29–32 konsistent festgelegt werden.
Gl. 18 mit Koeffizient `b_R` entspräche bei gleichgerichteter Parallelquelle
Gl. 17 mit `b_I=b_R/r`; das ist eine **Umrechnung der Konvention**, keine
Berechtigung zum stillen Ändern veröffentlichter Daten.

Für eine Paper-Reproduktion beide Lesarten benennen und gegen die
veröffentlichten Kurven bzw. verfügbare Referenzimplementierung prüfen.
Die Arbeit beschreibt für ihren WDF explizit die Verwendung von Gl. 18.

### 7.3 Numerische Lösung und Verzögerungen

S. 5–6 und 9: Nichtlinearer Widerstand und nichtlineare Kapazität verwenden
**um ein Sample verzögerte Steuergrößen**, um algebraische Schleifen und
globale Iterationen zu vermeiden. Für die Kapazität wird ein variabler
WDF-Übersetzer mit

```text
N_c = sqrt(1 / (1 + a·|v_c|^(n−1)))
```

verwendet, gespeist vom verzögerten `v_c` (Gl. 34).

Die Autoren nennen selbst mögliche **Instabilität bei starker Sättigung**
und ein höheres Risiko durch weitere künstliche Verzögerungen.
„WDF“ bedeutet für diese nichtlineare, verzögerte Realisierung daher
nicht automatisch bedingungslose Stabilität.

Eigene Zeitumrechnung: ein Sample entspricht 20,83 µs bei 48 kHz,
10,42 µs bei 96 kHz und 5,21 µs bei 192 kHz. Das sind interne
Rückkopplungsverzögerungen, keine unmittelbar daraus abzuleitende
zusätzliche Host-Latenz. Die Rate beeinflusst die Näherung; für Green
Stripe müssen insbesondere OS Off/2×/4× konsistent untersucht werden.

Die Referenzexponenten `n=7` und `m=4` sind ganzzahlig. Für einen festen
Parametersatz lassen sich die benötigten Potenzen durch wenige
Multiplikationen berechnen; ein allgemeiner `pow`-Aufruf ist dafür nicht
zwingend. Das ist eine mögliche eigene Implementierungsentscheidung,
kein bereits gemessener CPU-Gewinn.

## 8. Wie gut ist die Arbeit validiert?

**Berichtet im Paper:**

- Fender NSC041318 und Hammond T1750V elektrisch vermessen.
- Leerlauf und ohmsche Last, Eingangsstrom und Ausgangsspannung;
  Messstrom über einen **2,4-Ω-Serienwiderstand**.
- Logarithmische Sweeps **20 Hz–10 kHz**, Harmonische 1–5.
- Fender: deutliche Nichtlinearität vor allem unter etwa **100 Hz**;
  Hammond: vor allem unter etwa **30 Hz**, jeweils im untersuchten Aufbau.
- Fender-`H–Φ`-Fit bei **80 Hz** (Abb. 11), Vergleich der
  Harmonischenverläufe (Abb. 9/12).
- Echtzeitdemonstration der vollständigen Röhren-Ausgangskette mit
  BlockCompiler bei **96 kHz**, Intel Core 2 Quad 3 GHz, ungefähr **7 % CPU**.

**Von den Autoren benannte Grenzen:**

- Ergebnisse zur Schleifenübereinstimmung gelten ausdrücklich für die
  benutzten periodischen Testsignale (S. 11).
- Transientenverhalten ist weitere Arbeit (S. 14).
- Hochfrequenzabweichungen durch nicht enthaltene Verluste, etwa
  Wirbelströme, und vereinfachte verteilte Wicklungskapazitäten (S. 11–12).
- Einzelne Hochfrequenzspitzen der Sweep-Harmonischen sind Messartefakte
  und keine reale Trafonichtlinearität (S. 11).

Für unseren Zielprozessor liefert die historische CPU-Zahl keine belastbare
Kostenabschätzung; auch 48-kHz-Betrieb und Aliasqualität werden damit nicht
automatisch nachgewiesen.

## 9. Konkrete Folgerung für Green Stripe

1. **Referenz aufbauen:** Paper-Topologie Abb. 6(b), Tabelle 1, gemeinsame
   Kernzustände, definierte Portorientierung; elektrische R/C- und
   magnetische GC-Größen konsequent unterscheiden.
2. **Konventionsfragen offen lösen:** Verlustzweig und Sekanten-/
   Differentialbeziehung nachvollziehbar festlegen, beide relevanten
   Interpretationen bei Bedarf offline gegenüberstellen.
3. **Physikalische Grundprüfungen:** Last-Rückwirkung, Kleinsignalübersetzung,
   Nullsignal/Anfangszustände, Energie-/Passivitätsprüfung, 80-Hz-Schleife,
   Frequenz-/Pegelsweeps. Aus einer optisch ähnlichen Abbildung allein
   keinen numerisch exakten Paper-Fit behaupten; Rohmessreihen liegen in
   dieser PDF nicht als Tabelle vor.
4. **Echtzeitkandidat vergleichen:** verzögerten Paper-WDF bei 96 kHz gegen
   eine fein aufgelöste implizite Referenz; dann 48/96/192 kHz, Bursts,
   DC/Bias und hohe Aussteuerung. Das beantwortet, ob der günstigere
   verzögerte Ansatz für Green Stripe ausreicht.
5. **Eigene Stufen kalibrieren:** Erst nach stabiler Referenz digitale
   Volt-Skalierung, Quellen-/Lastimpedanz und musikalische Zielwerte
   festlegen. Das Paper stellt einen Röhren-Ausgangsübertrager vor;
   es kalibriert unsere geplante Kompressor-Eingangsstufe nicht direkt.
6. **Späterer DSP-Port:** Zustände pro Audiokanal, C++/EEL2 gemeinsam,
   Parität und Dwarf-CPU/Hören. Kein Übersprechen durch einen zwischen
   linkem und rechtem Audiokanal geteilten Kernzustand.

Damit ist die vorher nur allgemein empfohlene Gray-Box-Identifikation nun
durch einen veröffentlichten Rechenweg und einen konkreten Testparametersatz
unterlegt. Materialgeometrie und reale Windungszahlen sind für diesen
Ansatz nicht zwingend nötig; gemessene elektrische Größen und eine
konsistente Normierung reichen für die Identifikation.
