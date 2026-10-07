// SPDX-License-Identifier: MIT
// Offline-Renderer fuer die REAPER-Testbench-Renders: laedt das JSFX ueber
// ysfx (der gepinnte Referenz-Host), setzt die 13 Slider und rendert eine
// WAV-Datei. Ausgabe: IEEE-float WAV (wie tools/render_lv2.py), damit der
// Vergleich gegen die C++-Referenzen bitgenau laufen kann.
//
//   render_jsfx --jsfx jsfx/GreenStripe76-Stereo.jsfx --input in.wav --output out.wav \
//     --set colour=0 --set transformer=1 --set compression=0 ...
//
// Slider-Zuordnung (ysfx-Index = sliderN - 1):
//   0 input, 1 output, 2 attack, 3 release, 4 ratio, 5 mix, 6 colour,
//   7 compression, 8 enabled, 9 link, 10 preset, 11 oversampling, 12 transformer
#include "ysfx.h"

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace {

struct Options {
    std::string jsfx;
    std::string input;
    std::string output;
    double sliders[13] = {0, 0, 7, 7, 1, 100, 0, 0, 1, 1, 0, 1, 0};
    double rate = 48000.0;
};

Options parse(int argc, char** argv) {
    Options o;
    for (int i = 1; i < argc; ++i) {
        const std::string flag = argv[i];
        const bool hasValue = i + 1 < argc;
        const std::string value = hasValue ? argv[i + 1] : std::string();
        if (flag == "--jsfx") { o.jsfx = value; ++i; }
        else if (flag == "--input") { o.input = value; ++i; }
        else if (flag == "--output") { o.output = value; ++i; }
        else if (flag == "--rate") { o.rate = std::atof(value.c_str()); ++i; }
        else if (flag == "--set") {
            const std::string names[13] = {"input", "output", "attack", "release", "ratio",
                "mix", "colour", "compression", "enabled", "link", "preset",
                "oversampling", "transformer"};
            const std::string::size_type eq = value.find('=');
            if (eq == std::string::npos) { std::fprintf(stderr, "bad --set: %s\n", value.c_str()); std::exit(2); }
            const std::string name = value.substr(0, eq);
            const double v = std::atof(value.c_str() + eq + 1);
            bool found = false;
            for (unsigned k = 0; k < 13; ++k) {
                if (name == names[k]) { o.sliders[k] = v; found = true; break; }
            }
            if (!found) { std::fprintf(stderr, "unbekannter Regler: %s\n", name.c_str()); std::exit(2); }
            ++i;
        } else {
            std::fprintf(stderr, "Unknown option: %s\n", flag.c_str());
            std::exit(2);
        }
    }
    return o;
}

// Minimaler WAV-Leser: PCM 24 bit oder IEEE float, Stereo.
bool readWav(const std::string& path, std::vector<double>& left, std::vector<double>& right, double& rate) {
    std::FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    unsigned char header[12];
    if (std::fread(header, 1, 12, f) != 12 || std::memcmp(header, "RIFF", 4) != 0 ||
        std::memcmp(header + 8, "WAVE", 4) != 0) { std::fclose(f); return false; }
    unsigned fmtTag = 0, channels = 0, sampleRate = 0, bits = 0;
    long dataOffset = -1; unsigned dataLength = 0;
    for (;;) {
        unsigned char chunk[8];
        if (std::fread(chunk, 1, 8, f) != 8) break;
        unsigned size = (unsigned)chunk[4] | ((unsigned)chunk[5] << 8) |
                        ((unsigned)chunk[6] << 16) | ((unsigned)chunk[7] << 24);
        if (std::memcmp(chunk, "fmt ", 4) == 0) {
            unsigned char fmt[16];
            if (size < 16 || std::fread(fmt, 1, 16, f) != 16) break;
            if (size > 16) std::fseek(f, (long)(size - 16), SEEK_CUR);
            fmtTag = (unsigned)fmt[0] | ((unsigned)fmt[1] << 8);
            channels = (unsigned)fmt[2] | ((unsigned)fmt[3] << 8);
            sampleRate = (unsigned)fmt[4] | ((unsigned)fmt[5] << 8) |
                         ((unsigned)fmt[6] << 16) | ((unsigned)fmt[7] << 24);
            bits = (unsigned)fmt[14] | ((unsigned)fmt[15] << 8);
        } else if (std::memcmp(chunk, "data", 4) == 0) {
            dataOffset = std::ftell(f);
            dataLength = size;
            break;
        } else {
            std::fseek(f, (long)((size + 1) & ~1u), SEEK_CUR);
        }
    }
    if (dataOffset < 0 || channels != 2 || (bits != 24 && bits != 32)) { std::fclose(f); return false; }
    rate = sampleRate;
    const unsigned frames = dataLength / (channels * (bits / 8));
    left.resize(frames); right.resize(frames);
    std::fseek(f, dataOffset, SEEK_SET);
    if (bits == 24) {
        std::vector<unsigned char> raw((std::size_t)frames * 6);
        if (std::fread(raw.data(), 1, raw.size(), f) != raw.size()) { std::fclose(f); return false; }
        for (unsigned i = 0; i < frames; ++i) {
            const unsigned char* l = raw.data() + (std::size_t)i * 6;
            const unsigned char* r = l + 3;
            const std::int32_t lv = (std::int32_t)l[0] | ((std::int32_t)l[1] << 8) |
                ((std::int32_t)l[2] << 16);
            const std::int32_t rv = (std::int32_t)r[0] | ((std::int32_t)r[1] << 8) |
                ((std::int32_t)r[2] << 16);
            left[i] = (lv & 0x800000 ? lv - 0x1000000 : lv) / 8388608.0;
            right[i] = (rv & 0x800000 ? rv - 0x1000000 : rv) / 8388608.0;
        }
    } else {
        std::vector<float> raw((std::size_t)frames * 2);
        if (std::fread(raw.data(), 4, raw.size() / 2, f) != raw.size() / 2) { std::fclose(f); return false; }
        for (unsigned i = 0; i < frames; ++i) { left[i] = raw[2 * i]; right[i] = raw[2 * i + 1]; }
    }
    std::fclose(f);
    return true;
}

bool writeFloatWav(const std::string& path, const std::vector<float>& data, unsigned rate, unsigned channels) {
    std::FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) return false;
    const unsigned byteRate = rate * channels * 4;
    const unsigned dataLength = (unsigned)data.size() * 4;
    std::fwrite("RIFF", 1, 4, f);
    const unsigned riffSize = 36 + dataLength;
    std::fputc(riffSize & 0xFF, f); std::fputc((riffSize >> 8) & 0xFF, f);
    std::fputc((riffSize >> 16) & 0xFF, f); std::fputc((riffSize >> 24) & 0xFF, f);
    std::fwrite("WAVEfmt ", 1, 8, f);
    const unsigned fmtSize = 16;
    std::fputc(fmtSize & 0xFF, f); std::fputc((fmtSize >> 8) & 0xFF, f);
    std::fputc((fmtSize >> 16) & 0xFF, f); std::fputc((fmtSize >> 24) & 0xFF, f);
    const unsigned fmtTag = 3;
    std::fputc(fmtTag & 0xFF, f); std::fputc(0, f);
    std::fputc(channels & 0xFF, f); std::fputc(0, f);
    std::fputc(rate & 0xFF, f); std::fputc((rate >> 8) & 0xFF, f);
    std::fputc((rate >> 16) & 0xFF, f); std::fputc((rate >> 24) & 0xFF, f);
    std::fputc(byteRate & 0xFF, f); std::fputc((byteRate >> 8) & 0xFF, f);
    std::fputc((byteRate >> 16) & 0xFF, f); std::fputc((byteRate >> 24) & 0xFF, f);
    const unsigned blockAlign = channels * 4;
    std::fputc(blockAlign & 0xFF, f); std::fputc((blockAlign >> 8) & 0xFF, f);
    std::fputc(32, f); std::fputc(0, f);
    std::fwrite("data", 1, 4, f);
    std::fputc(dataLength & 0xFF, f); std::fputc((dataLength >> 8) & 0xFF, f);
    std::fputc((dataLength >> 16) & 0xFF, f); std::fputc((dataLength >> 24) & 0xFF, f);
    std::fwrite(data.data(), 4, data.size(), f);
    std::fclose(f);
    return true;
}

} // namespace

