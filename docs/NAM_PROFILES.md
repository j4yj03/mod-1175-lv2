# Lokale NAM-Profile — Inventar und Verwendung

Pfad relativ zum Repository: `../UREI_Universal Audio 1176/`.
Werkzeug: `python3 tools/inspect_nam.py` (read-only; keine Inferenz/Änderungen).

## 1. Beschreibung der Quelle

`desc.txt` enthält:

```text
Clean 2-channel captures of the compressor tone; Stereo aligned
~-21dBFS=0dBu
UREI 1176 Rev A
```

Das sind mitgelieferte Aussagen, nicht unabhängig geprüfte Capturebedingungen.
Autor, Download-URL, Reglerstellung, GR-Bypass, Converterkalibrierung und Profil-
Lizenz fehlen. Nach letzter Benutzerkorrektur muss Green Stripe nicht genau
Rev. A nachbilden; die Profile bleiben nützliche Zusatzreferenzen.

## 2. Identität (ursprüngliche Bytes)

| Datei | Bytes | SHA256 |
|---|---:|---|
| 1176 A1 L.nam | 421560 | `1a3222861bcd17273e6c5fba9781bc261bed194f61bb5a85f61d1465c5b9c9ac` |
| 1176 A1 R.nam | 421608 | `a7ec47e455bd034d3307b9127764f6e1d98c0c08e45e8921abed0d5093b27bb4` |
| 1176 A2 L.nam | 297026 | `5557307b670db31a86aa45b4cc801f7501538a4339cb8e3653fa5320c42ec44d` |
| 1176 A2 R.nam | 296969 | `69dc7637d4833d4fef009d39094ecf58307d9083866320af715fcc12ce6a8a5d` |

## 3. Modelle

### A1

- Format 0.5.0, Architektur WaveNet.
- Keys: version, architecture, config, weights.
- Keine metadata und **keine sample_rate**.
- Zwei Arrays: 1→16/ch16/head8, dann 16→8/ch8/head1.
- Kernel 3, jeweils dilations 1/2/4/8/16/32/64/128/256/512.
- Tanh, ungated, globale zusätzliche Head null, head_scale 0.02.
- 13.802 Exportwerte je Datei, davon 13.801 Gewichte/Bias und eine Scale.
- Receptive field 4093 Samples, maximaler Lookback 4092.

Nur **unter ausdrücklich protokollierter 48-kHz-Annahme** entsprechen 4092
Samples 85,25 ms. Ein Plugin-Fallback auf 48 kHz ist keine nachgewiesene
Training-/Capture-Rate. L/R-Konfig identisch, Gewichte verschieden.

### A2

- Format 0.7.0, **SlimmableContainer**, sample_rate 48000.
- Top-level weights leer, zwei vollständige verschachtelte WaveNets.
- Small: max_value=0.5, 3 Kanäle, 1871 Exportwerte.
- Full: max_value=1.0, 8 Kanäle, 12146 Exportwerte.
- Je Kind 23 Layer, LeakyReLU 0.01, ungated, residual 1×1 aktiv, FiLM inaktiv.
- Kernelgrößen 6, außer zwei 15; Head kernel 16.
- Receptive field 6347 Samples, Lookback 6346 = 132,208 ms bei 48 kHz.
- A2 L head_scale 0.00619239345715992; R 0.006460437986258447.

„Slimmable“ ist ein Rechen-/Modellgrößenwähler, **kein Signalpegel-Crossover**.
Nach geprüftem NAM-Core: default Full, `SetSlimmableSize(0)` Small,
`SetSlimmableSize(1)` Full. Kindmodelle werden nicht miteinander kaskadiert.
Kleine Modelle können klanglich wesentlich abweichen und dürfen nicht still
als äquivalente Referenz benutzt werden.

Top metadata: UREI 1176 Rev A, studio-gear/outboard, date/loudness/gain.
Exportdatumsfelder 15.05.2026; `gain` in NAM ist eine normalisierte
Nichtlinearitätsheuristik, **kein Gain-dB-/Ratio-/GR-Messwert**.

