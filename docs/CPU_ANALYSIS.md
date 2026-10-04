# CPU-Auswertung und Dissertation-Bezug — 0.1.1

## Ergebnis

Die CPU-Rückmeldung des Benutzers (etwa vierfacher Verbrauch gegenüber anderen
JSFX) war ein sinnvoller Anlass. Ein exakter Faktor gegenüber diesen nicht
benannten Vergleichsplugins lässt sich hier nicht verifizieren. Der eigene
**Vorher-/Nachher-Vergleich mit echter EEL2-Ausführung** ist dagegen gemessen.

Version 0.1.1 entfernt vermeidbare Rechenarbeit und behält die 4×-Verarbeitung
sowie die stationäre Feedback-/Färbungscharakteristik. Es wurde keine geringere
Antialiasingqualität hinter einem Optimierungslabel versteckt.

## 1. Tatsächliche Ursachen in 0.1.0

### Feste 4×-Verarbeitung

48 kHz Hostrate → 192 kHz DSP. Filter, Controller, Färbung und ursprünglich
auch viele Anzeigen-Gainumrechnungen laufen auf dieser Rate. Das ist gegenüber
einem einfachen 1×-Peakkompressor ein struktureller Mehrverbrauch.
4× alleine erklärt jedoch nicht jede beobachtete Differenz: Kennlinien,
Sample-Funktionsaufrufe, Memoryzugriffe und Anzahl Controller kommen hinzu.

### Impliziter Feedback-Solver

Aufladende Schritte können vier Intervallerweiterungen plus acht Newton-/
Bisektionsiterationen benötigen. Jede Zielauswertung berechnet den
FET-Divider, Preamp-Kennlinie, log und exp. Das ist deutlich aufwendiger als
ein LUT-Gaincomputer mit wenigen Einpolen.

Im instrumentierten Testsignal waren nur etwa **2,6 %** der High-rate-Schritte
aufladend; ungefähr **97,4 %** liefen im Entladezweig. Trotzdem berechnete
0.1.0 auch dort die ganze Ziel-Law in Chargeform, eine exponentielle
Releasefunktion und anschließend einen vollständigen GR-Logarithmus.

### Stereo immer dreifach

0.1.0 führte ständig L-, R- und Link-Controller aus, auch bei stabilen
Link=On/Off. Instrumentiert für 0,25 s × zwei Durchläufe:

| Modus | Controlleraufrufe | Targetaufrufe | Solveriterationen |
|---|---:|---:|---:|
| Mono vorher | 96000 | etwa 110352 | 9396 |
| Stereo Link vorher | **288000** | etwa 330243 | 27509 |

Diese Counts erklären Kosten, sind aber keine uninstrumentierte Zeitmessung.

### Bypass und Compression Off rechneten weiter

Regler waren warm gehalten, komplette Ziel-/Solverarbeit lief unsichtbar
weiter. Deshalb hatten Bypass und Colour only vorher fast denselben
CPU-Verbrauch wie aktive Kompression.

### EEL2-Resampler und unnötige Umrechnungen

- Pro Allpassstufe wiederholte RAM-Indexberechnung und Loop/Funktionsaufrufe.
- Dieselben Preamp-Bias-Werte/-Ableitungen mehrfach pro Solver-Target.
- Bei All exakt 1 wurde ein Tap gerechnet, das danach mit null multipliziert wurde.
- Bei Colour 0 wurden ungenutzte `softClip`-Stufen ausgewertet.
- GR-dB für Anzeigen wurde auf jeder der vier Subphasen berechnet, obwohl nur
  die letzte verwendet wurde; Mono berechnete das identische R-Meter erneut.
- Parameter wurden ewig gegen asymptotische Zielwerte geglättet, ohne
  numerisches Einrasten. Das verhindert stabile billige 0/1-Pfade.

Die Bildschirmgrafik selbst wurde im Benchmark nicht ausgeführt. Der Verbrauch
war damit kein Beleg, dass nur ein großes UI der Schuldige wäre.

