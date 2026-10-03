// SPDX-License-Identifier: MIT
#include "lv2_abi.h"
#include "dsp/GreenStripe.hpp"
#include <new>
#include <cstring>
#include <cstdlib>

// Optional ABI floor for non-MPB GNU-A builds. AArch64's initial glibc ABI
// is 2.17; newer libm defaults otherwise pull exp/log/pow@GLIBC_2.29.
// The official MPB glibc-2.27 sysroot does not need this option.
#if defined(GS_GLIBC_217) && defined(__aarch64__) && defined(__linux__)
__asm__(".symver exp,exp@GLIBC_2.17");
__asm__(".symver log,log@GLIBC_2.17");
__asm__(".symver pow,pow@GLIBC_2.17");
#endif

namespace {
const char* const monoURI = "https://github.com/j4yj03/mod-1175-lv2#green-stripe-76-mono";
const char* const stereoURI = "https://github.com/j4yj03/mod-1175-lv2#green-stripe-76-stereo";

struct Instance {
    greenstripe::Processor processor;
    float* ports[16];
    bool stereo;
    explicit Instance(double rate, bool twoChannels) : processor(rate, twoChannels), stereo(twoChannels) {
        for (unsigned i = 0; i < 16; ++i) ports[i] = 0;
    }
    double value(unsigned index, double fallback) const {
        return ports[index] ? greenstripe::finiteOr(*ports[index], fallback) : fallback;
    }
    void update() {
        const unsigned base = stereo ? 4 : 2;
        greenstripe::Parameters p;
        p.input = value(base, 0); p.output = value(base + 1, 0);
        p.attack = value(base + 2, 3); p.release = value(base + 3, 5);
        p.ratio = static_cast<int>(greenstripe::bounded(value(base + 4, 0), 0, 4) + 0.5);
        p.mix = value(base + 5, 100); p.colour = value(base + 6, 100);
        p.compression = value(base + 7, 1) > 0.0;
        p.enabled = value(base + 8, 1) > 0.0;
        p.stereoLink = !stereo || value(base + 9, 1) > 0.0;
        p.oversampling = static_cast<int>(greenstripe::bounded(value(stereo ? 15 : 12, 0), 0, 2) + 0.5);
        processor.setParameters(p);
    }
};

LV2_Handle instantiate(const LV2_Descriptor* descriptor, double rate, const char*, const LV2_Feature* const*) {
    if (!std::isfinite(rate) || rate < 8000.0 || rate > 384000.0) return 0;
    void* storage = std::malloc(sizeof(Instance));
    return storage ? new (storage) Instance(rate, std::strcmp(descriptor->URI, stereoURI) == 0) : 0;
}
void connect(LV2_Handle handle, uint32_t port, void* data) {
    Instance* self = static_cast<Instance*>(handle);
    if (port < (self->stereo ? 16u : 13u)) self->ports[port] = static_cast<float*>(data);
}
void activate(LV2_Handle handle) {
    Instance* self = static_cast<Instance*>(handle);
    self->processor.reset();
    self->update();
}
void run(LV2_Handle handle, uint32_t frames) {
    Instance* self = static_cast<Instance*>(handle);
    self->update();
    const unsigned latencyPort = self->stereo ? 14 : 11;
    for (uint32_t i = 0; i < frames; ++i) {
        // Read all inputs before writing to support in-place stereo processing.
        const double left = self->ports[0] ? self->ports[0][i] : 0.0;
        const double right = self->stereo && self->ports[1] ? self->ports[1][i] : left;
        double a, b;
        self->processor.sample(left, right, a, b);
        if (self->ports[self->stereo ? 2 : 1]) self->ports[self->stereo ? 2 : 1][i] = static_cast<float>(a);
        if (self->stereo && self->ports[3]) self->ports[3][i] = static_cast<float>(b);
    }
    if (self->ports[latencyPort]) *self->ports[latencyPort] = self->processor.latency();
}
void cleanup(LV2_Handle handle) {
    static_cast<Instance*>(handle)->~Instance();
    std::free(handle);
}
const LV2_Descriptor descriptors[] = {
    { monoURI, instantiate, connect, activate, run, 0, cleanup, 0 },
    { stereoURI, instantiate, connect, activate, run, 0, cleanup, 0 }
};
}

#ifdef _WIN32
extern "C" __declspec(dllexport)
#else
extern "C" __attribute__((visibility("default")))
#endif
const LV2_Descriptor* lv2_descriptor(uint32_t index) {
    return index < 2 ? &descriptors[index] : 0;
}
