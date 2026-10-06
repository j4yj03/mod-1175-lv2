# Green Stripe 76 — Externe Prüfungen und Presetbewertung

PluginDoctor-/ReaJS-Auswertungen, GR-Analysen und Einzelbewertung der Presetbank.

**Konsolidiert am 2026-10-06** aus den bisherigen Einzeldokumenten; Inhalt inhaltlich unverändert, Pfadangaben auf die neue Struktur angepasst.

## Inhalt

1. EXTERN.md — *(Quelle: EXTERN.md)*
2. EXTERN.md — *(Quelle: EXTERN.md)*
3. EXTERN.md — *(Quelle: EXTERN.md)*
4. EXTERN.md — *(Quelle: EXTERN.md)*
5. PRESET_REVIEW.md — *(Quelle: PRESET_REVIEW.md)*


---

<!-- ===== Teil 1: Quelle docs/EXTERN.md ===== -->

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
[`PERFORMANCE.md`](PERFORMANCE.md) dokumentiert. Kein Klangparameterfit aus
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
`PROJEKT.md` sind damit nicht widerlegt: dort waren Ratio-Modi, Frequenz,
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


---

<!-- ===== Teil 2: Quelle docs/PLUGIN_DOCTOR_GR_ANALYSIS.md ===== -->

# PluginDoctor GR-Analyse

## Evaluation
Siehe `EXTERN.md` und vertiefende Auswertung.

## GR vs Ratio (Messdaten)
Auswertung: `EXTERN.md`
- Peak-GR erreicht Maximum bei 8:1 (~18.4 dB), fällt bei 12:1/20:1 ab (modellbedingt)

## DSP-Vergleich
`EXTERN.md` – Abgleich mit `data/model.json` (Threshold/Knee-Verlauf erklärt Abnahme ab 8:1).

Detaillierte Tabellen und Rohdaten siehe jeweilige Dateien im Archiv oder Originale (werden zusammengefasst).


---

<!-- ===== Teil 3: Quelle docs/PLUGIN_DOCTOR_GR_EVAL.md ===== -->

# PluginDoctor GR vs Ratio – Auswertung

## Rahmenbedingungen
- Input Gain 0 dB, Output Gain 0 dB
- Attack 7, Release 7
- Comp On, Colour 100%, Mix 100%, Colour auf 0% (kein Unterschied)
- Messreihe unter `docs/sauce/gain - 0, atk - 7, rls - 7 - 100 - 100/*.txt`

## Ausgewertete GR-Werte (Input → Output, angenähert GR = Input - Output)
Tabelle zeigt geschätzte Gain Reduction in dB.

| Ratio | -20 dB In | -10 dB In | -6 dB In | -3 dB In | 0 dB In |
|---|---:|---:|---:|---:|---:|
| 2:1 | ~2.05 | ~7.02 | ~9.03 | ~10.55 | ~12.07 |
| 4:1 | ~3.34 | ~10.49 | ~13.49 | ~15.75 | ~18.00 |
| 8:1 | ~1.63 | ~9.66 | ~13.12 | ~15.74 | ~18.37 |
| 12:1 | ~0.49 | ~8.79 | ~12.39 | ~15.12 | ~17.87 |
| 20:1 | ~0.04 | ~7.71 | ~11.44 | ~14.26 | ~17.10 |
| All Buttons | ~0.67 | ~9.61 | ~13.41 | ~16.29 | ~19.18 |

## Beobachtung (Benutzer)
"Gainreduktion nimmt ab 8:1 aufwärts ab. [...]"

Aus Daten: 8:1 liefert bei 0 dB In ~18.37 dB, 12:1 ~17.87 dB, 20:1 ~17.10 dB – also **abnehmende Max-GR** bei höheren Ratios. Auch im mittleren Bereich (-10/-6 dB) fällt GR für 12:1/20:1 gegenüber 8:1 ab.

## Mögliche Ursachen (zu prüfen)
- Nichtlinearer Detektor/Knie (soft knee) beeinflusst effektive Ratio je Pegel
- Feedforward/Feedback-Topologie, Timing (Attack/Release) bei schnellen Pegelsprüngen
- Levelabhängiger Threshold/Makeup-Logik
- Messumgebung/PluginDoctor-Implementierung (z. B. Sweep vs Step) – Attack/Release 7 sind relativ moderat
- Internes Meter vs. externer Transfer (hier: In→Out über Loop)

