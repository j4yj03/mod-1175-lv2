#!/usr/bin/env python3
"""Exercise the actual native LV2 ABI via ctypes (no Lilv dependency)."""
import ctypes as C
import math
from pathlib import Path
import sys


class Descriptor(C.Structure):
    pass


Instantiate = C.CFUNCTYPE(C.c_void_p, C.POINTER(Descriptor), C.c_double, C.c_char_p, C.c_void_p)
Connect = C.CFUNCTYPE(None, C.c_void_p, C.c_uint32, C.c_void_p)
Activate = C.CFUNCTYPE(None, C.c_void_p)
Run = C.CFUNCTYPE(None, C.c_void_p, C.c_uint32)
Cleanup = C.CFUNCTYPE(None, C.c_void_p)
Descriptor._fields_ = [('uri', C.c_char_p), ('instantiate', Instantiate), ('connect', Connect),
                      ('activate', Activate), ('run', Run), ('deactivate', C.c_void_p),
                      ('cleanup', Cleanup), ('extension', C.c_void_p)]


def render(library, descriptor_index, rate, block, invalid=False, inplace=False, os_value=0, switch_at=None):
    pointer = library.lv2_descriptor(descriptor_index)
    d = pointer.contents
    stereo = descriptor_index == 1
    handle = d.instantiate(pointer, rate, b'./', C.pointer(C.c_void_p()))
    assert handle
    audio = [(C.c_float * block)() for _ in range(4 if stereo else 2)]
    controls = [C.c_float(v) for v in ([0,0,3,5,0,100,100,1,1,1] if stereo else [0,0,3,5,0,100,100,1,1])]
    latency = C.c_float()
    oversampling = C.c_float(0 if switch_at is not None else os_value)
    for i, buffer in enumerate(audio):
        output_index = 2 if stereo else 1
        source = audio[i-output_index] if inplace and i>=output_index else buffer
        d.connect(handle,i,C.cast(source,C.c_void_p))
    for i, value in enumerate(controls):
        d.connect(handle,len(audio)+i,C.byref(value))
    latency_port = len(audio)+len(controls)
    d.connect(handle,latency_port,C.byref(latency))
    d.connect(handle,latency_port+1,C.byref(oversampling))
    if invalid:
        controls[0].value = float('nan')
        controls[2].value = float('inf')
    d.activate(handle)
    d.run(handle,0)
    assert latency.value == (0 if switch_at is not None else (0 if os_value==0 else 3 if os_value==1 else 4)), 'Unexpected initial latency'
    output = []
    total=4096
    for offset in range(0,total,block):
        frames=min(block,total-offset)
        if switch_at is not None and offset>=switch_at and oversampling.value==0:
            oversampling.value=os_value
        for i in range(frames):
            audio[0][i]=0.2*math.sin(2*math.pi*1000*(i+offset)/rate)
            if stereo: audio[1][i]=0.08*math.sin(2*math.pi*777*(i+offset)/rate)
        if invalid and offset==0:
            audio[0][0]=float('nan'); audio[0][1]=float('inf')
        d.run(handle,frames)
        result = audio[0 if inplace else (2 if stereo else 1)]
        output.extend(float(result[i]) for i in range(frames))
    assert all(math.isfinite(x) for x in output)
    if switch_at is not None:
        assert latency.value == (3 if os_value==1 else 4), 'Latency did not follow oversampling switch'
    d.cleanup(handle)
    return output


def main():
    library=C.CDLL(str(Path(sys.argv[1]).resolve()))
    library.lv2_descriptor.argtypes=[C.c_uint32]
    library.lv2_descriptor.restype=C.POINTER(Descriptor)
    assert not library.lv2_descriptor(2)
    for index in (0,1):
        for rate in (44100,48000,96000):
            baseline=render(library,index,rate,1)
            for block in (64,128,256,511):
                assert render(library,index,rate,block)==baseline, 'Block-size-dependent output'
            assert render(library,index,rate,128,inplace=True)==baseline, 'In-place mismatch'
            render(library,index,rate,128,invalid=True)
            for os_value in (1,2):
                expected=render(library,index,rate,1,os_value=os_value)
                for block in (64,128,256,511):
                    assert render(library,index,rate,block,os_value=os_value)==expected, \
                        'Block-size-dependent output with oversampling'
                # Mid-stream switch: blocks aligned to the switch point only.
                switched=render(library,index,rate,512,os_value=os_value,switch_at=2048)
                for block in (64,128,256,512):
                    assert render(library,index,rate,block,os_value=os_value,switch_at=2048)==switched, \
                        'Oversampling transition is block-size dependent'
    print('LV2 ABI / zero block / in-place / finite / block invariance / oversampling latency + transitions: PASS')


if __name__=='__main__':
    main()
