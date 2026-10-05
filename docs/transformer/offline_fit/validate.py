#!/usr/bin/env python3
"""Independent convergence, causal state, passivity and held-out checks."""
import argparse
import json
import math
import time

import numpy as np
from scipy.integrate import solve_ivp

from fit import HERE,write_json,sha256
from reference import Reference,THRESHOLDS


def harmonic_metrics(time,output,frequency,count=15):
    design=[np.ones(len(time))]
    for k in range(1,count+1):
        design.extend((np.cos(2*np.pi*k*frequency*time),np.sin(2*np.pi*k*frequency*time)))
    coefficients=np.linalg.lstsq(np.array(design).T,output,rcond=None)[0]
    magnitudes=np.hypot(coefficients[1::2],coefficients[2::2])
    return dict(thd_percent=float(100*np.linalg.norm(magnitudes[1:])/magnitudes[0]),
                fundamental_peak_v=float(magnitudes[0]),dc_v=float(coefficients[0]))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',required=True)
    args=parser.parse_args()
    reference=Reference(args.library)
    fit=json.loads((HERE/'jensen-fit.json').read_text(encoding='utf-8'))
    base=fit['best']['parameters'].copy()
    profiles=json.loads((HERE/'profiles.json').read_text(encoding='utf-8'))['profiles']
    cases=[]
    for frequency,level in ((20,-20),(20,4),(20,20),(30,24),(50,28),(1000,4)):
        low=reference.tone(base,frequency,level,2048)[0]
        high=reference.tone(base,frequency,level,8192)[0]
        error_db=20*math.log10(low['thd_percent']/high['thd_percent'])
        error_gain=low['gain_primary_db']-high['gain_primary_db']
        cases.append(dict(frequency_hz=frequency,input_dbu=level,thd_step_error_db=error_db,
                          gain_step_error_db=error_gain,shooting_error=high['periodic_shooting_error'],
                          solver_iterations=high['max_solver_iterations']))
        assert abs(error_db)<.01 and abs(error_gain)<1e-4
        assert high['periodic_shooting_error']<1e-9

    # Independent high-order ODE solve for the smooth baseline (no stops).
    smooth=base.copy();smooth['hysteresis_enabled']=0
    smooth['hf_frequency_hz']=0
    frequency,level=50,14
    m,h,_=reference.tone(smooth,frequency,level,8192)
    amplitude=m['source_rms_v']*math.sqrt(2)
    ra=smooth['source_resistance_ohm']+smooth['primary_resistance_ohm']
    rb=smooth['secondary_resistance_ohm']+smooth['load_resistance_ohm']
    den=1+ra/rb+ra*smooth['core_conductance_s']
    def law(x):
        u=abs(x)/smooth['flux_scale_vs']
        return x*(1+smooth['saturation_strength']*u/(1-u))/smooth['lm_h']
    def ode(t,z):
        voltage=(amplitude*math.sin(2*math.pi*frequency*t)-ra*(law(z[0])+
                  (z[0]-z[1])/smooth['relax_l_h']))/den
        return voltage,2*math.pi*smooth['relax_frequency_hz']*(z[0]-z[1])
    duration=30.0
    times=duration-10/frequency+np.arange(10*2048)/(frequency*2048)
    solution=solve_ivp(ode,(0,duration),(0,0),method='DOP853',rtol=1e-10,atol=1e-13,
                       max_step=1/(frequency*64),t_eval=times)
    voltage=np.array([ode(t,z)[0] for t,z in zip(solution.t,solution.y.T)])
    independent=harmonic_metrics(times,voltage*smooth['load_resistance_ohm']/rb,frequency)
    smooth_error_db=20*math.log10(independent['thd_percent']/m['thd_percent'])
    print('independent smooth',smooth_error_db,independent,m,flush=True)
    assert abs(smooth_error_db)<.03

    physical=[];finite=[]
    for name,entry in profiles.items():
        p=entry['parameters'];scale=entry['source_volts_per_fs']
        # Stress across rates, start phase, burst duration and interspersed silence.
        for rate in (48000,96000,192000):
            count=int(rate*3.0);t=np.arange(count)/rate
            source=scale*np.sin(2*np.pi*20*t)*np.where((t<.3)|((t>1)&(t<1.8)),1,0)
            output,diag=reference.render(p,source,rate,True)
            negative,_=reference.render(p,-source,rate)
            positive_peak=float(np.max(abs(output)))
            symmetry=float(np.max(abs(output+negative)))
            assert np.all(np.isfinite(output)) and symmetry<1e-8
            tail=float(np.max(abs(output[-int(.2*rate):])))
            assert tail<.005*max(positive_peak,1e-8)
            finite.append(dict(profile=name,rate_hz=rate,peak_v=positive_peak,
                               tail_v=tail,odd_symmetry_error_v=symmetry,
                               max_iterations=float(np.max(diag[:,3]))))
        # Source/load response must actually change; predicted, not hardware-qualified.
        low_source=p.copy();low_source['source_resistance_ohm']=50
        high_source=p.copy();high_source['source_resistance_ohm']=2000
        heavy=p.copy();heavy['load_resistance_ohm']=1000
        measurement=reference.tone(p,20,10,4096)[0]
        low=reference.tone(low_source,20,10,4096)[0]
        high=reference.tone(high_source,20,10,4096)[0]
        loaded=reference.tone(heavy,1000,4,4096)[0]
        assert high['thd_percent']>low['thd_percent']
        assert loaded['gain_primary_db']<reference.tone(p,1000,4,4096)[0]['gain_primary_db']-3

        # Energy accounting for periodic native state: source = copper + load + core.
        # Raw waveform at DC-free periodic solution is used; HF cascade excluded.
        mm,_,wave=reference.tone(p,20,10,8192,True)
        source,primary,out,flux,current=wave[:,1:].T
        rb=p['secondary_resistance_ohm']+p['load_resistance_ohm']
        vcore=out*rb/p['load_resistance_ohm'];i_secondary=vcore/rb
        ps=float(np.mean(source*current))
        copper=float(np.mean((p['source_resistance_ohm']+p['primary_resistance_ohm'])*current**2+
                              p['secondary_resistance_ohm']*i_secondary**2))
        load=float(np.mean(out*i_secondary))
        core=float(np.mean(vcore*(current-i_secondary)))
        mismatch=ps-copper-load-core
        assert abs(mismatch)<1e-10*max(ps,1)
        assert core>=-1e-8
        physical.append(dict(profile=name,source_power_w=ps,copper_power_w=copper,
                              load_power_w=load,core_cycle_average_power_w=core,
                              power_balance_error_w=mismatch,
                              thd_rs50_percent=low['thd_percent'],thd_rs2000_percent=high['thd_percent']))
    # Causal rate convergence at steady 10 kHz tone, evaluated after warm-up.
    rate_checks=[]
    for name,entry in profiles.items():
        measurements=[]
        for rate in (192000,384000,768000):
            t=np.arange(int(rate*.12))/rate
            source=entry['source_volts_per_fs']*.4*np.sin(2*np.pi*10000*t)
            output,_=reference.render(entry['parameters'],source,rate)
            selected=t>=.1
            mm=harmonic_metrics(t[selected],output[selected],10000,count=3)
            measurements.append(dict(rate_hz=rate,**mm))
        error=20*math.log10(measurements[1]['fundamental_peak_v']/measurements[2]['fundamental_peak_v'])
        assert abs(error)<.03
        rate_checks.append(dict(profile=name,measurements=measurements,high_rate_gain_error_db=error))
    # Held-out scores refer to the selected model, not a retuned per-curve model.
    evaluation=fit['evaluation']
    stats={}
    for split in ('train','validation'):
        rows=[r for r in evaluation if r['split']==split]
        stats[split]=dict(count=len(rows),inside_intervals=sum(r['inside_interval'] for r in rows),
                          outside=[r['target_id'] for r in rows if not r['inside_interval']])
    validation=dict(status='PASS numerical reference checks; partial data-sheet fit, not hardware equality',
                    library_sha256=sha256(__import__('pathlib').Path(args.library)),
                    fit_sha256=sha256(HERE/'jensen-fit.json'),profiles_sha256=sha256(HERE/'profiles.json'),
                    script_sha256=sha256(__import__('pathlib').Path(__file__)),
                    source_sha256={name:sha256(HERE/name) for name in ('core.cpp','reference.py','fit.py')},
                    periodic_step_convergence=cases,independent_dop853=dict(reference=m,measurement=independent,
                        thd_error_db=smooth_error_db),causal_burst_stability=finite,power_and_loading=physical,
                    causal_high_rate_convergence=rate_checks,
                    data_sheet_scores=stats)
    write_json(HERE/'validation.json',validation)
    print(json.dumps(validation,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
