// SPDX-License-Identifier: MIT
// Standalone Green Stripe 76 core throughput bench for the MOD Dwarf.
// Uses the product headers (src/dsp) unchanged, so the measured code is the
// shipped code. Result unit: seconds of process CPU per second of audio, so
// 1.0 = one saturated core. This is the DSP core only, not jackd, not the MOD
// host and not a realtime claim; compare with tools/dwarf_loadtest.py.
#include "dsp/GreenStripe.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {

struct Options {
    double rate = 48000.0;
    double seconds = 3.0;
    double warmupSeconds = 0.1;
    int repeats = 3;
    std::vector<int> transformer{0, 1, 2, 3, 4};
    std::vector<int> oversampling{0};
    std::vector<int> channels{1};
    std::vector<int> instances{1};
    int ratio = 1;
    double inputDb = 6.0;
    double outputDb = 0.0;
    double attack = 3.0;
    double release = 5.0;
    double mix = 100.0;
    double colour = 100.0;
    int compression = 1;
    int link = 1;
    double levelDbfs = -6.0;
    double toneHz = 997.0;
    double noiseMix = 0.0;
    std::string json;
    std::string markdown;
    bool quiet = false;
};

const char* const kTransformerNames[5] = {"None", "60s", "80s", "00s", "Symmetric"};
const char* const kOversamplingNames[3] = {"Off", "2x", "4x"};

std::vector<int> parseList(const std::string& text) {
    std::vector<int> values;
    std::stringstream stream(text);
    std::string item;
    while (std::getline(stream, item, ',')) {
        if (item.empty()) continue;
        values.push_back(std::atoi(item.c_str()));
    }
    return values;
}

Options parse(int argc, char** argv) {
    Options o;
    for (int i = 1; i < argc; ++i) {
        const std::string flag = argv[i];
        const bool hasValue = i + 1 < argc;
        const std::string value = hasValue ? argv[i + 1] : std::string();
        if (flag == "--rate") { o.rate = std::atof(value.c_str()); ++i; }
        else if (flag == "--seconds") { o.seconds = std::atof(value.c_str()); ++i; }
        else if (flag == "--warmup-seconds") { o.warmupSeconds = std::atof(value.c_str()); ++i; }
        else if (flag == "--repeats") { o.repeats = std::max(1, std::atoi(value.c_str())); ++i; }
        else if (flag == "--transformer") { o.transformer = parseList(value); ++i; }
        else if (flag == "--oversampling") { o.oversampling = parseList(value); ++i; }
        else if (flag == "--channels") { o.channels = parseList(value); ++i; }
        else if (flag == "--instances") { o.instances = parseList(value); ++i; }
        else if (flag == "--ratio") { o.ratio = std::atoi(value.c_str()); ++i; }
        else if (flag == "--input-db") { o.inputDb = std::atof(value.c_str()); ++i; }
        else if (flag == "--output-db") { o.outputDb = std::atof(value.c_str()); ++i; }
        else if (flag == "--attack") { o.attack = std::atof(value.c_str()); ++i; }
        else if (flag == "--release") { o.release = std::atof(value.c_str()); ++i; }
        else if (flag == "--mix") { o.mix = std::atof(value.c_str()); ++i; }
        else if (flag == "--colour") { o.colour = std::atof(value.c_str()); ++i; }
        else if (flag == "--compression") { o.compression = std::atoi(value.c_str()); ++i; }
        else if (flag == "--link") { o.link = std::atoi(value.c_str()); ++i; }
        else if (flag == "--level-dbfs") { o.levelDbfs = std::atof(value.c_str()); ++i; }
        else if (flag == "--tone-hz") { o.toneHz = std::atof(value.c_str()); ++i; }
        else if (flag == "--noise-mix") { o.noiseMix = std::atof(value.c_str()); ++i; }
        else if (flag == "--json") { o.json = value; ++i; }
        else if (flag == "--markdown") { o.markdown = value; ++i; }
        else if (flag == "--quiet") { o.quiet = true; }
        else {
            std::cerr << "Unknown or incomplete option: " << flag << '\n';
            std::exit(2);
        }
    }
    if (o.transformer.empty() || o.oversampling.empty() || o.channels.empty() || o.instances.empty()) {
        std::cerr << "Empty sweep list\n";
        std::exit(2);
    }
    return o;
}

