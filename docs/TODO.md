# Offene Aufgaben

Konsolidiert am **2026-10-06** nach der Dokumentenzusammenfassung. Details zu
jeder Position stehen in den verlinkten Dokumenten. Nicht ausgeführte
Geräte-/Hörtests werden nicht als bestanden geführt.

## Offen — Scarlett (siehe [MESSTECHNIK](MESSTECHNIK.md))

Aktueller Stand 2026-10-07: Umstieg auf **Dwarf als Signalquelle**
(`tools/make_dwarf_tones.py`, Testtöne 48 kHz/PCM_24 zum Hochladen;
`scarlett_test.py --no-playback` und `scarlett_matrix.py --dwarf-source --level -2`
bereit, 16+21 Mocktests PASS). Die alte Scarlett-Stimulus-Kette (Pegelkette,
Loop-Gewinn −54…−30 dB) ist damit obsolet; die Punkte darunter betreffen nur
noch den Fall, dass stattdessen wieder über Scarlett angeregt wird.

- [ ] Testtöne auf den Dwarf hochladen (`test-results/dwarf-tones/`, siehe
  `MANIFEST.md`) und die Messreihe neu starten: `full --dwarf-source --level -2`
  — Gainmatch, Baseline (GS76 Bypass) und Matrix None/60s/80s/00s/Sym;
  Ablauf je Lauf: Enter, dann sofort Wiedergabe auf dem Dwarf.
- [ ] Windows-Geräteformat abschließen (nur noch Aufnahmeseite relevant):
  Sounddialog (`mmsys.cpl`) Aufnahme „Analogue 1 + 2 (Focusrite USB Audio)“
  auf 24 Bit/48000 Hz. Die Scarlett-Panel-Einstellung (48 kHz, SYNCED) ist
  **nicht** dieselbe Einstellung; `default_samplerate` meldete auch nach der
  Panel-Änderung weiterhin 44100. Kontrolle: `rate_mismatch`-Warnung weg.
- [ ] Routing/Board klären: Im Ch1-Probe (nur Out1 aktiv) kam das Signal auf
  **beiden** Scarlett-Eingängen an; Ch2 clippte bei 0,0 dBFS (105–139k
  Samples). Verdacht: MONO-Board am Dwarf (Mono verarbeitet Input L auf beide
  Outputs) oder abweichende Verkabelung. GS76-STEREO-Board laden und im
  nächsten Probe verifizieren (kein Clipping mehr, In2 still). SSH auf
  `last.json` ist hier ohne sshpass/expect nicht möglich (kein askpass) —
  über Benutzer klären. Mit Dwarf-Quelle entfällt der Stimulus-Anteil dieses
  Problems; der Rückkanal-Routing-Check bleibt.
- [ ] Alte Pegelkette (Loop-Gewinn ≥ +1 dB über Scarlett-INPUT-Gains) nur
  noch nötig, falls die Dwarf-Quelle wieder verlassen wird; als obsolet
  markiert, nicht löschen.
- [ ] Danach Auswertung `SUMMARY.md`: Anker −14/−8/−2 dBFS sollten jetzt
  exakt getroffen sein (Dateipegel = Plugin-Eingang); Kanaldifferenz aus dem
  Gainmatch gegen Toleranz ±1 dB prüfen.
- [ ] 20 kHz zusätzlich mit `--rates 48000 96000` messen (Geräteraten vorher
  umstellen).
- [ ] Klären, ob das Dwarf-INPUT-Meter (Web-UI 192.168.51.1) als
  Plugin-Eingangspegel-Referenz brauchbar ist; mit Dwarf-Quelle ist der
  Plugin-Eingang digital exakt bekannt, das Meter ist nur noch cross-check.
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
