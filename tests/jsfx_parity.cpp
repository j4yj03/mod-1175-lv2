// SPDX-License-Identifier: MIT
// Compile/load/render the real EEL2 program, then compare with the native core.
#include "ysfx.h"
#include "dsp/GreenStripe.hpp"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

static void logger(intptr_t, ysfx_log_level level, const char* message) {
    if (level==ysfx_log_error) std::cerr << message << '\n';
}
static double maximumError=0.0;

static bool runCase(const char* file, bool stereo, double rate, unsigned block,
                    greenstripe::Parameters p, unsigned fixture, unsigned oversampling=0) {
    p.oversampling=static_cast<int>(oversampling);
    ysfx_config_u config(ysfx_config_new());
    ysfx_set_log_reporter(config.get(),logger);
    ysfx_guess_file_roots(config.get(),file);
    ysfx_u fx(ysfx_new(config.get()));
    if (!ysfx_load_file(fx.get(),file,0) || !ysfx_compile(fx.get(),ysfx_compile_no_gfx)) return false;
    ysfx_set_sample_rate(fx.get(),rate); ysfx_set_block_size(fx.get(),block);
    ysfx_init(fx.get());
    const double values[]={p.input,p.output,p.attack,p.release,double(p.ratio),p.mix,p.colour,
                          double(p.compression),double(p.enabled),double(p.stereoLink)};
    for (unsigned i=0;i<10;++i) ysfx_slider_set_value(fx.get(),i,values[i],true);
    ysfx_slider_set_value(fx.get(),11,double(oversampling),true);
    greenstripe::Processor native(rate,stereo); native.setParameters(p);
    std::vector<float> inL(block),inR(block),outL(block),outR(block);
    const float* inputs[]={inL.data(),inR.data()}; float* outputs[]={outL.data(),outR.data()};
    double worst=0, square=0;
    unsigned total=fixture==4?32768:4096;
    for (unsigned done=0;done<total;done+=block) {
        unsigned n=std::min(block,total-done);
        if (fixture==2 && done==2048) {
            p.input=7; p.output=-3; p.attack=6; p.release=2; p.mix=43;
            p.colour=80; p.stereoLink=false; p.ratio=4;
            const double changes[]={p.input,p.output,p.attack,p.release,double(p.ratio),p.mix,p.colour,
                                     double(p.compression),double(p.enabled),double(p.stereoLink)};
            for (unsigned j=0;j<10;++j) ysfx_slider_set_value(fx.get(),j,changes[j],true);
            native.setParameters(p);
        }
        if (fixture==4 && (done==4096||done==8192||done==12288||done==16384||done==20480||done==24576||done==28672)) {
            if(done==4096)p.stereoLink=false;
            if(done==8192)p.stereoLink=true;
            if(done==12288)p.compression=false;
            if(done==16384){p.compression=true;p.colour=0;}
            if(done==20480)p.enabled=false;
            if(done==24576){p.enabled=true;p.colour=100;}
            if(done==28672)p.stereoLink=false;
            const double changes[]={p.input,p.output,p.attack,p.release,double(p.ratio),p.mix,p.colour,
                                     double(p.compression),double(p.enabled),double(p.stereoLink)};
            for (unsigned j=0;j<10;++j) ysfx_slider_set_value(fx.get(),j,changes[j],true);
            native.setParameters(p);
        }
        if (fixture==5 && done==2048) {
            p.oversampling=2;
            ysfx_slider_set_value(fx.get(),11,2,true);
            native.setParameters(p);
        }
        if (fixture==6 && done==2048) {
            p.oversampling=0;
            ysfx_slider_set_value(fx.get(),11,0,true);
            native.setParameters(p);
        }
        for (unsigned i=0;i<n;++i) {
            unsigned sample=done+i;
            double envelope=sample<700?0.01:sample<2600?0.42:0.003;
            inL[i]=fixture==1?(sample==0?0.5f:0.0f):static_cast<float>(envelope*std::sin(6.283185307179586*997*sample/rate));
            inR[i]=fixture==1?0.0f:static_cast<float>(0.13*std::sin(6.283185307179586*313*sample/rate));
            if (fixture==3 && sample<2)
                inL[i]=sample==0 ? std::numeric_limits<float>::quiet_NaN() : std::numeric_limits<float>::infinity();
        }
        ysfx_process_float(fx.get(),inputs,outputs,2,2,n);
        for (unsigned i=0;i<n;++i) {
            double l,r;
            native.sample(inL[i],stereo?inR[i]:inL[i],l,r);
            const double dl=outL[i]-static_cast<float>(l), dr=outR[i]-static_cast<float>(r);
            worst=std::max(worst,std::max(std::abs(dl),std::abs(dr)));
            square+=dl*dl+dr*dr;
            if (!std::isfinite(outL[i]) || !std::isfinite(outR[i])) return false;
        }
    }
    maximumError=std::max(maximumError,worst);
    if (worst>0.000002) {
        std::cerr << "Parity failed " << file << " rate=" << rate << " block=" << block
                  << " mode=" << p.ratio << " max=" << worst << " rms=" << std::sqrt(square/(2*total)) << '\n';
        std::cerr << "State JSFX charge=" << ysfx_read_var(fx.get(),"gs_engine.ctrlL.charge")
                  << " GR=" << ysfx_read_var(fx.get(),"gs_engine.grL")
                  << " native GR=" << native.gainReduction() << '\n';
        return false;
    }
    return true;
}

