#!/usr/bin/env python3
"""Audit actual LV2/RPL preset values and render every preset with a native probe."""
import argparse
import base64
import collections
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CONTROLS=('input','output','attack','release','ratio','mix','colour','compression')


def audit_banks(presets, parameters):
    ttl=(ROOT/'lv2/green-stripe-76.lv2/presets.ttl').read_text(encoding='utf-8')
    count=0
    for variant in ('mono','stereo'):
        rpl=(ROOT/f'jsfx/GreenStripe76-{variant.title()}.rpl').read_text(encoding='utf-8')
        records=re.findall(r'<PRESET "([^"]+)"\s+([A-Za-z0-9+/=]+)\s+>',rpl)
        assert len(records)==len(presets),variant
        for index,(preset,(name,payload)) in enumerate(zip(presets,records),1):
            assert name==preset['name'] and name.startswith(f'{index:02d} '),name
            expected=[preset[k] for k in CONTROLS]+[1,preset['link'],0,0,preset.get('transformer',0)]
            decoded=base64.b64decode(payload).decode('utf-8')
            assert list(map(float,decoded.split()[:13]))==expected,(variant,name,'RPL')
            block=re.search(r'<[^>]+#green-stripe-76-preset-'+variant+f'-{index:02d}>'+r'[^\n]*; lv2:port\n(.*?) \.\n',ttl,re.S)
            assert block,(variant,name,'TTL missing')
            actual={symbol:float(value) for symbol,value in re.findall(
                r'lv2:symbol "([^"]+)"; pset:value ([^\s\]]+)',block[1])}
            target={k:preset[k] for k in CONTROLS}
            target.update(enabled=1,oversampling=0,transformer=preset.get('transformer',0))
            if variant=='stereo': target['stereo_link']=preset['link']
            assert actual==target,(variant,name,'TTL')
            for parameter in parameters:
                if parameter['symbol'] not in actual: continue
                value=actual[parameter['symbol']]
                assert math.isfinite(value) and parameter['min']<=value<=parameter['max']
                if parameter.get('labels') or parameter.get('toggle'): assert value.is_integer()
            count+=1
    assert len({p['name'] for p in presets})==len(presets)
    return count


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    presets=json.loads((ROOT/'data/presets.json').read_text(encoding='utf-8'))
    parameters=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    model=json.loads((ROOT/'data/model.json').read_text(encoding='utf-8'))
    bank_count=audit_banks(presets,parameters)
    cases=[]; lines=[]
    def case(preset,stereo,os,fixture,level,ratio=None):
        p=dict(preset)
        if ratio is not None: p['ratio']=ratio
        cases.append(dict(preset=p['name'],stereo=stereo,oversampling=os,fixture=fixture,
                          input_peak_bound_dbfs=level,ratio_index=p['ratio']))
        values=[p[k] for k in CONTROLS]+[p['link'],p.get('transformer',0),os,int(stereo),fixture,level]
        lines.append(' '.join(map(str,values)))
    for preset in presets:
        for stereo in (False,True):
            for os in (0,1,2): case(preset,stereo,os,0,-12)
    for index in (30,34):
        for level in (-18,-12,-6):
            for ratio in (1,0): case(presets[index],True,0,1,level,ratio)
    result=subprocess.run([str(args.probe.resolve())],input='\n'.join(lines)+'\n',
                          text=True,capture_output=True,check=True)
    metrics=result.stdout.splitlines(); assert len(metrics)==len(cases)
    for c,line in zip(cases,metrics):
        values=list(map(float,line.split())); assert len(values)==4 and all(map(math.isfinite,values))
        c.update(zip(('output_peak_fs','peak_gr_db','mean_gr_db','rms_gain_db'),values))
    source_paths=['data/presets.json','data/parameters.json','data/model.json','data/transformers.json',
                  'src/dsp/GreenStripe.hpp','src/dsp/Transformer.hpp','src/dsp/ModelConstants.hpp',
                  'src/dsp/TransformerModels.hpp','jsfx/GreenStripe76-Core.jsfx-inc',
                  'tests/jsfx_parity.cpp','tools/preset_probe.cpp','tools/audit_presets.py']
    report=dict(version=model['version'],rate=48000,frames=57600,bank_states=bank_count,
                fixtures={'0':'53/997/6011-Hz left, 79/313-Hz right; peak-bound -12 dBFS; 0.15/0.65/0.8-s envelope; reset each case',
                          '1':'1-kHz coherent sine, opposite-polarity stereo, three peak levels; reset each case'},
                window_seconds=[.4,.6],gr_definition='FET gain reduction before Mix; excludes transformer/amplifier loss',
                limitation='Synthetic engineering review, not music listening or universal target-GR validation; output peaks use this fixture only',
                probe_sha256=hashlib.sha256(args.probe.read_bytes()).hexdigest(),
                source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths},
                active_ratios=dict(collections.Counter(str(p['ratio']) for p in presets if p['compression'])),
                cases=cases)
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'LV2/RPL/source values: {bank_count} states PASS; rendered {len(cases)} finite cases')
    for i,preset in enumerate(presets):
        c=cases[i*6]
        print(f'{preset["name"]}: peak GR={c["peak_gr_db"]:.3f} dB, output peak={c["output_peak_fs"]:.3f} FS')
    for c in cases[len(presets)*6:]:
        print(f'{c["preset"]} ratio={model["ratios"][c["ratio_index"]]:g}:1 input={c["input_peak_bound_dbfs"]} mean GR={c["mean_gr_db"]:.4f} dB output gain={c["rms_gain_db"]:.4f} dB')


if __name__=='__main__': main()
