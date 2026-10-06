// SPDX-License-Identifier: MIT
// Included inside namespace greenstripe, after the shared numeric helpers.
// Load-coupled flux model from the independent offline reference, with bounded
// Newton iterations and matched-pole HF discretization; see TRANSFORMER_RUNTIME.
struct TransformerCoefficients {
    const transformer_model::Profile* p;
    double h, ra, denominator, relaxation, weights[14], memoryBound;
    double a1, a2, b0, b1, outputScale;
    static double cosine(double x) {
        // Initialization only; identical fixed operation order in EEL2.
        const double x2 = x*x;
        double y = 1.0/6402373705728000.0;
        y = -1.0/20922789888000.0+x2*y;
        y = 1.0/87178291200.0+x2*y;
        y = -1.0/479001600.0+x2*y;
        y = 1.0/3628800.0+x2*y;
        y = -1.0/40320.0+x2*y;
        y = 1.0/720.0+x2*y;
        y = -1.0/24.0+x2*y;
        y = 0.5+x2*y;
        return 1.0-x2*y;
    }
    void prepare(double rate, unsigned modelIndex) {
        p = &transformer_model::profiles[modelIndex];
        h = 0.5/rate;
        ra = p->source_resistance_ohm+p->primary_resistance_ohm;
        const double rb = p->secondary_resistance_ohm+p->load_resistance_ohm;
        denominator = 1.0+ra/rb+ra*p->core_conductance_s;
        relaxation = h*6.283185307179586*p->relax_frequency_hz;
        memoryBound = 0;
        for (unsigned j=0; j<14; ++j) {
            weights[j] = p->hysteresis_enabled*p->hysteresis_stiffness_a_per_vs*
                seriesExp(p->hysteresis_slope*seriesLog(transformer_model::thresholds[j]/0.001));
            memoryBound += weights[j]*transformer_model::thresholds[j];
        }
        // Matched analog poles, then a minimum-phase real zero fitted at
        // min(20 kHz, 0.4 fs). Unlike raw Tustin this does not force a zero at
        // Nyquist when the analog corner is above Nyquist.
        const double w = 6.283185307179586*p->hf_frequency_hz/rate;
        const double decay = seriesExp(-std::min(60.0,w/(2.0*p->hf_q)));
        double angle = w*std::sqrt(1.0-1.0/(4.0*p->hf_q*p->hf_q));
        angle -= 6.283185307179586*std::floor(angle/6.283185307179586+0.5);
        a1 = -2.0*decay*cosine(angle); a2 = decay*decay;
        const double frequency = std::min(20000.0,rate*0.4);
        const double c = cosine(6.283185307179586*frequency/rate);
        const double r = frequency/p->hf_frequency_hz;
        const double magnitude2 = 1.0/((1.0-r*r)*(1.0-r*r)+r*r/(p->hf_q*p->hf_q));
        const double den2 = 1.0+a1*a1+a2*a2+2.0*a1*(1.0+a2)*c+2.0*a2*(2.0*c*c-1.0);
        const double sum = 1.0+a1+a2;
        const double product = (sum*sum-magnitude2*den2)/(2.0*(1.0-c));
        b0 = 0.5*(sum+std::sqrt(std::max(0.0,sum*sum-4.0*product)));
        b1 = sum-b0;
        outputScale = p->load_resistance_ohm/rb*p->fixed_output_normalization/p->source_volts_per_fs;
    }
};

struct TransformerBank {
    TransformerCoefficients c[3][4];
    explicit TransformerBank(double rate) {
        for (unsigned os=0; os<3; ++os)
            for (unsigned m=0; m<4; ++m) c[os][m].prepare(rate*(1u<<os),m);
    }
};

// Opt-in diagnostic counter for the bounded solver. Compiled out unless
// GS76_TRANSFORMER_STATS is defined, so no released build changes; the counter
// is a plain integer add and cannot alter the solved value. reset() clears it,
// so a mid-run model change or bypass restarts the count.
#ifdef GS76_TRANSFORMER_STATS
struct TransformerSolverStats {
    unsigned iterations, samples, capped;
    void clear() { iterations = samples = capped = 0; }
};
#endif

