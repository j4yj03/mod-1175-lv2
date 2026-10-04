# Anforderungen und Abgrenzung

Stand: Benutzerentscheidungen dieser Session, 2026-10-03.

## Produkt

- Name **Green Stripe 76**; eigenes grünes Erscheinungsbild.
- 1176-inspirierter FET-Kompressor/Limiter; nach letzter Benutzerkorrektur keine
  verbindliche Festlegung auf Rev. A oder D.
- Hohe musikalische Nähe ist Entwicklungsziel; gemessene Hardwaregleichheit ist
  ohne Referenzgerät/kalibrierte Daten kein belegter Lieferstatus.

## Plattformen

| Plattform | Anforderung |
|---|---|
| MOD Dwarf | OS 1.13.5.3315, aarch64/Cortex-A35, Kernel 6.1.15-rt7-moddwarf |
| LV2 | Mono und Stereo, optionale Link-Regelung, keine Meter-GUI/GR-Ports |
| REAPER 7 | JSFX Mono und Stereo, optionale Link-Regelung, GR und Level |
| Testrechner | anderer Rechner; dort Dwarf/REAPER, Docker/MPB und Hörprüfung |

## Bedienfunktionen

Input, Output, Attack 1–7, Release 1–7, Ratio 4/8/12/20/All,
Mix, Colour, Compression, Enabled und in Stereo Stereo Link.
Gemeinsame Regler im Dual-Mono-Modus. Eingebaute Instrument-Startwerte und `.rpl`.

## Technische Eigenschaften

- DSP-C++11, keine Runtime-Abhängigkeit auf JUCE, React, X11 oder NAM.
- Audiopfad float-Ports, double-Zustände, keine Lookahead-Puffer.
- Pro Sample begrenzte numerische Arbeit, keine Audio-Allokationen.
- 4×-Polyphasen-IIR-Verarbeitung für Audiopfad und Regelung.
- Input-Staging, nichtlinearer FET-Divider, post-cell Feedback-Abgriff vor Output,
  programabhängige Entladung und separater All-Modus.
- Geglättete Parameteränderungen und interner Bypass.
- Interner Dry/Wet teilt Resamplingphase, unveränderte Kanalzuordnung.
- Definierte Aktivierung/Reset, beliebige positive Blöcke und `run(0)`.

## Referenzmaterial

Dissertation, UA-Handbücher, DIY-Unterlagen, andere Open-Source-DSPs und
Praxisartikel werden mit Herkunft/Revision/Aussagegrenzen dokumentiert.
Die vier NAM-Dateien dienen als **Offline-Referenzmaterial**, nicht als automatisch
eingebauter Audioprozessor. A1-Abtastrate und Capture-Stellungen sind unbekannt.

## Abnahme

1. Native Build und Signal-/ABI-Tests bestanden.
2. JSFX geladen, gerendert und mit C++ verglichen.
3. Presets gültig, importierbar, dokumentiert.
4. Dwarf-Cross-ABI und reales Laden/CPU/Regler geprüft (extern).
5. REAPER-Meter, Preset-Recall, Routing, Automation geprüft (extern).
6. Klangabgleich und persönliche Bewertung protokolliert (extern).

Punkte 4–6 bleiben separat sichtbar, auch wenn 1–3 bestanden sind.
