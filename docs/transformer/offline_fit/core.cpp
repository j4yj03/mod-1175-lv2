// Offline transformer reference only. Not part of the LV2/JSFX runtime.
// Copyright (c) 2026 Green Stripe 76 contributors, MIT.
#include <algorithm>
#include <cmath>
#include <complex>
#include <cstddef>
#include <vector>

namespace {
const double pi = 3.141592653589793238462643383279502884;
const unsigned branches = 14;
const double thresholds[branches] = {
    0.00002, 0.00005, 0.0001, 0.0002, 0.0005, 0.001, 0.002,
    0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5
};

double power(double x, unsigned n) {
    double y = 1.0;
    for (unsigned i = 0; i < n; ++i) y *= x;
    return y;
}
double bounded(double x, double lo, double hi) {
    return std::max(lo, std::min(hi, x));
}
double db(double x) { return 20.0 * std::log10(std::max(std::abs(x), 1e-300)); }

// p: L0, lambdaScale, hysteresisStiffness, hysteresisSlope,
// Lrelax, frelax, Gcore, hfF0, hfQ, Rsource, Rp, Rs, Rload,
// hysteresisOn, family(0=polynomial,1=Frohlich,2=generalized rational), exponent,
// rational saturation strength; high-field L ratio (0 = no regularization),
// series resistance of nonlinear magnetization relaxation branch (0 = shared flux).
// For polynomial strength=1 to avoid scale degeneracy.
struct Core {
    const double* p;
    double ra, rb, denominator, h, relaxation, weights[branches];
    double lambda, relax, nonlinearFlux, stops[branches], voltage;
    unsigned maxIterations;
    Core(const double* params, double dt) : p(params), lambda(0), relax(0), nonlinearFlux(0), voltage(0), maxIterations(0) {
        ra = p[9] + p[10]; rb = p[11] + p[12];
        denominator = 1.0 + ra / rb + ra * p[6];
        h = 0.5 * dt;
        relaxation = p[4] > 0 ? h * 2.0 * pi * p[5] : 0.0;
        for (unsigned j = 0; j < branches; ++j) {
            stops[j] = 0;
            weights[j] = p[13] > 0 ? p[2] * std::pow(thresholds[j] / 0.001, p[3]) : 0;
        }
    }
    double law(double x, double& derivative) const {
        if (p[14] > 0.5) {
            const unsigned n = p[14] > 1.5 ? static_cast<unsigned>(p[15]) : 1;
            if (p[17] > 0 && std::abs(x) > .98*p[1]) {
                const double knee=.98*p[1];
                const double atKnee=power(.98,n);
                const double dk=1-atKnee;
                const double fk=knee*(1+p[16]*atKnee/dk)/p[0];
                const double slope=(1+p[16]*atKnee/dk+p[16]*n*atKnee/(dk*dk))/p[0];
                const double targetSlope=1/(p[0]*p[17]);
                const double transition=std::max(.000001,p[1]*.01);
                const double delta=std::abs(x)-knee;
                const double exponential=std::exp(-delta/transition);
                derivative=targetSlope+(slope-targetSlope)*exponential;
                return std::copysign(fk+targetSlope*delta+
                    (slope-targetSlope)*transition*(1-exponential),x);
            }
            const double nonlinear = power(std::abs(x) / p[1], n);
            const double d = 1.0 - nonlinear;
            derivative = (1.0 + p[16] * nonlinear / d + p[16] * n * nonlinear/(d*d)) / p[0];
            return x * (1.0 + p[16] * nonlinear / d) / p[0];
        }
        const unsigned n = static_cast<unsigned>(p[15]);
        const double nonlinear = power(std::abs(x) / p[1], n - 1);
        derivative = (1.0 + n * nonlinear) / p[0];
        return x * (1.0 + nonlinear) / p[0];
    }
    double current(double x, double& derivative, bool advanceStates) {
        double value = law(x, derivative);
        if (p[18] > 0) {
            double oldDerivative;
            const double oldCurrent=law(nonlinearFlux,oldDerivative)-nonlinearFlux/p[0];
            const double rhs=nonlinearFlux+x-lambda-h*p[18]*oldCurrent;
            double lo=-std::abs(rhs)-1e-14,hi=std::abs(rhs)+1e-14;
            if (p[14] > .5 && p[17] <= 0) {
                lo=std::max(lo,-p[1]*(1-1e-12));hi=std::min(hi,p[1]*(1-1e-12));
            }
            double z=bounded(nonlinearFlux+x-lambda,lo,hi),g=0,gprime=0;
            for (unsigned k=0;k<32;++k) {
                g=law(z,gprime)-z/p[0];gprime-=1/p[0];
                const double residual=z+h*p[18]*g-rhs;
                if (residual>0) hi=z;else lo=z;
                if (std::abs(residual)<1e-15*(1+std::abs(z))) break;
                const double next=z-residual/(1+h*p[18]*gprime);
                z=next>lo && next<hi?next:.5*(lo+hi);
            }
            value=x/p[0]+g;
            derivative=1/p[0]+gprime/(1+h*p[18]*gprime);
            if (advanceStates) nonlinearFlux=z;
        }
        if (p[4] > 0) {
            const double z = ((1.0 - relaxation) * relax + relaxation * (x + lambda)) /
                             (1.0 + relaxation);
            value += (x - z) / p[4];
            derivative += 1.0 / ((1.0 + relaxation) * p[4]);
            if (advanceStates) relax = z;
        }
        for (unsigned j = 0; j < branches; ++j) {
            const double tentative = stops[j] + x - lambda;
            const double z = bounded(tentative, -thresholds[j], thresholds[j]);
            value += weights[j] * z;
            if (std::abs(tentative) < thresholds[j]) derivative += weights[j];
            if (advanceStates) stops[j] = z;
        }
        return value;
    }
    double presentCurrent() const {
        double derivative;
        double value = p[18]>0 ? lambda/p[0]+law(nonlinearFlux,derivative)-nonlinearFlux/p[0] : law(lambda, derivative);
        if (p[4] > 0) value += (lambda - relax) / p[4];
        for (unsigned j = 0; j < branches; ++j) value += weights[j] * stops[j];
        return value;
    }
    void refresh(double source) {
        voltage = (source - ra * presentCurrent()) / denominator;
    }
    void step(double source) {
        double hysteresisBound = 0;
        for (unsigned j = 0; j < branches; ++j) hysteresisBound += weights[j] * thresholds[j];
        const double relaxationBound = p[4] > 0 ?
            std::abs((1.0 - relaxation) * relax + relaxation * lambda) /
            ((1.0 + relaxation) * p[4]) : 0;
        double bound = std::abs(lambda + h * voltage) + h *
            (std::abs(source) + ra * (hysteresisBound + relaxationBound)) / denominator + 1e-12;
        if (p[14] > 0.5 && p[17] <= 0) bound = std::min(bound, p[1] * (1.0 - 1e-12));
        double lo = -bound, hi = bound;
        double x = bounded(lambda + 2.0 * h * voltage, lo, hi);
        unsigned iteration = 0;
        for (; iteration < 40; ++iteration) {
            double derivative;
            const double i = current(x, derivative, false);
            const double residual = x - lambda - h * (voltage + (source - ra * i) / denominator);
            if (residual > 0) hi = x; else lo = x;
            if (std::abs(residual) <= 1e-14 * (1.0 + std::abs(x))) break;
            const double newton = x - residual / (1.0 + h * ra * derivative / denominator);
            x = newton > lo && newton < hi ? newton : 0.5 * (lo + hi);
        }
        maxIterations = std::max(maxIterations, iteration + 1);
        double derivative;
        const double i = current(x, derivative, true);
        lambda = x;
        voltage = (source - ra * i) / denominator;
    }
};

std::complex<double> hf(const double* p, double frequency) {
    if (p[7] <= 0) return std::complex<double>(1, 0);
    const double x = frequency / p[7];
    return 1.0 / std::complex<double>(1.0 - x * x, x / p[8]);
}

double periodic(const double* p, double frequency, double amplitude, unsigned steps,
                std::vector<double>& wave, unsigned& iterations) {
    Core initial(p, 1.0 / (frequency * steps));
    // Antiperiodic half-cycle shooting: all laws are odd, zero imposed DC.
    // The finite-time render below does not use shooting or state correction.
    double error = 1;
    for (unsigned shot = 0; shot < 48; ++shot) {
        Core end = initial;
        end.refresh(0);
        for (unsigned i = 1; i <= steps / 2; ++i)
            end.step(amplitude * std::sin(2 * pi * i / steps));
        error = std::max(std::abs(end.lambda + initial.lambda), std::abs(end.relax + initial.relax));
        error = std::max(error,std::abs(end.nonlinearFlux+initial.nonlinearFlux));
        initial.lambda = 0.5 * (initial.lambda - end.lambda);
        initial.relax = 0.5 * (initial.relax - end.relax);
        initial.nonlinearFlux = 0.5 * (initial.nonlinearFlux-end.nonlinearFlux);
        for (unsigned j = 0; j < branches; ++j) {
            error = std::max(error, std::abs(end.stops[j] + initial.stops[j]));
            initial.stops[j] = 0.5 * (initial.stops[j] - end.stops[j]);
        }
        if (error < 5e-13 * (1.0 + amplitude / frequency)) break;
    }
    initial.refresh(0);
    wave.resize(steps * 6);
    for (unsigned i = 0; i < steps; ++i) {
        const double source = amplitude * std::sin(2 * pi * i / steps);
        const double current = initial.presentCurrent() + p[6] * initial.voltage + initial.voltage / initial.rb;
        wave[6*i] = static_cast<double>(i) / (frequency * steps);
        wave[6*i+1] = source;
        wave[6*i+2] = source - p[9] * current;
        wave[6*i+3] = initial.voltage * p[12] / initial.rb;
        wave[6*i+4] = initial.lambda;
        wave[6*i+5] = current;
        initial.step(amplitude * std::sin(2 * pi * (i + 1) / steps));
    }
    iterations = initial.maxIterations;
    return error;
}
}

