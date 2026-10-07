#!/usr/bin/env python3
"""REAPER-Testbench-Generator: testbench_settings.json und testbench.rpp.

Die testbench.rpp hat drei Region-Gruppen mit Sub-Regionen (je ein getrimmtes
Matrix-Signal-Item mit Take-FX Green Stripe 76 in den Regionseinstellungen):

  GROUP 1        Transformator only (60s/80s/00s/sym; Colour 0)
  GROUP 2        Colour only (5/10/20/50/75/100 %; Transformer None)
  GROUP 1 x 2    alle Kombinationen (Colour x Transformer, 24 Regionen)

Modi:
  --inventory   RPP lesen -> testbench_settings.json schreiben (Ist-Zustand)
  --matrix      Settings aus der Zustandsmatrix neu berechnen (Layoutregeln)
  --apply       Settings -> RPP anpassen (Items + Region-Marker, .bak-Backup)

Die JSON ist die Quelle: Aenderungen an der Matrix werden dort gemacht und
mit --apply in die RPP uebertragen. Region-Namen behalten ihre GUIDs, so
bleiben bestehende Render-Einstellungen und Region-Matrix-Zuordnungen stabil.
"""
import argparse
import json
import re
import sys
import uuid
from pathlib import Path

COLOURS = [5, 10, 20, 50, 75, 100]
TYPES = [(1, '60s'), (2, '80s'), (3, '00s'), (4, 'sym')]
SIGNAL_LENGTH = 64.47
SIGNAL_NAME = 'gs76-matrix-all-m2-stereo.wav'
SIGNAL_TRACK = 'gs76-matrix-all-m2-stereo'
JSFX_NAME = 'GreenStripe/GreenStripe76-Stereo.jsfx'


def default_matrix():
    groups = []
    group1 = []
    for tf, name in TYPES:
        group1.append(dict(name=f'{name}_jsfx', state=dict(
            input=0, output=0, attack=7, release=7, ratio=1, mix=100,
            colour=0, compression=0, enabled=1, link=1, preset=0,
            oversampling=1, transformer=tf)))
    groups.append(dict(name='JSFX.GROUP 1', kind='transformer-only',
                       subregions=group1))
    group2 = []
    for c in COLOURS:
        group2.append(dict(name=f'{c}_col_jsfx', state=dict(
            input=0, output=0, attack=7, release=7, ratio=1, mix=100,
            colour=c, compression=0, enabled=1, link=1, preset=0,
            oversampling=1, transformer=0)))
    groups.append(dict(name='JSFX.GROUP 2', kind='colour-only',
                       subregions=group2))
    group12 = []
    for tf, name in TYPES[1:]:
        block = []
        for c in COLOURS:
            block.append(dict(name=f'{c}_col_{name}_jsfx', state=dict(
                input=0, output=0, attack=7, release=7, ratio=1, mix=100,
                colour=c, compression=0, enabled=1, link=1, preset=0,
                oversampling=1, transformer=tf)))
        groups.append(dict(name=f'JSFX.GROUP 1 x 2 — {name}',
                           kind='interaction', subregions=block))
        group12.append(dict(name=name, block=block))
    return groups


def layout_defaults():
    """Layoutregeln, abgeleitet aus der bestehenden testbench.rpp."""
    return dict(
        signal_length=SIGNAL_LENGTH,
        group1=dict(start=3.53, gap=3.53),
        group2=dict(start=776.0, gap=4.47),
        group12=dict(start=1664.0, colour_gap=4.47, type_gap=11.53),
    )


def slider_line(state):
    values = [state['input'], state['output'], state['attack'], state['release'],
              state['ratio'], state['mix'], state['colour'], state['compression'],
              state['enabled'], state['link'], state['preset'],
              state['oversampling'], state['transformer']]
    line = ' '.join(f'{float(v):.6f}' for v in values)
    return line + ' ' + ' '.join(['-'] * 32)


