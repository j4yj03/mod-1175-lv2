#!/usr/bin/env python3
"""Dwarf-Matrix-Session: lange Aufnahme in Wiedergaben schneiden, als Serie
analysieren und gegen die 0.5.2-Referenzrenders stellen.

Subcommands:
  cut      Pilot-Chirp-Erkennung in einer Langaufnahme, Schnitt je Zustand
  analyze  Run-Verzeichnisse (Treiberstruktur) je Quelle und Zustand,
           Auswertung mit tools/scarlett_test.py (Baseline = Referenz-Wiedergabe)
  report   Aggregation results.json -> summary.json + Plots

Aufnahme-Reihenfolge (Benutzer, 2026-10-08):
  reference, 60s, 80s, 00s, sym, col05, col10, col20, col50, col75, col100
Panel: Compression OFF, OS 2x, Input/Output 0 dB, Mix 100, Preset Custom.
"""
import argparse
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import scarlett_test as measurement  # noqa: E402

ORDER = ['reference', '60s', '80s', '00s', 'sym',
         'col05', 'col10', 'col20', 'col50', 'col75', 'col100']
CHIRP_START = 24000
CHIRP_FRAMES = 5760
PROGRAM_END_CHIRP = 2968800
GUARD = 12000
RATE = 48000
LEVEL = -2.0


def program_frames(stimulus_path):
    info = sf.info(str(stimulus_path))
    return info.frames


def block_correlate(signal, template):
    """Normalisierte Korrelationspeaks (matched filter) per FFT-Block."""
    n = len(template)
    t = np.fft.rfft(template, 2 * n)
    t_energy = float(np.dot(template, template))
    fft = 1 << 23
    hop = fft - 2 * n + 1
    hits = []
    for begin in range(0, len(signal), hop):
        chunk = signal[begin:begin + hop]
        if len(chunk) < n:
            break
        size = 1 << (len(chunk) + 2 * n - 1).bit_length()
        spec = np.fft.rfft(chunk, size)
        corr = np.fft.irfft(spec * np.conj(np.fft.rfft(template, size)), size)[:len(chunk) - n + 1]
        # Energie ueber das Template-Fenster: Korrelation von signal^2 mit Fenstern.
        ones = np.fft.rfft(np.ones(n), size)
        energy = np.fft.irfft(np.fft.rfft(chunk ** 2, size) * np.conj(ones), size)[:len(chunk) - n + 1]
        norm = corr / np.sqrt(np.maximum(energy, 0.02 * t_energy) * t_energy)
        norm[energy < 0.02 * t_energy] = 0.0
        idx = np.where(norm > 0.5)[0]
        for i in idx:
            hits.append((float(norm[i]), begin + int(i)))
    hits.sort(key=lambda x: x[1])
    merged = []
    for value, pos in hits:
        if merged and pos - merged[-1][1] < RATE:
            if value > merged[-1][0]:
                merged[-1] = (value, pos)
        else:
            merged.append((value, pos))
    return merged


def find_playbacks(recording, stimulus_frames):
    data, rate = sf.read(str(recording), dtype='float64', always_2d=True)
    if rate != RATE:
        raise SystemExit(f'Rate {rate} != {RATE}')
    mono = np.ascontiguousarray(data[:, 0])
    stim, _ = sf.read(str(_stimulus_path()), dtype='float64', always_2d=True)
    starts = block_correlate(mono, stim[CHIRP_START:CHIRP_START + CHIRP_FRAMES, 0])
    plays = [dict(start=pos, quality=round(value, 3)) for value, pos in starts]
    for p in plays:
        p['program_begin'] = p['start'] - CHIRP_START
    return data, plays


_STIM = None


def _stimulus_path():
    global _STIM
    if _STIM is None:
        _STIM = TOOLS.parent / 'test-results/dwarf-tones/gs76-matrix-all-m2-stereo.wav'
    return _STIM