double nowSeconds(clockid_t clock) {
    timespec t;
    clock_gettime(clock, &t);
    return static_cast<double>(t.tv_sec) + 1e-9 * static_cast<double>(t.tv_nsec);
}

// Deterministic uniform noise in [-1,1]; the same sequence on every run.
double noise(unsigned long long& state) {
    state = state * 6364136223846793005ULL + 1442695040888963407ULL;
    return 2.0 * (static_cast<double>((state >> 11) & ((1ULL << 53) - 1)) / 9007199254740992.0) - 1.0;
}

struct Measurement {
    double cpuSeconds = 0.0;
    double wallSeconds = 0.0;
    double checksum = 0.0;
    double outputRms = 0.0;
    double peakGainReductionDb = 0.0;
    double solverSamples = 0.0;
    double iterationsPerSample = 0.0;
    double cappedFraction = 0.0;
};

struct Case {
    int transformer = 0;
    int oversampling = 0;
    int channels = 1;
    int instances = 1;
    Measurement measurement;
};

greenstripe::Parameters parameters(const Options& o, int transformer, int oversampling) {
    greenstripe::Parameters p;
    p.ratio = o.ratio;
    p.input = o.inputDb;
    p.output = o.outputDb;
    p.attack = o.attack;
    p.release = o.release;
    p.mix = o.mix;
    p.colour = o.colour;
    p.compression = o.compression != 0;
    p.enabled = true;
    p.stereoLink = o.link != 0;
    p.oversampling = oversampling;
    p.transformer = transformer;
    return p;
}

// One case: `instances` processors stepped frame by frame with an internally
// generated signal, so the measurement needs neither pedalboard nor host.
Measurement runCase(const Options& o, int transformer, int oversampling, int channels, int instances) {
    const bool stereo = channels == 2;
    std::vector<greenstripe::Processor> processors;
    processors.reserve(static_cast<std::size_t>(instances));
    for (int n = 0; n < instances; ++n) {
        processors.push_back(greenstripe::Processor(o.rate, stereo));
        processors.back().setParameters(parameters(o, transformer, oversampling));
    }

    const double amplitude = std::pow(10.0, o.levelDbfs / 20.0);
    const double noiseGain = o.noiseMix * amplitude;
    const double step = 6.283185307179586 * o.toneHz / o.rate;
    unsigned long long state = 0x9e3779b97f4a7c15ULL;
    const unsigned long long warmupFrames =
        static_cast<unsigned long long>(o.warmupSeconds * o.rate);
    const unsigned long long frames = static_cast<unsigned long long>(o.seconds * o.rate);

    double peakGainReduction = 0.0;
    double rms = 0.0;
    double checksum = 0.0;

    // Warmup: coefficient preparation, filter settling and the first transform
    // states are not part of steady-state cost. The solver counters are cleared
    // afterwards so the reported average describes the measured window only.
    for (unsigned long long f = 0; f < warmupFrames; ++f) {
        const double x = amplitude * std::sin(step * static_cast<double>(f));
        double left = 0.0, right = 0.0;
        for (int n = 0; n < instances; ++n) {
            const double r = noise(state) * noiseGain;
            processors[static_cast<std::size_t>(n)].sample(x, x * 0.7 + r, left, right);
            checksum += left + right;
        }
    }
    for (int n = 0; n < instances; ++n) {
#ifdef GS76_TRANSFORMER_STATS
        processors[static_cast<std::size_t>(n)].clearTransformerStats();
#endif
    }

    const double wallStart = nowSeconds(CLOCK_MONOTONIC);
    const double cpuStart = nowSeconds(CLOCK_PROCESS_CPUTIME_ID);
    for (unsigned long long f = 0; f < frames; ++f) {
        const double x = amplitude * std::sin(step * static_cast<double>(f));
        double left = 0.0, right = 0.0;
        for (int n = 0; n < instances; ++n) {
            const double r = noise(state) * noiseGain;
            processors[static_cast<std::size_t>(n)].sample(x, x * 0.7 + r, left, right);
            rms += left * left + right * right;
            // Gain reduction is negative dB, so the deepest reduction is the minimum.
            peakGainReduction = std::min(peakGainReduction,
                processors[static_cast<std::size_t>(n)].gainReduction());
        }
    }
    const double cpuElapsed = nowSeconds(CLOCK_PROCESS_CPUTIME_ID) - cpuStart;
    const double wallElapsed = nowSeconds(CLOCK_MONOTONIC) - wallStart;

    Measurement m;
    // CPU seconds per second of audio: elapsed CPU divided by the audio duration.
    m.cpuSeconds = cpuElapsed * o.rate / static_cast<double>(frames);
    m.wallSeconds = wallElapsed * o.rate / static_cast<double>(frames);
    m.checksum = checksum;
    m.outputRms = std::sqrt(rms / (2.0 * static_cast<double>(frames)));
    m.peakGainReductionDb = peakGainReduction;
#ifdef GS76_TRANSFORMER_STATS
    unsigned long long iterations = 0, samples = 0, capped = 0;
    for (int n = 0; n < instances; ++n) {
        for (unsigned c = 0; c < (stereo ? 2u : 1u); ++c) {
            const greenstripe::TransformerSolverStats& s =
                processors[static_cast<std::size_t>(n)].transformerStats(c);
            iterations += s.iterations;
            samples += s.samples;
            capped += s.capped;
        }
    }
    m.solverSamples = static_cast<double>(samples);
    m.iterationsPerSample = samples ? static_cast<double>(iterations) / static_cast<double>(samples) : 0.0;
    m.cappedFraction = samples ? static_cast<double>(capped) / static_cast<double>(samples) : 0.0;
#endif
    return m;
}

