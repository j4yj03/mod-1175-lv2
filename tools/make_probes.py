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


# Diskriminierungssuite "echter Kern vs. Effektmodell" (2026-10-08,
# MESSTECHNIK 1k.2); Stereo L=R, -2 dBFS entspricht 0.794 Amplitude wie im
# Matrixprogramm. Die Fabriken geben (generator, sekunden) zurueck und sind
# die gemeinsame Quelle fuer die Einzeldateien hier und das Kombi-Programm
# (tools/make_discrimination_program.py).
BURST_SPANS = ((0.5, 1.5), (2.5, 3.5), (4.5, 5.5), (6.5, 9.5))
LEVELS_20HZ = (-26, -20, -14, -8, -2)
CARRIER = 0.003


def _env(n, rate, begin, end):
    fade = 0.02 * rate
    local = n - begin
    length = end - begin
    if local < 0 or local >= length:
        return 0.0
    return min(1.0, local / fade, (length - local) / fade)


def remanenz_bursts(rate):
    def gen(n):
        for begin, end in BURST_SPANS:
            gain = _env(n, rate, round(begin * rate), round(end * rate))
            if gain:
                return 0.794 * gain * math.sin(2 * math.pi * 20 * n / rate) + CARRIER * math.sin(2 * math.pi * 20 * n / rate)
        return CARRIER * math.sin(2 * math.pi * 20 * n / rate)
    return gen, 10.0


def zweiton_im(rate):
    return (lambda n: 0.501 * math.sin(2 * math.pi * 60 * n / rate)
            + 0.050 * math.sin(2 * math.pi * 1000 * n / rate)), 8.0


def pegelreihe_20hz(rate):
    def gen(n):
        idx = min(4, n // (3 * rate))
        amp = 10 ** (LEVELS_20HZ[idx] / 20)
        return amp * math.sin(2 * math.pi * 20 * n / rate) * _env(n, rate, idx * 3 * rate, (idx + 1) * 3 * rate)
    return gen, 15.0


def dc_asymmetrie(rate):
    def gen(n):
        t = n / rate
        if t < 3:
            return 0.3 + 0.4 * math.sin(2 * math.pi * 1000 * n / rate) * _env(n, rate, 0, 3 * rate)
        if t < 6:
            return 0.4 * math.sin(2 * math.pi * 1000 * n / rate) * _env(n, rate, 3 * rate, 6 * rate)
        return 0.3
    return gen, 8.0


DISCRIMINATION_PROBES = (
    ('remanenz-bursts.wav', remanenz_bursts),
    ('zweiton-im.wav', zweiton_im),
    ('pegelreihe-20hz.wav', pegelreihe_20hz),
    ('dc-asymmetrie.wav', dc_asymmetrie),
)


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
    for name, factory in DISCRIMINATION_PROBES:
        gen, seconds = factory(rate)
        write(args.output/name, rate, 2, lambda n, g=gen: (g(n), g(n)), seconds)
    print('Generated '+str(8+len(DISCRIMINATION_PROBES))+' PCM24 probes at '+str(rate)+' Hz')


if __name__=='__main__': main()
