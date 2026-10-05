# Reale Audioübertrager: Datenblätter und Kennlinien

Ausgewertet **2026-10-05** für Green Stripe 76. Alle sechs Seiten der drei
lokalen Datenblätter wurden als Text und als gerenderte Seiten gelesen.
Die Diagramme liegen in den PDFs als Rasterbilder vor; sie wurden zusätzlich
in nativer Auflösung vergrößert geprüft.

## 1. Ergebnis

**Die Hammond-Kennlinien sind deutlich passendere Zielkurven für einen
1:1-Line-Übertrager als der Röhren-Ausgangsübertrager aus dem de-Paiva-Paper.**
Das Paper liefert weiterhin eine mögliche Modellstruktur; diese Datenblätter
liefern Randbedingungen für deren Abstimmung.

- **Hammond 140TEX:** echtes 1:1, Nickel-Kern, 1-kΩ-Anwendung, im Audioband
  weitgehend eben; sichtbare Großsignalprobleme vor allem im tiefsten Bass.
- **Hammond 560Q:** echtes 1:1 bei gleichartiger Verschaltung beider Seiten;
  Frequenzgang, Phase und THD+N für Serien- und Parallelschaltung. Die
  vollständigste der drei Kennliniensammlungen, mit einigen offenen
  Zahlen-/Bezugsfragen.
- **Lundahl LL1930:** **in den spezifizierten Schaltungen kein 1:1**, sondern
  5,8:1 oder 11,6:1. Keine grafischen Kennlinien, nur tabellierte
  Frequenzgang-/Klirrgrenzen für eine Röhren-Parafeed-Line-Ausgangsanwendung.

Die wichtigste klangliche Folgerung: **Tiefbass-Nichtlinearität,
frequenzabhängige Phase und Beschaltung sind die belegten Effekte.** Ein
starker breitbandiger Waveshaper wird durch diese Kurven nicht begründet.

Das ist eine **Datenblattauswertung**, keine eigene Hardwaremessung oder
neue Simulation. Die Daten erlauben Zielkurven und Parametergrenzen, aber
keine eindeutige Identifikation sämtlicher GC-/Hystereseparameter.

**Spätere Ergänzung:** Whitlocks neu ausgewertetes Kapitel enthält mit dem
Jensen JT-11P-1 eine besser bezeichnete 1:1-Fitreferenz. Ein erster
effektiver Fit kann mit expliziten Schätzungen beginnen; Details in
[`PARAMETERFIT_GRUNDLAGE.md`](PARAMETERFIT_GRUNDLAGE.md). Dort wird auch
präzisiert, dass geringer relativer Klirr bei steigendem Pegel sowohl
Messrauschen als auch Hystereseverhalten widerspiegeln kann.

## 2. Quellen und Identität

| Lokale Datei | Seiten | Stand / Identität |
|---|---:|---|
| `ArHamm140TEX_140TEX.pdf` | 2 | Hammond; PDF-Erstellung 2012-07-13, keine gesonderte Revisionsnummer sichtbar |
| `ArHamm560Q_560Q.pdf` | 3 | Hammond; PDF-Erstellung 2014-01-27, keine gesonderte Revisionsnummer sichtbar |
| `ArLL1930_Lundahl_LL1930.pdf` | 1 | Lundahl, gedruckt **R181217**; PDF-Metadatentitel irreführend `LL1931`, sichtbares Datenblatt eindeutig **LL1930** |

SHA256:

```text
710d7f729bd951414c25028408046d46c555cbb934bee25c55a210721d3ed314  ArHamm140TEX_140TEX.pdf
05631df2c160b4b15197b5dd87878ab92a72b6a0d95b8c47465b35f7b0b4ff0f  ArHamm560Q_560Q.pdf
6a7fee4d50094ee3ff3a1465a2e2748598201a237f1c78784d436c4464a49863  ArLL1930_Lundahl_LL1930.pdf
```