## Nächste Schritte
- Gegen Referenz-1176-Verhalten (klassisch: höhere Ratio → höhere GR, typ. harte Knie) abgleichen
- DSP-Code prüfen: `src/dsp/GreenStripe.hpp`, Ratio-Handling, Detector (RMS/Peak?), Knee
- Gegebenenfalls mit anderen Attack/Release oder steilerer Anregung testen (Scarlett-Loop liefert präzisen Transfer)

## Anmerkung
Werte zeigen starken Anstieg ab ~-15 dB bis 0 dB; Peak-GR liegt um 8:1, nicht bei 20:1/All Buttons.


---

<!-- ===== Teil 4: Quelle docs/PLUGIN_DOCTOR_GR_DSP_COMPARISON.md ===== -->

# PluginDoctor GR vs DSP-Modell

## Modellparameter (data/model.json)
| Ratio | Mode | Ratio (linear) | Threshold (dBFS) | Knee (dB) |
|---|---:|---:|---:|---:|
| 2:1 | 0 | 2.0 | -24.0 | 6.0 |
| 4:1 | 1 | 4.0 | -24.0 | 6.0 |
| 8:1 | 2 | 8.0 | -21.0 | 4.0 |
| 12:1 | 3 | 12.0 | -19.5 | 3.0 |
| 20:1 | 4 | 20.0 | -18.0 | 2.0 |
| All Buttons | 5 | 16.0 | -22.0 | 1.5 |

## Messwerte PluginDoctor (GR = Input - Output, Transfer-In→Out)
Siehe Tabelle oben; Max-GR bei 0 dB In: 8:1 ~18.4 dB, 12:1 ~17.9 dB, 20:1 ~17.1 dB (abnehmend).

## Interpretation
- Knee wird kleiner (6→1.5), Threshold steigt (-24→-18) für höhere Ratio-Modi – das reduziert die effektive Kompression über weiten Pegelbereich (harder knee + höherer Threshold → späterer, schärferer aber begrenzter Übergriff).
- "All Buttons" (Mode 5) hat Ratio 16.0, sehr schmaler Knee 1.5, Threshold -22 – Verhalten zwischen 8:1 und 12:1, Peak-GR ~19.2 dB.
- Ab 8:1 steigt Threshold und sinkt Knee sukzessive – konsistent mit beobachteter Abnahme der Max-GR ab 8:1 (Messung). Das ist **modellseitig beabsichtigt** (nicht notwendigerweise klassisches FET-Hard-Knee aller Modi).

## Folge
PluginDoctors extern gemessener Transfer zeigt realistische Umsetzung der Modellparameter. Die Abnahme ab 8:1 erklärt sich aus Threshold/Knee-Verlauf, nicht aus einem DSP-Fehler. Für Hardware-Treue separate Vergleichsmessung (Scarlett-Loop) empfohlen, aber Kurvenverhalten ist konsistent mit Datenmodell.


---

<!-- ===== Teil 5: Quelle docs/PRESET_REVIEW.md ===== -->

# Prüfung aller Instrument-Presets — 0.4.1

Stand **2026-10-05**. Basis: `data/presets.json`, `data/parameters.json`,
`data/model.json`, aktuelle Transformatorbank und bestehende Quellenzuordnung.
**38 Presets** nach ausdrücklichem Korrektur-/Erweiterungsauftrag:
21 Kick Weight erhält Attack **2 statt 5**, 22 Snare Crack **3 statt 5**,
damit beide weniger Frontkante abregeln. Die vorherigen 2:1-Vorschläge sind
als **37 Piano Gentle 2:1** und **38 Stereo Bus Subtle 2:1** angehängt.
Nummern/Namen 01–36 bleiben erhalten; neue Varianten haben eigene URIs und
Selektorplätze. Bestehende Hostprojekte behalten gespeicherte Parameter;
erneuter Factory-Recall von 21/22 lädt die neuen Attackwerte.
Diese beabsichtigte Klangänderung ist als **0.4.1** versioniert.

## 1. Tatsächliche Prüfung und Befund

