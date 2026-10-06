#!/usr/bin/env python3
"""Automated Scarlett/Dwarf measurement series for Green Stripe 76.

Wraps tools/scarlett_test.py into a driver that can be started from Windows
CMD: input-gain match probe, bypass baselines and the transformer matrix with
repeats, median and spread. Hardware steps (Dwarf settings) are prompted
between conditions; everything else runs without interaction.
See docs/MESSTECHNIK.md for wiring, level rules and interpretation limits.
"""
import argparse
import json
import shutil
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import scarlett_test as measurement  # noqa: E402

ANCHORS_DBFS = (-14.0, -8.0, -2.0)
DEFAULT_TRANSFORMERS = ('None', '60s', '80s', '00s', 'Sym')
SLUGS = {'none': 'none', '60s': '60s', '80s': '80s', '00s': '00s', 'sym': 'sym'}
NAMES = {'none': 'None', '60s': '60s', '80s': '80s', '00s': '00s', 'sym': 'Sym'}
LEVEL_LIMIT_DBFS = -3.0
SUPPORT_RATES = (44100, 48000, 96000)


def slug(name):
    key = name.strip().lower()
    if key not in SLUGS:
        raise ValueError(f'Unknown transformer "{name}"; use one of '
                         f'{", ".join(sorted(SLUGS))}')
    return SLUGS[key]


def parse_transformers(text):
    names = []
    for part in text.split(','):
        if not part.strip():
            continue
        key = part.strip().lower()
        if key not in NAMES:
            raise ValueError(f'Unknown transformer "{part.strip()}"; use one of '
                             f'{", ".join(sorted(SLUGS))}')
        names.append(NAMES[key])
    if not names:
        raise ValueError('Empty transformer list')
    return tuple(names)


def find_devices(sd, hostapi_name):
    devices = list(sd.query_devices())
    apis = list(sd.query_hostapis())
    wanted = [index for index, api in enumerate(apis)
              if str(api.get('name', '')).lower() == hostapi_name.lower()]
    if not wanted:
        raise ValueError(f'Host API "{hostapi_name}" not available; found: '
                         f'{", ".join(str(a.get("name")) for a in apis)}')
    api = wanted[0]

    def pick(kind):
        found = [i for i, device in enumerate(devices)
                 if device.get('hostapi') == api
                 and device.get(f'max_{kind}_channels', 0) >= 2
                 and 'focusrite' in str(device.get('name', '')).lower()]
        if not found:
            candidates = [f'{i}:{device.get("name")}' for i, device in enumerate(devices)
                          if device.get('hostapi') == api
                          and device.get(f'max_{kind}_channels', 0) >= 2]
            raise ValueError(f'No Focusrite {kind} device on {hostapi_name}; '
                             f'candidates: {", ".join(candidates)}')
        return found[0]

    return pick('input'), pick('output')


def loop_gain_db(report):
    rows = [row for row in report['segments']
            if row.get('group') == 'tone' and row.get('valid')
            and row.get('gain_db') is not None]
    return min((row['gain_db'] for row in rows), default=None)


def choose_stimulus_level(loop_gain, anchors=ANCHORS_DBFS, limit=LEVEL_LIMIT_DBFS):
    """Stimulus peak so the levels series hits the anchors at the plugin input.

    Anchors sit 6 dB apart, exactly like the levels series steps, so one
    stimulus level aligns all of them at once. The highest anchor needs
    loop_gain >= max(anchors) - limit; otherwise no series step lands on an
    anchor and the run must be rejected (raise the Dwarf input gain first).
    """
    if loop_gain is None:
        raise ValueError('Loop gain unknown; run the gain-match probe first')
    if not -60 <= limit <= -3:
        raise ValueError('Stimulus level limit must be within -60..-3 dBFS')
    wanted = max(anchors) - loop_gain
    level = min(wanted, limit)
    reachable = [anchor for anchor in anchors if anchor - loop_gain <= limit + 1e-9]
    missing = [anchor for anchor in anchors if anchor not in reachable]
    return level, reachable, missing


def required_loop_gain(anchors=ANCHORS_DBFS, limit=LEVEL_LIMIT_DBFS):
    return max(anchors) - limit


def prepare_directory(directory):
    """Remove an incomplete leftover; refuse to overwrite a completed run."""
    directory = Path(directory)
    if directory.exists():
        if (directory / 'recording.wav').exists() and (directory / 'results.json').exists():
            raise ValueError(f'{directory} already holds a completed run; '
                             'delete it or choose another root')
        shutil.rmtree(directory)
    return directory


