#!/usr/bin/env python3
"""Offline measurement acceptance: known delay/gain/harmonics, drift and failures."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import scarlett_test as measurement


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.session = self.root / 'session'
        self.plan = measurement.generate(self.session, settle=.25, measure=.5)
        self.x, self.rate = sf.read(self.session / 'stimulus.wav')

    def capture(self, signal, name='recorded.wav'):
        path = self.root / name
        sf.write(path, signal, self.rate, subtype='FLOAT')
        return path

    def test_gain_delay_polarity_and_baseline(self):
        y = np.concatenate((np.zeros(731), -.5 * self.x))
        wav = self.capture(y)
        report = measurement.analyze(self.session, wav, adc_volts_per_fs=2.0)
        self.assertTrue(report['valid'])
        self.assertAlmostEqual(report['synchronization']['delay_at_first_marker_frames'], 731, delta=.01)
        row = report['segments'][0]
        self.assertAlmostEqual(row['gain_db'], -6.0206, delta=.002)
        self.assertLess(row['thdn_percent'], .005)
        self.assertEqual(row['peak_dbfs'], -18)
        self.assertAlmostEqual(row['recorded_peak_dbfs'], -24.0206, delta=.002)
        self.assertAlmostEqual(row['fundamental_vrms'], 10 ** (-18 / 20) / np.sqrt(2), delta=1e-6)
        base = self.session / 'results.json'
        measured = measurement.analyze(self.session, self.capture(y*.5, 'dut.wav'), baseline=base,
                                       report_dir=self.root / 'dut')
        self.assertAlmostEqual(measured['segments'][0]['relative_gain_db'], -6.0206, delta=.002)
        with (self.root / 'dut/results.csv').open() as stream:
            record = next(csv.DictReader(stream))
        self.assertEqual(float(record['peak_dbfs']), -18)
        self.assertLess(float(record['recorded_peak_dbfs']), -29)

    def test_known_harmonics_and_dc(self):
        y = .5 * self.x
        segment = self.plan['segments'][0]
        start = segment['measurement_start']
        frames = segment['measurement_frames']
        t = np.arange(frames) / self.rate
        amplitude = .5 * 10 ** (-18 / 20)
        y[start:start+frames] = .002 + amplitude * (np.sin(2*np.pi*1000*t) + .01*np.sin(2*np.pi*2000*t))
        report = measurement.analyze(self.session, self.capture(np.concatenate((np.zeros(300), y))))
        row = report['segments'][0]
        self.assertAlmostEqual(row['thd_percent'], 1, delta=.02)
        self.assertAlmostEqual(row['harmonic_dbc']['2'], -40, delta=.1)
        self.assertAlmostEqual(row['dc_fs'], .002, delta=1e-6)

    def test_clock_drift(self):
        scale = 1.00012
        n = np.arange(round(len(self.x)*scale)+500)
        y = np.interp((n-321)/scale, np.arange(len(self.x)), self.x, left=0, right=0)
        report = measurement.analyze(self.session, self.capture(y))
        self.assertAlmostEqual(report['synchronization']['drift_ppm'], 120, delta=5)
        self.assertAlmostEqual(report['segments'][0]['gain_db'], 0, delta=.03)
        self.assertAlmostEqual(report['segments'][0]['measured_frequency_hz'], 1000/scale, delta=.01)

    def test_missing_signal_truncation_rate_and_clipping(self):
        with self.assertRaisesRegex(ValueError, 'sync marker'):
            measurement.analyze(self.session, self.capture(np.zeros_like(self.x)))
        with self.assertRaises(ValueError):
            measurement.analyze(self.session, self.capture(self.x[:1000]))
        wrong = self.root / 'wrong.wav'
        sf.write(wrong, self.x, 44100, subtype='FLOAT')
        with self.assertRaisesRegex(ValueError, 'sample rates'):
            measurement.analyze(self.session, wrong)
        clipped = np.clip(self.x*16, -1, 1)
        report = measurement.analyze(self.session, self.capture(clipped))
        self.assertFalse(report['valid'])
        self.assertGreater(report['segments'][0]['clipped_samples'], 0)

    def test_protocol_generation_and_input_validation(self):
        full = measurement.generate(self.root / 'all', kind='all', settle=.25, measure=.5)
        self.assertEqual(len(full['segments']), 19)
        x, _ = sf.read(self.root / 'all/stimulus.wav')
        self.assertLessEqual(np.max(np.abs(x)), 10 ** (-18/20) + 1e-7)
        with self.assertRaises(ValueError):
            measurement.generate(self.root / 'bad', level=0)
        with self.assertRaises(FileExistsError):
            measurement.generate(self.session)
        with self.assertRaises(ValueError):
            measurement.generate(self.root / 'bad', frequency=float('nan'))

    def test_full_sweep_known_filter_and_changed_baseline(self):
        folder = self.root / 'sweep'
        plan = measurement.generate(folder, kind='sweep', settle=.25, measure=.5)
        x, _ = sf.read(folder / 'stimulus.wav')
        # Two-tap FIR has analytic magnitude cos(pi*f/fs), group delay 0.5 samples.
        filtered = np.convolve(x, [.5, .5])
        wav = self.capture(np.concatenate((np.zeros(257), filtered)), 'sweep.wav')
        report = measurement.analyze(folder, wav)
        self.assertTrue(report['valid'])
        self.assertEqual(len(report['segments']), 13)
        for row in report['segments']:
            expected = 20*np.log10(abs(np.cos(np.pi*row['frequency_hz']/self.rate)))
            self.assertAlmostEqual(row['gain_db'], expected, delta=.04)
        with self.assertRaisesRegex(ValueError, 'different stimulus'):
            measurement.analyze(self.session, self.capture(self.x), baseline=folder/'results.json')

    def test_two_second_latency_and_channel_selection(self):
        y = np.concatenate((np.zeros(96000), self.x))
        wav = self.capture(np.column_stack((np.zeros(len(y)), y)))
        report = measurement.analyze(self.session, wav, channel=2, max_delay=2.1)
        self.assertAlmostEqual(report['synchronization']['roundtrip_ms'], 2000, delta=.05)
        self.assertTrue(report['valid'])

    def test_live_routing_and_stream_status_with_fake_backend(self):
        backend = Mock()
        backend.PortAudioError = RuntimeError
        backend.query_devices.return_value = {'name':'Fake two-channel interface', 'hostapi':0}
        backend.query_hostapis.return_value = [{'name':'Fake'}]
        backend.get_status.return_value = 'input overflow'
        backend.playrec.side_effect = lambda playback, **kw: playback.copy()
        with patch.object(measurement, 'sounddevice', return_value=backend):
            wav = measurement.record(self.session, 4, 5, output_channel=2, input_channel=2, label='mock')
        output = backend.playrec.call_args.args[0]
        self.assertEqual(output.shape[1], 2)
        self.assertTrue(np.all(output[:, 0] == 0))
        self.assertGreater(np.max(np.abs(output[:, 1])), .1)
        self.assertEqual(backend.playrec.call_args.kwargs['device'], (4, 5))
        backend.stop.assert_called_once()
        report = measurement.analyze(self.session, wav, channel=2)
        self.assertFalse(report['valid'])
        self.assertEqual(report['capture']['stream_status'], 'input overflow')

    def test_aborted_backend_stops_stream(self):
        backend = Mock()
        backend.PortAudioError = RuntimeError
        backend.query_devices.return_value = {'name':'Fake', 'hostapi':0}
        backend.playrec.side_effect = RuntimeError('Disconnected')
        with patch.object(measurement, 'sounddevice', return_value=backend):
            with self.assertRaisesRegex(RuntimeError, 'Disconnected'):
                measurement.record(self.session, 1, 1)
        backend.stop.assert_called_once()
        self.assertFalse((self.session / 'recording.wav').exists())

    def test_high_frequency_has_no_claimed_zero_thd(self):
        t = np.arange(24000) / self.rate
        y = .1*np.sin(2*np.pi*20000.01*t)
        metrics = measurement.tone_metrics(y, self.rate, 20000, .1/np.sqrt(2))
        self.assertTrue(metrics['valid'])
        self.assertEqual(metrics['harmonic_count'], 1)
        self.assertIsNone(metrics['thd_percent'])
        self.assertLess(metrics['thdn_percent'], .01)

    def test_low_loop_gain_flags_level_check(self):
        report = measurement.analyze(self.session, self.capture(self.x * .0025))
        self.assertTrue(report['valid'])
        self.assertFalse(report['level_check']['adequate'])
        self.assertLess(report['level_check']['tone_loop_gain_db'], -50)
        text = (self.session / 'REPORT.md').read_text(encoding='utf-8')
        self.assertIn('ÜBERSCHRIETTEN', text)

    def test_device_rate_mismatch_recorded(self):
        backend = Mock()
        backend.PortAudioError = RuntimeError
        backend.query_devices.side_effect = lambda index: dict(
            name=f'Device {index}', hostapi=0, default_samplerate=44100)
        backend.query_hostapis.return_value = [{'name':'Fake'}]
        backend.get_status.return_value = ''
        backend.playrec.side_effect = lambda playback, **kw: playback.copy()
        with patch.object(measurement, 'sounddevice', return_value=backend):
            wav = measurement.record(self.session, 1, 2, label='rate-mismatch')
        metadata = json.loads(wav.with_suffix('.json').read_text(encoding='utf-8'))
        self.assertTrue(metadata['rate_mismatch'])


if __name__ == '__main__':
    unittest.main()
