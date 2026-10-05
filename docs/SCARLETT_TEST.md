# Testton und Messauswertung mit Scarlett 2i2 (1st Gen)

`tools/scarlett_test.py` erzeugt ein Messsignal, spielt es über ein ausgewähltes
Audiointerface ab, nimmt beide Eingänge gleichzeitig auf und analysiert einen
ausgewählten Rückkanal. Für die Scarlett 2i2 1st Gen sind **48 kHz und zwei
Kanäle** der Ausgangspunkt. Unterstützt sind außerdem 44,1 und 96 kHz.

Es gibt zwei Wege:

- **`run`**: direkte Wiedergabe/Aufnahme über PortAudio, z. B. Kabelschleife
  oder analoge Teststrecke mit MOD Dwarf dazwischen.
- **`generate` + `analyze`**: WAV in REAPER/anderem Host abspielen oder durch
  das Plugin rendern und die exportierte WAV danach auswerten.

Der Live-Weg führt das Signal nicht automatisch durch ein REAPER-Plugin.
Eine direkte Scarlett-Kabelschleife misst DAC, Kabel, Eingangsstufe und ADC.
Für die Pluginmessung muss das Plugin ausdrücklich im Host-/Dwarf-Signalweg liegen.

## 1. Verkabelung und feste Einstellungen

### Referenzmessung

```text
Scarlett Line Output 1 hinten ── 6,3-mm-Klinkenkabel ── Input 1 vorn (LINE)
```

Für Kanal 2 beide Kanaloptionen entsprechend wählen. Bei einer symmetrischen
Line-Verbindung ein TRS-Kabel nutzen. Die Eingangs-Klinkenbuchse verwenden,
nicht XLR-Mikrofonbetrieb. **INST aus/LINE**, **48 V aus**, **Direct Monitor aus**.
Direct Monitor würde das Rücksignal erneut auf den Ausgang geben und die
Messschleife verändern. Auch Host-/DAW-Eingangsmonitoring für diese Schleife
deaktivieren. Für `run` keine weitere App auf denselben Ausgängen spielen lassen.

Lautsprecher an den Messausgängen abziehen bzw. stummschalten. Zunächst mit
`--level -24` oder dem Default **−18 dBFS Peak** beginnen. Monitor-Regler und
Input-Gain so einstellen, dass ein deutlicher Rückpegel entsteht, ohne rote
Gain-Anzeige bzw. digitales Clipping. **Die Reglerstellungen zwischen
Referenz und Teststrecke nicht verändern** und im `--label` notieren.
Das Skript steuert keine Scarlett-Hardwarepotis, Phantomspannung oder Monitoring.

### Teststrecke

```text
Scarlett Out 1 → Dwarf/anderes Testgerät → Scarlett Input 1 (LINE)
```

Bei Dwarf die zusätzlich eingebauten Gates/Output-Kompressoren für den
Vergleich deaktivieren, Routing/Pegel und vollständige Pluginparameter notieren.
Für isolierte Transformator-/Colour-Kennlinien Compression Off und Mix 100 %;
für Gesamteffektmessung die gewünschten Einstellungen ausdrücklich festhalten.

## 2. Installation auf dem Audio-Rechner

Python **3.9 oder neuer**, dann im Projektordner:

```bash
python -m pip install -r tools/requirements-scarlett.txt
python tools/scarlett_test.py devices
```

Offline-Erzeugung/Auswertung benötigt NumPy und SoundFile; Live-Betrieb
zusätzlich sounddevice/PortAudio. Unter Linux gegebenenfalls das
Distributionspaket `libportaudio2` installieren. Unter Windows den passenden
Focusrite-Treiber für die erste Generation verwenden. Aus der Geräteliste
die Ein-/Ausgangs-IDs der Scarlett **unter derselben Host-API** wählen.
ASIO nur verwenden, wenn es in dieser sounddevice/PortAudio-Installation
tatsächlich verfügbar ist; alternativ die angebotene WASAPI-/MME-Schnittstelle.
Die Audiorate im Treiber/Host ebenfalls auf 48 kHz setzen.

Die IDs unten `4` und `5` sind **Beispiele** und müssen durch die Ausgabe von
`devices` ersetzt werden. Gerätenummern können sich nach Neustart ändern.
WSL ist nicht der Audio-Testrechner; das Skript nativ dort starten, wo die
Scarlett mit dem Treiber erreichbar ist.