- **76 Zustände:** alle Mono-/Stereo-LV2-Factory-Presets und RPL-Zustände
  gegen sämtliche Werte aus `data/presets.json` abgeglichen, inklusive
  Enabled, Link, Oversampling, Transformer und Custom-Selektorzustand.
- **228 Renderfälle:** jedes Preset in Mono und Stereo bei Off/2x/4x,
  48 kHz, deterministisches Signal, pro Fall frischer Processor.
  Endliche Audio-/GR-Werte; beide Compression-Off-Presets exakt 0 dB GR.
- **12 Zusatzfälle:** Piano Gentle und Stereo Bus Subtle jeweils 4:1/2:1
  bei −18/−12/−6 dBFS Peak. Signalwerte unten.
- Ratioverteilung bei aktiver Compression: **2 × 2:1, 22 × 4:1, 9 × 8:1,
  3 × All Buttons**. Zwei weitere Presets sind Compression Off und speichern
  inaktiv 4:1. Kein Factory-Preset nutzt 12:1 oder 20:1.
- Die sechs Transformatorzuordnungen sind stimmig mit den eigenen Profilen:
  **11/12 → 60s, 13/19/24 → 80s, 20 → 00s**. Alle anderen `None`.
- **25 Toms Body und 30 Percussion Snap** rufen in Stereo Dual Mono auf;
  sinnvoll für unabhängige Kanäle, für zusammengehörige Stereopaare Link aktivieren.
- OS wird über alle Factory-Recall-Wege auf Off gesetzt. Die Referenzwerte
  in der Tabelle beziehen sich auf den Wet-Regler, nicht auf eine Änderung
  der Lautheit durch Mix oder Output.

Messdaten, Quellen-/Probehashes und Bedingungen: [`PRESET_AUDIT.json`](PRESET_AUDIT.json).
Die JSFX-Selector-/RPL-Paritätsprüfung ist zusätzlich in `MESSTECHNIK.md` beschrieben.
Dies ist eine **Parameter-/Signalprüfung**, kein Hörurteil über Instrumentaufnahmen,
keine Geräteabnahme und keine Bestätigung universeller Ziel-GR-Werte.

### Zusätzlich gefundener Paritätsfehler

Historischer Befund der vorangegangenen 0.4.0-Prüfung; 0.4.1 enthält diese
Korrektur weiterhin. Aktuell 430 allgemeine + **76** Preset-Signalvergleiche.

Der bisherige Test verglich die 72 Bankzustände nur als Sliderwerte mit dem
Selektor und renderte dabei Stille. Der neue Signalvergleich aller Bankwerte
deckte bei **29 Drum Parallel Crush, Mono, 48 kHz/OS Off** eine Abweichung bis
**0,000409722 FS** auf. Alle Factorywerte und zuvor verglichenen Zustände
waren korrekt; der erste abweichende Solverzweig entstand bei Sample 702.

Ursache war die EEL2-Auswertung von `1+alpha-alpha*deriv`: Bei identischen
Operanden unterschied sich der Newton-Vorschlag um wenige ULP. Die strikte
Intervallprüfung wählte daraufhin Newton statt Bisektion, bei nur acht
Iterationen sichtbar im Ausgang. Der Nenner wird nun in C++ und EEL2 mit
expliziten Zwischenschritten ausgewertet. Toleranzen, Iterationszahl und
Presetparameter sind unverändert. **430 allgemeine plus 72 Preset-Signal-
vergleiche sind jetzt bitgleich (max. 0 FS)**; `make test` ebenfalls PASS.
Die JSFX kann in diesem Randfall dadurch anders als die frühere JSFX rendern;
das ist eine Paritätskorrektur, keine Preset-Neuabstimmung.
Der C++-Vorher-/Nachhervergleich gegen `c3153bf` besteht in **144 Fällen
bitgleich für Audio/GR/Latenz**; zusätzlich bestehen CMake/CTest 3/3.

### Messsignal für alle Presets

