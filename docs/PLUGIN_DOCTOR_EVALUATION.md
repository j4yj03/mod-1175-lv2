# Auswertung der PluginDoctor-Messungen — JSFX Mono

Ausgewertet und erweitert am **2026-10-03**, anhand aller **55 Dateien** in
`evaluation_plugindoc/Versuch 1/` bis `Versuch 7/`:
29 Graph-Textdateien und 26 Screenshots. Originaldaten sind unverändert.
Maschinenlesbare Kennwerte und Dateihashes:
[`PLUGIN_DOCTOR_EVALUATION.json`](PLUGIN_DOCTOR_EVALUATION.json).

## Kurzfazit

1. **Kompression funktioniert:** im Standardversuch ungefähr 4,00:1,
   bei stark angefahrenem All Buttons ungefähr 19,9:1.
2. `Colour=100` erzeugt zusätzliche gerade Harmonische. `Colour=0` entfernt
   die Audiopfadfärbung, nicht die Nichtlinearität der Kompressorregelung.
3. Der auffällige Hochtonabfall in `LinearAnalysis` ist bei diesen Einstellungen
   **keine isolierte Messung eines linearen Filters**. Der kräftige Deltaimpuls
   verändert die GR während seiner eigenen, oversample-gefilterten Antwort.
4. Die aktuelle native DSP-Fassung reproduziert die exportierten Delta-Spektren
   mit periodischer Anregung bis auf etwa **0,003–0,007 dB**. Der saubere
   Identitätspfad ohne Kompression ist dagegen praktisch eben.
5. Die Ergebnisse belegen noch keine Attack-/Release-Zeiten, Stereo-Link-
   Funktion, REAPER-7-Hostintegration oder Originalhardwaretreue.
6. **Versuch 4/5 isolieren die Färbung ohne dynamische GR:** bei gleicher
   fast vollausgesteuerter Sinusanregung etwa **3,52 % / 19,63 % THD**.
   Input +15,6 und Output −15,6 erhalten den Kleinsignal-Gain, erhöhen aber die
   Vorverstärker-Aussteuerung. Das ist Sättigung, kein trotz Off laufender
   Kompressor.
7. **Versuch 6 bestätigt extern den sauberen Pfad:** etwa −0,02 dB bei der
   Deltaantwort; maximal rund **0,050 dB** zusätzlicher Betragsabfall zwischen
   20 Hz und 20 kHz. Bei dieser Inputstellung befindet sich der 20:1-Ramp-Test
   fast vollständig unterhalb des Knies.
8. Alle **acht Delta-Spektren** (Versuch 7 enthält zwei) lassen sich mit dem
   vorhandenen Code reproduzieren. Neue Fälle 4–7: maximal **0,00003–0,00275 dB**
   FFT-Abweichung über 20 Hz…20 kHz; kein DSP-Umbau erforderlich.

Die detaillierte Ergänzung zu Versuch 4–7 steht in **Abschnitt 11**.

**Versionshinweis:** Die externen Dateien beziehen sich auf die vom Benutzer
gemessene Fassung (kein ausführbarer Hash mitgeliefert). Nach der separaten
CPU-Optimierung **0.1.1** wurden alle Delta-/Sinus-Gegenproben wiederholt;
stationäre Ergebnisse bleiben innerhalb derselben ursprünglichen Fehlergrenzen.
Die Optimierung und bewusst geänderten Off-/Link-Übergänge sind in
[`CPU_ANALYSIS.md`](CPU_ANALYSIS.md) dokumentiert. Kein Klangparameterfit aus
den Messdaten wurde vorgenommen.

## 1. Messumgebung und Aussagegrenzen

Die Screenshots zeigen **PluginDoctor 2.3.2 (64-bit)** mit **Cockos ReaJS** und
`GreenStripe/GreenStripe76-Mono.jsfx`. Das ist ein tatsächlicher externer
JSFX-/Oberflächentest, **kein direkt in REAPER 7 ausgeführter Test**.

Aus den Exporten lässt sich 44,1 kHz ableiten:

- Frequenzraster etwa `2,69198 Hz = 44100/16384`.
- IR-Zeitraster etwa `0,02268 ms = 1000/44100`.
- Linear/Harmonic: 8191 Punkte je Ausgabekurve, passend zu 16384 FFT-Samples.
- IR: 16384 Punkte je Ausgabekurve.
- Hammerstein: sechs Ordnungen, jeweils 4094 exportierte Punkte.

Auf den Screenshots sichtbar:

| Messung | Einstellung |
|---|---|
| LinearAnalysis | Delta-Anregung; **+6,45 dB** in Versuch 1–3, **0,00 dB** in Versuch 4–7 |
| HarmonicAnalysis | Sinus etwa **2516,7 Hz**, **−0,32 dB** Eingangspegel |
| Dynamics | **Ramp**, −100…0 dB, Schritt 1 dB, **T=1,5 s** |
| Hammerstein | Ordnung **6** |

