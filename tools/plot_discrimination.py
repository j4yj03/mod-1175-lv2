#!/usr/bin/env python3
"""Plots fuer die Diskriminierungsauswertung (MESSERGEBNISSE 12).

Liest test-results/diskriminierung-20261008/analysis.json (Ausgabe von
tools/analyze_discrimination.py) und rendert vier PNGs nach docs/plots/:

  mess-diskr-pegelreihe.png  Gain und THD ueber Pegelstufe (SSL | JSFX)
  mess-diskr-bursts.png      Burst-zu-Burst-Shift und Nachlauf ueber Boden
  mess-diskr-im.png          Zweiton-Seitenbaender gemessen vs. Vorhersage
  mess-diskr-dc.png          DC-Durchlass und H2 mit/ohne DC-Offset
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "test-results/diskriminierung-20261008/analysis.json"
PLOTS = ROOT / "docs/plots"

LABELS = {
    "matrix-0 AMOUNT-2026-10-08 23_21_15.wav": "SSL A0",
    "matrix-50 AMOUNT-2026-10-08 23_21_15.wav": "SSL A50",
    "matrix-100 AMOUNT-2026-10-08 23_21_15.wav": "SSL A100",
    "matrix-150 AMOUNT-2026-10-08 23_21_15.wav": "SSL A150",
    "matrix-200 AMOUNT-2026-10-08 23_21_15.wav": "SSL A200",
    "matrix-00s-2026-10-08 23_21_15.wav": "JSFX 00s",
    "matrix-60s-2026-10-08 23_21_15.wav": "JSFX 60s",
    "matrix-80s-2026-10-08 23_21_15.wav": "JSFX 80s",
    "matrix-Sym-2026-10-08 23_21_15.wav": "JSFX Sym",
}
SSL_COLORS = {"SSL A0": "#9e9e9e", "SSL A50": "#ff7f0e", "SSL A100": "#d62728",
              "SSL A150": "#8b0000", "SSL A200": "#444444"}
JSFX_COLORS = {"JSFX 00s": "#2ca02c", "JSFX 60s": "#1f77b4",
               "JSFX 80s": "#d62728", "JSFX Sym": "#9467bd"}


def main():
    results = json.loads(DATA.read_text(encoding="utf-8"))
    by_label = {LABELS[r["file"]]: r for r in results}
    ssl = [l for l in LABELS.values() if l.startswith("SSL")]
    jsfx = [l for l in LABELS.values() if l.startswith("JSFX")]
    plt.rcParams.update({"font.size": 9, "figure.dpi": 150})

    # ---------- P1 Pegelreihe: Gain und THD ueber Pegel ----------
    levels = [it["level_dbfs"] for it in by_label["SSL A0"]["pegelreihe"]["items"]]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, group, colors, title in (
        (axes[0], ssl, SSL_COLORS, "SSL Fusion Transformer"),
        (axes[1], jsfx, JSFX_COLORS, "GS76-JSFX (COMP OFF, OS 4x, Colour 0)"),
    ):
        for label in group:
            r = by_label[label]
            gains = [it["gain_db"] for it in r["pegelreihe"]["items"]]
            thds = [max(it["thd_pct"], 1e-3) for it in r["pegelreihe"]["items"]]
            ax.plot(levels, gains, "o-", label=label, color=colors[label], ms=4)
        ax.set_xlabel("Eingangspegel / dBFS"); ax.set_ylabel("Gain bei 20 Hz / dB")
        ax.set_title(f"Grundwellen-Gain — {title}")
        ax.grid(True, alpha=0.3); ax.legend(fontsize=7)
    for plot_id, pick, ylabel, title, suptitle, logy in (
        ("gain", lambda it: it["gain_db"], "Gain bei 20 Hz / dB", "Grundwellen-Gain",
         "Pegelreihe 20 Hz: Verlust über den Pegel (0-dB-Renders, 2026-10-08)", False),
        ("thd", lambda it: max(it["thd_pct"], 1e-3), "THD (H2..H10) / %", "Klirr über Pegel",
         "Pegelreihe 20 Hz: Klirr über den Pegel (0-dB-Renders, 2026-10-08)", True),
    ):
        fig_p, axes_p = plt.subplots(1, 2, figsize=(11, 4.4))
        for ax, group, colors, group_title in (
            (axes_p[0], ssl, SSL_COLORS, "SSL Fusion Transformer"),
            (axes_p[1], jsfx, JSFX_COLORS, "GS76-JSFX (COMP OFF, OS 4x, Colour 0)"),
        ):
            for label in group:
                ys = [pick(it) for it in by_label[label]["pegelreihe"]["items"]]
                ax.plot(levels, ys, "o-", label=label, color=colors[label], ms=4)
            if logy:
                ax.set_yscale("log"); ax.set_ylim(1e-3, 200)
            ax.set_xlabel("Eingangspegel / dBFS"); ax.set_ylabel(ylabel)
            ax.set_title(f"{title} — {group_title}")
            ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=7)
        fig_p.suptitle(suptitle, y=1.02)
        fig_p.tight_layout()
        fig_p.savefig(PLOTS / f"mess-diskr-pegelreihe-{plot_id}.png", bbox_inches="tight")
        plt.close(fig_p)

    # ---------- P2 Bursts: Shift und Nachlauf ----------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    labels_all = ssl + jsfx
    width = 0.22
    for idx, label in enumerate(labels_all):
        color = SSL_COLORS.get(label) or JSFX_COLORS[label]
        r = by_label[label]
        peaks = [it["peak_first_halfwave"] for it in r["bursts"]["items"]]
        ref = peaks[0]
        shifts = [20 * __import__("math").log10(p / ref) for p in peaks[1:]]
        ax1.bar([i + idx * width for i in range(3)], shifts, width,
                label=label, color=color)
        tail_over = r["bursts"]["items"][0]["tail_rms_db"] - r["bursts"]["carrier_floor_rms_db"]
        ax2.bar(idx, tail_over, 0.6, color=color)
        ax2.text(idx, tail_over + (0.3 if tail_over >= 0 else -1.1), f"{tail_over:+.1f}",
                 ha="center", fontsize=6.5)
        ax2.set_ylim(-2.2, 10.2)
    ax1.set_xticks([i + 4.5 * width for i in range(3)])
    ax1.set_xticklabels(["Burst 2 − 1", "Burst 3 − 1", "Burst 4 − 1"])
    ax1.set_ylabel("Erst-Halbwelle relativ zu Burst 1 / dB")
    ax1.set_title("Burst-zu-Burst-Shift — Kerne verschieben, statische Modelle nicht")
    ax1.set_ylim(-0.35, 0.35)
    ax1.grid(True, axis="y", alpha=0.3); ax1.legend(fontsize=6.5, ncol=2)
    ax2.axhline(0, color="grey", lw=0.8)
    ax2.set_xticks(range(len(labels_all)))
    ax2.set_xticklabels([l.replace("SSL ", "") for l in labels_all],
                        rotation=45, ha="right", fontsize=7)
    ax2.set_ylabel("Nachlauf-RMS über Trägerboden / dB")
    ax2.set_title("Nachlauf 50–250 ms nach Burst-Ende\n(SSL: verschwindet mit AMOUNT; JSFX: bleibt)")
    ax2.grid(True, axis="y", alpha=0.3)
    fig.suptitle("Remanenz-Bursts (20 Hz, −2 dBFS) (0-dB-Renders, 2026-10-08)", y=1.02)
    fig.tight_layout(); fig.savefig(PLOTS / "mess-diskr-bursts.png", bbox_inches="tight"); plt.close(fig)

    # ---------- P3 Zweiton-IM ----------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    floor = -140.0
    for ax, group, colors, title in (
        (axes[0], ["SSL A50", "SSL A100", "SSL A150", "SSL A200"], SSL_COLORS, "SSL Fusion Transformer"),
        (axes[1], jsfx, JSFX_COLORS, "GS76-JSFX (COMP OFF, OS 4x, Colour 0)"),
    ):
        ks = [1, 2, 3, 4]
        for label in group:
            z = by_label[label]["zweiton"]
            up = [max(v, floor) for v in z["rel_up_db"]]
            dn = [max(v, floor) for v in z["rel_down_db"]]
            ax.plot(ks, up, "o-", label=f"{label} gemessen", color=colors[label], ms=4)
            ax.plot(ks, dn, "s--", color=colors[label], ms=3, alpha=0.55)
            if "pred_rel_up_db" in z and all(v > floor for v in z["pred_rel_up_db"]):
                pred = [max(v, floor) for v in z["pred_rel_up_db"]]
                ax.plot(ks, pred, "^:", color=colors[label], ms=4, alpha=0.8)
        ax.axhline(floor, color="grey", lw=0.8, ls=":")
        ax.text(3.9, floor + 2, "PCM24-Flur", fontsize=6.5, color="grey", ha="right")
        ax.set_xticks(ks); ax.set_xlim(0.7, 4.3)
        ax.set_xlabel("Seitenband-Ordnung k (1000 ± k·60 Hz)")
        ax.set_ylabel("Pegel relativ zum 1-kHz-Ton / dB")
        ax.set_title(f"IM-Seitenbänder — {title}")
        ax.grid(True, which="both", alpha=0.3); ax.legend(fontsize=6, ncol=2)
        ax.set_ylim(floor - 15, 4)
    fig.text(0.5, 0.0, "● gemessen oben, ■ gemessen unten (nahezu deckungsgleich = odd-order), "
             "▲ statische Vorhersage aus der 20-Hz-Pegelreihe desselben Renders",
             ha="center", fontsize=7, color="grey")
    fig.suptitle("Zweiton-IM: Seitenbänder gegen speicherfreie Vorhersage (0-dB-Renders, 2026-10-08)", y=1.02)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(PLOTS / "mess-diskr-im.png", bbox_inches="tight"); plt.close(fig)

    # ---------- P4 DC ----------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    for idx, label in enumerate(labels_all):
        color = SSL_COLORS.get(label) or JSFX_COLORS[label]
        r = by_label[label]
        dc_out = r["dc_asym"]["dc_only_output_dc"]
        ax1.bar(idx, dc_out, 0.6, color=color)
        ax1.text(idx, dc_out + 0.004, f"{dc_out:.3f}".lstrip("0").replace("0.", "."),
                 ha="center", fontsize=6.5)
        w = r["dc_asym"]["windows"]
        ax2.bar(idx - 0.18, w["with_dc"]["h2_rel_db"], 0.32, color=color, alpha=0.95)
        ax2.bar(idx + 0.18, w["no_dc"]["h2_rel_db"], 0.32, color=color, alpha=0.45)
    ax1.axhline(0, color="grey", lw=0.8)
    ax1.set_xticks(range(len(labels_all)))
    ax1.set_xticklabels([l.replace("SSL ", "") for l in labels_all],
                        rotation=45, ha="right", fontsize=7)
    ax1.set_ylabel("Ausgangs-DC bei reinem DC-Eingang (0,3 FS) / FS")
    ax1.set_title("DC-Durchlass — realer Kern: ≈ 0")
    ax1.grid(True, axis="y", alpha=0.3)
    ax2.set_xticks(range(len(labels_all)))
    ax2.set_xticklabels([l.replace("SSL ", "") for l in labels_all],
                        rotation=45, ha="right", fontsize=7)
    ax2.set_ylabel("H2 relativ zum 1-kHz-Ton / dB")
    ax2.set_title("H2 mit (dunkel) / ohne (hell) DC-Offset\nJSFX-Kerne: H2-Anhebung; SSL: nichtmonoton")
    ax2.grid(True, axis="y", alpha=0.3)
    fig.suptitle("DC-/Polaritätsasymmetrie (0-dB-Renders, 2026-10-08)", y=1.02)
    fig.tight_layout(); fig.savefig(PLOTS / "mess-diskr-dc.png", bbox_inches="tight"); plt.close(fig)

    print("Plots geschrieben nach", PLOTS)


if __name__ == "__main__":
    main()
