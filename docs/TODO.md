# Offene Aufgaben

Konsolidiert am **2026-10-06** nach der Dokumentenzusammenfassung. Details zu
jeder Position stehen in den verlinkten Dokumenten. Nicht ausgeführte
Geräte-/Hörtests werden nicht als bestanden geführt.

## Offen — Scarlett (siehe [MESSTECHNIK](MESSTECHNIK.md))

Aktueller Stand 2026-10-07: **Transformator-Matrix am Gerät ausgeführt**
(Dwarf-Quelle, REAPER-Aufnahme, `test-results/matrix-dwarf-20261007`):
Baseline/60s/80s/00s × r1+r2, Sym × r1, je 2 Kanäle, alle gültig; Anker exakt,
Wiederholungs-Spreizung ≤ 0,01 dB, 20-Hz-Klirr-Reihung 60s 5,53 % / 80s 2,15 % /
00s 0,11 % / Sym 0,01 %. OS-Stellung laut Benutzer **2x** (in Index/Label
nachgetragen). Ergebnisse in PROJEKT.md; Auswertung/Interpretation
gegen die Modellanker in `EXTERN.md` folgt.

- [ ] Sym als r2 Wiederholung (der r1-Analoglauf war ein erster Clip-Versuch,
  die digitale Querreferenz bestätigt Sym als linear flach).
- [ ] ggf. r3 für engere Mediane; die r1/r2-Spreizung ≤ 0,01 dB macht das
  optional.
- [ ] 96-kHz-Messung entfällt für die Dwarf-Quelle (Player läuft mit der
  fester Geräterate 48 kHz); 20 kHz bleibt damit nah an Nyquist gemessen.
- [ ] Windows-Geräteformat abschließen (nur noch relevant, falls der
  Mess-Treiber statt REAPER aufnimmt): mmsys.cpl Aufnahme auf 24 bit/48000 Hz.
- [ ] Klären, ob das Dwarf-INPUT-Meter (Web-UI 192.168.51.1) als
  Plugin-Eingangspegel-Referenz brauchbar ist; mit Dwarf-Quelle ist der
  Plugin-Eingang digital exakt bekannt, das Meter ist nur noch cross-check.
- [ ] PluginDoctor-Sweep-Wiederholung zurückgestellt (PD erlaubt hier keine
  Einstellungssteuerung; Marker-Sync über `scarlett_test.py` ist der
  verlässliche Weg).

## Offen — Dwarf/Gerät (siehe [PROJEKT](PROJEKT.md), Abschnitt Übergabe)

- [ ] `transformer_bench` (Serie B) AArch64/MPB auf dem Dwarf ausführen zur
  isolierten Transformator-/Solver-Kostenmessung (PERFORMANCE, Abschnitt 5c).
  Serie A ist gemessen (MESSTECHNIK, Abschnitt Dwarf-Lastmessung). Ergebnis
  ist die Entscheidungsbasis für die CPU-Reduktions-Vorschläge (Abschnitt
  CPU-Reduktion Transformator): Iterationen/Stop-Zweig-Verteilung je
  Profil/OS lesen.
- [ ] Dwarf-Lasttabelle: Provenienz nachtragen (Messdatum, Tool-Version,
  installierte SHA256 je Serie, Settle/Messfenster).
- [ ] 0.4.1-Bundle mit MPB `moddwarf-new` neu bauen; ABI/Hash dokumentieren;
  danach 21/22 sowie 31/37 und 35/38 im Pedalboard hören, CPU/xruns prüfen.
- [ ] Reale REAPER-7-Abnahme (Recall/Automation/Host-GR/Fonts) und
  Dwarf-Bedienprüfung (PROJEKT, Abschnitt Übergabe P0/P1).
- [ ] Neue Drag-Handles am Gerät ziehen: unterer 9-px-Rand und Fußzeilenplatte
  (Cursor, Panel-Move, keine Reglerberührung). Toolkit-Bindung ist belegt
  (MESSTECHNIK, Abschnitt MOD-GUI-Browsertest); Lauf mit echter MOD-UI-Quelle offen.

## Offen — Klangmodell und Analyse

- [ ] SPICE-Befund umsetzen: konsistente Übertrager-Netzform klären, neu
  simulieren (QUELLEN, Abschnitt SPICE-Bericht); bisherige Schwellenzahlen
  sind kein freigegebener Fit.
- [ ] de-Paiva-Referenzmodell (Abb. 6(b)/Tabelle 1) als unabhängige
  Offline-Referenz gegen die WDF-Näherung prüfen (QUELLEN).
- [ ] Hammond-140TEX-/560Q-Ziele: Quelle/Last- und Volt-Skalierung festlegen,
  Amplituden-/Phasen-Fit (QUELLEN, Abschnitt Hersteller-Kennlinien).
- [ ] Weitere Jensen-Refits mit neuen Referenzdaten und dokumentierter
  Bankrevision; partialen Fit nicht als Hardwarekalibrierung ausgeben.
- [ ] PluginDoctor-GR (8:1-Schwäche): DSP-Gegenprobe steht aus; die
  Modellinterpretation (Knee/Threshold-Design) ist in
  [EXTERN](EXTERN.md) dokumentiert.
- [ ] Alias-Konvergenz und Hören der ~21,45-kHz-H9-Kandidatenlinie bei hohem
  Colour-only-Drive (EXTERN).
- [ ] Musik-Hörtests: alle 38 Presets auf geeignetem Material; pegelgleiche
  4:1/2:1-Vergleiche (31↔37, 35↔38); Attackkorrektur 21/22 hören
  (EXTERN, Abschnitt Presetbewertung).

## Offen — CPU-Reduktion Transformator (Skizze, nach Risiko sortiert)

