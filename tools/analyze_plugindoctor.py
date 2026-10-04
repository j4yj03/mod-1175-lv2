#!/usr/bin/env python3
"""Summarise the original PluginDoctor graph exports without altering them.

Reads all graphs, including both mono output copies. Optional numpy enables
IR/FFT checks; --probe runs the current native DSP for a separate crosscheck.
Screenshot-derived settings are evidence, not settings inferred from filenames.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = {
    1: dict(input=0.0, output=0.0, attack=3.0, release=5.0, ratio="4:1", colour=100.0, compression=True),
    2: dict(input=24.0, output=-11.2, attack=1.0, release=7.0, ratio="All Buttons", colour=100.0, compression=True),
    3: dict(input=24.0, output=-11.2, attack=1.0, release=7.0, ratio="All Buttons", colour=0.0, compression=True),
    4: dict(input=0.0, output=0.0, attack=1.0, release=1.0, ratio="All Buttons", colour=100.0, compression=False),
    5: dict(input=15.6, output=-15.6, attack=1.0, release=1.0, ratio="All Buttons", colour=100.0, compression=False),
    6: dict(input=-15.6, output=15.6, attack=7.0, release=7.0, ratio="20:1", colour=0.0, compression=True),
}
LINEAR_VARIANTS = {
    7: dict(experiment=7, file="Clipboard01_4_to1_ratio.txt", ratio="4:1"),
    8: dict(experiment=7, file="Clipboard01_all_Buttons.txt", ratio="All Buttons"),
}
FREQUENCIES = (20, 100, 1000, 5000, 10000, 15000, 18000, 20000)


def read_graphs(path):
    graphs = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("Graph #"):
            graphs.append([])
        elif line.strip():
            fields = line.split()
            if len(fields) != 2 or not graphs:
                raise ValueError(f"Invalid graph data: {path}:{number}")
            x, y = map(float, fields)
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError(f"Non-finite graph data: {path}:{number}")
            graphs[-1].append((x, y))
    if not graphs or any(not g for g in graphs):
        raise ValueError(f"Empty graph: {path}")
    return graphs


def interpolate(graph, x):
    import bisect
    i = bisect.bisect_left([row[0] for row in graph], x)
    if i == 0:
        return graph[0][1]
    if i == len(graph):
        return graph[-1][1]
    a, b = graph[i - 1], graph[i]
    return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])


def median(values):
    import statistics
    return statistics.median(values)


def regression(graph, lo, hi):
    rows = [(x, y) for x, y in graph if lo <= x <= hi]
    mean_x = sum(x for x, _ in rows) / len(rows)
    mean_y = sum(y for _, y in rows) / len(rows)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in rows) / sum((x - mean_x) ** 2 for x, _ in rows)
    return dict(input_range_db=[lo, hi], output_slope=slope, effective_ratio=1.0 / slope)


def linear_summary(graph):
    base = interpolate(graph, 1000)
    band = [row for row in graph if 20 <= row[0] <= 20000]
    peak = max(band, key=lambda row: row[1])
    minimum = min(band, key=lambda row: row[1])
    return dict(
        points=[dict(hz=f, output_fft_db=interpolate(graph, f), relative_to_1khz_db=interpolate(graph, f) - base) for f in FREQUENCIES],
        peak_20_20000=dict(hz=peak[0], db=peak[1], relative_to_1khz_db=peak[1] - base),
        minimum_20_20000=dict(hz=minimum[0], db=minimum[1], relative_to_1khz_db=minimum[1] - base),
        range_20_20000_db=peak[1] - minimum[1],
        peak_20000_22050=dict(zip(("hz", "db"), max((row for row in graph if 20000 <= row[0] <= 22050), key=lambda row: row[1]))),
    )


def harmonic_summary(spectrum):
    fundamental_hz, fundamental_db = max(spectrum, key=lambda row: row[1])
    bin_width = median([spectrum[i][0] - spectrum[i - 1][0] for i in range(1, len(spectrum))])
    partials = []
    for order in range(2, 9):
        window = [row for row in spectrum if abs(row[0] - order * fundamental_hz) < 1.5 * bin_width]
        if window:
            hz, db = max(window, key=lambda row: row[1])
            partials.append(dict(order=order, peak_bin_hz=hz, peak_dbfs=db, dbc=db - fundamental_db))
    thd = math.sqrt(sum(10.0 ** (p["dbc"] / 10.0) for p in partials))
    return dict(
        harmonic_fundamental=dict(peak_bin_hz=fundamental_hz, peak_dbfs=fundamental_db),
        harmonic_partials=partials,
        approximate_peak_bin_thd=dict(db=20 * math.log10(thd), percent=100 * thd, limitation="Peak-bin H2-H8 estimate, not a reimplementation of PluginDoctor THD/THD+N or a noise-floor measurement"),
    )


def extra_spectral_lines(spectrum):
    """Identify meaningful non-H1..H8 bins; folded-order labels are candidates.

    Exact FFT-bin indices avoid the slightly rounded/distorted exported Hz grid.
    A coherent periodic output does not uniquely distinguish all high orders
    from modulation; high-rate/oversampling convergence is still required.
    """
    fft_size, rate = 16384, 44100
    fundamental_bin = max(range(len(spectrum)), key=lambda i: spectrum[i][1]) + 1
    fundamental_db = spectrum[fundamental_bin - 1][1]
    aliases = []
    for order in (9, 11, 13, 15, 69, 71):
        folded = (order * fundamental_bin) % fft_size
        folded = min(folded, fft_size - folded)
        if 0 < folded <= len(spectrum):
            hz, db = spectrum[folded - 1]
            aliases.append(dict(
                candidate_order=order, fft_bin=folded,
                exact_bin_frequency_hz=folded * rate / fft_size,
                exported_bin_frequency_hz=hz, peak_dbfs=db, dbc=db - fundamental_db,
            ))
    excluded = {k for order in range(1, 9) for k in range(order * fundamental_bin - 3, order * fundamental_bin + 4)}
    candidates = []
    for i in range(1, len(spectrum) - 1):
        x, y = spectrum[i]
        if (i + 1 not in excluded and 20 <= x <= 20000 and y > -120.0 and
                y >= spectrum[i - 1][1] and y > spectrum[i + 1][1]):
            candidates.append(dict(fft_bin=i + 1, hz=x, peak_dbfs=y, dbc=y - fundamental_db))
    result = dict(
        folded_harmonic_candidates=aliases,
        largest_other_local_peaks_20_20000=sorted(candidates, key=lambda p: p["peak_dbfs"], reverse=True)[:8],
        limitation="Candidate folded harmonic mapping, not proof of the source order of every bin. Extra lines include gain modulation; high-rate reference needed for alias assessment.",
    )
    return result


def crosscheck(probe, scenario, exported_ir, exported_linear, np, delta_db):
    # Screenshot excitation differs: +6.45 dB in 1..3, 0 dB in 4..7.
    # Repeated impulses, rather than only the first, reproduce steady history.
    amplitude = 10.0 ** (delta_db / 20.0)
    text = subprocess.check_output([str(probe.resolve()), str(scenario), repr(amplitude), "10"], text=True)
    rendered = np.asarray([float(line) for line in text.splitlines()])
    if len(rendered) != 16384:
        raise ValueError("Native probe must emit 16384 samples")
    fft_db = 20.0 * np.log10(np.maximum(1.0e-15, np.abs(np.fft.rfft(rendered))))
    frequencies = np.fft.rfftfreq(len(rendered), 1.0 / 44100.0)
    reference_db = np.asarray([y for x, y in exported_linear if 20 <= x <= 20000])
    reference_hz = np.asarray([x for x, y in exported_linear if 20 <= x <= 20000])
    predicted = np.interp(reference_hz, frequencies, fft_db)
    result = dict(
        scenario="44100 Hz; periodic delta every 16384 samples; 10 periods; screenshot settings",
        delta_amplitude=amplitude,
        max_fft_error_20_20000_db=float(np.max(np.abs(reference_db - predicted))),
        rms_fft_error_20_20000_db=float(np.sqrt(np.mean((reference_db - predicted) ** 2))),
        limitation="Steady periodic excitation with screenshot parameters; spectrum agreement does not independently establish capture identity, hardware fidelity or latency",
    )
    if exported_ir is not None:
        reference = np.asarray([row[1] for row in exported_ir])
        if len(reference) != len(rendered):
            raise ValueError("Exported IR length differs from native probe")
        scale = float(np.dot(reference, rendered) / np.dot(rendered, rendered))
        result.update(
            assumed_impulse_offset_samples=1020,
            raw_peak_sample_error=float(np.max(np.abs(reference - rendered))),
            raw_rms_sample_error=float(np.sqrt(np.mean((reference - rendered) ** 2))),
            fitted_constant_scale=scale,
            scaled_peak_sample_error=float(np.max(np.abs(reference - scale * rendered))),
            impulse_alignment_limitation="Chosen placement and fitted scale validate shape, not independently measured latency",
        )
    return result


def sine_crosscheck(probe, scenario, summary, np):
    size, rate, fundamental_bin = 16384, 44100, 935
    frequency = rate * fundamental_bin / size
    amplitude = 10.0 ** (-0.32 / 20.0)
    text = subprocess.check_output([str(probe.resolve()), str(scenario), repr(amplitude), "10", "tone", repr(frequency)], text=True)
    samples = np.asarray([float(line) for line in text.splitlines()])
    if len(samples) != size:
        raise ValueError("Native tone probe must emit 16384 samples")
    magnitudes = 2.0 * np.abs(np.fft.rfft(samples)) / size
    db = 20.0 * np.log10(np.maximum(1e-15, magnitudes))
    fundamental = float(db[fundamental_bin])
    partials = []
    errors = []
    for reference in summary["harmonic_partials"]:
        order = reference["order"]
        value = float(db[order * fundamental_bin] - fundamental)
        meaningful = reference["peak_dbfs"] > -120.0
        if meaningful:
            errors.append(abs(value - reference["dbc"]))
        partials.append(dict(order=order, native_dbc=value, exported_dbc=reference["dbc"], above_comparison_floor=meaningful))
    thd = float(math.sqrt(sum(magnitudes[order * fundamental_bin] ** 2 for order in range(2, 9))) / magnitudes[fundamental_bin])
    ninth_bin = size - 9 * fundamental_bin
    return dict(
        coherent_frequency_hz=frequency,
        input_peak_dbfs=-0.32,
        settling_samples=9 * size,
        native_fundamental_dbfs=fundamental,
        exported_fundamental_dbfs=summary["harmonic_fundamental"]["peak_dbfs"],
        fundamental_error_db=fundamental - summary["harmonic_fundamental"]["peak_dbfs"],
        partials=partials,
        maximum_harmonic_error_above_minus120_dbfs_dbc=max(errors) if errors else None,
        native_h2_h8_thd_percent=100.0 * thd,
        native_h2_h8_thd_db=20.0 * math.log10(thd),
        ninth_folded_bin=dict(fft_bin=ninth_bin, hz=ninth_bin * rate / size,
                             native_dbfs=float(db[ninth_bin]), native_dbc=float(db[ninth_bin] - fundamental)),
        limitation="Coherent steady sine, unwindowed native FFT; no alias/THD+N certification and no comparison of numerically absent partials below -120 dBFS",
    )


def analyse(directory, probe=None):
    try:
        import numpy as np
    except ImportError:
        np = None
    if probe and np is None:
        raise RuntimeError("--probe needs numpy for spectral crosschecks")
    report = dict(
        host="PluginDoctor 2.3.2 (64-bit), Cockos ReaJS, GreenStripe76-Mono.jsfx (screenshots)",
        samplerate_inferred_hz=44100,
        samplerate_evidence="2.69198 Hz FFT bin spacing with FFT size 16384; 0.02268 ms IR spacing",
        test_frequency_from_screenshot_hz=2516.7,
        ramp_step_seconds_from_screenshot=1.5,
        harmonic_input_dbfs_from_screenshot=-0.32,
        linear_delta_db_from_screenshot_by_experiment={str(n): 6.45 if n <= 3 else 0.0 for n in range(1, 8)},
        raw_capture_files=[],
        experiments=[],
        additional_linear_curves=[],
        analysed_graph_files=[],
    )
    if probe:
        report["native_probe_provenance"] = dict(
            executable_sha256=hashlib.sha256(probe.read_bytes()).hexdigest(),
            source_sha256=hashlib.sha256((ROOT / "tools/measurement_probe.cpp").read_bytes()).hexdigest(),
            dsp_header_sha256=hashlib.sha256((ROOT / "src/dsp/GreenStripe.hpp").read_bytes()).hexdigest(),
            model_sha256=hashlib.sha256((ROOT / "data/model.json").read_bytes()).hexdigest(),
            numeric_domain="Current C++11 native core with double samples/states; no float port quantisation in this diagnostic",
        )
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in (".txt", ".jpg"):
            raw = path.read_bytes()
            report["raw_capture_files"].append(dict(path=str(path.relative_to(directory)), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    for n in SETTINGS:
        path = directory / f"Versuch {n}"
        if not path.is_dir():
            continue
        dynamics = read_graphs(path / f"dynamics{n}.txt")
        linear = read_graphs(path / f"linear{n}.txt")
        impulse_path = path / f"IR{n}.txt"
        impulse = read_graphs(impulse_path) if impulse_path.exists() else None
        hammerstein_path = path / f"hammerstein{n}.txt"
        if not hammerstein_path.exists():
            hammerstein_path = path / f"hamemrstein{n}.txt"
        hammerstein = read_graphs(hammerstein_path)
        harmonic_path = path / f"harmonics{n}.txt"
        if not harmonic_path.exists():
            harmonic_path = path / f"hamonics{n}.txt"
        harmonics = read_graphs(harmonic_path)
        report["analysed_graph_files"].extend(str(p.relative_to(directory)) for p in
            (path / f"dynamics{n}.txt", path / f"linear{n}.txt", hammerstein_path, harmonic_path))
        if impulse:
            report["analysed_graph_files"].append(str(impulse_path.relative_to(directory)))
        d = dynamics[0]
        base_gain = median([y - x for x, y in d if -90 <= x <= -60])
        settings = dict(SETTINGS[n], mix=100.0, enabled=True, variant="Mono")
        curve = linear[0]
        spectrum_summary = harmonic_summary(harmonics[0])
        linear_stats = linear_summary(curve)
        delta_db = 6.45 if n <= 3 else 0.0
        fits = []
        for lo, hi in ((-12, 0), (-6, 0), (-2, 0)):
            fit = regression(d, lo, hi)
            fit["interpretation"] = "working compressor: may include the knee" if settings["compression"] else "saturation slope; NOT dynamic compressor ratio"
            fits.append(fit)
        experiment = dict(
            number=n,
            screenshot_settings=settings,
            graph_counts=dict(linear=len(linear), harmonics=len(harmonics), dynamics=len(dynamics), impulse=len(impulse) if impulse else 0, hammerstein=len(hammerstein)),
            mono_output_copies_identical={name: graphs[0] == graphs[1] for name, graphs in (("linear", linear), ("dynamics", dynamics), ("impulse", impulse)) if graphs},
            linear_delta_db_from_screenshot=delta_db,
            dynamics_kind="stationary input/output ramp; not an attack/release time trace",
            small_signal_gain_db=base_gain,
            first_input_db_for_relative_reduction={str(limit): next((x for x, y in d if x + base_gain - y >= limit), None) for limit in (0.1, 1.0, 3.0)},
            reduction_interpretation="relative output reduction, NOT explicit controller GR when compression is disabled",
            ratios=fits,
            transfer_points=[dict(input_db=x, output_db=interpolate(d, x), reduction_vs_low_level_gain_db=x + base_gain - interpolate(d, x)) for x in (-36, -24, -18, -12, -6, 0)],
            delta_spectrum=linear_stats["points"],
            delta_peak_20_20000=linear_stats["peak_20_20000"],
            delta_minimum_20_20000=linear_stats["minimum_20_20000"],
            delta_range_20_20000_db=linear_stats["range_20_20000_db"],
            delta_peak_20000_22050=linear_stats["peak_20000_22050"],
            hammerstein_at_1khz=[dict(order=i + 1, db=interpolate(g, 1000)) for i, g in enumerate(hammerstein)],
            duplicate_first_two_screenshots=(path / "Clipboard01.jpg").read_bytes() == (path / "Clipboard02.jpg").read_bytes(),
            **spectrum_summary,
            extra_spectral_lines=extra_spectral_lines(harmonics[0]),
        )
        if impulse:
            sample = max(enumerate(impulse[0]), key=lambda item: abs(item[1][1]))
            experiment["impulse_peak"] = dict(index=sample[0], exported_time_ms=sample[1][0], amplitude=sample[1][1], limitation="Export includes unknown host/plot offset; this is not plugin latency")
        if np is not None and impulse:
            fft = 20 * np.log10(np.maximum(1e-15, np.abs(np.fft.rfft([y for x, y in impulse[0]]))))
            delta = [abs(y - fft[i + 1]) for i, (x, y) in enumerate(curve) if 20 <= x <= 20000]
            experiment["quantised_ir_fft_max_difference_20_20000_db"] = float(max(delta))
        if probe:
            experiment["native_periodic_impulse_crosscheck"] = crosscheck(probe, n, impulse[0] if impulse else None, curve, np, delta_db)
            experiment["native_sine_crosscheck"] = sine_crosscheck(probe, n, spectrum_summary, np)
        report["experiments"].append(experiment)
    for scenario, definition in LINEAR_VARIANTS.items():
        path = directory / f"Versuch {definition['experiment']}" / definition["file"]
        if not path.exists():
            continue
        graphs = read_graphs(path)
        report["analysed_graph_files"].append(str(path.relative_to(directory)))
        summary = linear_summary(graphs[0])
        result = dict(
            experiment=definition["experiment"], file=definition["file"], native_scenario=scenario,
            screenshot_settings=dict(input=-6.0, output=6.0, attack=7.0, release=1.0, ratio=definition["ratio"], colour=0.0, compression=True, mix=100.0, enabled=True, variant="Mono"),
            kind="Delta magnitude spectrum, NOT attack/release time curve",
            linear_delta_db_from_screenshot=0.0,
            graph_count=len(graphs), mono_output_copies_identical=graphs[0] == graphs[1],
            delta_spectrum=summary["points"],
            delta_peak_20_20000=summary["peak_20_20000"],
            delta_minimum_20_20000=summary["minimum_20_20000"],
            delta_range_20_20000_db=summary["range_20_20000_db"],
            delta_peak_20000_22050=summary["peak_20000_22050"],
        )
        if probe:
            result["native_periodic_impulse_crosscheck"] = crosscheck(probe, scenario, None, graphs[0], np, 0.0)
        report["additional_linear_curves"].append(result)
    if probe:
        text = subprocess.check_output([str(probe.resolve()), "0", "0.01", "10"], text=True)
        samples = np.asarray([float(line) for line in text.splitlines()])
        fft_db = 20 * np.log10(np.maximum(1e-15, np.abs(np.fft.rfft(samples)) / 0.01))
        freqs = np.fft.rfftfreq(len(samples), 1.0 / 44100)
        report["native_identity_chain"] = dict(
            colour=0, compression=False, frequency_range_hz=[20, 20000],
            maximum_gain_deviation_db=float(np.max(np.abs(fft_db[(freqs >= 20) & (freqs <= 20000)]))),
            limitation="Current native implementation; does not prove the unidentified external capture binary or ReaJS version",
        )
        report["native_colour_only_small_signal"] = []
        for scenario in (4, 5):
            amplitude = 1.0e-6
            text = subprocess.check_output([str(probe.resolve()), str(scenario), repr(amplitude), "10"], text=True)
            samples = np.asarray([float(line) for line in text.splitlines()])
            fft_db = 20 * np.log10(np.maximum(1e-15, np.abs(np.fft.rfft(samples)) / amplitude))
            freqs = np.fft.rfftfreq(len(samples), 1.0 / 44100)
            report["native_colour_only_small_signal"].append(dict(
                scenario=scenario, peak_amplitude=amplitude,
                normalised_magnitude_points=[dict(hz=f, db=float(np.interp(f, freqs, fft_db))) for f in FREQUENCIES],
                limitation="Current native infinitesimal/low-level response, not an external measurement; do not confuse with the 0 dB nonlinear delta in captures",
            ))
    report["unanalysed_graph_files"] = sorted(
        record["path"] for record in report["raw_capture_files"]
        if record["path"].endswith(".txt") and record["path"] not in report["analysed_graph_files"])
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, nargs="?", default=ROOT / "evaluation_plugindoc")
    parser.add_argument("--probe", type=Path, help="Native measurement_probe executable for current-core periodic impulse and coherent sine tests")
    parser.add_argument("--output", type=Path, help="Write a separate JSON report; original capture files remain untouched")
    args = parser.parse_args()
    report = analyse(args.directory, args.probe)
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Analysed {len(report['raw_capture_files'])} capture files; report: {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