double median(std::vector<double> values) {
    if (values.empty()) return 0.0;
    std::sort(values.begin(), values.end());
    const std::size_t middle = values.size() / 2;
    return values.size() % 2 ? values[middle] : 0.5 * (values[middle - 1] + values[middle]);
}

std::string jsonNumber(double value) {
    std::ostringstream out;
    out << std::setprecision(10) << value;
    return out.str();
}

void writeJson(const Options& o, const std::vector<Case>& cases) {
    std::ofstream file(o.json.c_str());
    file << "{\n";
    file << "  \"tool\": \"tools/transformer_bench.cpp\",\n";
    file << "  \"unit\": \"process CPU seconds per audio second; 1.0 = one saturated core\",\n";
    file << "  \"compiler\": \"" << __VERSION__ << "\",\n";
#ifdef GS76_TRANSFORMER_STATS
    file << "  \"solver_stats\": true,\n";
#else
    file << "  \"solver_stats\": false,\n";
#endif
    file << "  \"protocol\": {\n";
    file << "    \"rate\": " << jsonNumber(o.rate) << ",\n";
    file << "    \"audio_seconds_per_case\": " << jsonNumber(o.seconds) << ",\n";
    file << "    \"warmup_seconds\": " << jsonNumber(o.warmupSeconds) << ",\n";
    file << "    \"repeats\": " << o.repeats << ",\n";
    file << "    \"ratio\": " << o.ratio << ",\n";
    file << "    \"input_db\": " << jsonNumber(o.inputDb) << ",\n";
    file << "    \"output_db\": " << jsonNumber(o.outputDb) << ",\n";
    file << "    \"attack\": " << jsonNumber(o.attack) << ",\n";
    file << "    \"release\": " << jsonNumber(o.release) << ",\n";
    file << "    \"mix\": " << jsonNumber(o.mix) << ",\n";
    file << "    \"colour\": " << jsonNumber(o.colour) << ",\n";
    file << "    \"compression\": " << o.compression << ",\n";
    file << "    \"stereo_link\": " << o.link << ",\n";
    file << "    \"signal\": {\"level_dbfs\": " << jsonNumber(o.levelDbfs)
         << ", \"tone_hz\": " << jsonNumber(o.toneHz)
         << ", \"noise_mix\": " << jsonNumber(o.noiseMix) << "}\n";
    file << "  },\n";
    file << "  \"limitations\": \"DSP core only, single thread, no jackd/MOD host, no audio "
            "hardware, no xrun statement. Per-sample solver cost depends on signal level and "
            "profile; the numbers are not a Dwarf result unless run on the Dwarf.\",\n";
    file << "  \"cases\": [\n";
    for (std::size_t i = 0; i < cases.size(); ++i) {
        const Case& c = cases[i];
        const Measurement& m = c.measurement;
        file << "    {\"transformer\": " << c.transformer
             << ", \"transformer_name\": \"" << kTransformerNames[c.transformer]
             << "\", \"oversampling\": " << c.oversampling
             << ", \"oversampling_name\": \"" << kOversamplingNames[c.oversampling]
             << "\", \"channels\": \"" << (c.channels == 2 ? "stereo" : "mono")
             << "\", \"instances\": " << c.instances
             << ", \"cpu_seconds_per_audio_second\": " << jsonNumber(m.cpuSeconds)
             << ", \"cpu_seconds_per_audio_second_per_instance\": "
             << jsonNumber(m.cpuSeconds / c.instances)
             << ", \"wall_seconds_per_audio_second\": " << jsonNumber(m.wallSeconds)
             << ", \"cpu_percent_of_one_core_per_instance\": "
             << jsonNumber(100.0 * m.cpuSeconds / c.instances)
             << ", \"solver_iterations_per_sample\": " << jsonNumber(m.iterationsPerSample)
             << ", \"solver_capped_fraction\": " << jsonNumber(m.cappedFraction)
             << ", \"peak_gain_reduction_db\": " << jsonNumber(m.peakGainReductionDb)
             << ", \"output_rms\": " << jsonNumber(m.outputRms)
             << ", \"checksum\": " << jsonNumber(m.checksum) << "}"
             << (i + 1 == cases.size() ? "\n" : ",\n");
    }
    file << "  ]\n}\n";
}

