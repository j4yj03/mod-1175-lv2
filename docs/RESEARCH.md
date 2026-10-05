# Recherche und Modellierungsgrundlage

Gesamter Quellenkatalog: `SOURCES.md`. Im Folgenden stehen die fachlichen
Erkenntnisse und ihre Aussagegrenzen. Letzte Zielkorrektur des Benutzers:
**eigener Green Stripe, Revision A oder D unerheblich**.

**Produktstand 0.4.0:** Die am Ende dieses Dokuments beschriebenen Offlinefits
sind inzwischen als refit-fähige Eingangsstufe portiert. Der konkrete
Runtime-Vertrag und die getrennten Amplituden-/Phasengrenzen stehen in
`TRANSFORMER_RUNTIME.md`. Historische Quellen-/Fitberichte bleiben inhaltlich
erhalten und sind keine zusätzliche Geräte- oder Hardwareabnahme.

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

## 10. Transformator-Identifikation nach de Paiva et al., 2011

Am 2026-10-05 wurde die vom Benutzer bereitgestellte PDF *Real-Time Audio
Transformer Emulation for Virtual Tube Amplifiers* vollständig ausgewertet.
Detailbericht mit Formeln, Tabelle 1 und Seitenbelegen:
[`TRANSFORMER_PAPER_REVIEW.md`](TRANSFORMER_PAPER_REVIEW.md).

Die Arbeit schließt eine konkrete Lücke: Sie liefert ein **bidirektionales
GC-/WDF-Modell**, einen **elektrischen Mess-/Fitablauf** und einen
**vollständigen Referenzparametersatz** für einen Fender NSC041318.
Die beiden Wicklungen teilen einen Kern; Laständerungen wirken auf den
Treiber zurück. Damit unterscheidet sich die Struktur wesentlich von der
instabilen lokalen `xformer.lib`, die zuvor in `spice_sim/` untersucht wurde.

Der Fit benötigt keine bekannte Kerngeometrie: Strom an der angeregten
Wicklung und Spannung an der offenen Wicklung liefern die H–Φ-Schleife.
Die Mittellinie bestimmt `C/a/n` über gewichtete kleinste Quadrate;
Schleifenbreite, Remanenz und Koerzitivpunkte informieren den Verlustzweig.
Windungszahlen dürfen bei erhaltenem Verhältnis als Normierung gewählt
werden. Ein neuer Green-Stripe-Parametersatz braucht dennoch elektrische
Referenzdaten oder ausdrücklich eigene Klangziele und eine Volt-/dBFS-Skalierung.

Die Formel `H_s=Φ/C+a|Φ/C|^n·sgn(Φ/C)` macht zudem deutlich:
Eine selbst definierte Gleichheit der linearen/nichtlinearen Beiträge führt
zu `Φ_k=C·a^(-1/(n-1))`, nicht zur bisherigen Projektformel mit `ω`.
Das ist eine algebraische Definition in gewählter Normierung, kein
gemessener 1-dB-Kompressionspunkt. Frequenzabhängigkeit entsteht durch
Spannungsintegration und Beschaltung.

Offen bleiben vor Reproduktion die `b`-Normierung des Widerstandszweigs
und die Unterscheidung von Sekanten- zu Differentialpermeanz. Der Paper-WDF
verwendet Ein-Sample-Verzögerungen; der Artikel nennt selbst Stabilitäts-
und Transientengrenzen. Empfohlen ist deshalb zuerst eine **separate
Offline-Referenz mit Tabelle 1**, dann der Vergleich des günstigen WDF-
Kandidaten bei 48/96/192 kHz. Noch kein Paper-Modell implementiert oder
validiert, kein neuer Echtzeit-/Presetparametersatz.

## 11. Reale Line-Übertrager: Hammond und Lundahl

Die drei lokalen Datenblätter in `docs/transformer/` wurden am 2026-10-05
vollständig einschließlich aller acht Diagramme ausgewertet.
Bericht: [`transformer/AUSWERTUNG.md`](transformer/AUSWERTUNG.md),
47 grobe Ableseintervalle in `transformer/KENNLINIEN_ABLESUNG.csv`.

- **140TEX:** 1:1, 1-kΩ-Anwendung, nahezu ebener Audioband-Frequenzgang,
  auffällige Großsignal-Absenkung/THD+N hauptsächlich unter etwa 20–30 Hz.
  Die Lastangaben der beiden Diagramme unterscheiden sich (1000/100 Ω);
  absolute Schwelle und einzelne hohe Pegelkurven daher nicht präzise fitten.
