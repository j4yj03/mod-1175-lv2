#!/usr/bin/env python3
"""Offline driver acceptance for the automated Scarlett/Dwarf matrix.

Uses a simulated backend: identity loop with adjustable gain, so gain match,
anchor level choice, resume behaviour and aggregation are checked without
hardware. See docs/MESSTECHNIK.md for the live protocol.
"""
import contextlib
import io
import json
import shutil
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import scarlett_matrix as driver  # noqa: E402
import scarlett_test as measurement  # noqa: E402


def fake_devices():
    return [
        dict(name='Microsoft Sound Mapper - Input', hostapi=0, max_input_channels=2,
             max_output_channels=0, default_samplerate=48000),
        dict(name='Analogue 1 + 2 (Focusrite USB Audio)', hostapi=0,
             max_input_channels=2, max_output_channels=0, default_samplerate=48000),
        dict(name='Mikrofon (Realtek(R) Audio)', hostapi=0, max_input_channels=2,
             max_output_channels=0, default_samplerate=48000),
        dict(name='Microsoft Sound Mapper - Output', hostapi=0, max_input_channels=0,
             max_output_channels=2, default_samplerate=48000),
        dict(name='Lautsprecher (Focusrite USB Audio)', hostapi=0,
             max_input_channels=0, max_output_channels=2, default_samplerate=48000),
        dict(name='Lautsprecher (Realtek(R) Audio)', hostapi=0, max_input_channels=0,
             max_output_channels=2, default_samplerate=48000),
    ]


class FakeBackend:
    PortAudioError = RuntimeError

    def __init__(self, scale=1.0):
        self.scale = scale
        self.calls = []

    def query_devices(self, index=None):
        devices = fake_devices()
        return devices if index is None else devices[index]

    def query_hostapis(self):
        return [dict(name='MME', devices=list(range(len(fake_devices()))),
                     default_input_device=1, default_output_device=4)]

    def check_input_settings(self, **kwargs):
        pass

    def check_output_settings(self, **kwargs):
        pass

    def playrec(self, playback, **kwargs):
        self.calls.append(kwargs['device'])
        return np.asarray(playback, dtype=np.float32) * self.scale

    def rec(self, frames, samplerate, channels, dtype, device, blocking):
        self.calls.append(('rec', device))
        return np.zeros((frames, channels), dtype=np.float32)

    def get_status(self):
        return ''

    def stop(self):
        pass


class DriverTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.backend = FakeBackend()

    def run_driver(self, argv, scale=None):
        if scale is not None:
            self.backend.scale = scale
        with patch.object(measurement, 'sounddevice', return_value=self.backend):
            return driver.main(argv)

    def common(self, extra=()):
        return ['--yes', '--repeats', '1', '--baseline-repeats', '2',
                '--transformers', '60s', '--settle', '.25', '--measure', '.5',
                '--rates', '48000'] + list(extra)

    def run_full(self, root):
        self.backend.scale = 1.13  # about +1.07 dB loop gain: all anchors reachable
        self.run_driver(['full', '--root', str(root)] + self.common())
        return root


class DeviceAndLevelTests(DriverTestCase):
    def test_find_devices_picks_focusrite_mme_pair(self):
        self.assertEqual(driver.find_devices(self.backend, 'MME'), (1, 4))

    def test_find_devices_fails_without_focusrite(self):
        backend = FakeBackend()
        backend.query_devices = lambda index=None: [
            dict(name='Lautsprecher (Realtek(R) Audio)', hostapi=0,
                 max_input_channels=2, max_output_channels=2)]
        with self.assertRaisesRegex(ValueError, 'No Focusrite input'):
            driver.find_devices(backend, 'MME')

    def test_find_devices_rejects_unknown_hostapi(self):
        with self.assertRaisesRegex(ValueError, 'Host API "ASIO"'):
            driver.find_devices(self.backend, 'ASIO')

    def test_parse_transformers_normalizes_and_rejects(self):
        self.assertEqual(driver.parse_transformers('None, 60s ,sym'),
                         ('None', '60s', 'Sym'))
        with self.assertRaisesRegex(ValueError, 'Unknown transformer'):
            driver.parse_transformers('Jensen999')

    def test_choose_stimulus_level_hits_all_anchors_with_positive_loop_gain(self):
        # Anchors sit 6 dB apart like the series steps; a stimulus of -3 dBFS
        # plus loop gain >= +1 dB places all of them at the plugin input.
        level, reachable, missing = driver.choose_stimulus_level(1.0)
        self.assertEqual(level, -3)
        self.assertEqual(reachable, [-14.0, -8.0, -2.0])
        self.assertEqual(missing, [])

    def test_choose_stimulus_level_clamps_and_reports_missing(self):
        level, reachable, missing = driver.choose_stimulus_level(-11.0)
        self.assertEqual(level, -3)
        self.assertEqual(reachable, [-14.0])
        self.assertEqual(missing, [-8.0, -2.0])
        # Unity loop gain cannot reach the -2 dBFS anchor: stimulus is capped
        # at -3 dBFS, so the top step lands at -3, not -2.
        level, reachable, missing = driver.choose_stimulus_level(0.0)
        self.assertEqual(level, -3)
        self.assertEqual(reachable, [-14.0, -8.0])
        self.assertEqual(missing, [-2.0])
        self.assertAlmostEqual(driver.required_loop_gain(), 1.0)
        with self.assertRaisesRegex(ValueError, 'Loop gain unknown'):
            driver.choose_stimulus_level(None)


