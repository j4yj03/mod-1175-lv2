# Auftrag: Transformatorstufen nach den SPICE-Netzmodellen simulieren

Dieses Dokument ist die **vollständige Arbeitsanweisung für einen Folgeagenten**.
Ziel ist, die vier Stufen `60s`, `80s`, `00s` und `Symmetric` des Ports
`transformer` nicht mehr über eine skalare Sättigungskennlinie anzunähern,
sondern aus einer SPICE-Simulation der vorhandenen Netzmodelle abzuleiten.

Stand: Green Stripe 76, Version 0.3.0. Noch **nicht** ausgeführt.

## 0. Ausgangslage

Aktuell ist die Sättigung eine **skalare Kennlinie**, keine Netzsimulation. In
`src/dsp/GreenStripe.hpp` gilt:

```
φ_k = (C · ω / a)^(1/(n-1))          Knieschwelle der Stufe
u   = φ / φ_k                          normierter Fluss
u_knee = 1.0
```

Für `u > u_knee` greift eine weiche Sättigung, für `u ≤ u_knee` bleibt der Fluss
linear. Die Schwellen stammen aus den Koeffizienten in `docs/sauce/xformer.lib`:

| Stufe      | Kennung          | Aufbau         | `C`         | `a`         | `n` | `φ_k`    |
|------------|------------------|----------------|-------------|-------------|-----|----------|
| `60s`      | `GCOT-SE-01`     | single-ended   | `0.000709428` | `8792.792558` | `13` | `0.532` |
| `80s`      | `GCOT-PP-03`     | push-pull      | `0.012790087` | `11683.51058` | `6` | `0.337` |
| `00s`      | `GCOT-PP-04`     | push-pull      | `0.002610317` | `11434.182`  | `8` | `0.368` |
| `Symmetric`| `GCSYMETRICAL`   | push-pull      | `0.002`      | `1e-5`      | `25` | `1.761` |

`GCSYMETRICAL` trägt im Originalmodell den ausdrücklichen Hinweis
**„IMPORTANT: Only for testing purposes"**. Es ist **keine** Klangstufe und darf
nicht als Reziprokenstellung einer echten Revision verkauft werden. Es bleibt im
Port, weil die Presets ihn referenzieren, und wird ausschließlich als
Prüfreferenz simuliert.

Weitere Koeffizienten derselben Modelle: `R`, `b`, `m` (Kopplung), `Np`, `Ns`
(Primär-/Sekundärwindungen). Vollständige Tabellen in `docs/SOURCES.md`,
Abschnitt „SPICE-Netzmodelle in `docs/sauce/`".

Nicht simuliert und nicht Gegenstand dieses Auftrags: Kompressorregelung, Var-
istor, TAPE-Färbung, Ausgangsstufe. Nur der Transformator.

## 1. Verbindliche Randbedingungen

- **Kein Echtzeitcode in diesem Schritt.** Ergebnis dieses Auftrags ist eine
  **gemessene Tabelle plus abgeleitete Koeffizienten**, kein C++-Patch. Der
  DSP-Umbau ist ein separater Auftrag mit eigener Paritätsprüfung.
- **Simulation offline.** ngspice oder LTspice headless. Kein Download von
  Modellen aus dem Netz, keine fremden Bauteilbibliotheken: die Modelle liegen
  bereits in `docs/sauce/xformer.lib`.
- **Referenzfrequenz 20 Hz bis 20 kHz**, Abtastrate der Simulation 48 kHz,
  damit das Ergebnis direkt zur internen Rate passt.
- **Kein veränderter Koeffizient.** `C`, `a`, `n`, `R`, `b`, `m`, `Np`, `Ns`
  sind Eingangsdaten. Wer sie anpasst, um das Ergebnis schöner zu machen,
  hat den Auftrag nicht erfüllt.
- **Herkunft trennen.** Jede Zahl in der Ergebnis-Tabelle muss aus der
  Simulation stammen und mit dem Dateinamen und der Netlist benannt sein.
  Alles, was interpretiert wird, wird als Interpretation gekennzeichnet.

## 2. Schritt für Schritt

### 2.1 Modelle prüfen

`docs/sauce/xformer.lib` lesen und für jede der vier Kennungen den
Übertragungsweg bestimmen:

- Eingangsseite, Ausgangsseite, Primär- und Sekundärwindungszahl
- Kopplungsart der drei Modelle (`single-ended` vs. `push-pull`) und der
  Kopplungsfaktor `m`
- Serien- und Parallelanteile aus `R` und `b`
- Quelle und Last, mit denen die Kennungen ursprünglich charakterisiert wurden

Notiere, ob die Modelle eine **Übertrager**- oder eine **ZF-Übertragung**
beschreiben. Das entscheidet, ob ein Transformator- oder ein
Übertragungsmodell gebaut wird. Bei Zweifeln: beide Varianten simulieren und
im Ergebnisbericht nebeneinander stehen, mit Begründung, welche passt.

### 2.2 Simulationsaufbau bauen

Für **jede** der vier Kennungen eine Netlist nach diesem Muster:

```
* Sinusquelle am Primär, ohmsche Last am Sekundär.
* Pegelreihe: -30 dBV ... 0 dBV ... +6 dBV in 3-dB-Schritten.
* Frequenzreihe: 20 Hz, 100 Hz, 1 kHz, 10 kHz, 20 kHz.
* Für push-pull beide Wicklungen symmetrisch anregen.
* Für single-ended den Mittelabgriff (falls vorhanden) mitführen.

.ac  dec 200 20 20k          * Übertragungsfunktion
.tran 0 40m 48k              * Einschwingen, danach auswerten
```