- **560Q:** 1:1, Serien-/Parallelschaltung separat bei 40k/40k bzw.
  10k/10k vermessen. Neben Tiefbass-THD+N ist die HF-Anhebung relevant:
  bei 20 kHz grob +0,5 dB (Serie) bzw. +0,3 dB (parallel), mit etwa
  −10° Phase für die niedrigeren Pegel. Die echte Resonanzspitze liegt
  außerhalb des sichtbaren Amplitudenbereichs. Mittelband-THD+N teilweise
  mit Messrauschboden vereinbar, keine direkte H3-Zielkurve.
- **LL1930:** spezifiziert 5,8:1/11,6:1, nicht 1:1; keine Diagramme,
  nur Grenzen bei +30 dBu Primärsignal: <0,1 % bei 50 Hz, <1 % bei
  25 Hz und 20 Hz–30 kHz ±0,1 dB unter den genannten Bedingungen.

Konsequenz: de Paiva liefert Modellstruktur/Identifikation, die Hammond-
Blätter liefern für Green Stripe passendere **Line-Übertrager-Zielkurven**.
Amplitude und Phase zuerst gemeinsam abstimmen, dann die Tiefbass-
Nichtlinearität. Vor einem physikalischen Zahlenfit müssen dBm-Bezug,
Normalisierung und L-/Impedanzkonventionen geklärt werden. Eine skalare
breitbandige Sättigung oder ein eindeutiger Hysteresefit lässt sich aus
diesen Kurven allein nicht begründen.

## 12. Parameterfit mit Schätzungen: neue Literatur und Jensen-Referenz

Die zusätzliche Recherche vom 2026-10-05 ist in
[`transformer/PARAMETERFIT_GRUNDLAGE.md`](transformer/PARAMETERFIT_GRUNDLAGE.md)
zusammengeführt. Whitlocks *Audio Transformers* und DeLorias/Lundahls
Chapter 6 wurden vollständig gelesen, McLymans 534-seitiges Handbuch
gezielt in den relevanten Magnetisierungs-/Material-/Parasitenabschnitten.
Der GroupDIY-Thread war vollständig mit 22 Beiträgen zugänglich.

**Wichtigster neuer Datensatz:** Whitlock enthält das historische
**Jensen JT-11P-1**-Datenblatt mit 1:1, 600-Ω-Quelle, 10-kΩ-Last,
1,45/1,55-kΩ-DCR, THD-Kurven über Pegel/Frequenz und definierten dBu-
Eingangspegeln. Typisch +20 dBu bei 20 Hz für 1 % THD ist ein belastbarerer
Kalibrieranker als die uneindeutig bezeichneten Hammond-dBm-Kurven.
Als erste saubere Line-Eingangsreferenz ist der Jensen daher empfohlen;
Hammond bleibt jeweils eigenes Zielbild.

Eine erste **effektive** Identifikation kann mit expliziten Annahmen beginnen:
Fluxverkettung statt unbekannter Kerngeometrie, positive Verlustglieder,
effektives HF-`f0/Q`, symmetrischer Null-Bias, eigene Volt-/dBFS-Zuordnung.
Reproduzierbare Startrechnungen in `transformer/estimate_fit_start.py` und
`FIT_STARTWERTE.json`; keine fertigen DSP-Koeffizienten. Breiter LF-L-Suchraum
ist nötig: einzelne Bandbreiten-/Amplitudenpunkte implizieren verschiedene
Einpolwerte; ein konstantes L muss nicht das ganze Band beschreiben.

Für einen eindeutigen Bauteilfit fehlen weiter Magnetisierungsstrom,
getrennte H2/H3/H5, Minor-Loops/Transienten und eine zweite Last-/
Quellenbedingung. Schätzungen machen diese Information nicht überflüssig,
ermöglichen aber einen nachvollziehbaren ersten Gray-Box-Kandidaten.

**Korrektur einer möglichen Fehlinterpretation:** Sinkender relativer
Kleinpegelklirr muss kein Messrauschen sein. Whitlock zeigt auch reale
Hystereseverzerrung bei kleinen Pegeln. THD+N-Plateaubereiche deshalb als
unsicher behandeln, nicht pauschal als Noise entfernen. Außerdem ist
Jensens DLP keine rohe Phase. GroupDIY #8 enthält einen Rechenfehler
(`atan(0,5)` ist 26,565°, nicht 45°); Erfahrungsbeiträge sind keine
Bauteilparameterbank.

## 13. Erregerstrom und Vergleich einfacher/detaillierter Kernmodelle

Die sechs Seiten des HiFiHaven-Threads (110 Beiträge), StackExchange-Frage
606060 mit drei Antworten und vier zusätzliche Papers wurden am 2026-10-05
ausgewertet. Details:
[`transformer/ERREGERSTROM_UND_MODELLVERGLEICH.md`](transformer/ERREGERSTROM_UND_MODELLVERGLEICH.md).

