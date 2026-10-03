// SPDX-License-Identifier: MIT
// Read-only diagnostic of the current native DSP; writes samples to stdout.
// The screenshot settings are not a new calibration of the processor.
#include "dsp/GreenStripe.hpp"
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 4 || argc > 6) {
        std::cerr << "Usage: measurement_probe scenario(0..8) amplitude periods [delta|tone] [frequency_hz]\n"
                  << "0 identity; 1..6 screenshot experiments; 7 trial7 4:1; 8 trial7 All\n";
        return 2;
    }
    const int experiment = std::atoi(argv[1]);
    const double amplitude = std::atof(argv[2]);
    const int periods = std::atoi(argv[3]);
    const std::string mode = argc >= 5 ? argv[4] : "delta";
    const double frequency = argc == 6 ? std::atof(argv[5]) : 44100.0 * 935.0 / 16384.0;
    if (experiment < 0 || experiment > 8 || !std::isfinite(amplitude) || amplitude <= 0 || periods < 1 || periods > 1000 ||
        (mode != "delta" && mode != "tone") || !std::isfinite(frequency) || frequency <= 0 || frequency >= 22050)
        return 2;
    greenstripe::Parameters p;
    if (experiment == 0) { p.colour = 0; p.compression = false; }
    if (experiment == 2 || experiment == 3) {
        p.input = 24; p.output = -11.2; p.attack = 1; p.release = 7; p.ratio = 4;
    }
    if (experiment == 3) p.colour = 0;
    if (experiment == 4 || experiment == 5) {
        p.attack = 1; p.release = 1; p.ratio = 4; p.compression = false;
        if (experiment == 5) { p.input = 15.6; p.output = -15.6; }
    }
    if (experiment == 6) {
        p.input = -15.6; p.output = 15.6; p.attack = 7; p.release = 7;
        p.ratio = 3; p.colour = 0;
    }
    if (experiment == 7 || experiment == 8) {
        p.input = -6; p.output = 6; p.attack = 7; p.release = 1;
        p.ratio = experiment == 7 ? 0 : 4; p.colour = 0;
    }
    greenstripe::Processor processor(44100, false);
    processor.setParameters(p);
    std::cout << std::setprecision(17);
    for (int period = 0; period < periods; ++period) {
        for (unsigned sample = 0; sample < 16384; ++sample) {
            double left, right;
            const double input = mode == "delta" ? (sample == 1020 ? amplitude : 0.0) :
                amplitude * std::sin(6.2831853071795864769 * frequency * (period * 16384u + sample) / 44100.0);
            processor.sample(input, 0.0, left, right);
            if (period == periods - 1) std::cout << left << '\n';
        }
    }
}
