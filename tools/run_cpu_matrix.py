#!/usr/bin/env python3
"""Fuehrt die CPU-Matrix auf dem Dwarf aus (SSH mit askpass, root/mod).

Ablauf je Zustand: last.json schreiben -> Neustart -> auf Board-Mapping
warten -> dwarf_loadtest.py laufen lassen -> Metrik einsammeln. Fortsetzbar
(Fortschritt in /tmp/opencode/cpu/progress.json).

Aufruf (chunks):
  python3 tools/run_cpu_matrix.py --push        # einmalig: Boards hochladen
  python3 tools/run_cpu_matrix.py --max-states 3
  ... (wiederholen, bis alle 36 Zustaende fertig sind)
  python3 tools/run_cpu_matrix.py --finish      # last.json restaurieren + Neustart
"""
import argparse
import json
import os
import subprocess
import sys
import time

HOST = 'root@192.168.51.1'
PROGRESS = '/tmp/opencode/cpu/progress.json'
REMOTE_DIR = '/root/cpu_matrix'
ORIGINAL_LAST = '/root/.pedalboards/GS76x0.pedalboard'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cpu_board_builder import STATES  # noqa: E402


def ssh_env():
    env = dict(os.environ)
    env['DISPLAY'] = env.get('DISPLAY', ':0')
    env['SSH_ASKPASS'] = '/tmp/opencode/ssh/askpass.sh'
    env['SSH_ASKPASS_REQUIRE'] = 'force'
    return env


def ssh(command, timeout=120, check=True):
    proc = subprocess.run(['ssh', '-o', 'StrictHostKeyChecking=no',
                           '-o', 'ConnectTimeout=8', HOST, command],
                          capture_output=True, text=True, timeout=timeout,
                          env=ssh_env())
    if check and proc.returncode != 0:
        raise RuntimeError('SSH fehlgeschlagen ({0}): {1}'.format(
            proc.returncode, proc.stderr.strip()[:300]))
    return proc.stdout


def load_progress():
    if os.path.exists(PROGRESS):
        with open(PROGRESS, encoding='utf-8') as handle:
            return json.load(handle)
    return {'done': {}}


def save_progress(progress):
    with open(PROGRESS, 'w', encoding='utf-8') as handle:
        json.dump(progress, handle, indent=1)


def wait_device(max_seconds=240):
    deadline = time.time() + max_seconds
    while time.time() < deadline:
        try:
            out = ssh('echo up', timeout=15, check=False)
            if 'up' in out:
                return True
        except Exception:
            pass
        time.sleep(5)
    return False


def wait_mapping(max_seconds=90):
    deadline = time.time() + max_seconds
    probe = ("for m in /proc/[0-9]*/maps; do grep -q 'green-stripe-76.so' $m && echo $m; done | wc -l")
    while time.time() < deadline:
        try:
            count = ssh(probe, timeout=20, check=False).strip()
            if count and int(count) >= 1:
                return int(count)
        except Exception:
            pass
        time.sleep(4)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--push', action='store_true', help='Boards auf das Geraet laden')
    parser.add_argument('--max-states', type=int, default=3)
    parser.add_argument('--seconds', type=float, default=20.0)
    parser.add_argument('--finish', action='store_true', help='last.json restaurieren + Neustart')
    args = parser.parse_args()

    if args.push:
        subprocess.run(['tar', '-C', '/tmp/opencode/cpu/staging', '-czf',
                        '/tmp/opencode/cpu/boards.tgz', '--exclude=states.json', '.'],
                       check=True)
        subprocess.run(['scp', '-o', 'StrictHostKeyChecking=no',
                        '/tmp/opencode/cpu/boards.tgz', HOST + ':/root/boards.tgz'],
                       check=True, env=ssh_env(), capture_output=True)
        out = ssh('tar -xzf /root/boards.tgz -C /root/.pedalboards/ && '
                  'rm /root/boards.tgz && mkdir -p ' + REMOTE_DIR + ' && '
                  'ls -d /root/.pedalboards/cpux-* | wc -l')
        print('Boards auf dem Geraet:', out.strip())

    if args.finish:
        ssh('printf \'{"supportsDividers": true, "bank": -1, "pedalboard": "%s"}\' '
            '\'/root/.pedalboards/GS76x0.pedalboard\' > /root/data/last.json', check=False)
        ssh('cat /root/data/last.json; sync; reboot', check=False)
        print('last.json restauriert (GS76x0), Geraet startet neu.')
        return

    progress = load_progress()
    remaining = [(l, c, t) for l, c, t in STATES if l not in progress['done']]
    if not remaining:
        print('Alle {0} Zustaende fertig.'.format(len(STATES)))
        return

    todo = remaining[:args.max_states]
    for label, colour, transformer in todo:
        print('== {0} (Colour {1}, Transformer {2})'.format(label, colour, transformer))
        board = '/root/.pedalboards/cpux-{0}.pedalboard'.format(label)
        write = ('printf \'{"supportsDividers": true, "bank": -1, "pedalboard": "%s"}\' '
                 "'" + board + "' > /root/data/last.json && sync && cat /root/data/last.json")
        ssh(write)
        ssh('reboot', check=False)
        time.sleep(10)
        if not wait_device():
            raise SystemExit('Geraet kommt nach dem Neustart nicht zurueck.')
        instances = wait_mapping()
        if instances < 1:
            raise SystemExit('Board {0}: Plugin-Mapping fehlt nach dem Boot.'.format(label))
        print('   Mapping vorhanden ({0}), Settle...'.format(instances))
        time.sleep(5)
        note = 'colour={0} transformer={1} OS2x compOff'.format(colour, transformer)
        cmd = ('python3 /root/lt/dwarf_loadtest.py --label {0} --frames 128 '
               '--seconds {1} --expect-instances 1 '
               '--report {2}/load.json --markdown {2}/load.md '
               "--note '{3}'".format(label, args.seconds, REMOTE_DIR, note))
        out = ssh(cmd, timeout=180)
        tail = [line for line in out.strip().splitlines() if line.strip()][-3:]
        print('   ' + ' | '.join(tail))
        # Metrik aus load.json ziehen
        raw = ssh('cat {0}/load.json'.format(REMOTE_DIR), timeout=30)
        report = json.loads(raw)
        entry = None
        for condition in report['conditions']:
            if condition.get('label') == label:
                entry = condition
        if entry is None:
            raise SystemExit('Kein Messergebnis fuer {0} in load.json.'.format(label))
        progress['done'][label] = {
            'colour': colour, 'transformer': transformer,
            'median': entry.get('process_percent_median'),
            'peak': entry.get('process_percent_peak'),
            'mean': entry.get('process_percent_mean'),
            'frames': entry.get('frames'),
            'sha256': (list(entry.get('plugin_identity', {}).values())[0].get('sha256')
                       if entry.get('plugin_identity') else None),
            'xruns': sum(s.get('during_window', 0)
                         for s in entry.get('xrun_sources', []) or [])}
        save_progress(progress)
        print('   median {0:.1f}% peak {1:.1f}%'.format(
            progress['done'][label]['median'], progress['done'][label]['peak']))
    print('{0}/{1} Zustaende fertig; naechsten Chunk starten.'.format(
        len(progress['done']), len(STATES)))


if __name__ == '__main__':
    main()
