#!/usr/bin/env python3
"""Prüft Matrix, Provenienz, Wellenformen und vier erneut ausgeführte Einstiegsdecks."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import numpy as np

from run_simulations import (HERE, MODELS, SOURCE, FREQUENCIES, LEVELS, RATE,
                             ac_rows, analyze, make_case, read_csv, sha256, write_json,
                             write_text)


def model_parameters(text, name):
    block = re.search(r"(?m)^\.SUBCKT " + name + r"\b(.*?)^\.ENDS", text, re.S).group(1)
    return {key: float(value) for key, value in
            re.findall(r"\b(C|a|n|R|b|m|Np|Ns)\s*=\s*([\deE.+-]+)", block)}


def verify_hash_list():
    count = 0
    for line in (HERE / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, filename = line.split("  ", 1)
        assert sha256(HERE / filename) == expected, filename
        count += 1
    print(f"SHA256SUMS: {count} Dateien stimmen überein.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ngspice", default=shutil.which("ngspice"))
    parser.add_argument("--check-hashes", action="store_true")
    args = parser.parse_args()
    if args.check_hashes:
        verify_hash_list()
        return
    if not args.ngspice:
        parser.error("--ngspice fehlt")
    runs = json.loads((HERE / "run-manifest.json").read_text(encoding="utf-8"))
    diagnostics = json.loads((HERE / "diagnostic-manifest.json").read_text(encoding="utf-8"))
    quality = json.loads((HERE / "quality-summary.json").read_text(encoding="utf-8"))
    coefficients = json.loads((HERE / "coefficients.json").read_text(encoding="utf-8"))
    analysis = json.loads((HERE / "analysis-provenance.json").read_text(encoding="utf-8"))
    assert runs["original_sha256"] == sha256(SOURCE) == diagnostics["original_sha256"]
    assert runs["adapted_sha256"] == sha256(HERE / "xformer-ngspice.inc")
    assert runs["script_sha256"] == sha256(HERE / "run_simulations.py")
    assert diagnostics["script_sha256"] == sha256(HERE / "run_diagnostics.py")
    assert diagnostics["runner_sha256"] == sha256(HERE / "run_simulations.py")
    assert analysis["script_sha256"] == sha256(HERE / "analyze_results.py")
    for filename, digest in analysis["input_sha256"].items():
        assert sha256(HERE / filename) == digest, filename
    for model in MODELS:
        original = model_parameters(SOURCE.read_text(encoding="utf-8"), model)
        assert original == runs["parameters"][model]
        for filename in ("xformer-ddt.inc", "xformer-ngspice.inc"):
            assert original == model_parameters((HERE / filename).read_text(encoding="utf-8"), model)
        result = coefficients["models"][model]
        for unknown in ("phi_k_from_simulation", "phi_k_deviation_percent", "knee_width_db",
                        "fitted_saturation_exponent", "stationary_dc_offset_v"):
            assert result[unknown] is None, (model, unknown)

    all_runs = runs["runs"] + diagnostics["runs"]
    assert len(all_runs) == 340
    assert sum(not run["aborted"] for run in all_runs) == 336
    assert sum(run["aborted"] for run in all_runs if run["tag"] == "literal") == 4
    assert len({run["case_id"] for run in all_runs}) == len(all_runs)
    for run in all_runs:
        name = run["case_id"]
        assert sha256(HERE / "netlists" / (name + ".cir")) == run["netlist_sha256"], name
        log = (HERE / "logs" / (name + ".log")).read_text(encoding="utf-8")
        has_error = bool(re.search(r"(?im)\baborted\b|timestep too small|^error", log))
        assert has_error == run["aborted"], name
    assert len(list((HERE / "netlists").glob("*.cir"))) == 340
    assert len(list((HERE / "logs").glob("*.log"))) == 340

    waveform_arrays, waveform_points = 0, 0
    for filename in list(HERE.glob("*-waveforms.npz")):
        with np.load(filename, allow_pickle=False) as archive:
            for key in archive.files:
                data = archive[key]
                assert data.ndim == 2 and data.shape[1] == 7 and data.shape[0] > 3, key
                assert np.all(np.isfinite(data)), key
                assert np.all(np.diff(data[:, 0]) > 0), key
                if key.endswith("__48k"):
                    steps = np.diff(data[:, 0]) * RATE
                    assert np.max(np.abs(steps - np.round(steps))) < 1e-6, key
                waveform_arrays += 1
                waveform_points += len(data)

    for model in MODELS:
        rows = read_csv(HERE / (model + "-results.csv"))
        assert len(rows) == 65
        assert {(float(row["frequency_hz"]), float(row["source_dbv"])) for row in rows} == \
            {(float(f), float(level)) for f in FREQUENCIES for level in LEVELS}
        for row in rows:
            assert (HERE / row["netlist"]).exists() and (HERE / row["log"]).exists()
            for key in ("gain_source_db", "gain_primary_db", "phase_source_deg", "h3_dbc",
                        "h5_dbc", "output_dc_mean_v", "cap1_peak_v", "compression_source_db"):
                assert np.isfinite(float(row[key])), (model, key)
        ac = read_csv(HERE / (model + "-ac.csv"))
        assert len(ac) == 601
        frequencies = np.array([float(row["frequency_hz"]) for row in ac])
        assert np.all(np.diff(frequencies) > 0)
        assert abs(frequencies[0] - 20) < 1e-9 and abs(frequencies[-1] - 20000) < 1e-6
        q = quality["models"][model]
        assert q["refinement_max_abs_errors"]["gain_source_db"] < 2e-7
        assert q["refinement_max_abs_errors"]["h3_dbc"] < 1e-3
        assert q["refinement_max_abs_errors"]["h5_dbc"] < 1e-3
        assert q["gear_max_gain_change_db"] < 1e-7
        assert q["load_max_gain_change_db"] < 1e-12
        assert q["arithmetic_vs_ac_max_abs_gain_db"] < 1e-11
        assert q["growth_rate_relative_error"] < 1e-4

    # Use the actual saved entry decks, rather than a duplicate reconstructed
    # circuit. Only the .include path is made absolute in the temporary copy.
    reruns = []
    for model in MODELS:
        deck_path = HERE / (model + ".cir")
        deck = deck_path.read_text(encoding="utf-8").replace(
            '.include "xformer-ngspice.inc"', f'.include "{HERE / "xformer-ngspice.inc"}"')
        with tempfile.TemporaryDirectory(prefix="gs76-verify-", dir="/tmp/opencode") as temp:
            work = Path(temp)
            write_text(work / "run.cir", deck)
            process = subprocess.run([args.ngspice, "-n", "-b", "-o", "run.log", "run.cir"],
                                     cwd=work, capture_output=True, text=True, timeout=120)
            log = (work / "run.log").read_text(encoding="utf-8")
            assert process.returncode == 0 and not re.search(
                r"(?im)\baborted\b|timestep too small|^error", log), model
            arrays = {kind: np.loadtxt(work / (model + "-" + kind + ".txt"), skiprows=1)
                      for kind in ("ac", "transient")}
            case = make_case(model, 1000, 0)
            assert abs(arrays["transient"][-1, 0] - case["stop_s"]) < 1e-12
            assert np.all(np.isfinite(arrays["transient"]))
            _, ref = ac_rows(model, case, arrays["ac"])
            measured, _ = analyze(case, arrays, ref)
            stored = next(row for row in read_csv(HERE / (model + "-results.csv")) if
                          float(row["frequency_hz"]) == 1000 and float(row["source_dbv"]) == 0)
            differences = {key: abs(measured[key] - float(stored[key])) for key in
                           ("gain_source_db", "phase_source_deg", "h3_dbc", "h5_dbc", "output_dc_mean_v")}
            assert differences["gain_source_db"] < 1e-6, model
            assert differences["phase_source_deg"] < 1e-4, model
            assert differences["output_dc_mean_v"] < 1e-7, model
            for harmonic in ("h3_dbc", "h5_dbc"):
                if float(stored[harmonic]) > -120:
                    assert differences[harmonic] < 1e-3, (model, harmonic)
            original_run = next(run for run in runs["runs"] if run["case_id"] == case["case_id"])
            digest = hashlib.sha256(arrays["transient"].astype("<f8").tobytes()).hexdigest()
            reruns.append(dict(model=model, netlist=deck_path.name,
                               netlist_sha256=sha256(deck_path), metrics_abs_differences=differences,
                               full_native_array_hash_equal=(digest == original_run["full_native_array_sha256"]),
                               result="PASS"))

    summary = dict(result="PASS: Messprozess/Artefakte; Modelle NICHT als stabil qualifiziert",
                   script_sha256=sha256(Path(__file__)),
                   models=4, main_points=260, diagnostic_points=76, literal_aborts=4,
                   canonical_deck_reruns=reruns,
                   parameters_unchanged=True, provenance_verified=True,
                   waveform_arrays=waveform_arrays, stored_waveform_points=waveform_points,
                   finite_monotonic_waveforms=True,
                   checks="vollständige Matrix; AC-Referenz; Zeitschritt; Gear; DDT; Last; instabile Eigenmode")
    write_json(HERE / "verification.json", summary)
    hashes = []
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.name != "SHA256SUMS":
            hashes.append(sha256(path) + "  " + str(path.relative_to(HERE)))
    write_text(HERE / "SHA256SUMS", "\n".join(hashes) + "\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    verify_hash_list()


if __name__ == "__main__":
    main()
