# Entscheidungen und Entwicklungshistorie

## D13 — Refit-fähige Eingangstransformatoren, 0.4.0

Die instabile frühere xformer.lib ist als Laufzeitgrundlage verworfen.
Eigener partieller Jensen-Datenblattfit mit gemeinsamer Quelle/Last,
Flussverkettung und positivem Stop-Gedächtnis; Profile 60s warm, 80s
ausgewogen, 00s clean. `Symmetric` wird zur linearen technischen Referenz.
Bankrevision und Fit-/Importhashes in `data/transformers.json`, gemeinsamer
Generator und validierter Import statt eingebetteter handgepflegter Tabellen.
Keine Dateiladung im Audiothread; Refit bedeutet neuen Build/JSFX-Include-Stand.

Input vor Transformator, Dry davor, Colour unabhängig, Output hinter Detektor.
Modellwechsel über Eingang aus/ein, OS umfasst den Kern, PDC bleibt 0/3/4.
HF mit angepassten Polen statt ungeeigneter Base-rate-Tustin-Nullstelle;
Amplitude und bekannte Phasendifferenz ausdrücklich in `TRANSFORMER_RUNTIME.md`.

## D14 — MOD-GUI mit Hostwidgets und Asset-Vorlagen

Spaltfreie Paneele und Titel direkt auf Grün nach Benutzerwunsch. Alle Potis
nutzen `aluminium.png` als 65-Frame-Filmstrip, Bypass die zwei vertikalen Frames
von `toggle.png`, Status SVG zunächst 28×28 px. Mode ausdrücklich `mod-widget="switch"`
mit MOD-Klassen `on/off`. Nur der obere Rand ist Drag-Handle. Echter
MOD-Widget-/jQuery-UI-Browsertest statt bloßer Prüfung der HTML-Zeichenketten.

GUI-Nacharbeit auf Benutzerwunsch: Orange für die Colour-Beschriftung verworfen,
rechte Platte ohne Gruppentitel. GAIN/TIME mit vollhohen Sektionen, durchgehender
Trennlinie und identischem Schraubenabstand an den Modulecken. Die 20
Phillips-Kreuze haben feste individuelle Winkel; nur die Schlitze drehen sich,
die Beleuchtung der Köpfe bleibt oben links. Sechs kleine Wertefelder in
Dropdown-Grau, Bypass ohne gedruckte Beschriftung, Pilot-SVG zuletzt auf 44×44 px.
Leichte Schatten nach rechts unten auf Paneel, Modulkanten und Bedienelementen;
PNG-Vorschauen schließen den äußeren Schatten auf transparentem Rand mit ein.
Weitere Verdichtung: Transformer ohne Überschrift, ausgeschriebene Auswahltexte
mit „Transformer“. Fußbereich 12 px kürzer; LED und Bypass mit gemeinsamer
Mitte auf der Colour-Poti-Achse. Module und Fußzeile nutzen dasselbe 2:1:1-Raster,
gleich breite Plätze gleichen unterschiedliche LED-/Schalterbreiten aus.
ENGINE-Bedienung weiter vereinfacht: keine Überschriften für Mode, Oversampling
und Link. Mode zeigt `COMP_ON` / `COMP_OFF` im beweglichen Griff, gesteuert
durch die tatsächlichen MOD-Widgetklassen `on/off`. Die Auswahlfelder tragen
`No Oversampling` / `2x Oversampling` / `4x Oversampling` sowie `STEREO LINK` /
`DUAL MONO`; ihre numerische Zuordnung bleibt 0/1/2 bzw. 1/0.
GAIN/TIME ebenfalls ohne Gruppenüberschriften. Alle drei Potimodule verwenden
dasselbe Zeilenraster einschließlich reservierter unterer Dropdown-Zeile:
Input/Attack/Mix und Output/Release/Colour sind dadurch exakt höhengleich.

## D01 — Eigener Green Stripe

Anfangs gewünschte Rev.-A-/Blue-Stripe-Nähe, anschließend eigene Green-Stripe-
Gestaltung, zuletzt ausdrückliche Korrektur: **Revision A oder D egal**.
Die jetzige Implementierung ist deshalb eine eigene, dokumentierte Adaption.
Quellen behalten ihre tatsächliche Revision, Pluginname verspricht keine.

## D02 — Gemeinsamer, frameworkfreier Kern

C++11 und EEL2 mit identischen mathematischen Operationen. Kein JUCE/WebView-
Runtime für Dwarf; nur C-ABI-Deskriptoren/float Ports. ysfx als unabhängiger
Testhost, nicht als Runtime-Abhängigkeit. 0.1.0: 134 Audiofälle; 0.1.1: 152
mit zusätzlichen langen Übergängen tatsächlich verglichen.

## D03 — Implizite Feedback-Regelung

Abgriff nach nichtlinearem FET/Preamp, vor Output. Bounded Backward Euler statt
Base-rate-Einzelsampledelay. Analytische saubere Gain-Law-Ableitung plus
safeguarded Newton/Bisektion. Eine vollständige Schaltungs-ODE ist nicht
vorausgesetzt und nicht behauptet.

## D04 — 4× feste Rate

