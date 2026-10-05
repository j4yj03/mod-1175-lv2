#!/usr/bin/env python3
"""Zusatzmessungen: Realisierung, Zeitschritt, Last, Einschwingen, Zustandsstabilität."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import math
from pathlib import Path
import shutil

import numpy as np

from run_simulations import (HERE, MODELS, SOURCE, ac_rows, adapt_model, analyze,
                             archive_waveforms, make_case, read_csv, run_ngspice, sha256,
                             write_csv, write_json)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ngspice", default=shutil.which("ngspice"))
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    if not args.ngspice:
        parser.error("--ngspice erforderlich")
    parameters = adapt_model()
    cases = []
    for model in MODELS:
        for frequency in (20, 1000, 20000):
            for level in (-30, 6):
                cases.append(make_case(model, frequency, level, tag="refined", refinement=2))
        for frequency in (20, 1000):
            cases.append(make_case(model, frequency, 6, tag="gear", method="gear"))
        for load in (4, 1000):
            cases.append(make_case(model, 20, 6, tag=f"load{load}", load=load))
        for rs in (20, 2000):
            cases.append(make_case(model, 20, 6, tag=f"rs{rs}", rs=rs))
        for start in (5, 20):
            for level in (-30, 6):
                cases.append(make_case(model, 20, level, tag=f"late{start}", start=start))
        # Only time behaviour is measured here, not a harmonic/transfer fit.
        case = make_case(model, 20, -30, tag="zero_initial", start=0, cycles=400,
                         initial_u=1e-7, zero_input=True)
        cases.append(case)
    rows, runs, waveforms, checks = [], [], {}, []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i, (case, arrays, info) in enumerate(pool.map(
                lambda case: run_ngspice(args.ngspice, case), cases)):
            model = case["model"]
            info["full_native_array_sha256"] = hashlib.sha256(
                arrays["transient"].astype("<f8").tobytes()).hexdigest()
            runs.append(dict(**case, **info))
            data = arrays["transient"]
            if case.get("zero_input"):
                p = parameters[model]
                nh = p["Np"] if MODELS[model]["topology"] == "se" else p["Np"] / 2
                pole = 1 / math.sqrt(p["C"] * nh)
                # Before saturation and before floating-point floor, growth is
                # cosh(pole*t); fit log(u) after the initial cosh transient.
                selected = (data[:, 0] > 3.5 / pole) & (np.abs(data[:, 4]) < 1e-3)
                rate = np.polyfit(data[selected, 0], np.log(np.abs(data[selected, 4])), 1)[0]
                checks.append(dict(check="unstable_zero_input", model=model,
                                   netlist="netlists/" + case["case_id"] + ".cir",
                                   analytic_pole_per_s=pole, measured_growth_per_s=float(rate),
                                   initial_cap_v=case["initial_u"],
                                   final_cap_v=float(data[-1, 4]),
                                   max_output_v=float(np.max(np.abs(data[:, 3])))))
                # Keep actual solver points over the entire 20 seconds. No
                # interpolation: roughly one point/ms plus both endpoints.
                stride = max(1, len(data) // 20000)
                chosen = np.unique(np.r_[0, np.arange(0, len(data), stride), len(data) - 1])
                waveforms[case["case_id"] + "__native"] = data[chosen]
            else:
                _, reference = ac_rows(model, case, arrays["ac"])
                row, sampled = analyze(case, arrays, reference)
                row["waveform_archive"] = "diagnostic-waveforms.npz"
                rows.append(row)
                waveforms.update(archive_waveforms(case, data, sampled))
            print(f"[{i + 1}/{len(cases)}] {case['case_id']}", flush=True)

    # Independent realization of the original DDT branches: compare AC and
    # successfully simulated 20-Hz time windows with the KCL-reduced circuit.
    for model in MODELS:
        for level in (-30, 6):
            case = make_case(model, 20, level, tag="ddt_equivalent")
            case, arrays, info = run_ngspice(args.ngspice, case, realization="ddt", timeout=45)
            runs.append(dict(**case, **info))
            entry = dict(check="ddt_equivalent", model=model, level_dbv=level,
                         netlist="netlists/" + case["case_id"] + ".cir", aborted=info["aborted"])
            reference_csv = read_csv(HERE / (model + "-ac.csv"))
            ref_output = np.array([complex(float(x["output_real_v"]), float(x["output_imag_v"]))
                                   for x in reference_csv])
            measured_output = arrays["ac"][:, 5] + 1j * arrays["ac"][:, 6]
            entry["ac_max_abs_error_v"] = float(np.max(np.abs(measured_output - ref_output)))
            if not info["aborted"]:
                _, reference = ac_rows(model, case, arrays["ac"])
                row, sampled = analyze(case, arrays, reference)
                main = [x for x in read_csv(HERE / (model + "-results.csv"))
                        if float(x["frequency_hz"]) == 20 and float(x["source_dbv"]) == level][0]
                entry["gain_error_db"] = row["gain_source_db"] - float(main["gain_source_db"])
                entry["h3_error_db"] = row["h3_dbc"] - float(main["h3_dbc"])
                entry["output_dc_error_v"] = row["output_dc_mean_v"] - float(main["output_dc_mean_v"])
                row["waveform_archive"] = "diagnostic-waveforms.npz"
                rows.append(row)
                waveforms.update(archive_waveforms(case, arrays["transient"], sampled))
            checks.append(entry)
            print(f"DDT check {case['case_id']}: {entry}", flush=True)

    write_csv(HERE / "diagnostic-results.csv", rows,
              ["Additional actual SPICE runs; definitions as in MODEL-results.csv.",
               "Late windows, time-step refinement, Gear2, load/source sensitivity, DDT equivalence."])
    np.savez_compressed(HERE / "diagnostic-waveforms.npz", **waveforms)
    write_json(HERE / "diagnostic-manifest.json",
               dict(script_sha256=sha256(Path(__file__)),
                    runner_sha256=sha256(HERE / "run_simulations.py"),
                    waveform_storage="first/last cycle; zero-input every ~1 ms, actual solver samples",
                    original_sha256=sha256(SOURCE), runs=runs, checks=checks))


if __name__ == "__main__":
    main()
