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
    if (fixture==7) p.transformer=1;
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
    ysfx_slider_set_value(fx.get(),12,double(p.transformer),true);
    greenstripe::Processor native(rate,stereo); native.setParameters(p);
    std::vector<float> inL(block),inR(block),outL(block),outR(block);
    const float* inputs[]={inL.data(),inR.data()}; float* outputs[]={outL.data(),outR.data()};
    double worst=0, square=0;
    unsigned total=fixture==4||fixture==7?32768:4096;
    for (unsigned done=0;done<total;done+=block) {
        unsigned n=std::min(block,total-done);
        if (fixture==7 && done%4096==0) {
            const int selections[]={1,2,3,4,0,3,1,0};
            p.transformer=selections[done/4096];
            ysfx_slider_set_value(fx.get(),12,p.transformer,true);
            native.setParameters(p);
        }
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
            inL[i]=fixture==1?(sample==0?0.5f:0.0f):static_cast<float>(envelope*std::sin(6.283185307179586*(p.transformer?37:997)*sample/rate));
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
                  << " mode=" << p.ratio << " xf=" << p.transformer << " fixture=" << fixture
                  << " max=" << worst << " rms=" << std::sqrt(square/(2*total)) << '\n';
        std::cerr << "State JSFX charge=" << ysfx_read_var(fx.get(),"gs_engine.ctrlL.charge")
                  << " GR=" << ysfx_read_var(fx.get(),"gs_engine.grL")
                  << " native GR=" << native.gainReduction() << '\n';
        return false;
    }
    return true;
}

static bool checkPresets(const char* file, unsigned &loaded) {
    bool signalParity=true;
    ysfx_config_u config(ysfx_config_new()); ysfx_set_log_reporter(config.get(),logger);
    ysfx_u fx(ysfx_new(config.get()));
    if (!ysfx_load_file(fx.get(),file,0) || !ysfx_compile(fx.get(),ysfx_compile_no_gfx)) return false;
    ysfx_set_sample_rate(fx.get(),48000); ysfx_set_block_size(fx.get(),128); ysfx_init(fx.get());
    const std::string bankFile=std::string(file).substr(0,std::string(file).size()-5)+".rpl";
    ysfx_bank_u bank(ysfx_load_bank(bankFile.c_str()));
    // The expected count comes from the preset selector's own range instead of
    // a hardcoded number, so adding a preset cannot silently skip the check.
    ysfx_slider_range_t range{};
    if (!bank || !ysfx_slider_get_range(fx.get(),10,&range)) return false;
    const unsigned expected=static_cast<unsigned>(range.max);
    if (!bank || bank->preset_count!=expected) return false;
    std::vector<float> silence(128),l(128),r(128);
    const float* in[]={silence.data(),silence.data()}; float* out[]={l.data(),r.data()};
    // Sliders the bank state must reproduce exactly. Index 10 is the preset
    // selector itself and is deliberately excluded; 11 and 12 are the appended
    // oversampling and transformer ports, so per-preset transformer values get
    // verified through the selector and the bank, not just by construction.
    loaded+=bank->preset_count;
    const uint32_t compared[]={0,1,2,3,4,5,6,7,8,9,11,12};
    const unsigned comparedCount=sizeof(compared)/sizeof(compared[0]);
    for (unsigned i=0;i<bank->preset_count;++i) {
        if (!ysfx_load_state(fx.get(),bank->presets[i].state)) return false;
        ysfx_process_float(fx.get(),in,out,2,2,128);
        double values[13];
        for (unsigned j=0;j<comparedCount;++j) values[compared[j]]=ysfx_slider_get_value(fx.get(),compared[j]);
        // Render every actual bank setting with a signal, not just slider recall on silence.
        greenstripe::Parameters p;
        p.input=values[0]; p.output=values[1]; p.attack=values[2]; p.release=values[3];
        p.ratio=static_cast<int>(values[4]); p.mix=values[5]; p.colour=values[6];
        p.compression=values[7]>0; p.enabled=values[8]>0; p.stereoLink=values[9]>0;
        p.transformer=static_cast<int>(values[12]);
        if (!runCase(file,std::string(file).find("Stereo")!=std::string::npos,48000,128,p,0,
                     static_cast<unsigned>(values[11]))) {
            std::cerr << "Preset signal parity failed: " << i+1 << '\n';
            signalParity=false;
        }
        ysfx_slider_set_value(fx.get(),10,i+1,true);
        ysfx_process_float(fx.get(),in,out,2,2,128);
        for (unsigned j=0;j<comparedCount;++j)
            if (values[compared[j]]!=ysfx_slider_get_value(fx.get(),compared[j])) {
                std::cerr << "Bank/selector mismatch preset=" << i << " slider=" << compared[j] << '\n'; return false;
            }
        ysfx_slider_set_value(fx.get(),0,values[0]+0.1,true);
        ysfx_process_float(fx.get(),in,out,2,2,128);
        if (ysfx_slider_get_value(fx.get(),10)!=0) return false;
    }
    return signalParity;
}

int main(int argc,char** argv) {
    if (argc!=3) { std::cerr << "Usage: jsfx_parity mono.jsfx stereo.jsfx\n"; return 2; }
    unsigned passed=0, failed=0;
    for (bool stereo : {false,true}) for (double rate : {44100.0,48000.0,96000.0})
        for (unsigned block : {1u,64u,128u,256u}) for (int mode : {0,1,2,3,4,5}) {
            greenstripe::Parameters p; p.ratio=mode;
            p.stereoLink=(mode!=2); p.mix=mode==3?35:100;
            if (!runCase(argv[stereo?2:1],stereo,rate,block,p,0)) ++failed;
            ++passed;
        }
    for (bool stereo : {false,true}) {
        for (int xf : {1,2,3,4}) for (unsigned os : {0u,1u,2u})
            for (double rate : {44100.0,48000.0,96000.0}) {
                greenstripe::Parameters q; q.transformer=xf; q.colour=0; q.compression=false;
                if (!runCase(argv[stereo?2:1],stereo,rate,128,q,0,os)) ++failed;
                ++passed;
                q.colour=65; q.compression=true; q.input=12;
                if (!runCase(argv[stereo?2:1],stereo,rate,64,q,0,os)) ++failed;
                ++passed;
            }
        for (unsigned os : {0u,1u,2u}) {
            greenstripe::Parameters q; q.transformer=3;
            for (unsigned fixture : {3u,4u,5u,6u,7u}) {
                if (!runCase(argv[stereo?2:1],stereo,48000,128,q,fixture,os)) ++failed;
                ++passed;
            }
        }
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
            for (unsigned block : {64u,128u}) for (int mode : {0,2,5}) {
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
    unsigned presetLoads=0;
    const bool monoPresets=checkPresets(argv[1],presetLoads);
    const bool stereoPresets=checkPresets(argv[2],presetLoads);
    if (!monoPresets || !stereoPresets) {
        std::cerr << "Preset RPL/selector/custom-state test failed\n"; return 1;
    }
    if (failed) { std::printf("FAILURES: %u\n", failed); return 1; }
    std::cout << "JSFX/native parity: PASS (" << passed << " cases, max=" << maximumError << " FS)\n";
    std::cout << "JSFX instrument selector / RPL banks / Custom state / preset signal parity: PASS ("
              << presetLoads << " preset states)\n";
}