Ausgewertet wurden die vom Benutzer bereitgestellten lokalen Fassungen.
Tabellenangaben unten sind Herstellerangaben; Werte mit „ca.“ sind eigene
**visuelle Ablesungen** dieser Diagramme. Die Original-PDFs wurden nicht
verändert. Es wurden keine fehlenden Messreihen aus anderen Quellen ergänzt.

## 3. Messbedingungen sind Teil jeder Kennlinie

| Datenblatt / Seite | Konfiguration | Quellenwiderstand `R_s` | Last `R_L` | Pegel laut Legende |
|---|---|---:|---:|---|
| 140TEX / 2, Frequenzgang | 1:1 | 1 kΩ | **1 kΩ** | 1 Vpp, 10 dBm, 19 dBm |
| 140TEX / 2, THD+N | 1:1 | 1 kΩ | **100 Ω** | 1 Vpp, 10 dBm, 19 dBm |
| 560Q / 2 | beide Seiten Serie | 40 kΩ | 40 kΩ | 0, 10, 27 dBm |
| 560Q / 3 | beide Seiten parallel | 10 kΩ | 10 kΩ | 0, 10, 27 dBm |
| LL1930 / 1 | Primärhälften Serie, reguläre Übersetzung 5,8:1 bzw. 11,6:1 | 4,5 kΩ | für Frequenzgang **10 kΩ** genannt | **+30 dBu an Primär** |

Die Hammond-Testzeichnung enthält jeweils `R_s/2` in beiden Primärleitungen;
die Überschrift nennt also den **gesamten differentiellen** Quellenwiderstand.
Für den 560Q steht ausdrücklich „no D.C. saturation“ in den
Frequenzgangbedingungen. Eine DC-vormagnetisierte Kennlinie liegt nicht vor.

**140TEX:** Die abweichende Last `R_L=100` im THD+N-Titel ist auch im
Original-Raster lesbar. Ob dies ein Druckfehler oder eine andere Messung ist,
lässt sich aus der Datei nicht entscheiden. Sie wird nicht still auf 1 kΩ
korrigiert. Frequenzgang und THD+N sind somit vorläufig keine unter
identischer Last vermessene gemeinsame Datenreihe.

## 4. Hammond 140TEX

### 4.1 Tabellierte Ausgangsdaten — Seite 1

- Übersetzung **1:1**, nominal 1000 Ω : 1000 Ω.
- Gleichstromwiderstände **89,7 Ω pro Wicklung**.
- Leerlauf-Induktivität je **7,20 H**, gemessen bei 1 kHz / 1 V.
- Leerlauf-Impedanz je **62,7 kΩ**, ebenfalls 1 kHz / 1 V.
- Übertragungsbereich **20 Hz–20 kHz ±1 dB**; Einfügedämpfung **<1 dB**.
- Nickel-Kern, magnetisch schirmendes Gehäuse.
- Tabelle nennt **+10 dBm** Ausgangsleistung, die Gehäusezeichnung dagegen
  **5 mW**. Diese Angaben sind nicht gleich: 5 mW entsprechen rund +7 dBm.
  Daraus keinen präzisen Sättigungsgrenzpunkt ableiten.

Die nominalen 1000 Ω sind **keine konstanten internen Widerstände**. Die
Klemmenimpedanz hängt von Frequenz, Pegel und Sekundärlast ab.

### 4.2 Frequenzgang — Seite 2, oberes Diagramm

Die Darstellung liegt im Mittelband bei 0; die y-Achse ist inkonsistent als
`RESPONSE (dbm)` beschriftet. Sie eignet sich zur relativen Formbeurteilung,
nicht als eindeutig dokumentierter absoluter Spannungsgewinn.

Visuell abgelesen:

| Punkt | Beobachtung |
|---|---|
| 10 Hz, 1 Vpp | etwa **−0,3 dB** |
| 20 Hz, 1 Vpp | etwa **−0,1 dB** |
| 10 Hz, höhere Pegel | starke Absenkung bis zum unteren Rand bei **−3 dB** |
| ab etwa 20–30 Hz | die drei Kurven nähern sich stark an |
| 100 Hz–20 kHz | nahezu eben auf dem dargestellten Maßstab |
| 50 kHz | ungefähr **−0,1…−0,25 dB** |
| etwa 80–100 kHz | steiler Absturz; genaue Ursache und unbeschnittener Verlauf nicht belegt |