Gesamte Regelung und Färbung oversampled. Kurze Polyphasen-IIR-Kette; keine
variable Qualität in 0.1.0, damit Zustände/Latenz/Parität kontrollierbar bleiben.
Inputrate verändert interne Koeffizienten. 4 Frames nominale PDC ausdrücklich
nicht als linearphasiger exakter Delay beworben.

## D05 — Interner Mix/Bypass auf hoher Rate

Beide Wege teilen Resamplingphase, Dry vor Input. Vermeidet zusätzliches
IIR-Phasenproblem eines völlig ungefilterten Dryzweigs. Farbfilterphase verbleibt
Teil des Wetcharakters. Externer Dwarf-Parallelzweig erfordert eigenen Test.

## D06 — Link ein/aus

Ursprünglich L/R und gemeinsamer Betrags-Max-Controller warmgehalten.
Ab 0.1.1 nur aktive Controller, beim Umschalten Zustandsübernahme und temporäre
Gain-Crossfadeberechnung aller drei. Kein L+R-Detektor und keine elektrische
1176-SA-Identität. So entfällt unnötige dreifache Regelarbeit im stabilen Link.

## D07 — Meter nur JSFX

LV2 technisch nur Latency-Output; keine GR-/Level-Controloutputs oder GUI-Meter.
JSFX Peak/RMS/Hold/GR getrennt vom Core, atomare Block-Snapshots, GFX read-only.
Mono verarbeitet Input L auf beide Outputs; keine unbemerkte L/R-Summierung.

## D08 — Presets sind Startwerte

26 eigene Instrumentvarianten auf Grundlage zugänglicher Praxisquellen. Keine
universellen Input-/Outputwerte; Ziel-GR zum Abstimmen. `.rpl`-Bänke plus
eingebauter Selector, Custom nach manuellem Eingriff. Keine „garantierte“
Klanggleichheit mit originalen Clock-/T-Pad-Stellungen.

## D09 — NAM offline

Vier Capturemodelle analysiert, aber Rate/Settings/Bypass teilweise unbekannt.
Kein Kaskadieren oder Modellrate-Oversampling ohne Prüfung. Profile separat,
Hashes und Metadaten in Doku. Für kleinen gemeinsamen Runtimekern keine
WaveNet-/Eigen-/NAM-Loader-Abhängigkeit.

## D10 — Neue DSP-Referenzen

Paulllux' Divider/LN-Modell und Erläuterungen gelesen. Keine fremden
JUCE-/Transformer-/Pot-Tabellen importiert, weil eigener Kernel und
Referenzplugin-Kalibrierung eine klare Provenienz brauchen.
Schroeders tanh-Artikel führte zur präziseren gemeinsamen Padé-[7/6]-Funktion
inklusive analytischer Bias-Normalisierung. Kein Fast-Math/Float-Bit-Hack.

## D11 — Externe Praxistests, lokale Prüfungen trotzdem ausführen

Benutzer hat Dwarf/REAPER auf anderem Rechner. Hier native C++-/ABI-/Turtle-/
JSFX-Paritäts-/Grafik-/Presetprüfung. Cross-Build mit offizieller Arm-GNU-A9-
Toolchain, ursprüngliche glibc-2.17-libm-Symbolbindung; keine behauptete echte
Dwarf-Ausführung. MPB-Zweitbuild und Echtzeitlast im Übergabeauftrag.

## Noch zu entscheiden nach externen Ergebnissen

- Feinabstimmung hoher Ratio/Attack-/Releasebereiche anhand klarer Proben.
- Echte Farbkalibrierung gegen verifizierte NAM-Core-/Hardwaredaten.
- Weiter reduzierte Control-/LUT-Struktur nach Eichas, falls CPU nach den
  belegten 0.1.1-Optimierungen noch zu hoch ist; zuerst Zeitdaten/Fitting.
- Samplegenaue REAPER-Automation versus jetzige geglättete Blocksteuerung.
- Falls externe Parallelphasigkeit nötig: linearphasige oder zusätzliche
  Kompensationsvariante statt unerklärter Änderungen am jetzigen Bundle.

## D12 — CPU-Optimierung mit Dissertation-Abgleich, 0.1.1

Operationcounts zeigen 97 % Entladefälle, aber vorher exp/log-Zielauswertung
und dreifachen Stereo-Regler. Optimiert: gecachte Bias/Kniekonstanten, begrenzte
kubische Release-exp/log-Inkremente, Endpunktfastpaths, ausgerollte EEL2-
Resampler, letzte Subphase-Meter, Regler-Einrasten, aktive Controller und Parken.
Keine Oversamplingreduktion wegen bereits sichtbarer Alias-Kandidaten.

80 stationäre Burstfälle sind praktisch numerisch gleich; bewusste Änderungen
nur im Off-/Link-Startzustand, zusätzliche Übergangstests. Ein Feed-forward-
LUT-/Dreifiltermodell aus der Dissertation wäre eine weitere Kalibrierstufe,
nicht ungeprüft dieselbe Klangimplementierung. `CPU_ANALYSIS.md` erläutert
Messzahlen, Seitenbelege und Grenzen.