def compute_layout(settings):
    """Positionen je Sub-Region aus den Layoutregeln setzen."""
    layout = settings['layout']
    length = layout['signal_length']
    groups = settings['groups']
    for group in groups:
        for sub in group['subregions']:
            sub.setdefault('position', 0.0)
            sub.setdefault('length', length)
    g1 = groups[0]
    position = layout['group1']['start']
    for sub in g1['subregions']:
        sub['position'] = round(position, 2)
        position += length + layout['group1']['gap']
    g2 = groups[1]
    position = layout['group2']['start']
    for sub in g2['subregions']:
        sub['position'] = round(position, 2)
        position += length + layout['group2']['gap']
    g12_start = layout['group12']['start']
    for block in groups[2:]:
        position = g12_start
        for sub in block['subregions']:
            sub['position'] = round(position, 2)
            position += length + layout['group12']['colour_gap']
        g12_start = position + layout['group12']['type_gap']
    return settings


def parse_rpp(text):
    """Zeilen in Struktur zerlegen: Kopf, Markerzeilen, Tracks (mit Items)."""
    lines = text.splitlines()
    marker_lines = [i for i, line in enumerate(lines) if line.startswith('  MARKER ')]
    # Track-Bloecke per Klammerzaehlung ueber '<TRACK' / Schliesszeile
    tracks = []
    open_stack = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('<'):
            open_stack.append(stripped.split()[0].lstrip('<'))
        elif stripped == '>' or stripped == '>':
            if open_stack:
                tag = open_stack.pop()
                if tag == 'TRACK':
                    tracks.append(i)
    track_spans = []
    for end in tracks:
        start = end
        while start > 0 and not lines[start].strip().startswith('<TRACK'):
            start -= 1
        track_spans.append((start, end))
    return lines, marker_lines, track_spans


def find_signal_track(lines, track_spans):
    for start, end in track_spans:
        block = lines[start:end + 1]
        if any('NAME ' + SIGNAL_TRACK in line for line in block):
            return start, end, block
    raise SystemExit('Signal-Track "' + SIGNAL_TRACK + '" nicht gefunden')


def split_items(block):
    """ITEM-Bloecke des Tracks extrahieren (verschachtelte <...>-Bloecke
    innerhalb des Items werden ueber Klammerzuege verfolgt):
    (item_lines, non_item_lines)."""
    items = []
    current = None
    depth = 0
    others = []
    for line in block:
        stripped = line.strip()
        if current is None:
            if stripped.startswith('<ITEM'):
                current = [line]
                depth = 1
            else:
                others.append(line)
        else:
            current.append(line)
            if stripped.startswith('<'):
                depth += 1
            elif stripped == '>':
                depth -= 1
                if depth == 0:
                    items.append(current)
                    current = None
                    depth = 0
    return items, others


def parse_item_state(item_lines):
    position = length = None
    sliders = None
    for line in item_lines:
        s = line.strip()
        m = re.match(r'POSITION ([0-9.]+)', s)
        if m:
            position = float(m.group(1))
        m = re.match(r'LENGTH ([0-9.]+)', s)
        if m:
            length = float(m.group(1))
        m = re.match(r'([0-9.-]+(?: [0-9.-]+)*) - -', s)
        if m and sliders is None and s.count(' ') >= 12:
            try:
                sliders = [float(v) for v in s.split()[:13]]
            except ValueError:
                sliders = None
    return position, length, sliders


