// SPDX-License-Identifier: MIT — signal-level acceptance tests, no external DSP host.
#include "dsp/GreenStripe.hpp"
#include <iostream>
#include <limits>
#include <vector>
#include <stdexcept>

namespace {
void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
double tone(unsigned n, double amplitude, double hz = 1000, double fs = 48000) {
    return amplitude * std::sin(6.283185307179586 * hz * n / fs);
}
double rms(const std::vector<double>& signal, unsigned start) {
    double sum = 0;
    for (std::size_t i = start; i < signal.size(); ++i) sum += signal[i] * signal[i];
    return std::sqrt(sum / (signal.size() - start));
}
std::vector<double> render(greenstripe::Parameters p, double amplitude,
                           double fs = 48000, double frequency = 1000) {
    greenstripe::Processor processor(fs, false);
    processor.setParameters(p);
    std::vector<double> result(static_cast<unsigned>(fs * 0.8));
    for (unsigned i = 0; i < result.size(); ++i) {
        double b;
        processor.sample(tone(i, amplitude, frequency, fs), 0, result[i], b);
        require(std::isfinite(result[i]), "Non-finite audio");
    }
    return result;
}
}

int main() {
    try {
        greenstripe::Parameters p;
        p.colour = 0;
        double previous = 0;
        for (int ratio = 0; ratio < 4; ++ratio) {
            p.ratio = ratio;
            p.attack = 7; p.release = 1;
            const std::vector<double> low = render(p, 0.3);
            const std::vector<double> high = render(p, 0.6);
            const double change = greenstripe::gainDb(rms(high, 30000) / rms(low, 30000));
            const double measured = 6.020599913 / change;
            std::cout << "Ratio " << greenstripe::model::ratios[ratio] << ": " << measured << '\n';
            require(measured > greenstripe::model::ratios[ratio] * 0.70 &&
                    measured < greenstripe::model::ratios[ratio] * 1.35, "Static ratio outside tolerance");
            previous = measured;
        }
        require(previous > 10, "Limiter slope missing");

        // No colour/no compression is the identity resampling path, with unity RMS gain.
        p = greenstripe::Parameters(); p.colour = 0; p.compression = false;
        const std::vector<double> transparent = render(p, 0.1);
        require(std::abs(greenstripe::gainDb(rms(transparent, 30000) / (0.1/std::sqrt(2.0)))) < 0.001,
                "Identity-path gain is not unity");
        p.enabled = false;
        const std::vector<double> bypass = render(p, 0.1);
        for (unsigned i=0; i<bypass.size(); ++i)
            require(std::abs(bypass[i]-transparent[i])<1e-12, "Bypass must match phase-adjusted dry path");
        p.enabled = true; p.compression = true; p.mix = 0;
        require(render(p,0.1) == bypass, "0% Mix must match bypass response");

        // Output is downstream of the detector and must not alter the GR trajectory.
        greenstripe::Processor a(48000,false), b(48000,false);
        p = greenstripe::Parameters(); a.setParameters(p); p.output=12; b.setParameters(p);
        for (unsigned i=0; i<20000; ++i) {
            double al, ar, bl, br;
            a.sample(tone(i,0.3),0,al,ar); b.sample(tone(i,0.3),0,bl,br);
            require(a.gainReduction()==b.gainReduction(), "Output modifies compression");
        }

        // Dual-mono audio independence, and linked common gain for opposite polarity.
        greenstripe::Processor stereo(48000,true), mono(48000,false), linked(48000,true);
        p=greenstripe::Parameters(); p.colour=0; p.stereoLink=false;
        stereo.setParameters(p); mono.setParameters(p); p.stereoLink=true; linked.setParameters(p);
        for (unsigned i=0; i<20000; ++i) {
            double sl,sr,ml,mr,ll,lr;
            const double input=tone(i,0.2);
            stereo.sample(input,tone(i,0.8,777),sl,sr); mono.sample(input,0,ml,mr);
            require(sl==ml,"Dual-mono channel coupling");
            linked.sample(input,-input,ll,lr);
            require(std::abs(ll+lr)<1e-10,"Opposite-polarity stereo cancelled or changed gain");
            require(linked.gainReduction(0)==linked.gainReduction(1),"Linked envelopes differ");
        }

        // All Buttons, silence, extreme controls, and invalid input stay bounded/finite.
        for (double rate : {44100.0,48000.0,96000.0}) {
            greenstripe::Processor processor(rate,true);
            p=greenstripe::Parameters(); p.input=24; p.output=24; p.ratio=4; p.attack=7; p.release=7;
            processor.setParameters(p);
            for (unsigned i=0; i<30000; ++i) {
                double l,r;
                const double input=i<10000 ? tone(i,3,43,rate) : 0;
                processor.sample(input,-input,l,r);
                require(std::isfinite(l)&&std::isfinite(r),"Extreme controls unstable");
                require(std::abs(l)<10000&&std::abs(r)<10000,"Output runaway");
            }
            double l,r;
            processor.sample(std::numeric_limits<double>::quiet_NaN(),
                std::numeric_limits<double>::infinity(),l,r);
            require(std::isfinite(l)&&std::isfinite(r),"Invalid-input sanitation failed");
            processor.reset(); processor.setParameters(p); processor.sample(0,0,l,r);
            require(l==0&&r==0,"Silence/reset creates offset");
        }
        // Approximation is odd, bounded and has a matching derivative near biases.
        for (double x=-4.9; x<5; x+=0.01) {
            require(std::abs(greenstripe::softClip(x))<=1.001,"Shaper unbounded");
            require(std::abs(greenstripe::softClip(x)+greenstripe::softClip(-x))<1e-12,"Shaper not odd");
        }
        for (double x : {0.0,0.025,0.04,0.06}) {
            const double numerical=(greenstripe::softClip(x+1e-6)-greenstripe::softClip(x-1e-6))/2e-6;
            require(std::abs(numerical-greenstripe::clipSlope(x))<1e-7,"Shaper derivative mismatch");
        }
        for (double input : {-20.0,-1.0,-0.1,0.0,0.1,1.0,20.0})
            for (double charge : {0.0,0.2,2.0,20.0,1000.0}) {
                const double u=input*0.08;
                const double c=greenstripe::qBase()-1+charge;
                const double v=greenstripe::fet(input,charge,1,1)*0.08/greenstripe::qBase();
                const double residual=v+c*(v-0.32*v*v/(1+std::abs(v)))-u;
                require(std::abs(residual)<1e-10*(1+std::abs(u)),"FET closed-form KCL residual");
            }
        std::cout << "DSP acceptance tests: PASS\n";
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
