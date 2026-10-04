// SPDX-License-Identifier: MIT — offscreen meter/GFX and UI-independent audio.
#include "ysfx.h"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

static void logger(intptr_t,ysfx_log_level level,const char* message) {
    if (level==ysfx_log_error) std::cerr << message << '\n';
}
int main(int argc,char** argv) {
    if (argc!=3) { std::cerr << "Usage: jsfx_ui effect.jsfx output.ppm\n"; return 2; }
    ysfx_config_u config(ysfx_config_new()); ysfx_set_log_reporter(config.get(),logger);
    ysfx_u fx(ysfx_new(config.get()));
    if (!ysfx_load_file(fx.get(),argv[1],0)||!ysfx_compile(fx.get(),0)) return 1;
    ysfx_set_sample_rate(fx.get(),48000); ysfx_set_block_size(fx.get(),128); ysfx_init(fx.get());
    std::vector<float> inputL(128),inputR(128),outputL(128),outputR(128);
    const float* inputs[]={inputL.data(),inputR.data()}; float* outputs[]={outputL.data(),outputR.data()};
    std::thread audio([&] {
        for (unsigned block=0;block<100;++block) {
            for (unsigned i=0;i<128;++i) {
                inputL[i]=float(0.3*std::sin(6.283185307179586*997*(block*128+i)/48000));
                inputR[i]=float(0.1*std::sin(6.283185307179586*313*(block*128+i)/48000));
            }
            ysfx_process_float(fx.get(),inputs,outputs,2,2,128);
        }
    }); audio.join();
    const double charge=ysfx_read_var(fx.get(),"gs_engine.ctrlL.charge");
    std::vector<uint8_t> pixels(820*380*4);
    ysfx_gfx_config_t ui{}; ui.pixel_width=820; ui.pixel_height=380;
    ui.pixel_stride=820*4; ui.pixels=pixels.data(); ui.scale_factor=1;
    ysfx_gfx_setup(fx.get(),&ui); ysfx_gfx_set_window_state(fx.get(),true,true,true);
    for (unsigned i=0;i<10;++i) ysfx_gfx_run(fx.get());
    if (charge!=ysfx_read_var(fx.get(),"gs_engine.ctrlL.charge")) return 1;
    if (!std::any_of(pixels.begin(),pixels.end(),[](uint8_t p){return p!=0;})) return 1;
    std::ofstream ppm(argv[2],std::ios::binary); ppm << "P6\n820 380\n255\n";
    for (unsigned i=0;i<820*380;++i) {
        ppm.put(char(pixels[i*4+2])); ppm.put(char(pixels[i*4+1])); ppm.put(char(pixels[i*4]));
    }
    std::cout << "JSFX GFX render / unchanged controller state: PASS\n";
}
