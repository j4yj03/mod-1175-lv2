# Green Stripe 76

**Eigenständige FET-Kompressor-/Limiter-Adaption für MOD Dwarf und REAPER.**
Die Gestaltung ist bewusst **Green Stripe**. Das Projekt greift Funktionsprinzipien
der 1176-Familie auf, bildet aber keine bestimmte Revision verbindlich nach.

Aktuell **0.4.1**: hörbare Eingangstransformatorprofile **60s warm → 80s
ausgewogen → 00s clean**, dazu `None` und eine lineare `Symmetric`-Prüfreferenz.
C++ und JSFX nutzen dieselbe validierte, nachträglich neu fitbare Modellbank.
Details und Importweg: [DSP — Transformator-Laufzeit](docs/DSP.md).

Die drei LV2-Paneelbereiche schließen **spaltfrei** aneinander an. Der weiße
Produktname steht direkt auf dem grünen Feld. Aluminium-Filmstrip-Potis,
Bitmap-Bypass und auf 44 px skalierte SVG-Betriebslampe nutzen die
bereitgestellten Assets. Durchgehende GAIN/TIME-Trennung, individuell gedrehte
Phillips-Eckschrauben und dezente Schatten bei Licht von oben links geben dem
Paneel eine Rack-Optik. Die rechte Platte trägt keinen Gruppentitel; Colour
ist neutral beschriftet. Alle sechs Potiwerte stehen in kleinen hellgrauen
Rechtecken, der Bypass hat keinen aufgedruckten Text. Auch GAIN/TIME tragen
keine Gruppentitel; Input/Attack/Mix und Output/Release/Colour bilden jeweils
eine gemeinsame Potireihe.
`Mode` verwendet das MOD-Schalterwidget; das Paneel lässt sich am gesamten
sichtbaren Rahmenring (oben, seitlich, unten) sowie an der Fußzeilenplatte
verschieben, ohne die Reglerbedienung mitzuziehen.
38 Presets; 01–36 instrumentweise gruppiert, die zwei 2:1-Varianten angehängt.
Sechs Presets wählen ein Transformatorprofil.
Alle Factory-Recall-Wege setzen Oversampling auf Off.
Alle 38 Presets sind gegen Parameterdaten und Laufzeit geprüft.
**37 Piano Gentle 2:1** und **38 Stereo Bus Subtle 2:1** ergänzen die Bank;
Kick Weight/Snare Crack erhalten langsamere Attackwerte für mehr Anschlag.
Einzelbewertung und Messvergleich: [EXTERN — Presetbewertung](docs/EXTERN.md).
Für echte Audiointerface-Messungen: [MESSTECHNIK — Scarlett](docs/MESSTECHNIK.md),
mit Testton-/WAV-Erzeugung, Liveaufnahme und Frequenz-/Klirrauswertung.
Erste vollständige Transformator-Matrix am Gerät (Dwarf als digitale
Signalquelle, 2026-10-07): Sättigungsreihung 60s 5,53 % / 80s 2,15 % /
00s 0,11 % 20-Hz-Klirr gegen Bypass 0,005 %; Wiederholungsspreizung ≤ 0,01 dB.
Details: [PROJEKT](docs/PROJEKT.md), [MESSTECHNIK 1a/1b](docs/MESSTECHNIK.md).

Aus 0.2.0: auswählbares Oversampling (Off/2x/4x, Default Off) als separate
Qualitäts-/CPU-Auswahl; Off ist der CPU-günstige Referenzpfad. Im lokalen
ysfx-Vergleich etwa 42 % weniger Mono- und 50 % weniger Stereo-Link-Rechenzeit
gegenüber 0.1.0.

## Lieferumfang

- LV2 **Mono** und **Stereo** in einem Bundle; Stereo Link ein/aus.
- JSFX **Mono** und **Stereo** mit GR-, Peak-/RMS- und Hold-Anzeigen.
- 38 Instrument-Presets: eingebauter JSFX-Selektor, importierbare `.rpl`-Bänke
  und zusätzliche LV2-Factory-Presets.
- Frameworkfreier C++11-DSP und gleichwertiger EEL2-Kern, Off/2x/4x-Oversampling
  mit einblendungsgepufferter Umschaltung und Latenzmeldung (0/3/4 Frames).
