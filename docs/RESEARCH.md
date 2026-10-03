# Recherche und Modellierungsgrundlage

Gesamter Quellenkatalog: `SOURCES.md`. Im Folgenden stehen die fachlichen
Erkenntnisse und ihre Aussagegrenzen. Letzte Zielkorrektur des Benutzers:
**eigener Green Stripe, Revision A oder D unerheblich**.

## 1. Lokale Materialien

### `../1176.js`

JSFX/EEL2-Datei mit Stillwell-1175-Quelltext, keine JavaScript-Datei. Die lokale
Fassung enthält offenbar verlorene Multiplikationen und beschädigte Ausdrücke
(etwa `1srate`, `gfx_w20`, wet-output ohne Eingangsmultiplikation). Zudem mehrere
nicht initialisierte/ungenutzte Variable. Die permissive Stillwell-Lizenz ist
enthalten. Sie wurde **nicht überschrieben oder als neuer Kern kopiert**.

Das vereinfachte Feed-forward-Modell eignet sich als historischer Ausgangspunkt,
aber nicht als schaltungsgetreue 1176-Referenz. Der neue Code besitzt eigene
Namens-/Regler-/State-Struktur und einen tatsächlich rückgekoppelten Detektor.

### Felix Eichas: Dissertation, 2019

Titel: *System Identification of Nonlinear Audio Circuits*. HSU Hamburg,
Verteidigung 24.10.2019. Lokale Fassung 166 PDF-Seiten einschließlich
Bereinigungsseite; gedruckte Seite +15 = lokale PDF-Seite. Der vollständige
extrahierbare Text wurde ausgewertet; Grafiken/Schaltzeichnungen nicht visuell
digitalisiert. Der offizielle HSU-PDF hat eine Seite weniger.

Kapitelübersicht: Virtual-Analog/Identifikation (1–2), Filter/Nichtlinearitäten/
Antialiasing (3), Optimierung/Messung (4), Metriken/Hörtestmethoden (5),
Kompressoren (6), Verzerrer (7–8), Verstärker (9), Grenzen (10), Symbole/Bibliografie.

**1176-Fallstudie steht in 6.3**, nicht 6.2 (dort Flatline-Optokompressor):
Rev.-D-DIY-Nachbau, kein ursprünglicher Rev.-A- oder Vintage-Datensatz.
Kapitel 6.4–6.5 beschreiben ein flexibles **Feed-forward-Verhaltensmodell**, obwohl
die Hardware Feedback nutzt. Diese Vereinfachung ist ausdrücklich auf S. 68
genannt und darf nicht stillschweigend mit Schaltungsidentität gleichgesetzt werden.

Nutzbare Struktur, S. 63–75:

- Linearen Eingangsblock unter Kompressionseinsatz messen.
- Statische Kurven pro Ratio, Gain-LUT mit Interpolation.
- Pegeldetektor mit vier positiven/negativen Attack-/Release-Koeffizienten.
- Drei Einpolfilter: einer vorgeschaltet, zwei parallel; zwei Mischgewichte.
- Zusammen 14 anpassbare Parameter.
- Zuerst Hüllkurvenfehler, dann Zeitbereichsfehler auf Musik minimieren.
- Gemeinsame Attack-/Release-Fläche: Release-Stellung verändert Attack.
- Ein gezeigter Hüllkurventest verbessert sich von ~1 dB auf <0,1 dB Fehler.

Die Gleichungen/Optimierungsinitialisierung sind nutzbar, aber endgültige LUTs,
Polynom-/Filterkoeffizienten und gepaarte WAV-Aufnahmen wurden im PDF/Repository
**nicht veröffentlicht gefunden**. Kein Datenanhang. Vorsicht bei verwendeten
Filterzeitformeln: Faktor 2,2 entspricht etwa 10–90-%-Zeit, nicht klassischem RC-τ.

Die guten Gitarren-/Basswerte sind nicht gleich gut für Drums: auf S. 76 weist
der 1176-Drum-Test ESR etwa 0,266 auf. Hörtest 63 Teilnehmer, 31 ausgeschlossen;
keine allgemeine Ununterscheidbarkeit aller Reglerstellungen. Der Autor nennt
interaktiven Echtzeitvergleich als weitere Arbeit.

ADAA+2× (S. 20–25) gehört speziell zu Waveshaping und ist **kein bewiesener
Oversampling-Faktor für den Kompressorkreis**. ADAA bringt Phase/Delay mit und
kann im Feedbackkreis nicht beliebig ergänzt werden.

## 2. Hardwareprinzipien aus UA/UREI

Belegt sind: Input steuert Kompressionsmenge, Ratio steuert auch Threshold,
Soft Knee, schnelle Attack, programmabhängige Erholung, All-Buttons-Biasänderung,
GR-FET als Shunt-Spannungsteiler und Feedback-Abgriff vor dem Output-Regler.
Bei D/E Vollwellendetektion mit zwei phaseninvertierten Verstärkerzweigen.

