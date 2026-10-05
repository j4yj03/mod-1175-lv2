# CPU-Auswertung und Dissertation-Bezug — 0.1.1

## Ergänzung 0.4.0 — Transformator-Laufzeit, 2026-10-05

Die nachfolgenden 0.1.x/0.2.x-Werte bleiben historische Messungen. Für die neue
Stufe wurden echte C++- und EEL2-Läufe auf x86_64 ausgeführt, **keine neue
Dwarf- oder REAPER-Messung**. None überspringt die Transformatorrechnung;
gewählte Modelle rechnen kanalgetrennt, maximal 40 Solveriterationen, drei
OS-Koeffizientensätze vorab vorbereitet. Keine Allokation im Audiopfad.

Lokaler C++-Stereo-Lauf bei 48 kHz/OS Off: ungefähr **0,020 s/s mit None**,
**0,032–0,034 s/s** mit Modell, einschließlich bisherigem Kompressor.
Dies ist ein kurzer Durchsatzlauf, keine Peak-CPU-Abnahme.

ysfx `5c3452f…`, GCC 15.2, 48 kHz/128 Frames, 1 s Signal, Warmup plus
Median aus drei Läufen, Grafik nicht ausgeführt (`benchmark_jsfx`):

| Szenario | Mono s/s | Stereo Link s/s |
|---|---:|---:|
| None / OS Off | 0,0306 | 0,0451 |
| 60s / OS Off | 0,1009 | 0,1510 |
| 80s / OS Off | 0,0847 | 0,1518 |
| 00s / OS Off | 0,0840 | 0,1598 |
| 60s / OS 4x | 0,3157 | 0,5668 |

14 Stop-Zweige je Solverauswertung kosten in EEL2 deutlich mehr als im
optimierenden C++-Compiler. Diese Messung rechtfertigt keine konkrete
Cortex-A35-Auslastungsaussage. Neue Geräteprüfung mit Signal, 128/256 Frames,
mehreren Instanzen und xruns ist im `HANDOFF.md` priorisiert.

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
- **152 C++-/JSFX-Paritätsfälle** (0.1.1-Stand; der Stand 0.2.0 führt 232),
  damals zusätzlich lange Link-/Compression-/Enabled-/Colour-Wechsel.
  Größte float-Port-Abweichung weiter ~4,17×10⁻⁷ FS.
- Transitiontest: endliche Outputs, gemeinsamer GR nach Link-Anlauf,
  zero-GR im Off-Zustand, keine sprunghafte Gainumschaltung im Probe.
- Bestehende PluginDoctor-Deltas/Sinusproben reproduziert: alle bisherigen
  Kennlinien-/FFT-Abweichungen bleiben auf dem ursprünglichen Niveau.
- Analytische Release-Approximation mit Worst-case-Raten/Zeitwerten getestet.

## 5a. Ausgeführter Lauf 2026-10-04 (0.2.0, WSL)

