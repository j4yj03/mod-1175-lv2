# Instrument-Presets

> Alle Werte sind eigene Ausgangspunkte, keine Hardwaremessungen.
> Input bis zur gewünschten GR anpassen, Output anschließend pegelgleichen.
> Ziel-GR meint stets die dynamische FET-Abschwächung im Wet-Pfad vor Mix; keine Pegelgarantie für den gespeicherten Inputwert.
> Oversampling ist eine separate Qualitäts-/CPU-Auswahl (Default Off). JSFX-Selektor, importierte Factory-Bänke und LV2-Presets setzen Off.

> Ab 0.4.0 sind 60s/80s/00s hörbar: warm/früh, ausgewogen, clean. Die Zuordnung ist eigene Klangabstimmung; keine historische Revision.

> Der Transformator ist eine Klangwahl und wandert daher mit dem Preset. Er steht bei
> 6 von 38 Presets auf einer Stufe und sonst auf `None`.

Prüfung und Änderungsbegründung: [EXTERN.md (Abschnitt Presetbewertung)](EXTERN.md).
Ab 0.4.1: Attack in **21 Kick Weight** und **22 Snare Crack** korrigiert;
**37 Piano Gentle 2:1** und **38 Stereo Bus Subtle 2:1** als zusätzliche Varianten.
Die bisherigen Nummern bleiben erhalten. Input auf Ziel-GR einstellen und Output pegelgleichen.