Output beeinflusst den GR-Kern nicht, aber die Aussteuerung der Ausgangsstufe.
Attack OFF lässt Audiopfad und Färbung aktiv. Der UA-Plugin-Tippartikel beschreibt
auch No-Ratio-Buttons als Colour-only; das ist keine umfassende historische
Schalter-Netlistbestätigung. Green Stripe hat dafür explizit Compression Off.

Unterschiede A/AB/C/D/E/F/G/H sind real: LN-Linearisierung ab C, andere
Verstärkertransistoren/-strukturen, F Class-AB-Ausgang, später elektronischer
Eingang. Ursprüngliche A versus typische AB-Nachbauunterlagen nicht verwechseln.
Nach Benutzerkorrektur sind diese Daten Inspiration/Provenienz, keine feste
Green-Stripe-Revisionseinschränkung.

Nominale 20–800 µs / 50 ms–1,1 s nicht ohne Messdefinition als digitale τ
einsetzen. Der spätere UREI-Service-Test nutzt Burst-/Ausgangsamplitude und
63-%-Erholung; neuere Reissue-Specs/Thresholdtabellen nicht ungeprüft für alle
früheren Einheiten übernehmen.

## 3. Mason und AXT: zusätzliche numerische Evidenz

Mason: Gyraf/MNATS-F-abgeleiteter Nachbau mit Lundahl, ausdrücklich keine
Original-A-Referenz. Die `.xls` enthalten reale Kennlinien-/FET-Messwerte.

Mason-Ratio-Sekanten 0 bis −3,01 dBu Eingang:
**5,129 / 8,167 / 11,515 / 20,473**. 20:1 basiert auf nur 0,147 dB Output-
Änderung, daher Messauflösung wichtig. Grundgain aus unteren Punkten etwa
+0,263 dB; echte GR gegen Compression-Off-Referenz bestimmen.

AXT hat mehrere verschiedene Ratio-Snapshots, teilweise Zusatzratios. Sie nicht
als einheitliche Solltabelle zusammenführen. Die Testreport-Daten und die
separate Ratio-Datei ergeben für 20 verschiedene Werte (~19,45 versus ~13,64).
Input-/Outputstellungen bestimmen den externen Kompressionseinsatz.

FET-Matching: BF245A/2N5457-Lastlinien. Korrekt ist
`Id=(V_supply−Vds)/Rd`; Masons Fließtext verwechselt diese Formel, sein
Spreadsheet rechnet korrekt. Flaches Id-Plateau ist durch Versorgung/Rd
limitiert, nicht automatisch Idss; Vds/Id nur Sekantenwiderstand. Fehlende
Kleinsignal-/Polaritätskennfelder verhindern direkte vollständige GR-FET-Fits.

All Buttons bei AXT: AC-/DC-Pegel **und Quellenimpedanz** ändern sich. Für dessen
gezeigtes AC-Netz: 4-Tap 0,1661 / 20-Tap 0,8021 / All 0,4563. Thevenin etwa
39,19 / 44,92 / 25,55 kΩ. „~10:1-Tap“ ist eine Teiler-Heuristik, kein gemessener
geschlossener Ratio-Wert. Äußere Tasten können All elektrisch entsprechen.

Mason-WAV-Paare existieren: Drum-Beispiel Stereo 48 kHz/16 Bit, Bass Mono
44,1 kHz/16 Bit. Sie korrespondieren, benötigen jedoch Zeit-/Pegelabgleich und
haben keine vollständige dBu-/Regler-/Normalisierungsdokumentation.
Nutzbar als Hörtest, nicht präzise 20-µs-Identifikation.

## 4. Austin Moore: All Buttons In, 2012

UA-Reissue, musikalische Untersuchungen für Vocals/Bass/Drum-Room. 24-Bit/44,1-kHz-
Quellen und ungefähr −18 dBFS Sendpegel, keine absolute dBu-Kalibrierung.
Schnelle Basszeiten erzeugen hörbare Tieftonverzerrung; All auf Drum-Room
andere Textur und teilweise Überschwinger. Keine vollständigen Harmonischen-
oder Reglerparameterdaten und keine kontrollierte Hardwareidentifikation.

Der Artikel nennt 200–800 µs: **200 ist gegenüber Hersteller 20 µs fehlerhaft**.
Die aktuellen HTML-Beispiele sind Dateinamen ohne nutzbare WAV-Links. Verfügbarkeit
von Abbildungen beweist nicht Verfügbarkeit der Audioreferenzen.

## 5. Andere DSPs und Mathematik

### ZeroComp

Allgemeiner Feed-forward-Kompressor mit nachgelagerter asymmetrischer FET-`tanh`-
Färbung, JUCE/WebView/X11-Umgebung. Nützlicher Softwarevergleich, keine
1176-Schaltungsreferenz und nicht als Dwarf-Laufzeitgrundlage kopiert.

### Joep Vanlier

