#!/usr/bin/env python3
"""Analysiert die SSL-Fusion-Transformer-REAPER-Renders (AMOUNT-Sweep).

Batch: reaper/testbench/2026-10-08 15_22_27/SSL GROUP 1 — fuenf Renders
(AMOUNT 0/50/100/150/200) ueber das Standard-Matrixprogramm
(gs76-matrix-all-m2-stereo.wav, 64,47 s, 19 Segmente, −2 dBFS).

Die Analyse laeuft gegen den originalen Stimulusplan
(test-results/dwarf-tones/runs/matrix-all-m2) ohne Neugenerierung; die
Renders sind digital und paddgenau (REAPER-PDC kompensiert). Je AMOUNT
entstehen results.json/results.csv (Kanal 1/2, report_dir) plus ein
aggregiertes analysis.json. Stellungsprovenanz (SHINE/MIX/TRIM) ist
nicht protokolliert.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import scarlett_test as measurement  # noqa: E402

BATCH_DEFAULT = ROOT / "reaper/testbench/2026-10-08 15_22_27/SSL GROUP 1"
STIMULUS_DEFAULT = ROOT / "test-results/dwarf-tones/runs/matrix-all-m2"
OUTPUT_DEFAULT = ROOT / "test-results/ssl-amount-20261008"
NAME_PATTERN = re.compile(r"matrix-(\d+) Amount")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=BATCH_DEFAULT)
    parser.add_argument("--stimulus-dir", type=Path, default=STIMULUS_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    args = parser.parse_args()

    plan = json.loads((args.stimulus_dir / "plan.json").read_text(encoding="utf-8"))
    stimulus_sha = sha256(args.stimulus_dir / "stimulus.wav")
    if stimulus_sha != plan["stimulus_sha256"]:
        raise SystemExit("Stimulus/Plan-Hashabweichung")

    renders = []
    for path in sorted(args.batch.glob("*.wav")):
        match = NAME_PATTERN.match(path.name)
        if match:
            renders.append((int(match.group(1)), path))
    if not renders:
        raise SystemExit(f"Keine AMOUNT-Renders in {args.batch}")

    report = dict(
        date="2026-10-08",
        host="REAPER 2.3.2 (64 bit), Testbench-Programm gs76-matrix-all-m2-stereo.wav",
        batch=str(args.batch.relative_to(ROOT)),
        stimulus=str(args.stimulus_dir.relative_to(ROOT)),
        stimulus_sha256=stimulus_sha,
        programme=dict(rate=plan["rate"], frames=plan["frames"], segments=len(plan["segments"])),
        provenance_gaps=[
            "SSL-Knopfstellungen (SHINE, MIX, INPUT/OUTPUT TRIM, HF+/LF+) nicht protokolliert; AMOUNT aus dem Dateinamen.",
            "MIX steht vermutlich nicht auf 100 % WET (Grundwellengewinn im Befund pruefen).",
            "AMOUNT = 0 ist die kleinste gemessene Stellung, nicht notwendigerweise bypass.",
        ],
        runs=[],
    )
    args.output.mkdir(parents=True, exist_ok=True)
    for amount, path in renders:
        run_dir = args.output / f"amount-{amount}"
        run_dir.mkdir(exist_ok=True)
        entry = dict(amount=amount, file=str(path.relative_to(ROOT)),
                     sha256=sha256(path), channels={})
        for channel in (1, 2):
            results = measurement.analyze(args.stimulus_dir, path, channel,
                                          None, max_delay=2.0, report_dir=run_dir)
            sync = results["synchronization"]
            entry["channels"][str(channel)] = dict(
                valid=results["valid"],
                offset_frames=sync["offset_frames"],
                drift_ppm=sync.get("drift_ppm"),
                segments=[dict(
                    id=s["id"], group=s["group"], frequency_hz=s["frequency_hz"],
                    peak_dbfs=s["peak_dbfs"], gain_db=s.get("gain_db"),
                    thd_percent=s.get("thd_percent"), valid=s.get("valid"),
                    harmonic_dbc=s.get("harmonic_dbc"),
                ) for s in results["segments"]],
            )
        report["runs"].append(entry)
        seg1k = entry["channels"]["1"]["segments"][0]
        seg20 = entry["channels"]["1"]["segments"][1]
        print(f"AMOUNT {amount:>3}: Offset {entry['channels']['1']['offset_frames']} Frames, "
              f"1 kHz {seg1k['gain_db']:+.3f} dB / Klirr {seg1k['thd_percent']:.4f} %, "
              f"20 Hz {seg20['gain_db']:+.3f} dB / Klirr {seg20['thd_percent']:.4f} %")

    target = args.output / "analysis.json"
    measurement.write_json(target, report)
    print(f"Aggregiert: {len(report['runs'])} Runs -> {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
