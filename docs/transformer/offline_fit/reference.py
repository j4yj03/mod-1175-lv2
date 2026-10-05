"""Python interface and continuous small-signal model for the offline C++ reference."""
import ctypes
from pathlib import Path

import numpy as np

PARAMETER_NAMES = ("lm_h", "flux_scale_vs", "hysteresis_stiffness_a_per_vs",
                   "hysteresis_slope", "relax_l_h", "relax_frequency_hz",
                   "core_conductance_s", "hf_frequency_hz", "hf_q",
                   "source_resistance_ohm", "primary_resistance_ohm",
                   "secondary_resistance_ohm", "load_resistance_ohm",
                   "hysteresis_enabled", "family", "exponent", "saturation_strength",
                   "high_field_l_ratio", "nonlinear_series_resistance_ohm")
METRIC_NAMES = ("thd_percent", "gain_primary_db", "gain_source_db", "phase_primary_deg",
                "primary_rms_v", "source_rms_v", "output_h1_rms_v", "flux_peak_vs",
                "primary_current_rms_a", "h2_dbc", "h3_dbc", "h5_dbc", "output_dc_v",
                "max_solver_iterations", "periodic_shooting_error", "input_impedance_ohm")
THRESHOLDS = np.array((.00002,.00005,.0001,.0002,.0005,.001,.002,
                       .005,.01,.02,.05,.1,.2,.5))


def array_of(parameters):
    return np.array([parameters[key] for key in PARAMETER_NAMES], dtype=np.float64)


def default_parameters():
    return dict(zip(PARAMETER_NAMES,
                    (1000,.04,1e-5,0,200,5,1/2e6,108000,.66,
                     600,1450,1550,10000,0,0,7,1,0,0)))


def hf_response(parameters, frequencies):
    if parameters["hf_frequency_hz"] <= 0:
        return np.ones_like(frequencies, dtype=complex)
    x = np.asarray(frequencies) / parameters["hf_frequency_hz"]
    return 1 / (1 - x*x + 1j*x/parameters["hf_q"])


def linear_response(parameters, frequencies, tiny_signal=False):
    """Core network analytic admittance; HF stage is an effective cascade surrogate.

    For finite-amplitude +4dBu plots, saturated stop operators must be rendered,
    not approximated by their virgin-state stiffness.
    """
    p = parameters
    s = 2j*np.pi*np.asarray(frequencies, dtype=float)
    stiffness = 1/p["lm_h"]
    if tiny_signal and p["hysteresis_enabled"]:
        stiffness += p["hysteresis_stiffness_a_per_vs"] * np.sum(
            (THRESHOLDS/.001)**p["hysteresis_slope"])
    admittance = stiffness/s + p["core_conductance_s"]
    if p["relax_l_h"] > 0:
        admittance += 1/(p["relax_l_h"]*(s+2*np.pi*p["relax_frequency_hz"]))
    ra = p["source_resistance_ohm"]+p["primary_resistance_ohm"]
    rb = p["secondary_resistance_ohm"]+p["load_resistance_ohm"]
    core_source = 1/(1+ra*(admittance+1/rb))
    primary_source = 1-p["source_resistance_ohm"]*(admittance+1/rb)*core_source
    output_source = core_source*p["load_resistance_ohm"]/rb*hf_response(p, frequencies)
    return output_source/primary_source, output_source, 1/(admittance+1/rb)+p["primary_resistance_ohm"]


class Reference:
    def __init__(self, library):
        self.path = Path(library)
        self.library = ctypes.CDLL(str(self.path.resolve()))
        pointer = ctypes.POINTER(ctypes.c_double)
        self.library.gs76_transformer_tone.argtypes = [pointer,ctypes.c_double,ctypes.c_double,
                                                     ctypes.c_uint,pointer,pointer,pointer]
        self.library.gs76_transformer_tone.restype = ctypes.c_int
        self.library.gs76_transformer_render.argtypes = [pointer,ctypes.c_double,pointer,
                                                       ctypes.c_size_t,pointer,pointer]
        self.library.gs76_transformer_render.restype = ctypes.c_int
        self.pointer = lambda a: a.ctypes.data_as(pointer) if a is not None else None

    def tone(self, parameters, frequency, level, steps=1024, waveform=False):
        p = array_of(parameters)
        metrics = np.zeros(16, dtype=np.float64)
        harmonics = np.zeros(64, dtype=np.float64)
        wave = np.zeros((steps,6), dtype=np.float64) if waveform else None
        status = self.library.gs76_transformer_tone(self.pointer(p),frequency,level,steps,
                    self.pointer(metrics),self.pointer(harmonics),self.pointer(wave))
        if status:
            raise RuntimeError(f"tone failed {status}: {frequency}/{level}/{parameters}")
        return dict(zip(METRIC_NAMES,metrics.tolist())), harmonics[::2]+1j*harmonics[1::2], wave

    def render(self, parameters, source, rate, diagnostics=False):
        p = array_of(parameters)
        x = np.asarray(source, dtype=np.float64, order='C')
        y = np.zeros_like(x)
        diag = np.zeros((len(x),4), dtype=np.float64) if diagnostics else None
        status = self.library.gs76_transformer_render(self.pointer(p),rate,self.pointer(x),len(x),
                    self.pointer(y),self.pointer(diag))
        if status:
            raise RuntimeError(f"render failed {status}")
        return y, diag
