# Parameterfit: zusätzliche Quellen, fehlende Daten und vertretbare Schätzungen

Stand **2026-10-05**, Green Stripe 76. Auswertung der drei neu genannten PDFs
und des GroupDIY-Threads. Schätzungen sind entsprechend dem Benutzerwunsch
als Ausgangspunkt zulässig; sie sind nachfolgend von Herstellerwerten und
eigenen algebraischen Ableitungen gekennzeichnet.

## 1. Entscheidung: Ein erster Fit ist jetzt möglich

**Für eine plausible, eigenständige 1:1-Emulation reicht die vorliegende
Datenbasis für einen ersten eingeschränkten Gray-Box-Fit.** Zusätzliche
Hardwaremessungen sind dafür keine zwingende Vorbedingung. Sie wären nötig,
um die derzeit mehrdeutigen inneren Parameter und das Gedächtnisverhalten
eines konkreten Übertragers eindeutig zu identifizieren.

Die wichtigste neue Information ist das **im Whitlock-Kapitel enthaltene
Datenblatt des Jensen JT-11P-1**: ein 1:1-Line-Eingangsübertrager mit
definierten Eingangspegeln in dBu, 600-Ω-Quelle, 10-kΩ-Last, Widerständen,
Amplitudengang und THD-Kurven über Frequenz **und** Pegel. Das ist für den
ersten Fit eindeutiger als die zuvor betrachteten Hammond-Blätter.

Empfehlung:

1. **JT-11P-1 als erste saubere 1:1-Referenzbedingung** benutzen.
2. Fehlende Größen als wenige effektive Parameter mit Suchbereichen führen.
3. Reale Windungszahl, Kerngeometrie und absolute B-H-Kurve zunächst durch
   einen Zustand in **Flussverkettung `λ` [V·s]** ersetzen.
4. Hammond 140TEX und 560Q anschließend als **weitere, getrennte Zielbilder**
   untersuchen. Deren Kurven nicht zu einem vermeintlich gemessenen
   Jensen-/Hammond-Mischübertrager zusammenfügen.

Diese Arbeit liefert Analyse und **vorläufige Startwerte**, noch keinen
optimierten oder simulierten Klangkern. Rechenweg:
[`estimate_fit_start.py`](estimate_fit_start.py), maschinenlesbare Werte:
[`FIT_STARTWERTE.json`](FIT_STARTWERTE.json).

**Anschließende Durchführung:** Der erste Fit ist inzwischen tatsächlich
ausgeführt; Ergebnisse und drei eigene Profile unter
[`offline_fit/`](offline_fit/README.md). Die vorliegenden Startwerte bleiben
als Herkunft der Schätzungen erhalten. Der tatsächliche Fit ist partiell;
maßgeblich sind `offline_fit/BERICHT.md` und die dokumentierten Restfehler.

**Weitere Quellen, ebenfalls 2026-10-05:**
[`ERREGERSTROM_UND_MODELLVERGLEICH.md`](ERREGERSTROM_UND_MODELLVERGLEICH.md)
präzisiert die Messgröße Erregerstrom einschließlich Verlusten/Parasiten
und ergänzt eine dynamische Fröhlich-Baseline zum Modellvergleich.
HiFiHaven, StackExchange sowie Stromwandler-/FRA-/NN-Papers liefern
dafür Methoden und Grenzen, aber keine neuen Jensen-Koeffizienten.

## 2. Quellenprüfung

### 2.1 Bill Whitlock: `Audio-Transformers-Chapter.pdf`

*Audio Transformers*, zuerst 2001 als Kapitel 11 des *Handbook for Sound
Engineers*, 3. Auflage, Herausgeber Glen Ballou; vorliegende Fassung trägt
Copyright 2001/2006. **31 lokale PDF-Seiten** einschließlich einer
Bereinigungsseite und Titelseite. Gedruckte Seite **+2 = lokale PDF-Seite**;
die eingebetteten Datenblattseiten liegen auf PDF 28–29.

Volltext vollständig gelesen; Abb. 17–23 und die beiden Jensen-
Datenblattseiten zusätzlich visuell geprüft.

**Für den Fit besonders wertvoll:**

- S. 3–5: Magnetisierungsstrom, V/f-Abhängigkeit, pegel-/frequenzabhängige
  Permeabilität und DC-/Remanenzeinfluss. Bei zentriertem Kern vorwiegend
  ungerade Verzerrung, bei Verschiebung des Arbeitspunkts auch gerade Anteile.
