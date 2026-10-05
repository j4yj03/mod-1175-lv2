#!/usr/bin/env python3
"""Render exact-state high-rate previews and plot fit/profile evidence."""
import argparse
import csv
import json
import math
import struct
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import resample_poly

from fit import HERE,load_targets,write_json,sha256
from reference import Reference,linear_response


def float_wav(path,audio,rate):
    x=np.asarray(audio,dtype='<f4')
    if x.ndim==1:x=x[:,None]
    channels=x.shape[1];payload=x.tobytes()
    fmt=struct.pack('<HHIIHH',3,channels,rate,rate*channels*4,channels*4,32)
    with path.open('wb') as stream:
        stream.write(b'RIFF'+struct.pack('<I',36+len(payload))+b'WAVE')
        stream.write(b'fmt '+struct.pack('<I',16)+fmt+b'data'+struct.pack('<I',len(payload))+payload)


def test_signal(rate):
    duration=12.0;t=np.arange(int(rate*duration))/rate
    signal=np.zeros_like(t)
    # Three 20/50/100 Hz tone levels per section, no post-render normalization.
    for section,frequency in ((0,20),(3,50),(6,100)):
        for index,dbfs in enumerate((-18,-8,-2)):
            start=section+index+.05;stop=section+index+.85
            active=(t>=start)&(t<stop);u=t[active]-start
            ramp=np.minimum(1,u/.02)*np.minimum(1,(stop-t[active])/.02)
            signal[active]=10**(dbfs/20)*np.sin(2*np.pi*frequency*u)*ramp
    active=(t>=9)&(t<11.5);u=t[active]-9
    spectrum=np.sin(2*np.pi*80*u)+.45*np.sin(2*np.pi*240*u)+.25*np.sin(2*np.pi*1200*u)
    envelope=.55+.45*np.sin(2*np.pi*2*u)**2
    ramp=np.minimum(1,u/.02)*np.minimum(1,(11.5-t[active])/.05)
    signal[active]=.55*spectrum*envelope*ramp
    return t,signal


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',required=True)
    args=parser.parse_args()
    for sub in ('plots','audio'):(HERE/sub).mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.grid':True,'grid.alpha':.25,'svg.hashsalt':'gs76-first-fit'})
    reference=Reference(args.library)
    fit=json.loads((HERE/'jensen-fit.json').read_text())
    profiles=json.loads((HERE/'profiles.json').read_text())['profiles']
    rows=load_targets();base=fit['best']['parameters']
    # Curves: show target intervals and continuous model, with validation markers.
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    f=np.geomspace(.2,200000,500)
    hp=linear_response(base,f)[0];ref=linear_response(base,np.array([1000]))[0][0]
    axes[0].semilogx(f,20*np.log10(abs(hp/ref)),color='#236c40',label='linearer Hintergrund (Subaudio-Pegel unbekannt)')
    measured_f=np.geomspace(20,200000,90)
    gain1k=reference.tone(base,1000,4,2048)[0]['gain_primary_db']
    measured_gain=[reference.tone(base,float(freq),4,2048)[0]['gain_primary_db']-gain1k for freq in measured_f]
    axes[0].semilogx(measured_f,measured_gain,'--',label='vollständiger Zustand, +4 dBu')
    for row in rows:
        if row['quantity']=='response_db' and row['value_center'] is not None:
            c=row['value_center'];axis=axes[0]
            axis.errorbar(row['frequency_hz'],c,yerr=[[c-row['value_low']],[row['value_high']-c]],
                          fmt='o' if row['split']=='train' else 's',color='#bd6b17',capsize=2)
    axes[0].set_ylim(-8,1);axes[0].set_xlabel('Frequenz (Hz)');axes[0].set_ylabel('rel. Amplitude (dB)');axes[0].legend(fontsize=7)
    f=np.geomspace(20,20000,200);h=linear_response(base,f)[0]
    axes[1].semilogx(f,np.angle(h,deg=True)+360*f*fit['dlp_reference_us']*1e-6,label='Modell-DLP')
    fullphase=[reference.tone(base,float(freq),4,2048)[0]['phase_primary_deg']+
               360*float(freq)*fit['dlp_reference_us']*1e-6 for freq in f[::5]]
    axes[1].semilogx(f[::5],fullphase,'--',label='DLP vollständiger Zustand')
    for row in rows:
        if row['quantity']=='dlp_deg':
            c=row['value_center'];axes[1].errorbar(row['frequency_hz'],c,
                yerr=[[c-row['value_low']],[row['value_high']-c]],
                fmt='o' if row['split']=='train' else 's',color='#bd6b17',capsize=2)
    axes[1].set_xlabel('Frequenz (Hz)');axes[1].set_ylabel('Abweichung von linearer Phase (°)');axes[1].legend(fontsize=7)
    fig.suptitle('Erster Datenblattfit; Kreise Training, Quadrate zurückgehalten')
    fig.tight_layout();fig.savefig(HERE/'plots/linear-fit.svg',metadata={'Date':None});plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11,4))
    curve_rows=[]
    for frequency,color in ((20,'#236c40'),(30,'#bd6b17'),(50,'#3066a0')):
        levels=np.linspace(-25,30,80);thd=[]
        for level in levels:
            m=reference.tone(base,frequency,float(level),2048)[0]
            thd.append(m['thd_percent']);curve_rows.append(dict(kind='jensen',frequency_hz=frequency,
                                                              input_dbu=float(level),**m))
        axes[0].semilogy(levels,thd,color=color,label=f'{frequency} Hz')
        for row in rows:
            if row['quantity']=='thd_percent' and row['frequency_hz']==frequency and row['target_id'].startswith('t'):
                center=row['value_center'];axes[0].errorbar(row['input_dbu'],center,
                    yerr=[[center-row['value_low']],[row['value_high']-center]],
                    fmt='o' if row['split']=='train' else 's',color=color,capsize=2)
    for level,color in ((4,'#236c40'),(14,'#bd6b17'),(20,'#3066a0')):
        frequencies=np.geomspace(20,1000,70);thd=[]
        for freq in frequencies:
            m=reference.tone(base,float(freq),level,2048)[0];thd.append(m['thd_percent'])
        axes[1].loglog(frequencies,thd,color=color,label=f'{level:+} dBu')
        for row in rows:
            if row['quantity']=='thd_percent' and row['input_dbu']==level and row['target_id'].startswith('f') and row['value_center']:
                c=row['value_center'];axes[1].errorbar(row['frequency_hz'],c,
                    yerr=[[c-row['value_low']],[row['value_high']-c]],
                    fmt='o' if row['split']=='train' else 's',color=color,capsize=2)
    axes[0].set_ylim(.001,2);axes[1].set_ylim(.0001,2)
    axes[0].set_xlabel('Primärpegel (dBu RMS)');axes[1].set_xlabel('Frequenz (Hz)')
    for axis in axes:axis.set_ylabel('THD Modell / THD+N Zielbereiche (%)');axis.legend()
    fig.suptitle('Stationärer Klirrfit, einschließlich sichtbarer Restabweichungen')
    fig.tight_layout();fig.savefig(HERE/'plots/nonlinear-fit.svg',metadata={'Date':None});plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for (name,entry),color in zip(profiles.items(),('#3066a0','#bd6b17','#236c40')):
        p=entry['parameters'];f=np.geomspace(20,20000,300)
        response=linear_response(p,f)[0]/linear_response(p,np.array([1000]))[0][0]
        axes[0].semilogx(f,20*np.log10(abs(response)),label=name,color=color)
        dbfs=[];thd=[]
        for level in np.linspace(-10,26,65):
            m=reference.tone(p,20,float(level),2048)[0]
            dbfs.append(20*math.log10(m['source_rms_v']*math.sqrt(2)/entry['source_volts_per_fs']))
            thd.append(m['thd_percent'])
        axes[1].semilogy(dbfs,thd,label=name,color=color)
    axes[0].set_xlabel('Frequenz (Hz)');axes[0].set_ylabel('relative lineare Amplitude (dB)')
    axes[1].set_xlabel('digitaler Quellpegel, Sinus Peak (dBFS)');axes[1].set_ylabel('THD bei 20 Hz (%)')
    axes[1].set_ylim(.001,40)
    for axis in axes:axis.legend()
    fig.suptitle('Eigene Profile: 60s warm, 80s ausgewogen, 00s clean')
    fig.tight_layout();fig.savefig(HERE/'plots/profiles.svg',metadata={'Date':None});plt.close(fig)

    rate=768000;output_rate=48000;t,input_signal=test_signal(rate)
    input48=resample_poly(input_signal,1,16)
    float_wav(HERE/'audio/00-input.wav',input48,output_rate)
    assets=[];waves={'time_s':t[::16],'input':input48}
    for name,entry in profiles.items():
        voltage=input_signal*entry['source_volts_per_fs']
        output,diag=reference.render(entry['parameters'],voltage,rate,True)
        # Explicit fixed gain compensation chosen in create_profiles.py.
        audio=output/entry['source_volts_per_fs']*entry['fixed_output_normalization']
        sampled=resample_poly(audio,1,16)
        float_wav(HERE/f'audio/{name}-output.wav',sampled,output_rate)
        float_wav(HERE/f'audio/{name}-AB-input-output.wav',np.column_stack((input48,sampled)),output_rate)
        assets.append(dict(profile=name,source_rate_hz=rate,audio_rate_hz=output_rate,
                           frames=len(sampled),peak_fs=float(np.max(abs(sampled))),
                           peak_difference_fs=float(np.max(abs(sampled-input48))),
                           clipping_applied=False,post_peak_normalization=False,
                           wav_sha256=sha256(HERE/f'audio/{name}-output.wav')))
        waves[name]=sampled;waves[name+'__flux_vs']=diag[::16,1]
    np.savez_compressed(HERE/'preview-waveforms.npz',**waves)
    fig,axes=plt.subplots(2,1,figsize=(10,6))
    time48=np.arange(len(input48))/output_rate
    selected=(time48>.06)&(time48<.84)
    # Last tone of first section is near full-level 20Hz.
    selected=(time48>2.65)&(time48<2.8)
    axes[0].plot(time48[selected],input48[selected],label='Input',color='#777777')
    for name in profiles:
        axes[0].plot(time48[selected],waves[name][selected],label=name)
        axes[1].plot(time48,waves[name]-input48,label=name)
    axes[0].set_ylabel('Amplitude FS');axes[1].set_ylabel('Ausgang minus Eingang (FS)')
    axes[1].set_xlabel('Zeit (s)');axes[0].legend();axes[1].legend()
    fig.tight_layout();fig.savefig(HERE/'plots/preview.svg',metadata={'Date':None});plt.close(fig)
    write_json(HERE/'preview-manifest.json',dict(
        render_script_sha256=sha256(Path(__file__)),profiles_sha256=sha256(HERE/'profiles.json'),
        assets=assets,probe_description='20/50/100Hz bursts -18/-8/-2dBFS plus 80/240/1200Hz multitone',
        stereo_AB='left original input, right fixed-normalized profile output; no phase alignment',
        resampling='scipy.signal.resample_poly, Kaiser default antialias FIR, 768k -> 48k',
        listening_test='not performed'))
    with (HERE/'jensen-sweep.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(curve_rows[0]));writer.writeheader();writer.writerows(curve_rows)
    print('Plots, high-rate-rendered WAV previews and raw NPZ evidence written.',flush=True)


if __name__=='__main__':main()
