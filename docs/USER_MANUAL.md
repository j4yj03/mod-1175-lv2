# Bedienungsanleitung — Green Stripe 76

## 1. Zweck und Charakter

Green Stripe 76 ist ein schneller, charaktervoller FET-Kompressor mit
Feedback-Regelung. Er kann Spitzen kontrollieren, Sustain verdichten, Drum-Räume
aufblasen und Signalen Verstärkerfärbung geben. Die Regler orientieren sich am
1176-Bedienprinzip; **das Klangmodell und die grünen Oberflächen sind eigenständig**.

Die Stellung **20:1** ist ein musikalischer Limiter-Modus. Es gibt keinen
Lookahead und keine garantierte True-Peak-/Brickwall-Begrenzung. All Buttons kann
Spitzen durchlassen, obwohl die anschließende GR groß ist.

## 2. Varianten wählen

| Variante | Ein-/Ausgang | Anwendung |
|---|---|---|
| LV2 Mono | 1 → 1 | Dwarf-Gitarre, Bass, einzelne Mikrofonspur |
| LV2 Stereo | 2 → 2 | Stereo-Effektkette oder zwei getrennte Kanäle |
| JSFX Mono | Input L → identischer Output L/R | Monoquelle in REAPER |
| JSFX Stereo | L/R → L/R | Stereoquelle, optional gekoppelte Regelung |

JSFX Mono summiert **nicht** L+R. Eine rein rechts eingespeiste Quelle muss im
REAPER-Pin-Mapping auf Input L gelegt werden. Für echte Stereosignale die
Stereo-Version verwenden. Kanäle oberhalb 1/2 werden von JSFX nicht bearbeitet.

### Stereo Link

- **On:** Ein gemeinsamer Regelverlauf reagiert auf den lauteren Betragspegel.
  L/R behalten denselben dynamischen Gain; gegenphasige Signale lösen weiterhin
  Kompression aus. Kanalabhängige Färbung kann trotzdem das Spektrum verändern.
- **Off:** Dual Mono — L/R regeln unabhängig. Beide verwenden dieselben
  Bedienparameter. Geeignet für zwei unabhängige Monoquellen; bei einem
  Stereo-Raumsignal kann die Balance hörbar wandern.
- Umschaltung und Regleränderungen werden intern über etwa 2 ms geglättet.
  Alle drei Reglerzustände bleiben während des Betriebs warm.

## 3. Regler

### Input — −36 bis +24 dB

Erhöht den Pegel vor Audiopfad und Regelung. Mehr Input verursacht mehr
Kompression **und** mehr Aussteuerung/Färbung. Es gibt keinen frei einstellbaren
Threshold-Regler. Ein höherer Ratio-Modus verschiebt zusätzlich den internen
Kompressionseinsatz; bei einem Ratio-Wechsel kann die GR daher zurückgehen.

Die Input-Zahlen sind **digitale Gain-dB**, keine originalen 1176-T-Pad-Skalen.
Alle Preset-Inputs sind Startwerte, nicht universelle Pegelvorgaben.

### Output — −36 bis +24 dB

Gleicht den Ausgangspegel aus und verändert die Aussteuerung der Ausgangsfärbung.
Der Detektor greift **davor** ab: Output verändert den GR-Verlauf nicht.
Es gibt keine automatische Makeup-Kompensation. Zu lautes Output kann im
nachfolgenden Signalweg clippen; es wird kein versteckter Ausgangslimiter benutzt.

### Attack — 1 bis 7

**1 = langsamer, 7 = schneller.** Die nominelle Zuordnung ist geometrisch:

\[
t_A = 800\,\mu s\,(20/800)^{(A-1)/6}.
\]

Auch Attack 1 ist schnell. Ein niedriger Wert erhält mehr Frontkante eines
Schlags oder einer Silbe. Ein hoher Wert glättet Peaks stärker und kann den
Klang nach hinten versetzen. Der effektive Verlauf hängt von Feedback, Pegel,
Ratio und All Buttons ab; die Zahl ist keine garantierte gemessene Anstiegszeit.

### Release — 1 bis 7

**1 = längere Erholung, 7 = kürzere Erholung.** Nominell:

\[
t_R = 1100\,ms\,(50/1100)^{(R-1)/6}.
\]

Nach langer/tiefer Kompression bleibt die Erholung länger. Release dem Rhythmus
anpassen: ein Drum-Schlag sollte vor dem nächsten sinnvoll zurückkehren, ohne
unbeabsichtigtes Pumpen. Auf Bass können sehr schnelle Zeiten absichtlich rau
werden, weil die Regelung Teile einzelner Schwingungen mitverfolgt.

### Ratio

- **4:1:** offener Ausgangspunkt, breiteres Knie.
- **8:1:** kräftigere Kontrolle für dynamische Quellen.
- **12:1 / 20:1:** hohe nominale Kompression für Peaks und Effektpfade.
- **All Buttons:** eigener Bias-/Kennlinien-/Dynamikzustand, wechselnder
  wirksamer Ratio-Bereich, anfänglicher Lag und zusätzliche Färbung.

