#!/usr/bin/env python3
"""Measure Green Stripe 76 pedalboard load on a MOD Dwarf.

The plugin host runs as threads inside jackd, so the DSP load is visible as
process and per-thread CPU time, not as a separate process. Everything here is
read from /proc plus optional log sources; nothing is written to the device.

Per condition: one measurement window, jackd process and thread CPU sampled
periodically, plugin binary identity and instance count verified from
/proc/<pid>/maps, and xrun indications counted before and after the window.
See docs/MESSTECHNIK.md for the run order and its limits.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import statistics
import subprocess
import sys
import time

SCHEMA = 1
PLUGIN_NAME = 'green-stripe-76.so'
XRUN_PATTERN = re.compile(r'xrun', re.IGNORECASE)


def read_text(path):
    # The Dwarf runs Python 3.4 without Path.read_text, so go through io.open.
    with io.open(str(path), 'r', encoding='utf-8', errors='replace') as handle:
        return handle.read()


def read_bytes(path):
    with io.open(str(path), 'rb') as handle:
        return handle.read()


def write_text(path, text):
    with io.open(str(path), 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(text)


def write_bytes(path, data):
    with io.open(str(path), 'wb') as handle:
        handle.write(data)


def utc_stamp():
    # datetime.isoformat(timespec=...) only exists from Python 3.6 on.
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256_of(path):
    digest = hashlib.sha256()
    with io.open(str(path), 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def proc_root(value):
    return Path(value)


def find_jackd(root, explicit=None):
    """Return the pid of the audio server. Falls back to a /proc scan."""
    if explicit:
        return int(explicit)
    comm = root / 'comm'
    candidates = []
    for entry in sorted(root.iterdir()):
        if not entry.name.isdigit():
            continue
        try:
            name = read_text(entry / 'comm').strip()
        except OSError:
            continue
        if name in ('jackd', 'jackdmp', 'jackdbus'):
            candidates.append(int(entry.name))
    if not candidates:
        raise SystemExit('No jackd process found under %s' % root)
    return candidates[0]


def read_cmdline(root, pid):
    raw = read_bytes(root / str(pid) / 'cmdline')
    parts = [p.decode('utf-8', 'replace') for p in raw.split(b'\0') if p]
    return ' '.join(parts)


def cpu_ticks(root, pid):
    """utime+stime in clock ticks for the whole process and per thread."""
    def parse(path):
        text = read_text(path)
        head, _, tail = text.rpartition(')')
        fields = tail.split()
        # After the comm field: state is index 0, so utime/stime are 11 and 12.
        return int(fields[11]) + int(fields[12])
    base = root / str(pid)
    threads = {}
    for entry in sorted((base / 'task').iterdir()):
        if not entry.name.isdigit():
            continue
        try:
            ticks = parse(entry / 'stat')
            name = read_text(entry / 'comm').strip()
        except (OSError, IndexError, ValueError):
            continue
        threads[entry.name] = (ticks, name)
    return parse(base / 'stat'), threads


def plugin_maps(root, pid, name=PLUGIN_NAME):
    """Mapped plugin segments, binary identity and r-xp instance count."""
    found = []
    text = read_text(root / str(pid) / 'maps')
    for line in text.splitlines():
        if name not in line:
            continue
        fields = line.split()
        if len(fields) < 6:
            continue
        found.append({'start': fields[0], 'perms': fields[1], 'offset': fields[2],
                      'path': fields[5], 'inode': fields[4]})
    binaries = sorted({entry['path'] for entry in found})
    identity = {}
    for binary in binaries:
        path = Path(binary)
        try:
            size = path.stat().st_size
            digest = sha256_of(path)
        except OSError as error:
            # An unreadable binary is a finding, not a reason to lose the run.
            identity[binary] = {'readable': False, 'error': str(error)}
            continue
        identity[binary] = {'readable': True, 'bytes': size, 'sha256': digest}
    executable = [entry for entry in found if 'x' in entry['perms']]
    return {'segments': found, 'binaries': binaries, 'identity': identity,
            'text_segments': len(executable)}


def run_command(command):
    try:
        # Popen instead of subprocess.run: run() only exists from Python 3.5 on.
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, err = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        return {'command': ' '.join(command), 'available': False, 'error': str(error)}
    text = out.decode('utf-8', 'replace')
    return {'command': ' '.join(command), 'available': process.returncode == 0,
            'returncode': process.returncode,
            'xrun_lines': len(XRUN_PATTERN.findall(text)),
            'stderr': err.decode('utf-8', 'replace').strip()[:200]}


def xrun_sources(commands):
    if not commands:
        commands = [['dmesg']]
        if Path('/usr/bin/journalctl').exists() or Path('/bin/journalctl').exists():
            commands.append(['journalctl', '-k', '--no-pager'])
    return [run_command(shlex.split(command) if isinstance(command, str) else command)
            for command in commands]


def environment(root):
    info = {'root': str(root)}
    for key, path in (('uname', 'sys/kernel/osrelease'),
                      ('os_release', 'etc/os-release'),
                      ('cpu_model', 'proc/cpuinfo')):
        try:
            text = read_text(root / path)
        except OSError:
            continue
        if key == 'cpu_model':
            parts = [line for line in text.splitlines()
                     if line.startswith(('model name', 'CPU part', 'processor'))]
            info[key] = parts[:8]
        elif key == 'os_release':
            info[key] = [line for line in text.splitlines()
                         if line.startswith('PRETTY_NAME') or line.startswith('VERSION')]
        else:
            info[key] = text.strip()
    return info


def measure(args, root, pid, clk_tck):
    ticks_per_second = args.clk_tck if args.clk_tck else os.sysconf('SC_CLK_TCK')
    maps_before = plugin_maps(root, pid, args.plugin_name)
    xrun_before = xrun_sources(args.xrun_command)
    process0, threads0 = cpu_ticks(root, pid)
    window = max(1, int(round(args.seconds)))
    interval = max(0.01, args.interval)
    samples = max(1, int(round(window / interval)))
    series = []
    thread_series = {}
    for _ in range(samples):
        time.sleep(interval)
        process1, threads1 = cpu_ticks(root, pid)
        series.append(process1 - process0)
        for tid, (ticks, _) in threads1.items():
            previous = threads0.get(tid)
            if previous is None:
                continue
            thread_series.setdefault(tid, [previous[0], previous[1], 0.0])
            thread_series[tid][2] += ticks - previous[0]
        process0, threads0 = process1, threads1
    measured_window = samples * interval
    total_ticks = sum(series)
    process_percent = 100.0 * total_ticks / (ticks_per_second * measured_window)
    threads = [{'tid': tid, 'name': name, 'percent_of_one_core':
                100.0 * ticks / (ticks_per_second * measured_window)}
               for tid, (_, name, ticks) in thread_series.items()]
    threads.sort(key=lambda row: -row['percent_of_one_core'])
    xrun_after = xrun_sources(args.xrun_command)
    xrun_delta = []
    for before, after in zip(xrun_before, xrun_after):
        if before.get('available') and after.get('available'):
            xrun_delta.append({'command': before['command'],
                               'before': before['xrun_lines'],
                               'after': after['xrun_lines'],
                               'during_window': after['xrun_lines'] - before['xrun_lines']})
        else:
            xrun_delta.append({'command': before.get('command', '?'), 'available': False,
                               'error': after.get('error') or before.get('error')})
    return {
        'label': args.label,
        'note': args.note,
        'frames': args.frames,
        'expected_instances': args.expect_instances,
        'measured_text_segments': maps_before['text_segments'],
        'plugin_binaries': maps_before['binaries'],
        'plugin_identity': maps_before['identity'],
        'instances_match_expectation': (None if args.expect_instances is None
                                        else maps_before['text_segments'] == args.expect_instances),
        'md5_or_sha_match': verify_identity(maps_before, args.expect_sha256),
        'measured_at': utc_stamp(),
        'clk_tck': ticks_per_second,
        'window_seconds': round(measured_window, 3),
        'samples': samples,
        'interval_seconds': interval,
        'process_percent_mean': process_percent,
        'process_percent_median': statistics.median(series) * 100.0 / ticks_per_second / interval,
        'process_percent_peak': max(series) * 100.0 / ticks_per_second / interval,
        'process_ticks_total': total_ticks,
        'threads': threads,
        'xrun_sources': xrun_delta,
    }


def verify_identity(maps, expected):
    if not expected:
        return None
    wanted = expected.strip().lower()
    return any(entry.get('sha256') == wanted for entry in maps['identity'].values())


def summarise(report):
    rows = report['conditions']
    lines = ['# Green Stripe 76 — Dwarf-Lasttest (Messprotokoll)', '',
             'Prozent eines Kerns, jackd inklusive. Ohne diese Tabelle ist eine',
             'Aussage über Echtzeitfähigkeit nicht belegt.', '',
             '| Board | Frames | Instanzen (gemessen/erwartet) | Prozess Mittel |'
             ' Prozess Median | Prozess Spitze | schwerster Thread | xruns |',
             '|---|---:|---:|---:|---:|---:|---|---:|']
    baseline = None
    for row in rows:
        thread = row['threads'][0]['percent_of_one_core'] if row['threads'] else float('nan')
        name = row['threads'][0]['name'] if row['threads'] else '-'
        xruns = sum(source.get('during_window', 0) or 0 for source in row['xrun_sources'])
        match = row['measured_text_segments']
        if row['expected_instances'] is not None:
            match = '%d/%d' % (match, row['expected_instances'])
        lines.append('| %s | %s | %s | %.2f %% | %.2f %% | %.2f %% | %.2f %% (%s) | %d |'
                     % (row['label'], row['frames'], match,
                        row['process_percent_mean'], row['process_percent_median'],
                        row['process_percent_peak'], thread, name, xruns))
    lines.append('')
    first = rows[0]
    baseline = first['process_percent_mean']
    lines.append('## Differenz zur ersten Bedingung')
    lines.append('')
    lines.append('| Board | Frames | Delta Prozess Mittel | je Instanz |')
    lines.append('|---|---:|---:|---:|')
    for row in rows:
        delta = row['process_percent_mean'] - baseline
        per = delta / row['measured_text_segments'] if row['measured_text_segments'] else float('nan')
        lines.append('| %s | %s | %+.2f %% | %s |'
                     % (row['label'], row['frames'], delta,
                        ('%+.2f %%' % per) if row['measured_text_segments'] else '-'))
    lines.append('')
    lines.append('## Grenzen')
    lines.append('')
    lines.append('- Nur jackd-Threadlast. Kein Echtzeit-, Latenz- oder Hörtest.')
    lines.append('- Die Plugin-Host-API antwortet auf dem Dwarf nicht; xruns stammen')
    lines.append('  nur aus Kernel-/Journaltexten und sind nur so gut wie deren Zugang.')
    lines.append('- Pro Bedingung ist ein vollständiger Gerätestart nötig, weil nur er')
    lines.append('  das Pedalboard aus last.json übernimmt.')
    lines.append('- Ergebnisse gelten nur für die gemessene Binary (SHA256 oben).')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--label', default='', help='condition name, e.g. GS76x2')
    parser.add_argument('--note', default='', help='free text, e.g. board settings')
    parser.add_argument('--frames', type=int, default=0, help='host block size, for the record')
    parser.add_argument('--seconds', type=float, default=20.0, help='measurement window')
    parser.add_argument('--interval', type=float, default=0.5, help='sampling interval')
    parser.add_argument('--expect-instances', type=int, default=None,
                        help='fail unless this many plugin text segments are mapped')
    parser.add_argument('--expect-sha256', default='', help='expected plugin binary SHA256')
    parser.add_argument('--jackd-pid', type=int, default=None)
    parser.add_argument('--clk-tck', type=int, default=0, help='override SC_CLK_TCK')
    parser.add_argument('--output-json', type=str, default=None)
    parser.add_argument('--output-markdown', type=str, default=None)
    parser.add_argument('--plugin-name', default=PLUGIN_NAME)
    parser.add_argument('--proc-root', default='/proc',
                        help='procfs root; only for offline tests')
    parser.add_argument('--xrun-command', action='append', default=[],
                        help='repeatable log command line for xrun lines, e.g. "journalctl -k -n 500"')
    parser.add_argument('--report', type=Path, help='JSON report; existing conditions are kept')
    parser.add_argument('--markdown', type=Path, help='Markdown table')
    parser.add_argument('--self-test', action='store_true', help='run offline unit checks')
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.label:
        raise SystemExit('--label is required, e.g. --label GS76x2')
    if args.seconds <= 0 or args.interval <= 0:
        raise SystemExit('--seconds and --interval must be positive')
    root = proc_root(args.proc_root)
    pid = find_jackd(root, args.jackd_pid)
    condition = measure(args, root, pid, args.clk_tck)
    condition['jackd_pid'] = pid
    condition['jackd_cmdline'] = read_cmdline(root, pid)
    condition['environment'] = environment(root)

    report = {'schema': SCHEMA, 'unit': 'percent of one CPU core, jackd process included',
              'conditions': []}
    if args.report and args.report.exists():
        existing = json.loads(read_text(args.report))
        if existing.get('schema') != SCHEMA:
            raise SystemExit('Report schema mismatch: use a new file')
        report['conditions'] = existing.get('conditions', [])
    report['conditions'].append(condition)
    write_json(args.report, report) if args.report else print(json.dumps(condition, indent=2))
    if args.markdown:
        write_text(args.markdown, summarise(report))

    print('%s: %.2f %% process, %d mapped plugin instances, threads: %s'
          % (args.label, condition['process_percent_mean'],
             condition['measured_text_segments'],
             ', '.join('%s %.2f %%' % (row['name'], row['percent_of_one_core'])
                       for row in condition['threads'][:4])))
    for source in condition['xrun_sources']:
        print('  xrun source %s: %s' % (source['command'],
                                         source.get('during_window', source.get('error'))))
    if args.expect_instances is not None and not condition['instances_match_expectation']:
        print('WARNING: expected %d mapped instances, found %d'
              % (args.expect_instances, condition['measured_text_segments']))
    if args.expect_sha256 and not condition['md5_or_sha_match']:
        print('WARNING: plugin binary SHA256 does not match --expect-sha256')
    return 0


def write_json(path, value):
    with io.open(str(path), 'w', encoding='utf-8', newline='') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def self_test():
    """Offline check of the /proc parsing and the statistic, no device needed."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / '42' / 'task' / '42').mkdir(parents=True)
        (root / '42' / 'task' / '43').mkdir(parents=True)
        write_text(root / '42' / 'comm', 'jackd\n')
        (root / '43').mkdir()
        write_text(root / '43' / 'comm', 'bash\n')
        write_bytes(root / '42' / 'cmdline', b'jackd\x00-r\x00/dev/DWARF\x00')
        # comm contains a space and parentheses on purpose: naive splitting breaks.
        write_text(root / '42' / 'task' / '42' / 'comm', 'jackd\n')
        write_text(root / '42' / 'task' / '43' / 'comm', 'jack rt (x)\n')
        write_text(root / '42' / 'task' / '42' / 'stat',
                   '42 (jackd) S 1 42 42 0 -1 4194560 100 0 0 0 500 300 0 0 20 0 3 0 100\n')
        write_text(root / '42' / 'task' / '43' / 'stat',
                   '43 (jack rt (x)) R 1 42 42 0 -1 0 0 0 0 0 700 400 0 0 20 0 7 0 200\n')
        write_text(root / '42' / 'stat',
                   '42 (jackd) S 1 42 42 0 -1 0 0 0 0 0 1200 700 0 0 20 0 3 0 100\n')
        binary = root / 'lv2' / PLUGIN_NAME
        binary.parent.mkdir(parents=True)
        write_bytes(binary, b'not-a-real-plugin')
        maps = root / '42' / 'maps'
        write_text(maps,
                   '7f0000-7f1000 r-xp 00000000 08:01 12345   %s\n'
                   '7f1000-7f2000 r--p 00001000 08:01 12345   %s\n'
                   '7f2000-7f3000 rw-p 00002000 08:01 12345   %s\n'
                   % (binary, binary, binary))

        assert find_jackd(root) == 42
        process, threads = cpu_ticks(root, 42)
        assert process == 1900, process
        assert threads['42'][0] == 800 and threads['43'][0] == 1100, threads
        assert threads['43'][1] == 'jack rt (x)', threads['43']
        found = plugin_maps(root, 42)
        assert found['text_segments'] == 1, found
        assert verify_identity(found, sha256_of(binary))
        assert verify_identity(found, 'deadbeef') is False
        assert read_cmdline(root, 42) == 'jackd -r /dev/DWARF'
        assert XRUN_PATTERN.search('ALSA: xrun: at least one XRUN')
        assert not XRUN_PATTERN.search('ALSA: snd_pcm_start ok')
        series = [10, 20, 30, 40]
        assert statistics.median(series) == 25
    print('dwarf_loadtest self-test: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())