Die 10-/19-dBm-Kurven überdecken sich weitgehend. Ihre einzelnen
Tiefbassverläufe sind aus dem Raster nicht robust zu trennen. Die Pfeile
mit Pegelbeschriftungen sind **Annotationen, keine zusätzlichen Kennlinien**.

**Interpretation:** ausgeprägte pegelabhängige Tieffrequenzgrenze bei
ansonsten weitgehend ebenem Audioband. Daraus folgt keine generelle
Höhenverdunkelung und keine breitbandige Sättigung.

### 4.3 THD+N — Seite 2, unteres Diagramm

Bei den hohen Pegeln erreicht die dargestellte Kurvenhülle ungefähr
**35–40 % bei 10 Hz**, fällt auf **2–5 % bei 20 Hz** und liegt bei
etwa 30 Hz nahe der Grundlinie. 1 Vpp liegt auf diesem groben Maßstab
nahezu auf der Grundlinie.

Die y-Achse reicht von −10 bis +40 %. Negative THD+N sind keine realen
Messwerte, sondern ein unzweckmäßiger Darstellungsbereich. Der Maßstab
erlaubt insbesondere **keine Aussage wie „oberhalb 30 Hz exakt 0 %“** oder
einen präzisen Vergleich von 0,01 % und 0,1 %.

Zusammen mit Last-/Pegelunklarheiten ist die Kurve ein gutes qualitatives
Ziel für einen Tiefbass-Übersteuerungsbereich, aber noch keine belastbare
absolute Volt-/Flux-Knieschwelle.

## 5. Hammond 560Q

### 5.1 Tabellierte Ausgangsdaten — Seite 1

- Geteilte Wicklungen auf beiden Seiten, gleiche Verschaltung → **1:1**.
- Nominal **10 kΩ / 40 kΩ** je Seite, abhängig von Verschaltung.
- DCR Primär **339 Ω**, ausdrücklich Pins 1–4; Sekundär **291 Ω**, Pins 5–8.
- Leerlauf-Induktivitäten je **7,30 H** bei 1 kHz / 1 V; genaue
  Wicklungsverschaltung dieser Induktivitätsmessung nicht bezeichnet.
- Streuinduktivität **1,230 mH**; Messseite/Verschaltung nicht näher bezeichnet.
- Leerlauf-Impedanzen **246 kΩ / 244 kΩ** bei 1 kHz / 1 V.
- Tabelle nennt ±1 dB von **30 Hz–30 kHz**. Der darüberstehende Text nennt
  bei 0 dBm **30 Hz–15 kHz ±1 dB**, bei +10/+27 dBm denselben Bereich
  ohne Toleranz. Diese Angaben nicht zu einer stärkeren Garantie vermischen.

### 5.2 Serienverschaltung: 40 kΩ / 40 kΩ — Seite 2

**Frequenzgang:** bei 10 Hz ca. **−0,1…−0,2 dB**, Mittelband nahezu eben.
Oberhalb ungefähr 10 kHz wächst eine Anhebung: bei 20 kHz ca.
**+0,4…+0,55 dB**, bei 30 kHz ungefähr **+1 dB**. Im Bereich über etwa
40 kHz läuft die Kurve aus der +2-dB-Skala. **Die Resonanzspitze selbst ist
nicht abgebildet.** Man kann weder ihre genaue Frequenz noch ihre Höhe
aus diesem Ausschnitt bestimmen.

**Phase:** bei 10 Hz etwa **+5…+6°** für 0 dBm, **+4,5…+5,5°** für
10 dBm und **+2,5…+3,5°** für 27 dBm. Im Mittelband nahe 0°; bei 20 kHz
etwa **−9…−10°** für 0/10 dBm, bei 27 dBm eher **−6°**.
Die Phase ist also trotz nahezu gleicher Amplitudenkurven pegelabhängig.

