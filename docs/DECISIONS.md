# Entscheidungen und Entwicklungshistorie

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
