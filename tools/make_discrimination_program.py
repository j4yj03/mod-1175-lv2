#!/usr/bin/env python3
"""Baut das kombinierte Diskriminierungsprogramm als eine WAV-Datei.

Quelle sind die vier Diskriminierungsprobes aus tools/make_probes.py
(gemeinsame Generatoren, keine Kopie der Formeln). Das Programm wird mit
Sync-Marker (Pilot-Chirp wie in scarlett_test), Vor-/Nachlauf und
0,5-s-Trennstille zu einer Stereo-PCM24-Datei zusammengefasst und nach
reaper/testbench/Probes/diskriminierung/ geschrieben; dort liegt auch
README.md (Anleitung) und manifest.json (Timeline fuer die Auswertung).
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import make_probes  # noqa: E402

RATE = 48000
LEAD_S = 1.0
GAP_S = 0.5
TAIL_S = 1.0
PILOT_S = 0.12
PILOT_LEVEL_DB = -18.0
OUTPUT_DIR_DEFAULT = ROOT / "reaper/testbench/Probes/diskriminierung"
PROGRAM_NAME = "gs76-diskriminierung-stereo.wav"

RENDER_VARIANTS = (
    ("no_fx", "ohne FX (Referenz; leere/Bypass-FX-Kette)"),
    ("ssl-a50", "SSL Fusion Transformer, AMOUNT 50 (Stellungs-Screenshot!)"),
    ("ssl-a100", "SSL Fusion Transformer, AMOUNT 100 (Stellungs-Screenshot!)"),
    ("gs76-60s", "GS76-Stereo.jsfx: COMP OFF, Colour 0, OS 2x, Transformer 60s"),
    ("gs76-80s", "GS76-Stereo.jsfx: COMP OFF, Colour 0, OS 2x, Transformer 80s"),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pilot(rate, reverse=False):
    t = np.arange(round(PILOT_S * rate)) / rate
    window = np.sin(np.linspace(0, np.pi / 2, round(0.01 * rate))) ** 2
    wave_form = 10 ** (PILOT_LEVEL_DB / 20) * np.sin(2 * np.pi * (500 * t + (6000 - 500) / 0.24 * t * t))
    wave_form[:len(window)] *= window
    wave_form[-len(window):] *= window[::-1]
    if reverse:
        wave_form = wave_form[::-1].copy()
    return wave_form


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR_DEFAULT)
    parser.add_argument("--rate", type=int, default=RATE)
    args = parser.parse_args()
    rate = args.rate
    args.output_dir.mkdir(parents=True, exist_ok=True)

    parts = [np.zeros(round(LEAD_S * rate)), pilot(rate)]
    timeline = [dict(kind="marker", label="pilot-start",
                     start_frames=round(LEAD_S * rate), frames=len(parts[-1]))]
    position = sum(len(p) for p in parts)
    for name, factory in make_probes.DISCRIMINATION_PROBES:
        gen, seconds = factory(rate)
        parts.append(np.zeros(round(GAP_S * rate)))
        position += len(parts[-1])
        n_total = round(seconds * rate)
        samples = np.empty(n_total)
        for n in range(n_total):
            samples[n] = gen(n)
        parts.append(samples)
        timeline.append(dict(kind="probe", label=name[:-4], source=name,
                             start_frames=position, frames=n_total,
                             start_seconds=round(position / rate, 3)))
        position += n_total
    parts.append(np.zeros(round(GAP_S * rate)))
    parts.append(pilot(rate, reverse=True))
    timeline.append(dict(kind="marker", label="pilot-end",
                         start_frames=position + round(GAP_S * rate),
                         frames=round(PILOT_S * rate)))
    parts.append(np.zeros(round(TAIL_S * rate)))

    stereo = np.column_stack((np.concatenate(parts), np.concatenate(parts)))
    program_path = args.output_dir / PROGRAM_NAME
    sf.write(str(program_path), stereo, rate, subtype="PCM_24")

    total_frames = stereo.shape[0]
    manifest = dict(
        created_by="tools/make_discrimination_program.py",
        program=PROGRAM_NAME,
        rate=rate, channels=2, frames=total_frames, seconds=round(total_frames / rate, 3),
        pcm="24 bit", pilot="0,12-s-Chirp 500→6000 Hz bei −18 dBFS (Start + Ende, wie scarlett_test)",
        lead_seconds=LEAD_S, gap_seconds=GAP_S, tail_seconds=TAIL_S,
        timeline=timeline,
        render_variants=[dict(suffix=suffix, description=desc, filename=f"diskriminierung-{suffix}.wav")
                         for suffix, desc in RENDER_VARIANTS],
        sha256=sha256(program_path),
    )
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Diskriminierungsprogramm GS76/SSL (echter Kern vs. Effektmodell)",
        "",
        f"**Eine WAV-Datei, vier Proben:** `{PROGRAM_NAME}` "
        f"({total_frames} Frames, {total_frames / rate:.2f} s, 48 kHz, Stereo L=R, PCM 24).",
        "Erzeugt von `tools/make_discrimination_program.py` aus denselben",
        "Generatoren wie `tools/make_probes.py`; Rezepte und Kriterien:",
        "MESSTECHNIK 1k.1/1k.2. SHA256: `"
        + manifest["sha256"][:16] + "…` (vollständig in `manifest.json`).",
        "",
        "## Ablaufplan",
        "",
        "| Start s | Start Frames | Dauer s | Inhalt |",
        "|---:|---:|---:|---|",
    ]
    for entry in timeline:
        if entry["kind"] == "marker":
            lines.append(f"| {entry['start_frames'] / rate:.2f} | {entry['start_frames']} | "
                         f"{entry['frames'] / rate:.2f} | Sync-Marker {entry['label']} (Chirp −18 dBFS) |")
        else:
            lines.append(f"| {entry['start_seconds']:.2f} | {entry['start_frames']} | "
                         f"{entry['frames'] / rate:.2f} | Probe **{entry['label']}** |")
    lines += [
        "",
        "Proben im Detail:",
        "",
        "- **remanenz-bursts** — 20-Hz-Bursts −2 dBFS: 0,5–1,5 / 2,5–3,5 /",
        "  4,5–5,5 / 6,5–9,5 s (drei kurze + ein langer), dazwischen Träger",
        "  0,003. Misst Hysterese-Gedächtnis: Erstburst gegen Folgebürste,",
        "  Nachlauf-RMS (50–250 ms nach Burst-Ende), Ausgangs-DC nach Burst-Ende.",
        "- **zweiton-im** — 60 Hz −6 dBFS + 1 kHz −26 dBFS. Misst",
        "  Fluss-Modulation: Seitenbänder bei 1000±k·60 Hz (k = 1…4) gegen die",
        "  speicherfreie Vorhersage aus der Pegelreihe.",
        "- **pegelreihe-20hz** — 20 Hz bei −26/−20/−14/−8/−2 dBFS (je 3 s).",
        "  Misst Knie-/Verlustform: gain_db + THD je Stufe, alle Stufen aus",
        "  einem Render.",
        "- **dc-asymmetrie** — 0–3 s 1 kHz + DC +0,3 FS; 3–6 s 1 kHz ohne DC;",
        "  6–8 s reiner DC. Misst AC-Kopplung (Ausgangs-DC ≈ 0?) und H2/H3-",
        "  Verhalten unter Offset. **Vorsicht:** Spitze 0,7 FS; Ausgangs-Peak",
        "  nach dem Render kontrollieren.",
        "",
        "## Render-Auftrag (REAPER/Testbench)",
        "",
        "Das **gesamte Programm einmal je Variante** rendern (48 kHz, beide",
        "Kanäle), Dateinamen verbindlich:",
        "",
        "| Datei | Variante |",
        "|---|---|",
    ]
    for suffix, desc, _ in [(s, d, None) for s, d in RENDER_VARIANTS]:
        lines.append(f"| `diskriminierung-{suffix}.wav` | {desc} |")
    lines += [
        "",
        "- GS76-Varianten: JSFX wie in der Testbench (COMP OFF, Colour 0,",
        "  OS 2x, Transformer 60s/80s, In/Out 0 dB). SSL: nur AMOUNT ändern,",
        "  Stellungs-Screenshot mitarchivieren (SHINE/MIX/TRIM unbekannt =",
        "  Provenanzlücke, siehe MESSTECHNIK 1k).",
        "- Die OS-Differenz (SSL ohne OS, GS76 2x) betrifft Aliasing, nicht die",
        "  hier gemessenen Tieftonmetriken.",
        "- no_fx muss **sampleidentisch** zum Programm sein (Offset 0) —",
        "  Negative Control für die ganze Auswertekette.",
        "",
        "## Auswertung",
        "",
        "Offline über die Renders; Segmentgrenzen aus `manifest.json`",
        "(`start_frames`/`frames` je Probe, Marker für Offset-/Ratenprüfung",
        "per Chirp-Korrelation). Metriken und Entscheidungskriterien:",
        "MESSTECHNIK 1k.2. Ziel: SSL als Charakter- vs. Physikreferenz",
        "einordnen, bevor SSL A50 als Anker in den Klangmodellplan eingeht.",
        "",
    ]
    (args.output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{PROGRAM_NAME}: {total_frames} Frames ({total_frames / rate:.2f} s) -> {program_path.relative_to(ROOT)}")
    print(f"README.md + manifest.json -> {args.output_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