- S. 9–10, Abb. 17–19: gemessene THD über Pegel, Frequenz und
  Quellenwiderstand für Stahl-/Nickel-Kernbeispiele. **Relative Verzerrung
  kann schon bei kleinen Pegeln durch Hysterese entstehen** und mit Pegel
  zunächst sinken. Bei hohem Pegel kommt der Sättigungsanstieg.
- S. 10–12, Abb. 20–24: Niederfrequenzersatzbild, HF-Resonanz und
  Dämpfung, Definition von Einfügedämpfung. Quellen- und
  Wicklungswiderstand wirken gemeinsam auf Bassgang und Spannungsverzerrung.
- S. 11: steigende Permeabilität zu tiefen Frequenzen kann den Abfall
  flacher als einen konstanten Einpol-Hochpass machen. Ein einzelner
  tabellierter L-Wert muss den gesamten Bassgang nicht erklären.
- S. 24–25: definierte Messschaltung, Quellen-/Lastbedingungen und Kritik
  unvollständiger Datenblätter. Ein Maximumpegel ohne Frequenz,
  Verzerrungsgrenze und Quellenimpedanz reicht nicht.
- PDF 28–29: vollständiges historisches **JT-11P-1-Datenblatt, Stand 1/01**.

Die materialbezogenen Kurven sind Beispiele konkreter Konstruktionen,
keine universellen THD-Werte für jedes Stück Nickel oder Stahl. Aussagen
des Herstellers über besonders günstige Klangwirkung sind kein eigener
Hörbefund.

**Präzisierung unserer früheren Auswertung:** Ein sinkender THD+N-Prozentwert
kann durch Messrauschen erklärt werden, aber ebenso eine reale
Hysteresecharakteristik enthalten. Die Hammond-Blätter unterscheiden das
nicht. Ohne Messrauschkurve dürfen wir den niedrigen Pegelbereich weder
vollständig als Rauschen abziehen noch vollständig als Hysterese fitten.

### 2.2 McLyman: `ourdev_725050HHOGA4.pdf`

Die kryptisch benannte Datei ist **Colonel Wm. T. McLyman, *Transformer and
Inductor Design Handbook*, Third Edition, Revised and Expanded, 2004**,
Marcel Dekker, ISBN 0-8247-5393-3. **534 lokale PDF-Seiten**, einschließlich
Bereinigungsseite. Das Buch ist überwiegend ein Entwurfsbuch für
Leistungselektronik, keine spezielle Audio-Parameterbank.

Für diese Fragestellung geprüft: Inhaltsverzeichnis; Kapitel 1
(PDF 22–49); relevante Material-/Hysterese-/Verlustabschnitte aus Kapitel 2
(insbesondere PDF 51–60, 73–75, 83–99); Einleitung/Trade-offs aus Kapitel 5
(PDF 192–197); **Kapitel 17 vollständig, PDF 448–461**; Faraday-
Zusammenhang in Kapitel 21, Gl. 21-B12 (PDF 522). Nicht als vollständige
Detaillektüre aller 534 Seiten zu verstehen. OCR vorhanden, aber teils
beschädigt; verwendete Materialtabelle und wichtige Schaltungen/Formeln
wurden an Seitenbildern gegengeprüft.

**Nutzbare Beiträge:**

- Anfangs-, Sekanten-, inkrementelle und effektive Permeabilität sind
  verschieden. `L_m` ist material-, pegel-, bias- und frequenzabhängig.
- Kernform, Luftspalt und Verarbeitung ändern Materialschleifen erheblich.
  Eine B-H-Kurve einer toroidalen Materialprobe ist nicht unverändert die
  Kennlinie eines aufgebauten Audioübertragers.
- Tabelle 2-1 und Abb. 2-3…2-7 liefern Größenordnungen als **Material-Priors**.
  Hoch-Nickel-Beispiele: `B_s≈0,65…0,82 T`; Orthonol 50/50:
  `B_s≈1,42…1,58 T`; Siliziumeisen: `B_s≈1,5…1,8 T`.
- Kap. 17: getrennte Wicklungskapazitäten, Kopplungskapazitäten und
  Streuinduktivitäten; sie sind in Wirklichkeit verteilt, für ein
  reduziertes Modell können Ersatzglieder benutzt werden.
- Gl. 17-7: `C=1/((2πf_r)²L)` zur Kapazitätsabschätzung, **wenn klar ist,
  welches L in welcher Messschaltung resoniert**.
