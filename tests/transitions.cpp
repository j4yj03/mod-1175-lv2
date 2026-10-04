// SPDX-License-Identifier: MIT — long switching/parking tests, not implementation mirroring.
#include "dsp/GreenStripe.hpp"
#include <cmath>
#include <iostream>

int main() {
    greenstripe::Processor processor(48000,true);
    greenstripe::Parameters p; p.colour=0; p.input=6;
    processor.setParameters(p);
    double previousL=0,previousR=0,peak=0,largestJump=0;
    unsigned checkedLinked=0,checkedOff=0;
    for (unsigned n=0;n<48000*3;++n) {
        if(n==12000) {p.stereoLink=false; processor.setParameters(p);}
        if(n==30000) {p.stereoLink=true; processor.setParameters(p);}
        if(n==48000) {p.compression=false; processor.setParameters(p);}
        if(n==66000) {p.compression=true; processor.setParameters(p);}
        if(n==84000) {p.enabled=false; processor.setParameters(p);}
        if(n==102000) {p.enabled=true; processor.setParameters(p);}
        if(n==120000) {p.stereoLink=false; processor.setParameters(p);}
        const double a=0.3*std::sin(6.283185307179586*67*n/48000);
        const double b=0.09*std::sin(6.283185307179586*97*n/48000);
        double l,r; processor.sample(a,b,l,r);
        if(!std::isfinite(l)||!std::isfinite(r)) return 1;
        peak=std::max(peak,std::max(std::abs(l),std::abs(r)));
        largestJump=std::max(largestJump,std::max(std::abs(l-previousL),std::abs(r-previousR)));
        if (n>33000 && n<48000) {
            if(processor.gainReduction(0)!=processor.gainReduction(1)) return 1;
            ++checkedLinked;
        }
        if ((n>51000&&n<66000)||(n>87000&&n<102000)) {
            if(processor.gainReduction(0)!=0||processor.gainReduction(1)!=0) return 1;
            ++checkedOff;
        }
        previousL=l; previousR=r;
    }
    std::cout << "Transitions/parking: peak=" << peak << " maximum_sample_jump=" << largestJump
              << " linked_samples=" << checkedLinked << " off_samples=" << checkedOff << '\n';
    return peak<1.0 && largestJump<0.02 && checkedLinked && checkedOff ? 0 : 1;
}