void writeMarkdown(const Options& o, const std::vector<Case>& cases) {
    std::ofstream file(o.markdown.c_str());
    file << "# Green Stripe 76 — Standalone-Core-Bench (Dwarf-Lauf)\n\n";
    file << "Einheit: Prozess-CPU-Sekunden je Audio-Sekunde, 1.0 = ein voll belasteter Kern.\n";
    file << "Nur DSP-Kern, ein Thread, ohne jackd, ohne MOD-Host, ohne xruns.\n\n";
    file << "- Rate: " << o.rate << " Hz, " << o.seconds << " s je Fall, "
         << o.repeats << " Wiederholungen, Median.\n";
    file << "- Regler: Ratio-Index " << o.ratio << ", Input " << o.inputDb << " dB, Output "
         << o.outputDb << " dB, Attack " << o.attack << ", Release " << o.release
         << ", Mix " << o.mix << ", Colour " << o.colour << ".\n";
    file << "- Signal: " << o.levelDbfs << " dBFS Sinus " << o.toneHz << " Hz, Rauschanteil "
         << o.noiseMix << ".\n";
    file << "- Fester Signalpegel: Der Solver bricht nach iterationen ab, deshalb ist die\n";
    file << "  Iterationszahl und damit die Last pegel- und profilabhängig.\n\n";
    file << "| Transformator | OS | Kanäle | Instanzen | CPU s/s | je Instanz s/s | Kern %/Instanz |"
            " Iterationen/Probe | Anteil am 40er-Limit | Spitzen-GR dB | Ausgang RMS |\n";
    file << "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n";
    for (std::size_t i = 0; i < cases.size(); ++i) {
        const Case& c = cases[i];
        const Measurement& m = c.measurement;
        file << "| " << kTransformerNames[c.transformer] << " | " << kOversamplingNames[c.oversampling]
             << " | " << (c.channels == 2 ? "Stereo" : "Mono") << " | " << c.instances << " | "
             << std::fixed << std::setprecision(5) << m.cpuSeconds << " | "
             << m.cpuSeconds / c.instances << " | " << 100.0 * m.cpuSeconds / c.instances << " | "
             << std::setprecision(2) << m.iterationsPerSample << " | "
             << 100.0 * m.cappedFraction << "% | " << std::setprecision(2) << m.peakGainReductionDb
             << " | " << std::setprecision(4) << m.outputRms << " |\n";
    }
    file << "\n## Grenzen\n\n";
    file << "- Diese Zahlen sind **keine** Dwarf-Messung, solange der Lauf nicht auf dem\n";
    file << "  Dwarf mit dessen Compiler und Flags entstanden ist.\n";
    file << "- Kein Echtzeit-, xrun- oder Hörtest; der Bench umgeht den Plugin-Host.\n";
    file << "- Nur der Kern. jackd, LV2-Wrapper und alle anderen Pedale einer Kette\n";
    file << "  kommen in `tools/dwarf_loadtest.py` dazu.\n";
}

} // namespace