1,2 Sekunden: links 53/997/6011 Hz mit Gewichten 0,6/0,3/0,1;
rechts bei Stereo 79/313 Hz mit 0,4/0,2. Gemeinsame Amplitudenskalierung
−12 dBFS als **Spitzenobergrenze**, nicht normalisierter tatsächlicher Peak.
Hüllkurve 0,125 bis 0,15 s, 1 bis 0,65 s, 0,125 bis 0,8 s, danach Stille.
Messfenster für Mittelwerte 0,4–0,6 s; Spitzen-GR über die ganzen 1,2 s.

Der Input muss zur Quelle passen: Bereits **01 Neutral Start** erreicht in
dieser Probe ca. **8,46 dB** Spitzen-GR statt seiner Zielspanne 2–5 dB;
**31 Piano Gentle** ca. **6,04 dB**, **35 Stereo Bus Subtle** ca. **4,11 dB**.
Das ist kein falscher Presetindex, sondern die Folge von Pegel und
tiefer Detektorschwelle. Erst Input auf die Ziel-GR einstellen, dann Output
pegelgleichen und zuletzt Mix dosieren. Eine kleine Mixzahl reduziert nicht
die interne GR oder die Transformatoraussteuerung.

## 2. Einzelbewertung aller 38 Presets

„Stimmig“ bedeutet konsistente Absicht/Parameter, mit erforderlichem Input-
und Hörabgleich. Alle genannten GR-Ziele beziehen sich auf den Wet-Pfad.

