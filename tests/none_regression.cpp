// SPDX-License-Identifier: MIT — compare None against an independently saved previous tree.
#ifndef GS76_REFERENCE_HEADER
#error Define GS76_REFERENCE_HEADER to the previous GreenStripe.hpp
#endif
#define greenstripe reference_greenstripe
#include GS76_REFERENCE_HEADER
#undef greenstripe
#undef GREEN_STRIPE_DSP_HPP
#undef GREEN_STRIPE_MODEL_CONSTANTS_HPP
#undef GREEN_STRIPE_TRANSFORMER_MODELS_HPP
#include "dsp/GreenStripe.hpp"
#include <iostream>

int main() {
    unsigned count=0;
    for (bool stereo : {false,true}) for (double rate : {8000.0,44100.0,48000.0,96000.0})
        for (int os : {0,1,2}) for (int mode : {0,1,2,3,4,5}) {
            greenstripe::Processor now(rate,stereo);
            reference_greenstripe::Processor old(rate,stereo);
            greenstripe::Parameters p; reference_greenstripe::Parameters q;
            p.oversampling=q.oversampling=os; p.ratio=q.ratio=mode;
            p.input=q.input=12; p.colour=q.colour=mode%2 ? 100 : 0;
            now.setParameters(p); old.setParameters(q);
            for (unsigned n=0; n<8192; ++n) {
                if (n==2048) { p.stereoLink=q.stereoLink=false; p.output=q.output=-12; }
                if (n==4096) { p.oversampling=q.oversampling=(os+1)%3; p.compression=q.compression=false; }
                if (n==6144) { p.enabled=q.enabled=false; }
                if (n==2048||n==4096||n==6144) { now.setParameters(p); old.setParameters(q); }
                const double a=.3*std::sin(6.283185307179586*137*n/rate);
                const double b=.2*std::sin(6.283185307179586*53*n/rate);
                double nl,nr,ol,orr; now.sample(a,b,nl,nr); old.sample(a,b,ol,orr);
                if (nl!=ol || nr!=orr || now.gainReduction()!=old.gainReduction() || now.latency()!=old.latency()) {
                    std::cerr << "None regression rate=" << rate << " os=" << os << " mode=" << mode << " sample=" << n << '\n';
                    return 1;
                }
            }
            ++count;
        }
    std::cout << "None vs previous core: " << count << " cases, bit-equal audio/GR/latency\n";
}
