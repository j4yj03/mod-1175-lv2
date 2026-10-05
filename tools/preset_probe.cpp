// SPDX-License-Identifier: MIT — deterministic offline preset review, no audio files.
#include "dsp/GreenStripe.hpp"
#include <iomanip>
#include <iostream>

int main() {
    greenstripe::Parameters p;
    int compression, link, stereo, fixture;
    double level;
    std::cout << std::setprecision(17);
    while (std::cin >> p.input >> p.output >> p.attack >> p.release >> p.ratio
           >> p.mix >> p.colour >> compression >> link >> p.transformer
           >> p.oversampling >> stereo >> fixture >> level) {
        p.compression=compression!=0; p.stereoLink=link!=0;
        greenstripe::Processor processor(48000,stereo!=0);
        processor.setParameters(p);
        const double amplitude=greenstripe::dbGain(level);
        double peak=0, peakGR=0, sumGR=0, in2=0, out2=0;
        unsigned measured=0;
        for (unsigned n=0; n<57600; ++n) {
            const double t=n/48000.0;
            const double envelope=fixture==1 ? 1.0 : t<0.15 ? 0.125 : t<0.65 ? 1.0 : t<0.8 ? 0.125 : 0.0;
            const double a=amplitude*envelope*(fixture==1 ? std::sin(6.283185307179586*1000*t) :
                0.6*std::sin(6.283185307179586*53*t)+0.3*std::sin(6.283185307179586*997*t)+
                0.1*std::sin(6.283185307179586*6011*t));
            const double b=stereo ? (fixture==1 ? -a : amplitude*envelope*
                (0.4*std::sin(6.283185307179586*79*t)+0.2*std::sin(6.283185307179586*313*t))) : 0;
            double l,r; processor.sample(a,b,l,r);
            if (!std::isfinite(l)||!std::isfinite(r)||!std::isfinite(processor.gainReduction())) return 1;
            peak=std::max(peak,std::max(std::abs(l),std::abs(r)));
            peakGR=std::max(peakGR,std::max(-processor.gainReduction(),-processor.gainReduction(1)));
            if (n>=19200 && n<28800) {
                in2+=a*a; out2+=l*l; sumGR-=processor.gainReduction(); ++measured;
            }
        }
        if (!compression && peakGR!=0) return 1;
        std::cout << peak << ' ' << peakGR << ' ' << sumGR/measured << ' '
                  << 10*std::log10(out2/in2) << '\n';
    }
}