## 2. Was die Eichas-Dissertation nahelegt

Lokale PDF: `../PhD_Thesis_Felix_Eichas.pdf`. Gedruckte Seite +15 = lokale PDF.
Relevante erneut gelesene Stellen:

| Seiten | Inhalt | Empfehlung für Green Stripe |
|---|---|---|
| 63–68 | Pegeldetektor, Gain-LUT, drei Einpolfilter, 14 Parameter; bewusst Feed-forward | Ein stark reduzierter Kern kann nützliches Kompressionsverhalten mit wenig Rechenaufwand approximieren. |
| 66–67 | Mehrfilter-Antwort reduziert gezeigten Hüllkurvenfehler von ~1 dB auf <0,1 dB | Zeitform messen und niedrigordentlich fitten, nicht nur nominelle Attack/Release-Zahlen übertragen. |
| 68–70 | Multi-Sine, Hüllkurvenfit, danach Musik-Wellenformfit | Referenz-/Training-/Validierungsdaten bewusst trennen. |
| 70–75 | Kennlinien-LUT, Koeffizienten aus Reglerflächen; Attack und Release gekoppelt | Parametermapping offline vorbereiten; keine großen Online-Optimierungen. |
| 76 | Drums deutlich schlechter als Guitar/Bass, ESR ~0,266 | Ein schlankes Modell ist kein automatischer Beweis für alle Instrumente/All-Slam. |
| 21–25 | ADAA mit 2× für Waveshaping und Gitarrenspektrum | Kein pauschaler Beleg, den vollständigen Kompressorkreis auf 2× zu reduzieren. |
| 132 | Interaktiver Echtzeit-/Hardwarevergleich als ausstehende Arbeit | Keine Dwarf-/REAPER-CPU-Benchmarkbehauptung aus dieser Arbeit ableiten. |

**Würde ich Änderungen vornehmen? Ja:** die vorhandene Implementierung sollte
zuerst elementare Verschwendung entfernen — diese Session setzt das um.
Wenn die gewünschte Rest-CPU damit noch nicht erreicht ist, wäre danach ein
**eigenständiger, gemessener LUT-/Mehrzeitkonstanten-Kern nach Eichas** sinnvoll.
Das ist aber eine Modelländerung mit möglicher anderer Transienten-/Slamantwort,
keine mathematisch kostenlose Optimierung.

Die Dissertation liefert keine fertige Koeffizienten-/LUT-Bank, die hier einfach
eingesetzt werden könnte. Rohdaten und zeitliche Referenzmessungen fehlen.
Aktuelle PluginDoctor-Rampen/Deltaantworten sind gut für Regression; sie ersetzen
keine vollständige Attack-/Releasefläche eines Zielgeräts.

## 3. In 0.1.1 umgesetzt

1. **Preamp-Bias und Ableitung zwischenspeichern**, nur bei Modeänderung erneuern.
   Ausgangsbias ist konstant und wird einmal vorbereitet.
2. **All-/Colour-Endpunkte spezialisieren:** bei All=1 keinen unbenutzten
   Audio-Tap berechnen; bei Colour=0 keine ungenutzte Färbungskennlinie;
   unterhalb des gecachten Knieeinsatzes unnötige log/exp-Auswertung überspringen.
3. **Zielentscheidung in dB:** im Entladefall keine exp()-Rückrechnung der
   gewünschten Charge. Gleiche monotone `q↔GR`-Entscheidung.
4. **Release-Polynomial statt exp pro Sample:** kleiner begrenzter Schritt
   nutzt `1-s+s²/2-s³/6`. Worst-case absoluter Koeffizientenfehler unter
   7×10⁻¹⁵ bei 8k/4×/50 ms. Es wird kein grober Float-Bit-Hack benutzt.
5. **GR-Releaseinkrement statt vollem log:** `log(1-z)` kubisch mit z≤0,000625,
   erneute exakte Referenz bei aufladenden Schritten. Fehler analytisch begrenzt
   und im Langzeit-/Burstvergleich gemessen.