| Preset | Instrument | Input / Output dB | Attack / Release | Ratio | Mix / Colour % | Link | Transformator | Ziel-GR |
|---|---|---|---|---|---|---|---|---|
| 01 Neutral Start | Allgemein | 0 / 0 | 3 / 5 | 4:1 | 100 / 100 | On | None | 2–5 dB |
| 02 Dr Pepper Inspired | Allgemein | 3 / -1 | 2.5 / 5.5 | 4:1 | 100 / 100 | On | None | 3–7 dB |
| 03 Vocal Natural | Stimme | 2 / 0 | 3 / 5 | 4:1 | 100 / 75 | On | None | 3–5 dB |
| 04 Vocal Peak Catch | Stimme | 4 / -1 | 5.5 / 6 | 8:1 | 100 / 85 | On | None | 3–7 dB auf Spitzen |
| 05 Vocal Rock Forward | Stimme | 7 / -3 | 6 / 6 | 8:1 | 100 / 100 | On | None | 5–10 dB |
| 06 Vocal Grit Parallel | Stimme | 10 / -6 | 6.5 / 7 | All Buttons | 30 / 100 | On | None | 10–18 dB im Wet-Pfad |
| 07 Vocal Squashed | Stimme | 6 / -3 | 7 / 7 | 4:1 | 100 / 100 | On | None | 7–10 dB |
| 08 Vocal Transformer | Stimme | 4 / 0 | 3 / 5 | Colour only | 100 / 100 | On | None | 0 dB, keine Kompression |
| 09 Guitar Clean Sustain | E-Gitarre | 3 / 0 | 2.8 / 5.8 | 4:1 | 80 / 90 | On | None | 3–6 dB |
| 10 Guitar Rhythm Tight | E-Gitarre | 1 / 0 | 3 / 4 | 4:1 | 80 / 75 | On | None | 1–4 dB |
| 11 Guitar Colour Only | E-Gitarre | 6 / -6 | 3 / 5 | Colour only | 100 / 100 | On | 60s | 0 dB dynamisch |
| 12 Vintage Blue Grit | E-Gitarre | 7 / -4 | 4 / 4 | 8:1 | 70 / 100 | On | 60s | 4–7 dB |
| 13 Guitar Cruncher | E-Gitarre | 15 / -8 | 7 / 7 | 4:1 | 65 / 100 | On | 80s | 10–18 dB |
| 14 Acoustic Strum | Akustikgitarre | 1 / 0 | 2 / 4 | 4:1 | 80 / 65 | On | None | 2–5 dB |
| 15 Acoustic Finger | Akustikgitarre | 3 / 0 | 3 / 4.5 | 4:1 | 90 / 65 | On | None | 3–6 dB |
| 16 Bass Finger Level | Bass | 3 / 0 | 4 / 4 | 4:1 | 100 / 80 | On | None | 3–6 dB |
| 17 Bass Pick Punch | Bass | 5 / -1 | 4 / 4 | 8:1 | 85 / 100 | On | None | 4–8 dB |
| 18 Bass Fast Grit | Bass | 8 / -4 | 7 / 7 | 8:1 | 70 / 100 | On | None | 6–12 dB |
| 19 Bass Mojo Bite | Bass | 9 / -5 | 7 / 7 | 8:1 | 75 / 100 | On | 80s | 7–10 dB im Wet-Pfad |
| 20 Huge Sub Weight | Bass | 8 / -4 | 4 / 4 | 8:1 | 85 / 100 | On | 00s | 6–10 dB |
| 21 Kick Weight | Drums | 4 / -1 | 2 / 5 | 4:1 | 80 / 85 | On | None | 3–6 dB |
| 22 Snare Crack | Drums | 5 / -2 | 3 / 6 | 8:1 | 85 / 100 | On | None | 4–8 dB |
| 23 Snare Slow Attack | Drums | 3 / -1 | 2 / 5 | 4:1 | 90 / 90 | On | None | 2–6 dB |
| 24 Snare Saturated Parallel | Drums | 6 / -6 | 3 / 6 | 4:1 | 30 / 100 | On | 80s | 10–18 dB im Wet-Pfad |
| 25 Toms Body | Drums | 4 / -1 | 4 / 6 | 4:1 | 85 / 80 | Off | None | 3–7 dB |
| 26 Overheads Gentle | Drums | -2 / 1 | 1 / 4.5 | 4:1 | 75 / 60 | On | None | 1–3 dB |
| 27 Room All Buttons | Drums | 12 / -7 | 3 / 6 | All Buttons | 100 / 100 | On | None | 10–20 dB |
| 28 Drum Room Smasher | Drums | 10 / -5 | 7 / 7 | 4:1 | 75 / 100 | On | None | 8–15 dB |
| 29 Drum Parallel Crush | Drums | 14 / -8 | 2 / 7 | All Buttons | 25 / 100 | On | None | 12–24 dB im Wet-Pfad |
| 30 Percussion Snap | Drums | 2 / 0 | 1.3 / 6.5 | 4:1 | 75 / 80 | Off | None | 2–5 dB |
| 31 Piano Gentle | Tasten | -3 / 1 | 1 / 3.5 | 4:1 | 60 / 50 | On | None | 1–3 dB |
| 32 Rhodes Body | Tasten | 2 / 0 | 2.5 / 5 | 4:1 | 85 / 90 | On | None | 3–6 dB |
| 33 Synth Bass Control | Synth | 2 / 0 | 3.5 / 4 | 8:1 | 90 / 70 | On | None | 3–7 dB |
| 34 Synth Lead Sustain | Synth | 3 / 0 | 3 / 5.5 | 4:1 | 85 / 80 | On | None | 3–6 dB |
| 35 Stereo Bus Subtle | Bus | -6 / 1 | 1.5 / 3 | 4:1 | 40 / 40 | On | None | 0–2 dB |
| 36 Mix Bus Light Glue | Bus | -4 / 0 | 1.5 / 3 | 4:1 | 45 / 45 | On | None | 1–2 dB |
| 37 Piano Gentle 2:1 | Tasten | -3 / 1 | 1 / 3.5 | 2:1 | 60 / 50 | On | None | 1–2 dB im Wet-Pfad |
| 38 Stereo Bus Subtle 2:1 | Bus | -6 / 1 | 1.5 / 3 | 2:1 | 40 / 40 | On | None | 0–2 dB im Wet-Pfad |

## 01 Neutral Start

Allgemeiner Startpunkt mit Attack 3 (ca. 234 µs) und Release 5 (ca. 140 ms); zuerst Input nach Gehör und GR einstellen. Neutral bezeichnet die Ausgangseinstellung, nicht Klangtransparenz: Colour steht auf 100 %, Compression ist aktiv.

Transformator: None.
Anregungen: UA-TIPS.

## 02 Dr Pepper Inspired

Eigene Näherung an die 10-Uhr/2-Uhr/4:1-Idee; keine exakte Hardware-Potentiometerkalibrierung.