Nicht mitgeliefert: Version/Hash der extern geladenen `.jsfx`/Includes,
ReaJS-Version, vollständige Settings-Seite, Performance-/Attack-Release-
Aufzeichnung oder unbearbeitetes Input-/Output-WAV-Paar. Die Screenshot-
Reglerwerte und die folgenden Codevergleiche sind starke Indizien, aber keine
formal belegte Identität aller ausführbaren Dateien.

In Versuch 1 und 2 sind `Clipboard01.jpg` und `Clipboard02.jpg` jeweils
**byteidentisch**; sie sind keine zweite unabhängige Aufnahme. Versuch 1 hat
dadurch keine eigene Harmonic-/Hammerstein-Screenshotansicht. Die zugehörigen
Textdateien wurden trotzdem vollständig numerisch ausgewertet.

## 2. Plugin-Einstellungen

Alle Versuche: Mono, Mix 100 %, Enabled On, Custom.

| Versuch | Input | Output | Attack | Release | Ratio | Colour |
|---|---:|---:|---:|---:|---|---:|
| 1 | 0 dB | 0 dB | 3 | 5 | 4:1 | 100 % |
| 2 | +24 dB | −11,2 dB | 1 | 7 | All Buttons | 100 % |
| 3 | +24 dB | −11,2 dB | 1 | 7 | All Buttons | 0 % |

Versuch 2 gegen 3 ist deshalb ein sinnvoller Colour-Vergleich.
Versuch 1 gegen 2 verändert dagegen mehrere Regler gleichzeitig; daraus lässt
sich nicht die isolierte Wirkung der Ratio oder der Attack ableiten.

Neue Versuche:

| Versuch | Input | Output | Attack | Release | Ratio | Colour | Compression |
|---|---:|---:|---:|---:|---|---:|---|
| 4 | 0 dB | 0 dB | 1 | 1 | All Buttons | 100 % | **Off** |
| 5 | +15,6 dB | −15,6 dB | 1 | 1 | All Buttons | 100 % | **Off** |
| 6 | −15,6 dB | +15,6 dB | 7 | 7 | 20:1 | **0 %** | On |
| 7a | −6 dB | +6 dB | 7 | 1 | 4:1 | **0 %** | On |
| 7b | −6 dB | +6 dB | 7 | 1 | All Buttons | **0 %** | On |

Versuch 4, 5 und 6 haben je vier Textdateien und vier Screenshotansichten,
aber keinen separaten IR-Export. Versuch 7 enthält ausschließlich zwei
`LinearAnalysis`-Spektren und deren Screenshots; die Frequenz-x-Achse in Hz
darf nicht als Zeitachse oder stationäre Kompressionskennlinie gelesen werden.

## 3. Statische Kompressionskennlinien

`dynamics*.txt` enthält **Input-dB → Output-dB**, keinen zeitlichen
Attack-/Release-Verlauf. Die Ratio wurde aus einer linearen Regression über
−12…0 dB Input bestimmt, also deutlich oberhalb des weichen Knies:

\[
R_{eff}=\frac{1}{dL_{out}/dL_{in}}.
\]

| Kennwert | Versuch 1 | Versuch 2 | Versuch 3 |
|---|---:|---:|---:|
| Kleinsignal-Gain | −0,0131 dB | +12,7866 dB | +12,8000 dB |
| Ratio, Regression −12…0 dB | **4,0045:1** | **19,9029:1** | **19,8672:1** |
| Ratio, Regression −6…0 dB | 4,0137:1 | 19,9541:1 | 19,9004:1 |
| Erster 1-dB-Reduktionspunkt | −23 dB Input | −43 dB Input | −43 dB Input |
| Output bei 0 dB Input | −17,9395 dB | −28,9443 dB | −28,9196 dB |
| Reduktion relativ zum Kleinsignalpfad bei 0 dB Input | 17,9264 dB | 41,7310 dB | 41,7196 dB |

### Bewertung

- Der Standardversuch trifft die nominale 4:1-Steigung sehr gut.
- All Buttons liegt bei diesem hohen Pegel nahe 20:1, passend zum Modell
  `12+8×history`, dessen History hier hoch geladen wird.
- Die **+12,8 dB Kleinsignalverstärkung** in Versuch 3 ist genau
  `Input 24 + Output (−11,2)`. Das ist normales Gain-Staging, keine versteckte
  Auto-Makeup-Funktion.
- In Versuch 2 beträgt die zusätzliche Kleinsignalabweichung durch Colour nur
  etwa −0,0134 dB. Die Input-/Output-Absenkung passt daher zum Code.
- Das sichtbare Knie ist weich. Die gemessenen 1-dB-Punkte sind externe
  Inputpegel, nicht gleichbedeutend mit den internen Threshold-Konstanten.
