# LUT-Referenz für die statische Kennlinie

Wegweiser, wie dieses Projekt an eine Lookup-Table (LUT) der statischen
1176-Kennlinie kommt. Grundlage: `sauce/PhD_Thesis_Felix_Eichas.pdf`
(Felix Eichas, PhD-Thesis; liegt unter `docs/sauce/`, Originalmaterial, nicht
im Versionsverzeichnis — `.gitignore` schließt `docs/sauce/*` aus).
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

## Vorstudie Route 3 (2026-10-04, ohne DSP-Änderung)

Der in Schritt 1 geforderte Genauigkeitsvergleich wurde **vor** jedem Eingriff
in den DSP durchgeführt, als offline Python-Analyse über den analytischen
Formeln aus `src/dsp/GreenStripe.hpp`. Ergebnis: **Route 3 in der
geschriebenen Form ist nicht umsetzbar.** `softClip()` ist ein tragfähiger
Kandidat, `fet()` nicht — es erreicht das Genauigkeitsziel erst bei einem
Tabellenvolumen, das für das Zielgerät absurd ist.

### `fet()` / `gs_fet()` als LUT — verworfen

**Messgrundlage.** Die Offline-Analyse bildet `fet()` in Python ab und wurde
gegen den echten C++-Originalkern (`src/dsp/GreenStripe.hpp`) abgeglichen:
4 000 zufällige Punkte über input ∈ [±10⁻⁴, ±10⁻⁰·⁵], charge ∈ [10⁻³, 10],
curvature ∈ [0, 0.32], **maximale relative Abweichung 0.0** (bit-exakt).
Fehler werden auf der **realen Trajektorie** des laufenden Processors
gemessen: 352 602 `fet()`-Aufrufe einer Testabtastung, input −6.0722…+7.3028,
charge 0…68.752, curvature 0.000579…0.319226.

#### Warum das Volumen kippt

`fet(input, charge, colour, all)` hängt von **drei kontinuierlichen Größen** ab,
denn alle vier Parameter werden pro Sample ausgewertet:

- **`charge`** ist eine Zustandsvariable des Ladungsregelkreises, keine
  Einstellung. Bei festem input überspannt sie den Ausgang um **99,89 %**
  (input = 1: fet(charge=0) = +1.001161 → fet(charge=1000) = +0.001121).
  Eigene Achse zwingend; logarithmisch über den Modellbereich
  1 + charge ∈ [1.0001, 1001] (Klemme in `GreenStripe.hpp`).
- **`curvature = colour · (0.24 + 0.08 · all)`** ist *eine* Achse, nicht zwei —
  `colour` und `all` werden intern zu einem einzigen Skalar kombiniert. Der
  Einfluss ist klein, aber größer als das Ziel: bei input = 5.0, charge = 0
  bewirkt `curvature` 0 → 0.32 eine relative Änderung von **0,929 %**, also
  rund 93-mal das 10⁻⁴-Ziel. Eigene Achse ebenfalls zwingend.
- **Vorzeichen**: `a = 1 + g·(1 ∓ polarity · curvature)` hängt vom
  Vorzeichen des Eingangs ab. `fet` ist deshalb **nicht ungerade**:
  |fet(−x) − (−fet(x))| erreicht bei x = 3.0 relative **0,342 %** — das
  34-fache des Ziels. Eine einzige per Vorzeichen gespiegelte Tabelle
  scheidet aus, es braucht zwei Polaritätstabellen (Faktor 2 im Speicher).

Eine Steigungs-Polstelle ist dabei **nicht** die Ursache: mit
`a ≥ 1 + 0.68·g > 0` und `b² ≥ 0` ist `b² + 4·a·|u|` im gesamten
Betriebsbereich positiv, `fet` ist dort glatt. Für `input → 0` geht `fet`
analytisch in `input · qBase/(1+g)` über, eine exakt lineare Nullregion.

#### Gemessene Konvergenz

Trilineare Interpolation, |input| logarithmisch [10⁻⁴, 8], 1+charge
logarithmisch [1.0001, 1001], curvature linear [0, 0.32], zwei
Polaritätstabellen:

| Gitter (nx × ng × nk) | Zellen | Speicher | max. rel. Abweichung |
|---|---:|---:|---:|
| 257 × 129 × 33 | 2 188 098 | 16,7 MiB | 6,06·10⁻⁴ |
| 513 × 257 × 33 | 8 701 506 | 66,4 MiB | 1,52·10⁻⁴ |
| **1025 × 513 × 33** | 34 704 450 | **264,8 MiB** | **3,79·10⁻⁵** |
| 1025 × 513 × 65 | 68 357 250 | 521,5 MiB | 3,79·10⁻⁵ |

Die Konvergenz ist sauber und reproduzierbar: Verdopplung der Auflösung
senkt den Fehler exakt um Faktor 4.00 (O(h²), wie lineare Interpolation
erwarten lässt) — 3,94·10⁻² → 9,77·10⁻³ → 2,43·10⁻³ → 6,06·10⁻⁴ →
1,52·10⁻⁴ → 3,79·10⁻⁵. Zwei unabhängige Implementierungen (reines Python
unter WSL, vektorisiert mit numpy) reproduzieren dieselben Werte.

