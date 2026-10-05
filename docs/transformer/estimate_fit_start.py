#!/usr/bin/env python3
"""Quellengebundene Startschätzungen, KEIN abgeschlossener Transformatorfit.

Nur Standardbibliothek. Die Rechnungen sind vereinfachte Ersatzbild- und
Einheitenprüfungen; keine SPICE-/DSP-/Hardwaremessung wird dadurch erzeugt.
"""

import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
SAUCE = HERE.parent / "sauce"


def parallel(a, b):
    return a * b / (a + b)


def dbu_to_rms(level):
    return 0.775 * 10 ** (level / 20)


def main():
    source_names = ("Audio-Transformers-Chapter.pdf", "ourdev_725050HHOGA4.pdf",
                    "PSW_WhitePaper_Download_Chapter_6.pdf")
    rg, rp, rs, rl = 600.0, 1450.0, 1550.0, 10000.0
    req_generator = parallel(rg + rp, rs + rl)
    req_terminal = parallel(rp, rs + rl)
    fc_from_20hz = 20 * math.sqrt(10 ** (0.04 / 10) - 1)
    half_power_hz = 100000.0
    # H(jw) = 1 / [1-(f/f0)^2+j*f/(f0*Q)]. Use 100 kHz half-power
    # (-3.0103 dB) and -0.05 dB at 20 kHz, not an absolute phase fit.
    ratio2 = (20000 / half_power_hz) ** 2
    denominator_20 = 10 ** (0.05 / 10)
    y2 = (ratio2 - (denominator_20 - 1)) / (ratio2 - ratio2**2)
    y = math.sqrt(y2)
    f0 = half_power_hz / math.sqrt(y)
    q = 1 / math.sqrt(2 + (1 - y2) / y)
    rms4 = dbu_to_rms(4)
    scale_terminal = math.sqrt(2) * rms4 / 10 ** (-18 / 20)
    source_calibration = (rg + rp + rs + rl) / (rp + rs + rl)
    rms20 = dbu_to_rms(20)
    lambda_terminal = math.sqrt(2) * rms20 / (2 * math.pi * 20)
    lambda_core = lambda_terminal * (rs + rl) / (rp + rs + rl)
    output = {
        "status": "UNGEFITTETE Startschätzungen; keine freigegebenen DSP-Parameter",
        "date": "2026-10-05",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "pdf_sha256": {name: hashlib.sha256((SAUCE / name).read_bytes()).hexdigest()
                       for name in source_names},
        "recommended_reference": {
            "name": "Jensen JT-11P-1",
            "source": "Audio-Transformers-Chapter.pdf, lokale PDF-Seiten 28–29, eingebetteter Stand 1/01",
            "reason": "1:1-Line-Eingang; definierte Quelle/Last und dBu-Eingangspegel; THD über f und Pegel",
        },
        "published_values": {
            "turns_ratio_secondary_over_primary": 1.0,
            "source_resistance_ohm": rg,
            "load_resistance_ohm": rl,
            "primary_dcr_ohm": rp,
            "secondary_dcr_ohm": rs,
            "input_impedance_1khz_ohm": {"min": 12300, "typ": 13000, "max": 13700},
            "gain_1khz_db": {"min": -2.6, "typ": -2.3, "max": -2.0},
            "response_20hz_db_relative_1khz": {"min": -0.15, "typ": -0.04, "max": 0.0},
            "response_20khz_db_relative_1khz": {"min": -0.15, "typ": -0.05, "max": 0.0},
            "deviation_from_linear_phase_deg": {"typ": 0.6, "absolute_max": 2.0},
            "bandwidth_minus3db_hz": [0.25, 100000],
            "thd_20hz_at_plus4dbu_percent": {"typ": 0.025, "max": 0.1},
            "thd_1khz_at_plus4dbu_percent_upper_bound": 0.001,
            "level_20hz_for_1percent_thd_dbu": {"min": 18, "typ": 20},
            "output_impedance_1khz_rs50_ohm_typ": 2340,
            "primary_to_shield_case_capacitance_f": 98e-12,
            "secondary_to_shield_case_capacitance_f": 110e-12,
            "capacitance_caveat": "Schirm-/Gehäusekapazitäten, NICHT automatisch differentielles Ceff",
            "gain_caveat": "Primärklemmenbezug als Arbeitskonvention, durch Kupferrechnung gestützt",
            "phase_caveat": "DLP ist NICHT rohe Phase oder vollständige Gruppenlaufzeit",
            "harmonic_caveat": "Tabelle nennt THD; Grafiken sind THD+N beschriftet, Bandbreite fehlt",
        },
        "own_algebraic_checks": {
            "simple_input_impedance_ohm": rp + rs + rl,
            "simple_gain_from_primary_terminal_db": 20 * math.log10(rl / (rp + rs + rl)),
            "simple_gain_from_open_source_db": 20 * math.log10(rl / (rg + rp + rs + rl)),
            "output_impedance_including_test_load_ohm": parallel(50 + rp + rs, rl),
            "effective_resistance_generator_ohm": req_generator,
            "effective_resistance_terminal_ohm": req_terminal,
            "lm_from_025hz_h": {"generator_reference": req_generator / (2 * math.pi * 0.25),
                                  "terminal_reference": req_terminal / (2 * math.pi * 0.25)},
            "one_pole_fc_from_20hz_minus004db_hz": fc_from_20hz,
            "lm_from_20hz_minus004db_h": {
                "generator_reference": req_generator / (2 * math.pi * fc_from_20hz),
                "terminal_reference": req_terminal / (2 * math.pi * fc_from_20hz)},
            "lf_caveat": "Verschiedene Einpol-Ersatzwerte; kein Beleg für ein konstantes reales Lm",
            "two_pole_hf_seed": {"natural_frequency_hz": f0, "q": q,
                                  "lc_product_h_f": 1 / (2 * math.pi * f0)**2,
                                  "origin": "Zwei Amplitudenpunkte, ungeprüfte Phase/Topologie"},
            "vrms_at_plus4dbu": rms4,
            "vrms_at_plus20dbu": rms20,
            "lambda_at_1percent_thd_20hz_terminal_vs": lambda_terminal,
            "lambda_at_1percent_thd_20hz_core_copper_only_vs": lambda_core,
            "lambda_caveat": "1%-THD-Anker und Kupfernäherung; kein identifizierter physikalischer Kniefluss",
            "constant_v_over_f_1percent_level_prediction_dbu": {
                str(f): 20 + 20 * math.log10(f / 20) for f in (20, 30, 50, 100)},
            "conditional_560q_capacitance_from_assumed_resonance": {
                str(f): 1 / ((2 * math.pi * f)**2 * 1.23e-3) for f in (60000, 100000, 150000)},
            "conditional_560q_caveat": "Resonanz angenommen; Streu-L-Messseite ungeklärt; keine tatsächliche C-Bestimmung",
            "groupdiy_post8_atan05_deg": math.degrees(math.atan(0.5)),
        },
        "proposed_fixed_assumptions": {
            "port_ratio": "1:1",
            "dc_bias_a": 0.0,
            "initial_remanent_state": 0.0,
            "source_model": "lineare Theveninquelle; zusätzliche Treibergrenzen zunächst nicht fitten",
            "audio_mapping": "1-kHz-Sinus mit -18 dBFS PEAK entspricht +4 dBu RMS an Primärklemmen",
            "volts_per_fs_sample_at_primary_1khz": scale_terminal,
            "volts_per_fs_sample_of_generator_copper_estimate": scale_terminal * source_calibration,
            "full_scale_sine_level_dbu": 22,
            "onepercent_20hz_level_nominal_dbfs_peak": -2,
            "even_harmonics": "im symmetrischen Erstmodell null; keine geraden Harmonischen erfunden",
            "noise": "kein synthetisches Rauschen zum Fitten eines unbekannten Messrauschbodens",
            "fit_domain": "Flussverkettung lambda in V*s; keine unidentifizierte Kerngeometrie nötig",
        },
        "proposed_search_seeds_not_measured": {
            "effective_low_frequency_lm_h": {"seed": 1000, "min": 100, "max": 2000},
            "linear_loss_shunt_ohm_if_used": {"seed": 2e6, "min": 2e5, "max": 2e7},
            "hf_natural_frequency_hz": {"seed": f0, "min": 80000, "max": 200000},
            "hf_q": {"seed": q, "min": 0.45, "max": 1.0},
            "nonlinear_flux_scale_vs": {"seed": 0.08, "min": 0.02, "max": 0.2},
            "saturation_exponent_candidates": [3, 5, 7, 9],
            "hysteresis_strength": "schwach initialisieren und mehrere Lösungen vergleichen; keine identifizierte Zahl",
            "leakage_inductance_h": None,
            "differential_winding_capacitance_f": None,
            "comment": "Bauteil-L/C-Aufteilung nicht zusätzlich frei fitten, wenn nur f0/Q identifiziert werden",
        },
        "missing_for_unique_physical_fit": [
            "komplexe Leerlaufimpedanz bzw. phasenrichtiger Magnetisierungsstrom über Pegel und Frequenz",
            "getrennte H2/H3/H5 oder referenzierte Wellenformen",
            "Transienten/Minor-Loops/Remanenz bzw. Wiederanlauf nach Vorbelastung",
            "zweite Quellen-/Lastbedingung zur Entkopplung von Kern, Verlusten und Parasiten",
            "Streuinduktivität und differentielles Kapazitätsnetz, falls physikalische Einzelwerte benötigt werden",
        ],
    }
    # Numerical consistency checks of the stated formulas, not a model test.
    assert abs(output["own_algebraic_checks"]["simple_gain_from_primary_terminal_db"] + 2.3) < 0.03
    assert abs(output["own_algebraic_checks"]["output_impedance_including_test_load_ohm"] - 2340) < 3
    assert 0 < q < 1 and lambda_core < lambda_terminal
    with (HERE / "FIT_STARTWERTE.json").open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(output, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(json.dumps(output["own_algebraic_checks"], indent=2, ensure_ascii=False))
    print("FIT_STARTWERTE.json erzeugt; ungefitte Schätzungen und feste Quellenwerte bezeichnet.")


if __name__ == "__main__":
    main()
