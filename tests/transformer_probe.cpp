// SPDX-License-Identifier: MIT — offline bridge for independent numerical checks/refits.
#include "dsp/GreenStripe.hpp"
#include <cstddef>

extern "C" __attribute__((visibility("default")))
int gs76_runtime_transformer(unsigned profile, double rate, const double* input,
                           double* output, double* raw, std::size_t count) {
    if (profile<1 || profile>4 || rate<8000 || rate>1536000) return -1;
    greenstripe::TransformerCoefficients c; c.prepare(rate,profile-1);
    greenstripe::TransformerCore core; core.reset();
    for (std::size_t n=0; n<count; ++n) {
        output[n]=core.process(input[n],c);
        if (raw) raw[n]=core.voltage*c.outputScale;
        if (!std::isfinite(output[n])) return -2;
    }
    return 0;
}