Grundlage: PERFORMANCE 5c (x86) — nicht die Iterationszahl ist der Hebel
(2,0–2,6 je Probe, 0 % am 40er-Limit), sondern die **14 Stop-Zweige je
Auswertung**; OS multipliziert (4× ≈ ×4). Entscheidungsbasis ist Serie B auf
dem Dwarf (siehe Abschnitt Dwarf/Gerät) — die x86-Verteilung muss auf dem A35
nicht gelten.

Paritätsneutral (bit-identisch machbar):

- [ ] Finale Doppel-Auswertung in `Transformer.hpp`/`current()` einsparen:
  nach Konvergenz wird am selben `x` nochmals mit `advance=true` ausgewertet;
  Wert/Ableitung sind dort identisch reproduzierbar — Zustands-Aktualisierung
  an die letzte Schleifenauswertung hängen. Erwartung ~25–30 % des dominanten
  Terms; Bit-Vorher/Nachher als Nachweis beilegen.
- [ ] Build-Tuning für den MPB-Build prüfen: `-mcpu=cortex-a35`, LTO —
  semantikgleich (kein Fast-Math, `-ffp-contract=off` bleibt), reine
  Scheduling-Gewinne; Serie B als Messrahmen nutzen.
- [ ] NEON 2-Lane für Stereo in `src/dsp/Transformer.hpp`: L/R-Zustände sind
  vertragsgemäß getrennt; 2×double mit identischer Operationsreihenfolge je
  Lane und ohne horizontale Ops bleibt bit-identisch (max 0 FS hält), EEL2
  bleibt skalar. Erwartung ~2× auf den Transformerblock für Stereo-Instanzen,
  Mono ohne Gewinn; Paritätssatz trotzdem komplett laufen lassen.

Mit vollem Paritätspreis (C++/EEL2 gemeinsam, `generate.py`, 430+76 Fälle
gegen neue Bit-Basis, `cpu_regression` Vorher/Nachher, Übergangstests,
Gerätevergleich):

- [ ] Stop-Zweige je Profil spezialisieren: `generate.py` gibt die aktiven
  Zweige je Profil aus; Zweige, die im Erreichbarkeitsbereich nie klemmen,
  exakt in den Residual falten oder zur Bauzeit weglassen. Potenzial grob
  30–50 % des dominanten Terms; Fließkomma-Neuordnung ändert Rundung.
- [ ] Startwert-/Steigungsverbesserung (Prädiktor zweiter Ordnung) bzw.
  gelockerte Konvergenztoleranz (aktuell 1e-14 relativ) prüfen; Ziel
  Iterationen < 2 je Probe.

Vertragliche Hebel (nur mit Gerätedaten und begründeter Modelländerung):

- [ ] OS-Entkopplung „Transformator rechnet in Host-Rate" als explizite
  Option: größter Hebel, aber Modelländerung (Aliasing der Sättigung), neuer
  Port = Versionierung, Übergangstests; nur wenn Serie B genau das als
  Engpass zeigt.
- [ ] Kennlinien-LUT für `law()`: nur nach A35-Microbench — softClip-Lektion:
  LUT kann langsamer als analytisch sein (9,7 vs 1,87 ns auf x86), A35-Cache
  schlechter. Die Stop-Zweige sind zustandsabhängig und bleiben
  tabellenuntauglich.

Nicht wirkksam (dokumentiert, nicht verfolgen): Iterationslimit senken
(0 % am Cap); kanalübergreifende Zustandsnutzung (Vertrag);
Auto-Deaktivierung bei Compression Off (bewusst nicht vorgesehen).

Vorgeschlagene Reihenfolge: Doppel-Auswertung einsparen + Serie B zuerst,
dann NEON, dann mit Gerätedaten zwischen Zweig-Spezialisierung und
OS-Entkopplung entscheiden.

## Offen — Projektinfrastruktur

- [ ] Dwarf-GUI: Logo-Renderfix (`/resources/…{{{ns}}}`-Form, siehe PROJEKT)
  auf dem Gerät prüfen; dazu Fix committen/pushen und
  `GREEN_STRIPE_76_VERSION` in `packaging/mod-plugin-builder/…/green-stripe-76.mk`
  auf den neuen Commit setzen, dann MPB-Neubau (Gerät/Cloud) und Web-UI-Sichtprüfung.
- [ ] README-Verzeichnisse auf ersten beiden Stufen erstellen (Haupt-README
  nur Überblick + Referenzen).

## Erledigt (zur Erinnerung, nicht mehr offen)

- [x] `.opencode/skills/audio-coding/SKILL.md` um MOD-Dwarf-Erkenntnisse erweitert.
- [x] modgui-Logo im grünen Rechteck ersetzt (Commit `1262999`).
- [x] Dwarf-Messreihe GS76x0–x4, 128/256 Frames: Tabelle in MESSTECHNIK
  (Abschnitt Dwarf-Lastmessung); STATUS/HANDOFF 2026-10-06 aktualisiert.
- [x] PluginDoctor-GR-Daten dokumentiert (EXTERN).
- [x] Scarlett-Liveaufnahme 2026-10-05 ausgeführt; Auswertung zeigt
  Pegel-/SNR- und HF-Grenzen → Wiederholung offen (oben).
- [x] Dokumentation auf 7 Konsolidierungsdokumente + TODO zusammengefasst
  (2026-10-06); generiertes `PRESETS.md` bleibt als Generator-Artefakt.
- [x] modgui-Assets neu gerendert (2026-10-06, Chromium/Playwright): Logo wird
  dargestellt; `gui_preview.page_html()` inlined HTML-`src`-Assets als
  Data-URI (Basis-URL-Problem von `set_content()` behoben).