int main(int argc, char** argv) {
    Options o = parse(argc, argv);
    std::vector<double> left, right;
    double rate = 0;
    if (!readWav(o.input, left, right, rate)) { std::fprintf(stderr, "WAV-Lesefehler: %s\n", o.input.c_str()); return 1; }
    if (rate != o.rate) { std::fprintf(stderr, "Rate-Abweichung: WAV %g, angegeben %g\n", rate, o.rate); return 1; }

    ysfx_config_u config(ysfx_config_new());
    ysfx_u fx(ysfx_new(config.get()));
    if (!ysfx_load_file(fx.get(), o.jsfx.c_str(), 0) ||
        !ysfx_compile(fx.get(), ysfx_compile_no_gfx)) {
        std::fprintf(stderr, "JSFX-Ladefehler: %s\n", o.jsfx.c_str()); return 1;
    }
    ysfx_set_sample_rate(fx.get(), o.rate);
    ysfx_set_block_size(fx.get(), 128);
    for (unsigned index = 0; index < 13; ++index)
        ysfx_slider_set_value(fx.get(), index, o.sliders[index], true);
    ysfx_init(fx.get());

    const std::size_t frames = left.size();
    std::vector<float> out(frames * 2);
    const unsigned blockSize = 128;
    for (std::size_t offset = 0; offset < frames; offset += blockSize) {
        const unsigned count = (unsigned)std::min<std::size_t>(blockSize, frames - offset);
        float inL[128], inR[128], outL[128], outR[128];
        for (unsigned i = 0; i < count; ++i) { inL[i] = (float)left[offset + i]; inR[i] = (float)right[offset + i]; }
        float* in[2] = {inL, inR};
        float* outp[2] = {outL, outR};
        ysfx_process_float(fx.get(), in, outp, 2, 2, count);
        for (unsigned i = 0; i < count; ++i) { out[2 * (offset + i)] = outL[i]; out[2 * (offset + i) + 1] = outR[i]; }
    }
    if (!writeFloatWav(o.output, out, (unsigned)o.rate, 2)) { std::fprintf(stderr, "WAV-Schreibfehler\n"); return 1; }
    std::printf("%s\n", o.output.c_str());
    return 0;
}
