// SPDX-License-Identifier: MIT
// Green Stripe 76: independent, reduced-order FET feedback compressor.
// Parameter provenance and limitations: docs/DSP_ARCHITECTURE.md.
#ifndef GREEN_STRIPE_DSP_HPP
#define GREEN_STRIPE_DSP_HPP

#include "ModelConstants.hpp"
#include <algorithm>
#include <cmath>
#include <cstddef>

namespace greenstripe {

inline double bounded(double x, double lo, double hi) {
    return std::max(lo, std::min(hi, x));
}
inline double finiteOr(double x, double fallback = 0.0) {
    return std::isfinite(x) ? x : fallback;
}
// Shared transcendental kernels with mirrored EEL2 operation order, so both
// engines stay bit-equal through parameter-time attack/release mapping. Used
// only when parameters change; the per-sample path keeps libm/EEL2 calls.
inline double seriesLog(double g) {
    double x = g < 1.0e-15 ? 1.0e-15 : g;
    int k = 0;
    while (x >= 2.0) { x *= 0.5; ++k; }
    while (x < 1.0) { x += x; --k; }
    const double y = (x - 1.0) / (x + 1.0);
    const double y2 = y * y;
    double acc = 0.034482758620689655;
    acc = y2 * acc + 0.037037037037037035;
    acc = y2 * acc + 0.040000000000000001;
    acc = y2 * acc + 0.043478260869565216;
    acc = y2 * acc + 0.047619047619047616;
    acc = y2 * acc + 0.052631578947368418;
    acc = y2 * acc + 0.058823529411764705;
    acc = y2 * acc + 0.066666666666666666;
    acc = y2 * acc + 0.076923076923076927;
    acc = y2 * acc + 0.090909090909090912;
    acc = y2 * acc + 0.1111111111111111;
    acc = y2 * acc + 0.14285714285714285;
    acc = y2 * acc + 0.20000000000000001;
    acc = y2 * acc + 0.33333333333333331;
    return k * 0.6931471805599453 + 2.0 * y * (1.0 + y2 * acc);
}
inline double seriesExp(double x) {
    const int k = static_cast<int>(std::floor(x / 0.6931471805599453 + 0.5));
    const double r = x - k * 0.6931471805599453;
    double acc = 1.1470745597729725e-11;
    acc = r * acc + 1.6059043836821613e-10;
    acc = r * acc + 2.08767569878681e-09;
    acc = r * acc + 2.505210838544172e-08;
    acc = r * acc + 2.7557319223985888e-07;
    acc = r * acc + 2.7557319223985893e-06;
    acc = r * acc + 2.4801587301587302e-05;
    acc = r * acc + 0.00019841269841269841;
    acc = r * acc + 0.0013888888888888889;
    acc = r * acc + 0.0083333333333333332;
    acc = r * acc + 0.041666666666666664;
    acc = r * acc + 0.16666666666666666;
    acc = r * acc + 0.5;
    acc = r * acc + 1.0;
    acc = r * acc + 1.0;
    double result = acc;
    int e = k;
    while (e > 0) { result += result; --e; }
    while (e < 0) { result *= 0.5; ++e; }
    return result;
}

// [7/6] Pade tanh approximation. Same function for signal and bias cancellation.
// Formula/properties discussed by J. Tom Schroeder, approximating-tanh (2026).
inline double dbGain(double db) { return seriesExp(db * 0.1151292546497022842); }
inline double gainDb(double gain) {
    return 8.68588963806503655 * seriesLog(gain);
}
inline double zap(double x) { return std::abs(x) < 1.0e-30 ? 0.0 : x; }

inline double softClip(double x) {
    if (x >= 5.0) return 1.0;
    if (x <= -5.0) return -1.0;
    const double x2 = x * x;
    return x * (135135.0 + x2 * (17325.0 + x2 * (378.0 + x2))) /
               (135135.0 + x2 * (62370.0 + x2 * (3150.0 + 28.0 * x2)));
}
inline double clipSlope(double x) {
    if (std::abs(x) >= 5.0) return 0.0;
    const double x2 = x * x;
    const double p = 135135.0 + x2 * (17325.0 + x2 * (378.0 + x2));
    const double d = 135135.0 + x2 * (62370.0 + x2 * (3150.0 + 28.0 * x2));
    const double dp = 17325.0 + x2 * (756.0 + 3.0 * x2);
    const double dd = 62370.0 + x2 * (6300.0 + 84.0 * x2);
    return ((p + 2.0 * x2 * dp) * d - 2.0 * x2 * p * dd) / (d * d);
}
inline double amplifier(double x, double headroom, double bias) {
    return headroom * (softClip(x / headroom + bias) - softClip(bias)) /
           clipSlope(bias);
}

struct Parameters {
    double input, output, attack, release, mix, colour;
    int ratio, oversampling;
    bool compression, enabled, stereoLink;
    Parameters() : input(0), output(0), attack(3), release(5), mix(100),
        colour(100), ratio(0), oversampling(model::default_oversampling),
        compression(true), enabled(true), stereoLink(true) {}
};

struct RunningParameters {
    double inputGain, outputGain, attackTime, releaseTime;
    double ratio, threshold, knee, all, mix, colour, compression, enabled, link;
};

inline RunningParameters convert(const Parameters& p) {
    const int mode = std::max(0, std::min(4, p.ratio));
    const double attack = bounded(finiteOr(p.attack, 3), 1, 7);
    const double release = bounded(finiteOr(p.release, 5), 1, 7);
    RunningParameters r;
    r.inputGain = dbGain(bounded(finiteOr(p.input), -36, 24));
    r.outputGain = dbGain(bounded(finiteOr(p.output), -36, 24));
    r.attackTime = model::attack_slow_seconds * seriesExp((attack - 1.0) / 6.0 *
        seriesLog(model::attack_fast_seconds / model::attack_slow_seconds));
    r.releaseTime = model::release_slow_seconds * seriesExp((release - 1.0) / 6.0 *
        seriesLog(model::release_fast_seconds / model::release_slow_seconds));
    r.ratio = model::ratios[mode];
    r.threshold = model::thresholds_dbfs[mode];
    r.knee = model::knees_db[mode];
    r.all = mode == 4 ? 1.0 : 0.0;
    r.mix = bounded(finiteOr(p.mix, 100) * 0.01, 0, 1);
    r.colour = bounded(finiteOr(p.colour, 100) * 0.01, 0, 1);
    r.compression = p.compression ? 1.0 : 0.0;
    r.enabled = p.enabled ? 1.0 : 0.0;
    r.link = p.stereoLink ? 1.0 : 0.0;
    return r;
}

// The two polyphase allpass cascades use the recurrence documented by HIIR.
// Independently written scalar implementation; see docs/THIRD_PARTY.md.
template <std::size_t N> struct Halfband {
    double x[N], y[N];
    void reset() {
        for (std::size_t i = 0; i < N; ++i) x[i] = y[i] = 0.0;
    }
    void pair(double& even, double& odd, const double* coefficients) {
        for (std::size_t i = 0; i < N; i += 2) {
            const double a = (even - y[i]) * coefficients[i] + x[i];
            const double b = (odd - y[i + 1]) * coefficients[i + 1] + x[i + 1];
            x[i] = even; x[i + 1] = odd;
            y[i] = even = zap(a); y[i + 1] = odd = zap(b);
        }
    }
    void up(double input, double& first, double& second, const double* c) {
        first = second = input;
        pair(first, second, c);
    }
    double down(double first, double second, const double* c) {
        pair(second, first, c);
        return (first + second) * 0.5;
    }
};

struct Resampler {
    Halfband<8> up1, down1;
    Halfband<4> up2, down2;
    void reset() { up1.reset(); up2.reset(); down1.reset(); down2.reset(); }
    void up(double input, double (&samples)[4], unsigned factor) {
        if (factor == 1) { samples[0] = input; return; }
        double a, b;
        up1.up(input, a, b, model::halfband_stage1);
        if (factor == 2) { samples[0] = a; samples[1] = b; return; }
        up2.up(a, samples[0], samples[1], model::halfband_stage2);
        up2.up(b, samples[2], samples[3], model::halfband_stage2);
    }
    double down(const double (&samples)[4], unsigned factor) {
        if (factor == 1) return samples[0];
        if (factor == 2) return down1.down(samples[0], samples[1], model::halfband_stage1);
        const double a = down2.down(samples[0], samples[1], model::halfband_stage2);
        const double b = down2.down(samples[2], samples[3], model::halfband_stage2);
        return down1.down(a, b, model::halfband_stage1);
    }
};

struct Coefficients {
    double fs, smooth, inputHP, outputHP, flux, amplifierLP, memoryUp, memoryDown, lag;
    double outputBiasValue, outputBiasSlope;
    explicit Coefficients(double rate, unsigned factor = 4) : fs(rate * factor) {
        const double pi2 = 6.2831853071795864769;
        smooth = 1.0 - seriesExp(-1.0 / (0.002 * fs));
        inputHP = 1.0 - seriesExp(-pi2 * model::input_highpass_hz / fs);
        outputHP = 1.0 - seriesExp(-pi2 * model::output_highpass_hz / fs);
        flux = 1.0 - seriesExp(-pi2 * 35.0 / fs);
        amplifierLP = 1.0 - seriesExp(-pi2 * model::amplifier_lowpass_hz / fs);
        memoryUp = 1.0 - seriesExp(-1.0 / (0.08 * fs));
        memoryDown = 1.0 - seriesExp(-1.0 / (0.4 * fs));
        lag = 1.0 - seriesExp(-1.0 / (0.00006 * fs));
        outputBiasValue = softClip(0.04);
        outputBiasSlope = clipSlope(0.04);
    }
};

inline double qBase() { return dbGain(model::qbias_db); }
inline double dynamicGain(double charge) { return qBase() / (qBase() + charge); }

// Regularised JFET-inspired KCL. Multiplying by (1+|v|) gives a quadratic on
// each polarity branch. The rationalised positive root avoids subtracting two
// almost-equal numbers and replaces three per-tap Newton iterations.
inline double fet(double input, double charge, double colour, double all) {
    const double u = input * 0.08;
    const double conductance = qBase() - 1.0 + charge;
    const double curvature = colour * (0.24 + 0.08 * all);
    if (curvature == 0.0) return input * qBase() / (1.0 + conductance);
    const double magnitude = std::abs(u);
    const double polarity = u >= 0.0 ? 1.0 : -1.0;
    const double a = 1.0 + conductance * (1.0 - polarity * curvature);
    const double b = 1.0 + conductance - magnitude;
    const double v = 2.0 * u / (b + std::sqrt(b * b + 4.0 * a * magnitude));
    return v * qBase() / 0.08;
}

struct TapCalibration {
    double all, bias, value, slope;
    double threshold, knee, detectorFloor;
    void reset() { all = threshold = knee = -1.0; bias = value = slope = detectorFloor = 0.0; }
    void update(const RunningParameters& p) {
        if (all != p.all) {
            all = p.all; bias = 0.025 + 0.035 * p.all;
            value = softClip(bias); slope = clipSlope(bias);
        }
        if (threshold != p.threshold || knee != p.knee) {
            threshold = p.threshold; knee = p.knee;
            detectorFloor = dbGain(p.threshold - p.knee * 0.5);
        }
    }
};

inline double tap(double input, double charge, double colour, double all,
                  const TapCalibration& calibration) {
    const double x = fet(input, charge, colour, all);
    if (colour == 0.0) return x;
    const double shaped = 2.6 * (softClip(x / 2.6 + calibration.bias) - calibration.value) /
                                    calibration.slope;
    return x + colour * (shaped - x);
}
inline double tap(double input, double charge, double colour, double all) {
    TapCalibration c; c.reset();
    c.bias = 0.025 + 0.035 * all; c.value = softClip(c.bias); c.slope = clipSlope(c.bias);
    return tap(input, charge, colour, all, c);
}

struct Channel {
    double inDC, inFlux, preLP, outDC, outFlux;
    void reset() { inDC = inFlux = preLP = outDC = outFlux = 0.0; }
    double input(double x, double colour, const Coefficients& c) {
        inDC = zap(inDC + c.inputHP * (x - inDC));
        const double hp = x - inDC;
        inFlux = zap(inFlux + c.flux * (hp - inFlux));
        if (colour == 0.0) return x;
        const double iron = hp - 0.12 * (inFlux - 0.6 * softClip(inFlux / 0.6));
        return x + colour * (iron - x);
    }
    double output(double x, const RunningParameters& p, const Coefficients& c) {
        preLP = zap(preLP + c.amplifierLP * (x - preLP));
        x += p.colour * (preLP - x);
        x *= p.outputGain;
        outFlux = zap(outFlux + c.flux * (x - outFlux));
        if (p.colour != 0.0) {
            const double iron = x - 0.10 * (outFlux - 0.8 * softClip(outFlux / 0.8));
            const double driven = 1.8 * (softClip(iron / 1.8 + 0.04) - c.outputBiasValue) /
                                             c.outputBiasSlope;
            x += p.colour * (driven - x);
        }
        outDC = zap(outDC + c.outputHP * (x - outDC));
        return x - p.colour * outDC;
    }
};

inline double kneeValue(double over, double width) {
    if (over <= -width * 0.5) return 0.0;
    if (over >= width * 0.5) return over;
    const double k = over + width * 0.5;
    return k * k / (2.0 * width);
}
inline double kneeSlope(double over, double width) {
    return bounded((over + width * 0.5) / width, 0.0, 1.0);
}

struct Controller {
    double charge, memory, lagged;
    double cachedRelease, releaseStep, reductionDb;
    void reset() { charge = memory = lagged = reductionDb = 0.0; cachedRelease = -1.0; releaseStep = 0.0; }
    double requestedDb(double a, double b, double q, const RunningParameters& p,
                       double ratio, double& over, const TapCalibration& calibration) const {
        double rectified;
        if (p.all == 1.0) {
            rectified = lagged * dynamicGain(q);
        } else {
            const double left = std::abs(tap(a, q, p.colour, p.all, calibration));
            const double measured = a == b ? left :
                std::max(left, std::abs(tap(b, q, p.colour, p.all, calibration)));
            rectified = (1.0 - p.all) * measured + p.all * lagged * dynamicGain(q);
        }
        if (rectified <= calibration.detectorFloor) { over = -p.knee; return 0.0; }
        over = gainDb(rectified) - p.threshold;
        return std::min(60.0, (ratio - 1.0) * kneeValue(over, p.knee));
    }
    double target(double a, double b, double q, const RunningParameters& p,
                  double ratio, double& derivative, const TapCalibration& calibration) const {
        double over;
        const double desired = requestedDb(a, b, q, p, ratio, over, calibration);
        if (desired == 0.0) { derivative = 0.0; return 0.0; }
        const double result = qBase() * (dbGain(desired) - 1.0);
        derivative = desired >= 60.0 ? 0.0 :
            -(qBase() + result) * (ratio - 1.0) * kneeSlope(over, p.knee) /
                                  (qBase() + q);
        return result;
    }
    double process(double a, double b, const RunningParameters& p,
                   const Coefficients& c, const TapCalibration& calibration) {
        lagged = zap(lagged + c.lag * (std::max(std::abs(a), std::abs(b)) - lagged));
        const double ratio = p.ratio + p.all * ((12.0 + 8.0 * memory) - p.ratio);
        double derivative = 0.0;
        double over;
        const double wantedDb = requestedDb(a, b, charge, p, ratio, over, calibration);
        if (wantedDb <= reductionDb) {
            if (cachedRelease != p.releaseTime) {
                cachedRelease = p.releaseTime; releaseStep = 1.0 / (p.releaseTime * c.fs);
            }
            const double step = releaseStep / (1.0 + 0.75 * memory + 0.2 * p.all);
            // Fifth-order exp(-step), valid through 8k native / 50ms release.
            const double decay = 1.0 + step * (-1.0 + step * (0.5 + step *
                (-1.0 / 6.0 + step * (1.0 / 24.0 - step / 120.0))));
            const double z = (1.0 - decay) * charge / (qBase() + charge);
            // log(1-z) update; z<=0.0025 even at 8k native/50ms. Re-anchor on
            // every charging step; no full logarithm in the common release path.
            reductionDb = std::max(0.0, reductionDb + 8.68588963806503655 *
                z * (-1.0 + z * (-0.5 + z * (-1.0 / 3.0 + z * (-0.25 - z / 5.0)))));
            charge = zap(charge * decay);
            if (charge == 0.0) reductionDb = 0.0;
        } else {
            // Backward-Euler implicit feedback update; no explicit z^-1 tap.
            const double alpha = 1.0 / (c.fs * p.attackTime * ratio * (1.0 + 0.3 * p.all));
            const double level = gainDb(std::max(std::abs(a), std::abs(b)));
            const double guess = qBase() * (dbGain(std::min(60.0,
                (1.0 - 1.0 / ratio) * kneeValue(level - p.threshold, p.knee))) - 1.0);
            double low = charge;
            double high = std::min(1000.0, std::max(charge + 1.0, guess * 1.25 + 0.01));
            for (int i = 0; i < 4; ++i) {
                const double f = (1.0 + alpha) * high - charge -
                                  alpha * target(a, b, high, p, ratio, derivative, calibration);
                if (f >= 0.0) break;
                high = std::min(1000.0, high * 2.0 + 1.0);
            }
            if ((1.0 + alpha) * high - charge -
                alpha * target(a, b, high, p, ratio, derivative, calibration) < 0.0) high = 1000.0;
            double q = bounded(guess, low, high);
            for (int i = 0; i < 8; ++i) {
                const double wanted = target(a, b, q, p, ratio, derivative, calibration);
                const double f = (1.0 + alpha) * q - charge - alpha * wanted;
                if (std::abs(f) < 1.0e-10 * (1.0 + charge)) break;
                if (f > 0.0) high = q; else low = q;
                const double next = q - f / (1.0 + alpha - alpha * derivative);
                q = next > low && next < high ? next : (low + high) * 0.5;
            }
            charge = bounded(q, 0.0, 1000.0);
            reductionDb = charge == 0.0 ? 0.0 : -gainDb(dynamicGain(charge));
        }
        const double history = bounded(reductionDb / 24.0, 0.0, 1.0);
        memory = zap(memory + (history > memory ? c.memoryUp : c.memoryDown) * (history - memory));
        return charge;
    }
};

class Processor {
public:
    explicit Processor(double sampleRate, bool stereo = true)
        : coefficients_(sampleRate, 1), nativeCoefficients_(sampleRate, 1),
          twoCoefficients_(sampleRate, 2), fourCoefficients_(sampleRate, 4),
          stereo_(stereo), initial_(true), smoothing_(false), parked_(false), bypassed_(false),
          activeOS_(0), requestedOS_(0), osTransition_(0),
          osFadeLength_(static_cast<unsigned>(std::max(1.0, std::ceil(0.002 * sampleRate)))),
          osFadeRemaining_(0), osGain_(1.0), osFadeInv_(1.0 / osFadeLength_) { reset(); }
    void setParameters(const Parameters& p) {
        const unsigned selectedOS = static_cast<unsigned>(std::max(0, std::min(2, p.oversampling)));
        if (initial_) {
            changeOversampling(selectedOS);
            requestedOS_ = selectedOS; osTransition_ = 0; osGain_ = 1.0;
        } else if (selectedOS != requestedOS_) {
            requestedOS_ = selectedOS;
            osTransition_ = requestedOS_ == activeOS_ ? 2 : 1;
            // Continue the running fade without a gain jump; sample-counted.
            osFadeRemaining_ = static_cast<unsigned>(std::max(0.0, std::min(1.0,
                osTransition_ == 2 ? 1.0 - osGain_ : osGain_)) * osFadeLength_ + 0.5);
        }
        const RunningParameters next = convert(p);
        if (!initial_ && stereo_ && next.link != target_.link) {
            if (next.link == 0.0) {
                controllers_[0] = controllers_[1] = controllers_[2];
            } else {
                controllers_[2] = controllers_[controllers_[1].charge > controllers_[0].charge ? 1 : 0];
            }
        }
        target_ = next;
        if (initial_) {
            running_ = target_; initial_ = false; smoothing_ = false;
            calibration_.update(running_);
        }
        else smoothing_ = !sameParameters(running_, target_);
    }
    void reset() {
        for (int i = 0; i < 2; ++i) { resamplers_[i].reset(); channels_[i].reset(); }
        for (int i = 0; i < 3; ++i) controllers_[i].reset();
        calibration_.reset();
        lastGR_[0] = lastGR_[1] = 0.0;
        initial_ = true;
        smoothing_ = parked_ = bypassed_ = false;
        activeOS_ = requestedOS_ = osTransition_ = 0;
        osFadeRemaining_ = 0;
        coefficients_ = nativeCoefficients_;
        osGain_ = 1.0;
        target_ = running_ = convert(Parameters());
    }
    void sample(double left, double right, double& outputLeft, double& outputRight) {
        double in[2][4], out[2][4];
        const unsigned factor = 1u << activeOS_;
        resamplers_[0].up(bounded(finiteOr(left), -256.0, 256.0), in[0], factor);
        if (stereo_) resamplers_[1].up(bounded(finiteOr(right), -256.0, 256.0), in[1], factor);
        for (unsigned i = 0; i < factor; ++i) {
            smooth();
            if (running_.enabled == 0.0) {
                if (!bypassed_) {
                    for (int j = 0; j < 2; ++j) channels_[j].reset();
                    for (int j = 0; j < 3; ++j) controllers_[j].reset();
                    parked_ = bypassed_ = true;
                }
                out[0][i] = in[0][i];
                if (stereo_) out[1][i] = in[1][i];
                lastGR_[0] = lastGR_[1] = 0.0;
                continue;
            }
            bypassed_ = false;
            const double a = channels_[0].input(in[0][i] * running_.inputGain,
                                               running_.colour, coefficients_);
            const double b = stereo_ ? channels_[1].input(in[1][i] * running_.inputGain,
                                               running_.colour, coefficients_) : a;
            double qL = 0.0, qR = 0.0;
            const bool park = running_.compression == 0.0 || running_.enabled == 0.0;
            if (park) {
                if (!parked_) {
                    for (int j = 0; j < 3; ++j) controllers_[j].reset();
                    parked_ = true;
                }
            } else {
                parked_ = false;
                if (!stereo_) {
                    qL = qR = controllers_[0].process(a, a, running_, coefficients_, calibration_);
                } else if (running_.link == 1.0) {
                    qL = qR = controllers_[2].process(a, b, running_, coefficients_, calibration_);
                } else if (running_.link == 0.0) {
                    qL = controllers_[0].process(a, a, running_, coefficients_, calibration_);
                    qR = controllers_[1].process(b, b, running_, coefficients_, calibration_);
                } else {
                    const double independentL = controllers_[0].process(a, a, running_, coefficients_, calibration_);
                    const double independentR = controllers_[1].process(b, b, running_, coefficients_, calibration_);
                    const double linked = controllers_[2].process(a, b, running_, coefficients_, calibration_);
                    // All three run only during a bounded link crossfade.
                    const double gL = (1.0 - running_.link) * dynamicGain(independentL) + running_.link * dynamicGain(linked);
                    const double gR = (1.0 - running_.link) * dynamicGain(independentR) + running_.link * dynamicGain(linked);
                    qL = qBase() * (1.0 / gL - 1.0); qR = qBase() * (1.0 / gR - 1.0);
                }
            }
            qL *= running_.compression; qR *= running_.compression;
            const double wetL = channels_[0].output(tap(a, qL, running_.colour, running_.all, calibration_),
                                                   running_, coefficients_);
            const double blend = running_.mix * running_.enabled;
            out[0][i] = in[0][i] + blend * (wetL - in[0][i]);
            if (stereo_) {
                const double wetR = channels_[1].output(tap(b, qR, running_.colour, running_.all, calibration_),
                                                        running_, coefficients_);
                out[1][i] = in[1][i] + blend * (wetR - in[1][i]);
            }
            if (i == factor - 1) {
                lastGR_[0] = gainDb(dynamicGain(qL)) * running_.enabled;
                lastGR_[1] = stereo_ ? gainDb(dynamicGain(qR)) * running_.enabled : lastGR_[0];
            }
        }
        outputLeft = finiteOr(resamplers_[0].down(out[0], factor)) * osGain_;
        outputRight = stereo_ ? finiteOr(resamplers_[1].down(out[1], factor)) * osGain_ : outputLeft;
        advanceOversamplingTransition();
    }
    double gainReduction(unsigned channel = 0) const { return lastGR_[channel > 0 ? 1 : 0]; }
    unsigned latency() const {
        return activeOS_ == 0 ? 0 : activeOS_ == 1 ? model::latency_2x_frames : model::nominal_latency_frames;
    }
    unsigned oversamplingFactor() const { return 1u << activeOS_; }

private:
    void changeOversampling(unsigned selected) {
        activeOS_ = selected;
        coefficients_ = selected == 0 ? nativeCoefficients_ : selected == 1 ? twoCoefficients_ : fourCoefficients_;
        for (int i = 0; i < 2; ++i) resamplers_[i].reset();
        for (int i = 0; i < 3; ++i) controllers_[i].cachedRelease = -1.0;
    }
    void advanceOversamplingTransition() {
        if (osTransition_ == 1) {
            osFadeRemaining_ = osFadeRemaining_ > 0 ? osFadeRemaining_ - 1 : 0;
            osGain_ = osFadeRemaining_ * osFadeInv_;
            if (osFadeRemaining_ == 0) {
                changeOversampling(requestedOS_);
                osTransition_ = 2;
                osFadeRemaining_ = osFadeLength_;
            }
        } else if (osTransition_ == 2) {
            osFadeRemaining_ = osFadeRemaining_ > 0 ? osFadeRemaining_ - 1 : 0;
            osGain_ = 1.0 - osFadeRemaining_ * osFadeInv_;
            if (osFadeRemaining_ == 0) osTransition_ = 0;
        }
    }
    static bool sameParameters(const RunningParameters& a, const RunningParameters& b) {
        return a.inputGain == b.inputGain && a.outputGain == b.outputGain && a.attackTime == b.attackTime &&
               a.releaseTime == b.releaseTime && a.ratio == b.ratio && a.threshold == b.threshold &&
               a.knee == b.knee && a.all == b.all && a.mix == b.mix && a.colour == b.colour &&
               a.compression == b.compression && a.enabled == b.enabled && a.link == b.link;
    }
    void approach(double& value, double goal) {
        value += coefficients_.smooth * (goal - value);
        if (std::abs(goal - value) <= 1.0e-12 * std::max(1.0, std::abs(goal))) value = goal;
        else smoothing_ = true;
    }
    void smooth() {
        if (!smoothing_) return;
        smoothing_ = false;
#define GS_SMOOTH(field) approach(running_.field, target_.field)
        GS_SMOOTH(inputGain); GS_SMOOTH(outputGain); GS_SMOOTH(attackTime);
        GS_SMOOTH(releaseTime); GS_SMOOTH(ratio); GS_SMOOTH(threshold);
        GS_SMOOTH(knee); GS_SMOOTH(all); GS_SMOOTH(mix); GS_SMOOTH(colour);
        GS_SMOOTH(compression); GS_SMOOTH(enabled); GS_SMOOTH(link);
#undef GS_SMOOTH
        calibration_.update(running_);
    }
    Coefficients coefficients_;
    const Coefficients nativeCoefficients_, twoCoefficients_, fourCoefficients_;
    bool stereo_, initial_, smoothing_, parked_, bypassed_;
    RunningParameters running_, target_;
    Resampler resamplers_[2];
    Channel channels_[2];
    Controller controllers_[3];
    TapCalibration calibration_;
    double lastGR_[2];
    unsigned activeOS_, requestedOS_, osTransition_, osFadeLength_, osFadeRemaining_;
    double osGain_, osFadeInv_;
};

} // namespace greenstripe
#endif
