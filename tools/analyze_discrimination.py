#!/usr/bin/env python3
"""Auswertung der Diskriminierungs-Renders nach MESSTECHNIK 1k.2.

Liest einen (oder mehrere) Renders des Kombiprograms
gs76-diskriminierung-stereo.wav, lokalisiert die Proben ueber manifest.json
und berechnet die 1k.2-Metriken:

  1. Remanenz/Bursts   Erstburst gegen Folgebuerste, Nachlauf-RMS, Ausgangs-DC
  2. Zweiton-IM        Seitenbaender 1000+-k*60 Hz, Ober-/Unterband-Asymmetrie,
                       plus speicherfreie Vorhersage aus der Pegelreihe
  3. Pegelreihe 20 Hz  gain_db und THD (H2..H10) je Stufe
  4. DC-Asymmetrie     Ausgangs-DC, H2/H3 mit/ohne DC, Halbwellen-Peaks,
                       Nachlauf nach DC-Ende

Es wird nur Kanal L ausgewertet (Programm und Renders sind L=R; das wurde
verifiziert). Referenzpegel kommen aus dem Programm selbst.

Aufruf:
  python3 tools/analyze_discrimination.py RENDER.wav [RENDER2.wav ...]
      [--program PFAD] [--json AUSGABE.json] [--label NAME=WERT ...]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROGRAM = ROOT / "reaper/testbench/Probes/diskriminierung/gs76-diskriminierung-stereo.wav"
MANIFEST = DEFAULT_PROGRAM.parent / "manifest.json"

RATE = 48000
BURST_SPANS = ((0.5, 1.5), (2.5, 3.5), (4.5, 5.5), (6.5, 9.5))
LEVELS_20HZ = (-26, -20, -14, -8, -2)
CARRIER = 0.003
IM_CARRIER_HZ = 60.0
IM_PROBE_HZ = 1000.0


def amp(x, rate, freq):
    """Amplitude einer on-bin Sinusschwingung (Fensterung inklusive)."""
    n = np.arange(len(x))
    w = np.hanning(len(x))
    s = np.sum(x * w * np.exp(-2j * np.pi * freq * n / rate))
    return 2.0 * abs(s) / np.sum(w)


def db(v):
    return 20.0 * np.log10(max(v, 1e-12))


def thd(x, rate, f0, orders=range(2, 11)):
    fund = amp(x, rate, f0)
    if fund <= 0:
        return float("nan"), 0.0
    hs = [amp(x, rate, f0 * h) for h in orders]
    return 100.0 * np.sqrt(sum(h * h for h in hs)) / fund, fund


def analyze(path, program):
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    starts = {e["label"]: e["start_frames"] for e in man["timeline"] if e["kind"] == "probe"}
    d, rate = sf.read(str(path), dtype="float64", always_2d=True)
    x = d[:, 0]
    res = {"file": path.name, "rate": rate, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}

    # ---------- 1. Remanenz/Bursts ----------
    s0 = starts["remanenz-bursts"]
    bursts = []
    for begin, end in BURST_SPANS:
        b0 = s0 + round(begin * rate)
        # (a) Peak der ersten Halbwelle: Fenster 50 ms nach Burstbeginn
        seg = x[b0 + round(0.005 * rate): b0 + round(0.055 * rate)]
        peak_first = float(np.max(seg))
        b1 = s0 + round(end * rate)
        tail = x[b1 + round(0.05 * rate): b1 + round(0.25 * rate)]
        bursts.append(dict(
            span=(begin, end),
            peak_first_halfwave=peak_first,
            tail_rms_db=db(float(np.sqrt(np.mean(tail ** 2)))),
            tail_dc=float(np.mean(tail)),
        ))
    floors = []
    for lo, hi in ((1.7, 2.3), (3.7, 4.3), (5.7, 6.3)):
        seg = x[s0 + round(lo * rate): s0 + round(hi * rate)]
        floors.append(float(np.sqrt(np.mean(seg ** 2))))
    res["bursts"] = dict(
        items=bursts,
        carrier_floor_rms_db=db(float(np.median(floors))),
    )

    # ---------- 2. Zweiton-IM ----------
    s0 = starts["zweiton-im"]
    seg = x[s0 + round(2.0 * rate): s0 + round(6.0 * rate)]
    probe = amp(seg, rate, IM_PROBE_HZ)
    side_up, side_dn = [], []
    for k in range(1, 5):
        side_up.append(amp(seg, rate, IM_PROBE_HZ + k * IM_CARRIER_HZ))
        side_dn.append(amp(seg, rate, IM_PROBE_HZ - k * IM_CARRIER_HZ))
    harm60 = [amp(seg, rate, IM_CARRIER_HZ * h) for h in range(2, 6)]
    res["zweiton"] = dict(
        probe_1k_db=db(probe),
        carrier_60_db=db(amp(seg, rate, IM_CARRIER_HZ)),
        sidebands_up_db=[db(v) for v in side_up],
        sidebands_down_db=[db(v) for v in side_dn],
        rel_up_db=[db(v / probe) for v in side_up],
        rel_down_db=[db(v / probe) for v in side_dn],
        asym_db=[20 * np.log10(u / max(lv, 1e-12)) for u, lv in zip(side_up, side_dn)],
        harm60_rel_db=[db(v / max(amp(seg, rate, IM_CARRIER_HZ), 1e-12)) for v in harm60],
    )

    # ---------- 3. Pegelreihe 20 Hz ----------
    s0 = starts["pegelreihe-20hz"]
    stages = []
    gains = []
    for idx, level in enumerate(LEVELS_20HZ):
        lo = s0 + round((3 * idx + 1.0) * rate)
        hi = s0 + round((3 * idx + 2.9) * rate)
        seg = x[lo:hi]
        thd_pct, fund = thd(seg, rate, 20.0)
        gain = db(fund / (10 ** (level / 20)))
        stages.append(dict(level_dbfs=level, gain_db=gain, thd_pct=thd_pct,
                           thd_rel_db=db(thd_pct / 100.0)))
        gains.append(10 ** (gain / 20))
    res["pegelreihe"] = dict(items=stages)
    res["pegelreihe"]["input_amps"] = [10 ** (lv / 20) for lv in LEVELS_20HZ]
    res["pegelreihe"]["gains"] = gains

    # ---------- Speicherfreie Vorhersage der IM-Seitenbaender ----------
    # f(x) = x * g(|x|) mit g aus der 20-Hz-Pegelreihe (odd-symmetrisch,
    # memoryless; Caveat: Kennlinie bei 20 Hz gemessen, IM bei 60/1000 Hz).
    a_in = np.array(res["pegelreihe"]["input_amps"])
    g = np.array(gains)
    def gain_at(a):
        if a <= a_in[0]:
            return float(g[0])
        if a >= a_in[-1]:
            return float(g[-1])
        return float(np.exp(np.interp(np.log(a), np.log(a_in), np.log(g))))
    n = round(4.0 * rate)
    tt = np.arange(n) / rate
    sig = 0.501 * np.sin(2 * np.pi * IM_CARRIER_HZ * tt) + 0.050 * np.sin(2 * np.pi * IM_PROBE_HZ * tt)
    pred = sig * np.vectorize(gain_at)(np.abs(sig))
    p_probe = amp(pred, rate, IM_PROBE_HZ)
    pred_up = [amp(pred, rate, IM_PROBE_HZ + k * IM_CARRIER_HZ) for k in range(1, 5)]
    pred_dn = [amp(pred, rate, IM_PROBE_HZ - k * IM_CARRIER_HZ) for k in range(1, 5)]
    res["zweiton"]["pred_rel_up_db"] = [db(v / p_probe) for v in pred_up]
    res["zweiton"]["pred_rel_down_db"] = [db(v / p_probe) for v in pred_dn]

    # ---------- 4. DC-Asymmetrie ----------
    s0 = starts["dc-asymmetrie"]
    w1 = x[s0 + round(0.5 * rate): s0 + round(2.5 * rate)]   # 1 kHz + DC
    w2 = x[s0 + round(3.5 * rate): s0 + round(5.5 * rate)]   # 1 kHz ohne DC
    w3 = x[s0 + round(6.2 * rate): s0 + round(7.9 * rate)]   # reines DC
    h = {}
    for key, w in (("with_dc", w1), ("no_dc", w2)):
        h[key] = dict(
            dc=float(np.mean(w)),
            fund_1k_db=db(amp(w, rate, 1000.0)),
            h2_rel_db=db(amp(w, rate, 2000.0) / max(amp(w, rate, 1000.0), 1e-12)),
            h3_rel_db=db(amp(w, rate, 3000.0) / max(amp(w, rate, 1000.0), 1e-12)),
            pos_peak=float(np.max(w)),
            neg_peak=float(np.min(w)),
        )
    decay = x[s0 + round(8.0 * rate): s0 + round(8.45 * rate)]
    res["dc_asym"] = dict(
        windows=h,
        dc_only_output_dc=float(np.mean(w3)),
        dc_only_output_rms_db=db(float(np.sqrt(np.mean(w3 ** 2)))),
        after_dc_tail_dc=float(np.mean(decay)),
        after_dc_tail_rms_db=db(float(np.sqrt(np.mean(decay ** 2)))),
    )
    return res


def fmt_bursts(r):
    b = r["bursts"]
    lines = [f"  Traegerboden RMS {b['carrier_floor_rms_db']:.1f} dBFS"]
    for i, it in enumerate(b["items"]):
        lines.append(f"  Burst {i + 1} ({it['span'][0]:.1f}-{it['span'][1]:.1f}s): "
                     f"1.Halbwelle {db(it['peak_first_halfwave']):6.2f} dBFS, "
                     f"Nachlauf {it['tail_rms_db']:6.1f} dBFS, DC {it['tail_dc']:+.5f}")
    return "\n".join(lines)


def fmt_zweiton(r):
    z = r["zweiton"]
    lines = [f"  1 kHz {z['probe_1k_db']:.2f} dBFS, 60 Hz {z['carrier_60_db']:.2f} dBFS"]
    for k in range(4):
        pred = ""
        if "pred_rel_up_db" in z:
            pred = (f" | pred +{z['pred_rel_up_db'][k]:.1f}/-{abs(z['pred_rel_down_db'][k]):.1f}")
        lines.append(f"  SB k={k + 1}: +{z['rel_up_db'][k]:6.1f} / {z['rel_down_db'][k]:6.1f} dB rel 1k"
                     f" (Asymmetrie {z['asym_db'][k]:+5.1f} dB){pred}")
    lines.append("  60-Hz-Harmonische rel: " + " ".join(f"H{h + 2} {v:+.1f}" for h, v in enumerate(z["harm60_rel_db"])))
    return "\n".join(lines)


def fmt_pegel(r):
    lines = []
    for it in r["pegelreihe"]["items"]:
        lines.append(f"  {it['level_dbfs']:>3} dBFS: gain {it['gain_db']:+6.2f} dB, THD {it['thd_pct']:6.2f} % ({it['thd_rel_db']:+6.1f} dB)")
    return "\n".join(lines)


def fmt_dc(r):
    d = r["dc_asym"]
    w = d["windows"]
    lines = [
        f"  1k+DC: DC {w['with_dc']['dc']:+.5f}, 1k {w['with_dc']['fund_1k_db']:.2f} dBFS, "
        f"H2 {w['with_dc']['h2_rel_db']:+.1f} dB, H3 {w['with_dc']['h3_rel_db']:+.1f} dB, "
        f"Peaks +{db(w['with_dc']['pos_peak']):.1f}/-{abs(db(-w['with_dc']['neg_peak'])):.1f} dBFS",
        f"  1k  : DC {w['no_dc']['dc']:+.5f}, 1k {w['no_dc']['fund_1k_db']:.2f} dBFS, "
        f"H2 {w['no_dc']['h2_rel_db']:+.1f} dB, H3 {w['no_dc']['h3_rel_db']:+.1f} dB, "
        f"Peaks +{db(w['no_dc']['pos_peak']):.1f}/-{abs(db(-w['no_dc']['neg_peak'])):.1f} dBFS",
        f"  reines DC: Ausgangs-DC {d['dc_only_output_dc']:+.5f} ({db(abs(d['dc_only_output_dc'])):.1f} dBFS), "
        f"RMS {d['dc_only_output_rms_db']:.1f} dBFS",
        f"  Nachlauf nach DC-Ende: DC {d['after_dc_tail_dc']:+.5f}, RMS {d['after_dc_tail_rms_db']:.1f} dBFS",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("renders", nargs="+", type=Path)
    parser.add_argument("--program", type=Path, default=DEFAULT_PROGRAM)
    parser.add_argument("--json", type=Path, help="Ergebnisse als JSON schreiben")
    parser.add_argument("--label", action="append", default=[],
                        help="Datei=Label Zuordnung fuer die Ausgabe, z. B. matrix-0=SSL A0")
    args = parser.parse_args()

    program, _ = sf.read(str(args.program), dtype="float64", always_2d=True)
    labels = dict(l.split("=", 1) for l in args.label)
    results = []
    for path in args.renders:
        r = analyze(path, program)
        results.append(r)
        name = labels.get(path.name, path.name)
        print(f"\n=== {name} ({path.name})")
        print(fmt_bursts(r))
        print(fmt_zweiton(r))
        print(fmt_pegel(r))
        print(fmt_dc(r))
    if args.json:
        args.json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")
        print(f"\nJSON -> {args.json}")


if __name__ == "__main__":
    main()
