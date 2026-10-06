# Offene Aufgaben

Konsolidiert am **2026-10-06** nach der Dokumentenzusammenfassung. Details zu
jeder Position stehen in den verlinkten Dokumenten. Nicht ausgeführte
Geräte-/Hörtests werden nicht als bestanden geführt.

## Offen — Scarlett (siehe [MESSTECHNIK](MESSTECHNIK.md))

Aktueller Stand 2026-10-06: Matrix-Treiber `tools\scarlett_matrix.bat` bereit
(19 Offline-/Mocktests PASS, Windows-Python 3.9 und WSL); Gainmatch-Proben am
Gerät laufen, Messreihe `test-results/matrix-20261006-161927`.

- [ ] Windows-Geräteformat abschließen: Sounddialog (`mmsys.cpl`) Wiedergabe
  „Lautsprecher (Focusrite USB Audio)“ **und** Aufnahme „Analogue 1 + 2
  (Focusrite USB Audio)“ auf 24 Bit/48000 Hz. Die Scarlett-Panel-Einstellung
  (48 kHz, SYNCED) ist **nicht** dieselbe Einstellung; `default_samplerate`
  meldete auch nach der Panel-Änderung weiterhin 44100. Kontrolle:
  `rate_mismatch`-Warnung weg, Sync-Marker-Korrelation wieder > 0,35
  (beobachtet: 0,319 bei Resampling).
- [ ] Routing/Board klären: Im Ch1-Probe (nur Out1 aktiv) kommt das Signal auf
  **beiden** Scarlett-Eingängen an; Ch2 clippt bei 0,0 dBFS (105–139k Samples).
  Verdacht: MONO-Board am Dwarf (Mono verarbeitet Input L auf beide Outputs)
  oder abweichende Verkabelung. GS76-STEREO-Board laden und im nächsten Probe
  verifizieren (kein Clipping mehr, In2 still). SSH auf `last.json` ist hier
  ohne sshpass/expect nicht möglich (kein askpass) — über Benutzer klären.
- [ ] Pegelkette fertig stellen: Loop-Gewinn aktuell −30,6 (Ch1) / −35,5 (Ch2)
  dB; Kanaldifferenz −4,93 dB → zuerst Rebalance (+≈5 dB auf Ch2-Seite),
  dann beide Kanäle **gleich** anheben (primär Scarlett-INPUT-Gains bis ~+50 dB
  und Dwarf-OUTPUT-Knopf). Ziel ≥ +1 dB (Anker), mindestens −20 dB; gainmatch
  wiederholen, bis „OK“.
- [ ] Danach `full --repeats 3 --settings-label "…"` ausführen: Baseline
  (2 Läufe je Kanal, Dwarf-Bypass) und Matrix None/60s/80s/00s/Sym × 3
  Wiederholungen × 2 Kanäle; der Treiber fragt je Transformator-Bedingung
  (Dwarf umstellen). Zwischen Baseline und DUT keine Regler mehr verändern.
- [ ] 20 kHz zusätzlich mit `--rates 48000 96000` messen (Geräteraten vorher
  umstellen).
- [ ] Klären, ob das Dwarf-INPUT-Meter (Web-UI 192.168.51.1) als
  Plugin-Eingangspegel-Referenz brauchbar ist; der Rückkanal im Bypass ist nur
  Proxy (MESSTECHNIK Abschnitt 3). Damit lässt sich die Anker-Näherung
  absichern.
- [ ] PluginDoctor-Sweep-Wiederholung zurückgestellt (PD erlaubt hier keine
  Einstellungssteuerung; Marker-Sync über `scarlett_test.py` ist der
  verlässliche Weg).

## Offen — Dwarf/Gerät (siehe [PROJEKT](PROJEKT.md), Abschnitt Übergabe)

- [ ] `transformer_bench` (Serie B) AArch64/MPB auf dem Dwarf ausführen zur
  isolierten Transformator-/Solver-Kostenmessung (PERFORMANCE, Abschnitt 5c).
  Serie A ist gemessen (MESSTECHNIK, Abschnitt Dwarf-Lastmessung).
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

## Offen — Projektinfrastruktur

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
