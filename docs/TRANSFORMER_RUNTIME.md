# Transformatorstufe und spätere Refits — 0.4.0

## Produktstatus

`transformer` wirkt ab **0.4.0** in LV2 und JSFX. Die drei eigenen Profile
stammen aus dem partiellen Jensen-JT-11P-1-Datenblattfit in
[`transformer/offline_fit/`](transformer/offline_fit/README.md). Die instabile
`xformer.lib` und deren frühere Knieformeln sind keine Laufzeitgrundlage.

| Portwert | Profil | Bedeutung |
|---:|---|---|
| 0 | None | exakter Durchgang ohne Transformatorrechnung |
| 1 | 60s | warm, frühe/weiche Tiefbasssättigung, Potenzgesetz p=3 |
| 2 | 80s | ausgewogen, mittlerer Headroom, Potenzgesetz p=5 |
| 3 | 00s | clean, größter Headroom, regularisierter Fröhlich-Kern |
| 4 | Symmetric | lineare lastgekoppelte Referenz, ohne nichtlinearen Strom oder Stop-Gedächtnis |

Alle Profile sind polaritätssymmetrisch. `Symmetric` ist eine technische
Vergleichsstufe, kein viertes historisches Modell und kein Port des alten
`GCSYMETRICAL`. Namen bezeichnen eigene Klangabstimmung, keine Revisionstreue.
Der Referenzfit trifft 18/20 zurückgehaltene Intervalle und 24/33 Trainingsintervalle.
Diese Restfehler werden durch den Runtime-Port nicht zu Hardwarekalibrierung.

Presetprüfung: 11/12 wählen 60s, 13/19/24 wählen 80s, 20 wählt 00s;
alle anderen None. Die gespeicherten Input-Gains treiben den Kern zusätzlich:
„00s clean“ bedeutet größeren Headroom, nicht garantiert geringe Sättigung.
Die 20-Hz-Anker gelten am Transformator-Eingang nach Input-Gain.
`08 Vocal Transformer` ist ein Quellen-Trickname und bleibt bewusst None.
Vollständige Einordnung: `PRESET_REVIEW.md`.

## Signalweg und Zustand

```text
Host → Off/2x/4x-Interpolation → Input Gain → Transformator
     → bisherige Colour-Eingangsstufe → FET/Feedback → Output/Färbung
     → Mix/Enabled → Decimation
```

- `Input` steuert auch die Transformatoraussteuerung. `Output` liegt hinter
  dem Feedback-Abgriff und verändert weder Transformator noch GR-Verlauf.
- Eigene Flussverkettung, RL-Relaxation, 14 Stop-Zweige und HF-Historien je Kanal.
  Stereo Link verbindet ausschließlich die Kompressorregelung.
- Compression Off lässt die Transformatorstufe aktiv. Colour 0 schaltet sie
  ebenfalls nicht ab. Für den vollständig sauberen Pfad `None` wählen.
- Mix 0 und Enabled Off liefern den bisherigen resamplingangepassten Drypfad.
  Im eingerasteten Bypass werden Audio-/Transformatorzustände zurückgesetzt.
- Modellwechsel: bisherigen Transformatoranteil über 2 ms auf den Eingang
  zurückblenden, Modellzustand bei Blend=0 zurücksetzen, neues Modell über
  2 ms einblenden. Schnelle weitere Auswahländerungen verfolgen das neueste
  Ziel ohne zusätzliche Pfade oder Allokationen. Änderungen sind blockinvariant.
- OS-Wechsel nutzt die vorhandene 2-ms-Aus-/Einblendung des Gesamtausgangs und
  setzt die Transformatorhistorien am stummen Umschaltpunkt zurück.
- Nominale Hostlatenz weiterhin **0/3/4 Frames**. Transformatorfilter besitzen
  frequenzabhängige Phase, keine zusätzliche reine Sampleverzögerung.

## Numerisches Modell

`src/dsp/Transformer.hpp` und `jsfx/GreenStripe76-TransformerCore.jsfx-inc`
implementieren dieselbe implizite Trapez-Zustandsform wie der unabhängige
Offlinekern. Quelle, Primär-/Sekundärwiderstände und Last sind gekoppelt.
Der skalare monotone Solver hat maximal **40 Newton-/Bisektionsschritte**.
Zustände werden erst nach der Lösung fortgeschrieben. Keine Audioallokationen,
Dateizugriffe oder offenen Konvergenzschleifen; Koeffizienten für alle vier
Profile und drei OS-Stufen werden bei Initialisierung vorbereitet.

Die 00s-Kennlinie wird oberhalb `0.98·flux_scale_vs` C1-stetig auf eine endliche
positive Hochfeldsteigung fortgesetzt. `high_field_l_ratio=0.0001` ist eine
offengelegte Modellannahme, kein identifizierter Materialwert. Der Stop-Clamp
ist Teil des Gedächtnismodells, kein Audio-Limiter.

Die festen `source_volts_per_fs` und `fixed_output_normalization` werden aus
dem Profilimport übernommen: nominell −18 dBFS Peak → +4 dBu Primärpegel bei
1 kHz in der Referenzbeschaltung. Die Normalisierung ist **fest**, keine
signalabhängige Auto-Makeup-Regelung und keine Kalibrierung des Dwarf-Interfaces.

### HF-Diskretisierung und Grenzen