Daraus folgt das eigentliche Problem: **das Genauigkeitsziel 10⁻⁴ ist erst
bei 264,8 MiB erreichbar**, und das allein für den positiven Eingangszweig —
zwei Tabellen zusammen. Eine praxistaugliche Größe von 16,7 MiB verfehlt das
Ziel um Faktor 6. Der Cortex-A35 des MOD Dwarf hat keinen Cache in dieser
Größenordnung; 264,8 MiB wären pro Sample reines Cache-Miss-Streaming und
würden den Zweck (CPU-Ersparnis) weit verfehlen.

Die curvature-Achse ist der einzige günstige Teil: 33 → 65 Knoten ändert den
Fehler **überhaupt nicht** (3,79·10⁻⁵ in beiden Fällen), weil die Wirkung
nahezu linear in `curvature` ist. Sie verdoppelt das Volumen also ohne
Genauigkeitsgewinn — die zweite Achse für `all` ist damit endgültig
ausgeschlossen.

Eine Verengung der Ladungsachse auf den beobachteten Bereich (0…68.75, 61 %
der Modellachse) würde `ng` von 513 auf rund 315 senken, ändert die Größenordnung
aber nicht — und wäre zudem eine **Modelländerung**: Bei anderer Stellkonfiguration
oder Material würde die Achse clipped. Nicht zulässig.

**Fazit:** `fet()` ist nicht mathematisch untabellierbar — eine 264,8-MiB-
Tabelle erfüllt das Ziel. Sie ist aber innerhalb des für das Zielgerät
sinnvollen Speicherbudgets **nicht darstellbar**. Eine Wiederaufnahme würde eine
neu begründete Achsenwahl *und* ein revidiertes Genauigkeitsziel erfordern.

### `softClip()` / `gs_soft()` als LUT — technisch tragfähig

Die gemeinsame Padé-[7/6]-Sättigung ist dagegen ein 1-D-Kandidat auf
logarithmischer Achse |x| ∈ [10⁻⁶, 5], weil sie die am häufigsten aufgerufene
Nichtlinearität im Sample-Pfad ist (≈ 5–6 Aufrufe je hochratigem Sample) und
somit zugleich den teuersten Anteil trägt.

| N | max. rel. Abweichung | Speicher |
|---:|---:|---:|
| 129 | 1,82·10⁻³ | 2 KiB |
| 257 | 4,54·10⁻⁴ | 4 KiB |
| 513 | 1,14·10⁻⁴ | 8 KiB |
| **1025** | **2,84·10⁻⁵** | 16 KiB |
| 2049 | 9,65·10⁻⁶ | 32 KiB |

Auch diese Abbildung ist gegen den C++-Originalkern abgeglichen (5 000
Punkte, max. relative Abweichung 0.0). N = 1025 erfüllt das Ziel 10⁻⁴ mit
rund 3,5× Reserve **bei 16 KiB** — drei Größenordnungen weniger Speicher als
die `fet()`-Variante, die dasselbe Ziel erreicht. Exakte Odd-Symmetry und
die exakte Sättigung ±1 für |arg| ≥ 5 bleiben erhalten; unterhalb der
kleinsten Stützstelle gilt analytisch `softClip(x) = x·R(x²)` mit `R(0) = 1`,
sodass der Nullpunkt exakt bleibt.

### Entscheidung

Die Umsetzung ist **bewusst zurückgestellt**. `docs/DECISIONS.md` D12 verlangt
für LUT-/Dreifilterstrukturen ohnehin **zuerst Zeitdaten/Fitting**, und laut
`AGENTS.md` darf die EEL2-Seite nur zusammen mit C++ und mit bestandenem
Paritätssatz geändert werden. Route 3 bleibt damit offen, aber nicht mehr
unbestimmt: als Kandidat ist nur noch `softClip()`/`gs_soft()` vorgesehen, mit
den oben gemessenen Tabellengrößen.

**Nicht geliefert:** Hörtest, CPU-Vorher/Nachher, `cpu_regression`, Geräte- oder
REAPER-Messung. Ohne diese bleibt jede LUT-Variante unbelegt. Vor einer
Umsetzung sind zu erbringen: die Messungen aus Abschnitt 6/7 dieses Dokuments,
ein belastbarer REAPER-Vergleich und der vollständige Paritätssatz.

## Empfohlene Reihenfolge

1. **Vor jeder LUT-Arbeit** die Zeitdaten aus `docs/CPU_ANALYSIS.md`
   Abschnitt 6/7 erheben (REAPER und Dwarf, 128/256er Blöcke). Ohne diesen
   Nachweis ist der beabsichtigte CPU-Gewinn eine Annahme.
2. Nur bei bestätigtem Engpass `softClip()`/`gs_soft()` nach der Vorstudie
   tabellieren — N = 1025, 1-D logarithmisch, beide Engines aus
   `tools/generate.py`, mit Genauigkeits- und Paritätsprüfung.
3. Route 1 als Referenzplot neben die eigene Kurve legen (Abweichung
   dokumentieren, nicht als Zielwert missbrauchen).
4. Route 2, sobald Gerätzugang besteht — ersetzt Route 1 als Referenz.
5. Ein `fet()`-LUT gilt nach der Vorstudie als **verworfen**; eine Wiederaufnahme
   bräuchte eine neu begründete Achsenwahl und ein revidiertes Ziel.

Alle Varianten: Quellen- und Herkunftsangaben pflegen, keine
Thesis-/Messdaten in Pakete, keine Hardwaregleichheits-Behauptungen.