class MatrixFlowTests(DriverTestCase):
    def test_full_flow_runs_all_phases_in_sequence(self):
        self.backend.scale = 1.13  # about +1.07 dB loop gain: all anchors reachable
        root = self.run_full(Path(self.temp.name) / 'matrix')
        names = sorted(path.name for path in root.iterdir() if path.is_dir())
        self.assertEqual(names, [
            '60s-ch1-r1-48000', '60s-ch2-r1-48000',
            'baseline-ch1-r1-48000', 'baseline-ch1-r2-48000',
            'baseline-ch2-r1-48000', 'baseline-ch2-r2-48000',
            'gainmatch-ch1-48000', 'gainmatch-ch2-48000'])
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        roles = [run['role'] for run in index['runs']]
        self.assertEqual(roles.count('gainmatch'), 2)
        self.assertEqual(roles.count('baseline'), 4)
        self.assertEqual(roles.count('dut'), 2)
        self.assertAlmostEqual(index['gainmatch']['48000']['delta_db'], 0.0, places=6)
        self.assertGreaterEqual(index['gainmatch']['48000']['channel1_db'], 1.0)
        for run in index['runs']:
            self.assertTrue(run['valid'], run['directory'])
            self.assertFalse(run['rate_mismatch'])
            if run['role'] != 'gainmatch':
                expected = -2.0 - index['gainmatch']['48000']['channel1_db']
                self.assertLessEqual(run['stimulus_level_dbfs'], -3.0)
                self.assertAlmostEqual(run['stimulus_level_dbfs'], expected, places=6)
        self.assertTrue((root / 'summary.json').exists())
        self.assertTrue((root / 'SUMMARY.md').exists())

    def test_full_flow_aborts_when_anchors_unreachable(self):
        self.backend.scale = 1.0  # unity loop gain: -2 dBFS anchor out of reach
        stderr = io.StringIO()
        with patch.object(measurement, 'sounddevice', return_value=self.backend), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit):
                driver.main(['full', '--root', str(Path(self.temp.name) / 'matrix')]
                            + self.common())
        self.assertIn('>= +1.0 dB', stderr.getvalue())
        index = json.loads((Path(self.temp.name) / 'matrix' / 'index.json')
                           .read_text(encoding='utf-8'))
        self.assertEqual([run['role'] for run in index['runs']].count('baseline'), 0)

    def test_relax_anchors_continues_with_achieved_levels(self):
        self.backend.scale = 1.0  # unity loop gain, anchors off by 1 dB
        root = Path(self.temp.name) / 'matrix'
        self.run_driver(['full', '--root', str(root), '--relax-anchors'] + self.common())
        summary = json.loads((root / 'summary.json').read_text(encoding='utf-8'))
        anchors = summary['anchors_found']['48000/60s/ch1']
        self.assertEqual(anchors, [-14.0, -8.0, -2.0])
        self.assertTrue(any('erreicht nur' in issue for issue in summary['issues']))

    def test_matrix_relative_gain_and_anchors_against_baseline(self):
        root = Path(self.temp.name) / 'matrix'
        self.backend.scale = 1.13
        self.run_driver(['gainmatch', '--root', str(root)] + self.common())
        self.run_driver(['baseline', '--root', str(root)] + self.common())
        self.run_driver(['matrix', '--root', str(root)] + self.common(), scale=0.565)
        summary = json.loads((root / 'summary.json').read_text(encoding='utf-8'))
        dut = summary['dut']['48000']['60s']['1']['8']
        self.assertAlmostEqual(dut['relative_gain_db']['median'], -6.0206, places=3)
        self.assertEqual(dut['relative_gain_db']['count'], 1)
        self.assertAlmostEqual(dut['relative_gain_db']['spread'], 0.0, places=6)
        anchors = summary['anchors_found']['48000/60s/ch1']
        self.assertEqual(anchors, [-14.0, -8.0, -2.0])
        text = (root / 'SUMMARY.md').read_text(encoding='utf-8')
        self.assertIn('| 60s | 1 | 48000 |', text)
        self.assertIn('Stabilitaetsreferenz', text)
        self.assertIn('Pegelanker am Plugin-Eingang', text)
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        for run in index['runs']:
            self.assertTrue(Path(run['directory'], 'results.json').exists())

    def test_summary_cli_reaggregates_existing_root(self):
        root = self.run_full(Path(self.temp.name) / 'matrix')
        (root / 'SUMMARY.md').unlink()
        exit_code = self.run_driver(['summary', '--root', str(root)])
        self.assertEqual(exit_code, 0)
        self.assertTrue((root / 'SUMMARY.md').exists())

    def test_summary_requires_root(self):
        stderr = io.StringIO()
        with patch.object(measurement, 'sounddevice', return_value=self.backend), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit):
                driver.main(['summary'])
        self.assertIn('summary requires', stderr.getvalue())

    def test_matrix_resume_skips_completed_runs(self):
        root = Path(self.temp.name) / 'matrix'
        self.backend.scale = 1.13
        self.run_driver(['gainmatch', '--root', str(root)] + self.common())
        self.run_driver(['baseline', '--root', str(root)] + self.common())
        self.run_driver(['matrix', '--root', str(root)] + self.common(), scale=0.565)
        before = len(self.backend.calls)
        exit_code = self.run_driver(['matrix', '--root', str(root)] + self.common())
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(self.backend.calls), before)

    def test_baseline_resume_reuses_existing_baselines(self):
        root = Path(self.temp.name) / 'matrix'
        self.backend.scale = 1.13
        self.run_driver(['gainmatch', '--root', str(root)] + self.common())
        self.run_driver(['baseline', '--root', str(root)] + self.common())
        before = len(self.backend.calls)
        exit_code = self.run_driver(['baseline', '--root', str(root)] + self.common())
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(self.backend.calls), before)

    def test_incomplete_directory_is_cleaned_completed_refused(self):
        root = Path(self.temp.name) / 'matrix'
        self.backend.scale = 1.13
        self.run_driver(['gainmatch', '--root', str(root)] + self.common())
        self.run_driver(['baseline', '--root', str(root)] + self.common())
        self.run_driver(['matrix', '--root', str(root)] + self.common())
        complete = root / '60s-ch1-r1-48000'
        leftover = root / '80s-ch1-r1-48000'
        leftover.mkdir()
        (leftover / 'plan.json').write_text('{}', encoding='utf-8')
        shutil.copytree(complete, root / '80s-ch2-r1-48000')
        stderr = io.StringIO()
        with patch.object(measurement, 'sounddevice', return_value=self.backend), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit):
                driver.main(['matrix', '--root', str(root)] + self.common()
                            + ['--transformers', '80s'])
        self.assertIn('already holds a completed run', stderr.getvalue())
        self.assertTrue((leftover / 'recording.wav').exists())


