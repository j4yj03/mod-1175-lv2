// SPDX-License-Identifier: MIT
// Same offline vectors for before/after runs; excludes compilation and GUI work.
#include "ysfx.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

struct Scenario {
    const char* name;
    double input, output, ratio, colour, compression, enabled, link, transformer, oversampling;
};

static void logger(intptr_t, ysfx_log_level level, const char* message) {
    if (level == ysfx_log_error) std::cerr << message << '\n';
}
static double optionalVar(ysfx_t* fx, const char* name) {
    const ysfx_real* value = ysfx_find_var(fx, name);
    return value ? *value : 0.0;
}

int main(int argc, char** argv) {
    if (argc < 3 || argc > 5) {
        std::cerr << "Usage: benchmark_jsfx mono.jsfx stereo.jsfx [audio_seconds=1] [repeats=5]\n";
        return 2;
    }
    const double duration = argc > 3 ? std::stod(argv[3]) : 1.0;
    if (!std::isfinite(duration) || duration <= 0 || duration > 60) return 2;
    const unsigned frames = static_cast<unsigned>(48000 * duration);
    const unsigned repeats = argc > 4 ? static_cast<unsigned>(std::stoul(argv[4])) : 5;
    if (!frames || !repeats || repeats > 20) return 2;
    const unsigned block = 128;
    const Scenario scenarios[] = {
        {"normal", 0, 0, 1, 100, 1, 1, 1, 0, 0},
        {"all", 6, -3, 5, 100, 1, 1, 1, 0, 0},
        {"clean", 0, 0, 1, 0, 1, 1, 1, 0, 0},
        {"colour_only", 6, -6, 1, 100, 0, 1, 1, 0, 0},
        {"bypass", 0, 0, 1, 100, 1, 0, 1, 0, 0},
        {"dual_mono", 0, 0, 1, 100, 1, 1, 0, 0, 0},
        {"xf_60s", 0, 0, 1, 100, 1, 1, 1, 1, 0},
        {"xf_80s", 0, 0, 1, 100, 1, 1, 1, 2, 0},
        {"xf_00s", 0, 0, 1, 100, 1, 1, 1, 3, 0},
        {"xf_60s_4x", 0, 0, 1, 100, 1, 1, 1, 1, 2},
    };
    std::vector<float> signalL(frames), signalR(frames), outL(block), outR(block);
    for (unsigned i = 0; i < frames; ++i) {
        const double t = i / 48000.0;
        const double envelope = (i / 4096) % 3 == 0 ? 0.02 : (i / 4096) % 3 == 1 ? 0.25 : 0.6;
        signalL[i] = float(envelope * (0.7 * std::sin(6.283185307179586 * 997 * t) + 0.3 * std::sin(6.283185307179586 * 53 * t)));
        signalR[i] = float(envelope * (0.5 * std::sin(6.283185307179586 * 313 * t) + 0.2 * std::sin(6.283185307179586 * 79 * t)));
    }
    std::cout << "{\"rate\":48000,\"block\":128,\"frames\":" << frames
              << ",\"repeats\":" << repeats << ",\"gui\":\"not executed\",\"cases\":[\n";
    bool first = true;
    for (bool stereo : {false, true}) for (const Scenario& scenario : scenarios) {
        if (!stereo && std::string(scenario.name) == "dual_mono") continue;
        ysfx_config_u config(ysfx_config_new()); ysfx_set_log_reporter(config.get(), logger);
        ysfx_u fx(ysfx_new(config.get()));
        if (!ysfx_load_file(fx.get(), argv[stereo ? 2 : 1], 0) || !ysfx_compile(fx.get(), ysfx_compile_no_gfx)) return 1;
        ysfx_set_sample_rate(fx.get(), 48000); ysfx_set_block_size(fx.get(), block);
        ysfx_init(fx.get());
        const double controls[] = {scenario.input, scenario.output, 3, 5, scenario.ratio, 100,
                                  scenario.colour, scenario.compression, scenario.enabled, scenario.link};
        for (unsigned i = 0; i < 10; ++i) ysfx_slider_set_value(fx.get(), i, controls[i], true);
        ysfx_slider_set_value(fx.get(),11,scenario.oversampling,true);
        ysfx_slider_set_value(fx.get(),12,scenario.transformer,true);
        float* outputs[] = {outL.data(), outR.data()};
        std::vector<double> seconds;
        double checksum = 0;
        for (unsigned pass = 0; pass < repeats + 1; ++pass) {
            const auto start = std::chrono::steady_clock::now();
            for (unsigned done = 0; done < frames; done += block) {
                const unsigned count = std::min(block, frames - done);
                const float* inputs[] = {signalL.data() + done, signalR.data() + done};
                ysfx_process_float(fx.get(), inputs, outputs, 2, 2, count);
                checksum += outL[count - 1] + outR[count - 1];
            }
            const double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
            if (pass) seconds.push_back(elapsed);
        }
        std::sort(seconds.begin(), seconds.end());
        if (!first) std::cout << ",\n";
        first = false;
        std::cout << std::setprecision(10) << "{\"variant\":\"" << (stereo ? "stereo" : "mono")
                  << "\",\"scenario\":\"" << scenario.name << "\",\"median_seconds\":" << seconds[seconds.size() / 2]
                  << ",\"seconds_per_audio_second\":" << seconds[seconds.size() / 2] * 48000.0 / frames
                  << ",\"minimum_seconds\":" << seconds[0] << ",\"checksum\":" << checksum
                  << ",\"profile_controller_calls\":" << optionalVar(fx.get(), "gs_profile_controllers")
                  << ",\"profile_target_calls\":" << optionalVar(fx.get(), "gs_profile_targets")
                  << ",\"profile_solver_iterations\":" << optionalVar(fx.get(), "gs_profile_iterations")
                  << ",\"profile_release_updates\":" << optionalVar(fx.get(), "gs_profile_release") << "}";
    }
    std::cout << "\n]}\n";
}