static bool checkPresets(const char* file) {
    ysfx_config_u config(ysfx_config_new()); ysfx_set_log_reporter(config.get(),logger);
    ysfx_u fx(ysfx_new(config.get()));
    if (!ysfx_load_file(fx.get(),file,0) || !ysfx_compile(fx.get(),ysfx_compile_no_gfx)) return false;
    ysfx_set_sample_rate(fx.get(),48000); ysfx_set_block_size(fx.get(),128); ysfx_init(fx.get());
    const std::string bankFile=std::string(file).substr(0,std::string(file).size()-5)+".rpl";
    ysfx_bank_u bank(ysfx_load_bank(bankFile.c_str()));
    if (!bank || bank->preset_count!=26) return false;
    std::vector<float> silence(128),l(128),r(128);
    const float* in[]={silence.data(),silence.data()}; float* out[]={l.data(),r.data()};
    for (unsigned i=0;i<bank->preset_count;++i) {
        if (!ysfx_load_state(fx.get(),bank->presets[i].state)) return false;
        ysfx_process_float(fx.get(),in,out,2,2,128);
        double values[10];
        for (unsigned j=0;j<10;++j) values[j]=ysfx_slider_get_value(fx.get(),j);
        ysfx_slider_set_value(fx.get(),10,i+1,true);
        ysfx_process_float(fx.get(),in,out,2,2,128);
        for (unsigned j=0;j<10;++j)
            if (values[j]!=ysfx_slider_get_value(fx.get(),j)) {
                std::cerr << "Bank/selector mismatch preset=" << i << " slider=" << j << '\n'; return false;
            }
        ysfx_slider_set_value(fx.get(),0,values[0]+0.1,true);
        ysfx_process_float(fx.get(),in,out,2,2,128);
        if (ysfx_slider_get_value(fx.get(),10)!=0) return false;
    }
    return true;
}

int main(int argc,char** argv) {
    if (argc!=3) { std::cerr << "Usage: jsfx_parity mono.jsfx stereo.jsfx\n"; return 2; }
    unsigned passed=0, failed=0;
    for (bool stereo : {false,true}) for (double rate : {44100.0,48000.0,96000.0})
        for (unsigned block : {1u,64u,128u,256u}) for (int mode : {0,1,2,3,4}) {
            greenstripe::Parameters p; p.ratio=mode;
            p.stereoLink=(mode!=2); p.mix=mode==3?35:100;
            if (!runCase(argv[stereo?2:1],stereo,rate,block,p,0)) ++failed;
            ++passed;
        }
    for (bool stereo : {false,true}) {
        greenstripe::Parameters p; p.colour=0; p.compression=false;
        if (!runCase(argv[stereo?2:1],stereo,48000,128,p,1)) ++failed;
        p.enabled=false;
        if (!runCase(argv[stereo?2:1],stereo,48000,128,p,1)) ++failed;
        passed+=2;
        p=greenstripe::Parameters();
        for (unsigned block : {1u,64u,128u,256u}) {
            if (!runCase(argv[stereo?2:1],stereo,48000,block,p,2)) ++failed;
            ++passed;
        }
        if (!runCase(argv[stereo?2:1],stereo,48000,128,p,3)) ++failed;
        ++passed;
        for (double rate : {44100.0,48000.0,96000.0}) for (unsigned block : {64u,128u,256u}) {
            if (!runCase(argv[stereo?2:1],stereo,rate,block,p,4)) ++failed;
            ++passed;
        }
        for (unsigned oversampling : {1u,2u}) for (double rate : {44100.0,48000.0,96000.0})
            for (unsigned block : {64u,128u}) for (int mode : {0,2,4}) {
                greenstripe::Parameters q; q.ratio=mode; q.stereoLink=(mode!=2); q.mix=mode==3?35:100;
                if (!runCase(argv[stereo?2:1],stereo,rate,block,q,0,oversampling)) ++failed;
                ++passed;
            }
        for (unsigned block : {64u,128u}) {
            if (!runCase(argv[stereo?2:1],stereo,48000,block,greenstripe::Parameters(),5)) ++failed;
            if (!runCase(argv[stereo?2:1],stereo,48000,block,greenstripe::Parameters(),6,2u)) ++failed;
            passed+=2;
        }
    }
    if (!checkPresets(argv[1]) || !checkPresets(argv[2])) {
        std::cerr << "Preset RPL/selector/custom-state test failed\n"; return 1;
    }
    if (failed) { std::printf("FAILURES: %u\n", failed); return 1; }
    std::cout << "JSFX/native parity: PASS (" << passed << " cases, max=" << maximumError << " FS)\n";
    std::cout << "JSFX instrument selector / RPL banks / Custom state: PASS (52 presets)\n";
}