**THD+N**, ungefähre Ablesung:

| Frequenz | 0 dBm | 10 dBm | 27 dBm |
|---:|---:|---:|---:|
| 10 Hz | 0,09 % | 0,11 % | >0,2 %, oberhalb der Skala |
| 20 Hz | 0,03–0,04 % | 0,045–0,055 % | 0,08–0,10 % |
| 1 kHz | etwa 0,01–0,02 % | etwa 0,003–0,008 % | nahe Grundlinie, grob <0,005 % |

Dass der relative Mittelbandwert mit höherem Pegel fällt, ist **mit einem
Messrauschboden vereinbar**. Es beweist keine mit Pegel sinkende
Kernverzerrung. THD+N darf nicht als H3 oder als ausschließlich magnetischer
Klirr in einen Waveshaperfit eingehen.

### 5.3 Parallelschaltung: 10 kΩ / 10 kΩ — Seite 3

**Frequenzgang:** etwas stärkere Tiefenabsenkung, bei 10 Hz ca.
**−0,35…−0,45 dB**, bei 20 Hz ca. **−0,2…−0,3 dB**. Im Mittelband erneut
nahe 0. Bei 20 kHz ca. **+0,25…+0,35 dB**, bei 30 kHz
**+0,5…+0,65 dB**. Das Diagramm endet vertikal schon bei +1 dB;
auch hier ist die tatsächliche Resonanzspitze nicht gezeigt.

**Phase:** bei 10 Hz ca. **+10°** für 0 dBm, **+7°** für 10 dBm und
**+6°** für 27 dBm. Bei 20 kHz ca. **−10…−11°** für 0/10 dBm und
**−6°** für 27 dBm.

**THD+N:** bei 10 Hz ca. **0,25–0,30 %** für 0 dBm,
**0,30–0,36 %** für 10 dBm und ungefähr **2 %** für 27 dBm.
Bei 20 Hz ca. **0,1–0,16 %** für 0/10 dBm und **0,3–0,42 %**
für 27 dBm. Ab ungefähr 100 Hz sind alle auf diesem gröberen
0,5-%-Raster nahe der Grundlinie; der Restklirr ist dort nicht präzise
ablesbar.

**Interpretation:** Die komplette geprüfte Parallel-Konfiguration zeigt mehr
Tiefbass-THD+N. Das darf nicht allein einer „anderen Kernsättigung“
zugeschrieben werden: Windungszahl, Anschluss, Quellen-/Lastimpedanz und
eventuell Pegelbezug verändern sich gemeinsam. Insbesondere ist nicht
belegt, dass beide Diagramme dieselbe tatsächliche Spannung pro Windung
verwenden.

## 6. Lundahl LL1930

Das Datenblatt spezifiziert **5,8 + 5,8 : 1 + 1**, mit Primärhälften in
Serie und Sekundärhälften in Serie für **5,8:1** bzw. parallel für **11,6:1**.
Das ist eine Röhren-Line-Ausgangsanwendung mit Parafeed-Kopplung, kein
als 1:1 spezifizierter Line-Isolator.

Zwei gleichartige Teilwicklungen könnte man prinzipiell gegeneinander als
1:1 verwenden. **Die veröffentlichten Kennwerte qualifizieren diese
abweichende Beschaltung aber nicht.**

Tabellierte Angaben, keine abgelesenen Kurven:

- hochpermeabler Mu-Metall-Kern,
- je Primärhälfte **610 Ω**, je Sekundärhälfte **16 Ω**,
- Verzerrung bei **+30 dBu Primärsignal**, `R_s=4,5 kΩ`, Primär Serie:
  **<0,1 % bei 50 Hz**, **<1 % bei 25 Hz**,
- Frequenzgang mit obiger Anregung und **10 kΩ Sekundärlast**:
  **20 Hz–30 kHz innerhalb ±0,1 dB**.

