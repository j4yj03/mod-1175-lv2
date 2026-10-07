#!/usr/bin/env python3
"""Erzeugt die CPU-Matrix-Pedalboards fuer den Dwarf aus dem GS76x2-Template.

Je Zustand ein Boardverzeichnis cpux-<label>.pedalboard mit eingeschriebenen
GS76-Parametern (Colour/Transformer/OS 2x/COMP OFF) und einem 20-Hz-Oszillator
als Signalquelle (SWH analogueOsc, Sine). Basistemplate: /tmp/opencode/cpu/.

Aufruf: python3 tools/cpu_board_builder.py [--template /tmp/opencode/cpu]
"""
import argparse
import json
import os
import re
import shutil

STATES = [('bypass', 0, 0)]
_TYPES = [(0, 'None'), (1, '60s'), (2, '80s'), (3, '00s'), (4, 'Sym')]
for _tf, _name in _TYPES:
    STATES.append(('c0-tf{0}'.format(_name), 0, _tf))
for _c in (5, 10, 20, 50, 75, 100):
    STATES.append(('c{0}-tf{1}'.format(_c, 'None'), _c, 0))
for _c in (5, 10, 20, 50, 75, 100):
    for _tf, _name in _TYPES[1:]:
        STATES.append(('c{0}-tf{1}'.format(_c, _name), _c, _tf))

OSC_BLOCK = '''
<signal_osc>
    ingen:canvasX 800.0 ;
    ingen:canvasY 776.2 ;
    ingen:enabled true ;
    ingen:polyphonic false ;
    lv2:port <signal_osc/output> ,
             <signal_osc/wave> ,
             <signal_osc/freq> ,
             <signal_osc/warm> ,
             <signal_osc/instab> ,
             <signal_osc/:bypass> ;
    lv2:prototype <http://plugin.org.uk/swh-plugins/analogueOsc> ;
    pedal:instanceNumber 2 ;
    pedal:preset <> ;
    a ingen:Block .

<signal_osc/output>
    a lv2:AudioPort ,
        lv2:OutputPort .

<signal_osc/wave>
    ingen:value 1.000000 ;
    a lv2:ControlPort ,
        lv2:InputPort .

<signal_osc/freq>
    ingen:value 20.000000 ;
    a lv2:ControlPort ,
        lv2:InputPort .

<signal_osc/warm>
    ingen:value 0.000000 ;
    a lv2:ControlPort ,
        lv2:InputPort .

<signal_osc/instab>
    ingen:value 0.000000 ;
    a lv2:ControlPort ,
        lv2:InputPort .

<signal_osc/:bypass>
    ingen:value 0 ;
    a lv2:ControlPort ,
        lv2:InputPort .

'''


def set_port_value(text, symbol, value):
    pattern = (r'(<green_stripe_76_stereo/' + symbol + r'>\s*\n'
               r'\s*ingen:value )[0-9.]+')
    new, count = re.subn(pattern, lambda m: m.group(1) + '{:.6f}'.format(value), text)
    if count != 1:
        raise ValueError('Port {0}: {1} Treffer statt 1'.format(symbol, count))
    return new


def build_board(template, label, colour, transformer, out_dir):
    ttl = template
    ttl = ttl.replace('doap:name "GS76x2"', 'doap:name "cpux-{0}"'.format(label))
    for symbol, value in (('colour', colour), ('transformer', transformer),
                          ('oversampling', 1.0), ('compression', 0.0),
                          ('enabled', 0.0 if label == 'bypass' else 1.0),
                          ('input', 0.0), ('output', 0.0)):
        ttl = set_port_value(ttl, symbol, value)
    # Oszillator einfuegen (vor dem Graphen <>)
    ttl = ttl.replace('\n<>', OSC_BLOCK + '<>', 1)
    # Bogen capture -> GS76 durch Oszillator ersetzen
    ttl = ttl.replace('''_:b2
    ingen:tail <capture_2> ;
    ingen:head <green_stripe_76_stereo/in_r> .''',
                      '''_:b2
    ingen:tail <signal_osc/output> ;
    ingen:head <green_stripe_76_stereo/in_r> .''')
    ttl = ttl.replace('''_:b4
    ingen:tail <capture_1> ;
    ingen:head <green_stripe_76_stereo/in_l> .''',
                      '''_:b4
    ingen:tail <signal_osc/output> ;
    ingen:head <green_stripe_76_stereo/in_l> .''')
    if 'signal_osc' not in ttl or 'capture_2> ;\n    ingen:head <green_stripe' in ttl:
        raise ValueError('Oszillator-Ersetzung fehlgeschlagen')
    ttl = ttl.replace('ingen:block <green_stripe_76_stereo> ;',
                      'ingen:block <signal_osc> ,\n              <green_stripe_76_stereo> ;')
    # Boardverzeichnis
    board = os.path.join(out_dir, 'cpux-{0}.pedalboard'.format(label))
    if os.path.isdir(board):
        shutil.rmtree(board)
    os.makedirs(board)
    with open(os.path.join(board, 'cpux-{0}.ttl'.format(label)), 'w',
              encoding='utf-8', newline='\n') as handle:
        handle.write(ttl)
    return board


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', default='/tmp/opencode/cpu')
    parser.add_argument('--out', default='/tmp/opencode/cpu/staging')
    args = parser.parse_args()
    with open(os.path.join(args.template, 'GS76x2.ttl'), encoding='utf-8') as handle:
        template = handle.read()
    manifest = open(os.path.join(args.template, 'manifest.ttl'), encoding='utf-8').read()
    if os.path.isdir(args.out):
        shutil.rmtree(args.out)
    os.makedirs(args.out)
    for label, colour, transformer in STATES:
        board = build_board(template, label, float(colour), float(transformer), args.out)
        with open(os.path.join(board, 'cpux-{0}.ttl'.format(label)), encoding='utf-8') as handle:
            text = handle.read()
        # Konsistenzpruefung: Werte wirklich drin?
        checks = {
            'colour': float(colour), 'transformer': float(transformer),
            'oversampling': 1.0, 'compression': 0.0,
            'enabled': 0.0 if label == 'bypass' else 1.0}
        for symbol, expected in checks.items():
            found = re.search(r'/' + symbol + r'>\s*\n\s*ingen:value ([0-9.]+)', text)
            if not found or abs(float(found.group(1)) - expected) > 1e-9:
                raise ValueError('{0}: {1}={2} erwartet, gefunden {3}'.format(
                    label, symbol, expected, found.group(1) if found else 'nichts'))
        with open(os.path.join(board, 'manifest.ttl'), 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(manifest.replace('<GS76x2.ttl>', '<cpux-{0}.ttl>'.format(label)))
        for extra in ('addressings.json', 'snapshots.json'):
            source = os.path.join(args.template, extra)
            if os.path.exists(source):
                shutil.copy(source, os.path.join(board, extra))
    with open(os.path.join(args.out, 'states.json'), 'w', encoding='utf-8') as handle:
        json.dump([{'label': l, 'colour': c, 'transformer': t} for l, c, t in STATES],
                  handle, indent=1)
    print('{0} Boards in {1}'.format(len(STATES), args.out))


if __name__ == '__main__':
    main()