class GainMatchTests(DriverTestCase):
    def test_gainmatch_reports_channel_delta(self):
        root = Path(self.temp.name) / 'gain'
        calls = {'count': 0}

        def playrec(playback, **kwargs):
            calls['count'] += 1
            buffer = np.asarray(playback)
            scale = 0.9 if np.any(buffer[:, 1]) else 1.0
            return buffer * scale

        self.backend.playrec = playrec
        with patch.object(measurement, 'sounddevice', return_value=self.backend):
            exit_code = driver.main(['gainmatch', '--root', str(root)] + self.common())
        self.assertEqual(exit_code, 0)
        self.assertEqual(calls['count'], 2)
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        delta = index['gainmatch']['48000']['delta_db']
        self.assertAlmostEqual(delta, 20 * np.log10(0.9), places=3)
        self.assertLess(delta, -0.5)

    def test_gainmatch_flags_inadequate_loop_gain(self):
        root = Path(self.temp.name) / 'gain'
        self.backend.scale = 0.005  # about -46 dB loop gain
        with patch.object(measurement, 'sounddevice', return_value=self.backend):
            driver.main(['gainmatch', '--root', str(root)] + self.common())
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        self.assertLess(index['gainmatch']['48000']['channel1_db'], -40)

    def test_device_id_override_bypasses_autodetection(self):
        root = Path(self.temp.name) / 'gain'
        with patch.object(measurement, 'sounddevice', return_value=self.backend):
            exit_code = driver.main(['gainmatch', '--root', str(root)] + self.common()
                                    + ['--input-device', '1', '--output-device', '4'])
        self.assertEqual(exit_code, 0)
        self.assertEqual(self.backend.calls, [(1, 4), (1, 4)])

    def test_rate_mismatch_is_recorded_in_index(self):
        root = Path(self.temp.name) / 'gain'
        original = self.backend.query_devices

        def query_devices(index=None):
            if index is None:
                return original()
            return dict(original(index), default_samplerate=44100)

        self.backend.query_devices = query_devices
        with patch.object(measurement, 'sounddevice', return_value=self.backend):
            driver.main(['gainmatch', '--root', str(root)] + self.common())
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        self.assertTrue(all(run['rate_mismatch'] for run in index['runs']))
        summary = driver.build_summary(root, index)
        # Probe runs are deliberately excluded from the series issue list; the
        # metadata itself must still record the mismatch.
        self.assertTrue(all(run['rate_mismatch'] for run in index['runs']))