def inventory(args):
    rpp_path = Path(args.rpp)
    text = rpp_path.read_text(encoding='utf-8', errors='replace')
    lines, marker_lines, track_spans = parse_rpp(text)
    start, end, block = find_signal_track(lines, track_spans)
    items, _ = split_items(block)
    regions = []
    for i in marker_lines:
        m = re.match(r'  MARKER (\d+) ([0-9.]+) (".*?"|\S+) (.*)$', lines[i])
        if not m:
            continue
        regions.append(dict(line_index=i, marker_id=int(m.group(1)),
                            position=float(m.group(2)), name=m.group(3).strip('"'),
                            tail=m.group(4)))
    # Region-Gruppen anhand der Namen erkennen
    subregions = []
    for item_lines in items:
        position, length, sliders = parse_item_state(item_lines)
        if position is None or sliders is None:
            continue
        state = dict(input=sliders[0], output=sliders[1], attack=sliders[2],
                     release=sliders[3], ratio=sliders[4], mix=sliders[5],
                     colour=sliders[6], compression=int(sliders[7]),
                     enabled=int(sliders[8]), link=int(sliders[9]),
                     preset=int(sliders[10]), oversampling=int(sliders[11]),
                     transformer=int(sliders[12]))
        subregions.append(dict(position=position, length=length, state=state))
    groups = []
    open_group = None
    open_marker = None
    for reg in regions:
        name = reg['name']
        if 'GROUP 1' in name and 'x' not in name.lower() and open_group is None:
            open_group = dict(name=name)
            open_marker = None
            continue
    # einfache Zuordnung: Sub-Region-Namen aus den Items mit Region-Namen matchen
    # Nur Sub-Region-Marker (Regionstyp '0 2'); Parent-/Sonstige ('0 1'/'0 3')
    # haben eigene Namen und duerfen die Zuordnung nicht ueberschreiben.
    region_by_pos = {round(r['position'], 2): r for r in regions
                     if r['name'] and r['name'] != '""' and r['tail'].endswith(' 0 2')}
    # Gruppierung nach Zustand (robuster als Namensmuster):
    #   Colour 0 + Transformer > 0 -> Transformer only
    #   Colour > 0 + Transformer 0 -> Colour only
    #   Colour > 0 + Transformer > 0 -> Interaktion
    kinds = [('transformer-only', 'JSFX.GROUP 1'), ('colour-only', 'JSFX.GROUP 2'),
             ('interaction', 'JSFX.GROUP 1 x 2')]
    groups_out = [dict(name=name, subregions=[]) for _, name in kinds]
    for sub in subregions:
        state = sub['state']
        colour, transformer = state['colour'], state['transformer']
        if colour == 0 and transformer > 0:
            index = 0
        elif colour > 0 and transformer == 0:
            index = 1
        else:
            index = 2
        groups_out[index]['subregions'].append(
            dict(name=region_by_pos.get(round(sub['position'], 2), {}).get('name',
                 sub['name'] if 'name' in sub else ''),
                 position=sub['position'], length=sub['length'], state=state))
    settings = dict(schema=1, generator='tools/testbench_rpp.py',
                    signal=dict(file='Media\\\\' + SIGNAL_NAME, length=SIGNAL_LENGTH),
                    jsfx=JSFX_NAME, layout=layout_defaults(),
                    groups=groups_out)
    Path(args.json).write_text(json.dumps(settings, indent=1, ensure_ascii=False) + '\n',
                               encoding='utf-8')
    print('Inventar: {0} Sub-Regionen in {1} Gruppen -> {2}'.format(
        sum(len(g['subregions']) for g in groups_out), len(groups_out), args.json))


def render_regions(settings):
    for group in settings['groups']:
        start = min(sub['position'] for sub in group['subregions'])
        end = max(sub['position'] + sub['length'] for sub in group['subregions'])
        yield group, start, end


