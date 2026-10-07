#!/usr/bin/env python3
# CPU-Matrix auf dem MOD Dwarf: alle Colour x Transformator-Kombinationen.
# Läuft AUF dem Gerät (Python 3.4, Buildroot). Parameter werden live über den
# mod-host-Socket gesetzt und je Zustand per Rücklesung verifiziert; gemessen
# wird mit tools/dwarf_loadtest.py (Serie-A-Werkzeug, /proc-Ticks).
#
# Vorbereitung (Web-UI):
#   1. Board mit Green Stripe 76 Stereo laden (File-Player -> GS76 -> Ausgang),
#      Recorder/sonstige FX entfernen.
#   2. Matrix-Datei abspielen, LOOP MODE ON (Signal waehrend der ganzen Serie).
#   3. Input-Gate/Output-Kompressor des Dwarf deaktivieren.
# Ablauf:
#   python3 /root/lt/dwarf_cpu_matrix.py
# Danach: Dwarf neu starten (Empfehlung), dann optional:
#   python3 /root/lt/dwarf_cpu_matrix.py --only bypass,c0-60s,col100-60s
# Ergebnisse: /root/cpu_matrix/ (load.json je Zustand + cpu_results.json + .md)
import argparse
import json
import os
import socket
import subprocess
import sys
import time

TRY_SOCKETS = [('tcp', '127.0.0.1', 5555), ('tcp', '127.0.0.1', 5556),
               ('unix', '/tmp/mod-host.socket', 0)]
COLOURS = [0, 5, 10, 20, 50, 75, 100]
TYPES = [(0, 'None'), (1, '60s'), (2, '80s'), (3, '00s'), (4, 'Sym')]


def io_open(*args, **kwargs):
    import io
    return io.open(*args, **kwargs)


def load_json(path):
    with io_open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def save_json(path, data):
    text = json.dumps(data, indent=1, sort_keys=True)
    with io_open(path, 'w', encoding='utf-8') as handle:
        handle.write(text)
        handle.write('\n')


class ModHost(object):
    def __init__(self, spec):
        if spec[0] == 'tcp':
            self.sock = socket.create_connection((spec[1], spec[2]), timeout=3)
        else:
            self.sock = socket.socket(socket.AF_UNIX)
            self.sock.settimeout(3)
            self.sock.connect(spec[1])
        self.file = self.sock.makefile('rw', 1)

    def command(self, line):
        self.file.write(line + '\n')
        self.file.flush()
        response = self.file.readline().strip()
        if not response:
            raise ValueError('mod-host: leere Antwort auf "' + line + '"')
        return response

    def set(self, effect, param, value):
        response = self.command('set {0} {1} {2:.6f}'.format(effect, param, value))
        if response.lower().startswith('error'):
            raise ValueError('set {0} {1}: {2}'.format(effect, param, response))

    def get(self, effect, param):
        response = self.command('get {0} {1}'.format(effect, param))
        if response.lower().startswith('error'):
            raise ValueError('get {0} {1}: {2}'.format(effect, param, response))
        return float(response.split()[-1])


def find_effect(mh):
    for effect in range(0, 8):
        try:
            mh.get(effect, 'transformer')
            mh.get(effect, 'colour')
            return effect
        except ValueError:
            continue
    raise ValueError('Keine GS76-Instanz gefunden (get transformer/colour schlug '
                     'fuer ids 0..7 fehl). Laeuft das Board mit Green Stripe 76?')


