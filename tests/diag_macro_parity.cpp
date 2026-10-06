// SPDX-License-Identifier: MIT — proves the opt-in solver counter is audio neutral.
#include "dsp/GreenStripe.hpp"
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>

namespace {

const double kPi = 3.14159265358979323846;

void hashDouble(std::uint64_t& hash, double value) {
    unsigned char bytes[sizeof(double)];
    std::memcpy(bytes, &value, sizeof(double));
    for (unsigned i = 0; i < sizeof(double); ++i) {
        hash ^= bytes[i];
        hash *= 1099511628211ULL;
    }
}

struct Signal {
    double left, right;
    Signal(std::uint64_t& seed)
        : left(0), right(0), seed_(seed) {}
    void next(double level) {
        seed_ = seed_ * 6364136223846793005ULL + 1442695040888963407ULL;
        const double noise = static_cast<double>(seed_ >> 11) / 9007199254740992.0 - 0.5;
        const double t = static_cast<double>(phase_++) / 48000.0;
        left = level * (0.55 * std::sin(2.0 * kPi * 60.0 * t)
                        + 0.25 * std::sin(2.0 * kPi * 431.0 * t) + 0.30 * noise);
        right = level * (0.55 * std::sin(2.0 * kPi * 60.0 * t + 0.4)
                         + 0.25 * std::sin(2.0 * kPi * 431.0 * t - 0.2) - 0.24 * noise);
    }
    std::uint64_t seed_;
    unsigned phase_ = 0;
};

void fail(const char* message) {
    std::cerr << "FAIL: " << message << '\n';
}

}  // namespace

int main() {
    std::uint64_t hash = 1469598103934665603ULL;
    std::uint64_t seed = 0x9e3779b97f4a7c15ULL;
    unsigned cases = 0, samples = 0, finiteFailures = 0;

    for (int transformer = 0; transformer < 5; ++transformer) {
        for (int oversampling = 0; oversampling < 3; ++oversampling) {
            for (int ratio = 0; ratio < 6; ratio += 3) {
                for (int stereoMode = 0; stereoMode < 2; ++stereoMode) {
                    const bool stereo = stereoMode == 1;
                    greenstripe::Processor processor(48000, stereo);
                    greenstripe::Parameters p;
                    p.transformer = transformer;
                    p.oversampling = oversampling;
                    p.ratio = ratio;
                    p.colour = 60;
                    p.input = 6;
                    p.output = -3;
                    p.attack = 2;
                    p.release = 4;
                    processor.setParameters(p);
                    Signal signal(seed);
                    const unsigned frames = 1500;
                    for (unsigned n = 0; n < frames; ++n) {
                        double level = 0.9;
                        if (n > 200 && n < 260) level = 0.02;
                        if (n >= 700 && n < 760) level = 2.5;
                        signal.next(level);
                        double l = 0.0, r = 0.0;
                        processor.sample(signal.left, signal.right, l, r);
                        if (!std::isfinite(l) || !std::isfinite(r)) ++finiteFailures;
                        hashDouble(hash, l);
                        hashDouble(hash, r);
                        if (n == 600) { p.oversampling = (oversampling + 1) % 3; processor.setParameters(p); }
                        if (n == 900) { p.transformer = (transformer + 1) % 5; processor.setParameters(p); }
                        if (n == 1100) { p.stereoLink = !p.stereoLink; processor.setParameters(p); }
                    }
                    samples += frames;
                    ++cases;
                }
            }
        }
    }

#ifdef GS76_TRANSFORMER_STATS
    {
        greenstripe::Processor none(48000, true);
        greenstripe::Parameters p; p.transformer = 0;
        none.setParameters(p);
        for (unsigned n = 0; n < 480; ++n) { double l, r; none.sample(0.5, -0.5, l, r); }
        if (none.transformerStats(0).samples != 0) fail("None must not enter the solver");
        if (none.transformerStats(0).iterations != 0) fail("None must not iterate");

        greenstripe::Processor model(48000, true);
        p.transformer = 1; p.oversampling = 2;
        model.setParameters(p);
        for (unsigned n = 0; n < 480; ++n) { double l, r; model.sample(0.5, -0.5, l, r); }
        for (unsigned channel = 0; channel < 2; ++channel) {
            const greenstripe::TransformerSolverStats& s = model.transformerStats(channel);
            if (s.samples != 480u * 4u) fail("internal sample count must follow 4x oversampling");
            if (s.iterations < s.samples) fail("every sample needs at least one iteration");
            if (s.iterations > s.samples * 40u) fail("iteration budget exceeded");
            if (s.capped != 0) fail("the 40 iteration limit must not be reached here");
        }
        const greenstripe::TransformerSolverStats before = model.transformerStats(0);
        if (before.iterations == 0) fail("counter did not move");
        model.clearTransformerStats();
        if (model.transformerStats(0).iterations != 0
            || model.transformerStats(0).samples != 0
            || model.transformerStats(0).capped != 0) fail("clear did not reset");
        model.reset();
        if (model.transformerStats(1).samples != 0) fail("reset must clear the counter");
    }
#endif

    if (finiteFailures) fail("non finite output in the sweep");
    std::cout << "macro_parity " << hash << ' ' << cases << ' ' << samples << '\n';
    return finiteFailures ? 1 : 0;
}