| Nr. / Preset | Bewertung und Prüfpunkt |
|---|---|
| 01 Neutral Start | 4:1 als allgemeiner Einstieg stimmig. „Neutral“ ist kein transparenter Bypass: Colour 100 %, Compression On; Notiz präzisiert. |
| 02 Dr Pepper Inspired | 4:1, relativ langsamer Attack und flotter Release passen zur Idee; Input +3 ist eigene digitale Zuordnung, keine Uhrzeitkalibrierung. |
| 03 Vocal Natural | 4:1, Attack 3, Release 5 und Colour 75 plausibel; Atem/Endsilben und Input auf 3–5 dB abstimmen. |
| 04 Vocal Peak Catch | 8:1 und Attack 5,5 sinnvoll für Spitzen; kein Lookahead/Brickwall, nachfolgende langsamere Stufe möglich. |
| 05 Vocal Rock Forward | 8:1, Input +7, schnelle Zeiten und Colour 100 konsistent mit dichterem Effekt. |
| 06 Vocal Grit Parallel | All, hohe Anregung, 30 % Mix konsistent; 10–18 dB Ziel-GR gilt vor Mix. |
| 07 Vocal Squashed | 4:1 und 7/7 bleiben passend; Quellbeispiel ist Anregung, kein Nachweis gleicher Verformung im eigenen Modell. |
| 08 Vocal Transformer | Compression Off, Colour 100, Transformer None sind beabsichtigt. Quellen-Trickname wird ausdrücklich vom neuen Modellselektor abgegrenzt; Output-Abgleich nötig. |
| 09 Guitar Clean Sustain | 4:1, 80 % Mix, Colour 90 passen zur Sustain-Idee; „Clean“ bezeichnet die Quelle, nicht verfärbungsfreie Verarbeitung. |
| 10 Guitar Rhythm Tight | Geringere Anregung und 80 % Mix plausibel; bei bereits verzerrtem Material nur wenig GR zulassen. |
| 11 Guitar Colour Only | Compression Off mit 60s/Colour 100 stimmig. Input +6/Output −6 gleicht nicht automatisch sämtliche Sättigungsverluste aus. |
| 12 Vintage Blue Grit | 8:1, 60s und 70 % Mix passen zum warmen Grit-Ziel, ohne Blue-Stripe-Revisionsbehauptung. |
| 13 Guitar Cruncher | 4:1, +15 dB Input, 7/7, 80s und 65 % Mix ausdrücklich aggressive eigene Interpretation. 80s kann vor dem Regler kräftig sättigen. |
| 14 Acoustic Strum | 4:1, relativ langsamer Attack 2, 80 % Mix/Link stimmig; Plektrum und Stereoabbildung hören. |
| 15 Acoustic Finger | Mehr Input und Wet-Anteil als Strum plausibel für Details; Raum-/Spielgeräusche mitprüfen. |
| 16 Bass Finger Level | 4:1 und 4/4 als Leveler plausibel; Tieftöne können trotz mittlerer Skalenstellung schnell geregelt werden. |
| 17 Bass Pick Punch | 8:1/4/4 und 85 % Mix stimmig; Attack 4 entspricht ca. 126 µs. Gemeinsame Resamplingphase ist keine vollständige Wet/Dry-Phasengleichheit. |
| 18 Bass Fast Grit | 8:1/7/7, +8 Input, 70 % Mix passen bewusst zu schneller rauer Regelung. |
| 19 Bass Mojo Bite | 8:1/7/7 plus 80s ergänzt den Grit-Pfad; moderate Profilbezeichnung bedeutet bei +9 Input nicht automatisch wenig Klirr. |
| 20 Huge Sub Weight | 8:1/4/4 plus 00s plausibel für relativ mehr Headroom; keine Bassanhebung. Bei +8 Input kann auch 00s kräftig angeregt werden. |
| 21 Kick Weight | Korrigiert auf Attack 2, ca. 433 µs statt 68 µs. Für das Weight-/Klick-Ziel mehr Frontkante; im Testsignal Spitzen-GR 11,19 statt 11,71 dB. |
| 22 Snare Crack | Korrigiert auf Attack 3, ca. 234 µs statt 68 µs. Weiterhin schneller als Preset 23; im Testsignal Spitzen-GR 11,65 statt 11,94 dB. |
| 23 Snare Slow Attack | Attack 2 (ca. 433 µs) relativ langsam und zur Absicht passend. Unbelegte pauschale Verzerrungsbegründung gegen Attack 1 entfernt; externer HP bleibt optionaler Quellentipp. |
| 24 Snare Saturated Parallel | 80s, Colour 100, 30 % Mix konsistent. 10–18 dB ist eigene aggressive Parallel-Abstimmung, nicht GR-Vorgabe von MTM-SNARE. |
| 25 Toms Body | 4:1/4/6 und Dual Mono für getrennte Toms stimmig; Stereosumme gegebenenfalls linken. |
| 26 Overheads Gentle | 4:1/1/4,5, 75 % Mix und Link plausibel; bei −12-dBFS-Probe bereits ca. 6,62 dB GR, deshalb Input senken. |
| 27 Room All Buttons | All, +12 Input, 3/6 und voller Wet-Pfad konsequenter Raumeffekt; Überschwinger beabsichtigt möglich. |
| 28 Drum Room Smasher | 4:1/7/7 und 75 % Mix passend; Ratio bleibt ausdrücklich eigene Wahl zur Quelle. |
| 29 Drum Parallel Crush | All, +14 Input, Release 7 und 25 % Mix stimmige starke Parallelstufe. |
| 30 Percussion Snap | Langsamerer Attack 1,3, schneller Release und 75 % Mix plausibel; Dual Mono nur für unabhängige Kanäle. |
| 31 Piano Gentle | 4:1 mit 60 % Mix/Colour 50 bleibt erhalten; zusätzliche 2:1-Variante unter 37. |
| 32 Rhodes Body | 4:1/2,5/5 und Colour 90 schlüssig für Körper/Sustain; Chorus-/Stereoeffekte mithören. |
| 33 Synth Bass Control | 8:1/3,5/4, geringere Colour und hoher Wet-Anteil schlüssig; tiefe Dauertöne/Release prüfen. |
| 34 Synth Lead Sustain | 4:1/3/5,5 und 85 % Mix passen zu Sustain; Delay/Reverb-Routing beeinflusst Pumpen. |
| 35 Stereo Bus Subtle | Niedrige Anregung, 40 % Mix/Colour, Link und None bleiben erhalten; zusätzliche 2:1-Variante unter 38. |
| 36 Mix Bus Light Glue | 4:1 bleibt wegen des ausdrücklichen Quellenbezugs. 1–2 dB Wet-GR wird über Input eingestellt, nicht über Mix; Notiz korrigiert. |
| 37 Piano Gentle 2:1 | Neu: bis auf Ratio identisch mit 31; Ziel 1–2 dB Wet-GR. Bei derselben Probe ca. 3,96 statt 6,04 dB Spitzen-GR, Input weiterhin abstimmen. |
| 38 Stereo Bus Subtle 2:1 | Neu: bis auf Ratio identisch mit 35; Ziel 0–2 dB Wet-GR. Bei derselben Probe ca. 2,62 statt 4,11 dB Spitzen-GR. |

