#!/usr/bin/env python3
"""Tabellen, Diagnose-Koeffizienten und Abbildungen aus den SPICE-Messdateien."""

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from run_simulations import HERE, MODELS, read_csv, sha256, write_json, write_text


COLORS = ("#236c40", "#bd6b17", "#3066a0", "#8b438d")


def numeric_rows(path):
    rows = read_csv(path)
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = float(value)
            except ValueError:
                pass
    return rows


def select(rows, frequency, level, tag=None):
    return next(row for row in rows if row["frequency_hz"] == frequency and
                row["source_dbv"] == level and (tag is None or row["tag"] == tag))


def resolved(row, harmonic):
    value = row[f"h{harmonic}_dbc"]
    return f"{value:.2f}" if value > -120 else "< −120"


def save_plot(fig, name):
    fig.tight_layout()
    fig.savefig(HERE / "plots" / name, metadata={"Date": None})
    plt.close(fig)


def main():
    (HERE / "plots").mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9, "svg.hashsalt": "gs76-spice-20261005",
                         "axes.grid": True, "grid.alpha": 0.25})
    manifest = json.loads((HERE / "run-manifest.json").read_text(encoding="utf-8"))
    diagnostic = json.loads((HERE / "diagnostic-manifest.json").read_text(encoding="utf-8"))
    diagnostics = numeric_rows(HERE / "diagnostic-results.csv")
    main_rows = {model: numeric_rows(HERE / (model + "-results.csv")) for model in MODELS}
    coefficients = dict(kind="eigene Offline-Rechnung; keine freigegebenen DSP-Koeffizienten",
                        original_sha256=manifest["original_sha256"], models={})
    quality = {"models": {}}
    text = ["# Messwerttabellen", "", "Automatisch aus `*-results.csv` erzeugt.", "",
            "Alle Werte sind **Fenstermessungen**, keine bestätigten eingeschwungenen Kennlinien.",
            "Quelle: 200 Ω differentiell, Last: 8 Ω, DC-Anregung: 0 V. Frequenzen in Hz,",
            "Pegel in dBV RMS **vor** dem Quellenwiderstand. Pro Zeile verlinkte Netlist;",
            "exakte Zeitfenster, Primärpegel, Peaks, Roh-Harmonische und Driftwerte in der CSV.",
            "`K` = Kleinsignal-Gain minus Großsignal-Gain; negative Werte = Expansion.",
            "`H` und Phase beziehen sich auf die Quelle. H3/H5 aus analogen adaptiven Zeitpunkten;",
            "unter −120 dBc keine belastbare Klirraussage. DC = Mittelwert des gespeicherten",
            "nativen Fensters (leicht kürzer als zehn volle Perioden), kein stationärer Offset.", ""]
    for model, config in MODELS.items():
        rows = main_rows[model]
        diag = [row for row in diagnostics if row["model"] == model]
        growth = next(item for item in diagnostic["checks"] if
                      item["model"] == model and item["check"] == "unstable_zero_input")
        at_1k = select(rows, 1000, 6)
        p = manifest["parameters"][model]
        f_ref = math.sqrt(70 * 15000) if model == "GCOT-SE-01" else math.sqrt(20 * 20000)
        phi_old = (p["C"] * 2 * math.pi * f_ref / p["a"]) ** (1 / (p["n"] - 1))
        reason = ("Kein zeitinvarianter Arbeitspunkt: instabiler Nullzustand; "
                  "kein identifizierter magnetischer Fluss; kein positives 1-dB-Knie im Hauptfenster.")
        coefficients["models"][model] = dict(
            stage=config["stage"], status="keine Skalar-Kalibrierung ableitbar",
            original_parameters=p,
            original_formula_arithmetic_only={"reference_frequency_hz": f_ref,
                                               "phi_number": phi_old,
                                               "origin": "Auftragsformel, keine Messung, Einheit nicht belegt"},
            phi_k_from_simulation=None, phi_k_deviation_percent=None, knee_width_db=None,
            fitted_saturation_exponent=None, stationary_dc_offset_v=None,
            unavailable_reason=reason,
            measured_unstable_growth_per_s=growth["measured_growth_per_s"],
            measured_growth_time_constant_s=1 / growth["measured_growth_per_s"],
            growth_measurement=growth["netlist"],
            short_window_measurement=dict(csv=model + "-results.csv", case_id=at_1k["case_id"],
                                          gain_source_db=at_1k["gain_source_db"],
                                          compression_source_db=at_1k["compression_source_db"],
                                          capacitor_voltage_peak_v=at_1k["cap1_peak_v"]),
            diagnostic_only_state_coefficients=dict(
                source="algebraische KCL-Reduktion, keine gefitteten Messwerte",
                inverse_c=1 / p["C"],
                inverse_n_half=1 / (p["Np"] if config["topology"] == "se" else p["Np"] / 2)))
        error_keys = ("gain_source_db", "phase_source_deg", "h3_dbc", "h5_dbc")
        errors = {key: [] for key in error_keys}
        for refined in (row for row in diag if row["tag"] == "refined"):
            base = select(rows, refined["frequency_hz"], refined["source_dbv"])
            for key in error_keys:
                if key in ("h3_dbc", "h5_dbc") and min(base[key], refined[key]) <= -120:
                    continue
                errors[key].append(abs(base[key] - refined[key]))
        base_20 = select(rows, 20, 6)
        quality["models"][model] = dict(
            row_count=len(rows),
            refinement_max_abs_errors={key: max(values) for key, values in errors.items()},
            load_max_gain_change_db=max(abs(row["gain_source_db"] - base_20["gain_source_db"])
                                        for row in diag if row["tag"].startswith("load")),
            gear_max_gain_change_db=max(abs(row["gain_source_db"] -
                                            select(rows, row["frequency_hz"], 6)["gain_source_db"])
                                        for row in diag if row["tag"] == "gear"),
            growth_rate_relative_error=abs(growth["measured_growth_per_s"] /
                                           growth["analytic_pole_per_s"] - 1),
            arithmetic_vs_ac_max_abs_gain_db=0)
        ac = numeric_rows(HERE / (model + "-ac.csv"))
        nh = p["Np"] if config["topology"] == "se" else p["Np"] / 2
        gain = p["Ns"] / (200 + (p["R"] if config["topology"] == "se" else 2 * p["R"]))
        gain_errors = []
        for row in ac:
            q = p["C"] * nh * (2 * math.pi * row["frequency_hz"]) ** 2
            expected = 20 * math.log10(gain * q / (q + 1))
            gain_errors.append(abs(row["gain_source_db"] - expected))
        quality["models"][model]["arithmetic_vs_ac_max_abs_gain_db"] = max(gain_errors)
        text += [f"## {config['stage']} — {model}", "",
                 f"Messdatei: [{model}-results.csv]({model}-results.csv).", "",
                 "| f | dBV | H dB | Phase ° | K dB | H3 dBc | H5 dBc | H3−H5 dB | DC V |",
                 "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for row in rows:
            difference = (f"{row['h3_minus_h5_db']:.2f}" if
                          min(row["h3_dbc"], row["h5_dbc"]) > -120 else "n. b.")
            text.append(f"| [{row['frequency_hz']:g}]({row['netlist']}) | {row['source_dbv']:+g} | "
                        f"{row['gain_source_db']:.6f} | {row['phase_source_deg']:.6f} | "
                        f"{row['compression_source_db']:.6f} | {resolved(row, 3)} | {resolved(row, 5)} | "
                        f"{difference} | {row['output_dc_mean_v']:.6g} |")
        text.append("")
    write_text(HERE / "MESSWERTE.md", "\n".join(text))
    write_json(HERE / "coefficients.json", coefficients)
    write_json(HERE / "quality-summary.json", quality)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for (model, config), color in zip(MODELS.items(), COLORS):
        rows = [row for row in main_rows[model] if row["frequency_hz"] == 1000]
        x = [row["source_dbv"] for row in rows]
        for axis, key in zip(axes.flat, ("gain_source_db", "compression_source_db", "h3_dbc", "h5_dbc")):
            y = [max(-120, row[key]) if key.startswith("h") else row[key] for row in rows]
            axis.plot(x, y, marker=".", color=color, label=config["stage"])
            axis.set_xlabel("Quellpegel (dBV RMS)")
    for axis, label in zip(axes.flat, ("|H1| Quelle → Ausgang (dB)", "K (dB); negativ = Expansion",
                                       "H3/H1 (dBc; Boden −120)", "H5/H1 (dBc; Boden −120)")):
        axis.set_ylabel(label)
    axes[0, 0].legend()
    fig.suptitle("1 kHz, Messfenster 40–50 ms — kein stationärer Kennlinienfit")
    save_plot(fig, "pegel_und_klirr.svg")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for (model, config), color in zip(MODELS.items(), COLORS):
        for level, linestyle in ((-30, "--"), (6, "-")):
            rows = [select(main_rows[model], 20, level)] + [select(
                [row for row in diagnostics if row["model"] == model], 20, level, tag)
                for tag in ("late5", "late20")]
            times = [(row["tstart_s"] + row["tstop_s"]) * 0.5 for row in rows]
            for axis, key in zip(axes, ("compression_source_db", "output_dc_mean_v")):
                axis.plot(times, [row[key] for row in rows], linestyle=linestyle,
                          marker="o", color=color, label=f"{config['stage']} {level:+} dBV")
                axis.set_xlabel("Mitte des 0,5-s-Messfensters (s)")
    axes[0].set_ylabel("K (dB), Quelle → Ausgang")
    axes[1].set_ylabel("Fenstermittelwert am Ausgang (V)")
    axes[0].legend(fontsize=7, ncols=2)
    fig.suptitle("20 Hz: gleiche Anregung, unterschiedliche Beobachtungszeit")
    save_plot(fig, "zeitabhaengigkeit.svg")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    with np.load(HERE / "diagnostic-waveforms.npz") as archive:
        for (model, config), color in zip(MODELS.items(), COLORS):
            key = model + "__zero_initial__f20__m30dBV__native"
            data = archive[key]
            axes[0].semilogy(data[:, 0], np.abs(data[:, 4]), color=color, label=config["stage"])
            axes[1].plot(data[:, 0], data[:, 3], color=color, label=config["stage"])
    for axis in axes:
        axis.set_xlabel("Zeit (s)")
    axes[0].set_ylabel("|u| = Spannung an ursprünglichem Cc (V)")
    axes[1].set_ylabel("Ausgangsspannung (V)")
    axes[0].legend()
    fig.suptitle("Nullsignal, nur Anfangsstörung u(0) = 10⁻⁷ V; kein magnetischer Bias")
    save_plot(fig, "nullsignal_instabilitaet.svg")

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    with np.load(HERE / "diagnostic-waveforms.npz") as late:
        for (model, config), axis in zip(MODELS.items(), axes.flat):
            row = select(main_rows[model], 20, 6)
            with np.load(HERE / (model + "-waveforms.npz")) as main_archive:
                data = main_archive[row["case_id"] + "__native"]
            for samples, stop, label in ((data, 1.5, "1,45–1,50 s"),
                    (late[model + "__late20__f20__p6dBV__native"], 20.5, "20,45–20,50 s")):
                selected = samples[samples[:, 0] >= stop - 0.05]
                axis.plot((selected[:, 0] - (stop - 0.05)) * 1000, selected[:, 3], label=label)
            axis.set_title(config["stage"])
            axis.set_xlabel("Zeit im letzten Sinuszyklus (ms)")
            axis.set_ylabel("Ausgang (V)")
            axis.legend()
    fig.suptitle("Wellenformen bei 20 Hz / +6 dBV, identische Amplitude und Last")
    save_plot(fig, "wellenformen.svg")

    input_files = [HERE / "run-manifest.json", HERE / "diagnostic-manifest.json",
                   HERE / "diagnostic-results.csv"] + [HERE / (m + "-results.csv") for m in MODELS]
    write_json(HERE / "analysis-provenance.json", dict(
        script_sha256=sha256(Path(__file__)),
        input_sha256={p.name: sha256(p) for p in input_files},
        numpy=np.__version__, matplotlib=matplotlib.__version__))
    print("MESSWERTE.md, coefficients.json, quality-summary.json und vier SVGs erzeugt.")
    print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    main()