def do_cut(args):
    stim_frames = program_frames(_stimulus_path())
    data, plays = find_playbacks(args.recording, stim_frames)
    if len(plays) != len(ORDER):
        print(f'WARNUNG: {len(plays)} Wiedergaben gefunden, {len(ORDER)} erwartet')
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for i, play in enumerate(plays[:len(ORDER)]):
        label = ORDER[i]
        begin = max(0, play['program_begin'] - GUARD)
        end = min(len(data), play['program_begin'] + stim_frames + GUARD)
        chunk = data[begin:end]
        dest = out / f'{label}.wav'
        sf.write(str(dest), chunk, RATE, subtype='PCM_24')
        index.append(dict(label=label, file=dest.name, **play))
        print(f"{label:10s} chirp={play['start']} begin={begin} q={play['quality']}")
    (out / 'cuts.json').write_text(json.dumps(
        dict(source=str(args.recording), stimulus=str(_stimulus_path()),
             order=ORDER, playbacks=index), indent=2), encoding='utf-8')
    print(f'{len(index)} Schnitte in {out}')


def prepare_run(directory, recording, channel, baseline):
    directory = Path(directory)
    if (directory / 'results.json').exists():
        return None
    if directory.exists():
        shutil.rmtree(directory)
    measurement.generate(directory, rate=RATE, level=LEVEL, kind='all',
                         frequency=1000, settle=2, measure=1, max_level=-0.1)
    shutil.copy2(recording, directory / 'recording.wav')
    return measurement.analyze(directory, directory / 'recording.wav', channel,
                               baseline, max_delay=10.0)


def do_analyze(args):
    root = Path(args.series)
    cuts_root = Path(args.cuts)
    states = [s for s in ORDER if s != 'reference']
    jobs = []
    for source, channels in (('modsession', (1, 2)), ('reaper', (1, 2))):
        cut_dir = cuts_root / source
        if not (cut_dir / 'cuts.json').exists():
            print(f'skip {source}: keine Schnitte')
            continue
        for ch in channels:
            base_dir = root / source / f'baseline-ch{ch}-{RATE}'
            recording = cut_dir / 'reference.wav'
            if not recording.exists():
                continue
            report = prepare_run(base_dir, recording, ch, None)
            if report is not None:
                _write_results(base_dir, report, ch)
            for state in states:
                recording = cut_dir / f'{state}.wav'
                if not recording.exists():
                    continue
                run = root / source / f'{state}-ch{ch}-{RATE}'
                report = prepare_run(run, recording, ch, base_dir / 'results.json')
                if report is not None:
                    _write_results(run, report, ch)
                jobs.append(f'{source}/{state}-ch{ch}')
            jobs.append(f'{source}/baseline-ch{ch}')
    # C++-Referenzen: Baseline ist der Stimulus selbst (0 dB Bezug).
    cpp = root / 'cpp052'
    base_dir = cpp / f'baseline-ch1-{RATE}'
    report = prepare_run(base_dir, _stimulus_path(), 1, None)
    if report is not None:
        _write_results(base_dir, report, 1)
    refs = Path(args.refs)
    for state in states:
        tf_names = {'60s': 'c0-tf1', '80s': 'c0-tf2', '00s': 'c0-tf3', 'sym': 'c0-tf4'}
        name = tf_names.get(state) or f"c{int(state[3:])}-tf0"
        ref = refs / f'{name}.wav'
        run = cpp / f'{state}-ch1-{RATE}'
        report = prepare_run(run, ref, 1, base_dir / 'results.json')
        if report is not None:
            _write_results(run, report, 1)
        jobs.append(f'cpp052/{state}-ch1')
    print(f'{len(jobs)} Runs ausgewertet in {root}')


def _write_results(directory, report, channel):
    with (Path(directory) / 'results.json').open('w', encoding='utf-8',
                                                 newline='') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def _load_run(root, source, state, ch):
    label = state if state != 'reference' else 'baseline'
    path = root / source / f'{label}-ch{ch}-{RATE}' / 'results.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    sync = data.get('synchronization', {})
    segs = {}
    for seg in data.get('segments', []):
        segs[seg['id']] = seg
    return dict(clock_scale=sync.get('clock_scale'), offset_frames=sync.get('offset_frames'),
                noise_dbfs=data.get('noise_floor_dbfs'), level_check=data.get('level_check'),
                segments=segs, sync_quality=sync.get('quality'))