Transformator: None.
Anregungen: UA-TIPS, MOORE, PENNY.

## 03 Vocal Natural

Konsonanten erhalten; Satzenden und Atemgeräusche prüfen.

Transformator: None.
Anregungen: VOCAL-GUIDE, PENNY, MOORE.

## 04 Vocal Peak Catch

Kontrolliert Peaks; kann vor einer langsameren Leveling-Stufe stehen.

Transformator: None.
Anregungen: VOCAL-GUIDE.

## 05 Vocal Rock Forward

Body und Bewegung mit Release abstimmen; Input bei dünnem Klang reduzieren.

Transformator: None.
Anregungen: VOCAL-GUIDE, MOORE, UA-TIPS.

## 06 Vocal Grit Parallel

Effekt für laute/raue Vocals; Mix langsam erhöhen.

Transformator: None.
Anregungen: UA-TIPS.

## 07 Vocal Squashed

MOORE S.16 Beispiel 1 (4:1, schnellste Attacke und schnellster Release): höchste, am stärksten verdichtete Gesamtdeformation. Satzenden und Atemgeräusche müssen erhalten bleiben, sonst klingt die Stimme eingedrückt.

Transformator: None.
Anregungen: MOORE, VOCAL-GUIDE.

## 08 Vocal Transformer

TOZZOLI „Vocal Transformer“ ist der Name des quelleninspirierten Tricks: Kompression aus, Audiopfad aktiv. Bei uns wird der Controller geparkt; Attack und Release steuern keine GR. FET-/Verstärkerfärbung über Colour bleibt aktiv. Der separate Eingangstransformator steht bewusst auf None; der Presetname verlangt kein Transformatorprofil. Input +4 dB und Output 0 dB sind nicht pegelkompensiert, deshalb Output nach Gehör abgleichen.

Transformator: None.
Anregungen: TOZZOLI.

## 09 Guitar Clean Sustain

Geeignet nach Amp/Cab; Pedalboard-Pegel vor Input einstellen.

Transformator: None.
Anregungen: EICHAS, UA-TIPS.

## 10 Guitar Rhythm Tight

Bereits stark verzerrte Gitarren nur leicht verdichten.

Transformator: None.
Anregungen: PENNY, UA-TIPS.

## 11 Guitar Colour Only

Verstärkerfärbung ohne Regelung; Output beeinflusst die nachfolgende Sättigung. Eigenes Transformatorprofil 60s für warme, früh einsetzende Tiefbasssättigung und HF-Abrundung; die Quelle benennt keine Stufe, die Zuordnung ist unsere.

Transformator: 60s.
Anregungen: UA-TIPS, BLACKBIRD.

## 12 Vintage Blue Grit

PENNY-Quicksheet E-Gitarre: mittlere Attacke und mittlerer Release, 4:1 oder 8:1; sie verweist für Extra-Grit auf Blue-Stripe-Emulationen. Der 1176-Absatz in MOORE S.9 nennt die frühen Revisionen mit rohem, farbigem Ton. Eigenes Transformatorprofil 60s für Wärme und weiche Tiefbasssättigung, ohne Revisionsbehauptung.

Transformator: 60s.
Anregungen: PENNY, MOORE.

## 13 Guitar Cruncher

TOZZOLI „Guitar Cruncher“: Output zurückgenommen, Input weit über die 3-Uhr-Stellung hinaus, 4:1, Attack und Release ganz rechts; zum Aufhellen des Pumpens Release nach links. Green Stripe 76 hat keinen Revisionsschalter: Das eigene 80s-Profil ergänzt ausgewogene Tiefbasssättigung zwischen 60s und 00s. Uhrzeiten werden nicht umgerechnet, siehe METHODIK in docs/SOURCES.md.

Transformator: 80s.
Anregungen: TOZZOLI, MOORE.

## 14 Acoustic Strum

Plektrum-Anschlag und Stereo-Balance erhalten.

Transformator: None.
Anregungen: MASON, PENNY.

## 15 Acoustic Finger

Leise Details hervorholen, Raumrauschen und Atemanteile mithören.

Transformator: None.
Anregungen: MASON.

## 16 Bass Finger Level

Tiefe Noten auf Regelverzerrung prüfen; Release bei Bedarf langsamer.