Die Last wird explizit in der Frequenzgangzeile genannt, nicht nochmals
in der Verzerrungszeile. +30 dBu entsprechen für einen Sinus ungefähr
**24,5 V RMS**; diese Umrechnung ist eigene Rechnung. Die beiden
Verzerrungsgrenzen sind **Ungleichungen**, keine exakten Messpunkte und
keine vollständig bestimmte Sättigungskurve.

## 7. Was sich für ein Modell ableiten lässt

### 7.1 Gut belegte Größen

- Wicklungsverhältnis und Anschlussvarianten.
- DCR unter den bezeichneten Anschlussbedingungen.
- Relative Amplitudengänge; beim 560Q zusätzlich Phasengänge.
- Frequenz-/Pegelbereiche steigender THD+N sowie einzelne obere Grenzen.
- Induktivitäts-/Impedanzangaben als **Messwerte bei einer konkreten
  Frequenz und Spannung**, nicht automatisch als frequenzunabhängige
  ideale Bauteilwerte.

### 7.2 Noch nicht eindeutig identifizierbar

- H2/H3/H5-Verteilung, Asymmetrie und zeitliche Wellenform.
- Remanenz, Koerzitivfeld und Hystereseschleifen.
- Ein eindeutiger Satz `C/a/n/r/b/m` des de-Paiva-Modells.
- Digitale dBFS-zu-Volt-Skalierung, solange Pegelbezug der Herstellerkurven
  offen ist.
- Aus den mittelbandbezogenen Frequenzgängen eine absolute
  Eingang-Ausgang-Kompressionskennlinie.
- Genaue Resonanzfrequenz/-güte oberhalb des sichtbaren Kurvenbereichs.

THD+N begrenzt die Verzerrung unter dem jeweiligen Messaufbau, enthält aber
auch Rauschen und Restfehler des Aufbaus. Die Plot-Grundlinie darf kein
exaktes Nullziel für einen Parameteroptimierer sein.

### 7.3 Drei Konsistenzprüfungen vor einem Fit

**1. Relativer Frequenzgang versus absolute Einfügedämpfung.**
Die Hammond-Frequenzgänge liegen ungefähr bei 1 kHz auf 0 dB. Mit
endlicher Quelle und Last kann das nicht ohne weiteres das Verhältnis zur
unbelasteten Quellspannung sein. Beim 140TEX ergibt ein einfacher
Mittelband-Kupfercheck aus `R_s=R_L=1000 Ω` und zweimal 89,7 Ω:

```text
Vout/Vsource ≈ 1000/(1000 + 89.7 + 89.7 + 1000)
             ≈ −6,77 dB
Zusatzverlust gegenüber direkter 1k/1k-Verbindung ≈ −0,75 dB
```

Das passt als Plausibilität zur angegebenen Einfügedämpfung <1 dB,
beweist aber nicht die genaue Normalisierung der Abbildung.

**2. dBm ist keine feste Spannung.**
Bei tatsächlicher Leistung in einer bekannten ohmschen Last gilt
`V_RMS=√(R·0,001·10^(dBm/10))`. Beispiel +27 dBm: **141,6 V RMS in
40 kΩ**, **70,8 V RMS in 10 kΩ**. Die Datenblätter sagen nicht eindeutig,
ob ihre Legenden Lastleistung, verfügbare Quellleistung oder eine auf
anderer Referenzimpedanz beruhende Geräteeinstellung meinen. Diese
Spannungen sind daher **bedingte Umrechnungen, keine belegte Anregung**.
Die Einheiten nicht still durch dBu ersetzen. Ebenso ist die Messstelle
von „1 Vpp“ nicht eindeutig bezeichnet.

**3. L-, Impedanz- und Frequenzgangangaben nicht blind zusammenstecken.**
Eine ideale 7,20-H-Induktivität hätte bei 1 kHz `ωL≈45,2 kΩ`, während
der 140TEX **62,7 kΩ** nennt. Für 7,30 H sind es **45,9 kΩ**, während
der 560Q **246/244 kΩ** nennt. Verlustbehaftete Messmodi, parasitäre
Kapazitäten, Pegel-/Frequenzabhängigkeit oder uneindeutige Anschlussangaben
müssen vor einer Gleichsetzung untersucht werden; die Zahlen werden
nicht als falsche Daten ersetzt.