## 3. Kurzer 1-kHz-Test

```bash
python tools/scarlett_test.py run --output test-results/scarlett-tone \
  --input-device 4 --output-device 5 \
  --input-channel 1 --output-channel 1 \
  --kind tone --frequency 1000 --level -18 --rate 48000 \
  --label "Scarlett 2i2 1st Gen; LINE; Gain min; Monitor markiert; direktes Kabel"
```

PowerShell: Befehl in **einer Zeile** eingeben oder deren Backtick-Zeilenfortsetzung
verwenden; die gezeigten `\` sind Bash-Syntax. Es wird sofort abgespielt.
Der Ausgabeordner muss neu sein; vorhandene Aufnahmen werden nicht ersetzt.

Standard: 0,75 s Einschwingen und 1 s Messfenster je Ton, 20-ms-Ein-/Ausblendung,
Ruhefenster sowie zwei unterschiedliche Synchronisations-Chirps am Anfang/Ende.
Das Programm beendet den Stream auch bei einem Abbruch. Beide Eingänge werden
gespeichert, nur der gewählte Ausgang spielt; der andere Ausgang bleibt digital still.

## 4. Frequenz- und Pegelreihe mit Referenz

```bash
python tools/scarlett_test.py run --output test-results/scarlett-reference \
  --input-device 4 --output-device 5 --kind all --level -18 \
  --settle 2 --measure 1 --label "Direktes Kabel, feste Reglerstellungen"

python tools/scarlett_test.py run --output test-results/scarlett-dwarf \
  --input-device 4 --output-device 5 --kind all --level -18 \
  --settle 2 --measure 1 --baseline test-results/scarlett-reference/results.json \
  --label "Dwarf 48k; GS76 0.4.1; Preset 37; Mix100; OS4x; Pegel dokumentiert"
```

Beide Messungen brauchen **identische Signaloptionen** und dieselben analogen
Reglerstellungen. Die Referenz wird anhand des Stimulus-Hashes geprüft.
Sie muss gültig sein und denselben Eingangskanal/dieselbe Rate verwenden.
Der Bericht zeigt zusätzlich `relative_gain_db`: gemessener Gain minus
Referenz-Gain. **Verzerrungswerte werden nicht subtrahiert.**

| `--kind` | Signal |
|---|---|
| `tone` | Einzelton, Default 1 kHz |
| `sweep` | Gestufte Sinusreihe 20/40/80/160/315/630/1000/2000/4000/8000/12000/16000/20000 Hz, soweit unter 0,45·Rate |
| `levels` | Einzelton bei `level−24`, `−18`, `−12`, `−6` und `level` dBFS Peak |
| `all` | Einzelton + Frequenzreihe + Pegelreihe, bei 48 kHz 19 Segmente |

Für starke Kompression/langen Release gegebenenfalls `--settle 5 --measure 2`.
Die Pegelreihe läuft von leise nach laut; vorherige Segmente können
gedächtnisbehaftete Prozessoren beeinflussen. Längeres Einschwingen hilft,
ersetzt aber keine gesonderte Transientenmessung. Zeiten bis 10 s je Abschnitt.

## 5. WAV im Host erzeugen/aufnehmen

```bash
python tools/scarlett_test.py generate --output test-results/reaper-plan \
  --kind all --level -18 --settle 2
```

`stimulus.wav` in REAPER importieren. Direktsignal und bearbeitete Spur mit
gleicher Rate, ohne Normalisierung und ohne entfernte Anfangs-/Endabschnitte
als PCM24 oder Float-WAV exportieren. Für eine externe Aufnahme den gesamten
Stimulus samt Markern und Ausklang aufnehmen. Dann:

```bash
python tools/scarlett_test.py analyze --session test-results/reaper-plan \
  --recording test-results/reaper-wet.wav --input-channel 1 \
  --report-dir test-results/reaper-analysis
