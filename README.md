# Green Stripe 76

**Eigenständige FET-Kompressor-/Limiter-Adaption für MOD Dwarf und REAPER.**
Die Gestaltung ist bewusst **Green Stripe**. Das Projekt greift Funktionsprinzipien
der 1176-Familie auf, bildet aber keine bestimmte Revision verbindlich nach.

Aktuell **0.4.0**: hörbare Eingangstransformatorprofile **60s warm → 80s
ausgewogen → 00s clean**, dazu `None` und eine lineare `Symmetric`-Prüfreferenz.
C++ und JSFX nutzen dieselbe validierte, nachträglich neu fitbare Modellbank.
Details und Importweg: [TRANSFORMER_RUNTIME](docs/TRANSFORMER_RUNTIME.md).

Die drei LV2-Paneelbereiche schließen **spaltfrei** aneinander an. Der weiße
Produktname steht direkt auf dem grünen Feld. Aluminium-Filmstrip-Potis,
Bitmap-Bypass und auf 28 px verkleinerte SVG-Betriebslampe nutzen die
bereitgestellten Assets. `Mode` verwendet das MOD-Schalterwidget; verschieben
lässt sich das Paneel am oberen Rand, ohne die Reglerbedienung mitzuziehen.
36 nach Instrument gruppierte Presets; sechs wählen ein Transformatorprofil.
Alle Factory-Recall-Wege setzen Oversampling auf Off.

Aus 0.2.0: auswählbares Oversampling (Off/2x/4x, Default Off) als separate
Qualitäts-/CPU-Auswahl; Off ist der CPU-günstige Referenzpfad. Im lokalen
ysfx-Vergleich etwa 42 % weniger Mono- und 50 % weniger Stereo-Link-Rechenzeit
gegenüber 0.1.0.

## Lieferumfang

- LV2 **Mono** und **Stereo** in einem Bundle; Stereo Link ein/aus.
- JSFX **Mono** und **Stereo** mit GR-, Peak-/RMS- und Hold-Anzeigen.
- 36 Instrument-Presets: eingebauter JSFX-Selektor, importierbare `.rpl`-Bänke
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
Für Dwarf-Build und Installation: [BUILD](docs/BUILD.md),
[INSTALLATION](docs/INSTALLATION.md).

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [USER_MANUAL](docs/USER_MANUAL.md) | Bedienung, Gain-Staging, Stereo, Mix und Instrument-Workflows |
| [PRESETS](docs/PRESETS.md) | Alle Presetwerte, musikalische Ziele und GR-Richtwerte |
| [REQUIREMENTS](docs/REQUIREMENTS.md) | Verbindlicher Umfang und Zielumgebung |
| [PARAMETERS](docs/PARAMETERS.md) | Parameter, Portindizes, Einheiten und Hostverhalten |
| [DSP_ARCHITECTURE](docs/DSP_ARCHITECTURE.md) | Signalfluss, Numerik, Färbung, Grenzen |
| [TRANSFORMER_RUNTIME](docs/TRANSFORMER_RUNTIME.md) | Laufzeitmodelle, Refit-Vertrag, Gain-/Rate-/Übergangspolitik |
| [CPU_ANALYSIS](docs/CPU_ANALYSIS.md) | Gemessene CPU-Hotspots, Optimierungen und Dissertation-Bezug |
| [BUILD](docs/BUILD.md) | Native/MPB-Builds, Cross-ABI, Paketierung |
| [INSTALLATION](docs/INSTALLATION.md) | Übergabe auf anderen Rechner, Dwarf und REAPER |
| [TESTING](docs/TESTING.md) | Offline-, Paritäts- und Praxistests |
| [PLUGIN_DOCTOR_EVALUATION](docs/PLUGIN_DOCTOR_EVALUATION.md) | Auswertung der sieben externen JSFX-/ReaJS-Versuche, Färbung und Alias-Prüfpunkte |
| [TEST_REPORT_TEMPLATE](docs/TEST_REPORT_TEMPLATE.md) | Ausfüllbares Protokoll für den anderen Agenten |
| [RESEARCH](docs/RESEARCH.md) | Auswertung der wissenschaftlichen und technischen Quellen |
| [NAM_PROFILES](docs/NAM_PROFILES.md) | Identität, Metadaten und Grenzen der lokalen Capture-Modelle |
| [SOURCES](docs/SOURCES.md) | Vollständiger Quellenkatalog mit Zugriffsstatus |
| [THIRD_PARTY](docs/THIRD_PARTY.md) | Codeherkunft, Lizenzen, Testhost-Versionen |
| [DECISIONS](docs/DECISIONS.md) | Technische Entscheidungen und Entwicklungshistorie |
| [STATUS](docs/STATUS.md) | Tatsächlicher Prüfstand, offene Punkte, nächste Arbeit |
| [HANDOFF](docs/HANDOFF.md) | Priorisierter Auftrag an den Agenten auf dem Testrechner |
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
Fremde Quellen und die Testhost-Lizenzen sind in `docs/THIRD_PARTY.md` aufgeführt.
Die Originaldatei `../1176.js`, Dissertation und `.nam`-Profile werden nicht
überschrieben. Capture-Profile werden nicht mit ausgeliefert.