class DwarfSourceTests(DriverTestCase):
    """--dwarf-source: the Dwarf file player is the stimulus, script records only."""

    def dwarf_args(self, root):
        from types import SimpleNamespace
        return SimpleNamespace(
            rates=[48000], input_device=None, output_device=None, hostapi='MME',
            dwarf_source=True, pad=10.0, level=-2, frequency=1000, settle=.25,
            measure=.5, settings_label='', relax_anchors=False, tolerance=1.0,
            baseline_repeats=1, repeats=1, transformers='60s', skip_gainmatch=True,
            yes=True, root=str(root))

    def test_anchor_guard_uses_digital_levels(self):
        base = Path(self.temp.name)
        d = driver.Driver(self.dwarf_args(base / 'guard'))
        level, reachable, missing = d.anchor_guard(48000)
        self.assertEqual(level, -2)
        self.assertEqual(missing, [])
        self.assertEqual(reachable, [-14.0, -8.0, -2.0])
        args = self.dwarf_args(base / 'guard2')
        args.level = -12
        level, reachable, missing = driver.Driver(args).anchor_guard(48000)
        self.assertEqual(level, -12)
        self.assertEqual(missing, [-14.0, -8.0, -2.0])

    def test_full_dwarf_flow_records_without_playback(self):
        root = Path(self.temp.name) / 'dwarf-flow'
        with patch.object(measurement, 'sounddevice', return_value=self.backend), \
             patch.object(measurement, 'generate') as gen, \
             patch.object(measurement, 'record') as rec, \
             patch.object(measurement, 'analyze') as ana:
            rec.return_value = Path('recording.wav')

            def fake_analyze(directory, wav, channel=1, baseline=None, max_delay=2.0, **kw):
                directory = Path(directory)
                directory.mkdir(parents=True, exist_ok=True)
                report = dict(valid=True, capture={},
                              segments=[dict(id=1, group='tone', frequency_hz=1000,
                                             peak_dbfs=-2, valid=True, gain_db=0.0,
                                             relative_gain_db=0.0, thd_percent=0.0,
                                             thdn_percent=0.0)])
                (directory / 'results.json').write_text(
                    json.dumps(report), encoding='utf-8')
                return report
            ana.side_effect = fake_analyze
            driver.main(['full', '--root', str(root), '--dwarf-source', '--level', '-2',
                         '--skip-gainmatch'] + self.common())
        self.assertEqual(gen.call_count, 6)   # 4 baseline (2ch x 2) + 2 DUT runs
        self.assertEqual(rec.call_count, 6)
        for call in rec.call_args_list:
            self.assertIs(call.kwargs['play'], False)
            self.assertEqual(call.kwargs['pad_seconds'], 10.0)
            self.assertIsNone(call.args[2], 'Dwarf mode must not open an output device')
        for call in gen.call_args_list:
            self.assertEqual(call.args[2], -2, 'fixed file level, not loop-gain derived')
            self.assertEqual(call.kwargs['max_level'], -0.1)
        for call in ana.call_args_list:
            self.assertEqual(call.kwargs['max_delay'], 10.0)
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        self.assertEqual(len([r for r in index['runs'] if r['role'] == 'baseline']), 4)
        self.assertEqual(len([r for r in index['runs'] if r['role'] == 'dut']), 2)


if __name__ == '__main__':
    unittest.main()