- Build-, Paketierungs-, Test- und NAM-Inventarwerkzeuge.
- Deutsche Bedienungsanleitung und Übergabedokumentation für eine weitere Session.

## Schnellstart

### REAPER 7

1. `jsfx/` vollständig nach `REAPER-Ressourcenordner/Effects/GreenStripe76/`
   kopieren (REAPER: **Options → Show REAPER resource path**).
2. FX-Liste aktualisieren, **Green Stripe 76 Mono** oder **Stereo** hinzufügen.
3. `Instrument preset` wählen. **Input** auf die gewünschte GR einstellen,
   **Output** anschließend mit dem trockenen Signal pegelgleichen.
4. In der Stereo-Fassung `Stereo Link=On` für ein zusammenhängendes Stereo-Signal;
   `Off` für zwei unabhängig geregelte Kanäle.

Die Mono-JSFX verarbeitet **Input L** und gibt denselben Ausgang auf L/R aus.
REAPER hat hier weiterhin zwei Pins; das Mapping ist absichtlich dokumentiert.

### Native LV2-Entwicklung

```bash
make
make test
make install PREFIX="$HOME/.local"
```

Der native Build ist für den **Buildrechner**, nicht automatisch für den Dwarf.
Für Dwarf-Build und Installation: [BETRIEB — Build/Installation](docs/BETRIEB.md).

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [PROJEKT](docs/PROJEKT.md) | Verbindlicher Umfang, aktueller Stand, Prüfstand, Übergabeauftrag, Historie und Entscheidungen |
| [DSP](docs/DSP.md) | Signalfluss, Numerik, Färbung, Parameter/Ports, Transformator-Laufzeit, LUT-Grenzen |
| [BETRIEB](docs/BETRIEB.md) | Bedienung, Gain-Staging, Stereo/Mix, Build, Paketierung, Installation |
| [MESSTECHNIK](docs/MESSTECHNIK.md) | Tests und Prüfungen, Protokollvorlage, Dwarf-Lastmessung, Scarlett-Workflow und Archive |
| [PERFORMANCE](docs/PERFORMANCE.md) | Gemessene CPU-Hotspots, Optimierungen und Dissertation-Bezug |
| [EXTERN](docs/EXTERN.md) | PluginDoctor-/ReaJS-Auswertungen, GR-Analysen, Presetbewertung |
| [QUELLEN](docs/QUELLEN.md) | Quellenkatalog, Lizenzen, NAM-Profile, Literatur- und Simulationsforschung |
| [TODO](docs/TODO.md) | Offene Punkte und nächste Arbeit |
| [PRESETS](docs/PRESETS.md) | Generierte Presetwerte, musikalische Ziele und GR-Richtwerte |
| [AGENTS.md](AGENTS.md) | Anweisungen für die Weiterarbeit |

## Modellstatus

Dies ist ein **funktionsfähiges Gray-Box-Ausgangsmodell**, dessen Parameter teils
aus belegten Funktionsprinzipien, teils aus eigenen Abstimmungsentscheidungen
stammen. Thresholds, Knie, Transformerfärbung und Reglerinteraktionen sind **nicht
an einem konkreten Originalgerät kalibriert**. Die NAM-Profile sind zusätzliche
Offline-Referenzen und nicht Teil des Laufzeitplugins.

4×-Polyphasen-IIR-Filter halten die Verzögerung klein, sind aber nicht linearphasig.
Die gemeldeten vier Samples sind eine **nominale** Latenz; sie kompensieren keine
frequenzabhängige Gruppenlaufzeit vollständig. Der interne Mix und interne
Bypass führen beide Pfade durch dieselbe Resamplingkette.

Praxistests finden auf dem anderen Rechner statt: MOD Dwarf **1.13.5.3315**,
**aarch64**, Kernel **6.1.15-rt7-moddwarf** und **REAPER 7**.

## Lizenz und Originalmaterial

Eigener Code: [MIT](LICENSE). Der schmale LV2-ABI-Header enthält ISC-Hinweise.
Fremde Quellen und die Testhost-Lizenzen sind in `docs/QUELLEN.md` aufgeführt.
Die Originaldatei `../1176.js`, Dissertation und `.nam`-Profile werden nicht
überschrieben. Capture-Profile werden nicht mit ausgeliefert.