Die Zahlen sind Ziel-/Nominalbezeichnungen. Tatsächliche Steigungen können
pegel- und zeitabhängig abweichen; siehe Prüfbericht. All ist nicht einfach eine
unendliche Ratio.

### Mix — 0 bis 100 %

- 100 %: vollständig bearbeiteter Pfad.
- 0 %: resamplingangepasster trockener Pfad **vor** Input/Output/Färbung.
- Dazwischen: lineare Mischung auf der hohen internen Rate.

Trocken und Wet teilen die Resamplingphase. Die zusätzliche Audiopfadfärbung
hat weiterhin ihre eigene Filterphase; `Mix` garantiert daher keinen Nulltest
gegen eine externe, unbearbeitete Parallelspur.

Für Dwarf-Parallelkompression den **internen Mix** bevorzugen. Eine separate
Pedalboard-Abzweigung kann wegen fehlender Host-Kompensation anders phasenliegen.

### Colour — 0 bis 100 %

Dosiert die Audiopfadfärbung: nichtlinearen FET-Anteil, DC-/Bandbegrenzung,
asymmetrische Verstärkerkennlinien und niederfrequente Sättigungszustände.
0 % ist der saubere Modellpfad; die eigentliche Feedback-Kompression bleibt
aktiv. Der Regler ist eine eigene Erweiterung und kein originaler Hardwareknopf.

### Compression

- **On:** dynamische FET-Regelung.
- **Off:** Audioverstärker-/Färbungspfad bleibt aktiv, dynamische Abschwächung
  ist aus. Input und Output können weiter Färbung erzeugen.

Der Controller läuft warm im Hintergrund, sodass Wiedereinschalten nicht wie ein
hart zurückgesetzter Kompressor startet. Das ist eine digitale Betriebsentscheidung.

### Enabled / Bypass

- `Enabled=On`: normaler Betrieb.
- `Enabled=Off`: interner, geglätteter Bypass auf den resamplingangepassten
  trockenen Pfad. Input und Output werden dabei umgangen.

Beim Dwarf bedient der normale Bypass-Schalter diesen `lv2:enabled`-Port.
REAPERs äußerer Host-Bypass ist eine andere Funktion: dessen Phase, Zustände und
PDC-Verhalten entscheidet REAPER. Für konsistente Vergleiche den **internen**
Enabled-Regler verwenden.

## 4. Anzeigen der JSFX-Fassung

Die LV2-Fassung hat absichtlich keine GR-/Level-Anzeige. JSFX zeigt:

- **IN:** Peak dBFS vor Input, RMS-Linie des Eingangs.
- **GR:** tatsächlicher dynamischer Regelgain in dB, vor Mix und Output.
  Ein kleiner Mixwert macht die angezeigte Wet-GR nicht kleiner.
- **OUT:** Peak dBFS, RMS-Linie und goldene Peak-Hold-Linie.
- **Rot:** Samplewert am Ausgang mindestens 0 dBFS; keine True-Peak-Messung.
- Peak-Abfall etwa 350 ms, RMS-Zustand etwa 300 ms, Hold etwa 800 ms.

RMS wird mathematisch als `20 log10(sqrt(mean(x²)))` dargestellt. Ein Sinus mit
0 dBFS **Peak** hat daher ungefähr **−3,01 dBFS RMS**. Es gibt keinen versteckten
AES17-Offset und keine LUFS-Anzeige.

REAPER 7 erhält zusätzlich `ext_gr_meter` als negative GR des vorherigen Blocks,
bei Dual Mono die stärkste Kanalabschwächung. Die Hostanzeige folgt nicht dem
Output-Makeup oder der Färbungs-Lautheit. Die Grafik liest Momentaufnahmen;
Öffnen/Schließen verändert den Audiokern nicht.

## 5. Erster Arbeitsablauf

1. Das richtige Mono-/Stereo-Routing wählen. Extrem heißen Eingangspegel vorher
   im Track-/Pedalboard-Signalweg reduzieren.
2. `01 Neutral Start` oder ein Instrument-Preset laden.
3. Input langsam erhöhen, bis typische Spitzen die gewünschte GR zeigen.
   Auf dem Dwarf nach Gehör und Pegelvergleich arbeiten.
4. Attack so einstellen, dass Frontkante und Körper zusammenpassen.
5. Release im Songtempo hören: atmet der Klang, bleibt er zu lange gedrückt,
   oder kehrt er zu hektisch zurück?
6. Output so einstellen, dass Enabled On/Off ähnlich laut wahrgenommen wird.
7. Erst danach Colour und gegebenenfalls Mix abstimmen.
8. Im vollständigen Mix vergleichen. Lauter klingt oft scheinbar besser;
   bei einem lauteren Preset zunächst Output reduzieren.

Die Beschreibung der NAM-Captures `~−21 dBFS = 0 dBu` ist lediglich eine
provisorische Referenz. Green Stripe setzt keine universelle Dwarf-/Interface-
Spannungskalibrierung voraus und verändert nicht automatisch Pegel danach.

## 6. Instrument-Workflows

### Vocals

