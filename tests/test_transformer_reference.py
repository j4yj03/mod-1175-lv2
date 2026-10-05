#!/usr/bin/env python3
"""Compare runtime flux to the independent offline solver and HF to analog targets."""
import argparse
import ctypes
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'docs/transformer/offline_fit'))
from reference import Reference, hf_response


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',required=True)
    parser.add_argument('--reference',required=True)
    args=parser.parse_args()
    lib=ctypes.CDLL(str(Path(args.runtime).resolve()))
    pointer=ctypes.POINTER(ctypes.c_double)
    lib.gs76_runtime_transformer.argtypes=[ctypes.c_uint,ctypes.c_double,pointer,pointer,pointer,ctypes.c_size_t]
    ptr=lambda x:x.ctypes.data_as(pointer)
    ref=Reference(args.reference)
    bank=json.loads((ROOT/'data/transformers.json').read_text(encoding='utf-8'))
    worst_flux=0; worst_hf=0; worst_phase=0
    for model,name in enumerate(('60s','80s','00s'),1):
        p=bank['profiles'][name]
        for rate in (44100,48000,96000,192000):
            n=np.arange(rate)
            # Abrupt bass/DC/unequal bursts include history and high-field continuation.
            x=(0.7*np.sin(2*np.pi*23*n/rate)+.2*np.sin(2*np.pi*71*n/rate))*(n<rate*.7)
            x[:rate//5]+=0.6
            x=np.ascontiguousarray(x); output=np.zeros_like(x); raw=np.zeros_like(x)
            assert lib.gs76_runtime_transformer(model,rate,ptr(x),ptr(output),ptr(raw),len(x))==0
            _,diag=ref.render(p,x*p['source_volts_per_fs'],rate,diagnostics=True)
            expected=diag[:,0]*p['fixed_output_normalization']/p['source_volts_per_fs']
            error=float(np.max(np.abs(expected-raw)))
            worst_flux=max(worst_flux,error)
            assert error<2e-9,(name,rate,error)
            # Actual rendered transfer at low excitation. Compare HF only: dividing
            # runtime output/raw isolates the changed discretization from LF memory.
            for frequency in (1000,5000,10000,15000,20000):
                if frequency>=rate*.49: continue
                x=np.ascontiguousarray(.001*np.sin(2*np.pi*frequency*n/rate))
                assert lib.gs76_runtime_transformer(model,rate,ptr(x),ptr(output),ptr(raw),len(x))==0
                phase=np.exp(-2j*np.pi*frequency*n[rate//2:]/rate)
                measured=np.sum(output[rate//2:]*phase)/np.sum(raw[rate//2:]*phase)
                analog=hf_response(p,np.array([frequency]))[0]
                gain_error=float(abs(20*np.log10(abs(measured/analog))))
                phase_error=float(abs(np.angle(measured/analog)*180/np.pi))
                worst_hf=max(worst_hf,gain_error); worst_phase=max(worst_phase,phase_error)
                assert gain_error<.65,(name,rate,frequency,gain_error)
        print(name,'independent flux reference / analog HF: PASS')
    print(f'Runtime/reference raw max={worst_flux:.6g} FS; HF gain max={worst_hf:.6g} dB; HF phase max={worst_phase:.6g} deg')


if __name__=='__main__': main()