```

Bei gleichem Plan können getrennte `--report-dir` für Referenz und Test benutzt
werden. Ein Referenzbericht darf nicht durch dieselbe Auswertung überschrieben
werden. Rate muss übereinstimmen; das Skript resampelt die Aufnahme nicht.
`--max-delay 2` erlaubt bis etwa 2 s Zeitversatz, maximal 10 s wählbar.

## 6. Dateien und Kennwerte

- `stimulus.wav`: PCM24, Mono; digital definierte Anregung.
- `plan.json`: Rate, Tonfrequenzen, Pegel, Messfenster, Marker, Hashes.
- `recording.wav`: bei Livebetrieb zweikanaliges Float-WAV.
- `recording.json`: Geräte-/Host-API-Daten, Kanalrouting, Nutzerlabel,
  Overflow-/Underflowstatus und Aufnahmesha256.
- `results.json`, `results.csv`, `REPORT.md`: maschinenlesbare und lesbare Ergebnisse.

Synchronisation über normierte FFT-Korrelation, auch bei invertierter Polarität.
Zwei Marker schätzen Offset und Taktabweichung; Fenster und erwartete
Tonfrequenz werden daran angepasst, **ohne die Messdaten zu interpolieren**.
Eine lokale Frequenzsuche mit Sinus-/Cosinusfit mindert FFT-Leckage bei
nicht kohärenter Interface-Aufnahme. Unzuverlässige Marker, falsche Rate,
abgeschnittene Aufnahmen und extreme Drift brechen mit Fehlermeldung ab.

Pro Segment: Peak/RMS dBFS, DC, Grundtonfrequenz/-pegel, digitaler Gain,
Harmonische H2…H10 bis 20 kHz/Nyquist, THD und THD+N.
**THD+N ist ungewichtetes Vollband-Residual** nach Entfernen von DC und
angepasstem Grundton; kein AES17-/A-bewerteter Herstellervergleich.
Wenn keine zweite Harmonische im Messband liegt, ist THD `null`/„—“, nicht 0 %.
Clippingsamples (≥0,999 FS) und PortAudio-Over-/Underflows markieren den Bericht
als ungültig; ein Exitcode 0 setzt gültige Messfenster voraus.

Der gemessene Gain bezieht sich auf digitale DAC-Anregung und ADC-Aufnahme.
Analogregler und Wandler liegen dazwischen. Auch die Laufzeit enthält Treiber,
Puffer und Wandler; sie ist **nicht allein Pluginlatenz**. THD/Noise enthalten
die gesamte Schleife. Kleine Unterschiede unterhalb des Eigenfehlers der
Scarlett sind damit nicht sauber einem Testgerät zuzuordnen.

**Keine interne GR-Ablesung:** gemessene analoge Pegelreduktion enthält Input,
Output, Mix, Transformer/Colour und die Interface-Pegel. Sie ist nicht gleich
der FET-Wet-GR, die die JSFX anzeigt.

### Optionale Volt-/dBu-Kalibrierung

Ohne eigene Kalibrierung werden keine nominalen Scarlett-Maximalpegel erfunden.
Für `analyze --adc-volts-per-fs K` zunächst einen 1-kHz-Sinus mit bekanntem
RMS-Wert **am ADC-Eingang** und festen Gainstellungen messen. Aus
`K = bekannte_Vrms / gemessene_digitale_Grundton_RMS` ergibt sich der Faktor.
Beispiel: 0,1 V RMS bei 0,05 digital RMS → `K=2`. Der Bericht ergänzt dann
`fundamental_vrms` und `20·log10(Vrms/0,775)` dBu. Die Kalibrierung gilt nur für
diesen Kanal und diese Eingangsverstärkung. Die Ausgangs-Voltzuordnung ist
separat am Ausgang zu messen.

## 7. Lokale Prüfungen und Geräteübergabe

```bash
python tests/test_scarlett_test.py
```

Zehn bestandene Offline-/Backendtests: bekannte Verstärkung, invertierte Polarität, Verzögerung bis 2 s,
120-ppm-Taktabweichung, 1-%-H2 mit DC, analytischer FIR-Frequenzgang,
fehlende/falsche/abgeschnittene/geclippte Aufnahme und Referenzvergleich.
Ein simulierter Audio-Backend prüft Kanalrouting, Streamfehler und Stop bei
Abbruch. **Kein echter Scarlett-Test wurde hier ausgeführt.**
Am Audio-Rechner mit direktem Kabel anfangen; Betriebssystem, Treiberversion,
Kabel, Reglerstellungen, Pluginparameter und sämtliche Ergebnisdateien
zusammen übergeben. Checkliste: `TEST_REPORT_TEMPLATE.md`.