int main(int argc, char** argv) {
    const Options o = parse(argc, argv);
    std::vector<Case> cases;
    for (std::size_t t = 0; t < o.transformer.size(); ++t) {
        for (std::size_t s = 0; s < o.oversampling.size(); ++s) {
            for (std::size_t c = 0; c < o.channels.size(); ++c) {
                for (std::size_t n = 0; n < o.instances.size(); ++n) {
                    Case kase;
                    kase.transformer = o.transformer[t];
                    kase.oversampling = o.oversampling[s];
                    kase.channels = o.channels[c];
                    kase.instances = o.instances[n];
                    std::vector<double> cpu, wall, rms, iterations, capped;
                    for (int r = 0; r < o.repeats; ++r) {
                        const Measurement m = runCase(o, kase.transformer, kase.oversampling,
                                                      kase.channels, kase.instances);
                        cpu.push_back(m.cpuSeconds);
                        wall.push_back(m.wallSeconds);
                        rms.push_back(m.outputRms);
                        iterations.push_back(m.iterationsPerSample);
                        capped.push_back(m.cappedFraction);
                        kase.measurement = m;
                    }
                    kase.measurement.cpuSeconds = median(cpu);
                    kase.measurement.wallSeconds = median(wall);
                    kase.measurement.outputRms = median(rms);
                    kase.measurement.iterationsPerSample = median(iterations);
                    kase.measurement.cappedFraction = median(capped);
                    cases.push_back(kase);
                    if (!o.quiet) {
                        std::cout << kTransformerNames[kase.transformer] << " OS="
                                  << kOversamplingNames[kase.oversampling] << " "
                                  << (kase.channels == 2 ? "stereo" : "mono  ") << " x"
                                  << kase.instances << "  cpu=" << std::fixed
                                  << std::setprecision(5) << kase.measurement.cpuSeconds
                                  << " s/s  je Instanz=" << kase.measurement.cpuSeconds / kase.instances
                                  << " s/s (" << std::setprecision(2)
                                  << 100.0 * kase.measurement.cpuSeconds / kase.instances
                                  << " % Kern)" << std::setprecision(2)
                                  << "  Iter/Probe=" << kase.measurement.iterationsPerSample
                                  << "  40er-Limit=" << 100.0 * kase.measurement.cappedFraction
                                  << " %" << std::setprecision(1) << "  GRmax="
                                  << kase.measurement.peakGainReductionDb << " dB\n";
                    }
                }
            }
        }
    }
    if (!o.json.empty()) {
        writeJson(o, cases);
        if (!o.quiet) std::cout << "JSON: " << o.json << '\n';
    }
    if (!o.markdown.empty()) {
        writeMarkdown(o, cases);
        if (!o.quiet) std::cout << "Markdown: " << o.markdown << '\n';
    }
    return 0;
}