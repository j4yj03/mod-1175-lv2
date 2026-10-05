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
# read_text() without an encoding uses the locale encoding, which on Windows
#     is cp1252 and mangles the UTF-8 dashes in data/*.json.
    parameters=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    presets=json.loads((ROOT/'data/presets.json').read_text(encoding='utf-8'))
    # Preset value per control port. Derived from the parameter list instead of
    # special-casing symbols, so a new port cannot silently skip this check:
    # 'enabled' and 'link' mirror the preset, appended ports (oversampling,
    # transformer) reset to their documented default.
    def preset_value(preset,spec):
        symbol=spec['symbol']
        if symbol=='enabled':
            return 1
        if symbol=='stereo_link':
            return preset['link']
        if symbol in preset:
            return preset[symbol]
        assert spec.get('lv2_append'),(symbol,'not a preset value and not appended')
        return spec['default']
    for p in presets:
        for spec in parameters:
            key='link' if spec['symbol']=='stereo_link' else spec['symbol']
            value=preset_value(p,spec)
            assert spec['min']<=value<=spec['max'],(p['name'],key)
    bundle=ROOT/'lv2/green-stripe-76.lv2'
    # Port count is derived: audio ports plus control ports plus the latency port.
    expected={variant:audio+len([s for s in parameters
                                  if variant=='stereo' or not s.get('stereo_only')])+1
              for variant,audio in [('mono',2),('stereo',4)]}
    for variant, count in expected.items():
        ttl=(bundle/(variant+'.ttl')).read_text(encoding='utf-8')
        indices=list(map(int,re.findall(r'lv2:index (\d+)',ttl)))
        assert indices==list(range(count)), (variant,indices)
        assert len(re.findall('lv2:OutputPort, lv2:ControlPort',ttl))==1
        assert 'lv2:designation lv2:enabled' in ttl
        assert 'gain_reduction' not in ttl
        for spec in parameters:
            if variant=='mono' and spec.get('stereo_only'):
                assert f'lv2:symbol "{spec["symbol"]}"' not in ttl,spec['symbol']
            else:
                assert f'lv2:symbol "{spec["symbol"]}"' in ttl,spec['symbol']
        assert 'lv2:connectionOptional' in ttl
    for path in (ROOT/'jsfx').glob('*.jsfx*'):
        content=path.read_text(encoding='utf-8')
        for include in re.findall(r'^import (.+)$',content,re.M):
            assert (path.parent/include.strip()).is_file(),include
    gui=(bundle/'modgui.ttl').read_text(encoding='utf-8')
    for path in re.findall(r'<(modgui/[^>]+)>',gui):
        assert (bundle/path).is_file(),f'Missing asset: {path}'
    css=(bundle/'modgui/green-stripe.css').read_text(encoding='utf-8')
    for asset in re.findall(r'/resources/(assets/[^{}\)]+)',css):
        assert (bundle/'modgui'/asset).is_file(),f'Missing control asset: {asset}'
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
