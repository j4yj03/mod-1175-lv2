#!/usr/bin/env python3
"""Read local NAM JSON metadata and hashes; no inference or file mutation."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def summarise(model):
    result={k:model.get(k) for k in ('version','architecture','sample_rate','metadata')}
    weights=model.get('weights',[])
    result['weight_count']=len(weights)
    result['all_weights_finite']=all(isinstance(x,(int,float)) and math.isfinite(x) for x in weights)
    config=model.get('config',{})
    if model.get('architecture')=='SlimmableContainer':
        result['submodels']=[dict(max_value=s.get('max_value'),model=summarise(s['model'])) for s in config.get('submodels',[])]
    else:
        result['config']=config
        lookback=0
        for layer in config.get('layers',[]):
            dilations=layer.get('dilations',[])
            kernels=layer.get('kernel_sizes') or [layer.get('kernel_size',1)]*len(dilations)
            lookback+=sum((k-1)*d for k,d in zip(kernels,dilations))
            lookback+=max(0,layer.get('head',{}).get('kernel_size',1)-1)
        result['receptive_field_samples']=lookback+1
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path,nargs='?',default=Path(__file__).resolve().parents[2]/'UREI_Universal Audio 1176')
    args=parser.parse_args()
    records=[]
    for file in sorted(args.directory.glob('*.nam')):
        raw=file.read_bytes(); model=json.loads(raw)
        records.append(dict(file=file.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),**summarise(model)))
    if not records: raise SystemExit('No .nam profiles in '+str(args.directory))
    print(json.dumps(records,indent=2,ensure_ascii=False))


if __name__=='__main__': main()