Erstmals wurden in dieser Arbeitsumgebung die **bindenden** Gates tatsächlich
ausgeführt, statt sie aus früheren Läufen zu übernehmen. Nach dem
Wiederherstellen der Toolchain (siehe `docs/BUILD.md`, Abschnitt „WSL ohne
Root") und dem Klon des gepinnten ysfx-Standes `5c3452f…`:

| Prüfung | Ergebnis |
|---|---|
| `make test` (DSP, Übergänge, LV2-ABI, Generator, Bündel) | **PASS** |
| `build/parity-wsl/jsfx_parity` (Mono + Stereo) | **PASS — 232 Fälle, max = 0 FS** |
| JSFX-Selector / RPL-Bänke / Custom | **PASS — 52 Presets** |
| `tools/validate.py` | PASS, 36 Presets/Imports — **nur strukturell**, `rdflib` fehlt |

Damit ist der in `LUT_REFERENCE.md` und `AGENTS.md` geforderte Paritätssatz für
den aktuellen Stand erstmals belegt und **nicht** nur behauptet.

### CPU-Baselinemessung auf dieser Maschine

`make benchmark` (native C++, O3) und `benchmark_jsfx` (EEL2, 48 kHz, Block 128,
2 s, Warmup + 7 Läufe, Median). Rechenzeit pro Audiosekunde:

| Szenario | C++ ns/Frame | EEL2 s/s |
|---|---:|---:|
| Mono normal | 283,1 | 0,0270 |
| Mono clean | — | 0,0219 |
| Mono Colour only | — | 0,0197 |
| Mono Bypass | — | 0,0060 |
| Stereo Link normal | 367,9 | 0,0439 |
| Stereo Dual Mono | — | 0,0508 |
| Stereo Bypass | — | 0,0050 |

**Diese Werte sind nicht mit der Tabelle in Abschnitt 4 vergleichbar.** Sie
stammen von anderer CPU, anderem Compiler und anderem ysfx-Build als der
gepaarte 0.1.0/0.1.1-Lauf, und der Projektstand ist inzwischen 0.2.0. Sie sind
als **Baseline für künftige Paarvergleiche auf dieser Maschine** zu lesen, nicht
als Fortschrittsnachweis. Insbesondere folgt aus ihnen **keine** Aussage, dass
0.2.0 gegenüber 0.1.1 schneller geworden wäre.

Die Profilzähler (`profile_*`) sind hier durchweg 0, weil die Instrumentation
nur in der per `tools/profile_jsfx_copy.py` erzeugten Kopie existiert — das ist
das erwartete Verhalten und kein Fehlschlag.

**Damit nicht geliefert:** REAPER-Gesamt-CPU und Hörtest. **Inzwischen geliefert:**
Dwarf-CPU auf echtem Cortex-A35, siehe Abschnitt 5b. Die dort genannten
Einschränkungen (kein Eingangssignal, keine xruns) gelten weiterhin.

## 5b. Messung auf dem MOD Dwarf (2026-10-04)

Als Nächstes wurde der **echte Zielcodecortex-A35** gemessen. Vorbedingung war
ein funktionierender AArch64-Build.

### Gerät, Build, Vorbedingungen

| Angabe | Wert |
|---|---|
| Gerät | MOD Dwarf, OS **1.13.5.3315**, Kernel **6.1.15-rt7-moddwarf** |
| CPU | aarch64, Cortex-A35 (`CPU part: 0xd04`), 4 Kerne, 963 MB RAM |
| Audio | jackd, 48 000 Hz, `-p 128 -n 2`, ALSA `hw:DWARF` |
| LV2-Pfad | `LV2_PATH=/root/.lv2:/usr/lib/lv2` |
| Compiler | Arm GNU **9.2-2019.12**, `-O3 -mcpu=cortex-a35`, `-ffp-contract=off` |
| ABI | `check_abi.py --dwarf`: **PASS**, GLIBC-Floor **2.17**, nur `libm`/`libc` |
| Binary | `green-stripe-76.so`, 47 984 B, md5 `fba59e9bfb68c32d3d7dc1bf3d2b3f9b` |

Der Build ist ein **Dokumentierter Fallback**, nicht der offizielle
`moddwarf-new`-Weg (Docker-WSL-Integration war deaktiviert, siehe
`docs/BUILD.md`). Architektur allein ist kein Gerätetest — deshalb folgen zwei
echte Nachweise auf dem Gerät:

- `lv2info` lädt das Binary per `dlopen`: *Green Stripe 76 Stereo* mit 16 Ports,
  *Mono* mit 13 Ports, jeweils exit 0 und leere Fehlerausgabe. Kontrollprobe mit
  absichtlich falscher URI → exit 255, der Test ist also aussagekräftig.
- jackd mappt die `.so` als `r-xp`-Segment und führt sie als Plugin aus
  (`<green_stripe_76_stereo/in_l>` verkettet mit `capture_1`/`playback_1`).

Der Vorbehalt „still requires real firmware load test“ aus `check_abi.py` ist
damit für diesen Build ausgeräumt.

### Messverfahren

Der Plugin-Host läuft auf dem Dwarf **als Threads im jackd-Prozess**, nicht als
eigener Prozess. Die DSP-Last des Plugins steckt deshalb in jackds
`utime+stime`. Gemessen wurde:

- `CLK_TCK` per `os.sysconf("SC_CLK_TCK")` **gelesen** (100), nicht geraten.
- 40 Samples je 20 s, Abstand 0,5 s; berichtet werden Mittel, Median, Spitze.
- Pro Bedingung **ein vollständiger Gerätestart**. Ein `systemctl restart
  jack2.service` genügt nicht: die Hardware-Controlchain behält dann ihren
  Zustand. Erst der Vollstart übernimmt die Auswahl aus `/root/data/last.json`.
- Kontrolle je Bedingung: `.so` muss in `/proc/<jackd>/maps` stehen
  (`plugin_mapped`) und die Binär-md5 muss `fba59e9b…` sein.

Diese md5-Prüfung ist nicht Kosmetik: während der ersten Serie wurde die
vorhandene ältere Binary `c547a3eb` durch eine UI-Installation ersetzt. Die
Seriesmessung mit dieser md5 wurde daraufhin **verworfen** und mit dem
HEAD-Build wiederholt. Die Zahlen beider Serien stimmen innerhalb der
Streubreite überein.

### Ergebnisse

Last in Prozent **eines** A35-Kerns, jackd inklusive:

| Pedalboard | Block | Plugin gemappt | Mittel | Median | Spitze | Δ zur leeren Kette | je Instanz |
|---|---:|---|---:|---:|---:|---:|---:|
| `GS76x0` (leer) | 128 | nein | 10,91 % | 11,96 % | 13,96 % | — | — |
| `GS76x1` (1× Stereo) | 128 | ja | 24,66 % | 25,88 % | 27,91 % | **+13,75 %** | +13,75 % |
| `GS76x2` (2× Stereo) | 128 | ja | 37,66 % | 37,86 % | 39,87 % | **+26,75 %** | +13,37 % |
| `GS76x0` (leer) | 256 | nein | 7,57 % | 7,97 % | 9,97 % | — | — |
| `GS76x1` (1× Stereo) | 256 | ja | 19,98 % | 19,94 % | 21,93 % | **+12,41 %** | +12,41 % |
| `GS76x2` (2× Stereo) | 256 | ja | 32,59 % | 31,90 % | 33,90 % | +25,01 % | +12,51 % |

Weitere Datenpunkte aus der ersten Serie (ältere Binary, gleiche Quelle):
4 Instanzen bei 128 Frames ergaben +52,8 % → **+13,2 % je Instanz**.

**Kernaussage:** Eine Stereo-Instanz kostet rund **12,4–13,8 % eines Kerns**.
Das ist linear (13,75 / 13,37 / 13,2 für 1 / 2 / 4 Instanzen) und nahezu
unabhängig von der Blockgröße, wie es für eine Sample-für-Sample-Verarbeitung
mit fester 4×-Rate erwartbar ist. Auf den vier Kernen entspricht eine Instanz
etwa **3,4 % der Gesamtleistung**, vier Instenzen rund 13 %.

### Einschränkungen — ausdrücklich offen

- **Ohne Eingangssignal gemessen.** Die Kette war stumm. Der Kompressionsdetektor
  arbeitet damit auf nahezu null Pegel. Da Reglerdetektor, Filter, Resampler und
  `softClip` im Green Stripe 76 **pro Sample bedingungslog** laufen und nur die
  Werte vom Pegel abhängen, ist das für den Audiopfad ein brauchbarer Proxy —
  es ist aber **keine** Worst-Case-Aussage. Eine Messung mit Signal (z. B.
  mittels Tone-Generator im Pedalboard) steht aus.
- **Keine xruns erfasst.** Die Plugin-Host-API ist auf diesem Gerät defekt
  (Port 5555 nimmt Verbindungen an, beantwortet aber keine Anfrage; siehe
  unten). xrun-Zähler waren deshalb nicht abfragbar.
- **Kein Hörtest** und kein REAPER-Vergleich.
- Die Werte gelten für **diesen** Build mit `-O3 -mcpu=cortex-a35`. Andere
  Compiler Flags oder Optimierungsstufen ändern sie.

### Nebenbefund: die Plugin-Host-API ist auf diesem Gerät defekt

Unabhängig von der Messung fiel auf, dass `mod-host` **keinen eigenen Prozess**
hat und auf Port 5555 Verbindungen annimmt, ohne sie zu beantworten. Die
Oberfläche im Web-UI funktioniert, weil die Pedalboard-Auswahl über die
Hardware-Controlchain (`/dev/ttyS3`) läuft, nicht über die API. Für die
Messung war das nicht hinderlich, weil sich `last.json` plus Vollstart als
Steuerweg erwies. Für Werkzeuge, die auf `/api/host/cpu` und `/api/pedals/load`
setzen, ist das jedoch eine echte Einschränkung der Testumgebung.

### Konsequenz für die LUT-Frage

Damit liegt erstmals **echte Zielhardware-Daten** vor, und sie sprechen gegen
eine LUT als CPU-Maßnahme:

- Eine Stereo-Instanz mit rund 13 % Kernlast ist für ein Pedal mit vier Kernen
  unkritisch; selbst vier Instanzen bleiben bei etwa 13 % der Gesamtleistung.
- Die Last ist linear und wird nicht von einem einzelnen Hotspot dominiert.
- Die auf x86 gemessene Analyse zeigte bereits, dass eine `softClip`-Log-LUT
  **langsamer** ist als die analytische Form und eine Linear-LUT erst ab
  N=2049 die Genauigkeitsanforderung erfüllt — bei doppelter
  Tabellenspeichergröße und ohne Geschwindigkeitsgewinn
  (`docs/LUT_REFERENCE.md`, Route 3).

Eine LUT bleibt damit eine **Modell- und Rechenwegfrage**, keine
Notwendigkeit für die Echtzeitfähigkeit auf dem Zielgerät. Sie sollte nur
verfolgt werden, wenn die Genauigkeit des Feedback-Zweigs oder die
FärbungscharakteristikPriorität bekommt — nicht als CPU-Rettung.

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
- **Erledigt:** Dwarf-CPU für 128/256 Frames und 1/2/4 Instanzen, Abschnitt 5b.
  Ergebnis: rund 13 % eines Kerns je Stereo-Instanz, linear skalierend.
- **Offen:** xruns auf dem Dwarf. Die Plugin-Host-API antwortet auf diesem Gerät
  nicht; als nächstes eine andere Quelle prüfen (jackd/JACK-Logs, Alsa-Status
  der Karte, ALSA `hw:DWARF`-Status-API) statt `/api/host/cpu`.
- **Offen:** Dwarf-Messung mit Eingangssignal, z. B. Tone-Generator im
  Pedalboard vor der Stereo-Instanz. Ohne Signal ist der Detektor praktisch
  stumm; die Zahl 13 % ist eine untere Schranke, kein Worst Case.
- **Offen:** Hörtest auf dem Dwarf, insbesondere bei vier Instanzen.
- Falls Restlast zu hoch: LUT-/dreifilterbasierten Control-Kern nach Eichas
  **als kalibrierte weitere Modellstufe** entwickeln, mit unverändertem Colour-
  Audiopfad und klaren Transienten-/THD-/Aliasvergleichsgrenzen.
- Keine automatische 2×-Reduktion: starke Colour-/Fast-GR-Tests zeigten bereits
  Alias-Kandidaten; Qualität zuerst gegen höhere Offline-Rate prüfen.
- Die Dissertation unterstützt die Mess-/Fittingmethode, liefert aber weder
  fertige Koeffizienten noch einen Echtzeit-CPU-Nachweis für unser Gerät.