Auch ein einfaches 1:1-Modell mit 7,30 H als reinem Magnetisierungsshunt
und `R_s=R_L=40 kΩ` hätte näherungsweise
`f_c=(R_s||R_L)/(2πL)≈436 Hz` und bei 10 Hz fast **+89° Phase**.
Das reproduziert die gezeigten etwa +3…+6° offensichtlich nicht.
Die Rechnung widerlegt dieses **einfache Ersatzmodell mit dieser
Wertzuordnung**, nicht den realen Übertrager. Für einen physikalischen
Fit ist die genaue Bedeutung der tabellierten Induktivität offen.

## 8. Empfohlener Weg für Green Stripe

1. **1:1-Klangziel anhand dieser Line-Übertrager definieren.** Der 140TEX
   gibt einen passenden 1-kΩ-Anwendungsrahmen; der 560Q liefert die
   informativere Amplituden-/Phasen-/Pegelmatrix. Die zwei 560Q-
   Verschaltungen als getrennte Referenzbedingungen behandeln.
2. **Linearen Anteil zuerst fitten:** relative Amplitude **und Phase**
   beim 560Q gemeinsam, mit der dokumentierten Quelle/Last. Unaufgelöste
   Resonanzspitzen nicht extrapolieren. Die gemessene Phasendrehung ist
   auch für interne Parallelmischung relevant, selbst bei flachem Betrag.
3. **Nichtlinearität danach:** zunächst Tiefbass-THD-Bereiche und
   Pegelabhängigkeit; Mittelband-Rauschboden als Unsicherheitsgrenze
   behandeln. Ein flacher Pegelgang allein ist keine Klirrfreiheit.
4. **Physikalischer GC-Fit erst mit geklärten Bezugsgrößen:**
   Leerlauf-Strom/Spannung bzw. Schleifenmessungen nach de Paiva oder
   zusätzliche Herstellerangaben. Bis dahin sind mehrere
   Parametersätze mit denselben Datenblattkurven vereinbar.
5. **Volt-Skalierung explizit festlegen:** Der spätere virtuelle Drive
   bestimmt, ob die Schwelle bei normalem Programmmaterial erreicht
   wird. Eine absichtlich stärker färbende Variante wäre eine eigene
   Abstimmung, keine aus diesen Datenblättern belegte Eigenschaft.

Die Daten legen eine sparsame, überwiegend saubere 1:1-Stufe nahe, deren
Nichtlinearität bei genügend **V/f** im Bass wächst. Sie begründen weder
eine bestimmte „60s/80s/00s“-Zuordnung noch einen Nachbau eines 1176-
Übertragers.

## 9. Ablesedatei und Aussagegenauigkeit

[`KENNLINIEN_ABLESUNG.csv`](KENNLINIEN_ABLESUNG.csv) enthält **47 bewusst
grob abgegrenzte Ablesepunkte/-bereiche** mit Dateiname, Seite, Verschaltung,
Quellen-/Lastwiderstand, Kurvenlabel und Einheit.

- `visual_interval`: visueller Bereich für einen bezeichneten Verlauf.
- `visual_envelope`: Bereich über mehrere angegebene, teilweise
  überlagerte Pegelkurven; keine statistische Unsicherheit eines Einzelpunkts.
- `visual_upper_range`: auf dem Raster nur eine grobe obere Größenordnung.
- `*_bound_*`: durch Bildrand begrenzter Wert; leere Schranke = unbekannt.

Das sind **keine Original-Rohmessdaten und kein automatisch digitalisierter
hochpräziser Kurvensatz**. Bei einem späteren Fit sind diese Bereiche als
schwach gewichtete Intervalle zu verwenden, nicht als Gleichungen mit
sechs Nachkommastellen. Bildgröße, Strichbreite, Überlagerung und
Beschriftungen begrenzen die Ablesbarkeit.