def run_measurement(directory, *, input_device, output_device, rate, level, kind,
                    frequency, settle, measure, output_channel, input_channel,
                    label, baseline=None, play=True, pad_seconds=10.0):
    prepare_directory(directory)
    # Dwarf source: the stimulus is the digital plugin input, so the old
    # -3 dBFS ADC-protection cap does not apply to the file level.
    measurement.generate(directory, rate, level, kind, frequency, settle, measure,
                         max_level=-0.1 if play is False else -3)
    wav = measurement.record(directory, input_device, output_device, output_channel,
                             input_channel, label, play=play, pad_seconds=pad_seconds)
    report = measurement.analyze(directory, wav, input_channel, baseline,
                                 max_delay=pad_seconds if not play else 2.0)
    return report


def load_index(root):
    path = Path(root) / 'index.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return dict(schema=1, created_utc=None, settings_label=None, runs=[])


def save_index(root, index):
    path = Path(root) / 'index.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        json.dump(index, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def now_utc():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def record_run(index, **entry):
    entry['created_utc'] = now_utc()
    index['runs'].append(entry)
    return entry


def run_label(role, transformer, channel, repeat, rate, level, settings_label):
    parts = [role]
    if transformer:
        parts.append(f'TF{transformer}')
    parts.append(f'Ch{channel}')
    if repeat:
        parts.append(f'R{repeat}')
    parts.append(f'{rate}Hz')
    parts.append(f'Stimulus{level:g}dBFS')
    if settings_label:
        parts.append(settings_label)
    return '; '.join(parts)


def prompt(message, assume_yes):
    if assume_yes:
        print(f'[auto] {message}')
        return
    try:
        input(message)
    except EOFError:
        print('[auto] no interactive input; continuing')