struct TransformerCore {
    double flux, relax, voltage, stops[14], x1, y1, y2;
#ifdef GS76_TRANSFORMER_STATS
    TransformerSolverStats stats;
#endif
    void reset() {
        flux=relax=voltage=x1=y1=y2=0;
        for (unsigned j=0; j<14; ++j) stops[j]=0;
#ifdef GS76_TRANSFORMER_STATS
        stats.clear();
#endif
    }
    static double law(double x, const transformer_model::Profile& p, double& slope) {
        const double u=std::abs(x)/p.flux_scale_vs;
        if (p.family==1) {
            if (u>0.98) {
                const double knee=0.98*p.flux_scale_vs;
                const double fk=knee*(1.0+p.saturation_strength*0.98/0.02)/p.lm_h;
                const double sk=(1.0+p.saturation_strength*0.98/0.02+
                    p.saturation_strength*0.98/(0.02*0.02))/p.lm_h;
                const double target=1.0/(p.lm_h*p.high_field_l_ratio);
                const double width=std::max(0.000001,p.flux_scale_vs*0.01);
                const double delta=std::abs(x)-knee;
                const double e=seriesExp(-std::min(60.0,delta/width));
                slope=target+(sk-target)*e;
                const double value=fk+target*delta+(sk-target)*width*(1.0-e);
                return x>=0 ? value : -value;
            }
            const double d=1.0-u;
            slope=(1.0+p.saturation_strength*u/d+p.saturation_strength*u/(d*d))/p.lm_h;
            return x*(1.0+p.saturation_strength*u/d)/p.lm_h;
        }
        double nonlinear=1;
        for (unsigned i=1; i<static_cast<unsigned>(p.exponent); ++i) nonlinear*=u;
        nonlinear*=p.saturation_strength;
        slope=(1.0+p.exponent*nonlinear)/p.lm_h;
        return x*(1.0+nonlinear)/p.lm_h;
    }
    double current(double x, const TransformerCoefficients& c, double& derivative, bool advance) {
        double value=law(x,*c.p,derivative);
        const double z=((1.0-c.relaxation)*relax+c.relaxation*(x+flux))/(1.0+c.relaxation);
        value+=(x-z)/c.p->relax_l_h;
        derivative+=1.0/((1.0+c.relaxation)*c.p->relax_l_h);
        if (advance) relax=zap(z);
        for (unsigned j=0; j<14; ++j) {
            const double trial=stops[j]+x-flux;
            const double stop=bounded(trial,-transformer_model::thresholds[j],transformer_model::thresholds[j]);
            value+=c.weights[j]*stop;
            if (std::abs(trial)<transformer_model::thresholds[j]) derivative+=c.weights[j];
            if (advance) stops[j]=zap(stop);
        }
        return value;
    }
    double process(double input, const TransformerCoefficients& c) {
        const double source=input*c.p->source_volts_per_fs;
        const double rb=std::abs((1.0-c.relaxation)*relax+c.relaxation*flux)/
            ((1.0+c.relaxation)*c.p->relax_l_h);
        const double bound=std::abs(flux+c.h*voltage)+c.h*
            (std::abs(source)+c.ra*(c.memoryBound+rb))/c.denominator+1e-12;
        double lo=-bound, hi=bound, x=bounded(flux+2.0*c.h*voltage,lo,hi);
#ifdef GS76_TRANSFORMER_STATS
        unsigned usedIterations=0;
#endif
        for (unsigned iteration=0; iteration<40; ++iteration) {
#ifdef GS76_TRANSFORMER_STATS
            ++usedIterations;
#endif
            double derivative;
            const double i=current(x,c,derivative,false);
            const double residual=x-flux-c.h*(voltage+(source-c.ra*i)/c.denominator);
            if (std::abs(residual)<=1e-14*(1.0+std::abs(x))) break;
            if (residual>0) hi=x; else lo=x;
            const double next=x-residual/(1.0+c.h*c.ra*derivative/c.denominator);
            x=next>lo && next<hi ? next : 0.5*(lo+hi);
        }
#ifdef GS76_TRANSFORMER_STATS
        stats.iterations+=usedIterations; ++stats.samples;
        if (usedIterations>=40) ++stats.capped;
#endif
        double derivative;
        const double i=current(x,c,derivative,true);
        flux=zap(x); voltage=zap((source-c.ra*i)/c.denominator);
        const double raw=voltage*c.outputScale;
        const double y=c.b0*raw+c.b1*x1-c.a1*y1-c.a2*y2;
        x1=raw; y2=y1; y1=zap(y);
        return y;
    }
};

struct TransformerStage {
    TransformerCore core;
    int active, requested;
    double blend;
    void reset(int model=0) { core.reset(); active=requested=model; blend=model ? 1.0 : 0.0; }
    double process(double x, int selected, const TransformerCoefficients* bank, double rate) {
        if (!active && !selected) return x;
        requested=selected;
        const double step=1.0/std::max(1.0,std::ceil(0.002*rate));
        if (active!=requested) {
            blend=std::max(0.0,blend-step);
            if (blend<=1e-12) { blend=0; active=requested; core.reset(); }
        } else blend=std::min(active ? 1.0 : 0.0,blend+step);
        if (!active) return x;
        const double y=core.process(x,bank[active-1]);
        return x+blend*(y-x);
    }
};
