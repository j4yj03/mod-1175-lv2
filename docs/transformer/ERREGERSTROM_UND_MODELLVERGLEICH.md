# Erregerstrom, Impulsantwort und Transformator-Modellvergleich

Auswertung **2026-10-05** für Green Stripe 76. Ergänzt
[`PARAMETERFIT_GRUNDLAGE.md`](PARAMETERFIT_GRUNDLAGE.md) um den vollständigen
HiFiHaven-Thread, die StackExchange-Frage 606060 und vier weitere PDFs.

## 1. Ergebnis für den nächsten Fit

**Die neuen Quellen verbessern vor allem Modellwahl und Messverfahren. Sie
liefern keinen neuen kalibrierten Parametersatz für unseren 1:1-Line-
Übertrager.** Die Jensen-JT-11P-1-Kurven bleiben die bisher klarste
erste Fitreferenz.

Vier konkrete Konsequenzen:

1. **Gemessener Leerlaufstrom ist nicht automatisch reiner
   Magnetisierungsstrom.** Verlust- und kapazitive Anteile gehören zur
   Auswertung. Für den Fit benötigen wir phasenrichtige Strom-/
   Spannungsdaten oder müssen deren Aufteilung als Modellannahme behandeln.
2. **Ein dynamischer Kern mit einfacher Sättigung ist ein sinnvoller
   erster Kandidat.** `05_e.pdf` vergleicht Fröhlich und Jiles–Atherton
   in einer realen Audioanwendung. Die dort geringe Differenz rechtfertigt
   einen eigenen Modellvergleich; sie beweist nicht, dass Hysterese bei
   unseren kleinen Line-Pegeln bedeutungslos wäre.
3. **Kleinsignal-Frequenzgang und Großsignalverhalten brauchen getrennte
   Messungen.** Eine Impulsantwort identifiziert unter geeigneten Bedingungen
   den linearen Anteil, nicht die Sättigung oder sämtliche Gedächtniseffekte.
4. **Neuronale Verfahren ersetzen keine fehlenden Referenzdaten.** Die
   vorgelegte NN-Arbeit interpoliert Kennwerte aus einem bereits vorhandenen
   500-kV-Transformator-Simulationsmodell; sie erzeugt keine identifizierte
   Audio-Kernkennlinie.

Dies ist eine Quellen-/Formelprüfung, kein ausgeführter neuer Fit,
SPICE-Render, DSP-Umbau oder Hörtest. Die bisherigen Startschätzungen
werden dadurch nicht zu verifizierten Bauteilwerten.

## 2. Erregerstrom, Magnetisierungsstrom und Inrush

### 2.1 StackExchange: Zugriff und Inhalt

