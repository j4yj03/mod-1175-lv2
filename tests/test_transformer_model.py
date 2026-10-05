#!/usr/bin/env python3
"""Model interchange rejects unsupported, malformed and unsafe refit banks."""
import copy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from transformer_model import validate


def main():
    bank=json.loads((ROOT/'data/transformers.json').read_text(encoding='utf-8'))
    validate(bank)
    rejected=0
    for key,value in [('lm_h',0),('flux_scale_vs',float('nan')),('hf_q',.2),
                      ('family',2),('exponent',13),('high_field_l_ratio',0),
                      ('nonlinear_series_resistance_ohm',100),('extra_parameter',1)]:
        candidate=copy.deepcopy(bank); candidate['profiles']['00s'][key]=value
        try: validate(candidate)
        except ValueError: rejected+=1
        else: raise AssertionError(f'Accepted invalid {key}={value}')
    assert rejected==8
    print('Refit model validation / unsupported laws / finite and physical ranges: PASS')


if __name__=='__main__': main()
