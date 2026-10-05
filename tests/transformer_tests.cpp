// SPDX-License-Identifier: MIT — signal-level acceptance of the fitted input stage.
#include "dsp/GreenStripe.hpp"
#include <chrono>
#include <complex>
#include <iostream>
#include <stdexcept>

static void require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}
static double thd(unsigned model, double rate, double amplitude, double frequency) {
    greenstripe::TransformerCoefficients c; c.prepare(rate,model);
    greenstripe::TransformerCore core; core.reset();
    const unsigned samples=static_cast<unsigned>(rate);
    std::complex<double> harmonics[16]={};
    // Two seconds settle, one second coherent measurement, no shooting.
    for (unsigned n=0; n<3*samples; ++n) {
        const double phase=6.283185307179586*frequency*n/rate;
        const double y=core.process(amplitude*std::sin(phase),c);
        require(std::isfinite(y),"Non-finite transformer tone");
        if (n>=2*samples) for (unsigned k=1; k<16; ++k)
            harmonics[k]+=y*std::complex<double>(std::cos(k*phase),-std::sin(k*phase));
    }
    double distortion=0;
    for (unsigned k=2; k<16; ++k) distortion+=std::norm(harmonics[k]);
    return 100*std::sqrt(distortion/std::norm(harmonics[1]));
}

int main() {
    try {
        for (unsigned m=0; m<3; ++m) {
            const double amplitude=greenstripe::dbGain(-14.0+6*m);
            for (double rate : {48000.0,96000.0,192000.0}) {
                const double value=thd(m,rate,amplitude,20);
                std::cout << "Transformer " << m+1 << " @" << rate << " 20-Hz anchor THD=" << value << "%\n";
                require(value>0.85 && value<1.15,"1% bass anchor outside tolerance");
            }
        }
        require(thd(3,48000,0.8,20)<0.001,"Symmetric reference must be linear");
        for (double rate : {8000.0,44100.0,48000.0,96000.0,384000.0})
            for (int os=0; os<3; ++os) for (int xf=1; xf<5; ++xf) {
                greenstripe::Parameters p; p.transformer=xf; p.oversampling=os;
                p.colour=0; p.stereoLink=false; p.input=12;
                greenstripe::Processor stereo(rate,true), mono(rate,false), outGain(rate,false), dry(rate,false);
                stereo.setParameters(p); mono.setParameters(p);
                p.output=12; outGain.setParameters(p); p.mix=0; dry.setParameters(p);
                greenstripe::Processor bypass(rate,false); p.enabled=false; bypass.setParameters(p);
                for (unsigned n=0; n<4096; ++n) {
                    const double x=0.4*std::sin(6.283185307179586*31*n/rate);
                    double sl,sr,ml,mr,ol,orr,dl,dr,bl,br;
                    stereo.sample(x,0,sl,sr); mono.sample(x,0,ml,mr);
                    outGain.sample(x,0,ol,orr); dry.sample(x,0,dl,dr); bypass.sample(x,0,bl,br);
                    require(sl==ml && sr==0,"Transformer channel coupling");
                    require(mono.gainReduction()==outGain.gainReduction(),"Output alters transformer/GR");
                    require(dl==bl,"Transformer leaks into dry/bypass");
                    require(std::isfinite(sl)&&std::abs(sl)<16,"Unstable transformer chain");
                }
            }
        // Repeated selection changes, oversampling changes, and long silence after stress.
        for (int xf=1; xf<5; ++xf) {
            greenstripe::Processor processor(48000,true);
            greenstripe::Parameters p; p.transformer=xf; p.colour=0; p.compression=false;
            processor.setParameters(p);
            double previous=0, maxJump=0;
            for (unsigned n=0; n<144000; ++n) {
                if (n<48000 && n%256==0) { p.transformer=(n/256)%5; processor.setParameters(p); }
                const double x=n<48000 ? 0.4*std::sin(6.283185307179586*31*n/48000) : 0;
                double l,r; processor.sample(x,-x,l,r);
                require(std::isfinite(l)&&std::isfinite(r),"Transformer transition non-finite");
                require(std::abs(l+r)<1e-10,"Transformer polarity symmetry lost");
                if (n<48000) maxJump=std::max(maxJump,std::abs(l-previous));
                previous=l;
                if (n==143999) require(std::abs(l)<0.002,"Transformer does not decay after silence");
            }
            require(maxJump<0.03,"Excessive model-switch discontinuity");
        }
        // Input sanitation and severe high-field operation remain bounded, with no audio clamp.
        for (int xf=1; xf<5; ++xf) for (int os=0; os<3; ++os) {
            greenstripe::Processor processor(8000,true);
            greenstripe::Parameters p; p.transformer=xf; p.oversampling=os; p.input=24; p.output=24;
            p.compression=false; p.colour=0; processor.setParameters(p);
            for (unsigned n=0; n<16000; ++n) {
                const double x=n<8000 ? 256*std::sin(6.283185307179586*7*n/8000) : 0;
                double l,r; processor.sample(x,-x,l,r);
                require(std::isfinite(l)&&std::isfinite(r)&&std::abs(l)<1000000,"High-field runaway");
            }
        }
        // Local throughput, not a target-device timing guarantee.
        for (int xf=0; xf<5; ++xf) {
            greenstripe::Processor processor(48000,true);
            greenstripe::Parameters p; p.transformer=xf; processor.setParameters(p);
            const auto start=std::chrono::steady_clock::now(); double checksum=0;
            for (unsigned n=0; n<48000; ++n) {
                double l,r; processor.sample(0.3*std::sin(6.283185307179586*53*n/48000),0.05,l,r); checksum+=l+r;
            }
            std::cout << "Local stereo OS-Off xf=" << xf << " seconds/audio_second="
                      << std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()
                      << " checksum=" << checksum << '\n';
        }
        std::cout << "Transformer signal / independence / bypass / transitions / stress: PASS\n";
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