class Driver:
    def __init__(self, args):
        if any(rate not in SUPPORT_RATES for rate in args.rates):
            raise ValueError('Supported rates: 44100, 48000, 96000 Hz')
        self.args = args
        self.root = Path(args.root) if args.root else None
        self.index = None
        self.devices = None

    def open_root(self):
        if self.root is None:
            stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            self.root = Path('test-results') / f'matrix-{stamp}'
        self.root.mkdir(parents=True, exist_ok=True)
        self.index = load_index(self.root)
        if self.index.get('created_utc') is None:
            self.index['created_utc'] = now_utc()
        if self.index.get('settings_label') is None:
            self.index['settings_label'] = self.args.settings_label
        if self.args.relax_anchors:
            self.index['relax_anchors'] = True
        return self.root

    def resolve_devices(self):
        if self.args.dwarf_source:
            if self.args.input_device is not None:
                self.devices = (self.args.input_device, None)
            elif self.devices is None:
                input_only = find_devices(measurement.sounddevice(), self.args.hostapi)
                self.devices = (input_only[0], None)
            return self.devices
        if self.args.input_device is not None and self.args.output_device is not None:
            self.devices = (self.args.input_device, self.args.output_device)
        elif self.devices is None:
            self.devices = find_devices(measurement.sounddevice(), self.args.hostapi)
        return self.devices

    def loop_gain_for(self, rate):
        current = (self.index.get('gainmatch') or {}).get(str(rate)) or {}
        values = [current.get('channel1_db'), current.get('channel2_db')]
        values = [value for value in values if value is not None]
        if values:
            return statistics.median(values)
        entries = [run for run in self.index['runs']
                   if run['role'] == 'baseline' and run['rate'] == rate
                   and run.get('loop_gain_db') is not None]
        if not entries:
            return None
        return statistics.median([run['loop_gain_db'] for run in entries])

    def baseline_for(self, channel, rate):
        entries = [run for run in self.index['runs']
                   if run['role'] == 'baseline' and run['channel'] == channel
                   and run['rate'] == rate and run.get('valid')]
        if not entries:
            raise ValueError(f'No valid baseline for channel {channel} at {rate} Hz; '
                             'run the baseline step first')
        return Path(entries[-1]['directory']) / 'results.json'

    def gainmatch(self):
        args = self.args
        self.open_root()
        input_device, output_device = self.resolve_devices()
        results = {}
        for rate in args.rates:
            for channel in (1, 2):
                directory = self.root / f'gainmatch-ch{channel}-{rate}'
                if directory.exists():
                    shutil.rmtree(directory)  # probe result; a re-probe replaces it
                label = run_label('Gainmatch', None, channel, None, rate, args.level,
                                  args.settings_label)
                self.dwarf_play_prompt('Dwarf: Gainmatch-Ton-Datei starten. ')
                report = run_measurement(
                    directory, input_device=input_device, output_device=output_device,
                    rate=rate, level=args.level, kind='tone', frequency=args.frequency,
                    settle=args.settle, measure=args.measure, output_channel=channel,
                    input_channel=channel, label=label,
                    play=not args.dwarf_source, pad_seconds=args.pad)
                gain = loop_gain_db(report)
                results[(rate, channel)] = gain
                record_run(self.index, role='gainmatch', channel=channel, rate=rate,
                           directory=str(directory), label=label, valid=report['valid'],
                           loop_gain_db=gain, level_check=report.get('level_check'),
                           rate_mismatch=bool((report.get('capture') or {}).get('rate_mismatch')))
                save_index(self.root, self.index)
                state = 'unbestimmbar' if gain is None else f'{gain:+.2f} dB'
                print(f'Loop-Gewinn Ch{channel} @{rate}: {state} (gueltig={report["valid"]})')
            first, second = results.get((rate, 1)), results.get((rate, 2))
            delta = None if first is None or second is None else second - first
            self.index['gainmatch'] = self.index.get('gainmatch') or {}
            self.index['gainmatch'][str(rate)] = dict(channel1_db=first, channel2_db=second,
                                                      delta_db=delta,
                                                      tolerance_db=args.tolerance)
            save_index(self.root, self.index)
            if delta is None:
                print('Gain-Abgleich: Messung unvollstaendig; Kabel/Routing/Pegel pruefen.')
                continue
            adequate = min(g for g in (first, second) if g is not None) >= -20.0
            print(f'Kanal-Differenz Ch2-Ch1 @{rate}: {delta:+.2f} dB '
                  f'(Toleranz +-{args.tolerance:.1f} dB -> '
                  + ('OK' if abs(delta) <= args.tolerance else 'NACHSTELLEN') + ')')
            print('Loop-Gewinn ' + ('ausreichend (>= -20 dB)' if adequate
                                    else 'ZU NIEDRIG; Windows-Pegel/Dwarf-Input-Gain anheben'))
            if not adequate or abs(delta) > args.tolerance:
                print('Input-Gain am Dwarf je Kanal nachstellen und "gainmatch" '
                      'erneut ausfuehren.')
        return results

    def anchor_guard(self, rate):
        """Abort unless the loop gain can place all anchors on levels steps."""
        if self.args.dwarf_source:
            # The uploaded file IS the plugin input: the levels series
            # (level-24 .. level in 6 dB steps) aligns the digital anchors
            # exactly when level = -2 dBFS. Loop gain only affects the
            # recording level, not the plugin input.
            level = self.args.level
            series = [level - step for step in (24, 18, 12, 6, 0)]
            reachable = [a for a in ANCHORS_DBFS
                         if any(abs(a - s) < 1e-9 for s in series)]
            missing = [a for a in ANCHORS_DBFS if a not in reachable]
            if missing:
                print(f'Rate {rate} Hz: Dwarf-Quelle mit Pegel {level:g} dBFS; '
                      f'Anker {", ".join(f"{a:g}" for a in missing)} dBFS liegen '
                      'nicht auf den Pegelstufen (Datei mit -2 dBFS verwenden).')
            return level, reachable, missing
        loop_gain = self.loop_gain_for(rate)
        if loop_gain is None:
            return None, [], list(ANCHORS_DBFS)
        level, reachable, missing = choose_stimulus_level(loop_gain)
        if missing and not self.args.relax_anchors:
            raise ValueError(
                f'Rate {rate} Hz: Loop-Gewinn {loop_gain:+.2f} dB ist zu niedrig; '
                f'fuer alle Anker {", ".join(f"{a:g}" for a in ANCHORS_DBFS)} dBFS am '
                f'Plugin-Eingang ist >= {required_loop_gain():+.1f} dB noetig. '
                'Dwarf-Input-Gain beider Kanaele gleich hoch anheben und "gainmatch" '
                'erneut ausfuehren; --relax-anchors misst mit abweichenden Ankerpegeln.')
        return level, reachable, missing

    def dwarf_play_prompt(self, what):
        """Each Dwarf-source run starts with a silent recording head; the user
        presses Enter and starts the file playback on the Dwarf right after."""
        if self.args.dwarf_source:
            prompt(f'{what} Enter startet die Aufnahme; JETZT SOFORT danach die '
                   'Testton-Datei auf dem Dwarf starten.', self.args.yes)

    def baseline(self):
        args = self.args
        self.open_root()
        input_device, output_device = self.resolve_devices()
        for rate in args.rates:
            level, reachable, missing = self.anchor_guard(rate)
            if level is None:
                print(f'Kein Loop-Gewinn fuer {rate} Hz bekannt; Stimulus-Pegel '
                      f'{args.level:g} dBFS ohne Anker-Abgleich.')
                level, reachable, missing = args.level, [], list(ANCHORS_DBFS)
            if missing:
                print(f'Rate {rate} Hz: --relax-anchors aktiv; Anker '
                      f'{", ".join(f"{a:g}" for a in missing)} dBFS werden mit '
                      'abweichenden Pegeln gemessen.')
            print(f'Rate {rate} Hz: Stimulus-Pegel {level:g} dBFS '
                  f'(erreicht Anker {", ".join(f"{a:g}" for a in reachable) or "keine"} '
                  'am Plugin-Eingang).')
            done = {(run['channel'], run['repeat']) for run in self.index['runs']
                    if run['role'] == 'baseline' and run['rate'] == rate}
            if done:
                print(f'Baseline fuer {rate} Hz vorhanden; vorhandene Laeufe werden '
                      'wiederverwendet.')
            prompt('Dwarf: GS76 geladen und BYPASS aktiv, Regler unveraendert lassen. '
                   'Enter startet die Baseline-Laeufe.', args.yes)
            for channel in (1, 2):
                for repeat in range(1, args.baseline_repeats + 1):
                    if (channel, repeat) in done:
                        continue
                    directory = self.root / f'baseline-ch{channel}-r{repeat}-{rate}'
                    label = run_label('Baseline-Bypass', None, channel, repeat, rate,
                                      level, args.settings_label)
                    self.dwarf_play_prompt('Dwarf: Datei mit GS76 BYPASS aktiv starten. ')
                    report = run_measurement(
                        directory, input_device=input_device, output_device=output_device,
                        rate=rate, level=level, kind='all', frequency=args.frequency,
                        settle=args.settle, measure=args.measure, output_channel=channel,
                        input_channel=channel, label=label,
                        play=not args.dwarf_source, pad_seconds=args.pad)
                    record_run(self.index, role='baseline', channel=channel,
                               repeat=repeat, rate=rate, directory=str(directory),
                               label=label, stimulus_level_dbfs=level,
                               valid=report['valid'], loop_gain_db=loop_gain_db(report),
                               level_check=report.get('level_check'),
                               rate_mismatch=bool((report.get('capture') or {})
                                                  .get('rate_mismatch')))
                    save_index(self.root, self.index)
                    print(f'Baseline Ch{channel} R{repeat} @{rate}: '
                          f'gueltig={report["valid"]} ({directory / "REPORT.md"})')
        return self.index

    def matrix(self):
        args = self.args
        self.open_root()
        input_device, output_device = self.resolve_devices()
        for rate in args.rates:
            level, reachable, missing = self.anchor_guard(rate)
            if level is None:
                raise ValueError(f'No loop gain for {rate} Hz; run baseline first')
            done = {(run['transformer'], run['channel'], run['repeat'])
                    for run in self.index['runs']
                    if run['role'] == 'dut' and run['rate'] == rate}
            for name in parse_transformers(args.transformers):
                remaining = [(channel, repeat)
                             for channel in (1, 2)
                             for repeat in range(1, args.repeats + 1)
                             if (name, channel, repeat) not in done]
                if not remaining:
                    continue
                prompt(f'Dwarf: Transformer "{name}" einstellen, Bypass AUS, alle '
                       'uebrigen Regler unveraendert. Enter startet '
                       f'{len(remaining)} Laeufe @ {rate} Hz.', args.yes)
                for channel, repeat in remaining:
                    directory = self.root / f'{slug(name)}-ch{channel}-r{repeat}-{rate}'
                    label = run_label('DUT', name, channel, repeat, rate, level,
                                      args.settings_label)
                    baseline = self.baseline_for(channel, rate)
                    self.dwarf_play_prompt('Dwarf: Matrix-Datei mit dem eingestellten '
                                           'Transformator starten. ')
                    report = run_measurement(
                        directory, input_device=input_device, output_device=output_device,
                        rate=rate, level=level, kind='all', frequency=args.frequency,
                        settle=args.settle, measure=args.measure, output_channel=channel,
                        input_channel=channel, label=label, baseline=baseline,
                        play=not args.dwarf_source, pad_seconds=args.pad)
                    record_run(self.index, role='dut', transformer=name,
                               channel=channel, repeat=repeat, rate=rate,
                               directory=str(directory), label=label,
                               stimulus_level_dbfs=level, valid=report['valid'],
                               loop_gain_db=loop_gain_db(report),
                               level_check=report.get('level_check'),
                               rate_mismatch=bool((report.get('capture') or {})
                                                  .get('rate_mismatch')))
                    save_index(self.root, self.index)
                    print(f'DUT {name} Ch{channel} R{repeat} @{rate}: '
                          f'gueltig={report["valid"]} ({directory / "REPORT.md"})')
        return self.index

    def full(self):
        args = self.args
        self.open_root()
        print(f'Messreihe: {self.root.resolve()}')
        if args.dwarf_source:
            print('Checkliste: Windows nur Aufnahme 48 kHz/24 bit, Signalverbesserungen '
                  'aus; Dwarf-Board mit File-Player + GS76 geladen, Testton-Dateien '
                  'hochgeladen (siehe tools/make_dwarf_tones.py).')
        else:
            print('Checkliste: Windows Wiedergabe+Aufnahme 48 kHz, Signalverbesserungen '
                  'aus, Direct Monitor OFF, Dwarf-Board geladen.')
        if args.skip_gainmatch:
            print('Gainmatch uebersprungen (--skip-gainmatch).')
        else:
            self.gainmatch()
        self.baseline()
        self.matrix()
        print(f'Auswertung: {(self.root / "SUMMARY.md").resolve()}')
        return build_summary(self.root, self.index)


