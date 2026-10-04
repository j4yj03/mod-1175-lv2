#!/usr/bin/env python3
"""Generate repeatable PCM24 burst/step/music-independent probes; no numpy needed."""
import argparse
import math
from pathlib import Path
import random
import wave


def write(path,rate,channels,generator,seconds):
    data=bytearray()
    for n in range(round(rate*seconds)):
        frame=generator(n)
        if channels==1: frame=(frame,)
        for value in frame:
            integer=max(-8388608,min(8388607,round(value*8388607)))
            data.extend(integer.to_bytes(3,'little',signed=True))
    with wave.open(str(path),'wb') as wav:
        wav.setnchannels(channels); wav.setsampwidth(3); wav.setframerate(rate); wav.writeframes(data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path); parser.add_argument('--rate',type=int,default=48000)
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True); rate=args.rate
    tone=lambda n,hz: math.sin(2*math.pi*hz*n/rate)
    write(args.output/'silence.wav',rate,1,lambda n:0,3)
    write(args.output/'impulse.wav',rate,1,lambda n:0.5 if n==rate//4 else 0,2)
    write(args.output/'level-steps.wav',rate,1,lambda n:10**((-48,-36,-24,-12,-6,-36)[min(5,n//rate)]/20)*tone(n,1000),6)
    write(args.output/'short-long-bursts.wav',rate,1,lambda n:(0.4 if (0.5<=n/rate<0.51 or 2<=n/rate<3) else 0.003)*tone(n,1000),7)
    write(args.output/'bass-burst.wav',rate,1,lambda n:(0.4 if 0.5<=n/rate<2 else 0.003)*tone(n,50),5)
    write(args.output/'stereo-unbalanced.wav',rate,2,lambda n:(0.4*tone(n,1000),0.04*tone(n,777)),4)
    write(args.output/'stereo-antiphase.wav',rate,2,lambda n:(0.2*tone(n,1000),-0.2*tone(n,1000)),4)
    rng=random.Random(1176)
    write(args.output/'deterministic-noise.wav',rate,2,lambda n:(rng.uniform(-0.2,0.2),rng.uniform(-0.2,0.2)),4)
    print('Generated 8 PCM24 probes at '+str(rate)+' Hz')


if __name__=='__main__': main()