- Leerlaufmessung liefert zunächst **Erregerstrom** inklusive Kernverlust-
  und gegebenenfalls kapazitiver Anteile. Phasen-/Wirkleistungsinformation
  ist für einen separaten Magnetisierungs-/Verlustfit wichtig. Ein
  Hysteresemodell kann Verluste bereits enthalten; nicht doppelt addieren.
- `05_e.pdf` ist Macak/Schimmel DAFx-11, S. 59–62. Es vergleicht einen
  **dynamischen Fröhlich-Kern ohne Hysterese** mit Jiles–Atherton in einer
  vollständigen Röhrenendstufe. Ähnliche Resultate in diesem Aufbau
  rechtfertigen eine einfache Baseline; sie qualifizieren keinen Jensen-
  Kleinpegelkern. Eigene Umformung in `L0` und `lambda_sat` erlaubt eine
  geometriefreie Fitparametrisierung; Polstelle und numerische Lösung prüfen.
- Bal/Öncü 2014: lineares 40-kHz-Stromwandlermodell und Zenerlast,
  brauchbare Strom-/Lastinteraktion, keine Audio-Sättigungsbank.
- Shadid et al. 2022: mehrere Impuls-/Anschlussbedingungen zur
  Wicklungsdiagnose, methodisch nützlich. Gedrucktes `h(t)=Vout/Vin`
  nicht übernehmen: `H=FFT(out)/FFT(in)` bzw. regularisierte Entfaltung.
  Eine LTI-Impulsantwort ersetzt keine nichtlineare Identifikation.
- Wu et al. 2019: NN schätzt statische Stromkennwerte aus bereits
  vorhandenen 500-kV-PSCAD-Simulationen; keine Audio-Wellenform und
  kein Ersatz fehlender Trainings-/Messdaten.
- HiFiHaven enthält Hörberichte, Filtervorschläge und Scope-Deutungen.
  Die Zusatzfilterwerte sind keine gemessenen Übertragerparameter;
  Rekonstruktionsbilder, Aliasing, lineares Ringing und nichtlineare
  Harmonische müssen sauber unterschieden werden.

Empfehlung: Jensen-Referenz beibehalten, einfache lastgekoppelte
Flux-/Sättigungsbaseline gegen schwaches GC-Gedächtnis vergleichen,
J-A erst bei zusätzlichem Bedarf. H2/H3/H5, phasenrichtiger Leerlaufstrom
und Einschalt-/Vorbelastungsbursts bleiben die wichtigsten neuen Messdaten.

## 14. Tatsächlich ausgeführter Jensen-Offlinefit

Auftrag und Benutzerwahl **„warm → ausgewogen → clean“** sind am 2026-10-05
als Offlinearbeit umgesetzt. Ergebnisse:
[`transformer/offline_fit/BERICHT.md`](transformer/offline_fit/BERICHT.md).

Ein reduziertes lastgekoppeltes Flux-Netz, 14 positive Stop-Zweige,
ein RL-Relaxationszweig und effektives HF-`f0/Q` wurden gegen die historischen
Jensen-JT-11P-1-Ziele untersucht. 36 Basisfits (18 Varianten × 2 Starts),
acht lineare Starts und Verfeinerungen; keine Produkt-DSP-Änderung.
Ausgewählt wurde ein Fröhlich-artiger Kern mit schwachem Gedächtnis.
Ein zusätzlicher dynamischer Sättigungszweig verbesserte den Fit nicht
und wurde nicht als weitere freie Parameterquelle übernommen.

53 Zielbedingungen, 20 davon zurückgehalten: **18/20** innerhalb der
Intervalle. **24/33** Trainingstreffer; der Fit bleibt partiell. Typischer
1-%-THD-Punkt des Modells bei +20,49 dBu / 20 Hz statt +20 dBu.
Kleinpegel- und steile Hochpegelkurven bleiben teilweise abweichend;
Gedächtnis-/Materialidentität folgt nicht aus dem stationären Fit.
Subaudio-Amplitude mit unbekanntem Herstellerpegel wird nur als linearer
Hintergrund fitten, nicht als bestätigte vollständige Großsignalantwort.

Daraus sind eigene Profile abgeleitet: 60s warm (p=3, 26-kHz-HF),
80s ausgewogen (p=5, 48-kHz-HF), 00s clean (Jensen-artig,
108-kHz-HF). 1-%-THD-Anker bei 20 Hz auf −14/−8/−2 dBFS Peak;
gemeinsame Volt-Skalierung und feste explizite Mittelbandnormalisierung.
Sieben WAV-Proben und 168 Messpunkte liegen vor. Numerische
Konvergenz, unabhängige ODE-Gegenprobe, Lastkopplung, positive
Kern-Zyklusverluste und kausale Bursts sind überprüft. Hörabgleich,
RT-Ratekonzept und C++/EEL2-Port bleiben nächste Schritte.