6. **JSFX-Allpasszustände als skalare, ausgerollte Felder:** gleiche Koeffizienten,
   Rekursion und Phase, keine zusätzlichen/längeren Filter. C++-Template bleibt
   unverändert — dessen Schleifen optimiert der Compiler bereits.
7. **GR-Anzeigenumrechnung nur auf letzter Subphase**, Mono-R-Anzeige kopiert
   die L-Momentaufnahme statt identische Sample-Meter zweimal fortzuschreiben.
8. **Regler einrasten:** relative/absolute 10⁻¹²-Schwelle für Zielwerte;
   anschließend Glättungsarbeit überspringen.
9. **Nur aktive Controller:** Mono 1, Stereo Link 1, Dual Mono 2. Alle drei nur
   während Link-Crossfade. Zustände beim Umschalten übernehmen.
10. **Ausgeschaltete Regelung parken:** Compression Off / Enabled Off setzt
    unsichtbare Controller zurück. Im vollständigen Bypass nur Resamplingkette,
    Audiopfadzustände einmal zurücksetzen.

### Bewusst geändertes Übergangsverhalten

- Link On→Off: beide unabhängigen Regler starten mit dem bisherigen gemeinsamen
  Zustand. Off→On: gemeinsamer Regler startet mit dem stärker geregelten Kanal.
- Vollständiges Compression/Enabled Off entlädt nicht mehr einen unsichtbaren
  warmen Kompressor weiter, sondern parkt ihn. Wiedereinschalten wird über
  dieselbe 2-ms-Steuerung und die Attack des aktiven Reglers eingeblendet.
- Der IIR-Resampler bleibt beim Bypass aktiv: gemeldete Nominal-PDC und Dryphase
  ändern sich nicht.

Diese Übergänge sind ausdrücklich dokumentiert, stationäre Signalverläufe
bleiben praktisch numerisch gleich. Es wurde kein neues Instrumentpreset oder
Threshold-/Knie-/Färbungsfit versteckt vorgenommen.

## 4. Gemessener CPU-Vergleich

Quelle: [`CPU_BENCHMARK.json`](CPU_BENCHMARK.json) mit Sourcehashes.
Testhost: ysfx `5c3452fee62583aa3d1b7e877d0c758c4024af89`, x86_64/WSL.
48 kHz, Block 128, identische vordefinierte Pegel-/Multitonevektoren,
2 s Audiosignal, Warmup plus sieben Durchläufe, Median. Compile/GFX nicht gemessen.

Werte sind Rechenzeit pro Audiosekunde. **Nicht** REAPER-Gesamt-CPU-Prozente,
Dwarf-CPU oder universelle Kosten auf einem anderen Rechner.

| Variante / Szenario | vorher s/s | nachher s/s | weniger Zeit |
|---|---:|---:|---:|
| Mono normal | 0,1363 | 0,0787 | **42 %** |
| Mono All | 0,1232 | 0,0635 | **48 %** |
| Mono clean | 0,1119 | 0,0397 | **65 %** |
| Mono Colour only | 0,1302 | 0,0548 | **58 %** |
| Mono Bypass | 0,1275 | 0,0124 | **90 %** |
| Stereo Link normal | 0,2853 | 0,1432 | **50 %** |
| Stereo Link All | 0,2836 | 0,1202 | **58 %** |
| Stereo Link clean | 0,2645 | 0,0646 | **76 %** |
| Stereo Colour only | 0,3220 | 0,0983 | **69 %** |
| Stereo Bypass | 0,2870 | 0,0245 | **91 %** |
| Stereo Dual Mono | 0,2955 | 0,1580 | **47 %** |

Auf anderen Durchläufen schwanken die Werte; die Richtung und große Stereo/
Off-/Clean-Einsparung ist konsistent. Die Tabelle stammt aus dem abschließenden
gepaarten Lauf mit sieben Wiederholungen. Frühere fünfteilige Zwischenläufe
führten die Optimierung, gelten nicht als zusätzliche unabhängige Geräte-
Messungen. Profilcounts nach Änderung:

- Stereo Link: 96000 statt 288000 Controlleraufrufe im gleichen kurzen Probe.
- Dual Mono: 192000 statt 288000.
- Bypass/Colour only: 0 statt 96000/288000 Controlleraufrufe.
- Aufladende Solverarbeit normal Mono bleibt identisch; die Einsparung
  ist vor allem unnötige Auswertung und Laufzeitverwaltung.

## 5. Verifikation

- **80 stationäre Vorher/Nachher-Burstfälle**, 8/44,1/48/96 kHz,
  Mono/Stereo, alle Modes, Colour 0/100.
- Größte Audioabweichung etwa **7,1×10⁻¹⁴ FS**, größte GR-Abweichung etwa
  **2,4×10⁻¹¹ dB**. Der Vergleich benutzt die separat gesicherte 0.1.0-Fassung.
- **152 C++-/JSFX-Paritätsfälle**, jetzt zusätzlich lange Link-/Compression-/
  Enabled-/Colour-Wechsel. Größte float-Port-Abweichung weiter ~4,17×10⁻⁷ FS.
- Transitiontest: endliche Outputs, gemeinsamer GR nach Link-Anlauf,
  zero-GR im Off-Zustand, keine sprunghafte Gainumschaltung im Probe.
- Bestehende PluginDoctor-Deltas/Sinusproben reproduziert: alle bisherigen
  Kennlinien-/FFT-Abweichungen bleiben auf dem ursprünglichen Niveau.
- Analytische Release-Approximation mit Worst-case-Raten/Zeitwerten getestet.

## 6. Reproduktion

```bash
cmake -S tests -B build/parity -DYSFX_SOURCE_DIR=/absolute/pinned/ysfx
cmake --build build/parity
build/parity/benchmark_jsfx jsfx/GreenStripe76-Mono.jsfx jsfx/GreenStripe76-Stereo.jsfx 2 7
```

Für Profilcounts, **nicht zum CPU-Zeitvergleich**, separate Kopie erzeugen:

```bash
python3 tools/profile_jsfx_copy.py jsfx /absolute/empty/tmp-profile/jsfx
build/parity/benchmark_jsfx /absolute/tmp-profile/jsfx/GreenStripe76-Mono.jsfx \
  /absolute/tmp-profile/jsfx/GreenStripe76-Stereo.jsfx 0.25 1
```

Vorher-/Nachher-JSON zusammenführen:

```bash
python3 tools/compare_cpu.py before.json after.json \
  --before-source /absolute/previous/jsfx --after-source jsfx \
  --output docs/CPU_BENCHMARK.json
```

Regression gegen alten, unabhängig gesicherten C++-Kern:
`tests/cpu_regression.cpp` mit `GS76_REFERENCE_HEADER` kompilieren; das alte
Header/Include im separaten Verzeichnis lassen. Kein Test soll seine eigene
aktuelle Implementierung als „vorher“ vergleichen.

## 7. Weitere Empfehlungen

- CPUvergleich direkt in REAPER bei identischer Rate/Blockgröße, gleichem
  Track-/FX-Routing und GUIzustand wiederholen. Die anderen JSFX nennen und
  vergleichbare Qualität/Modelle einstellen.
- Dwarf Peak CPU/xruns für 128/256 und mehrere Instanzen messen.
- Falls Restlast zu hoch: LUT-/dreifilterbasierten Control-Kern nach Eichas
  **als kalibrierte weitere Modellstufe** entwickeln, mit unverändertem Colour-
  Audiopfad und klaren Transienten-/THD-/Aliasvergleichsgrenzen.
- Keine automatische 2×-Reduktion: starke Colour-/Fast-GR-Tests zeigten bereits
  Alias-Kandidaten; Qualität zuerst gegen höhere Offline-Rate prüfen.
- Die Dissertation unterstützt die Mess-/Fittingmethode, liefert aber weder
  fertige Koeffizienten noch einen Echtzeit-CPU-Nachweis für unser Gerät.