## 3. Zwei umgesetzte 2:1-Erweiterungen

### 37 Piano Gentle 2:1 — Variante von 31

- Factory-Variante mit **Ratio 2:1**, übrige Werte wie 31:
  Input −3 dB, Output +1 dB, Attack 1, Release 3,5, Mix 60 %, Colour 50 %,
  Link On, Transformer None, OS Off.
- Hörziel: weniger Verdichtung langer Anschläge, mehr Anschlagsdynamik.
  Input danach auf etwa **1–2 dB Wet-GR** einstellen, Output neu pegelgleichen.
- Nominal Attack **800 µs**, Release **303 ms**. Auch die langsamste
  Attack bleibt FET-schnell; 2:1 macht aus dem Modell keinen langsamen Leveler.

### 38 Stereo Bus Subtle 2:1 — Variante von 35

- Factory-Variante mit **Ratio 2:1**: Input −6 dB, Output +1 dB,
  Attack 1,5, Release 3, Mix 40 %, Colour 40 %, Link On, None, OS Off.
- Hörziel: kleine Verdichtung bei höherer interner Durchlässigkeit;
  Ziel **0–2 dB Wet-GR**, anschließend pegelgleicher Bypass-/Ratiovergleich.
- Nominal Attack **588 µs**, Release **393 ms**. Bei 40 % Mix ist der
  hörbare Unterschied kleiner als der Unterschied der internen GR.

### Gemessener isolierter Ratiovergleich

1-kHz-Sinus, Stereo Link, R=−L, 48 kHz/OS Off, Original-Presetwerte außer Ratio,
Mittel der FET-GR von 0,4–0,6 s. Inputpegel bezeichnet den Hosteingang **vor**
dem Preset-Input-Gain. Kein Nachregeln von Input/Output in dieser Messung.

| Preset | Eingang Peak | 4:1 GR | 2:1 GR |
|---|---:|---:|---:|
| 31 Piano Gentle | −18 dBFS | 2,6181 dB | 1,5566 dB |
| 31 Piano Gentle | −12 dBFS | 6,6720 dB | 4,4165 dB |
| 31 Piano Gentle | −6 dBFS | 11,1249 dB | 7,3967 dB |
| 35 Stereo Bus Subtle | −18 dBFS | 0,9560 dB | 0,4930 dB |
| 35 Stereo Bus Subtle | −12 dBFS | 4,5981 dB | 2,9496 dB |
| 35 Stereo Bus Subtle | −6 dBFS | 8,9146 dB | 5,9342 dB |

2:1 regelt in diesen Fällen weniger, aber weder allgemein halb so stark noch
allgemein ein Drittel so stark. Die frühere Drittel-Aussage verwechselte
festen Feedback-Tap-Pegel mit festem Eingang. Herleitung in `DSP.md`.
Quelle für die beiden Varianten ist **eigene Modell-/Signalbewertung**,
kein historischer 1176-Tipp. 31/35 bleiben bei 4:1, 37/38 ergänzen die Bank
am Ende. Die ersten 36 Plätze bleiben dadurch abrufkompatibel; nur 21/22
haben die oben begründete Attackkorrektur. Eigene Feinabstimmungen separat speichern.

## 4. Wiederholung und Dokumentationsstand

```bash
make build/native/preset_probe
python3 tools/audit_presets.py --probe build/native/preset_probe \
  --output docs/PRESET_AUDIT.json
make check-generated
```

Zusätzlich die reale ysfx-Parität mit RPL-/Selector-Lader nach `MESSTECHNIK.md`
ausführen. `PRESETS.md` wird weiterhin aus `data/presets.json` generiert.
Die projektweite Markdown-Konsistenzprüfung berücksichtigt Preset-, Ratio-,
GR- und GUI-Aussagen; aktuelle Anleitungen, Quellenzuordnung und Übergabe sind
abgeglichen. Historische Mess-/Fitberichte und ihre Hashmanifeste behalten
ihre damaligen Bedingungen und Fallzahlen. Der aktuelle Bericht ersetzt
keine dort noch offene Geräte-, NAM- oder Hörprüfung.
