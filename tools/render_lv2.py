#!/usr/bin/env python3
"""Offline-render PCM16/24/32 WAV through native LV2; output IEEE float WAV.

No resampling, normalization, lookahead or automatic alignment is performed.
This loads a binary for the current machine, not a Dwarf binary on x86.
"""
import argparse
import ctypes as C
import importlib.util
import json
from pathlib import Path
import struct
import wave

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lv2_test_host',ROOT/'tests/test_lv2.py')
host=importlib.util.module_from_spec(spec); spec.loader.exec_module(host)


def read_pcm(path):
    with wave.open(str(path),'rb') as wav:
        channels=wav.getnchannels(); rate=wav.getframerate(); width=wav.getsampwidth()
        if channels not in (1,2) or width not in (2,3,4) or wav.getcomptype()!='NONE':
            raise ValueError('Expected mono/stereo PCM16/24/32 WAV')
        raw=wav.readframes(wav.getnframes())
    scale=float(1 << (8*width-1))
    values=[int.from_bytes(raw[i:i+width],'little',signed=True)/scale for i in range(0,len(raw),width)]
    return rate,channels,values


def write_float(path,rate,channels,values):
    data=struct.pack('<'+'f'*len(values),*values)
    fmt=struct.pack('<HHIIHH',3,channels,rate,rate*channels*4,channels*4,32)
    fact=struct.pack('<I',len(values)//channels)
    contents=b'WAVE'+b'fmt '+struct.pack('<I',len(fmt))+fmt+b'fact'+struct.pack('<I',4)+fact+b'data'+struct.pack('<I',len(data))+data
    path.write_bytes(b'RIFF'+struct.pack('<I',len(contents))+contents)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary',type=Path); parser.add_argument('input',type=Path); parser.add_argument('output',type=Path)
    parser.add_argument('--mono',action='store_true'); parser.add_argument('--preset',type=int,default=0)
    parser.add_argument('--block',type=int,default=128)
    parser.add_argument('--set',action='append',default=[],metavar='SYMBOL=VALUE')
    args=parser.parse_args()
    if args.block<1: raise SystemExit('Block must be positive')
    rate,ch,signal=read_pcm(args.input)
    stereo=not args.mono and ch==2
# read_text() without an encoding uses the locale encoding, which on Windows
#     is cp1252 and mangles the UTF-8 dashes in data/*.json.
    parameters=json.loads((ROOT/'data/parameters.json').read_text(encoding='utf-8'))
    values={p['symbol']:p['default'] for p in parameters}
    if args.preset:
        presets=json.loads((ROOT/'data/presets.json').read_text(encoding='utf-8'))
        if not 1<=args.preset<=len(presets): raise SystemExit('Invalid preset number')
        selected=presets[args.preset-1]; values.update({k:selected[k] for k in values if k in selected})
        values['stereo_link']=selected['link']
    for assignment in args.set:
        key,value=assignment.split('=',1)
        if key not in values: raise SystemExit('Unknown parameter '+key)
        values[key]=float(value)
    library=C.CDLL(str(args.binary.resolve())); library.lv2_descriptor.argtypes=[C.c_uint32]
    library.lv2_descriptor.restype=C.POINTER(host.Descriptor)
    pointer=library.lv2_descriptor(1 if stereo else 0); d=pointer.contents
    handle=d.instantiate(pointer,rate,b'./',C.pointer(C.c_void_p()))
    if not handle: raise SystemExit('Cannot instantiate native plugin')
    audio=[(C.c_float*args.block)() for _ in range(4 if stereo else 2)]
    relevant=[p for p in parameters if stereo or not p.get('stereo_only')]
    existing=[p for p in relevant if not p.get('lv2_append')]
    appended=[p for p in relevant if p.get('lv2_append')]
    controls=[C.c_float(values[p['symbol']]) for p in existing]
    extra=[C.c_float(values[p['symbol']]) for p in appended]
    latency=C.c_float()
    for i,buffer in enumerate(audio): d.connect(handle,i,C.cast(buffer,C.c_void_p))
    for i,value in enumerate(controls): d.connect(handle,len(audio)+i,C.byref(value))
    latency_index=len(audio)+len(controls)
    d.connect(handle,latency_index,C.byref(latency))
    for i,value in enumerate(extra): d.connect(handle,latency_index+1+i,C.byref(value))
    d.activate(handle)
    output=[]; total=len(signal)//ch
    for offset in range(0,total,args.block):
        frames=min(args.block,total-offset)
        for i in range(frames):
            audio[0][i]=signal[(offset+i)*ch]
            if stereo: audio[1][i]=signal[(offset+i)*ch+1]
        d.run(handle,frames)
        for i in range(frames):
            output.append(float(audio[2 if stereo else 1][i]))
            if stereo: output.append(float(audio[3][i]))
    d.cleanup(handle)
    write_float(args.output,rate,2 if stereo else 1,output)
    print(json.dumps(dict(input=str(args.input),output=str(args.output),rate=rate,
                          channels=2 if stereo else 1,frames=total,nominal_latency=latency.value,parameters=values),indent=2))


if __name__=='__main__': main()