- In Versuch 2/3 ist der Kompressionseinsatz wegen Input +24 weit nach unten
  verschoben; das ist beabsichtigt.
- Alle statischen Kennlinien sind monoton. Keine Expansion oder invertierte
  Ratio ist in den vorliegenden Kurven sichtbar.

Die hier aus Gain-Differenzen berechnete Reduktion ist eine **stationäre
Pegeldifferenz** gegen den extrapolierten Kleinsignalpfad. Die JSFX-GR-Anzeige
meldet den expliziten dynamischen FET-Gain; Färbung, RMS/Peak und Anzeigen-
Ballistik können zu kleinen Unterschieden führen.

Die früher dokumentierten hohen-Ratio-Abweichungen im 1-kHz-Test von
`STATUS.md` sind damit nicht widerlegt: dort waren Ratio-Modi, Frequenz,
Attack/Release und Input-Pegelpunkte anders. All bei 2516,7 Hz ist eine
andere Betriebsbedingung.

## 4. Harmonische und Colour

Der höchste FFT-Bin liegt bei **2517,00024 Hz**, konsistent mit dem angezeigten
2516,7-Hz-Sinus und dem FFT-Raster. Harmonische wurden aus den lokalen
Peak-Bins um n×Grundfrequenz bestimmt und gegen den Ausgangsgrundton
normalisiert. Das ist eine **Näherung**, kein Nachbau des PluginDoctor-
THD/THD+N-Algorithmus einschließlich Fenster-/Bandintegration.

| Kennwert | Versuch 1 | Versuch 2 | Versuch 3 |
|---|---:|---:|---:|
| Grundton, Peak-Bin | −18,0057 dBFS | −28,9587 dBFS | −28,9405 dBFS |
| H2 relativ zum Grundton | −59,47 dBc | −67,19 dBc | unter etwa −125 dBc, nahe numerischem Hintergrund |
| H3 relativ zum Grundton | −63,76 dBc | −75,67 dBc | −68,14 dBc |
| H5 relativ zum Grundton | −80,48 dBc | −75,33 dBc | −75,08 dBc |
| Peak-Bin-THD H2…H8 | etwa **0,125 %** | etwa **0,0504 %** | etwa **0,0439 %** |

Die Screenshots melden für Versuch 2 THD ungefähr −65,9 dB und für Versuch 3
−67,2 dB. Das stimmt gut mit den aus den Textdaten geschätzten Werten überein.
Für Versuch 1 existiert kein eigener THD-Screenshot; 0,125 % ist die Export-
Näherung.

### Bewertung

- `Colour=0` unterdrückt gerade Harmonische stark, wie vom symmetrischen
  sauberen Audiopfad erwartet.
- Die ungeraden Harmonischen bleiben, weil der **Gain-Regelkreis selbst
  signalabhängig und damit nichtlinear** ist. Colour Off ≠ Compression Off.
- Bei Colour 100 erscheint H2; H3 kann dabei gleichzeitig schwächer werden.
  Das beweist, dass Colour nicht lediglich pauschal mehr THD addiert:
  Audiopfad-/Regelanteile können sich in Betrag und Phase überlagern.
- All Buttons ist in dieser 2,5-kHz-/Attack-1-Messung **kein stark verzerrender
  Clipper**. Wenn musikalisch mehr „Slam“ gewünscht ist, zuerst 50/100 Hz,
  Attack/Release 7/7 und echte Drum-Bursts testen. Nicht allein wegen des
  niedrigen 2,5-kHz-THD-Werts den Colour-Regler künstlich verstärken.
- Der FFT-Teppich weit unter −120 dBFS ist kein gemessener analoger Noise Floor.
  Fensterung, Rundung und zeitabhängige Verarbeitung sind zu berücksichtigen.

## 5. Hochtonabfall: entscheidend ist die Messmethode

Relativ zum jeweiligen 1-kHz-Punkt sieht die Delta-FFT so aus:

| Frequenz | Versuch 1 | Versuch 2 | Versuch 3 |
|---|---:|---:|---:|
| 20 Hz | −0,75 dB | −0,54 dB | +0,02 dB |
| 5 kHz | −0,36 dB | −0,11 dB | −0,39 dB |
| 10 kHz | −1,71 dB | −1,53 dB | −1,79 dB |
| 15 kHz | −4,98 dB | −4,79 dB | −4,90 dB |
| 18 kHz | −6,65 dB | −3,17 dB | −8,34 dB |
| 20 kHz | −4,09 dB | −2,43 dB | −12,16 dB |

Auf den ersten Blick könnte Versuch 3 einen unerwünschten festen Lowpass trotz
Colour=0 vermuten lassen. Das wäre ohne zusätzliche Prüfung eine falsche
Schlussfolgerung.

### Was PluginDoctor hier einspeist

