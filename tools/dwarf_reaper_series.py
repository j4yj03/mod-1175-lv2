#!/usr/bin/env python3
"""Import REAPER-recorded Dwarf playbacks into the scarlett_matrix series.

Workflow for the Dwarf-as-source series when REAPER (not the script's
PortAudio recorder) captures the Scarlett inputs: the user plays a test-tone
file once on the Dwarf and records it in REAPER (stereo, 48 kHz); this tool
maps that one stereo recording onto the per-channel run directories of
tools/scarlett_matrix.py, analyses both channels and maintains the same
index.json/summary.json structure.

One playback covers both channels: the stereo file is copied into the ch1 and
ch2 run directories and analysed with input channel 1 and 2 respectively
(DUT runs use the matching per-channel baseline).

Offline only: numpy + soundfile. See docs/MESSTECHNIK.md, section
'Dwarf als Signalquelle'.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import scarlett_matrix as driver  # noqa: E402
import scarlett_test as measurement  # noqa: E402

RATES = (44100, 48000, 96000)


def slug_for(transformer):
    return driver.SLUGS[transformer.strip().lower()]


def name_for(role, transformer, channel, repeat, rate):
    if role == 'gainmatch':
        return f'gainmatch-ch{channel}-{rate}'
    if role == 'baseline':
        return f'baseline-ch{channel}-r{repeat}-{rate}'
    return f'{slug_for(transformer)}-ch{channel}-r{repeat}-{rate}'


def import_run(directory, recording, rate, level, kind, frequency, settle, measure,
               input_channel, baseline, label):
    """Generate the run directory, copy the recording in, analyse, report."""
    driver.prepare_directory(directory)
    measurement.generate(directory, rate, level, kind, frequency, settle, measure,
                         max_level=-0.1)
    shutil.copy2(recording, directory / 'recording.wav')
    report = measurement.analyze(directory, directory / 'recording.wav',
                                 input_channel, baseline, max_delay=10.0)
    with (directory / 'recording.json').open('w', encoding='utf-8',
                                             newline='') as stream:
        json.dump(dict(source_wav=str(recording), analyzed_input_channel=input_channel,
                       imported=True, label=label),
                  stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    return report


def do_import(args):
    parts = [part.strip() for part in args.spec.split(':')]
    role = parts[0].lower()
    transformer = None
    repeat = None
    if role == 'gainmatch':
        if len(parts) != 1:
            raise ValueError("'gainmatch' takes no suffix")
    elif role == 'baseline':
        if len(parts) != 2 or not (parts[1].startswith('r') and parts[1][1:].isdigit()):
            raise ValueError("baseline spec is 'baseline:rN'")
        repeat = int(parts[1][1:])
    else:
        transformer = driver.NAMES.get(role)
        if transformer is None or len(parts) != 2 \
                or not (parts[1].startswith('r') and parts[1][1:].isdigit()):
            raise ValueError("transformer spec is 'None:rN' | '60s:rN' | '80s:rN' "
                             "| '00s:rN' | 'Sym:rN'")
        role = 'dut'
        repeat = int(parts[1][1:])
    rate = args.rate
    if rate not in RATES:
        raise ValueError('Supported rates: 44100, 48000, 96000 Hz')
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    index = driver.load_index(root)
    if index.get('created_utc') is None:
        index['created_utc'] = driver.now_utc()
    if index.get('settings_label') is None:
        index['settings_label'] = args.settings_label
    index['dwarf_source'] = True
    wav = Path(args.recording)
    if not wav.is_file():
        raise ValueError(f'Recording not found: {wav}')
    kind = 'tone' if role == 'gainmatch' else 'all'
    channels = args.channels if role == 'gainmatch' else (1, 2)
    for channel in channels:
        directory = root / name_for(role, transformer, channel, repeat, rate)
        label = driver.run_label(role.capitalize() if role != 'dut' else 'DUT',
                                 transformer, channel, repeat, rate,
                                 args.level, args.settings_label)
        baseline = _baseline_path(root, channel, rate) if role == 'dut' else None
        report = import_run(directory, wav, rate, args.level, kind,
                            args.frequency, args.settle, args.measure,
                            channel, baseline, label)
        entry = dict(role=role, channel=channel, rate=rate,
                     directory=str(directory), label=label,
                     stimulus_level_dbfs=args.level, valid=report['valid'],
                     loop_gain_db=driver.loop_gain_db(report),
                     level_check=report.get('level_check'),
                     rate_mismatch=bool((report.get('capture') or {})
                                        .get('rate_mismatch')))
        if transformer:
            entry['transformer'] = transformer
        if repeat is not None:
            entry['repeat'] = repeat
        driver.record_run(index, **entry)
        driver.save_index(root, index)
        gain = entry['loop_gain_db']
        state = 'unbestimmbar' if gain is None else f'{gain:+.2f} dB'
        print(f'{role} ch{channel}'
              + (f' r{repeat}' if repeat is not None else '')
              + f' @{rate}: gueltig={report["valid"]} Loop-Gewinn={state} '
              f'({directory / "REPORT.md"})')
    if role == 'gainmatch':
        _record_gainmatch_summary(root, index, rate, args.tolerance)
    return 0


def _baseline_path(root, channel, rate):
    entries = [run for run in driver.load_index(root)['runs']
               if run['role'] == 'baseline' and run['channel'] == channel
               and run['rate'] == rate and run.get('valid')]
    if not entries:
        raise ValueError(f'Keine gueltige Baseline fuer Kanal {channel} @ {rate} Hz; '
                         'erst "baseline:r1" importieren.')
    return Path(entries[-1]['directory']) / 'results.json'


def _record_gainmatch_summary(root, index, rate, tolerance):
    runs = [run for run in index['runs'] if run['role'] == 'gainmatch'
            and run['rate'] == rate]
    values = {run['channel']: run.get('loop_gain_db') for run in runs}
    first, second = values.get(1), values.get(2)
    delta = None if first is None or second is None else second - first
    index['gainmatch'] = index.get('gainmatch') or {}
    index['gainmatch'][str(rate)] = dict(channel1_db=first, channel2_db=second,
                                         delta_db=delta, tolerance_db=tolerance)
    driver.save_index(root, index)
    if delta is not None:
        print(f'Kanal-Differenz Ch2-Ch1 @{rate}: {delta:+.2f} dB '
              f'(Toleranz +-{tolerance:.1f} dB -> '
              + ('OK' if abs(delta) <= tolerance else 'NACHSTELLEN') + ')')


def do_summary(args):
    root = Path(args.root)
    summary = driver.build_summary(root, driver.load_index(root))
    print(f'Auswertung: {(root / "SUMMARY.md").resolve()}')
    return 0 if not summary['issues'] else 1


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--root', required=True, type=Path,
                        help='Measurement root (same layout as scarlett_matrix.py)')
    common.add_argument('--rate', type=int, default=48000)
    common.add_argument('--level', type=float, default=-2,
                        help='File peak level in dBFS (uploaded Dwarf file)')
    common.add_argument('--frequency', type=float, default=1000)
    common.add_argument('--settle', type=float, default=2)
    common.add_argument('--measure', type=float, default=1)
    common.add_argument('--settings-label', default='')
    common.add_argument('--channels', nargs='+', type=int, default=(1, 2),
                        choices=(1, 2),
                        help='Channels to analyse (gainmatch: one run per channel)')
    common.add_argument('--tolerance', type=float, default=1.0)
    imp = sub.add_parser('import', parents=[common],
                         help='Import one REAPER stereo recording')
    imp.add_argument('--recording', required=True, type=Path)
    imp.add_argument('--spec', required=True,
                     help="'gainmatch' | 'baseline:r1' | '60s:r1' "
                          "(transformer None/60s/80s/00s/Sym)")
    sub.add_parser('summary', parents=[common], help='Aggregate the series')
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == 'import':
            return do_import(args)
        return do_summary(args)
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f'Import failed: {error}\n')


if __name__ == '__main__':
    sys.exit(main())
