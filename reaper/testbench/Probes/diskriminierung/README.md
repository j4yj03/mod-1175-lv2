# Diskriminierungsprogramm GS76/SSL (echter Kern vs. Effektmodell)

**Eine WAV-Datei, vier Proben:** `gs76-diskriminierung-stereo.wav` (2195520 Frames, 45.74 s, 48 kHz, Stereo L=R, PCM 24).
Erzeugt von `tools/make_discrimination_program.py` aus denselben
Generatoren wie `tools/make_probes.py`; Rezepte und Kriterien:
MESSTECHNIK 1k.1/1k.2. SHA256: `7e262ef47c4fd173…` (vollständig in `manifest.json`).

## Ablaufplan

| Start s | Start Frames | Dauer s | Inhalt |
|---:|---:|---:|---|
| 1.00 | 48000 | 0.12 | Sync-Marker pilot-start (Chirp −18 dBFS) |
| 1.62 | 77760 | 10.00 | Probe **remanenz-bursts** |
| 12.12 | 581760 | 8.00 | Probe **zweiton-im** |
| 20.62 | 989760 | 15.00 | Probe **pegelreihe-20hz** |
| 36.12 | 1733760 | 8.00 | Probe **dc-asymmetrie** |
| 44.62 | 2141760 | 0.12 | Sync-Marker pilot-end (Chirp −18 dBFS) |

Proben im Detail:

- **remanenz-bursts** — 20-Hz-Bursts −2 dBFS: 0,5–1,5 / 2,5–3,5 /
  4,5–5,5 / 6,5–9,5 s (drei kurze + ein langer), dazwischen Träger
  0,003. Misst Hysterese-Gedächtnis: Erstburst gegen Folgebürste,
  Nachlauf-RMS (50–250 ms nach Burst-Ende), Ausgangs-DC nach Burst-Ende.
- **zweiton-im** — 60 Hz −6 dBFS + 1 kHz −26 dBFS. Misst
  Fluss-Modulation: Seitenbänder bei 1000±k·60 Hz (k = 1…4) gegen die
  speicherfreie Vorhersage aus der Pegelreihe.
- **pegelreihe-20hz** — 20 Hz bei −26/−20/−14/−8/−2 dBFS (je 3 s).
  Misst Knie-/Verlustform: gain_db + THD je Stufe, alle Stufen aus
  einem Render.
- **dc-asymmetrie** — 0–3 s 1 kHz + DC +0,3 FS; 3–6 s 1 kHz ohne DC;
  6–8 s reiner DC. Misst AC-Kopplung (Ausgangs-DC ≈ 0?) und H2/H3-
  Verhalten unter Offset. **Vorsicht:** Spitze 0,7 FS; Ausgangs-Peak
  nach dem Render kontrollieren.

## Render-Auftrag (REAPER/Testbench)

Das **gesamte Programm einmal je Variante** rendern (48 kHz, beide
Kanäle), Dateinamen verbindlich:

| Datei | Variante |
|---|---|
| `diskriminierung-no_fx.wav` | ohne FX (Referenz; leere/Bypass-FX-Kette) |
| `diskriminierung-ssl-a50.wav` | SSL Fusion Transformer, AMOUNT 50 (Stellungs-Screenshot!) |
| `diskriminierung-ssl-a100.wav` | SSL Fusion Transformer, AMOUNT 100 (Stellungs-Screenshot!) |
| `diskriminierung-gs76-60s.wav` | GS76-Stereo.jsfx: COMP OFF, Colour 0, OS 2x, Transformer 60s |
| `diskriminierung-gs76-80s.wav` | GS76-Stereo.jsfx: COMP OFF, Colour 0, OS 2x, Transformer 80s |

- GS76-Varianten: JSFX wie in der Testbench (COMP OFF, Colour 0,
  OS 2x, Transformer 60s/80s, In/Out 0 dB). SSL: nur AMOUNT ändern,
  Stellungs-Screenshot mitarchivieren (SHINE/MIX/TRIM unbekannt =
  Provenanzlücke, siehe MESSTECHNIK 1k).
- Die OS-Differenz (SSL ohne OS, GS76 2x) betrifft Aliasing, nicht die
  hier gemessenen Tieftonmetriken.
- no_fx muss **sampleidentisch** zum Programm sein (Offset 0) —
  Negative Control für die ganze Auswertekette.

## Auswertung

Offline über die Renders; Segmentgrenzen aus `manifest.json`
(`start_frames`/`frames` je Probe, Marker für Offset-/Ratenprüfung
per Chirp-Korrelation). Metriken und Entscheidungskriterien:
MESSTECHNIK 1k.2. Ziel: SSL als Charakter- vs. Physikreferenz
einordnen, bevor SSL A50 als Anker in den Klangmodellplan eingeht.