def do_report(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    root = Path(args.series)
    states = [s for s in ORDER if s != 'reference']
    sweep_ids = list(range(2, 15))
    level_ids = list(range(15, 20))
    summary = dict(schema_version=1, created=str(args.series), states=states, sources={})
    for source in ('modsession', 'reaper', 'cpp052'):
        entry = {}
        for state in ['reference'] + states:
            for ch in ((1,) if source == 'cpp052' else (1, 2)):
                run = _load_run(root, source, state, ch)
                if run:
                    entry.setdefault(state, {})[f'ch{ch}'] = run
        summary['sources'][source] = entry

    def relgain(run, seg_id):
        seg = run['segments'].get(seg_id, {})
        return seg.get('relative_gain_db')

    def thd(run, seg_id):
        return run['segments'].get(seg_id, {}).get('thd_percent')

    comparisons = {}
    for state in states:
        dev = summary['sources']['modsession'].get(state, {}).get('ch1')
        cpp = summary['sources']['cpp052'].get(state, {}).get('ch1')
        if not dev or not cpp:
            continue
        rows = []
        for seg_id in [1] + sweep_ids + level_ids:
            d, c = relgain(dev, seg_id), relgain(cpp, seg_id)
            seg = dev['segments'].get(seg_id, {})
            rows.append(dict(id=seg_id, group=seg.get('group'), hz=seg.get('frequency_hz'),
                             level_dbfs=seg.get('peak_dbfs'),
                             dev_rel_db=d, cpp_rel_db=c,
                             delta_db=None if (d is None or c is None) else round(d - c, 4),
                             dev_thd=thd(dev, seg_id), cpp_thd=thd(cpp, seg_id)))
        comparisons[state] = rows
    summary['comparison'] = comparisons
    out = root / 'summary.json'
    out.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding='utf-8')
    print(f'{out} geschrieben')

    plots = root / 'plots'
    plots.mkdir(exist_ok=True)
    freqs = [dev['segments'][i]['frequency_hz'] for i in sweep_ids
             if dev and i in dev['segments']]

    # 1) Relativer Gain ueber Frequenz je Transformator (Device vs C++).
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey=True)
    for ax, state in zip(axes.flat, ['60s', '80s', '00s', 'sym']):
        dev = summary['sources']['modsession'].get(state, {}).get('ch1')
        dev2 = summary['sources']['modsession'].get(state, {}).get('ch2')
        cpp = summary['sources']['cpp052'].get(state, {}).get('ch1')
        y = [relgain(dev, i) for i in sweep_ids]
        y2 = [relgain(dev2, i) for i in sweep_ids]
        yc = [relgain(cpp, i) for i in sweep_ids]
        ax.semilogx(freqs, y, 'o-', label='Dwarf ch1')
        ax.semilogx(freqs, y2, 's--', label='Dwarf ch2', alpha=0.6)
        ax.semilogx(freqs, yc, 'x:', label='0.5.2 Referenz (C++)', color='k')
        ax.set_title(f'Transformer {state}')
        ax.grid(True, which='both', alpha=0.3)
        ax.axhline(0, color='gray', lw=0.5)
    axes[1, 0].set_xlabel('Frequenz / Hz')
    axes[1, 1].set_xlabel('Frequenz / Hz')
    axes[0, 0].set_ylabel('relativer Gain / dB')
    axes[1, 0].set_ylabel('relativer Gain / dB')
    axes[0, 0].legend(loc='lower left', fontsize=8)
    fig.suptitle('0.5.2 am Gerät — relativer Gain gegen Bypass (Sweeps, −2 dBFS)')
    fig.tight_layout()
    fig.savefig(plots / 'gain-frequency.png', dpi=140)
    plt.close(fig)

    # 2) 20-Hz-KlirrReihung.
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ['60s', '80s', '00s', 'sym']
    x = np.arange(len(labels))
    dev_thd, cpp_thd = [], []
    for state in labels:
        dev = summary['sources']['modsession'].get(state, {}).get('ch1')
        cpp = summary['sources']['cpp052'].get(state, {}).get('ch1')
        dev_thd.append(thd(dev, 2) if dev else None)
        cpp_thd.append(thd(cpp, 2) if cpp else None)
    ax.bar(x - 0.18, [v or 0 for v in dev_thd], 0.36, label='Dwarf ch1')
    ax.bar(x + 0.18, [v or 0 for v in cpp_thd], 0.36, label='0.5.2 Referenz (C++)')
    for i, v in enumerate(dev_thd):
        if v:
            ax.text(x[i] - 0.18, v, f'{v:.2f}', ha='center', va='bottom', fontsize=8)
    for i, v in enumerate(cpp_thd):
        if v:
            ax.text(x[i] + 0.18, v, f'{v:.2f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(x, labels)
    ax.set_ylabel('THD @ 20 Hz / %')
    ax.set_title('20-Hz-Klirr, Transformer-Reihung (Compression OFF, OS 2x)')
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(plots / 'thd-20hz.png', dpi=140)
    plt.close(fig)

    # 3) Colour-Sweep: 1-kHz-Klirr und Gain.
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    cols = [5, 10, 20, 50, 75, 100]
    key = {5: 'col05', 10: 'col10', 20: 'col20', 50: 'col50', 75: 'col75', 100: 'col100'}
    dev_t, cpp_t, dev_g, cpp_g = [], [], [], []
    for c in cols:
        d = summary['sources']['modsession'].get(key[c], {}).get('ch1')
        cp = summary['sources']['cpp052'].get(key[c], {}).get('ch1')
        dev_t.append(thd(d, 1) if d else None)
        cpp_t.append(thd(cp, 1) if cp else None)
        dev_g.append(relgain(d, 1) if d else None)
        cpp_g.append(relgain(cp, 1) if cp else None)
    ax1.plot(cols, dev_t, 'o-', label='Dwarf ch1')
    ax1.plot(cols, cpp_t, 'x:', label='0.5.2 Referenz (C++)', color='k')
    ax1.set_xlabel('Colour / %')
    ax1.set_ylabel('THD @ 1 kHz / %')
    ax1.set_title('1-kHz-Klirr ueber Colour (Transformer None)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax2.plot(cols, dev_g, 'o-', label='Dwarf ch1')
    ax2.plot(cols, cpp_g, 'x:', label='0.5.2 Referenz (C++)', color='k')
    ax2.set_xlabel('Colour / %')
    ax2.set_ylabel('relativer Gain @ 1 kHz / dB')
    ax2.set_title('Relativer Gain ueber Colour')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(plots / 'colour-sweep.png', dpi=140)
    plt.close(fig)

    # 4) Pegelreihe (1 kHz, −26..−2 dBFS): Saettigungsabhaengigkeit.
    fig, axes = plt.subplots(1, 4, figsize=(13, 4), sharey=True)
    ref60 = summary['sources']['modsession'].get('60s', {}).get('ch1')
    lvls = [ref60['segments'][i]['peak_dbfs'] for i in level_ids if ref60 and i in ref60['segments']]
    for ax, state in zip(axes, ['60s', '80s', '00s', 'sym']):
        dev = summary['sources']['modsession'].get(state, {}).get('ch1')
        cpp = summary['sources']['cpp052'].get(state, {}).get('ch1')
        ax.plot(lvls, [relgain(dev, i) for i in level_ids], 'o-', label='Dwarf ch1')
        ax.plot(lvls, [relgain(cpp, i) for i in level_ids], 'x:', label='0.5.2 Referenz', color='k')
        ax.set_title(f'Transformer {state}')
        ax.set_xlabel('Pegel / dBFS')
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel('relativer Gain / dB')
    axes[0].legend(fontsize=8)
    fig.suptitle('Pegelreihe 1 kHz (relativ zum Bypass)')
    fig.tight_layout()
    fig.savefig(plots / 'levels.png', dpi=140)
    plt.close(fig)
    print(f'Plots in {plots}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    cut = sub.add_parser('cut', help='Langaufnahme in Wiedergaben schneiden')
    cut.add_argument('recording', type=Path)
    cut.add_argument('--output', type=Path, required=True)
    cut.set_defaults(func=do_cut)
    ana = sub.add_parser('analyze', help='Schnitte als Serie auswerten')
    ana.add_argument('--cuts', type=Path, required=True)
    ana.add_argument('--series', type=Path, required=True)
    ana.add_argument('--refs', type=Path, default=Path('/tmp/opencode/ref052'))
    ana.set_defaults(func=do_analyze)
    rep = sub.add_parser('report', help='Aggregation + Zusammenfassung')
    rep.add_argument('--series', type=Path, required=True)
    rep.set_defaults(func=do_report)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