def aggregate_dut(runs):
    """runs: index entries of one (transformer, channel, rate) group."""
    per_segment = {}
    for run in runs:
        report = json.loads((Path(run['directory']) / 'results.json')
                            .read_text(encoding='utf-8'))
        for row in report['segments']:
            bucket = per_segment.setdefault(row['id'], dict(
                id=row['id'], group=row['group'], frequency_hz=row['frequency_hz'],
                peak_dbfs=row['peak_dbfs'], relative=[], thd=[], thdn=[], valid=[]))
            bucket['relative'].append(row.get('relative_gain_db'))
            bucket['thd'].append(row.get('thd_percent'))
            bucket['thdn'].append(row.get('thdn_percent'))
            bucket['valid'].append(bool(row.get('valid')))
    return per_segment


def stat_row(values):
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return dict(median=statistics.median(clean), spread=max(clean) - min(clean),
                count=len(clean))


def segment_metadata(groups):
    """id -> segment dict, taken from the first available report."""
    for runs in groups:
        for run in runs:
            path = Path(run['directory']) / 'results.json'
            if path.exists():
                report = json.loads(path.read_text(encoding='utf-8'))
                return {row['id']: row for row in report['segments']}
    return {}


def frequency_ids(metadata):
    return {row['frequency_hz']: row['id'] for row in metadata.values()
            if row.get('group') == 'sweep'}


