# Parameter, Ports und Persistenz

Normative Quelle: `data/parameters.json`. TTL und JSFX-Wrappers werden mit
`python3 tools/generate.py` erzeugt. Diese Tabelle beschreibt Version 0.3.0.
Gegenüber 0.1.1 kamen `oversampling` und `transformer` hinzu; die Indizes der
bestehenden Ports und die Plugin-URIs sind unverändert.

| Symbol | JSFX-Slider | Bereich | Default | Bedeutung |
|---|---:|---|---:|---|
| input | 1 | −36…+24 dB | 0 | Staging vor dem Feedback-Modell |
| output | 2 | −36…+24 dB | 0 | Gain vor Ausgangsfärbung, hinter Detektor |
| attack | 3 | 1…7 | 3 | 1 langsam, 7 schnell |
| release | 4 | 1…7 | 5 | 1 langsam, 7 schnell |
| ratio | 5 | 0…4, Enum | 0 | 4:1 / 8:1 / 12:1 / 20:1 / All |
| mix | 6 | 0…100 % | 100 | lineare, interne Dry/Wet-Mischung |
| colour | 7 | 0…100 % | 100 | eigene Audiopfad-Färbungsdosierung |
| compression | 8 | 0/1, Enum | 1 | dynamische Abschwächung aktiv (`COMP ON`/`COMP OFF`) |
| enabled | 9 | 0/1 | 1 | interner Bypass; LV2 designation enabled |
| stereo_link | 10 | 0/1 | 1 | Stereo: gemeinsamer Gain / Dual Mono |
| Instrument preset | 11 | 0…31 | 0 | JSFX-only: Custom oder Instrumentstartwert |
| oversampling | 12 | 0…2, Enum | 0 | Off / 2x / 4x; Qualitäts-/CPU-Wahl, **nicht** im Preset |
| transformer | 13 | 0…4, Enum | 0 | None / 60s / 80s / 00s / Symmetric; ohne Klangwirkung in 0.3.0 |

Alle Klangparameter außer Mode-Auswahl werden in abgeleiteter Form geglättet:
Gains linear, Zeiten in Sekunden, Threshold/Knie/Ratio linear. Die Mode-Auswahl
wird in Ratio/Threshold/Knie/All-Zielwerte übersetzt und diese geglättet.

### Unterschiedliche Preset-Semantik der angehängten Ports

`oversampling` und `transformer` sind beide `lv2_append` und beide
`connectionOptional`, ihre Preset-Semantik ist aber **absichtlich verschieden**:

| Port | Verhalten beim Recall | Begründung |
|---|---|---|
| `oversampling` | startet immer auf **Off** | Qualitäts-/CPU-Wahl, nicht Teil des Klangs; ein Recall darf nicht ungefragt 4x-Rechenzeit aktivieren |
| `transformer` | übernimmt den **Wert des Presets**, sonst `None` | Klangwahl; 3 von 31 Presets tragen eine Stufe |

Beide Pfade laufen in `tools/generate.py` durch `appended_value()`, deshalb
können LV2-TTL, JSFX-Selektor und RPL-Bänke nicht auseinanderlaufen.

## LV2-Portlayout

### Mono — 14 Ports

0 Audio In, 1 Audio Out; 2–10 die ersten neun Parameter in obiger Reihenfolge;
11 Nominal Latency (Output ControlPort, `notOnGUI`), 12 Oversampling,
13 Transformer. Kein Stereo-Link-Port.

### Stereo — 17 Ports

0 In L, 1 In R, 2 Out L, 3 Out R; 4–13 die zehn Parameter;
14 Nominal Latency (Output ControlPort, `notOnGUI`), 15 Oversampling,
16 Transformer.

| Variante | URI |
|---|---|
| Mono | `https://github.com/j4yj03/mod-1175-lv2#green-stripe-76-mono` |
| Stereo | `https://github.com/j4yj03/mod-1175-lv2#green-stripe-76-stereo` |

Der Host setzt normale ControlPorts, alle Presetwerte sind normale Ports.
Kein Atom-/Worker-/State-Extension-Sonderzustand ist erforderlich. Aktivierung
setzt DSP-Historien zurück, nicht die verbundenen Portadressen.

Die MOD-GUI-`lv2:index`-Werte beziehen sich auf **GUI-Reihenfolge**, nicht auf
DSP-Portnummern. `:bypass` ist ein Hostsymbol und kein LV2-Audio-/Control-Port.

## JSFX-Verhalten

Das vollständige Paket enthält zwei `.jsfx`, Core/Model/Presets/UI-Includes und
zwei `.rpl`-Bänke. Reglerwerte speichert REAPER normal im Projekt. Es wird kein
laufender GR-/Resamplerzustand serialisiert; reguläres `@init` setzt die Historie
zurück. Bei Abtastratenwechsel werden Rate und Koeffizienten aktualisiert.

Der eingebettete Selektor setzt bei Laden auch Enabled und Link. Danach führt
manuelles Verändern zu Custom. RPL-Bankwerte speichern Custom=0 und die
eigentlichen Klangeinstellungen, damit Projekt-Recall keine unerwartete
Preset-Neuanwendung auslöst.

Änderungen werden bei `@slider` und `@block` übernommen, intern geglättet.
**Keine samplegenaue `slider_next_chg`-Interpolation in 0.1.1**: die verfügbaren
Testhosts implementieren diese REAPER-Funktion nicht vollständig. Das darf in
der nächsten Session als ausdrückliche Erweiterung hinzugefügt werden.

## Latenz

Die Latenz folgt dem Oversampling: **0 / 3 / 4** Frames nominal für Off / 2x / 4x
(LV2 `lv2:latency`, JSFX `pdc_delay`, `pdc_bot_ch=0`, `pdc_top_ch=2`).
Off ist der CPU-günstige Referenzpfad mit 0 Frames. Die tatsächliche IIR-Gruppenlaufzeit ist
frequenzabhängig. Kein Anspruch auf sampleexaktes Nulling einer externen Spur.
