# Entscheidungen und Entwicklungshistorie

## D01 — Eigener Green Stripe

Anfangs gewünschte Rev.-A-/Blue-Stripe-Nähe, anschließend eigene Green-Stripe-
Gestaltung, zuletzt ausdrückliche Korrektur: **Revision A oder D egal**.
Die jetzige Implementierung ist deshalb eine eigene, dokumentierte Adaption.
Quellen behalten ihre tatsächliche Revision, Pluginname verspricht keine.

## D02 — Gemeinsamer, frameworkfreier Kern

C++11 und EEL2 mit identischen mathematischen Operationen. Kein JUCE/WebView-
Runtime für Dwarf; nur C-ABI-Deskriptoren/float Ports. ysfx als unabhängiger
Testhost, nicht als Runtime-Abhängigkeit. 134 Audiofälle tatsächlich verglichen.

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

Unabhängige L/R-Controller plus gemeinsamer Betrags-Max-Controller warmhalten.
Link-Crossfade in Gain-Domäne; kein L+R-Detektor. Mehr CPU als ein einzelner
Controller, dafür gleichmäßige Umschaltung. Keine elektrische 1176-SA-Identität.

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
- Mögliche niedrigere CPU bei warmen Stereo-Reglern.
- Samplegenaue REAPER-Automation versus jetzige geglättete Blocksteuerung.
- Falls externe Parallelphasigkeit nötig: linearphasige oder zusätzliche
  Kompensationsvariante statt unerklärter Änderungen am jetzigen Bundle.