Transformator: None.
Anregungen: MOORE, PENNY, UA-TIPS.

## 17 Bass Pick Punch

Anschlag erhält Gewicht; der interne Mix ergänzt Direktanteil mit gemeinsamer Resamplingphase. Colour behält seine eigene Filterphase. Attack 4 ist mit ca. 126 µs schnell; für mehr Frontkante bei Bedarf Richtung 1 zurücknehmen.

Transformator: None.
Anregungen: MOORE, PENNY.

## 18 Bass Fast Grit

Bewusst schnelle Zeiten für GR-bedingte Rauheit, kein neutraler Bass-Leveler.

Transformator: None.
Anregungen: UA-TIPS, MOORE.

## 19 Bass Mojo Bite

MOORE S.21 Beispiel 3 (A7/R7, 8:1): die schnellsten Zeiten lassen den Kompressor innerhalb jeder Periode arbeiten; das erzeugt die dort beschriebene tieffrequente FET-Verzerrung. Über den Mix-Regler dosiert. Eigenes 80s-Transformatorprofil für zusätzliche, moderate Tiefbasssättigung.

Transformator: 80s.
Anregungen: MOORE.

## 20 Huge Sub Weight

MOORE S.9 (Owsinski 2006) und S.21: 8:1 mit deutlicher Gain-Reduktion für Bass. „Huge“ meint hier Tiefe und Gewicht, nicht mehr Verhältnis. Eigenes 00s-Profil mit größtem Tiefbass-Headroom und zurückhaltender HF-Färbung; keine Bassanhebung oder bestimmte Wicklung behauptet.

Transformator: 00s.
Anregungen: MOORE, PENNY.

## 21 Kick Weight

Ab 0.4.1 Attack 2 (ca. 433 µs) statt 5 (ca. 68 µs): mehr Frontkante passend zum Kick-Weight-Ziel. Release an den Abstand der Kicks anpassen; 80 % Mix ergänzen trockenen Anschlag. Auch Attack 2 bleibt FET-schnell. Bestehende Hostprojekte behalten ihre gespeicherten Werte; erneuter Factory-Recall lädt die Korrektur.

Transformator: None.
Anregungen: PENNY, UA-TIPS.

## 22 Snare Crack

Ab 0.4.1 Attack 3 (ca. 234 µs) statt 5 (ca. 68 µs): weniger gekappter Anschlag passend zum Crack-Ziel, weiterhin schneller als Preset 23 Snare Slow Attack. 85 % Mix ergänzen trockene Frontkante. Release vor dem nächsten Schlag erholen lassen; erneuter Factory-Recall lädt den neuen Attackwert.

Transformator: None.
Anregungen: PENNY, UA-TIPS.

## 23 Snare Slow Attack

MTM-SNARE regt 4:1, langsame Attacke, musikalisch passenden Release und 2–6 dB GR für eine Snare-Spur an. Attack 2 ist unsere relativ langsame Wahl (ca. 433 µs), weiterhin FET-schnell; daraus folgt kein allgemeiner Verzerrungsvorteil gegenüber Attack 1. Der in der Quelle empfohlene Hochpass um 30 Hz mit 12 dB/Okt. muss bei Bedarf im Host ergänzt werden.

Transformator: None.
Anregungen: MTM-SNARE, MOORE.

## 24 Snare Saturated Parallel

MTM-SNARE motiviert Farbe und Sättigung; die aggressive Ziel-GR von 10–18 dB im Wet-Pfad ist unsere parallele Effektwahl, keine GR-Empfehlung der Quelle. Input auf diese Wirkung abstimmen, Output pegelgleichen, dann über 30 % Mix dosieren. Das 80s-Transformatorprofil ist unsere Zuordnung; die Quelle nennt keine Stufe.

Transformator: 80s.
Anregungen: MTM-SNARE, UA-TIPS.

## 25 Toms Body

Stereo-Version als Dual Mono für getrennte Tom-Kanäle; Link nach Routing wählen.

Transformator: None.
Anregungen: PENNY, UA-TIPS.

## 26 Overheads Gentle

Stereo Link erhält Balance; Becken dürfen nicht matt oder pumpend werden.