Alle extrahierten Gewichte sind endlich. Kein eingebauter stereoseitiger
Regel-/Linkkanal: alle Profile sind mono. „Stereo aligned“ muss durch L/R-
Phase-/Laufzeitmessung bestätigt werden.

## 4. Gedächtnis ist nicht Latenz

Kausale WaveNets berechnen heutiges Output mit früheren Inputs. Receptive field
ist kein erzwungener Plugin-Delay. Es begrenzt aber, welche frühere
Programmhistorie unabhängig beeinflussen kann: beliebige Release-Historien über
eine Sekunde können diese endlichen Fenster nicht exakt behalten.

`gated=false/none` beschreibt eine neuronale Aktivierungsarchitektur, nicht
Hardware-GR-Bypass. Auch ein statisches Tone-Capture kann pegelabhängige Gain-
Änderungen enthalten; von Sättigung gegen dynamische Kompression unterscheiden.

## 5. Raten und Kalibrierung

Core meldet bei unbekannter Modellrate `−1`; offizieller Pluginwrapper nutzt
für ältere unbekannte Modelle 48 kHz. Die rohe Core-Renderfunktion übernimmt
bei unbekannter Rate die Input-WAV-Rate. Keines davon identifiziert A1s Rate.

Ein Capture darf nicht einfach im 192-kHz-Oversamplingloop abgespielt werden:
das ändert physische Gedächtnis-/Frequenzskalen. NAM stets in seiner expliziten
Modellraten-Domäne testen, gegebenenfalls korrekt resamplen.

`−21 dBFS=0 dBu` lässt Peak/RMS offen. Peakamplitude wäre 0,089125; reale
Volts-RMS-/Output-Kalibrierung ist damit nicht abschließend dokumentiert.
Nicht automatisch die NAM-Metadaten-Gain/Loudness auf Green Stripe übertragen.

## 6. Vorgehen auf dem Testrechner

1. Hashes vergleichen.
2. NAM-Core auf dokumentierter Revision bauen; Formate 0.5…0.7 unterstützen.
3. A2 Full zuerst bei 48 kHz rendern; Small getrennt kennzeichnen.
4. A1 mit expliziter 48-kHz-Annahme und anschließend gegebenenfalls alternative
   Rate beurteilen; Annahme im Bericht stehen lassen.
5. Nullsignal/DC, Kleinsignal-Frequenz/Phase, H2/H3/THD über Level, Polarität,
   IMD, kurzen/längeren Carrier-Burst testen.
6. Core-Output mit jeder selbst geschriebenen Inferenz vergleichen. Frühere
   NumPy-Exploration in dieser Recherche war **keine offizielle Core-Zertifizierung**.
7. Capture und GreenStripe Compression Off pegelgleichen, erst dann Färbung
   beurteilen. Ganzes Capture nicht ungeprüft hinter den Kompressor hängen.

Pinned API: `nam::get_dsp(path)`, `GetExpectedSampleRate()`, `Reset(rate,maxBlock)`,
`process(inputPointers,outputPointers,n)`. Core-CLI:

```bash
loadmodel "1176 A1 L.nam"
render --slim 1.0 "1176 A2 L.nam" "48k-probe.wav" "a2-full-output.wav"
render --slim 0.0 "1176 A2 L.nam" "48k-probe.wav" "a2-small-output.wav"
```

CLI-/API-Beleg: NAM-Core Commit
`0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842`, siehe Quellen.

## 7. Projektentscheidung

Kein NAM-Core im Dwarf-/JSFX-Laufzeitkern. Beide Formate behalten ein kompaktes
gemeinsames Modell. Ein späterer dokumentierter Färbungsfit ist möglich, wenn
Rate, Inferenz und Messbedingungen belastbar sind. Profil-Dateien werden weder
kopiert noch mit Distributionspaketen verschickt; der Testagent erhält sie
gegebenenfalls separat. MIT-Lizenz der NAM-Software ≠ Lizenz dieser Capturegewichte.
