#!/usr/bin/env python3
"""Own 60s/80s/00s profiles derived from the first Jensen gray-box fit."""
import argparse
import csv
import json
import math

from scipy.optimize import brentq
import numpy as np

from fit import HERE, write_json, sha256
from reference import Reference, linear_response


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',required=True)
    args=parser.parse_args()
    reference=Reference(args.library)
    fitted=json.loads((HERE/'jensen-fit.json').read_text(encoding='utf-8'))
    base=fitted['best']['parameters'].copy()
    base.setdefault('high_field_l_ratio',0)
    base.setdefault('nonlinear_series_resistance_ohm',0)
    # Regularization only above the largest fitted operating point, to avoid
    # an unphysical infinite magnetizing-current asymptote during stress tests.
    # This is an explicit high-field assumption, not a fitted material parameter.
    base['high_field_l_ratio']=.0001
    specifications={
        '00s':dict(target_one_percent_dbfs=-2,flux_l_scale=1.0,history_scale=1.0,
                   family=1,exponent=1,
                   history_threshold_scale=1.0,hf_frequency_hz=base['hf_frequency_hz'],
                   hf_q=base['hf_q'],description='Clean/Jensen-like, largest headroom'),
        '80s':dict(target_one_percent_dbfs=-8,flux_l_scale=.8,history_scale=1.5,
                   family=0,exponent=5,
                   history_threshold_scale=1.0,hf_frequency_hz=48000.0,
                   hf_q=1/math.sqrt(2),description='Balanced, moderate earlier saturation'),
        '60s':dict(target_one_percent_dbfs=-14,flux_l_scale=.65,history_scale=2.0,
                   family=0,exponent=3,
                   history_threshold_scale=1.0,hf_frequency_hz=26000.0,
                   hf_q=1/math.sqrt(2),description='Warm, soft/earlier saturation and HF rounding'),
    }
    # One universal drive scale: -18 dBFS peak -> +4 dBu 1k primary
    # under the fitted reference fixture. No loudness difference by arbitrary
    # input scaling; the core flux thresholds are actually varied below.
    base1k=reference.tone(base,1000,4,4096)[0]
    source_volts_per_fs=base1k['source_rms_v']*math.sqrt(2)/10**(-18/20)
    profiles={}
    for name,spec in specifications.items():
        params=base.copy()
        params['family']=spec['family'];params['exponent']=spec['exponent']
        if params['family']==0:
            params['saturation_strength']=1
            params['high_field_l_ratio']=0
        params['lm_h']*=spec['flux_l_scale']
        params['relax_l_h']*=spec['flux_l_scale']
        params['hysteresis_stiffness_a_per_vs']*=spec['history_scale']
        params['hf_frequency_hz']=spec['hf_frequency_hz'];params['hf_q']=spec['hf_q']
        # Determine threshold for a fixed open-circuit digital source amplitude.
        desired_source=source_volts_per_fs*10**(spec['target_one_percent_dbfs']/20)/math.sqrt(2)
        def source_for_one_percent(flux):
            params['flux_scale_vs']=flux
            def deviation(level):
                return reference.tone(params,20,level,2048)[0]['thd_percent']-1
            level=brentq(deviation,-50,54,xtol=1e-6)
            return reference.tone(params,20,level,2048)[0]['source_rms_v']-desired_source
        flux=brentq(source_for_one_percent,.003,.2,xtol=1e-9)
        params['flux_scale_vs']=flux
        level=brentq(lambda dbu:reference.tone(params,20,dbu,4096)[0]['thd_percent']-1,
                     -50,54,xtol=1e-7)
        anchor=reference.tone(params,20,level,4096)[0]
        actual_dbfs=20*math.log10(anchor['source_rms_v']*math.sqrt(2)/source_volts_per_fs)
        small=reference.tone(params,1000,4,4096)[0]
        normalization=10**(-small['gain_source_db']/20)
        profiles[name]=dict(name=name,kind='own musical profile, not vintage hardware revision',
                            derivation=spec,parameters=params,
                            source_volts_per_fs=source_volts_per_fs,
                            fixed_output_normalization=normalization,
                            normalization_policy='explicit fixed 1k/+4dBu gain normalization, no auto-makeup',
                            measured_20hz_1percent_dbu=level,
                            measured_20hz_1percent_dbfs=actual_dbfs,
                            measured_hf_gain_20khz_db=20*math.log10(abs(linear_response(
                                params,np.array([20000]))[0][0]/linear_response(params,np.array([1000]))[0][0])))
        print(name,flux,level,actual_dbfs,profiles[name]['measured_hf_gain_20khz_db'],flush=True)
    rows=[];waves={}
    for name,profile in profiles.items():
        params=profile['parameters']
        reference_gain=reference.tone(params,1000,-20,4096)[0]['gain_source_db']
        for frequency in (20,30,50,100,1000,10000,20000):
            for level in (-20,0,4,10,14,18,20,24):
                m,h,w=reference.tone(params,frequency,level,4096,waveform=True)
                rows.append(dict(profile=name,frequency_hz=frequency,input_primary_dbu=level,
                                 input_source_dbfs=20*math.log10(m['source_rms_v']*math.sqrt(2)/source_volts_per_fs),
                                 compression_from_clean_midband_db=reference_gain-m['gain_source_db'],**m))
                if frequency in (20,50,1000) and level in (4,18):
                    # Output is raw core voltage in waveform; filtered complex
                    # harmonics are separate, prevents accidental HF mislabeling.
                    waves[f'{name}_f{frequency}_p{level}__core']=w
                    waves[f'{name}_f{frequency}_p{level}__output_harmonics']=h
    write_json(HERE/'profiles.json',dict(
        status='offline draft profiles; normalized audio previews; not in plugin runtime',
        user_direction='60s warm -> 80s balanced -> 00s clean',
        fit_sha256=sha256(HERE/'jensen-fit.json'),script_sha256=sha256(__import__('pathlib').Path(__file__)),
        high_field_extension='C1 continuous monotone finite high-field slope above .98*fluxscale; assumed ratio 1e-4',
        profiles=profiles))
    with (HERE/'profile-matrix.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    np.savez_compressed(HERE/'profile-waveforms.npz',**waves)


if __name__=='__main__':main()