Transformator: None.
Anregungen: UA-TIPS, BLACKBIRD.

## 27 Room All Buttons

Explosiver Effektpfad, nicht Brickwall; Transientenüberschwinger möglich.

Transformator: None.
Anregungen: UA-TIPS, MOORE, AXT-SLAM.

## 28 Drum Room Smasher

TOZZOLI „Drum Room Smasher": Release ganz rechts, Attack ebenfalls ganz rechts — die Quelle betont, dass die Release-Stellung wichtiger ist als die Attacke. Kompression und Verzerrung passieren so schnell, dass der Raum klingt und die Tiefe hervortritt; zum Aufhellen des Pumpens Release nach links. Das Verhältnis nennt die Quelle nicht, 4:1 ist unsere Wahl.

Transformator: None.
Anregungen: TOZZOLI, MOORE.

## 29 Drum Parallel Crush

Integrierter Parallelmix vermeidet separate ungeprüfte Dwarf-Zweige.

Transformator: None.
Anregungen: UA-TIPS, MUSICGUY.

## 30 Percussion Snap

Dual Mono nur bei tatsächlich unabhängigen Kanälen wählen.

Transformator: None.
Anregungen: UA-TIPS.

## 31 Piano Gentle

Konservativer eigener 4:1-Startwert; keine gemessene historische Einstellung. Die weichere zusätzliche Variante steht unter 37 Piano Gentle 2:1. Input auf gewünschte Wet-GR einstellen, Output pegelgleichen; Klangabnahme auf Musik bleibt offen.

Transformator: None.
Anregungen: EICHAS.

## 32 Rhodes Body

Transient und Sustain ausbalancieren, Chorus-Stereobild prüfen.

Transformator: None.
Anregungen: Eigener musikalischer Startpunkt.

## 33 Synth Bass Control

Tiefe Dauertöne benötigen ruhigere Release; keine Auto-Gain-Funktion.

Transformator: None.
Anregungen: UA-TIPS.

## 34 Synth Lead Sustain

Delay/Reverb vorzugsweise nach dem Kompressor, wenn deren Tails nicht gepumpt werden sollen.

Transformator: None.
Anregungen: Eigener musikalischer Startpunkt.

## 35 Stereo Bus Subtle

Kreativer 4:1-Bus-Startwert; diese Adaption ersetzt keinen transparenten Mastering-Limiter. Die weichere zusätzliche Variante steht unter 38 Stereo Bus Subtle 2:1. Input auf 0–2 dB Wet-GR einstellen und Output pegelgleichen; Musikbewertung offen.

Transformator: None.
Anregungen: BLACKBIRD, PENNY.

## 36 Mix Bus Light Glue

PENNY-Quicksheet Mixbus motiviert Attack 1–2, Release 2–4, 4:1 und 1–2 dB GR. Input bestimmt die Wet-GR; Mix 45 % dosiert lediglich deren Anteil am Ausgang und ändert die Regelung nicht. Deshalb erst Input einstellen, Output pegelgleichen und danach Mix abstimmen. 4:1 bleibt hier als quellenbezogener Ausgangspunkt erhalten.

Transformator: None.
Anregungen: PENNY, BLACKBIRD.

## 37 Piano Gentle 2:1

Neue eigene 2:1-Variante von Preset 31, ansonsten identische Startwerte. Weniger Verdichtung für natürliche Anschläge; im 1-kHz-Vergleich bei −18 dBFS Peak ca. 1,56 statt 2,62 dB mittlere Wet-GR. Das ist ein Signalbeleg, kein Piano-Hörtest. Input an die Aufnahme anpassen und Output neu pegelgleichen.

Transformator: None.
Anregungen: Eigener musikalischer Startpunkt.

## 38 Stereo Bus Subtle 2:1

Neue eigene 2:1-Variante von Preset 35, ansonsten identische Startwerte. Sanfte Stereo-Verdichtung; bei −18 dBFS Peak im 1-kHz-Test ca. 0,49 statt 0,96 dB mittlere Wet-GR. Link On erhält gemeinsame Regelung. Mix dosiert den Effekt, nicht die interne GR; Musik-/Geräteabnahme offen.

Transformator: None.
Anregungen: Eigener musikalischer Startpunkt.
