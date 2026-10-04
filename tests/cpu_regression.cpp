// SPDX-License-Identifier: MIT
// Optional before/after reference; the old header stays outside the repository.
// Build with -DGS76_REFERENCE_HEADER='"/absolute/previous/src/dsp/GreenStripe.hpp"'.
#ifndef GS76_REFERENCE_HEADER
#error Define GS76_REFERENCE_HEADER to an independently saved previous core
#endif
#define greenstripe reference_greenstripe
#include GS76_REFERENCE_HEADER
#undef greenstripe
#undef GREEN_STRIPE_DSP_HPP
#undef GREEN_STRIPE_MODEL_CONSTANTS_HPP
#include "dsp/GreenStripe.hpp"
#include <algorithm>
#include <cmath>
#include <iostream>

int main() {
    double maximumAudio = 0, maximumGR = 0;
    unsigned cases = 0;
    for (double rate : {8000.0,44100.0,48000.0,96000.0})
        for (bool stereo : {false,true}) for (int mode : {0,1,2,3,4})
            for (double colour : {0.0,100.0}) {
                greenstripe::Processor now(rate,stereo);
                reference_greenstripe::Processor old(rate,stereo);
                greenstripe::Parameters p; reference_greenstripe::Parameters q;
                p.colour=q.colour=colour; p.ratio=q.ratio=mode;
                p.attack=q.attack=7; p.release=q.release=7;
                p.stereoLink=q.stereoLink=mode!=2;
                p.input=q.input=mode==4?12:0; p.output=q.output=-3;
                // The legacy reference core always runs 4x internally; match it.
                p.oversampling=2;
                now.setParameters(p); old.setParameters(q);
                const unsigned count=static_cast<unsigned>(rate*1.2);
                for (unsigned n=0;n<count;++n) {
                    const double t=n/rate;
                    const double envelope=t<0.1?0.005:t<0.32?0.8:t<0.7?0.012:0;
                    const double a=envelope*(0.7*std::sin(6.283185307179586*127*t)+0.3*std::sin(6.283185307179586*1031*t));
                    const double b=envelope*(0.4*std::sin(6.283185307179586*313*t)+0.2*std::sin(6.283185307179586*61*t));
                    double nl,nr,ol,orr;
                    now.sample(a,b,nl,nr); old.sample(a,b,ol,orr);
                    if (!std::isfinite(nl)||!std::isfinite(nr)) return 1;
                    maximumAudio=std::max(maximumAudio,std::max(std::abs(nl-ol),std::abs(nr-orr)));
                    maximumGR=std::max(maximumGR,std::max(std::abs(now.gainReduction(0)-old.gainReduction(0)),
                                                         std::abs(now.gainReduction(1)-old.gainReduction(1))));
                }
                ++cases;
            }
    std::cout << "Before/after stationary burst regression: " << cases << " cases; peak_audio="
              << maximumAudio << " FS; peak_GR=" << maximumGR << " dB\n";
    return maximumAudio<=0.000002 && maximumGR<=0.00002 ? 0 : 1;
}