- Faraday für Sinus: `V_RMS≈4,44·f·N·A_e·B_peak` bei SI-Flächen in m².
  Die Buchform mit cm² enthält den zusätzlichen Einheitenfaktor.

**Nicht aus dem Buch gewinnen wir** den exakten Kernquerschnitt, die
Windungszahl, Legierung, Glühung, den Luftspalt oder die Minor-Loops eines
Hammond/Jensen-Exemplars. Die tabellierten Verlustgesetz-Exponenten
`P∝k f^m B^n` sind **nicht** die gleich benannten GC-Koeffizienten
`m/n` aus de Paiva. Sie dürfen nicht zwischen diesen Formeln ausgetauscht
werden.

Materialwerte sind als Bereich nützlich, aber für einen Audiofit ist es
zweckmäßiger, erst `λ`, Strom und Spannung zu identifizieren. Ohne `N A_e`
liefert auch ein exakt angenommenes `B_s=0,75 T` keine Spannungsschwelle.

### 2.3 Ken DeLoria / Lundahl / ProSoundWeb: Chapter 6

*Exploring the Electrical Characteristics of Audio Transformers*,
**sieben PDF-Seiten**, Metadaten von 2014. Vollständig gelesen;
Ersatzschaltungen auf S. 2–3 visuell geprüft.

Das Whitepaper reduziert die wichtigsten elektrischen Eigenschaften auf
`L_P`, Kupferwiderstand, Streuinduktivität und interne Kapazität.
Es betont, dass alle gemessenen Eigenschaften von Quelle und Last
abhängen. Bei niedrigem Lastwiderstand ist Streuinduktivität besonders
relevant; bei hochohmigen Anwendungen die kapazitive Belastung.
Zusätzliche Kabelkapazität kann mit Streuinduktivität resonieren.

Die Vereinfachungen „L ignorieren“ oder „C ignorieren“ sind
**bereichsabhängig**. Beim 560Q mit sichtbarer HF-Anhebung wäre ein
vollständiges Weglassen der Wechselwirkung gerade nicht gerechtfertigt.
Der Rest des Textes enthält auch Hersteller-/Fertigungsargumente;
keinen neuen THD-Kurvensatz und keine komplette Bauteilwerttabelle.

### 2.4 GroupDIY, Thread 65719

