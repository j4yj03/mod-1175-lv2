# LUT-Referenz für die statische Kennlinie

Wegweiser, wie dieses Projekt an eine Lookup-Table (LUT) der statischen
1176-Kennlinie kommt. Grundlage: `../PhD_Thesis_Felix_Eichas.pdf`
(Felix Eichas, PhD-Thesis; im Elternverzeichnis, Originalmaterial).
Stand: 0.2.0. Keine dieser Routen ist bisher umgesetzt.

## Was die Thesis selbst dokumentiert

- **Messprotokoll (S. 79):** statische Kennlinie pro Ratio-Stellung des
  Referenzgeräts gemessen. Eingangspegel **−80 bis 0 dB, logarithmisch
  verteilte Amplituden** (gute Auflösung im unteren Bereich). Die Kurve
  ist das Verhältnis **Ausgangsspannung / Eingangsspannung** je Pegel.
- **Verwendung (S. 79):** die Kurve wird als Lookup-Table mit **linearer
  Interpolation** im Digitalmodell genutzt; Pre-Gain vor und Post-Gain
  nach der Abbildung skalieren die Kurve.
- **Abbildung:** **Fig. 6.13 (S. 77)** zeigt die gemessenen statischen
  Kennlinien aller Ratio-Tasten des UREI 1176LN inkl. „ABI" (All Buttons
  In); Fig. 6.8 (S. 72) zeigt das berechnete/gemessene Gegenstück des
  Flatline-Compressors. Die **numerischen Tabellenwerte sind nicht
  abgedruckt** — sie liegen in der Implementierung des Autors, die nicht
  Teil der Thesis ist.

## Route 1 — Fig. 6.13 digitalisieren

1. PDF-Seite 77 in hoher Auflösung rendern (z. B. `pypdf`/`pdftoppm`).
2. Achsenkalibrierung und Kurvenzug pro Ratio in **WebPlotDigitizer**
   (oder vergleichbar) nachziehen; pro Kurve 60–120 Punkte sichern.
3. Punkte glätten, in dB→dB-Paare überführen, als CSV/JSON ablegen und
   monotone Lücken füllen.

Grenzen: Ablesungen sind auf die Strichstärke der Publikationsgrafik
begrenzt (typischer Fehler einige 0,1 dB); Rechte beachten — die
Abbildung ist Originalmaterial. Abgeleitete Zahlen **nicht** in
Distributionspakete legen; Herkunft in `docs/SOURCES.md` eintragen
(Autor, Seite, Figur, Digitalisierdatum). Nicht als „verifizierte
Hardwarekalibrierung" ausgeben.

## Route 2 — Eigenmessung nach Thesis-Protokoll

Der gray-box-konforme Weg, wenn ein physisches 1176 (oder eine seriöse
Referenz) verfügbar ist:

1. Sinusbursts auf logarithmisch gestuften Pegeln von −80 bis 0 dBFS
   erzeugen (Stimulus-Material kann mit `tools/make_probes.py` bzw.
   dem Measurement-Probe erweitert werden).
2. Je Ratio-Stellung (4:1, 8:1, 12:1, 20:1, All Buttons) und Pegel den
   stationären Ausgangspegel messen; LUT-Paar = 20·log10(out/in).
3. Pegelstufung und Interpolation wie in der Thesis (log-Stufung,
   lineare Interpolation), Pre-/Post-Gain-Taps vorsehen.

Ergebnis ist eine **eigene** Kalibrierreferenz mit dokumentierter
Herkunft (Gerät, Seriennummer, Interface, Datum, Temperatur); gemäß
AGENTS.md bleibt Hardwarekalibrierung eigenständige Arbeit.

## Route 3 — LUT aus dem eigenen Modell (CPU-Hebel)

Die analytische Kennlinie des eigenen Kerns (FET-Teiler `fet()`/`gs_fet`,
zusammen mit dem Feedback-Regler) offline tabellieren:

1. Tabellenerzeugung im **Generierungsschritt** (`tools/generate.py`
   aus `data/model.json`): identische Tabellen in
   `src/dsp/ModelConstants.hpp` **und** `jsfx/GreenStripe76-Model.jsfx-inc`
   ausgeben — eine Quelle, zwei Konsumenten, bitgleiche Werte.
2. Im Sample-Pfad Tabellenzugriff mit linearer Interpolation statt
   Wurzel/Polynomen; Speicherung mit logarithmischer Achse, wie in der
   Thesis. Stufe `data/model.json` hochzählen.
3. **Paritätsdisziplin:** beide Engines müssen dieselben Werte und
   dieselbe Interpolations-Operationsreihenfolge nutzen
   (siehe bindende Regel in `docs/TESTING.md`); vollständigen
   Paritätssatz (232 Fälle, max=0 FS), Vorher/Nachher
   (`cpu_regression`) und Übergangstests laufen lassen.

Motiv: der Colour-Pfad ist der CPU-dominante Anteil (gemessen 2,1×
gegenüber Colour 0, siehe `docs/STATUS.md`); eine Kennlinien-LUT ist der
wirksamste strukturierende Eingriff, ohne das Modell zu ändern. Vor der
Tabellierung Genauigkeit gegen die analytische Form quantifizieren
(Ziel ≤ 10⁻⁴ relative Abweichung der Gainkurve; Hörtest im Befund).

## Empfohlene Reihenfolge

1. Route 3 zuerst (kein Hardwarezugriff nötig, messbarer CPU-Gewinn,
   vollständige Testabdeckung im Haus).
2. Route 1 als Referenzplot neben die eigene Kurve legen (Abweichung
   dokumentieren, nicht als Zielwert missbrauchen).
3. Route 2, sobald Gerätzugang besteht — ersetzt Route 1 als Referenz.

Alle Varianten: Quellen- und Herkunftsangaben pflegen, keine
Thesis-/Messdaten in Pakete, keine Hardwaregleichheits-Behauptungen.