Tight Compressor zeigt EEL2-Namespaces, GR-Anzeige und Dynamikdarstellung.
Seine große `saike_upsamplers`-Bibliothek ist FIR, nicht die hier gesuchte IIR-
Kette. Bei 4× etwa 32 Samples Up+Down-Verzögerung. Nicht pauschal als
„low latency allpass“-Bibliothek bezeichnen. Die Codebibliothek wurde nicht in
Green Stripe kopiert; der gepflegte ysfx-Fork ist der separate Testhost.

### Paulllux/fetcomp-dsp

MIT, Commit `de18f5ac793e36397c725abdca7fcb8c08760ce2`, zwei Header mit JUCE-
Abhängigkeit. Divider-Gleichung aus JFET-Ohmik/LN-Gatefeedback, feedbackseitige
Ratio-Gain-Law `R−1`, getrennte Detektor-/Release-/Iron-Stufen.

README erklärt den Fit gegen ein **Referenzplugin**, nicht Originalhardware;
Transformer ist nach Autorangabe schwächster Teil. Die Aussage, ein einzelner
Sampledelay sei gegenüber allen Zeitkonstanten vernachlässigbar, darf bei 20 µs
und 48 kHz nicht ungeprüft übernommen werden. Green Stripe verwendet deshalb
weiterhin seine zeitkonsistente implizite Lösung.

Der Header enthält mehrere fortlaufende Experiment-/Kalibrierzweige; Kommentare
sind keine unabhängige Evidenz für deren Hardwaretreue. Die dortigen
Potentiometertabellen und Transformerwerte sind hier nicht importiert.

### Approximating Hyperbolic Tangent

J. Tom Schroeder (2026) vergleicht Taylor, Padé, Splines und Float-Format-Hacks.
Green Stripe nutzt die mathematische [7/6]-Padé-Formel (C++ und EEL identisch),
nicht Rust-/JUCE-Code und keine Bit-Hacks. Wichtig: begrenzte Approximation,
identische Biaskorrektur, passende Ableitung und gesonderte Aliasingprüfung.
Eine schnelle Approximation alleine liefert keine originalgetreue Färbung.

## 6. Praxisquellen → Presetentwurf

UA: 4:1, Attack 10 Uhr, Release 2 Uhr („Dr Pepper“), musikalischer Release,
All bei Raum/Parallel, Fast/Fast für Grit, Colour-only bei DI-Gitarre.
Die Clock-Positionen werden als **eigene Skalenannäherung** dokumentiert.

Vocal-Guide: Frontkante, Body und Platzierung hören; Lernübung Extreme mit
12–15 dB GR, danach zurücknehmen. MusicGuy nennt 4/8 und Mix/All als Start,
verwechselt aber stellenweise Knopfzahlen/Inputbezeichnung. Primärunterlagen
haben bei technischen Konflikten Vorrang. Blackbird beschreibt Praxis/Revisionen,
doch nicht jede Gain-/Transformerbehauptung ist als Schaltplanbeleg belastbar.

Reddit-/Gearspace-Inhalte waren nicht sinnvoll zugänglich. Keine erfundenen
Forumtipps als Presetbegründung. Instrumentwerte in `data/presets.json` sind
musikalische Startpunkte, nicht aus einem Thread übernommene „beste Settings“.

## 7. NAM

Siehe `NAM_PROFILES.md`. Sourcebeschreibung „Clean captures of compressor tone“
passt zu Färbung, belegt aber keinen GR-Off-Zustand. Die endlichen WaveNet-
Historyfenster können keine beliebig lange unabhängige Release-Historie
speichern. Ein ganzes Hardware-Capture ist nicht eindeutig in Input/GR/Output
zerlegbar. Kein automatisches Kaskadieren mit der expliziten Kompressorregelung.

## 8. Konsequenz

Quellenwissen bestimmt Struktur, Vergleichsverfahren und dokumentierte Grenzen.
Der funktionsfähige Green Stripe ist eine prüfbare erste Abstimmung.
Weitere Färbungs-/Zeitkalibrierung wird anhand dokumentierter Messungen und
pegelgleicher Musiktests entschieden, nicht durch alleinigen Revisionstitel.

## 9. Erneuter Dissertation-Abgleich für CPU, 0.1.1

Gedruckte S.63–75 erneut geprüft: die Arbeit setzt bewusst einen reduzierten
Feed-forward-Pegel-/LUT-/Dreieinpolkern statt transistor-/solverintensiver
Onlineauswertung ein. Diese Richtung ist für ein weiteres CPU-Ziel plausibel,
aber kein direktes Drop-in für denselben Feedback-/Slam-Klang. Die Arbeit
veröffentlicht weder fertige Tabellen noch Echtzeitkosten für Dwarf.

0.1.1 entfernt zunächst belegte Verschwendung im bestehenden Kern: drei immer
aktive Stereoregler, Off-/Bypass-Reglerarbeit, Sample-exp/log bei Entladung,
mehrfacher Bias und EEL2-RAM-Schleifen. Stationäres Verhalten gegen gesicherte
0.1.0 geprüft. Details, Messzahlen und weitere LUT-/Mehrzeitkonstanten-
Kalibrierempfehlung in `CPU_ANALYSIS.md`.