`03 Vocal Natural` als Start: 4:1, langsamerer Attack, mittlerer/schnellerer
Release. 3–5 dB GR hält den Pegel zusammen, ohne Atem und Satzenden unnötig
aufzuziehen. Für Peaks `04 Vocal Peak Catch`; bei Rock `05 Vocal Rock Forward`.

Laut der Vocal-Praxisquelle kann man zu Lernzwecken absichtlich übertreiben:
Attack schnell, Release langsam und Input bis 12–15 dB GR. Danach Attack wieder
langsamer stellen und hören, wie Frontkante zurückkommt. Diese Übung ist kein
Standard-Preset für jede Stimme. All Buttons/7-7 ist ein ausdrücklicher Effekt.

### Bass

`07 Bass Finger Level` erhält den Körper; `08 Bass Pick Punch` bewahrt mehr
Anschlag. Bei Tieftonknattern Release verlängern oder Input/Colour reduzieren.
`09 Bass Fast Grit` nutzt diese Rauheit absichtlich. Unterschiedlich gespielte
Noten benötigen Input-Anpassung; kein Preset kann die Aufnahme ersetzen.

### Kick, Snare, Toms

Attack niedriger, um Frontkante zu erhalten; Release so wählen, dass zwischen
Schlägen Erholung möglich ist. `10 Kick Weight`, `11 Snare Crack`, `12 Toms Body`
sind Ausgangspunkte. Dual Mono ist für getrennte Quellen gedacht, nicht als
automatisch bessere Stereobehandlung.

### Overheads und Raum

Für natürlichere Overheads `13 Overheads Gentle`, Link On und kleine GR.
`14 Room All Buttons` ist ein starker Raum-Effekt. Für die gesamte Drumgruppe
`15 Drum Parallel Crush`: Input im Wet-Pfad kräftig, Output pegelgleichen,
Mix zunächst etwa 25 %. Transienten können trotz hoher GR herausragen.

### Elektrische und akustische Gitarre

`16 Guitar Clean Sustain` nach Amp/Cab ausprobieren. Bereits verzerrte Gitarren
haben oft wenig verbleibende Dynamik: `17 Guitar Rhythm Tight` zurückhaltend.
`18 Guitar Colour Only` nutzt nur den Audiopfad. Strumming/Fingerpicking erhalten
eigene Ausgangspunkte (`19`/`20`); Pickgeräusche und Raumrauschen kontrollieren.

### Piano, Rhodes, Synths und Bus

`21 Piano Gentle` bewusst vorsichtig; All Buttons ist hier selten ein neutraler
Start. Rhodes und Synth-Leads können mehr Körper bekommen. Synthbass braucht
auf langen tieffrequenten Noten ruhige Release. `26 Stereo Bus Subtle` ist ein
kreativer Bus-Preset, keine Mastering-Empfehlung.

## 7. Presets laden und speichern

### Eingebauter Selektor

`Instrument preset` lädt alle Klangregler einschließlich Enabled und Stereo Link.
Beim anschließenden manuellen Verändern wird die Auswahl auf **Custom** gesetzt.
Zum erneuten Laden zuerst Custom, dann denselben Preset wählen, falls die
Auswahlliste bereits dessen Namen zeigt. REAPER speichert die eigentlichen
Reglerwerte mit dem Projekt.

### REAPER-Presetbank

Die zwei `.rpl`-Dateien sind vollständig mitgeliefert. In REAPER im FX-Presetmenü
**Import preset library (.rpl)** wählen und die passende Mono-/Stereo-Datei
laden. Die Bänke wurden zusätzlich mit dem ysfx-RPL-Lader überprüft; REAPERs
Import und Projekt-Recall werden auf dem anderen Rechner abgenommen.

Eigene Ergebnisse unter neuen Namen speichern. Die eingebauten Presets sind
Ausgangspunkte, keine automatischen Instrument-Erkenner.

## 8. Fehlersuche

| Symptom | Prüfen |
|---|---|
| Mono-JSFX bleibt stumm | Quelle muss auf Input L liegen |
| Wenig GR | Input erhöhen, Compression/Enabled prüfen, Ratio-Einsatz beachten |
| Zu rau/knatternd | Input, Colour und schnelle Release reduzieren |
| Sterebild wandert | Stereo Link On; Routing und unterschiedliche Kanalquellen prüfen |
| GR groß, Effekt klein | Mix-Wet-Anteil prüfen; GR wird vor Mix angezeigt |
| Bypass nullt nicht mit roher Spur | IIR-Phase und nominelle, nicht exakte PDC |
| Preset wirkt anders als erwartet | Aufnahmepegel und Input/Output pegelgleichen |
| Dwarf lädt Plugin nicht | aarch64- und glibc/GLIBCXX-ABI, TTL und Bundlepfad prüfen |
| Geräte-CPU zu hoch | Andere Plugins isolieren, 256 Frames vergleichen, Prüfbericht erstellen |

Für reproduzierbare Tests siehe `TESTING.md`. Färbungs-/Hörabgleich mit einem
Originalgerät oder NAM-Core ist noch kein bestandener Teil dieser Anleitung.