[Vollständiger Thread](https://groupdiy.com/threads/help-with-1-1-transformer-choice-for-cathode-follower.65719/),
22 Beiträge vom 14.–17.04.2017, am 2026-10-05 zugänglich gelesen.
Kontext: kapazitiv gekoppelter Kathodenfolger, etwa 55 Ω Quellimpedanz,
unterschiedliche Lasten. Erfahrungsdiskussion, keine kalibrierte Messreihe.

- Beiträge **#2, #5, #7**: Last, Pegel und verfügbare Stromlieferfähigkeit
  gehören zur Transformatorauswahl; DCR wirkt auf LF-Gang und Klirr;
  primäre Induktivität auf Bass, Streu-L und Kapazitäten auf Höhen.
- Beiträge **#10–12**: Parallelschaltung der Primärhälften kann wegen
  kleinerer Induktivität den Treiber stärker belasten.
- Beitrag **#13**: Jensen JT-10K61-1M und angeblich 2000 H werden genannt;
  das ist hier nur ein Forumsbeleg, kein verifiziertes Produktdatum.

**Ein nachweisbarer Rechenfehler:** Beitrag #8 nennt `atan(0,5)=45°`.
Richtig ist **26,565°**. Überdies gilt eine solche einfache Phasenformel
nur für das entsprechende reduzierte RL-Netz; Sekundärlast und weitere
Widerstände verändern das Ergebnis. Auch die Pegelumrechnung in #3 ist
nicht belastbar: +22 dBu bedeuten etwa 9,76 V RMS bzw. 13,80 V Peak,
nicht die dort genannten 8,75 V Peak.

Die Schaltungsanlage und verlinkten Fremd-Datenblätter wurden nicht als
zusätzliche verifizierte Netlist/Parameterbank übernommen. Weder „geringe
Ausgangsimpedanz“ noch „1:1“ alleine bestimmt den Klang.

## 3. Neu verfügbare Fitdaten: Jensen JT-11P-1

Quelle: Whitlock-PDF **28–29**, eingebettetes Jensen-Datenblatt 1/01.
Die folgende Tabelle enthält **veröffentlichte Werte**, keine Schätzungen:

| Größe | Wert / Bedingung |
|---|---|
| Übersetzung | 1:1; angegeben 0,999…1,001 |
| Quelle | 600 Ω differentiell für die bezeichneten Übertragungstests |
| Last | 10 kΩ in Testschaltung 1 |
| Primär-DCR / Sekundär-DCR | 1,45 kΩ / 1,55 kΩ |
| Eingangsimpedanz | typisch 13,0 kΩ, min. 12,3 / max. 13,7 kΩ, 1 kHz / +4 dBu |
| Spannungsgewinn | typisch −2,3 dB, min. −2,6 / max. −2,0 dB, 1 kHz / +4 dBu |
| Frequenzgang, relativ 1 kHz | typisch −0,04 dB bei 20 Hz, −0,05 dB bei 20 kHz; jeweils Grenze −0,15…0 dB |
| −3-dB-Bandbreite | 0,25 Hz bis 100 kHz, laut erster Datenblattseite |
| Abweichung von linearer Phase | typisch +0,6°, Grenze ±2° über 20 Hz–20 kHz |
| THD bei 20 Hz / +4 dBu | typisch 0,025 %, maximal 0,10 % |
| THD bei 1 kHz / +4 dBu | <0,001 % |
| 20-Hz-Eingang bei 1 % THD | typisch **+20 dBu**, mindestens **+18 dBu** |
| Ausgangsimpedanz | typisch 2,34 kΩ, 1 kHz, Quelle 50 Ω, Testschaltung 1 |
| Kapazität Primär → Schirm/Gehäuse | 98 pF bei 1 kHz |
| Kapazität Sekundär → Schirm/Gehäuse | 110 pF bei 1 kHz |

Zusätzlich gibt es:

- Amplitudengang etwa 0,2 Hz bis 200 kHz,
- Phasenabweichung von einer linearen Phase,
- THD+N über Frequenz bei +4/+14/+20 dBu,
- THD+N über Eingangspegel bei **20/30/50 Hz**, etwa −25 bis +30 dBu.

Die beiden Klirrplots heißen in ihrer Überschrift THD, ihre Achsen aber
**THD+N**. Die Tabelle bezeichnet THD; eine vollständige Messbandbreite und
der Analysator-Rauschboden fehlen. Die Plateauwerte der Kurven können also
nicht ohne Weiteres in einzelne Harmonische zerlegt werden.

**Zwei wichtige Bezugsdetails:**

1. Die Kapazitäten 98/110 pF sind **Schirmkapazitäten**. Sie sind nicht
   automatisch die differentielle Wicklungskapazität eines
   Zweipol-HF-Ersatzmodells.
2. `DLP`, also *Deviation from Linear Phase*, ist die **Abweichung von
   einer linearen Phasenfunktion**, nicht die rohe Phase. Eine flache
   DLP-Kurve bedeutet nicht Null-Gruppenlaufzeit. Beim Fit muss eine
   gemeinsame lineare Phasenreferenz benutzt werden.

Das Beispiel-Anwendungsbild enthält ein sekundäres Serien-RC-Dämpfungsnetz
von 13 kΩ und 620 pF, mit ausdrücklichem Hinweis, es für `R_L=10 kΩ`
wegzulassen. Für den Fit der Testschaltung 1 wird es daher **nicht zusätzlich
parallel zur bereits vorhandenen 10-kΩ-Last eingebaut**.

### 3.1 Konsistenz der Widerstands- und Gainangaben

Ein einfaches 1:1-Mittelbandmodell liefert aus den veröffentlichten DCR:

```text
Zin ≈ 1450 + 1550 + 10000 = 13000 Ω
Vout/Vprimary ≈ 10000/13000 = −2,279 dB
Vout/Vsource,unbelastet ≈ 10000/13600 = −2,671 dB
Zout bei Rs=50 Ω, mit 10k-Testlast ≈ (50+1450+1550)||10000 = 2337 Ω
```

Die Werte stimmen gut mit 13 kΩ, −2,3 dB und 2,34 kΩ überein.
Damit ist **Primärklemmenpegel als Arbeitskonvention** für die genannten
Eingangspegel plausibel. Es ist weiterhin eine aus dem Schaltbild und den
Zahlen gestützte Auslegung, keine zusätzlich gemessene Spannung.

Bei einer Offline-Reproduktion wird die Sinusquellenamplitude so
kalibriert, dass der gewünschte RMS-Pegel an den Primärklemmen erreicht
wird. Den 600-Ω-Quellenwiderstand nicht entfernen: Eine direkt ideale
Spannungsquelle an der Primärseite würde gerade die Quellimpedanzwirkung
auf die Verzerrung verändern.

## 4. Welche Informationen fehlen wirklich?

| Größe / Information | Stand | Für ersten Fit handhabbar? | Was einen genaueren Fit ermöglichen würde |
|---|---|---|---|
| Referenzgerät und Anschluss | Jensen 1:1 / 600 Ω / 10 kΩ jetzt klar nutzbar | **Ja, fixieren** | weitere Lastbedingungen |
| Digitale Volt-Skalierung | Produktentscheidung, kein Materialparameter | **Ja, bewusst festlegen** | gewünschter Arbeits-/Drivebereich |
| Kupferwiderstände | vorhanden | **Ja, fest übernehmen**, ggf. Sensitivitätsband | eigene DCR-Messung mit definiertem Zustand |
| `L_m(f,Pegel)` / komplexe Permeanz | für Jensen nicht tabelliert | **Ja, effektive Größen fitten** | komplexe Leerlaufimpedanz oder phasenrichtiger Strom |
| Streuinduktivität und differentielles Kapazitätsnetz | fehlen bei Jensen; 560Q nur unvollständig spezifiziert | **Ja, zunächst `f₀/Q` bzw. wenige Ersatzglieder** | Kurzschlussimpedanz, zusätzliche Lasten, Resonanz-/Ringmessung |
| Kernverlust / Frequenzdispersion | nur indirekt in Betrag/Phase sichtbar | **Ja, schwacher positiver Verlust-/Relaxationszweig** | Wirk-/Blindstrom über Frequenz und Pegel |
| Sättigungseinsatz | 1-%-THD-Pegel und Pegelkurven vorhanden | **Ja, in V·s fitten** | H3/H5/Wellenformen bei mehreren hohen Pegeln |
| Knieform / Sättigungsexponent | aus gesamten THD-Kurven nur eingeschränkt | **Ja, wenige Kandidaten vergleichen** | Harmonischenverteilung und Grundtonkompression |
| Hysterese, Minor-Loops, Remanenz | nur qualitativ/materialbezogen | **Ja, als schwache Annahme; nicht eindeutig** | auf-/absteigende Schleifen, Bursts und Wiederanlauf |
| Gerade Harmonische / Asymmetrie | keine getrennten Daten | **Ja, zunächst symmetrisch und DC-frei** | Polaritätstest, DC-Vorbelastung, H2/H4 |
| Treiberstromgrenze und Clipping | für das Transformatorziel nicht beschrieben | **Ja, linearen Treiber annehmen** | Treiberschaltung, Lastkennlinien, Stromgrenze |
| Rauschboden und Messbandbreite | nicht vollständig angegeben | **Ja, untere Plotwerte als Grenze behandeln** | Messung des leeren Aufbaus, Filter-/Analyzerangaben |
| Absolute Kerngeometrie, Legierung und Windungszahl | nicht bekannt | **Für effektiven Audiofit nicht erforderlich** | nur für material-/bauteilidentische Rekonstruktion nötig |

**Für einen eindeutigen physikalischen Fit fehlen vor allem drei
Informationsarten:** Magnetisierungsstrom, getrennte Harmonische und
Gedächtnis-/Transientendaten. Weitere Literatur liefert dafür
Plausibilitätsbereiche, aber keine eindeutige Identifikation des Exemplars.

## 5. Konkreter Schätzstart

### 5.1 Feste, veröffentlichte Randbedingungen

```text
Nsek/Nprim = 1
Rsource   = 600 Ω
Rprimary  = 1450 Ω
Rsecondary= 1550 Ω
Rload     = 10000 Ω
DC-Bias   = 0                 eigene Erstmodell-Annahme
```

Die hohen DCR sind für diesen Line-**Eingangs**übertrager belegt; sie
werden nicht durch für andere Ausgangsübertrager genannte 40 Ω ersetzt.

### 5.2 Effektive Magnetisierung und LF-Verluste

Für das einfache 1:1-LF-Modell lautet der wirksame Widerstand

```text
R_eff = (Rsource+Rprimary) || (Rsecondary+Rload) ≈ 1741 Ω
L_m ≈ R_eff/(2π f_c)
```

Mit `f_c=0,25 Hz` ergibt das etwa **1,11 kH**. Betrachtet man die
Übertragung bezogen auf die tatsächliche Primärklemmenspannung, entfällt
der Quellenanteil in dieser vereinfachten Formel: etwa **820 H**.
Ein **Startwert von 1 kH** ist daher als effektiver LF-Wert nachvollziehbar.

Aber: −0,04 dB bei 20 Hz entspräche für einen idealen Einpol einem
`f_c≈1,92 Hz` und nur **107–144 H**, je nach Bezug. Beide Angaben lassen
sich also **nicht exakt mit einem einzigen konstanten L** erklären.
Whitlocks frequenzabhängige Permeabilität bietet eine plausible physikalische
Erklärung; zusätzlich spielen Messgenauigkeit und Definitionen hinein.

**Vorschlag:** zunächst 100–2000 H als breiten **eigenen Suchbereich**,
Start 1000 H. Einpol als Baseline gegen die garantierten Amplitudenbereiche
prüfen; bei Bedarf genau einen passiven Verlust-/Relaxationszweig ergänzen,
der die Übergänge kausal modelliert. Kein frequenzabhängiger Tabellenwert
pro Audiosample ohne dynamisches Modell.

Ein konstanter Kernverlust-Shunt wäre vorerst nur ein Hilfsparameter:
Start **2 MΩ**, Suchbereich **0,2–20 MΩ**. Die Untergrenze hat eine
Plausibilitätsstütze: Mit einer rein ohmschen Magnetisierungsparallele
und `Zin≥12,3 kΩ` ergibt sich näherungsweise `R_loss≥179 kΩ`.
Das ist keine gemessene Verlustimpedanz und kein Hystereseparameter.

### 5.3 Hochfrequenz: zuerst zwei effektive Parameter

Ein normiertes Zweipolmodell

\[
H_{HF}(j\omega)=\frac{1}{1-(f/f_0)^2+jf/(Qf_0)}
\]

lässt sich als **Startapproximation** an −0,05 dB bei 20 kHz und den
ungefähren Halb-Leistungspunkt bei 100 kHz anpassen:

```text
f0 ≈ 107,8 kHz
Q  ≈ 0,659
```

Das ist eine **eigene Zwei-Punkte-Rechnung, kein abgeschlossener Fit**.
Vorgeschlagener Suchbereich: `f0=80…200 kHz`, `Q=0,45…1,0`.
Alle vorhandenen Amplitudenpunkte und DLP müssen die spätere Auswahl
prüfen. Daraus noch keine präzisen Wicklungskapazitäten/Leckinduktivitäten
behaupten; verschiedene Netze können denselben Zweipol liefern.

McLymans Resonanzformel kann Grenzen eingrenzen, wenn ein L belegt ist.
Beispiel nur für den **560Q**: Bei angenommenen `f_r=60…150 kHz` und
dem tabellierten `L_σ=1,230 mH` ergäben sich **C≈0,9…5,7 nF**.
Da Resonanzspitze und Messseite hier offen sind, ist auch das nur ein
bedingter Suchbereich. Er wird nicht als Jensen-Kapazität übernommen.

### 5.4 Sättigungsmaßstab in Flussverkettung

Für einen Sinus gilt bei geeigneter Kernspannung:

\[
\lambda_\text{Peak}=\frac{V_\text{Peak}}{2\pi f}.
\]

Der veröffentlichte typische Anker **+20 dBu / 20 Hz / 1 % THD**
entspricht **7,75 V RMS** an der Primärseite. Daraus folgen **0,0872 V·s**
aus der Klemmenspannung. Mit einer einfachen Kupfer-Spannungsteiler-
Näherung bleiben am Kern ungefähr **0,0775 V·s**.

**Startwert `λ_scale≈0,08 V·s`, Suchbereich 0,02…0,2 V·s** ist daher
für eine erste Optimierung sinnvoll. Es ist **kein direkt gemessener
Kniefluss**: 1 % THD hängt auch von Quellenwiderstand, Last, Verlusten
und Kennlinienform ab. Der Optimierer soll diesen Ausgangspunkt anhand
der gesamten 20/30/50-Hz-Pegelkurven justieren.

Eine konstante V/f-Schwelle würde von +20 dBu bei 20 Hz ungefähr zu
**+23,5 dBu bei 30 Hz** und **+28,0 dBu bei 50 Hz** wandern. Die
Jensen-Kurven steigen in diesen Bereichen steil an; das ist eine
qualitative Plausibilitätsprüfung, keine exakte weitere Herstellerangabe.

Für eine strom-/flussbasierte Nichtlinearität zunächst wenige Exponenten
prüfen, beispielsweise **3, 5, 7, 9**; sie sind eigene Kandidaten, keine
gemessenen Materialexponenten. Ein einfaches Beispiel wäre

```text
i_mag = (lambda_scale/L0) · [u + |u|^(p−1)·u] + i_history
u = lambda/lambda_scale
```

Hier ist der nichtlineare Vorfaktor zur Definition von `lambda_scale`
fixiert. **Nicht gleichzeitig einen freien Vorfaktor und eine freie
Flux-Normierung fitten**, wenn beide nur dieselbe Kennlinienverschiebung
ausdrücken. Die Formel allein enthält noch keine Hysterese; dafür braucht
`i_history` einen definierten dissipativen Zustand und separate Prüfung.

### 5.5 Hysterese und Materialannahmen

Ein symmetrischer Start mit Null-Bias und schwacher Hysterese ist
vertretbar. Whitlock stützt eine überwiegend **H3-dominierte** Verzerrung
als Anfangsannahme; für die konkreten Bauteile ist deren genaue
H2/H3/H5-Verteilung trotzdem nicht gemessen. Ein reines statisches
Sättigungsgesetz dürfte die niedrigen Pegelplateaus der Jensen-Kurven
nicht automatisch erklären.

McLyman liefert z. B. für Permalloy/Supermalloy Materialbereiche:
`B_s≈0,65…0,82 T`; Koerzitivfelder zwischen ungefähr
`0,003…0,04 Oe` über diese beiden Materialfamilien. Sie gelten für
die beschriebenen Materialproben, **nicht als nachgewiesene Jensen-Legierung**.
Für ein effektives Modell sollten sie lediglich unwahrscheinliche
Lösungen ausschließen, nicht unbekannte Remanenz-/Hysteresekoeffizienten
scheinpräzise ersetzen.

Für Hysterese gibt es hier daher bewusst keinen erfundenen „richtigen“
Zahlenwert. Sinnvoll ist ein Vergleich von wenigen schwachen
Gedächtnisvarianten bei gleichem stationärem Fehler; deren Unterschiede
auf Bursts bleiben als Prognoseunsicherheit sichtbar.

### 5.6 Empfohlene digitale Pegelkonvention

**Eigene Produktannahme:** Ein 1-kHz-Sinus mit **−18 dBFS Peak** soll
unter Referenzbeschaltung **+4 dBu RMS an den Primärklemmen** entsprechen.
„Peak“ ist hier absichtlich genannt, damit keine 3,01-dB-RMS-Verwechslung
entsteht.

Das entspricht einer nominalen Primärskalierung von **13,80 V pro
digitaler Sampleeinheit**, für die unbelastete Quelle mit obiger
Kupfernäherung etwa **14,43 V pro Sampleeinheit**. Ein Full-Scale-Sinus
entspricht damit nominal +22 dBu. Der typische 20-Hz-/1-%-THD-Anker
liegt in dieser nominalen Zuordnung ungefähr bei **−2 dBFS Peak**;
bei niedrigen Frequenzen/hohem Drive verändert das Netz selbst die
tatsächliche Klemmenspannung.

Das ist ein sinnvoller sauberer Ausgangspunkt. Eine hörbar stärker
färbende Variante kann später bewusst früher angesteuert werden. Ein
solcher Drive-Offset wäre eigene Abstimmung, keine neue Herstellerangabe.

## 6. Wie der erste Fit konkret ablaufen sollte

1. **Datenaufbereitung:** Jensen-Kurven als Ableseintervalle digitalisieren;
   Tabellenwerte mit Toleranzen übernehmen. Keine sechs Nachkommastellen
   aus dünnen Plotlinien erzeugen. Datenblattversion und Messschaltung
   an jedem Zielpunkt führen.
2. **Linearen Anteil bestimmen:** DCR, Übersetzung, Quelle/Last fixieren;
   effektive LF-Größen und HF-Zweipol fitten. DLP mit einer gemeinsamen
   linearen Phasenreferenz vergleichen. Absolute Verstärkung separat
   prüfen, nicht durch freie Normalisierung kaschieren.
3. **Nichtlinearität bestimmen:** 20-/30-/50-Hz-Pegelkurven und
   Frequenzkurven gemeinsam verwenden; Source-Amplitude auf den
   angegebenen Primärpegel kalibrieren. Exponent und Flux-Skala zuerst,
   danach höchstens wenige Verlust-/Hystereseparameter nachziehen.
4. **Mehrdeutigkeit prüfen:** verschiedene Starts, Profil-/Sensitivitäts-
   kurven und Intervalle statt nur eines besten Zahlenvektors. Zeigen
   zwei Parameter nahezu dieselbe Wirkung, einen fixieren oder die
   äquivalente Kombination berichten. THD und Gainabfall nicht als
   voneinander unabhängige frei nachstellbare Effekte behandeln.
5. **Zurückgehaltene Fälle:** beispielsweise 30-Hz-Pegelkurve oder
   +14-dBu-Frequenzkurve erst zur Validierung verwenden. Bursts, Stille
   und Anfangszustände auf Stabilität prüfen. Nicht gemessene
   Quellen-/Lastwechsel sind Modellprognosen, keine zusätzliche Abnahme.
6. **Echtzeit später:** kontinuierliche/fein aufgelöste Referenz vor
   48/96/192-kHz-Diskretisierung; Alias-/Übergangsprüfung, C++/EEL2-
   Parität und Dwarf-CPU gemäß Projektworkflow.

Als Fehlerfunktion eignen sich gewichtete Amplituden-/Phasenfehler und
logarithmische Klirrfehler nur im aufgelösten Bereich. Bei einem Zielintervall
gibt es innerhalb des Bereichs keinen Grund, eine bestimmte Pixelmitte zu
erzwingen. Obergrenzen wie `<0,001 %` sind **einseitige Bedingungen**.

Rauschen wird dafür nicht in den DSP eingefügt. Für THD+N kann der
Messprozess mit einem unbekannten Rausch-/Restfehleranteil modelliert
werden; ohne Messbandbreite und Leeraufnahme bleibt dieser ein
Unsicherheitsparameter der Auswertung.

## 7. Welches kleine Messpaket später den größten Nutzen hätte

Für eine präzisere Bauteilemulation wäre folgende Ergänzung besonders
wertvoll, in dieser Reihenfolge:

1. **Phasenrichtige Leerlaufmessung von Eingangsstrom und Sekundärspannung**
   bei 20/50/100/1000 Hz und mehreren Pegeln. Daraus effektive
   Magnetisierung, Verluste und H–Φ-/i–λ-Schleifen bestimmen.
2. **H2/H3/H5 und Eingangs-/Ausgangsgrundton** bei etwa 20/30/50/100 Hz,
   vom kleinen Pegel bis knapp über den gewünschten 1-%-Punkt.
3. **Eine zweite Beschaltung**, z. B. Quelle 50 statt 600 Ω und Last
   100 statt 10 kΩ, bei ausgewählten Pegeln. Das trennt Quellenwirkung
   von inneren Parametern besser als sehr viele weitere Punkte im
   gleichen Aufbau.
4. **Kurzer/langer Bassburst und Wiederanlauf nach Vorbelastung**, möglichst
   mit aufgezeichnetem Strom. Damit unterscheiden sich Modelle, die im
   stationären THD-Fit fast gleich gut sind.
5. Falls physikalische Einzelwerte gewünscht sind: **Kurzschlussimpedanz
   und Hochfrequenz-Impedanz/Resonanz unter definierten Lasten**.

Reale Windungszahl, Kernquerschnitt und Legierung sind nützlich, müssen
für den ersten effektiven Audiofit aber nicht beschafft werden. Der
entscheidende Schritt ist jetzt die Festlegung einer Referenzbeschaltung
und weniger identifizierbarer Freiheitsgrade, nicht weitere pauschale
Material- oder „Vintage“-Zuordnung.

## 8. Quellenidentität und Prüfstand

```text
0e7a82774a90eee784897962ec3ed8ae17ac26122225a57596ef6c383f3bcc2d  Audio-Transformers-Chapter.pdf
7c40a46c8c541a1fb4b50029765f968e2be8f131949dcf425026132e48fae680  ourdev_725050HHOGA4.pdf
c2c9285bdf87da26d1587d515ace16169cbad8234757cc1962ea51962ad1a875  PSW_WhitePaper_Download_Chapter_6.pdf
```

Hashes beziehen sich auf die lokalen Dateien, nicht auf die auf den
Bereinigungsseiten genannten Vorgängerversionen. GroupDIY-Beiträge
werden nach Beitragsnummer und URL zitiert, nicht als Hardwaremessung.

Die Zahlen in `FIT_STARTWERTE.json` werden aus dem kurzen, ausführbaren
Rechenweg `estimate_fit_start.py` reproduziert. Die Referenzwerte,
algebraischen Schätzungen, gewählten Produktannahmen und noch fehlenden
Größen sind dort ausdrücklich bezeichnet. **Kein Fitlauf, SPICE-Render,
DSP-Port oder Hörtest des Jensen-Kandidaten wurde hier ausgeführt.**
