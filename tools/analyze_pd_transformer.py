#!/usr/bin/env python3
"""Analysiert die PluginDoctor-Captures "Transformer Harmonics" (2026-10-08).

Liest die Rohexporte unter docs/PluginDoctor messen/Transformer Harmonics/
(THD.txt = Klirr-ueber-Frequenz-Kurve, data.txt = FFT-Momentaufnahme,
Clipboard01.jpg = 2D-Sweep-Screenshot), ohne sie zu veraendern, und
schreibt ein Analyse-JSON nach test-results/pd-transformer-20261008/.

Die Panelsellungen der GS76-Captures sind benutzerbelegt (COMP OFF,
4x Oversampling, Colour 0 %, Mix 100 %); die Eingangspegel und die
SSL-Knopfstellungen (MIN/STOCK/MAX) sind im Screenshot/Verzeichnisnamen
proveniert, nicht numerisch protokolliert.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/PluginDoctor messen/Transformer Harmonics"
OUT = ROOT / "test-results/pd-transformer-20261008"

GS76_SETTINGS = dict(compression=False, oversampling=4, colour_percent=0.0,
                     mix_percent=100.0, source="Benutzerangabe 2026-10-08")

CAPTURES = [
    ("60s", "gs76"),
    ("80s", "gs76"),
    ("00s", "gs76"),
    ("Sym", "gs76"),
    ("Commercial Plugin/MIN", "ssl"),
    ("Commercial Plugin/STOCK", "ssl"),
    ("Commercial Plugin/MAX", "ssl"),
]

SWEEP_EXCITATION_DB = -0.32  # Toolbar-Anzeige in den Screenshots (reajs)
BIN_HZ = 22050.0 / 8191.0    # Exportraster: 8191 Punkte bis Nyquist


def read_graphs(path):
    graphs = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("Graph #"):
            graphs.append([])
        elif line.strip():
            fields = line.split()
            if len(fields) != 2 or not graphs:
                raise ValueError(f"Ungueltige Graphzeile: {path}:{number}")
            x = float(fields[0])
            y = float("nan") if fields[1] == "-inf" else float(fields[1])
            if not math.isfinite(x):
                raise ValueError(f"Ungueltige Frequenz: {path}:{number}")
            graphs[-1].append((x, y))
    if not graphs or any(not g for g in graphs):
        raise ValueError(f"Leerer Graph: {path}")
    return graphs


def curve_lookup(graph, x):
    """Schrittgetreuer Abruf: Wert innerhalb eines Plateaus, sonst naechster
    Exportpunkt (mit Abstand). Keine Interpolation ueber Klippen."""
    best = None
    for f, v in graph:
        if not math.isfinite(v):
            continue
        distance = abs(math.log(f / x))
        if best is None or distance < best[0]:
            best = (distance, f, v)
        if f >= x and math.isfinite(v):
            break
    if best is None or best[0] > math.log(1.5):
        return None
    return dict(db=round(best[2], 2), at_hz=round(best[1], 2), log_distance=round(best[0], 4))


def curve_points(graph, freqs):
    out = {}
    for f in freqs:
        hit = curve_lookup(graph, f)
        out[str(f)] = None if hit is None else hit
    return out


def classify_second_curve(graph):
    values = [y for _, y in graph if math.isfinite(y)]
    if not values:
        return "leer", None, None
    peak = max(values)
    span = peak - min(values)
    if span < 3.0:
        return "Boden (flach, keine zweite Kurve)", round(peak, 2), None
    finite = [(x, y) for x, y in graph if math.isfinite(y)]
    peak_hz = max(finite, key=lambda row: row[1])[0]
    return "enthaelt Signalanteil", round(peak, 2), round(peak_hz, 2)


def spectrum_summary(spectrum):
    finite = [(x, y) for x, y in spectrum if math.isfinite(y)]
    peak_hz, peak_db = max(finite, key=lambda row: row[1])
    if peak_db < -60.0:
        return None
    f0 = peak_hz
    partials = []
    for order in range(2, 42):
        target = order * f0
        window = [row for row in finite if abs(row[0] - target) < 0.45 * f0]
        if not window:
            continue
        hz, db = max(window, key=lambda row: row[1])
        if db <= peak_db - 90.0:
            continue
        partials.append(dict(order=order, hz=round(hz, 2), dbc=round(db - peak_db, 2)))
    power = sum(10.0 ** (p["dbc"] / 10.0) for p in partials)
    thd = math.sqrt(power)
    thd_db = 20 * math.log10(thd) if power > 0.0 else None
    odd = [p for p in partials if p["order"] % 2 == 1]
    even = [p for p in partials if p["order"] % 2 == 0]
    return dict(
        fundamental=dict(hz=round(f0, 2), dbfs=round(peak_db, 2)),
        partials=partials,
        odd_dbc={str(p["order"]): p["dbc"] for p in odd[:14]},
        even_dbc={str(p["order"]): p["dbc"] for p in even[:8]},
        odd_dominant=len(odd) and (not even or max(p["dbc"] for p in odd) > max(p["dbc"] for p in even) + 6.0),
        thd_from_snapshot=dict(db=None if thd_db is None else round(thd_db, 2),
                               percent=None if power <= 0.0 else round(100 * thd, 2),
                               limit="Peak-bin-Summe H2..H41 einer einzigen FFT-Momentaufnahme; keine Rausch-/Fenster-Nachbildung"),
    )


def curve_steps(graph):
    """Zusammenhaengende Bereiche konstanten Werts (Treppenzuege der SSL-Kurven)."""
    steps = []
    start = 0
    for i in range(1, len(graph) + 1):
        boundary = (i == len(graph) or graph[i][1] != graph[start][1])
        if boundary:
            value = graph[start][1]
            if math.isfinite(value):
                steps.append(dict(from_hz=round(graph[start][0], 2),
                                  to_hz=round(graph[i - 1][0], 2),
                                  db=round(value, 2)))
            start = i
    return steps


def analyse_capture(directory, kind):
    thd = read_graphs(directory / "THD.txt")
    data = read_graphs(directory / "data.txt")
    curve, second = thd[0], thd[1]
    spec0, spec1 = data[0], data[1]
    summary = spectrum_summary(spec0)
    second_kind, second_peak, second_peak_hz = classify_second_curve(second)
    result = dict(
        kind=kind,
        thd_curve=dict(
            points=len(curve),
            range_hz=[round(curve[0][0], 2), round(curve[-1][0], 2)],
            at_hz=curve_points(curve, (5.38, 8.08, 13.46, 20, 30, 50, 80, 100, 200, 500, 1000, 2000, 5000, 10000)),
            steps=curve_steps(curve),
            floor_present=any(math.isfinite(y) for _, y in curve),
        ),
        second_curve=dict(kind=second_kind, peak_db=second_peak, peak_hz=second_peak_hz),
        snapshot=None,
    )
    if summary is not None:
        f0 = summary["fundamental"]["hz"]
        hit = curve_lookup(curve, f0)
        crosscheck = None
        snap_db = summary["thd_from_snapshot"]["db"]
        if hit is not None and snap_db is not None:
            crosscheck = dict(
                curve_thd_db_at_f0=hit["db"],
                curve_point_hz=hit["at_hz"],
                snapshot_thd_db=snap_db,
                difference_db=round(snap_db - hit["db"], 2),
            )
        result["snapshot"] = dict(summary, thd_curve_crosscheck=crosscheck)
    else:
        result["snapshot"] = None
    result["snapshot_second_channel_matches"] = (
        len(spec1) == len(spec0) and all(
            (math.isfinite(a[1]) and math.isfinite(b[1]) and abs(a[1] - b[1]) < 1e-9
             or (not math.isfinite(a[1]) and not math.isfinite(b[1])))
            and abs(a[0] - b[0]) < 1e-6 for a, b in zip(spec0, spec1)))
    return result


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    report = dict(
        date="2026-10-08",
        host="PluginDoctor 2.3.2 (64 bit), Backend ReaJS (REAPER 2.3.2 64 bit laut Screenshotfuss)",
        captures_root=str(args.source.relative_to(ROOT)),
        sweep_excitation_db=SWEEP_EXCITATION_DB,
        bin_hz=round(BIN_HZ, 5),
        samplerate_backend_hz=44100,
        gs76_panel_settings=GS76_SETTINGS,
        provenance_gaps=[
            "Eingangspegel der GS76-Captures nicht numerisch protokolliert (Sweep-Anregung −0,32 dB laut Screenshot-Toolbar).",
            "SSL-Knopfstellungen MIN/STOCK/MAX nur als Verzeichnisnamen belegt, keine numerischen Werte.",
            "FFT-Snapshot landet je Export an einer anderen Tonfrequenz (Sweep-Position beim Export); Vergleich deshalb über die THD(f)-Kurve und Ordnungsprofile.",
            "GS76-Kurve Graph #1 ist flacher Boden (−100 dB), SSL-Kurve Graph #1 enthält die Grundwelle; Graph-#1-Bedeutung ist nicht kalibriert.",
        ],
        captures=[],
    )
    for name, kind in CAPTURES:
        directory = args.source / name
        entry = analyse_capture(directory, kind)
        entry["name"] = name
        entry["files"] = {}
        for filename in ("THD.txt", "data.txt", "Clipboard01.jpg"):
            path = directory / filename
            stat = path.stat()
            entry["files"][filename] = dict(
                sha256=sha256(path), bytes=stat.st_size,
                mtime=datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
        report["captures"].append(entry)
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / "analysis.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Analysiert: {len(report['captures'])} Captures -> {target.relative_to(ROOT)}")
    for entry in report["captures"]:
        curve = entry["thd_curve"]["at_hz"]
        snap = entry["snapshot"]
        head = entry["name"]
        if snap:
            cross = snap["thd_curve_crosscheck"]
            cross_text = f", Crosscheck Δ {cross['difference_db']:+.2f} dB" if cross else ", kein Kurvencrosscheck"
            percent = snap["thd_from_snapshot"]["percent"]
            percent_text = f"{percent:.2f} %" if percent is not None else "unter Summenboden"
            print(f"  {head}: f0={snap['fundamental']['hz']} Hz @ {snap['fundamental']['dbfs']} dB, "
                  f"THD(Snapshot) {percent_text}{cross_text}")
        else:
            print(f"  {head}: keine Grundwelle im Snapshot")
        keys = ("20", "30", "50", "100", "1000")
        print("    THD(f) dB: " + " ".join(
            f"{k}Hz={curve[k]['db'] if curve.get(k) else '--'}" for k in keys))


if __name__ == "__main__":
    main()
