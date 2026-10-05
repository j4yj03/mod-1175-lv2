#!/usr/bin/env python3
"""Generate, record and analyse Scarlett 2i2 analog-loop test signals.

Offline: numpy + soundfile. Live recording additionally needs sounddevice.
See docs/SCARLETT_TEST.md for wiring, calibration and measurement limits.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import soundfile as sf

SCHEMA = 1
FREQUENCIES = (20, 40, 80, 160, 315, 630, 1000, 2000, 4000, 8000, 12000, 16000, 20000)


def db(value):
    return 20 * math.log10(max(float(value), 1e-15))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def fade(signal, frames):
    window = np.sin(np.linspace(0, np.pi / 2, frames)) ** 2
    signal[:frames] *= window
    signal[-frames:] *= window[::-1]
    return signal


def generate(directory, rate=48000, level=-18, kind='tone', frequency=1000,
             settle=0.75, measure=1.0):
    if rate not in (44100, 48000, 96000):
        raise ValueError('Supported rates: 44100, 48000, 96000 Hz')
    if not math.isfinite(level) or not -60 <= level <= -3:
        raise ValueError('Peak level must be between -60 and -3 dBFS')
    if not 0.25 <= settle <= 10 or not 0.25 <= measure <= 10:
        raise ValueError('Settle/measurement duration must be 0.25..10 seconds')
    if not math.isfinite(frequency) or not 20 <= frequency <= min(20000, rate * .45):
        raise ValueError('Tone frequency outside supported audio band')
    if kind not in ('tone', 'sweep', 'levels', 'all'):
        raise ValueError('Unknown test kind')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    parts = []
    position = 0

    def append(x):
        nonlocal position
        start = position
        parts.append(x)
        position += len(x)
        return start

    def silence(seconds):
        return append(np.zeros(round(rate * seconds)))

    silence(.5)
    t = np.arange(round(.12 * rate)) / rate
    pilot = fade(10 ** (min(level, -18) / 20) * np.sin(2 * np.pi *
                 (500 * t + (6000 - 500) / (.24) * t * t)), round(.01 * rate))
    markers = [dict(start=append(pilot), frames=len(pilot))]
    silence(.5)
    requested = []
    if kind in ('tone', 'all'):
        requested.append(('tone', frequency, level))
    if kind in ('sweep', 'all'):
        requested += [('sweep', f, level) for f in FREQUENCIES if f < rate * .45]
    if kind in ('levels', 'all'):
        requested += [('levels', frequency, x) for x in (level - 24, level - 18, level - 12, level - 6, level)]
    segments = []
    measurement_frames = round(measure * rate)
    settle_frames = round(settle * rate)
    ramp = round(.02 * rate)
    for index, (group, freq, peak_db) in enumerate(requested):
        # Coherent stimulus; actual quantized frequency is stored in the plan.
        freq = round(freq * measurement_frames / rate) * rate / measurement_frames
        n = np.arange(settle_frames + measurement_frames + ramp)
        tone = fade(10 ** (peak_db / 20) * np.sin(2 * np.pi * freq * n / rate), ramp)
        start = append(tone)
        segments.append(dict(id=index + 1, group=group, frequency_hz=freq, peak_dbfs=peak_db,
                             start=start, frames=len(tone), measurement_start=start + settle_frames,
                             measurement_frames=measurement_frames))
        silence(.15)
    silence(.5)
    markers.append(dict(start=append(pilot[::-1].copy()), frames=len(pilot)))
    # Tail allows a full round trip up to --max-delay (default 2 s).
    silence(2.5)
    stimulus = np.concatenate(parts)
    sf.write(str(directory / 'stimulus.wav'), stimulus, rate, subtype='PCM_24')
    plan = dict(schema_version=SCHEMA, created_utc=datetime.now(timezone.utc).isoformat(),
                rate=rate, kind=kind, peak_level_dbfs=level, frames=len(stimulus),
                markers=markers, segments=segments, stimulus_sha256=sha(directory / 'stimulus.wav'),
                script_sha256=sha(__file__), level_reference='digital peak dBFS, not calibrated volts/dBu')
    write_json(directory / 'plan.json', plan)
    return plan


def correlation_marker(signal, pattern, low, high):
    """Normalized FFT correlation; absolute peak supports inverted loop wiring."""
    low = max(0, int(low))
    high = min(len(signal) - len(pattern), int(high))
    if high < low:
        raise ValueError('Recording too short for synchronization marker')
    x = signal[low:high + len(pattern)]
    size = 1 << (len(x) + len(pattern) - 2).bit_length()
    corr = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(pattern[::-1], size), size)
    corr = corr[len(pattern) - 1:len(x)]
    energy = np.concatenate(([0.0], np.cumsum(x * x)))
    energy = np.maximum(energy[len(pattern):] - energy[:-len(pattern)], 0)
    score = np.abs(corr) / np.sqrt(np.maximum(energy * np.dot(pattern, pattern), 1e-30))
    # Avoid numerical cancellation in silent windows producing a huge score.
    score[energy < max(float(np.max(energy)) * 1e-8, 1e-24)] = 0
    score = np.minimum(score, 1.0)
    index = int(np.argmax(score))
    quality = float(score[index])
    if quality < .35:
        raise ValueError(f'No reliable sync marker (correlation {quality:.3f}); check routing/level')
    offset = 0.0
    if 0 < index < len(score) - 1:
        a, b, c = score[index - 1:index + 2]
        denominator = a - 2 * b + c
        if denominator < 0:
            offset = float(np.clip(.5 * (a - c) / denominator, -.5, .5))
    return low + index + offset, quality


def synchronize(stimulus, recording, plan, max_delay):
    rate = plan['rate']
    first, last = plan['markers']
    pattern = stimulus[first['start']:first['start'] + first['frames']]
    start, quality_start = correlation_marker(recording, pattern, first['start'] - max_delay * rate,
                                               first['start'] + max_delay * rate)
    lag = start - first['start']
    expected_end = last['start'] + lag
    search = max(.1 * rate, .005 * (last['start'] - first['start']))
    end_pattern = stimulus[last['start']:last['start'] + last['frames']]
    end, quality_end = correlation_marker(recording, end_pattern, expected_end - search, expected_end + search)
    scale = (end - start) / (last['start'] - first['start'])
    ppm = (scale - 1) * 1e6
    if abs(ppm) > 2000:
        raise ValueError(f'Excessive clock drift / wrong markers ({ppm:.1f} ppm); check sample rates')
    return dict(offset_frames=start - scale * first['start'], clock_scale=scale,
                delay_at_first_marker_frames=lag, roundtrip_ms=1000 * lag / rate,
                drift_ppm=ppm, first_marker_correlation=quality_start, last_marker_correlation=quality_end)


def fundamental_fit(y, rate, frequency):
    phase = 2 * np.pi * frequency * np.arange(len(y)) / rate
    matrix = np.column_stack((np.ones(len(y)), np.sin(phase), np.cos(phase)))
    coefficients = np.linalg.lstsq(matrix, y, rcond=None)[0]
    residual = y - matrix @ coefficients
    return coefficients, residual


def estimate_frequency(y, rate, expected):
    # Bounded local search: marker drift already supplies a close initial value.
    half = .7 * rate / len(y)
    low, high = expected - half, expected + half
    fraction = (math.sqrt(5) - 1) / 2
    a, b = high - fraction * (high - low), low + fraction * (high - low)

    def error(f):
        _, residual = fundamental_fit(y, rate, f)
        return float(np.dot(residual, residual))

    ea, eb = error(a), error(b)
    for _ in range(28):
        if ea < eb:
            high, b, eb = b, a, ea
            a = high - fraction * (high - low)
            ea = error(a)
        else:
            low, a, ea = a, b, eb
            b = low + fraction * (high - low)
            eb = error(b)
    return (low + high) / 2


def tone_metrics(y, rate, expected, input_rms, adc_volts_per_fs=None):
    peak = float(np.max(np.abs(y)))
    rms = float(np.sqrt(np.mean(y * y)))
    clipped = int(np.count_nonzero(np.abs(y) >= .999))
    if rms < 1e-10:
        return dict(valid=False, reason='No measurable signal', recorded_peak_dbfs=db(peak), rms_dbfs=db(rms), clipped_samples=clipped)
    freq = estimate_frequency(y, rate, expected)
    # Always fit the fundamental, even if frequency estimation puts 20 kHz
    # a fraction above the harmonic-band cutoff.
    count = max(1, min(10, int(min(20000, rate / 2 - rate / len(y)) / freq)))
    phase = 2 * np.pi * freq * np.arange(len(y)) / rate
    columns = [np.ones(len(y))]
    for k in range(1, count + 1):
        columns.extend((np.sin(k * phase), np.cos(k * phase)))
    coefficients = np.linalg.lstsq(np.column_stack(columns), y, rcond=None)[0]
    harmonics = np.hypot(coefficients[1::2], coefficients[2::2]) / math.sqrt(2)
    fundamental = float(harmonics[0])
    _, residual = fundamental_fit(y, rate, freq)
    # Residual includes harmonics and noise across the full sampled bandwidth.
    thdn = float(np.sqrt(np.mean(residual * residual))) / max(fundamental, 1e-15)
    thd = float(np.linalg.norm(harmonics[1:])) / max(fundamental, 1e-15)
    metrics = dict(valid=not clipped and fundamental > 1e-8, measured_frequency_hz=freq,
                   recorded_peak_dbfs=db(peak), rms_dbfs=db(rms), dc_fs=float(np.mean(y)),
                   fundamental_rms_dbfs=db(fundamental), gain_db=db(fundamental / input_rms),
                   thd_percent=100 * thd if count > 1 else None, thdn_percent=100 * thdn, thdn_db=db(thdn),
                   harmonic_count=count, harmonic_dbc={str(k + 1):db(v / fundamental)
                       for k, v in enumerate(harmonics) if k}, clipped_samples=clipped)
    if adc_volts_per_fs is not None:
        volts = fundamental * adc_volts_per_fs
        metrics.update(fundamental_vrms=volts, fundamental_dbu=db(volts / .775))
    return metrics


def analyze(directory, recording_path, channel=1, baseline=None, max_delay=2.0,
            adc_volts_per_fs=None, report_dir=None):
    directory = Path(directory)
    plan = json.loads((directory / 'plan.json').read_text(encoding='utf-8'))
    if plan['schema_version'] != SCHEMA or sha(directory / 'stimulus.wav') != plan['stimulus_sha256']:
        raise ValueError('Unsupported plan or stimulus hash mismatch')
    if channel not in (1, 2) or not 0 < max_delay <= 10:
        raise ValueError('Channel must be 1/2; max-delay must be >0 and <=10 seconds')
    if adc_volts_per_fs is not None and (not math.isfinite(adc_volts_per_fs) or adc_volts_per_fs <= 0):
        raise ValueError('ADC volts-per-FS must be finite and positive')
    stimulus, sr = sf.read(str(directory / 'stimulus.wav'), dtype='float64')
    audio, rate = sf.read(str(recording_path), dtype='float64', always_2d=True)
    if rate != sr or rate != plan['rate']:
        raise ValueError('Recording and stimulus sample rates must match; no implicit resampling')
    if channel > audio.shape[1] or not np.isfinite(audio).all():
        raise ValueError('Missing input channel or non-finite recording')
    recorded = audio[:, channel - 1]
    sync = synchronize(stimulus, recorded, plan, max_delay)
    rows = []
    for segment in plan['segments']:
        begin = round(sync['offset_frames'] + sync['clock_scale'] * segment['measurement_start'])
        frames = round(sync['clock_scale'] * segment['measurement_frames'])
        if begin < 0 or begin + frames > len(recorded):
            raise ValueError(f'Recording truncated at segment {segment["id"]}')
        nominal_rms = 10 ** (segment['peak_dbfs'] / 20) / math.sqrt(2)
        metrics = tone_metrics(recorded[begin:begin + frames], rate,
                               segment['frequency_hz'] / sync['clock_scale'], nominal_rms, adc_volts_per_fs)
        rows.append(dict(segment, capture_start=begin, capture_frames=frames, **metrics))
    baseline_hash = None
    if baseline:
        base = json.loads(Path(baseline).read_text(encoding='utf-8'))
        if not base['valid'] or base['rate'] != rate or base['channel'] != channel:
            raise ValueError('Baseline invalid or captured at a different rate/input channel')
        if Path(baseline).resolve() == ((Path(report_dir) if report_dir else directory) / 'results.json').resolve():
            raise ValueError('Use --report-dir to keep the baseline report instead of overwriting it')
        if base['stimulus_sha256'] != plan['stimulus_sha256'] or len(base['segments']) != len(rows):
            raise ValueError('Baseline uses a different stimulus/protocol')
        for row, ref in zip(rows, base['segments']):
            if row['id'] != ref['id']:
                raise ValueError('Baseline segment order differs')
            row['relative_gain_db'] = row['gain_db'] - ref['gain_db'] if row['valid'] and ref['valid'] else None
        baseline_hash = sha(baseline)
    # Noise measured before the first marker, with guard against pre-ringing.
    begin = max(0, round(sync['offset_frames'] + sync['clock_scale'] * .1 * rate))
    end = round(sync['offset_frames'] + sync['clock_scale'] * .35 * rate)
    noise = recorded[begin:end]
    noise_dbfs = db(np.sqrt(np.mean((noise - np.mean(noise)) ** 2))) if len(noise) > rate * .1 else None
    capture_path = Path(recording_path).with_suffix('.json')
    capture = json.loads(capture_path.read_text(encoding='utf-8')) if capture_path.exists() else None
    # Associate optional live-stream status only with its exact recorded WAV.
    if capture and capture.get('recording_sha256') != sha(recording_path):
        capture = None
    report = dict(schema_version=SCHEMA, created_utc=datetime.now(timezone.utc).isoformat(),
                  rate=rate, channel=channel, synchronization=sync,
                  stimulus_sha256=plan['stimulus_sha256'], recording_sha256=sha(recording_path),
                  plan_sha256=sha(directory / 'plan.json'), script_sha256=sha(__file__),
                  baseline_sha256=baseline_hash, capture=capture,
                  adc_volts_per_fs=adc_volts_per_fs, idle_noise_rms_dbfs=noise_dbfs,
                  valid=all(r['valid'] for r in rows) and not (capture and capture.get('stream_status')),
                  notes=['Gain is ADC digital level / DAC stimulus digital level; not calibrated DUT gain without a baseline.',
                         'THD uses H2..H10 below 20 kHz and Nyquist; THD+N is unweighted DC-removed full-band residual.',
                         'Distortion includes DAC, ADC and test path; baseline THD is not subtracted.',
                         'Roundtrip delay includes converters, host buffers and test path, not just plugin latency.',
                         'Analog measured attenuation is not the internal wet FET gain-reduction meter.'], segments=rows)
    destination = Path(report_dir) if report_dir else directory
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / 'results.json', report)
    keys = ('id', 'group', 'frequency_hz', 'peak_dbfs', 'valid', 'measured_frequency_hz',
            'gain_db', 'relative_gain_db', 'rms_dbfs', 'recorded_peak_dbfs', 'thd_percent', 'thdn_percent', 'clipped_samples')
    with (destination / 'results.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            record = {key:row.get(key) for key in keys}
            writer.writerow(record)
    lines = ['# Scarlett-Messauswertung', '',
             f'- Rate: {rate} Hz; Eingangskanal: {channel}',
             f'- Synchronisation: {sync["roundtrip_ms"]:.3f} ms; Drift: {sync["drift_ppm"]:.2f} ppm',
             f'- Messdaten gültig: {report["valid"]}; Leerlaufrauschen RMS: {noise_dbfs} dBFS',
             '- Gain relativ zu digitalen Abspielwerten; für die Teststrecke zuerst direkte Kabelreferenz messen.',
             '- THD: H2…H10 bis 20 kHz/Nyquist; THD+N: ungewichtetes Vollband-Residual.',
             '- Keine interne FET-GR-, Hardwaregleichheits- oder Hörabnahme.', '',
             '| Teil | Hz | Anregung Peak dBFS | Gain dB | relativ dB | THD % | THD+N % | gültig |',
             '|---|---:|---:|---:|---:|---:|---:|---|']
    for segment, row in zip(plan['segments'], rows):
        def fmt(key):
            value = row.get(key)
            return f'{value:.5g}' if value is not None else '—'
        lines.append(f'| {row["group"]} | {row["frequency_hz"]:g} | {segment["peak_dbfs"]:g} | '
                     f'{fmt("gain_db")} | {fmt("relative_gain_db")} | {fmt("thd_percent")} | '
                     f'{fmt("thdn_percent")} | {row["valid"]} |')
    (destination / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return report


def sounddevice():
    try:
        import sounddevice as sd
    except (ImportError, OSError) as error:
        raise ValueError('Live audio needs sounddevice and PortAudio; see docs/SCARLETT_TEST.md') from error
    return sd


def record(directory, input_device, output_device, output_channel=1, input_channel=1, label=''):
    sd = sounddevice()
    directory = Path(directory)
    recording = directory / 'recording.wav'
    if recording.exists():
        raise ValueError('recording.wav already exists; use a new measurement directory')
    stimulus, rate = sf.read(str(directory / 'stimulus.wav'), dtype='float32')
    plan = json.loads((directory / 'plan.json').read_text(encoding='utf-8'))
    if sha(directory / 'stimulus.wav') != plan['stimulus_sha256'] or rate != plan['rate']:
        raise ValueError('Stimulus/plan changed before playback')
    if output_channel not in (1, 2) or input_channel not in (1, 2):
        raise ValueError('Scarlett channels must be 1 or 2')
    try:
        input_info = dict(sd.query_devices(input_device))
        output_info = dict(sd.query_devices(output_device))
        if input_info['hostapi'] != output_info['hostapi']:
            raise ValueError('Input and output must use the same host API')
        sd.check_input_settings(device=input_device, channels=2, dtype='float32', samplerate=rate)
        sd.check_output_settings(device=output_device, channels=2, dtype='float32', samplerate=rate)
    except sd.PortAudioError as error:
        raise RuntimeError(str(error)) from error
    playback = np.zeros((len(stimulus), 2), dtype=np.float32)
    playback[:, output_channel - 1] = stimulus
    print(f'Playing {len(stimulus)/rate:.1f} s on output {output_channel}; recording both inputs at {rate} Hz.')
    try:
        audio = sd.playrec(playback, samplerate=rate, channels=2, dtype='float32',
                           device=(input_device, output_device), blocking=True)
        status = str(sd.get_status())
    except sd.PortAudioError as error:
        raise RuntimeError(str(error)) from error
    finally:
        sd.stop()
    sf.write(str(recording), audio, rate, subtype='FLOAT')
    metadata = dict(recording_sha256=sha(recording), input_device=input_info,
                    output_device=output_info, hostapis=sd.query_hostapis(),
                    output_channel=output_channel, analyzed_input_channel=input_channel,
                    label=label, stream_status=status, note='No hardware gain/monitor/phantom controls were changed')
    write_json(recording.with_suffix('.json'), metadata)
    return recording


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('devices', help='List audio devices and host APIs')
    for name in ('generate', 'run'):
        sub = commands.add_parser(name)
        sub.add_argument('--output', type=Path, required=True, help='New measurement directory')
        sub.add_argument('--kind', choices=('tone', 'sweep', 'levels', 'all'), default='tone')
        sub.add_argument('--rate', type=int, default=48000)
        sub.add_argument('--level', type=float, default=-18, help='Highest digital peak level, dBFS')
        sub.add_argument('--frequency', type=float, default=1000)
        sub.add_argument('--settle', type=float, default=.75)
        sub.add_argument('--measure', type=float, default=1)
        if name == 'run':
            sub.add_argument('--input-device', type=int, required=True)
            sub.add_argument('--output-device', type=int, required=True)
            sub.add_argument('--output-channel', type=int, choices=(1, 2), default=1)
            sub.add_argument('--input-channel', type=int, choices=(1, 2), default=1)
            sub.add_argument('--label', default='')
            sub.add_argument('--baseline', type=Path)
    sub = commands.add_parser('analyze')
    sub.add_argument('--session', type=Path, required=True)
    sub.add_argument('--recording', type=Path, required=True)
    sub.add_argument('--input-channel', type=int, choices=(1, 2), default=1)
    sub.add_argument('--baseline', type=Path)
    sub.add_argument('--max-delay', type=float, default=2)
    sub.add_argument('--adc-volts-per-fs', type=float)
    sub.add_argument('--report-dir', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'devices':
            sd = sounddevice()
            try:
                print(sd.query_devices())
                print(json.dumps(sd.query_hostapis(), indent=2))
            except sd.PortAudioError as error:
                raise RuntimeError(str(error)) from error
        elif args.command in ('generate', 'run'):
            plan = generate(args.output, args.rate, args.level, args.kind, args.frequency, args.settle, args.measure)
            print(f'Generated {len(plan["segments"])} segments: {args.output}/stimulus.wav and plan.json')
            if args.command == 'run':
                wav = record(args.output, args.input_device, args.output_device, args.output_channel,
                             args.input_channel, args.label)
                result = analyze(args.output, wav, args.input_channel, args.baseline)
                print(f'Analysis valid={result["valid"]}: {args.output}/REPORT.md')
                return 0 if result['valid'] else 1
        else:
            result = analyze(args.session, args.recording, args.input_channel, args.baseline,
                             args.max_delay, args.adc_volts_per_fs, args.report_dir)
            print(f'Analysis valid={result["valid"]}: {args.report_dir or args.session}/REPORT.md')
            return 0 if result['valid'] else 1
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f'Measurement failed: {error}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