Laut [PluginDoctor-Handbuch](https://ddmf.eu/pdfmanuals/PlugindoctorManual.pdf),
S. 3–5, ist „Delta“ ein einzelner hoher Samplewert im Messbuffer. Der Regler
0 dB entspricht Samplewert 1. In Versuch 1–3 steht **+6,45 dB**, also
ungefähr **2,10136** als Spitzenwert; dies ist kein Kleinsignal.

Durch die Interpolation wird daraus eine mehrsamplelange Antwort auf hoher
Rate. **Die eingeschaltete Kompression ändert den Gain während dieser Antwort.**
Eine Multiplikation mit zeitvariablem Gain verändert deren Fouriertransformierte.
Das Spektrum ist dann eine pegel-/zeitabhängige Systemreaktion, kein nur vom
linearen Filter abhängiger Frequenzgang. Wiederholte Impulse laden auch die
GR-Historie; ein isolierter erster Impuls liefert andere Ergebnisse.

Auch die absoluten Ordinaten dürfen nicht ungeprüft als Transfergain gelesen
werden: der kräftigere Delta-Pegel und der veränderte Gain beeinflussen die
Ausgangs-FFT. Im Bericht werden daher die exportierten Werte und der auf 1 kHz
bezogene Verlauf getrennt angegeben.

### Gegenprüfung mit dem aktuellen Code

Neue Diagnosewerkzeuge, ohne Änderung des DSP:

```bash
make measurement-probe
python3 tools/analyze_plugindoctor.py \
  --probe build/native/measurement_probe \
  --output docs/PLUGIN_DOCTOR_EVALUATION.json
```

Die native Probe verwendet:

- 44,1 kHz, exakt die Screenshot-Reglerwerte.
- Deltaamplitude `10^(6,45/20)`.
- Wiederholung alle 16384 Samples, zehn Perioden, Auswertung der letzten.
- 1020 Samples Platzierungsoffset zum Vergleich mit der Exportzeitachse.
  Dieser Offset ist **keine neu gemessene Pluginlatenz**.

| Vergleich | Versuch 1 | Versuch 2 | Versuch 3 |
|---|---:|---:|---:|
| Maximale FFT-Abweichung 20 Hz…20 kHz | **0,00340 dB** | **0,00303 dB** | **0,00743 dB** |
| Unskalierter RMS-Samplefehler | 2,14×10⁻⁶ FS | 1,91×10⁻⁶ FS | 3,03×10⁻⁶ FS |
| Angepasster konstanter Skalierungsfaktor | 1,000054 | 1,000065 | 1,000177 |

Der Skalierungsfit dient nur zur Form-/Rundungsprüfung. Die FFT-Abweichungen
sind **ohne diesen Fit** angegeben. Die Daten lassen sich sehr gut durch die
aktuelle Implementierung erklären; kein neues Frequenzgangmodell war nötig.

Separat wurde derselbe Resampler bei `Compression=Off`, `Colour=0`, 0 dB
Input/Output und kleinem Impuls geprüft. Maximale Gain-Abweichung 20 Hz…20 kHz
bei 44,1 kHz: etwa **2×10⁻⁹ dB** in double. Der aktuelle Identitätspfad ist
damit betragsmäßig praktisch eben. Seine Phase bleibt IIR-typisch nichtlinear.

**Folgerung:** Die vorliegenden Delta-Kurven liefern keinen Beleg für einen
kaputten Oversampling-Passband oder einen fest eingebauten Hochton-Lowpass bei
Colour=0. Um den tatsächlichen Audiopfad-Frequenzgang zu messen, zuerst
Compression Off und niedrigen Pegel benutzen. Für den arbeitenden Kompressor
einen langsamen, ausreichend eingeschwungenen **Sinus-Fundamental-Sweep** mit
bekanntem Inputpegel verwenden.

## 6. IR und Latenz

Die exportierten Spitzen liegen ungefähr bei 23,22/23,24 ms. Das ist die absolute
Position im dargestellten Messbuffer, kein Beleg für 23 ms Pluginlatenz.
Erregungsposition, Host-/PDC-Offset und Filterphase sind darin nicht getrennt.

Die bisherigen **vier Samples nominale PDC** lassen sich mit diesen Dateien
weder vollständig bestätigen noch widerlegen. Für die Prüfung werden
Referenz-Inputimpuls, Bypass-/Identitätssignal und explizite Host-PDC-Einstellung
benötigt. Gruppenlaufzeit ist weiterhin frequenzabhängig.

## 7. Hammerstein und Kanalvergleich

Die sechs Hammerstein-Ordnungskurven zeigen deutliche G(3)/G(5)-Anteile im
Tiefton und geringe gerade Anteile bei Colour 0. Das passt qualitativ zu
gerader/ungerader Audiopfad-/Regelnichtlinearität.

Die Messmethode approximiert ein System mit Potenzzweigen plus linearen Filtern.
Ein Kompressor enthält dagegen Pegel-/Zeit-/Historienabhängigkeit und
Feedback. Deshalb:

- G(n) nicht direkt als n-te Sinus-Harmonische mit gleichem dBc-Wert lesen.
- G(n) nicht als fertige Green-Stripe-/NAM-Kalibrierdatenbank übernehmen.
- Unterschiedliche Sweep-/Einschwingbedingungen verändern das Ergebnis.
- Für einen späteren Färbungsfit Compression Off messen und mit reinem
  Audiopfad arbeiten.

Linear-, Dynamics- und IR-Kurven beider exportierter Kanäle sind in allen
Versuchen **identisch**. Oberhalb −120 dBFS sind auch die Harmonicdaten identisch;
kleine Unterschiede existieren nur im sehr tiefen numerischen Hintergrund.
Die Mono-JSFX gibt absichtlich den linken verarbeiteten Input auf beide Outputs.
Diese Doppelkurven sind deshalb **kein Test der Stereo-Link-Version**.

## 8. Anzeige- und Hostbeobachtungen

- Die JSFX lässt sich extern in ReaJS laden und die Green-Stripe-Grafik ist sichtbar.
- In Versuch 3 ist ein Ausgangs-Clipindikator bei der kräftigen Delta-Anregung
  erwartbar: Clean Colour=0 hebt die analoge Ausgangssättigung auf; gleichzeitig
  beträgt der Kleinsignal-Gain +12,8 dB. Der rote Punkt ist kein Beweis für
  numerische Instabilität.
- Die GR-Anzeige zeigt starke Wet-Regelung; sie ist nicht einfach Input minus
  Output, weil Input-/Output-Gain und Färbung zusätzlich im Signalweg liegen.
- Anzeigen am Ende einer schnell offline abgearbeiteten Ramp können Peak-/
  RMS-Nachläufe und sehr tiefe Werte zeigen. Dafür zunächst PluginDoctor-
  Speed **Realtime** wählen und konstanten Sinus messen.
- Im Screenshot fehlt die Autorität eines REAPER-7-Tests: Host-GR,
  Projekt-Recall, Automation und Fonts/HIDPI dort separat prüfen. Die ältere
  ReaPlugs/ReaJS-Veröffentlichung ist nicht derselbe Hoststand wie REAPER 7.

## 9. Priorisierte Folgemessungen

### P0 — Audiopfad und Messpegel isolieren

1. **Identität:** Input/Output 0, Colour 0, Compression Off, Mix 100.
   Delta zunächst −30 oder −60 dB. Erwartet: betragsmäßig flach bis 20 kHz
   (bei 44,1/48 kHz), IIR-Phase erlaubt.
2. **Colour only:** Colour 100, Compression Off, gleicher kleiner Pegel.
   Erwartet: milde LF-/HF-Färbung, keine dynamische GR.
3. **Working compressor:** Compression On, jeweils −30/−18/−6 dB,
   Fundamental-Sweep mit ausreichend Hold/Settling. Delta-Pegel separat
   protokollieren; keine Gleichsetzung mit LTI-Frequenzgang.

### P1 — Zeitverhalten und musikalischer Slam

4. PluginDoctor **Attack/Release** statt Ramp: Inputstufe unter/über/unter
   Threshold, mehrere Burstlängen. Alle Reglerwerte und Messdefinition festhalten.
5. 50/100 Hz und 1/2,5/5 kHz, 4/8/12/20/All, Attack/Release 1/1, 1/7, 7/7.
   THD/IMD plus zeitliche GR vergleichen.
6. All Buttons mit realen Raum-/Drumsignalen, Output pegelgleichen; eventuelle
   Transientenverformung erst musikalisch beurteilen, dann Modell ändern.

### P2 — Plattform, Stereo und Provenienz

7. Gleicher Test direkt in REAPER 7 oder gepflegtem ysfx-Host; ReaJS-Version
   und Plugin-/Includehashes protokollieren.
8. Stereo-Version: ungleiche Kanäle und Gegenphase bei Link On/Off.
9. Performance, 128/256/1024 Frames, reale Host-PDC und parallele Phasigkeit.
10. Vergleichsgerät/-plugin erst mit gleichem Pegel, Rate, Ratio und Recall-
    Bedingungen als Referenz gegenüberstellen.

## 10. Konsequenz für diese Session

Die Ergebnisse sind numerisch dokumentiert und mit dem vorhandenen Code
abgeglichen. **Keine DSP-/Presetänderung** wurde allein aus diesen drei
Messreihen vorgenommen. Insbesondere ist eine sofortige Hochtonanhebung als
„Oversampling-Reparatur“ durch die Daten nicht gerechtfertigt.

Die Daten schließen eine konkrete Lücke im ursprünglichen Prüfstand:
externes JSFX-Laden, sichtbare UI, stationäre 4:1-/All-Buttons-Kurven und
Harmonic-/Delta-Reaktionen sind jetzt belegt. Vollständige REAPER-/Dwarf-/
Zeitkalibrierungsabnahme bleibt getrennt offen.

## 11. Ergänzung — Versuch 4 bis 7

### 11.1 Umfang und Messbedingungen

28 weitere Dateien wurden hinzugefügt: 14 Textdateien und 14 Screenshots.
Zusammen mit Versuch 1–3 sind es jetzt **55 Dateien**. Alle 29 Textdateien sind
ausgewertet und alle Bilder gesichtet; Dateihashes stehen im JSON-Bericht.
Fehlbenennung `hamemrstein5.txt` bleibt im Original erhalten und wird vom Tool
explizit berücksichtigt.

Die neuen Screenshots zeigen weiterhin ReaJS und PluginDoctor 2.3.2. Sie
entsprechen denselben FFT-/Frequenzrastern von 44,1 kHz wie die ersten Versuche.
Delta steht jetzt auf **0,00 dB** (= Sampleamplitude 1), nicht +6,45 dB.
Das ist immer noch keine Kleinsignalanregung für die Colour-Stufen.

**Versuch 7 ist keine Zeitkurve:** x-Achse Hz, Tab LinearAnalysis, je zwei
Magnitude-Graphen für Mono-Output L/R. Die zwei Ratio-Stellungen dürfen deshalb
nicht zu gemessenen Attack-/Release-Zeiten umgedeutet werden.

### 11.2 Versuch 4 — Colour only, 0 dB Input/Output

Einstellungen: Compression Off, Colour 100, All Buttons ausgewählt,
Attack/Release 1/1, Input/Output 0, Mix 100.

- GR-Anzeige bleibt bei null: der explizite Controllergain wird deaktiviert.
- Kleinsignal-Gain bei 2516,7 Hz etwa **−0,0131 dB**.
- Output bei 0 dB Sinusinput **−1,3205 dB**; gegenüber dem Kleinsignalpfad
  etwa **1,3074 dB** pegelabhängige Verringerung.
- Bei −0,32 dB Sinusinput: Grundton etwa −1,1622 dBFS, H2 **−35,45 dBc**,
  H3 **−30,21 dBc**, Peak-Bin-THD etwa **3,525 %** (−29,06 dB).

Das ist die Audiopfadsättigung bei ausgeschalteter dynamischer GR. Eine
abgeflachte Dynamics-Ramp ist hier nicht als eingestellte Kompressor-Ratio zu
bewerten. Dass Compression Off nicht transparent ist, entspricht dem
dokumentierten Colour-only-Modus.

Die Deltaantwort liegt um 1 kHz bei −0,760 dB, bei 20 Hz bei −1,723 dB.
Ein kleiner Hochtonanstieg relativ zum Mittelband (20 kHz etwa +0,288 dB)
und ein Peak um 20,7 kHz sind in dieser starken Impulsantwort sichtbar.
Auch ohne dynamische GR bleibt die Färbung nichtlinear; die hohe Delta-FFT
ist daher nicht ihr universeller linearer Frequenzgang.

Die All-Auswahl verändert im aktuellen Modell auch bei Compression Off
FET-Krümmung und Preamp-Bias. Das ist eine eigene Green-Stripe-Entscheidung;
Colour-only mit 4:1 und All ist nicht als identischer Audiopfad garantiert.

### 11.3 Versuch 5 — stärkerer Drive, Output kompensiert

Gleiche Einstellungen wie Versuch 4, aber Input **+15,6 dB** und Output
**−15,6 dB**. Der Kleinsignal-Gain bleibt praktisch gleich:

| Kennwert | Versuch 4 | Versuch 5 |
|---|---:|---:|
| Kleinsignal-Gain | −0,01310 dB | −0,01318 dB |
| Output bei 0 dB Input | −1,32054 dB | −7,64558 dB |
| Grundton bei −0,32 dB Sinusinput | −1,16218 dBFS | −6,21536 dBFS |
| H2 | −35,45 dBc | −32,73 dBc |
| H3 | −30,21 dBc | **−14,52 dBc** |
| H5 | −57,85 dBc | **−26,26 dBc** |
| Peak-Bin-THD H2…H8 | **3,525 %** | **19,627 %** |

Die intern höhere FET-/Preamp-Aussteuerung lässt sich durch Output-Absenkung
nicht rückgängig machen. Im hohen Signalbereich ist Versuch 5 ein deutlich
saturierender **Effekt**, keine bloß geringfügige Tonfärbung.

Die Deltaantwort steigt relativ zu 1 kHz bei 20 kHz um etwa **4,35 dB** und
erreicht bei etwa 20,874 kHz einen absoluten Exportpeak von +0,2145 dB.
Diese Form ist mit der bestehenden nichtlinearen Audiokette reproduzierbar.
Eine lineare Bass-/Hochtonkorrektur würde den eigentlichen Drive-Charakter
verändern und ist aus dieser Messung nicht automatisch gerechtfertigt.

Separat lokal mit einem Impuls von nur `10⁻⁶` geprüft:

- Colour-only bei 0 dB und +15,6/−15,6 hat praktisch denselben
  **normalisierten Kleinsignalverlauf**.
- Ungefähr −0,92 dB bei 20 Hz, −0,004 dB bei 1 kHz, −0,171 dB bei 10 kHz,
  −0,622 dB bei 20 kHz.
- Diese Werte stammen aus der **nativen Gegenprobe**, nicht aus einem zusätzlich
  extern gemessenen Kleinsignal-Sweep.

Damit ist der starke Hochtonverlauf in Versuch 5 nicht als Beweis für eine
feste +5-dB-Höhenanhebung des Audiopfads zu lesen.

### 11.4 Zusatzlinien und Alias-Kandidaten

Die bisherigen H2…H8-THD-Werte berücksichtigen keine zurückgefalteten
Harmonischen oberhalb Nyquist. In Versuch 5 existiert eine auffällige
zusätzliche Linie:

- Exportraster: etwa **21452,37 Hz**, **−78,54 dBFS**.
- Gegen Grundton −6,215 dBFS: ungefähr **−72,33 dBc**.
- Tatsächliches kohärentes FFT-Bin-Raster: Grundton
  `935 × 44100/16384 = 2516,693115 Hz`.
- H9 wäre etwa 22650,24 Hz und faltet im 44,1-kHz-Ausgang auf
  **21449,76 Hz** zurück. Diese Kandidatenposition stimmt mit dem Exportbin
  und der nativen Gegenprobe überein (Hz-Achse des Exports ist leicht gerundet).

Versuch 4 hat den entsprechenden Peak nur um −136,8 dBFS, Versuch 6 um
−110,5 dBFS. Die gefaltete H9 ist damit deutlich Drive-abhängig.

Das ist ein konkreter Anlass, **Alias-Konvergenz bei starkem Drive zu prüfen**.
Der Peak liegt in dieser Messung oberhalb 20 kHz; bei anderen Testfrequenzen
können gefaltete Produkte tiefer liegen. Ohne höher aufgelöste Referenz ist
nicht jede Zusatzlinie abschließend von Pegelmodulation zu trennen.
Eine pauschale Aussage „4× ist in jedem Betriebszustand aliasfrei“ ist nicht
durch die Daten gedeckt.

### 11.5 Versuch 6 — 20:1, Colour 0 und geringe interne Aussteuerung

Einstellungen: Input **−15,6 dB**, Output **+15,6 dB**, Attack/Release 7/7,
20:1, Colour 0, Compression On.

- Kleinsignal-Gain **0,0000 dB**.
- Dynamics-Ramp bleibt von −100 bis **−4 dB** Input bei Unity.
- Erst −3 dB Input: etwa 0,181 dB Verringerung; bei 0 dB etwa **2,6084 dB**.
- Der Rampbereich erreicht damit vor allem das **Knie**. Eine Regression über
  −12…0 dB liefert keine sinnvolle Aussage zur nominalen 20:1-Steigung, weil
  fast alle Punkte unkomprimiert sind.
- Harmonic-Sinus: Outputgrundton −2,6515 dBFS, H3 −73,71 dBc,
  H5 −78,93 dBc, Peak-Bin-THD etwa **0,0248 %** (−72,12 dB).

Die Deltaantwort ist im Audioband nahezu eben:

| Punkt | Absolut | Relativ zu 1 kHz |
|---|---:|---:|
| 1 kHz | −0,02087 dB | 0 dB |
| 10 kHz | −0,02951 dB | −0,00864 dB |
| 15 kHz | −0,04668 dB | −0,02581 dB |
| 20 kHz | −0,06688 dB | −0,04600 dB |

Über alle exportierten Bins zwischen 20 Hz und 20 kHz beträgt die
Maximum-minus-Minimum-Spanne **0,04978 dB**. Das bestätigt den sauberen
Betragsverlauf auch im externen Host. Die kleine Rest-GR der Deltaantwort ist
im aktuellen Modell reproduzierbar; es ist kein vollständig abgeschalteter
Kompressortest.

Zusätzliche Linien sind um etwa **2748,51 Hz** und **2285,49 Hz** sichtbar:
etwa −92,17 beziehungsweise −93,03 dBc. Die native Gegenprobe zeigt sie
ebenfalls. Auf dem kohärenten Raster stimmen sie mit Kandidaten für gefaltete
H69/H71 überein. Das allein beweist ihre konkrete Entstehung nicht; insbesondere
kann die sehr schnelle zyklische Reglerladung weitere Modulation erzeugen.
Für die Qualitätsprüfung niedrige direkte THD und zusätzliche Linien deshalb
**getrennt** ausweisen.

### 11.6 Versuch 7 — gleiche Regler, 4:1 versus All

Beide Kurven: Input −6 dB, Output +6 dB, Attack 7, Release 1, Colour 0,
Compression On, Mix 100. Delta 0 dB.

| Frequenz | 4:1 absolut | All absolut | 4:1 relativ 1 kHz | All relativ 1 kHz |
|---|---:|---:|---:|---:|
| 1 kHz | −9,7145 dB | −4,0009 dB | 0 dB | 0 dB |
| 5 kHz | −9,7665 dB | −4,0520 dB | −0,0520 dB | −0,0511 dB |
| 10 kHz | −9,9543 dB | −4,1996 dB | −0,2398 dB | −0,1987 dB |
| 15 kHz | −10,4246 dB | −4,4416 dB | −0,7101 dB | −0,4407 dB |
| 20 kHz | −10,7868 dB | −5,0952 dB | −1,0723 dB | −1,0942 dB |

All liefert bei gleicher **Impulsanregung** deutlich weniger Mittelband-
Abschwächung als 4:1. Das ist in diesem Code erklärbar durch den separaten
All-Detektor-Lag, den anderen Einsatzpunkt und die Historie. Höhere nominale
Ratio bedeutet bei solchen Transienten nicht automatisch stärkere GR.

Eine statische All-/4:1-Sinuskennlinie oder der Attack-Transientenverlauf lässt
sich aus diesen Frequenzdaten nicht rekonstruieren. Vor Änderung der
All-Dynamik deshalb zuerst den eigentlichen Zeitbereich aufnehmen.

### 11.7 Reproduzierbarer Abgleich aller neuen Fälle

`tools/measurement_probe.cpp` unterstützt die Screenshot-Szenarien 0–8:

```text
0 Identität, 1–6 Versuche 1–6, 7 Versuch 7/4:1, 8 Versuch 7/All
```

Mit optionalem `tone` und Frequenzargument erzeugt es zusätzlich den
eingeschwungenen, kohärenten Sinus. Das Analysewerkzeug prüft nun alle
Versuche, optionale/fehlende IRs, den ursprünglichen Dateinamenfehler bei
Hammerstein 5 und separate Linear-only-Kurven.

| Neue Messung | maximale Delta-FFT-Abweichung 20 Hz…20 kHz |
|---|---:|
| Versuch 4 | **0,000495 dB** |
| Versuch 5 | **0,002747 dB** |
| Versuch 6 | **0,000029 dB** |
| Versuch 7, 4:1 | **0,000841 dB** |
| Versuch 7, All | **0,000442 dB** |

Auch die Sinusgrundtöne und sinnvollen H2…H8-Partialwerte werden reproduziert:
größte Grundtonabweichung aller sechs Harmonic-Dateien etwa **0,00213 dB**,
größte Partialabweichung oberhalb −120 dBFS etwa **0,017 dB**. Die extrem
tiefen numerischen FFT-Bins werden dabei nicht als reale Harmonische verglichen.
Frequenz-/Fenster-/Pegeleinstellung des externen Hosts ist weiterhin nicht
vollständig dokumentiert; die Übereinstimmung belegt Verhaltenskonsistenz,
nicht Hardwaregleichheit.

## 12. Nächste Arbeit nach Versuch 4–7

1. **Zeitbereich:** Attack/Release-Tab mit unter/über/unter Threshold und
   Export der Zeitachse. Kurzer/langer Burst bei 4/20/All; Signalpegel und
   Reglerstellungen festhalten.
2. **Colour-Kleinsignal:** Compression Off bei −30/−60 dB Delta und
   eingeschwungenem Fundamental-Sweep; damit feste Färbung vom Drive-Effekt
   unterscheiden. Input/Output 0 sowie +15,6/−15,6 vergleichen.
3. **Aliasing:** starke Colour-only-Aussteuerung und schnelle GR bei mehreren
   Frequenzen/Raten; 4× gegen höhere Offline-Rate vergleichen. Nicht nur THD
   melden, sondern nicht harmonische/gefaltete Linien separat.
4. **20:1 oberhalb Knie:** Input erhöhen oder einen passenden Pegelbereich
   wählen, bis ausreichend vollständig komprimierte Punkte existieren.
5. **Hörprüfung:** Ist Colour 100 bei nominalem Aufnahmepegel musikalisch
   passend? 3,5–20 % THD wurden nahe 0 dBFS **Peak** gemessen, nicht bei
   üblichen −18/−21-dBFS-Bezugspegeln. Lautstärke immer pegelgleichen.

**Konsequenz:** Die neuen Daten werden dokumentiert; DSP und Presets wurden
nicht automatisch geändert. Es liegt weiterhin kein Hinweis auf eine kaputte
Resampling-Passband vor. Neu konkret belegt sind driveabhängige Sättigung,
nahezu flacher Clean-Pfad, All-spezifische Impulsreaktion und messbare zusätzliche
Spektralprodukte für die nächste Alias-/Zeitkalibrierung.