def apply_settings(args):
    settings = json.loads(Path(args.json).read_text(encoding='utf-8'))
    rpp_path = Path(args.rpp)
    text = rpp_path.read_text(encoding='utf-8', errors='replace')
    lines, marker_lines, track_spans = parse_rpp(text)
    start, end, block = find_signal_track(lines, track_spans)
    template_items, others = split_items(block)
    if not template_items:
        raise SystemExit('Keine Item-Vorlage im Signal-Track gefunden.')
    template = template_items[0]
    # GUIDs aus dem Bestand uebernehmen (Region- und Item-Stabilitaet)
    old_by_name = {}
    for item_lines in template_items:
        position, length, sliders = parse_item_state(item_lines)
        guid = None
        for line in item_lines:
            m = re.search(r'IGUID \{([0-9A-F-]+)\}', line)
            if m:
                guid = m.group(1)
        if position is not None and guid:
            old_by_name[round(position, 2)] = guid
    # Region-GUIDs nach Namen
    region_guid = {}
    for i in marker_lines:
        m = re.match(r'  MARKER (\d+) ([0-9.]+) ("(?:[^"]*)"|\S+) (.*)$', lines[i])
        if m and m.group(3).strip('"'):
            region_guid[m.group(3).strip('"')] = m.group(4)

    # Signal-Track neu aufbauen
    new_items = []
    iid_base = 40
    for group in settings['groups']:
        for index, sub in enumerate(group['subregions']):
            item = list(template)
            for line_no, line in enumerate(item):
                s = line.strip()
                if s.startswith('POSITION '):
                    item[line_no] = line.replace(s, 'POSITION {:.2f}'.format(sub['position']))
                elif s.startswith('LENGTH '):
                    item[line_no] = line.replace(s, 'LENGTH {:.2f}'.format(sub['length']))
                elif s.startswith('IGUID '):
                    old_guid = old_by_name.get(round(sub['position'], 2))
                    item[line_no] = '      IGUID {{{0}}}'.format(
                        old_guid or str(uuid.uuid4()).upper())
                elif s.startswith('IID '):
                    item[line_no] = '      IID {0}'.format(iid_base + len(new_items))
                elif s.startswith('GUID {'):
                    item[line_no] = '      GUID {{{0}}}'.format(str(uuid.uuid4()).upper())
                elif re.match(r'^[0-9.-]+(?: [0-9.-]+)* - -', s) and s.count(' ') >= 12:
                    item[line_no] = '          ' + slider_line(sub['state'])
            new_items.append(item)
    others[-1] = '    >'
    new_block = others[:-1] + [line for item in new_items for line in item] + ['    >']
    lines = lines[:start] + new_block + lines[end + 1:]

    # Marker: Sub-Region- und Gruppenmarker neu schreiben, Rest (Dwarf-Aufnahmen
    # etc.) behalten
    keep = []
    known_sub_names = {sub['name'] for g in settings['groups'] for sub in g['subregions']}
    for i in marker_lines:
        m = re.match(r'  MARKER (\d+) ([0-9.]+) (".*?"|\S+) (.*)$', lines[i])
        if not m:
            continue
        name = m.group(3).strip('"')
        if name in known_sub_names or 'GROUP' in name or name.startswith('jsfx'):
            continue
        keep.append(lines[i])
    new_markers = []
    marker_id = 100
    for group, g_start, g_end in render_regions(settings):
        guid = region_guid.get(group['name']) or str(uuid.uuid4()).upper()
        new_markers.append('  MARKER {0} {1:.2f} "{2}" 1 0 1 R {{{3}}} 0 1'.format(
            marker_id, g_start, group['name'], guid))
        for sub in group['subregions']:
            marker_id += 1
            sguid = region_guid.get(sub['name']) or str(uuid.uuid4()).upper()
            new_markers.append('  MARKER {0} {1:.2f} "{2}" 5 0 1 R {{{3}}} 0 2'.format(
                marker_id, sub['position'], sub['name'], sguid))
            new_markers.append('  MARKER {0} {1:.2f} "" 5'.format(
                marker_id, sub['position'] + sub['length']))
        marker_id += 1
        new_markers.append('  MARKER {0} {1:.2f} "" 1'.format(marker_id, g_end))
    if marker_lines:
        first = marker_lines[0]
        lines = lines[:first] + new_markers + keep + lines[marker_lines[-1] + 1:]
    backup = rpp_path.with_suffix('.rpp.bak')
    backup.write_text(text, encoding='utf-8', newline='\n')
    rpp_path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print('RPP angepasst: {0} Items, {1} Region-Marker (Backup: {2}).'.format(
        len(new_items), len(new_markers), backup.name))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rpp', default='reaper/testbench/testbench.rpp')
    parser.add_argument('--json', default='reaper/testbench/testbench_settings.json')
    parser.add_argument('--inventory', action='store_true', help='RPP -> JSON')
    parser.add_argument('--matrix', action='store_true', help='Zustandsmatrix -> JSON')
    parser.add_argument('--apply', action='store_true', help='JSON -> RPP')
    args = parser.parse_args()
    if args.inventory:
        inventory(args)
    elif args.matrix:
        settings = dict(schema=1, generator='tools/testbench_rpp.py',
                        signal=dict(file='Media\\\\' + SIGNAL_NAME, length=SIGNAL_LENGTH),
                        jsfx=JSFX_NAME, layout=layout_defaults(),
                        groups=default_matrix())
        compute_layout(settings)
        Path(args.json).write_text(json.dumps(settings, indent=1, ensure_ascii=False) + '\n',
                                   encoding='utf-8')
        print('Matrix in {0} geschrieben ({1} Sub-Regionen); --apply uebertraegt sie in die RPP.'.format(
            args.json, sum(len(g['subregions']) for g in settings['groups'])))
    elif args.apply:
        apply_settings(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