Der analoge effektive Zweipol wird mit angepassten Polstellen diskretisiert.
Ein reeller minimalphasiger Zähler wird auf DC und `min(20 kHz, 0.4·fs_internal)`
abgeglichen. Die frühere rohe Tustin-Abbildung würde bei OS Off trotz oberhalb
Nyquist liegender Eckfrequenz eine Nullstelle bei Nyquist erzwingen.

Im tatsächlich gerenderten Vergleich bei 44,1/48/96/192 kHz und
1/5/10/15/20 kHz beträgt der größte Amplitudenfehler **0,3081 dB**.
Die größte Phasendifferenz zum analogen HF-Surrogat beträgt **67,91°**:
Amplitudenanpassung ist keine analoge Phasengleichheit, besonders nahe Nyquist.
Für strengere Phasenziele sind höhere interne Rate oder eine erneute gemeinsame
Amplituden-/Phasenanpassung nötig. OS Off ist kein aliasfreier Betrieb; der
Transformator folgt der gewählten OS-Stufe, keine versteckte feste Hochrate.

## Refit-Vertrag

`data/model.json` verweist über `transformer_bank` auf **`data/transformers.json`**.
Diese Datei ist die normative, versionierte Bank. `schema_version=1`, eigene
`revision`, SHA256 des importierten `profiles.json` und des zugrunde liegenden
Fits halten die Herkunft fest. `tools/generate.py` erzeugt daraus:

- `src/dsp/TransformerModels.hpp`
- `jsfx/GreenStripe76-Transformers.jsfx-inc`

Keine JSON-Datei wird vom Audiothread geladen. Ein Refit ist ein neuer Build
bzw. ein neuer JSFX-Include-Stand. Bestehende Projekte speichern weiterhin die
Profilnummer: Austausch der Bank ändert deshalb den Klang bestehender Projekte.
Für reproduzierbare Projekte alten Build/JSFX-Ordner und Bankrevision aufheben.

### Ablauf

1. Ziele, Quelle/Last, Pegelbezug und zurückgehaltene Bedingungen im Offlinefit
   dokumentieren; Werkzeuge in `transformer/offline_fit/BERICHT.md` verwenden.
2. `fit.py`, `create_profiles.py` und Offlinevalidierung ausführen. Ein neuer
   `profiles.json` muss dieselben physikalischen Parameternamen enthalten.
3. Bank importieren, beispielsweise:

   ```bash
   python3 tools/transformer_model.py \
     --import-profiles docs/transformer/offline_fit/profiles.json \
     --revision gs76-input-2026-10-05-v1
   python3 tools/generate.py
   make test
   make check-generated
   ```

   Mit `--output /pfad/kandidat.json` zuerst einen Kandidaten schreiben.
   Validierung erfolgt vor dem Schreiben: endliche Werte, positive elektrische
   Größen, sichere Bereiche und unterstützte Modellfamilien. Unbekannte Felder,
   generalisierte rationale Exponenten, zusätzliche nichtlineare Serienzweige
   oder geänderte Stop-Schwellen werden ausdrücklich abgelehnt.
4. C++/EEL2-Parität und unabhängigen Referenzvergleich gemäß `TESTING.md`
   ausführen. Die 1-%-Abnahmeanker bei −14/−8/−2 dBFS sind aktuelle Klangziele;
   deren Änderung muss bewusst dokumentiert werden, nicht bloß Testgrenzen lockern.
5. Bankrevision/Produktversion und Testergebnisse aktualisieren; Geräte-CPU,
   Automation, Recall und pegelgleiches Hören auf dem Testrechner prüfen.

Es braucht keinen DSP-Umbau für neue Koeffizienten innerhalb dieses Vertrags.
Eine neue Topologie erfordert dagegen eine Schema-/Implementierungsänderung
in beiden Engines und eigene Signalprüfungen.

## Lokal tatsächlich geprüft

- Native Signal-/Stress-/Übergangsprüfung: 8…384 kHz, alle Profile/OS-Modi,
  Kanaltrennung, Gegenphase, Output/GR, Dry/Bypass und schwere Übersteuerung.
- 20-Hz-THD an den drei Ankern: **1,00009 / 1,00271 / 1,00001 %** bei 48 kHz;
  96/192 kHz ebenfalls innerhalb der definierten 0,85…1,15-%-Abnahmegrenze.
- Unabhängiger Offlinekern, Bass/DC-/Burstverläufe: maximale rohe
  Ausgangsabweichung **5,42×10⁻¹⁵ FS**, 44,1/48/96/192 kHz.
- **430** allgemeine C++/EEL2-Fälle plus **72 Preset-Signalvergleiche**,
  maximale Float-Port-Abweichung **0 FS**; **72** RPL-/Selector-Presetzustände.
- `None` gegen den unabhängig aus Commit `77a25fd` exportierten Kern:
  **144 Fälle bitgleich**, einschließlich Audio/GR/Latenz und Umschaltungen.
- Tatsächlich geladene LV2-Binary: optionale Portverbindung, hörwirksame
  Modellauswahl, In-place, nichtendliche Eingaben und blockinvariante Wechsel.

Aktuelle Dwarf-/REAPER-Geräteprüfung und Hörabnahme bleiben auf dem anderen
Rechner auszuführen. Frühere Geräte-CPU-Werte gelten nicht für die neue Stufe.
