#!/usr/bin/env python3
"""Static bundle/preset checks. RDF parsing, if rdflib is installed, is stronger."""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    subprocess.run([sys.executable,str(ROOT/'tools/generate.py'),'--check'],check=True)
    parameters=json.loads((ROOT/'data/parameters.json').read_text())
    presets=json.loads((ROOT/'data/presets.json').read_text())
    for p in presets:
        for spec in parameters:
            key='link' if spec['symbol']=='stereo_link' else spec['symbol']
            value=1 if key=='enabled' else p[key]
            assert spec['min']<=value<=spec['max'],(p['name'],key)
    bundle=ROOT/'lv2/green-stripe-76.lv2'
    for variant, expected in [('mono',12),('stereo',15)]:
        ttl=(bundle/(variant+'.ttl')).read_text()
        indices=list(map(int,re.findall(r'lv2:index (\d+)',ttl)))
        assert indices==list(range(expected)), (variant,indices)
        assert len(re.findall('lv2:OutputPort, lv2:ControlPort',ttl))==1
        assert 'lv2:designation lv2:enabled' in ttl
        assert 'gain_reduction' not in ttl
    for path in (ROOT/'jsfx').glob('*.jsfx*'):
        content=path.read_text()
        for include in re.findall(r'^import (.+)$',content,re.M):
            assert (path.parent/include.strip()).is_file(),include
    gui=(bundle/'modgui.ttl').read_text()
    for path in re.findall(r'<(modgui/[^>]+)>',gui):
        assert (bundle/path).is_file(),f'Missing asset: {path}'
    try:
        import rdflib
    except ImportError:
        print('rdflib unavailable: structural checks only; run RDF validation on test machine')
    else:
        for path in bundle.glob('*.ttl'):
            graph=rdflib.Graph(); graph.parse(path,format='turtle')
        print('Turtle parsing: PASS')
    print(f'Bundle / {len(presets)} presets / imports: PASS')


if __name__=='__main__':
    main()