[Frage 606060](https://electronics.stackexchange.com/questions/606060/difference-between-the-excitation-current-of-a-transformer-and-the-magnetizing-c),
Frage vom 27.01.2022; drei Antworten, zuletzt ergänzt am 06.12.2024.
Direkter Webzugriff: **HTTP 403**. Der StackPrinter-Versuch lieferte keine
Seite. Über die **offizielle StackExchange-API** waren Frage, alle drei
Antworten und die zwei Fragekommentare zugänglich:

- `https://api.stackexchange.com/2.3/questions/606060?site=electronics&filter=withbody`
- `https://api.stackexchange.com/2.3/questions/606060/answers?site=electronics&filter=withbody`

Antworten: Andy aka (akzeptiert, ID 606093), Louis (606064),
Eng. Omar Eyad (732732). API-Inhaltslizenz: CC BY-SA 4.0. Die verlinkten
Inrush-Bilder waren direkt nicht zugänglich; daraus keine eigene
Bildauswertung behauptet.

Die ersten beiden Antworten erklären sinngemäß: Leerlauf-Erregerstrom
enthält Magnetisierung und Kernverluste; Inrush entsteht beim Einschalten
durch den Anfangszustand und gegebenenfalls starke Sättigung. Die spätere
Antwort grenzt Inrush terminologisch als Einschaltvorgang ab. Für unsere
Modellierung ist die Unterscheidung **Betriebszustand versus Zweigstrom**
wichtiger als eine einzig mögliche Benennung.

### 2.2 Präzise Arbeitsdefinition für Green Stripe

Im einfachen, primärbezogenen Ersatzschaltbild mit
`n=Nsek/Nprim`, festgelegter Stromorientierung und ohne kapazitive
Verschiebungsströme gilt:

```text
i_prim = n · i_sek + i_exc
i_exc  = i_mag + i_loss          gewählte Ersatzmodell-Aufteilung
```

- **`i_exc`**: gesamter Erregerstrom des Kernzweigs.
- **`i_mag`**: Strom des überwiegend energiespeichernden,
  gegebenenfalls nichtlinearen Magnetisierungszweigs.
- **`i_loss`**: im gewählten Modell gesondert geführte Kernverlustanteile.

Bei einer realen Leerlaufmessung ist `i_prim` zusätzlich um Ströme in
Wicklungs-/Kopplungskapazitäten, Messgeräten und gegebenenfalls anderen
angeschlossenen Wicklungen zu bereinigen. Bei tiefen Frequenzen kann
dieser Zusatz klein sein, bei hohen Frequenzen nicht voraussetzen.

**Wichtig:** Diese Aufteilung ist ein Ersatzmodell. Eine dynamische
Hysteresekennlinie kann die dissipative Wirkung bereits im Kernstrom
enthalten. Dann nicht noch einmal denselben Verlust durch einen frei
addierten Widerstand nachbilden. Aus einer einzigen gemessenen Stromkurve
folgt keine eindeutige momentane Zerlegung in zwei physikalisch separat
messbare Ströme.

Im linearen Sinusfall ist eine Zeigerzerlegung möglich:

\[
\underline I_{exc}=\underline V_c
\left(G_c+\frac{1}{j\omega L_m}\right).
\]

Wirk- und Blindanteil addieren sich **komplex**, nicht als einfache Summe
von RMS-Beträgen. Bei Sättigung ist der Strom nicht sinusförmig; eine
einzige 90°-Annahme für seine gesamte Wellenform reicht nicht.

Für den kleinen, sinusförmigen Messfall, nach Korrektur der Parasiten:

```text
Y1 = Iexc,1 / Vcore,1
Gc = Re(Y1)
Lm = -1 / [omega · Im(Y1)]       nur bei netto induktivem Blindanteil
```

`Rc=Vcore,RMS²/Pcore` ist ein äquivalenter Wirkleistungswert am jeweiligen
Arbeitspunkt, keine vollständige Hysteresekennlinie.

### 2.3 Was künftig gemessen beziehungsweise gefittet werden sollte

Phasenrichtig und gleichzeitig: **Primärspannung, Primärstrom und
Sekundärspannung**, unter Last möglichst auch Sekundärstrom. Dazu Quelle,
Last, Kopplungskondensatoren und Messbandbreite dokumentieren.

Eine mögliche Rekonstruktion lautet:

\[
v_c=v_p-R_p i_p-L_{\sigma p}\frac{di_p}{dt},\qquad
\lambda(t)=\lambda(0)+\int v_c(t)\,dt.
\]

Im Leerlauf kann die Sekundärspannung eine alternative Flussinformation
geben, nach Übersetzungs-/Orientierungs- und Parasitenkorrektur. Die
Integration darf nicht durch einen Messoffset wegdriften. Das Korrigieren
eines Instrumentenoffsets ist aber nicht dasselbe wie das willkürliche
Entfernen einer realen Remanenz.

Für eine geschlossene periodische Kernschleife liefert
`∮ i_exc dλ = ∫ v_c i_exc dt` die aufgenommene Energie pro Zyklus.
Bei dynamischer Anregung enthält sie auch weitere Kernverluste wie
Wirbelströme; sie ist nicht automatisch reine quasistatische Hystereseenergie.

### 2.4 Einschaltstrom ist kein eigener dauerhafter Klangparameter

Bei einer ideal angelegten Sinusspannung ab `t=0`, Null-Anfangsfluss und
Einschalten im Spannungsnulldurchgang ergibt die Integration:

\[
\lambda(t)=\frac{V_{pk}}{\omega}\left(1-\cos\omega t\right).
\]

Der erste Flusshub kann doppelt so groß wie der stationäre Scheitel sein;
Remanenz und Serienverluste verändern dies. Der anschließende Stromanstieg
hängt von der nichtlinearen Kernbeziehung ab. Das ist ein sinnvoller
**Anfangszustands-/Bursttest**, kein Beleg für permanenten H2-Klirr.

Eine symmetrische stationäre Anregung eines zentrierten symmetrischen
Modells liefert vorwiegend ungerade Harmonische. DC-/Remanenzverschiebung
oder asymmetrisches Einschwingen kann gerade Anteile erzeugen. H2 darf
deshalb nicht allein wegen eines Inrush-Beispiels in die normale
Line-Übertrager-Kennlinie eingebaut werden.

## 3. HiFiHaven: alle sechs Seiten

[Thread 10495](https://hifihaven.org/index.php?threads/why-you%E2%80%99re-not-crazy-to-use-repeating-coils-bridging-transformers-between-digital-and-analog-audio.10495/),
**110 Beiträge**, 24.06.2023–18.01.2025, alle sechs Seiten am 2026-10-05
gelesen. Seite 4 war der vom Benutzer genannte Einstieg.

| Seiten / Beiträge | Inhalt und Verwendbarkeit |
|---|---|
| 1, #1–20 | Oszilloskop-Vorher/Nachher bei etwa 200 Hz, subjektive Eindrücke, Übertragerlisten; #15 erläutert sinnvoll die quadratische Impedanztransformation |
| 2, #21–40 | Erfahrungsberichte, Bandbreitenspezifikationen und Ringing; #35 berichtet eine Blindbox, aber ohne ausreichendes Pegel-/Versuchs-/Statistikprotokoll für eine Abnahme |
| 3, #41–60 | Diskussion von Rekonstruktion/Filterung; ab #46 konkrete **separate LCL-/LC-Filter**, kein identifizierter Übertrager |
| 4, #61–80 | Kabel-/Lastkapazität, zusätzliche Dämpfung, FFT- und 20-Hz-Klirrtests, Aufbau des Filters und weitere Höreindrücke |
| 5, #81–100 | Wicklungstaps, Anschluss-/Massefragen, Produktberichte; keine neue Messmatrix |
| 6, #101–110 | weitere Erfahrungsberichte, Produktlinks und Anschlussvarianten; kein neues kalibriertes Referenzsignal |

### 3.1 Verwertbare Hinweise

- **Quelle, Last, Kabel und Dämpfung gemeinsam betrachten.** Eine
  externe Kabelkapazität ist nicht automatisch innere Wicklungskapazität.
- **Ringing zusätzlich zum Frequenzgang prüfen.** Ein nominelles
  Übertragungsband sagt noch nicht, ob der Übergang stark überhöht ist.
- **Spektren vor und hinter dem Gerät** bei definiertem Pegel erfassen,
  insbesondere auch tiefere Sinustöne. Das ist aussagekräftiger als ein
  optisch „glatterer“ einzelner Scope-Trace.
- **150:600 ist ein Impedanzverhältnis**, bei passender Verschaltung
  typischerweise 1:2 Spannungsübersetzung, nicht 1:4. Eine andere
  Verschaltung ändert auch Induktivität, Verluste und Headroom.

### 3.2 Konkrete Schaltung auf Seite 3/4 ist ein Zusatzfilter

Die zugängliche Bildvorschau zu **#60** wurde gelesen:
`76,8 Ω` Serie, `150 mH` Serie, `220 pF` gegen Masse,
`27 kΩ + 10 nF` als Serien-RC-Dämpfungszweig gegen Masse,
`100 kΩ` Last. Später kommen Drossel-DCR und Kabelkapazität hinzu.
Diese Größen sind **keine gemessenen Streu-/Kernparameter** eines
WE111C oder Jensen.

Die grobe LC-Eigenfrequenz von 150 mH und 220 pF beträgt **27,7 kHz**.
Das ist nicht automatisch der −3-dB-Punkt: Quellenwiderstand, Dämpfungs-
zweig und Last verschieben den tatsächlichen Verlauf. Die im Thread
genannten Simulationen sind nicht hier selbst reproduziert.

Einheiten-/Kontextfehler nicht übernehmen: #55 nennt zunächst 220 µF,
#56 korrigiert auf **220 pF**; #65 bezeichnet eine Drossel als „150 mF“.
#66 verwendet „185 pF für 3 Meter“, obwohl zuvor 1-m-Kabel und pF/m-Werte
genannt werden. Solche Angaben benötigen Klärung, bevor sie ein Fit-Ziel
werden.

### 3.3 Nicht als Modellbeleg übernehmen

Die Behauptung, ein Transformator fülle fehlende digitale Information auf,
ist nicht durch die Scope-Bilder belegt. Ein korrekt rekonstruiertes
bandbegrenztes Signal besteht nicht aus hörbaren Lücken zwischen Samples.
Ein analoges Netz kann Rekonstruktionsbilder oder HF-Störungen dämpfen,
Amplitude/Phase verändern und bei Nichtlinearität neue Spektralanteile
erzeugen; diese neu erzeugten Anteile sind keine wiedergewonnenen Samples.

Auch **lineares Ringing erzeugt keine stationären neuen Harmonischen**
eines reinen Sinus. Es ist die transiente Antwort eines frequenzselektiven
Systems. Nichtlineare Harmonische und lineares Nachschwingen sind
unterschiedliche Prüfgrößen.

Scope-Treppen oder gestrichelte Linien allein identifizieren weder Aliasing
noch Hörbarkeit. Im Thread werden mehrfach „Aliases“ und analoge
Rekonstruktionsbilder vermischt. Eine nachgeschaltete analoge Filterung
entfernt keine schon im digitalen Audioband gefalteten Aliasanteile.

Die Aussage „Impulsantwort und Frequenzgang enthalten dieselbe Information“
gilt vollständig für **LTI-Verhalten**. Für den arbeitenden nichtlinearen
Kern fehlt damit die Pegel-/Historienabhängigkeit. Ebenso folgt aus einem
Nulltest an einem Signal keine universelle Gleichheit zweier nichtlinearer
Systeme unter allen Einstellungen und Anfangszuständen.

**Zugriffsgrenze:** Scope-Vorher/Nachher-Vorschaubilder und die Filter-
Schaltungsvorschau waren abrufbar. Die Original-Scope-Anhänge gaben
HTTP 403 zurück; Achsen/Spannungen wurden daraus nicht quantifiziert.
Der zusätzliche Audio-Amateur-Scan und ausgehende Produkt-/Bloglinks
wurden nicht als neue Primärmessungen ausgewertet.

## 4. Bal / Öncü: Magnetisierungsstrom im Stromwandler

**Güngör Bal, Selim Öncü**, *Effects of a current transformer's magnetizing
current on the driving voltage in self-oscillating converters*, Turkish
Journal of Electrical Engineering & Computer Sciences **22 (2014),
191–201**, DOI **10.3906/elk-1205-38**.

Lokale Datei hat 13 Seiten: Bereinigungsseite, Repositorydeckblatt und
elf Artikelseiten. Artikel S. 191 = PDF 3. Volltext gelesen;
Modellgleichungen/-tabellen PDF 5–7 zusätzlich visuell geprüft.

### Was untersucht wurde

- **Stromgetriebener** Ferrit-Toroid Philips TN23/14/7, Material **3F3**.
- Primär eine Windung, Sekundär **40/45/50 Windungen**.
- Primärstrom etwa **2 A Peak bei 40 kHz**; Last aus **15-V-Zenerdioden**
  zur Ansteuerung selbstschwingender Leistungselektronik.
- Kern als **ungesättigte lineare Magnetisierungsinduktivität**;
  Kernverluste, Wicklungskapazitäten und Temperatur ausdrücklich ignoriert.

Die Autoren vergleichen gekoppeltes Induktivitätsmodell, reduziertes
Ersatzbild und Hardware. Ein Teil des sekundärbezogenen Stroms fließt
in den Magnetisierungszweig, der Rest in die Zenerlast. Das verschiebt
die Umschaltzeit der Ausgangsspannung. Die Grundidee der Stromaufteilung
und der Lastwechselwirkung ist übertragbar, die Millihenry-/Zenerwerte
sind es auf unseren 1:1-Line-Fit nicht.

**Plausibilitätscheck:** Für 40 kHz, 15 V und `Lm=3,044 mH`
ergibt eine symmetrische Rechteckspannung einen dreieckförmigen Strom
mit `ΔIpp=V/(2fLm)≈61,6 mA`, also `Ipk≈30,8 mA`.
Das passt zum berichteten rund 31-mA-Wert. Die Gleichungen auf S. 194
wechseln zwischen Halbperiodenhub, Anfangsstrom und Peak; bei einer
Übernahme ist der Faktor 2 explizit zu prüfen.

Der Text nutzt `Ll=(1−k)Ls` und `Lm=kLs` für seine Aufteilung. Das ist
nicht ungeprüft gleichzusetzen mit der am kurzgeschlossenen zweiten Port
gemessenen Gesamtstreuinduktivität `Lsc=L1(1−k²)` eines idealisierten
gekoppelten Spulenpaars. Ersatzbild, Bezugsseite und Kopplungsdefinition
müssen übereinstimmen.

**Nutzen:** Leerlauf-/Laststrom und Zustand beeinflussen Amplitude und
Phase. **Kein** Nachweis einer Audio-Sättigungs-/Hysteresekennlinie, da
diese im Modell gerade ausgeschlossen ist.

## 5. Shadid et al.: Impulsantwort zur Wicklungsfehlererkennung

**Mozon Shadid, Noureddine Harid, Braham Barkat, Ashwin Manjunath**,
*Application of the Impulse Response of Transformer Winding for Detection
of Internal Turn-to-Turn Short Circuits*, UPEC 2022,
DOI **10.1109/UPEC55022.2022.9917862**. Sechs PDF-Seiten vollständig
gelesen; Formeln, Messaufbau und Ergebnistabellen auf S. 2–4 visuell geprüft.

### Übertragbare Methode

Vergleich gesunder und absichtlich fehlerhafter **10-kVA-/0,4-kV-/50-Hz-
Dreiphasentransformatoren**. Fünf unterschiedlich schnelle Doppel-
Exponentialimpulse decken verschiedene Frequenzbereiche ab; Vergleich
gegen eine Referenzsignatur. Gezeigt werden Leerlauf-, Kurzschluss-,
kapazitive und induktive Zwischenwicklungs-Messkonfigurationen.

Für Audio nützlich ist die Idee, durch **mehrere Messkonfigurationen**
Magnetisierung, Streuung und kapazitive Kopplung besser zu unterscheiden.
Eine kleine Impuls-/Sweepmessung kann lineare Pole und Dämpfung liefern.
Die Wicklungsfehler-Signaturen selbst sind keine Audio-Zielkurven.

### Gedruckte Formelfehler beachten

Auf S. 2 steht tatsächlich

```text
h(t) = Vout(t)/Vin(t)                        Gl. 1
H = Fourier{h(t)}                            Gl. 2
```

**Das ist für ein dynamisches System im Allgemeinen falsch.**
Korrekt ist im LTI-Fall bei geeigneter Anregung und Messung:

\[
y=h*x,\qquad H(f)=\frac{Y(f)}{X(f)},\qquad h=\mathcal F^{-1}\{H\}.
\]

Die zeitpunktweise Division von Wellenformen ist keine Entfaltung.
Gl. 3 des Papers benutzt anschließend das richtige Verhältnis der
Spektralbeträge in dB; das behebt die Inkonsistenz der vorigen Definition
nicht. Ohne Quellcode ist unklar, welcher Weg tatsächlich programmiert
wurde.

Weitere sichtbare Probleme: Gl. 4 enthält im Korrelationszähler eine
**Differenz statt des Kovarianzprodukts**; „t-test=0“ ist eine
Entscheidungskennzahl, keine Aussage exakter Gleichheit; Tabellen nennen
20 MHz als obere Grenze, der beschriebene Versuch 2 MHz.
Keine dieser unklaren Formeln wird in unsere Auswertung übernommen.

Für unseren linearen Messpfad wäre z. B. ein regularisierter Schätzer

```text
H(f) = Y(f) · conj(X(f)) / [|X(f)|² + epsilon(f)]
```

vertretbar, mit phasenrichtigem Zeitbezug und brauchbarer Anregungsenergie
im jeweiligen Bin. `epsilon` ist ein dokumentierter Mess-/Noiseparameter,
kein frei kaschierender Klangfaktor. Überlappende Bänder mehrerer Anregungen
müssen Betrag und Phase konsistent liefern. Bei großem Pegel ist ein
einzelnes `H(f)` keine vollständige Beschreibung der Nichtlinearität.

## 6. Wu et al.: neuronaler Fit von Magnetisierungsstrom-Kennwerten

**Guoxing Wu, Peng Wang, Yonghao Ren, Yuanda Song, Sheng Lin**,
*Research on Calculation Method of Transformer Magnetizing Current Based
on Neural Network Fitting*, IEEE APAP **2019, S. 969–973**,
DOI **10.1109/APAP47170.2019.9225003**. Titel/DOI zusätzlich über
Crossref-Metadaten abgeglichen. Fünf PDF-Seiten vollständig gelesen;
Definitionen, Netzwerk und Ergebnisplots auf S. 970–972 visuell geprüft.

### Was tatsächlich gefittet wird

- Bereits vorhandenes **PSCAD-Modell eines 500-kV-Autotransformators**.
- Eingang des Fits: **DC-Strom am Neutralpunkt**.
- Vier Ausgänge über separate Netze: Mittelwert/DC, Maximum, Minimum
  und THD des Magnetisierungsstroms. **Keine sampleweise Audiowellenform.**
- Training: −100…+100 A in 2-A-Schritten. Test: versetztes Raster
  −99…+101 A. Das ist überwiegend Interpolation derselben Simulationsfamilie,
  am letzten Punkt leicht darüber hinaus.
- Je Netz 50 Hidden-Neuronen, `logsig` → `purelin`, `trainbr`.

Damit kann ein teures vorhandenes Modell durch einen schnellen
Kennwertschätzer ersetzt werden. Das Netz identifiziert weder aus dem
Nichts den Kern noch ersetzt es Messdaten eines anderen Bauteils.
Kein vollständiger Gewichtssatz oder Audio-Referenzdatensatz ist angegeben.

### Grenzen der vorliegenden Zahlen

Fig. 3 bezeichnet Werte bis ungefähr **700–800 A** als DC-Mittelwert,
während Fig. 4/5 Extrema etwa zwischen **−20 und +15 A** zeigen.
Ohne eine zusätzlich erklärte Skalierung können dies nicht Mittelwert
und Extrema desselben Stroms sein. Auch die empirische Hidden-Layer-
Formel erklärt die gewählten 50 Neuronen nicht unmittelbar. Die Kurven
sind daher kein quantitatives Fit-Ziel für uns.

**Übernehmbar:** Mess-/Simulationsdaten und Testpunkte trennen;
Rechenzeit durch einen erst später trainierten Ersatzschätzer reduzieren.
**Nicht geliefert:** zustandsbehaftetes Audiomodell, Energie-/
Passivitätsgarantie, Generalisierung auf andere Frequenzen/Quellen/Lasten
oder ein Satz Hysteresekoeffizienten.

## 7. `05_e.pdf`: direkt relevanter Audio-Modellvergleich

**Jaromir Macak, Jiri Schimmel**, *Simulation of a Vacuum-Tube Push-Pull
Guitar Power Amplifier*, DAFx-11, Paris, 2011, Proceedings **S. 59–62**.
Die lokale PDF hat fünf Seiten, davon eine Bereinigungsseite; Artikel
Seite 1 / Proceedings 59 = PDF 2. Volltext und alle Modell-/Ergebnisseiten
gelesen, Formeln und Tabellen visuell geprüft.

### 7.1 Die zwei Kernvarianten

**Fröhlich-Sättigung, ohne Hysterese:**

\[
B=\frac{H}{c+b|H|}.
\]

**Jiles–Atherton:** zusätzliche Magnetisierungshistorie, mit Korrektur
unphysikalischer kleiner Hystereseschleifen nach einer weiteren Quelle.
Die Gleichungen werden zusammen mit der Röhrenstufe und einer
frequenzabhängigen Lautsprecherlast implizit gelöst.

Wichtig für unser Modellverständnis: „ohne Hysterese“ heißt hier **nicht
zustandsloser Audio-Waveshaper**. Der Fluss wird weiterhin aus der
Wicklungsspannung integriert. Die algebraische B-H-Beziehung wird in
einen dynamischen, lastgekoppelten Kreis eingesetzt.

### 7.2 Ergebnis und Aussagegrenze

Verglichen wird die vollständige Endstufe mit einer **Engl-Combo**, nicht
ein isolierter 1:1-Übertrager. Lautsprecherimpedanz hat einen deutlichen
Einfluss. Unterschiede zwischen Fröhlich und J-A sind für diese
Versuche klein und vor allem unter etwa **150 Hz** sichtbar.

Tabelle 2 nennt eine „normalized computational complexity“ von
0,04 / 0,05 / 0,12 / 0,27 % für konstante Last / Lautsprecher / Fröhlich /
J-A. Diese Zahlen sind historisch und unzureichend für eine Übertragung
auf Dwarf oder unseren Solver; keine Zielgeräte-CPU-Aussage daraus ableiten.
Die Offlineimplementation verwendet Matlab/MEX-C, Newton mit bis zu
100 Iterationen und numerischem Jacobian. Das ist kein unmittelbar
übernehmbares Echtzeit-Budget unseres Plugins.

Die Autoren sagen ausdrücklich, dass Kernparameter experimentell
gewählt wurden. Die Fröhlich-Beispielwerte `c=113,38`, `b=0,71`,
`A=0,003 m²`, `l=0,2 m`, `N1=1560`, `N2=60` sind ein
**Röhren-Ausgangsübertragerbeispiel**, keine Jensen-/Hammond-Kalibrierung.
Beim J-A-Satz steht im PDF außerdem „3a = 8,56“; diese Schreibweise ist
kein eindeutiger Wert `a=8,56` und wird nicht still korrigiert.

### 7.3 Geometriefreie Form als zusätzlicher Kandidat

**Eigene algebraische Umformung** von Fröhlich, bei festgelegter
Bezugswicklung und ohne Hysterese:

```text
lambda = N · A · B
i_mag  = l · H / N
L0     = N² · A / (c · l)
lambda_sat = N · A / b

i_mag(lambda) = (lambda/L0) / (1 - |lambda|/lambda_sat)
```

Gültig für `|lambda| < lambda_sat`. Damit reichen für diese
Kernkennlinie zunächst **Kleinsignalinduktivität und Flussverkettungsmaßstab**;
Windungszahl und Geometrie müssen nicht einzeln identifiziert werden.
Nahe der Polstelle ist ein geeignet begrenzter impliziter Lösungsweg
erforderlich; bloßes Abschneiden des Flusszustands wäre keine äquivalente
Implementierung. Ein glattes Potenzmodell bleibt eine weitere
Baseline ohne diese Polstelle.

Die vorher aus +20 dBu/20 Hz abgeschätzten etwa **0,08 V·s** bleiben
ein **Startmaßstab**, nicht automatisch `lambda_sat` oder ein genauer
Fröhlich-Kniepunkt. Kernform und Netzwerk müssen gemeinsam an den
Ausgangsdaten gefittet werden.

Eine einfache 1:1-Netz-Baseline zeigt zugleich die nötige Rückwirkung:

```text
Ra = Rsource + Rprimary
Rb = Rsecondary + Rload
i_exc = F(lambda) + Gcore · vcore

d(lambda)/dt = vcore
             = [vsource - Ra·F(lambda)] / [1 + Ra/Rb + Ra·Gcore]
vout = vcore · Rload/Rb
```

Hier sind Streuung und HF-Kapazitäten zur Herleitung weggelassen.
Für positive Widerstände, `Gcore≥0` und monotones `F` ist der
Nullzustand rückstellend statt der zuvor gefundenen positiven
DDT-Rückkopplung. Das ist eine **Modellkonstruktion**, noch kein
Simulations-/Stabilitätsnachweis einer diskreten Implementierung.

## 8. Aktualisierte praktische Empfehlung

### Modellvergleich statt sofortiger großer Hysteresefit

1. **Baseline A:** lineares Referenznetz plus dynamischer
   Sättigungskern (glattes Potenzgesetz oder Fröhlich), ohne Remanenz.
2. **Kandidat B:** dieselbe elektrische Beschaltung plus schwacher
   dissipativer Gedächtniszweig nach konsistent formulierter GC-Methode.
3. **J-A erst als weiterer Vergleich**, wenn B mit den verfügbaren
   Messungen nicht genügt oder gezielt Remanenz/Minor-Loops benötigt werden.

Baseline A kann Hystereseplateaus bei kleinen Pegeln verfehlen. Das ist
eine messbare Modellauswahlfrage und darf nicht mit einem beliebigen
statischen Noise-/Klirrterm verdeckt werden. Die DAFx-Ergebnisse
belegen nicht, dass A beim Jensen unter allen Pegeln ausreicht.

### Was die Messliste jetzt genauer festlegt

- Leerlauf-Erregerstrom **einschließlich Phase und Wirkleistung** aufzeichnen;
  Strom-, Verlust- und Parasitenaufteilung konsistent modellieren.
- Linearer Frequenzgang: ausreichend kleiner Pegel, gespeicherte
  Eingangs-/Ausgangssignale, komplexes Spektralverhältnis; kein
  punktweises Teilen von Zeitkurven.
- Harmonische: mehrere Pegel/Frequenzen, H2/H3/H5 und Grundtongain;
  Grundtonspannung vor/nach Quellenwiderstand unterscheiden.
- Gedächtnis: zwei Einschaltphasen (Nulldurchgang/Maximum), kurze/lange
  Bassbursts und Wiederanlauf nach Vorbelastung.
- HF: Lastkapazität und Dämpfung einschließlich externer Kabel getrennt
  dokumentieren, nicht alle Höhenänderungen dem magnetischen Kern zuordnen.

Ohne neue Hardwaredaten kann der bereits vorgeschlagene Jensen-
Gray-Box-Fit weiterhin mit Schätzbereichen starten. Ein neuronales
Kennwertmodell oder eine Hochspannungs-Wicklungsdiagnose löst die
verbleibende Mehrdeutigkeit nicht. Für die erste Umsetzung ist ein kleiner
transparenter Zustandskern mit nachvollziehbarer Verlustbehandlung
die am besten begründete Richtung.

## 9. Quellenidentität

Alle vier lokalen PDFs wurden vollständig als Text gelesen; genannte
Modell-/Methoden-/Ergebnisseiten zusätzlich mit Poppler gerendert und
visuell geprüft. Keine der lokalen Originaldateien wurde verändert.

```text
8cf8e6fedd5c5140cad5d8f0bfee7df7149644ab73370a744965431d738b06e4
  Effects of a current transformers magnetizing current on the dri.pdf
cd5a7fc2966a27d86db4c062b2f4a8956d63276f2cfa044d38472eb5edc0adbb
  Application_of_the_Impulse_Response_of_Transformer_Winding_for_Detection_of_Internal_Turn-to-Turn_Short_Circuits.pdf
b6dbf690f748cc7f13ee5409eac7e89c6d38e6483251417a947a0519605aef0c
  Research_on_Calculation_Method_of_Transformer_Magnetizing_Current_Based_on_Neural_Network_Fitting.pdf
a2f04f897eb7cfbe8efa23a141f859cefaf6cf371670bbe65786537c85027d63
  05_e.pdf
```

Die auf Bereinigungsseiten genannten Hashes früherer Originalfassungen
sind davon zu unterscheiden. Webzugriff am 2026-10-05; StackExchange
über API, HiFiHaven alle sechs Textseiten. Die eigenen Zahlenprüfungen
betreffen Einheiten, Integral-/Spektralbeziehungen und einfache
Ersatzbildrechnungen, keine neuen Gerätemessungen.
