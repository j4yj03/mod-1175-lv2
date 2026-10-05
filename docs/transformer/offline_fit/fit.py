#!/usr/bin/env python3
"""Reproducible first offline interval fit, never changes the plugin DSP."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
from scipy.optimize import least_squares, brentq
import scipy

from reference import Reference, default_parameters, linear_response, hf_response

HERE = Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with path.open('w',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
        stream.write('\n')


def load_targets():
    with (HERE/'targets.csv').open(encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key in ('frequency_hz','input_dbu','value_low','value_high','value_center'):
            row[key] = float(row[key]) if row[key] else None
    return rows


def interval_residual(value, row, logarithmic=False):
    lo, hi, center = row['value_low'],row['value_high'],row['value_center']
    if logarithmic:
        value = math.log10(max(value,1e-12))
        lo = math.log10(lo) if lo else -12
        hi = math.log10(hi) if hi else 12
        center = math.log10(center) if center else None
        scale = max((hi-lo)*.5,.045) if lo > -10 else .1
    else:
        scale = max((hi-lo)*.5, .015 if row['unit']=='dB' else .06)
    outside = (value-lo)/scale if value<lo else (value-hi)/scale if value>hi else 0
    # Weak centering is declared; the interval violation is the main residual.
    middle = .15*(value-center)/scale if center is not None else 0
    return outside,middle


def fit_linear(rows, seed=20261005):
    p = default_parameters()
    p['hysteresis_enabled']=0
    relevant=[r for r in rows if r['quantity'] in ('response_db','dlp_deg') and r['split']=='train']
    reference_frequency=np.array([1000.0])
    rng=np.random.default_rng(seed)
    # ln(L0), ln(Lrelax), ln(frelax), ln(fHF), Q, shared DLP reference tau(us).
    bounds=([math.log(100),math.log(200),math.log(.02),math.log(70000),.45,0],
            [math.log(4000),math.log(2e6),math.log(500),math.log(220000),1.0,8])
    initial=np.array([math.log(1000),math.log(15000),math.log(20),math.log(108000),.66,2.3])
    trials=[]

    def unpack(x):
        params=p.copy()
        for key,index in (('lm_h',0),('relax_l_h',1),('relax_frequency_hz',2),('hf_frequency_hz',3)):
            params[key]=math.exp(x[index])
        params['hf_q']=x[4]
        return params

    def predict(params,tau,row):
        f=row['frequency_hz']
        hp=linear_response(params,np.array([f]))[0][0]
        if row['quantity']=='response_db':
            return 20*math.log10(abs(hp/linear_response(params,reference_frequency)[0][0]))
        return float(np.angle(hp,deg=True))+360*f*tau*1e-6

    def residual(x):
        params=unpack(x)
        values=[]
        for row in relevant:
            values.extend(interval_residual(predict(params,x[5],row),row))
        # Only data-fit and very weak prevention of an unbounded unused pole.
        return np.asarray(values)

    for index in range(8):
        x=initial.copy() if index==0 else np.array([
            rng.uniform(lo,hi) for lo,hi in zip(*bounds)])
        result=least_squares(residual,x,bounds=bounds,max_nfev=600,
                             ftol=1e-10,xtol=1e-10,gtol=1e-10)
        trial=dict(start=index,cost=float(result.cost),nfev=result.nfev,
                   parameters=unpack(result.x),dlp_reference_us=float(result.x[5]))
        trials.append(trial)
        print('linear',index,trial['cost'],trial['parameters'],flush=True)
    best=min(trials,key=lambda item:item['cost'])
    return best,trials


def fit_core(reference, rows, base, steps=512, maximum_evaluations=140, seed=20261005):
    targets=[r for r in rows if r['quantity']=='thd_percent' and r['split']=='train']
    rng=np.random.default_rng(seed)
    trials=[]
    families=[('polynomial',0,n,enabled) for n in (3,5,7,9) for enabled in (0,1)]
    families += [('frohlich',1,3,enabled) for enabled in (0,1)]
    families += [('rational',2,n,enabled) for n in (2,4,6,8) for enabled in (0,1)]
    for family,family_index,exponent,enabled in families:
        for start in range(2):
            # log(fluxscale), log(stop stiffness), stop spectrum slope.
            lo=[math.log(.012),math.log(1e-8),-.4]
            hi=[math.log(2.0),math.log(.02),1.3]
            x=[math.log(.08 if family_index else .10),math.log(.00005),.3]
            if start:
                x=[math.log(rng.uniform(.05,.25)),math.log(rng.uniform(1e-5,2e-4)),rng.uniform(0,.7)]
            if not enabled:
                lo=lo[:1]; hi=hi[:1]; x=x[:1]
            if family_index:
                lo += [math.log(.001)]; hi += [math.log(100)]; x += [math.log(1)]
            basep=base.copy()
            basep['family']=family_index
            basep['exponent']=exponent
            basep['hysteresis_enabled']=enabled

            def unpack(v):
                p=basep.copy()
                p['flux_scale_vs']=math.exp(v[0])
                p['hysteresis_stiffness_a_per_vs']=math.exp(v[1]) if enabled else 0
                p['hysteresis_slope']=v[2] if enabled else 0
                p['saturation_strength']=math.exp(v[-1]) if family_index else 1
                return p

            calls=0
            def residual(v):
                nonlocal calls
                calls+=1
                p=unpack(v)
                result=[]
                for row in targets:
                    m,_,_=reference.tone(p,row['frequency_hz'],row['input_dbu'],steps)
                    result.extend(interval_residual(m['thd_percent'],row,True))
                return np.array(result)
            before=time.monotonic()
            result=least_squares(residual,x,bounds=(lo,hi),max_nfev=maximum_evaluations,
                                 diff_step=2e-4,ftol=2e-5,xtol=2e-5,gtol=2e-5)
            trial=dict(family=family,exponent=exponent,hysteresis=bool(enabled),start=start,
                       train_cost=float(result.cost),nfev=result.nfev,model_calls=calls,
                       elapsed_s=time.monotonic()-before,parameters=unpack(result.x),
                       jacobian_singular_values=np.linalg.svd(result.jac,compute_uv=False).tolist())
            trials.append(trial)
            write_json(HERE/'fit-progress.json',trials)
            print('core',family,exponent,enabled,start,trial['train_cost'],
                  trial['parameters']['flux_scale_vs'],trial['parameters']['hysteresis_stiffness_a_per_vs'],
                  trial['parameters']['hysteresis_slope'],flush=True)
    best=min(trials,key=lambda t:t['train_cost'])
    return best,trials


def evaluate(reference,rows,parameters,tau,steps=2048):
    results=[]
    cache={}
    refgain=reference.tone(parameters,1000,4,steps)[0]['gain_primary_db']
    for row in rows:
        f=row['frequency_hz']; level=row['input_dbu']
        if row['quantity'] in ('response_db','dlp_deg'):
            hp=linear_response(parameters,np.array([f]))[0][0]
            if level is not None:
                key=(f,level)
                if key not in cache:cache[key]=reference.tone(parameters,f,level,steps)[0]
            if row['quantity']=='response_db' and level is not None:
                value=cache[(f,level)]['gain_primary_db']-refgain
            elif row['quantity']=='response_db':
                value=20*math.log10(abs(hp/linear_response(parameters,np.array([1000]))[0][0]))
            else:
                value=cache[(f,level)]['phase_primary_deg']+360*f*tau*1e-6
        else:
            key=(f,level)
            if key not in cache: cache[key]=reference.tone(parameters,f,level,steps)[0]
            metric={'gain_primary_db':'gain_primary_db','thd_percent':'thd_percent',
                    'zin_ohm':'input_impedance_ohm'}[row['quantity']]
            value=cache[key][metric]
        lo,hi=row['value_low'],row['value_high']
        entry=dict(**row,predicted=float(value),inside_interval=bool(lo<=value<=hi),
                   measurement_scope='linear_background_only_unknown_source_level' if level is None else
                                     'full_periodic_state_model')
        if row['quantity']=='thd_percent':
            nearest=max(lo,min(hi,value))
            entry['error_to_interval_db']=20*math.log10(max(value,1e-12)/max(nearest,1e-12))
        results.append(entry)
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',required=True)
    parser.add_argument('--steps',type=int,default=512)
    parser.add_argument('--max-nfev',type=int,default=140)
    parser.add_argument('--linear-only',action='store_true')
    parser.add_argument('--resume-linear',action='store_true')
    parser.add_argument('--refine-only',action='store_true')
    parser.add_argument('--dynamic-saturation',action='store_true')
    args=parser.parse_args()
    rows=load_targets()
    if args.resume_linear:
        linear=json.loads((HERE/'linear-fit.json').read_text())
        bestl,trials_l=linear['best'],linear['trials']
        for trial in [bestl]+trials_l:
            trial['parameters'].setdefault('high_field_l_ratio',0)
            trial['parameters'].setdefault('nonlinear_series_resistance_ohm',0)
    else:
        bestl,trials_l=fit_linear(rows)
        write_json(HERE/'linear-fit.json',dict(best=bestl,trials=trials_l))
    if args.linear_only:return
    reference=Reference(args.library)
    if args.dynamic_saturation:
        previous=json.loads((HERE/'jensen-fit.json').read_text())
        trials=previous['trials'];dynamic=[]
        candidates=[min((t for t in trials if t['hysteresis'] and t['family']==family),
                        key=lambda t:t['train_cost']) for family in ('frohlich','rational')]
        training=[r for r in rows if r['quantity']=='thd_percent' and r['split']=='train']
        for trial in candidates:
            for rstart in (5000,50000):
                p0=trial['parameters'].copy();p0.setdefault('high_field_l_ratio',0)
                def unpack(x):
                    p=p0.copy();p['flux_scale_vs']=math.exp(x[0]);p['hysteresis_stiffness_a_per_vs']=math.exp(x[1])
                    p['hysteresis_slope']=x[2];p['saturation_strength']=math.exp(x[3])
                    p['nonlinear_series_resistance_ohm']=math.exp(x[4]);return p
                def residual(x):
                    p=unpack(x);errors=[]
                    for row in training:
                        m=reference.tone(p,row['frequency_hz'],row['input_dbu'],args.steps)[0]
                        errors.extend(interval_residual(m['thd_percent'],row,True))
                    return np.array(errors)
                x=[math.log(p0['flux_scale_vs']),math.log(p0['hysteresis_stiffness_a_per_vs']),
                   p0['hysteresis_slope'],math.log(p0['saturation_strength']),math.log(rstart)]
                result=least_squares(residual,x,bounds=([math.log(.02),math.log(1e-8),-.4,math.log(.005),math.log(1)],
                                    [math.log(.3),math.log(.02),1.3,math.log(100),math.log(1e7)]),
                                    max_nfev=args.max_nfev,diff_step=2e-4,ftol=1e-6,xtol=1e-6,gtol=1e-6)
                item=dict(family=trial['family'],exponent=trial['exponent'],hysteresis=True,dynamic_saturation=True,
                          start=rstart,parameters=unpack(result.x),train_cost=float(result.cost),nfev=result.nfev,
                          jacobian_singular_values=np.linalg.svd(result.jac,compute_uv=False).tolist())
                dynamic.append(item);print('dynamic',trial['family'],rstart,item,flush=True)
        trials+=dynamic;best=min(trials,key=lambda t:t['train_cost'])
        best['parameters'].setdefault('nonlinear_series_resistance_ohm',0)
    elif args.refine_only:
        previous=json.loads((HERE/'jensen-fit.json').read_text())
        trials=previous['trials']
        refined=[]
        for trial in sorted((t for t in trials if t['hysteresis']),key=lambda t:t['train_cost'])[:4]:
            p0=trial['parameters']
            p0.setdefault('high_field_l_ratio',0)
            p0.setdefault('nonlinear_series_resistance_ohm',0)
            training=[r for r in rows if r['quantity']=='thd_percent' and r['split']=='train']
            family_index=p0['family']
            def unpack(x):
                p=p0.copy();p['flux_scale_vs']=math.exp(x[0])
                p['hysteresis_stiffness_a_per_vs']=math.exp(x[1]);p['hysteresis_slope']=x[2]
                p['saturation_strength']=math.exp(x[3]) if family_index else 1
                return p
            def residual(x):
                p=unpack(x);errors=[]
                for row in training:
                    metric=reference.tone(p,row['frequency_hz'],row['input_dbu'],args.steps)[0]
                    errors.extend(interval_residual(metric['thd_percent'],row,True))
                return np.array(errors)
            x=[math.log(p0['flux_scale_vs']),math.log(p0['hysteresis_stiffness_a_per_vs']),p0['hysteresis_slope']]
            lo=[math.log(.012),math.log(1e-8),-.4];hi=[math.log(2),math.log(.02),1.3]
            if family_index:
                x+=[math.log(p0['saturation_strength'])];lo+=[math.log(.001)];hi+=[math.log(100)]
            result=least_squares(residual,x,bounds=(lo,hi),
                    diff_step=1e-4,max_nfev=args.max_nfev,ftol=1e-7,xtol=1e-7,gtol=1e-7)
            refined.append(dict(**{k:v for k,v in trial.items() if k not in ('parameters','train_cost','refinement_steps')},
                                parameters=unpack(result.x),train_cost=float(result.cost),
                                refinement_steps=args.steps))
            print('refined',trial['family'],trial['exponent'],float(result.cost),flush=True)
        best=min(refined,key=lambda t:t['train_cost']);trials+=refined
    else:
        best,trials=fit_core(reference,rows,bestl['parameters'],args.steps,args.max_nfev)
    evaluation=evaluate(reference,rows,best['parameters'],bestl['dlp_reference_us'])
    onepercent=brentq(
        lambda level: reference.tone(best['parameters'],20,level,4096)[0]['thd_percent']-1,
        18,23,xtol=1e-7)
    write_json(HERE/'jensen-fit.json',dict(
        status='First offline data-sheet fit, reduced gray-box, not uniquely identified hardware',
        source_pdf_sha256='0e7a82774a90eee784897962ec3ed8ae17ac26122225a57596ef6c383f3bcc2d',
        targets_sha256=sha256(HERE/'targets.csv'),fixture_sha256=sha256(HERE/'fixture.json'),
        source_sha256={name:sha256(HERE/name) for name in ('core.cpp','reference.py','fit.py')},
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        library_sha256=sha256(Path(args.library)),linear=bestl,best=best,trials=trials,
        accepted_partial_fit=True,
        unresolved=['typical 20Hz/-0.04dB amplitude not exact; guaranteed interval is the gate',
                    'steep saturation intervals not all matched; disclose THD errors',
                    'magnetization/hysteresis not uniquely identified from datasheet'],
        dlp_reference_us=bestl['dlp_reference_us'],
        onepercent_20hz_primary_dbu=onepercent,
        target_definition_notes=['hf150k is one-sided: curve exits plot',
            'lf20 uses published guaranteed -0.15..0, with typical -0.04 weakly centered',
            'THD+N raster intervals are own estimates, 30Hz and plus14dBu held out'],
        periodic_measurement=dict(steps=2048,harmonics_max=31,
            initialization='antiperiodic half-cycle shooting, not a real-time reset'),
        evaluation=evaluation))
    with (HERE/'jensen-evaluation.csv').open('w',encoding='utf-8',newline='') as stream:
        keys=list(evaluation[0])+['error_to_interval_db']
        writer=csv.DictWriter(stream,fieldnames=list(dict.fromkeys(keys)))
        writer.writeheader();writer.writerows(evaluation)
    print('selected',best,flush=True)
    print('evaluation',[(r['target_id'],r['predicted'],r['inside_interval']) for r in evaluation],flush=True)


if __name__=='__main__':main()