extern "C" {
// One period, actual instantaneous state currents; filtered harmonics returned separately.
int gs76_transformer_tone(const double* p, double frequency, double dbu, unsigned steps,
                          double* metrics, double* harmonics, double* waveform) {
    if (frequency <= 0 || steps < 128 || steps % 2) return -1;
    const double target = 0.775 * std::pow(10.0, dbu / 20.0);
    double amplitude = std::sqrt(2.0) * target *
        (p[9] + p[10] + p[11] + p[12]) / (p[10] + p[11] + p[12]);
    std::vector<double> wave;
    double error = 1;
    unsigned iterations = 0;
    double primaryRms = 0;
    for (unsigned calibration = 0; calibration < 9; ++calibration) {
        error = periodic(p, frequency, amplitude, steps, wave, iterations);
        double sum = 0;
        for (unsigned i = 0; i < steps; ++i) sum += wave[6*i+2] * wave[6*i+2];
        primaryRms = std::sqrt(sum / steps);
        if (std::abs(primaryRms / target - 1.0) < 1e-9) break;
        amplitude *= target / primaryRms;
    }
    std::complex<double> ports[4][32] = {};
    for (unsigned k = 0; k < 32; ++k) {
        const std::complex<double> increment = std::polar(1.0, -2*pi*k/steps);
        std::complex<double> phase(2.0/steps,0);
        for (unsigned i = 0; i < steps; ++i) {
            ports[0][k] += wave[6*i+1] * phase;
            ports[1][k] += wave[6*i+2] * phase;
            ports[2][k] += wave[6*i+3] * phase;
            ports[3][k] += wave[6*i+5] * phase;
            phase *= increment;
        }
        ports[2][k] *= hf(p, k * frequency);
        if (harmonics) {
            harmonics[2*k] = ports[2][k].real();
            harmonics[2*k+1] = ports[2][k].imag();
        }
    }
    const double fundamental = std::abs(ports[2][1]);
    double thd2 = 0, lambdaPeak = 0, current2 = 0, dc = 0;
    for (unsigned k = 2; k < 32; ++k) thd2 += std::norm(ports[2][k]);
    for (unsigned i = 0; i < steps; ++i) {
        lambdaPeak = std::max(lambdaPeak, std::abs(wave[6*i+4]));
        current2 += wave[6*i+5] * wave[6*i+5];
        dc += wave[6*i+3];
    }
    metrics[0] = 100.0 * std::sqrt(thd2) / fundamental;
    metrics[1] = db(fundamental / std::abs(ports[1][1]));
    metrics[2] = db(fundamental / std::abs(ports[0][1]));
    metrics[3] = std::arg(ports[2][1] / ports[1][1]) * 180.0 / pi;
    metrics[4] = primaryRms;
    metrics[5] = amplitude / std::sqrt(2.0);
    metrics[6] = fundamental / std::sqrt(2.0);
    metrics[7] = lambdaPeak;
    metrics[8] = std::sqrt(current2 / steps);
    metrics[9] = db(std::abs(ports[2][2]) / fundamental);
    metrics[10] = db(std::abs(ports[2][3]) / fundamental);
    metrics[11] = db(std::abs(ports[2][5]) / fundamental);
    metrics[12] = dc / steps;
    metrics[13] = iterations;
    metrics[14] = error;
    metrics[15] = std::abs(ports[1][1] / ports[3][1]);
    if (waveform) std::copy(wave.begin(), wave.end(), waveform);
    for (unsigned i = 0; i < 16; ++i) if (!std::isfinite(metrics[i])) return -2;
    return 0;
}

// Finite-time causal reference; source samples in volts, one state per channel.
// Full reference wave includes raw output, flux and current, with no artificial resets.
int gs76_transformer_render(const double* p, double rate, const double* source,
                            std::size_t count, double* output, double* diagnostic) {
    Core core(p, 1.0 / rate);
    core.refresh(0);
    // Tustin discretization for effective HF surrogate; documented and convergence tested.
    const double w = 2.0 * pi * p[7] / rate;
    const double a0 = 4.0 + 2.0 * w / p[8] + w*w;
    const double a1 = (2.0*w*w - 8.0) / a0;
    const double a2 = (4.0 - 2.0*w/p[8] + w*w) / a0;
    const double b0 = w*w/a0, b1 = 2.0*b0, b2 = b0;
    double x1=0, x2=0, y1=0, y2=0;
    for (std::size_t i = 0; i < count; ++i) {
        core.step(source[i]);
        const double raw = core.voltage * p[12] / core.rb;
        double y = raw;
        if (p[7] > 0) {
            y = b0*raw+b1*x1+b2*x2-a1*y1-a2*y2;
            x2=x1; x1=raw; y2=y1; y1=y;
        }
        output[i] = y;
        if (diagnostic) {
            diagnostic[4*i] = raw;
            diagnostic[4*i+1] = core.lambda;
            diagnostic[4*i+2] = core.presentCurrent();
            diagnostic[4*i+3] = core.maxIterations;
        }
        if (!std::isfinite(y) || !std::isfinite(core.lambda)) return -2;
    }
    return 0;
}
}
