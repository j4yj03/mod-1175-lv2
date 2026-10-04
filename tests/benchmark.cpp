// SPDX-License-Identifier: MIT — host-dependent throughput, not a Dwarf claim.
#include "dsp/GreenStripe.hpp"
#include <chrono>
#include <iostream>

int main() {
    const unsigned count=48000;
    for (bool stereo : {false,true}) for (int mode : {0,4}) {
        greenstripe::Processor processor(48000,stereo);
        greenstripe::Parameters p; p.ratio=mode; p.input=6; processor.setParameters(p);
        double checksum=0,l,r;
        const auto start=std::chrono::steady_clock::now();
        for (unsigned i=0;i<count;++i) {
            const double x=0.25*std::sin(6.283185307179586*997*i/48000);
            processor.sample(x,x*0.5,l,r); checksum+=l+r;
        }
        const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        std::cout << (stereo?"Stereo":"Mono") << " mode=" << mode << " seconds_per_audio_second="
                  << elapsed << " ns_per_frame=" << elapsed*1e9/count << " checksum=" << checksum << '\n';
    }
}