def current_loop_gains(index):
    """Current loop gain per rate: gainmatch values first, baseline median fallback."""
    probes = index.get('gainmatch') or {}
    gains = {}
    rates = {run['rate'] for run in index['runs']} | {int(key) for key in probes}
    for rate in rates:
        probe = probes.get(str(rate)) or {}
        values = [probe.get('channel1_db'), probe.get('channel2_db')]
        values = [value for value in values if value is not None]
        if values:
            gains[rate] = statistics.median(values)
            continue
        entries = [run['loop_gain_db'] for run in index['runs']
                   if run['role'] == 'baseline' and run['rate'] == rate
                   and run.get('loop_gain_db') is not None]
        if entries:
            gains[rate] = statistics.median(entries)
    return gains


def build_summary(root, index):
    root = Path(root)
    gains = current_loop_gains(index)
    dut_groups = {}
    baseline_groups = {}
    for run in index['runs']:
        if run['role'] == 'dut':
            dut_groups.setdefault((run['rate'], run['transformer'], run['channel']),
                                  []).append(run)
        elif run['role'] == 'baseline':
            baseline_groups.setdefault((run['rate'], run['channel']), []).append(run)
    metadata = segment_metadata(list(baseline_groups.values()) + list(dut_groups.values()))
    freq_ids = frequency_ids(metadata)
    check_frequencies = [value for value in (20, 1000, 4000, 16000, 20000)
                         if value in freq_ids]
    summary = dict(schema=1, created_utc=now_utc(), root=str(root),
                   settings_label=index.get('settings_label'),
                   loop_gain_db=gains, anchors_dbfs=list(ANCHORS_DBFS),
                   dut={}, baseline={}, stability={}, issues=[])
    lines = ['# Green Stripe 76 - Scarlett-Transformator-Matrix', '',
             f'- Messreihe: `{root}`',
             f'- Einstellungen: {index.get("settings_label") or "(siehe Label je Lauf)"}',
             '- Loop-Gewinn (Median): '
             + (', '.join(f'{rate} Hz: {gain:+.2f} dB'
                          for rate, gain in sorted(gains.items())) or 'nicht bestimmt'),
             '']
    for rate, gain in sorted(gains.items()):
        level, reachable, missing = choose_stimulus_level(gain)
        if missing:
            summary['issues'].append(
                f'Rate {rate}: Anker {", ".join(f"{a:g}" for a in missing)} dBFS nicht '
                f'erreichbar (Loop-Gewinn {gain:+.2f} dB); Dwarf-Input-Gain anheben.')
    # Baseline stability: within-channel repeat spread and cross-channel asymmetry.
    lines += ['## Stabilitaetsreferenz (Bypass-Baseline)', '',
              '| Rate | Vergleich | '
              + ' | '.join(f'{value} Hz' for value in check_frequencies) + ' |',
              '|---|---' + '|---:' * len(check_frequencies) + '|']
    columns = [freq_ids[value] for value in check_frequencies]

    def baseline_gain(run, segment_id):
        report = json.loads((Path(run['directory']) / 'results.json')
                            .read_text(encoding='utf-8'))
        row = {entry['id']: entry for entry in report['segments']}.get(segment_id)
        return row.get('gain_db') if row else None

    for rate in sorted({key[0] for key in baseline_groups}):
        for channel in (1, 2):
            runs = baseline_groups.get((rate, channel), [])
            if len(runs) < 2:
                continue
            spreads = {}
            for segment_id in columns:
                stat = stat_row([baseline_gain(run, segment_id) for run in runs])
                if stat:
                    spreads[segment_id] = stat['spread']
            summary['stability'][f'{rate}/ch{channel}-repeat'] = {
                str(freq_ids[value]): spreads[columns[index]]
                for index, value in enumerate(check_frequencies) if columns[index] in spreads}
            lines.append(f'| {rate} | Ch{channel} Wiederholungsspreizung | '
                         + ' | '.join(f'{spreads[segment_id]:.3f}'
                                      if segment_id in spreads else '-'
                                      for segment_id in columns) + ' |')
        first, second = baseline_groups.get((rate, 1)), baseline_groups.get((rate, 2))
        if first and second:
            asymmetry = {}
            for segment_id in columns:
                first_values = [baseline_gain(run, segment_id) for run in first]
                second_values = [baseline_gain(run, segment_id) for run in second]
                first_stat, second_stat = stat_row(first_values), stat_row(second_values)
                if first_stat and second_stat:
                    asymmetry[segment_id] = abs(first_stat['median'] - second_stat['median'])
            summary['stability'][f'{rate}/ch1-ch2'] = {
                str(freq_ids[value]): asymmetry[columns[index]]
                for index, value in enumerate(check_frequencies) if columns[index] in asymmetry}
            lines.append(f'| {rate} | Ch1-Ch2 Asymmetrie | '
                         + ' | '.join(f'{asymmetry[segment_id]:.3f}'
                                      if segment_id in asymmetry else '-'
                                      for segment_id in columns) + ' |')
    # DUT tables.
    sweep = [metadata[segment_id] for segment_id in sorted(metadata)
             if metadata[segment_id].get('group') == 'sweep']
    lines += ['', '## Frequenzgang relativ zur Bypass-Baseline', '',
              'Median ueber die Wiederholungen; Klammer = Spreizung (max-min). '
              '20 kHz bei 48 kHz ist nicht trennscharf (siehe MESSTECHNIK).', '',
              '| Transformer | Ch | Rate | '
              + ' | '.join(f'{row["frequency_hz"]:g}' for row in sweep) + ' |',
              '|---|---:|---:' + '|---:' * len(sweep) + '|']
    order = sorted(dut_groups, key=lambda key: (key[0], slug(key[1]), key[2]))
    for rate, transformer, channel in order:
        buckets = aggregate_dut(dut_groups[(rate, transformer, channel)])
        summary['dut'].setdefault(str(rate), {}).setdefault(transformer, {})[
            str(channel)] = {
            str(bucket['id']): dict(
                frequency_hz=bucket['frequency_hz'], group=bucket['group'],
                peak_dbfs=bucket['peak_dbfs'],
                relative_gain_db=stat_row(bucket['relative']),
                thd_percent=stat_row(bucket['thd']),
                thdn_percent=stat_row(bucket['thdn']),
                valid_count=sum(bucket['valid']), runs=len(bucket['valid']))
            for bucket in buckets.values()}
        cells = []
        for row in sweep:
            bucket = buckets.get(row['id'])
            stat = stat_row(bucket['relative']) if bucket else None
            cells.append(f'{stat["median"]:+.2f} ({stat["spread"]:.2f})' if stat else '-')
        lines.append(f'| {transformer} | {channel} | {rate} | ' + ' | '.join(cells) + ' |')
    # Anchor table (levels segments). With an exact level choice each anchor
    # lands on one series step; --relax-anchors runs report the achieved level
    # of the nearest step and its deviation from the requested anchor.
    lines += ['', '## Pegelanker am Plugin-Eingang (1-kHz-Pegelreihe)', '',
              'Anker = Pegel am Plugin-Eingang im Bypass; Stimulus = Anker minus '
              'Loop-Gewinn. "erreicht" = realer Pegel des naechsten Segments.', '',
              '| Transformer | Ch | Rate | Anker dBFS | Stimulus dBFS | erreicht dBFS | '
              'rel. dB Median (Spreizung) | THD % | THD+N % |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    anchor_rows = {}
    for rate, transformer, channel in order:
        gain = gains.get(rate)
        if gain is None:
            continue
        buckets = aggregate_dut(dut_groups[(rate, transformer, channel)])
        for anchor in ANCHORS_DBFS:
            stimulus = anchor - gain
            bucket = min((bucket for bucket in buckets.values()
                          if bucket['group'] == 'levels'),
                         key=lambda bucket: abs(bucket['peak_dbfs'] - stimulus),
                         default=None)
            if bucket is None or abs(bucket['peak_dbfs'] - stimulus) > 3.0:
                continue
            deviation = bucket['peak_dbfs'] + gain - anchor
            if abs(deviation) > 0.01:
                summary['issues'].append(
                    f'{rate}/{transformer}/ch{channel}: Anker {anchor:g} dBFS erreicht '
                    f'nur {bucket["peak_dbfs"] + gain:+.2f} dBFS (Abweichung '
                    f'{deviation:+.2f} dB)')
            relative = stat_row(bucket['relative'])
            thd = stat_row(bucket['thd'])
            thdn = stat_row(bucket['thdn'])
            anchor_rows.setdefault(f'{rate}/{transformer}/ch{channel}', []).append(anchor)
            lines.append(
                f'| {transformer} | {channel} | {rate} | {anchor:g} | {stimulus:g} | '
                f'{bucket["peak_dbfs"] + gain:+.2f} | '
                + (f'{relative["median"]:+.3f} ({relative["spread"]:.3f})'
                   if relative else '-')
                + ' | ' + (f'{thd["median"]:.3f}' if thd else '-')
                + ' | ' + (f'{thdn["median"]:.3f}' if thdn else '-') + ' |')
    summary['anchors_found'] = anchor_rows
    for rate, transformer, channel in order:
        key = f'{rate}/{transformer}/ch{channel}'
        if key not in anchor_rows:
            summary['issues'].append(f'{key}: keine Pegelanker-Segmente gefunden')
    # Consistency: loop gains recorded per run must not drift within a rate,
    # otherwise the anchor mapping (stimulus = anchor - gain) breaks.
    for rate in sorted({run['rate'] for run in index['runs']
                        if run['role'] in ('baseline', 'dut')}):
        values = [run['loop_gain_db'] for run in index['runs']
                  if run['rate'] == rate and run['role'] in ('baseline', 'dut')
                  and run.get('loop_gain_db') is not None]
        if values and max(values) - min(values) > 1.0:
            summary['issues'].append(
                f'Rate {rate}: Loop-Gewinn driftet um {max(values) - min(values):.2f} dB '
                'zwischen den Laeufen; Regler zwischen Baseline und DUT nicht '
                'veraendern.')
    for run in index['runs']:
        if run['role'] == 'gainmatch':
            continue
        if not run.get('valid'):
            summary['issues'].append(f'{run["directory"]}: Lauf ungueltig')
        elif run.get('level_check') and run['level_check'].get('adequate') is False:
            summary['issues'].append(f'{run["directory"]}: Loop-Gewinn unter -20 dB')
        if run.get('rate_mismatch'):
            summary['issues'].append(f'{run["directory"]}: Geraeteraten-Mismatch')
    if summary['issues']:
        lines += ['', '## Hinweise', '']
        lines += [f'- {issue}' for issue in summary['issues']]
    lines += ['', 'Keine interne FET-GR-, Hardwaregleichheits- oder Hoerabnahme. '
              'Relative Werte gelten gegen die Bypass-Baseline desselben Kanals.', '']
    with (root / 'SUMMARY.md').open('w', encoding='utf-8', newline='') as stream:
        stream.write('\n'.join(lines))
    with (root / 'summary.json').open('w', encoding='utf-8', newline='') as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    return summary


def add_common(parser):
    parser.add_argument('--input-device', type=int)
    parser.add_argument('--output-device', type=int)
    parser.add_argument('--hostapi', default='MME')
    parser.add_argument('--dwarf-source', action='store_true',
                        help='The MOD Dwarf plays the pre-generated 24-bit WAV test '
                             'tones itself (digital plugin input); the script only '
                             'records. Use --level -2 so the levels series hits the '
                             'anchors exactly; see tools/make_dwarf_tones.py')
    parser.add_argument('--pad', type=float, default=10,
                        help='Recording padding in --dwarf-source mode to cover the '
                             'manual playback start')
    parser.add_argument('--rates', nargs='+', type=int, default=[48000],
                        help='Sample rates to measure, e.g. --rates 48000 96000')
    parser.add_argument('--level', type=float, default=-12,
                        help='Probe stimulus peak in dBFS; the matrix level is '
                             'derived from the measured loop gain')
    parser.add_argument('--frequency', type=float, default=1000)
    parser.add_argument('--settle', type=float, default=2)
    parser.add_argument('--measure', type=float, default=1)
    parser.add_argument('--settings-label', default='',
                        help='Dwarf settings documentation appended to every run label')
    parser.add_argument('--relax-anchors', action='store_true',
                        help='Measure even when the loop gain cannot place the anchor '
                             'levels on series steps; the summary reports the achieved '
                             'levels instead of aborting')
    parser.add_argument('--transformers', default=','.join(DEFAULT_TRANSFORMERS))
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--baseline-repeats', type=int, default=2)
    parser.add_argument('--tolerance', type=float, default=1.0)
    parser.add_argument('--skip-gainmatch', action='store_true')
    parser.add_argument('--yes', action='store_true',
                        help='Run without interactive prompts (for scripted use)')
    parser.add_argument('--root', help='Measurement root; default test-results/matrix-<timestamp>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('devices', help='List audio devices and host APIs')
    common = argparse.ArgumentParser(add_help=False)
    add_common(common)
    commands.add_parser('gainmatch', parents=[common],
                        help='Measure loop gain on both channels')
    commands.add_parser('baseline', parents=[common],
                        help='Bypass baselines for both channels')
    commands.add_parser('matrix', parents=[common],
                        help='Transformer matrix (requires baselines)')
    commands.add_parser('full', parents=[common],
                        help='Gain match, baselines and matrix in one run')
    commands.add_parser('summary', parents=[common],
                        help='Aggregate an existing measurement root')
    args = parser.parse_args(argv)
    try:
        if args.command == 'devices':
            sd = measurement.sounddevice()
            print(sd.query_devices())
            print(json.dumps(sd.query_hostapis(), indent=2))
            return 0
        if args.command == 'summary' and not args.root:
            raise ValueError('summary requires --root <measurement root>')
        driver = Driver(args)
        if args.command == 'gainmatch':
            driver.gainmatch()
        elif args.command == 'baseline':
            driver.baseline()
        elif args.command == 'matrix':
            driver.matrix()
            build_summary(driver.root, driver.index)
            print(f'Auswertung: {(driver.root / "SUMMARY.md").resolve()}')
        elif args.command == 'full':
            driver.full()
        else:
            build_summary(Path(args.root), load_index(args.root))
            print(f'Auswertung: {(Path(args.root) / "SUMMARY.md").resolve()}')
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f'Measurement failed: {error}\n')


if __name__ == '__main__':
    sys.exit(main())