Für die Sättigung ist ein reiner Kleinsignal-`.ac`-Lauf **nicht ausreichend**,
weil die Sättigung genau das ist, was wir suchen. Er braucht ein großes
Eingangssignal. Deshalb:

- `.step` oder eine Schleife über die Pegelreihe, damit der Übergang sichtbar
  wird
- Je Pegel und Frequenz den **Frequenzgang der Übertragungsfunktion** und die
  **Wellenform** auswerten, nicht nur den RMS-Wert
- Aus dem Verhältnis Eingangs- zu Ausgangsamplitude die **Kompression** dieses
  Stufenübergangs bilden. Das ist die Größe, die unser Skalar `u` abbilden soll.

### 2.3 Messgrößen

Für jede Kennung und jeden Arbeitspunkt mindestens:

| Größe | Einheit | Wofür |
|---|---|---|
| Spannungsübertragung `|H|` | dB | Frequenzgang der Stufe |
| Phasendrehung | Grad | Gruppenlaufzeit, ob die Stufe im Passband dreht |
| Kompression `20·log10(1/M)` | dB | **Zielgröße für unser Knie** |
| 3. Harmonische `H3/H1` | dB | Klirrverzerrung im Passband |
| 5. Harmonische `H5/H1` | dB | Klirrverzerrung im Passband |
| Differenzverzerrung `H3−H5` | dB | Weichheit des Knies |
| Gleichanteil der Ausgangsspannung | V | Einseitige Stufen können DC erzeugen |

Zusätzlich, **nur wenn** die Netlist es hergibt:

-_GROUPdelay`_ über die Frequenz
- Ausgangs-Spitzenpegel gegen Eingangs-Spitzenpegel, um Übersteuern sichtbar zu
  machen

Falls eine Größe im Modell nicht bestimmbar ist, wird sie als
**„nicht bestimmbar, Grund"** notiert und nicht geschätzt.

### 2.4 Auswertung

Ziel ist eine Tabelle, die die drei Skalarparameter je Stufe ersetzt oder
verifiziert:

| Parameter | heute | neu aus der Simulation |
|---|---|---|
| Knieschwelle `φ_k` | `(C·ω/a)^(1/(n-1))` | Frequenzabhängig? Wenn ja, als Kurve `φ_k(f)` |
| Kniebreite | implizit, `u_knee = 1.0` | Breite im dB-Maß, aus `H3` gegen Kompression |
| Sättigungstyp | ein skalares `tanh`-ähnliches Knie | Potenzzahl `n` je Stufe, falls die Kennlinie es hergibt |
| DC-Offset | keiner | aus der Messung, falls vorhanden |

**Prüffall.** Berechne aus den Simulationsdaten `φ_k` neu und vergleiche mit
dem Wert aus Schritt 0. Eine Abweichung unter 10 % gilt als Bestätigung des
bisherigen Ansatz und ist ein gültiges Ergebnis: *„Die skalare Näherung ist für
diese Stufe ausreichend."* Eine größere Abweichung ist das eigentliche
Ergebnis und gehört ausführlich beschrieben.

## 3. Zu liefernde Artefakte

1. `docs/sauce/sim/<Kennung>.cir` — die Netlist, eine Datei je Stufe
2. `docs/sauce/sim/<Kennung>-results.csv` — Rohmesswerte, im Kopf mit allen
   Betriebspunkten
3. `docs/sauce/sim/BERICHT.md` — Auswertung mit den Tabellen aus 2.3, dem
   Vergleich zu Schritt 0 und einer klaren Aussage je Stufe
4. Nächster Schritt-Abschnitt in `docs/DSP_ARCHITECTURE.md`: welchen
   Koeffizienten die Simulation liefert und was der DSP-Umbau daraus machen
   müsste
5. `docs/SOURCES.md`: die Simulation ist **keine externe Quelle**, sondern
   unsere eigene Rechnung. Sie wird als Rechenweg dokumentiert, nicht als
   Zitat. Modelldatei-Herkunft bleibt bei `docs/sauce/`.

## 4. Was dieser Auftrag ausdrücklich nicht liefert

- Keine Änderung an `src/dsp/GreenStripe.hpp` oder `jsfx/`
- Keine neuen Presetwerte
- Kein Hörtest und kein Test auf dem Dwarf
- **Keine Aussage über Klangrevisionen.** Eine simulierte Übertragungsfunktion
  sagt nichts darüber aus, wie sich eine reale 1176 des Originalherstellers
  anhört. Revisionszuordnung bleibt, wie in `docs/SOURCES.md` beschrieben,
  ausdrücklich offen.

## 5. Fertigkeitsprüfung

Der Auftrag gilt als erfüllt, wenn

- [ ] alle vier Netlists vorliegen und reproduzierbar laufen
- [ ] `BERICHT.md` je Stufe eine klare Aussage enthält: passt die skalare
      Näherung, oder nicht, und wenn nicht, warum
- [ ] jede Zahl auf eine Netlist und eine Messung zurückführbar ist
- [ ] Unsicherheiten und nicht bestimmbare Größen benannt, nicht geglättet sind
- [ ] keine Aussage getroffen wurde, die über eine Simulation hinausgeht
- [ ] der Rechenweg in `docs/SOURCES.md` als **eigener** gekennzeichnet ist