def build_states():
    states = [('bypass', 0, 0)]
    for tf, name in TYPES:
        states.append(('c{0}-tf{1}'.format(0, name), 0, tf))
    for c in COLOURS[1:]:
        states.append(('c{0}-tf{1}'.format(c, 'None'), c, 0))
    for c in COLOURS[1:]:
        for tf, name in TYPES[1:]:
            states.append(('c{0}-tf{1}'.format(c, name), c, tf))
    return states


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--loadtest', default='/root/lt/dwarf_loadtest.py')
    parser.add_argument('--output', default='/root/cpu_matrix')
    parser.add_argument('--seconds', type=float, default=15.0)
    parser.add_argument('--frames', type=int, default=128)
    parser.add_argument('--socket', default='auto', help='tcp:HOST:PORT | unix:PFAD | auto')
    parser.add_argument('--only', default='', help='Kommaliste von Labels fuer Teilserie')
    parser.add_argument('--settle', type=float, default=2.5)
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    spec = None
    if args.socket != 'auto':
        parts = args.socket.split(':', 1)
        spec = ('unix', parts[1], 0) if parts[0] == 'unix' else ('tcp', parts[1], int(parts[2]))
    else:
        for candidate in TRY_SOCKETS:
            try:
                probe = ModHost(candidate)
                spec = candidate
                break
            except Exception as error:
                sys.stderr.write('Socket {0}: {1}\n'.format(candidate, error))
        if spec is None:
            raise SystemExit('Kein mod-host-Socket gefunden. ps | grep mod-host '
                             'pruefen und --socket angeben.')
    mh = ModHost(spec)
    print('mod-host-Socket: {0}'.format(spec))

    effect = find_effect(mh)
    print('GS76-Instanz: effect id {0}'.format(effect))

    original = dict( colour=mh.get(effect, 'colour'),
                     transformer=mh.get(effect, 'transformer'),
                     oversampling=mh.get(effect, 'oversampling'),
                     compression=mh.get(effect, 'compression'),
                     enabled=mh.get(effect, 'enabled'))
    print('Originalzustand: {0}'.format(original))

    binary = subprocess.Popen(['sha256sum', '/root/.lv2/green-stripe-76.lv2/green-stripe-76.so'],
                              stdout=subprocess.PIPE).communicate()[0].split()[0]
    print('Binary SHA256: {0}'.format(binary.decode('ascii')))

    states = build_states()
    if args.only:
        wanted = [w.strip() for w in args.only.split(',') if w.strip()]
        states = [s for s in states if s[0] in wanted]
        if not states:
            raise SystemExit('--only passt auf kein Label. Gueltig: ' +
                             ', '.join(s[0] for s in build_states()))

    results_path = os.path.join(args.output, 'cpu_results.json')
    results = load_json(results_path) if os.path.exists(results_path) else {}
    load_path = os.path.join(args.output, 'load.json')

    for label, colour, transformer in states:
        mh.set(effect, 'enabled', 0.0 if label == 'bypass' else 1.0)
        mh.set(effect, 'compression', 0.0)
        mh.set(effect, 'oversampling', 1.0)
        mh.set(effect, 'transformer', float(transformer))
        mh.set(effect, 'colour', float(colour))
        time.sleep(0.2)
        readback = dict(colour=mh.get(effect, 'colour'),
                        transformer=mh.get(effect, 'transformer'),
                        oversampling=mh.get(effect, 'oversampling'),
                        compression=mh.get(effect, 'compression'),
                        enabled=mh.get(effect, 'enabled'))
        expected = dict(colour=float(colour), transformer=float(transformer),
                        oversampling=1.0, compression=0.0,
                        enabled=0.0 if label == 'bypass' else 1.0)
        bad = [k for k in expected if abs(readback[k] - expected[k]) > 0.01]
        if bad:
            raise SystemExit('Zustand {0}: Ruecklesung weicht ab ({1}). Abbruch, '
                             'damit keine veralteten Zustandszahlen entstehen.'.format(label, bad))
        time.sleep(args.settle)
        report = os.path.join(args.output, 'load.json')
        markdown = os.path.join(args.output, 'load.md')
        cmd = ['python3', args.loadtest, '--label', label,
               '--frames', str(args.frames),
               '--seconds', str(args.seconds),
               '--expect-instances', '1',
               '--report', report, '--markdown', markdown,
               '--note', 'colour={0} transformer={1} OS2x compOff'.format(colour, transformer)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.communicate()[0]
        sys.stdout.write(out.decode('ascii', 'replace'))
        if proc.returncode != 0:
            raise SystemExit('loadtest fehlgeschlagen bei {0}.'.format(label))
        entry = None
        if os.path.exists(report):
            for condition in load_json(report)['conditions']:
                if condition.get('label') == label:
                    entry = condition
        results[label] = dict(colour=colour, transformer=transformer, readback=readback,
                              loadtest=entry)
        save_json(results_path, results)
        if entry:
            print('{0}: median {1:.1f}% peak {2:.1f}%'.format(
                label, entry.get('process_percent_median', float('nan')),
                entry.get('process_percent_max', float('nan'))))

    mh.set(effect, 'enabled', original['enabled'])
    mh.set(effect, 'compression', original['compression'])
    mh.set(effect, 'oversampling', original['oversampling'])
    mh.set(effect, 'transformer', original['transformer'])
    mh.set(effect, 'colour', original['colour'])
    print('Originalzustand wiederhergestellt.')

    lines = ['# CPU-Matrix Dwarf (OS 2x, COMP OFF)', '',
             '| Zustand | Colour % | Transformer | Median % | Peak % |',
             '|---|---:|---|---:|---:|']
    for label, colour, transformer in states:
        entry = results.get(label, {}).get('loadtest') or {}
        lines.append('| {0} | {1} | {2} | {3:.1f} | {4:.1f} |'.format(
            label, colour, TYPES[transformer][1] if transformer else 'None',
            entry.get('process_percent_median', float('nan')),
            entry.get('process_percent_max', float('nan'))))
    with io_open(os.path.join(args.output, 'summary.md'), 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')
    print('Fertig. Ergebnisse in {0} (cpu_results.json, summary.md, load.json/md).'.format(args.output))
    print('Empfehlung: Dwarf jetzt neu starten; danach Optional-Wiederholung:')
    print('  python3 {0} --only bypass,c0-tf60s,c100-tf60s,c0-tfNone'.format(sys.argv[0]))


if __name__ == '__main__':
    main()
