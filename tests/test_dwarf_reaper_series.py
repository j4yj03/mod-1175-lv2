#!/usr/bin/env python3
"""Offline acceptance for the REAPER-import path of the Dwarf-source series."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import soundfile as sf

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import scarlett_test as measurement  # noqa: E402


def run_cli(*args):
    result = subprocess.run([sys.executable, str(TOOLS / 'dwarf_reaper_series.py'), *args],
                            capture_output=True, text=True)
    return result


class DwarfReaperSeriesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        scratch = self.root / 'scratch-all'
        measurement.generate(scratch, 48000, -2, 'all', 1000, .25, .25, max_level=-0.1)
        self.recording = self.capture(scratch, 'capture.wav')
        scratch = self.root / 'scratch-tone'
        measurement.generate(scratch, 48000, -2, 'tone', 1000, .25, .25, max_level=-0.1)
        self.tone_recording = self.capture(scratch, 'capture-tone.wav')

    def capture(self, scratch, name):
        stimulus, rate = sf.read(str(scratch / 'stimulus.wav'), dtype='float32')
        delay = int(1.0 * rate)
        signal = np.zeros(len(stimulus) + delay + rate, dtype='float32')
        signal[delay:delay + len(stimulus)] = stimulus * 0.7
        path = self.root / name
        sf.write(str(path), np.column_stack((signal, signal)), rate, subtype='PCM_24')
        return path

    def import_spec(self, spec, recording=None):
        result = run_cli('import', '--root', str(self.root / 'series'),
                         '--recording', str(recording or self.recording), '--spec', spec,
                         '--settle', '.25', '--measure', '.25',
                         '--settings-label', 'Testreihe')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_gainmatch_imports_both_channels_from_one_recording(self):
        result = self.import_spec('gainmatch', self.tone_recording)
        self.assertIn('Kanal-Differenz Ch2-Ch1 @48000: +0.00 dB', result.stdout)
        root = self.root / 'series'
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        self.assertEqual(len(index['runs']), 2)
        self.assertTrue(all(run['role'] == 'gainmatch' for run in index['runs']))
        self.assertTrue(index['dwarf_source'])
        for channel in (1, 2):
            report = json.loads(
                (root / f'gainmatch-ch{channel}-48000' / 'results.json')
                .read_text(encoding='utf-8'))
            self.assertAlmostEqual(report['segments'][0]['gain_db'], -3.0987, delta=.01)
        # A completed probe run is not silently overwritten.
        repeat = run_cli('import', '--root', str(root), '--recording',
                         str(self.recording), '--spec', 'gainmatch',
                         '--settle', '.25', '--measure', '.25')
        self.assertNotEqual(repeat.returncode, 0)

    def test_baseline_then_dut_relative_gain_and_summary(self):
        self.import_spec('baseline:r1')
        self.import_spec('60s:r1')
        root = self.root / 'series'
        index = json.loads((root / 'index.json').read_text(encoding='utf-8'))
        self.assertEqual(sorted({run['role'] for run in index['runs']}),
                         ['baseline', 'dut'])
        report = json.loads((root / '60s-ch1-r1-48000' / 'results.json')
                            .read_text(encoding='utf-8'))
        self.assertAlmostEqual(report['segments'][0]['relative_gain_db'], 0.0, delta=.01)
        summary = run_cli('summary', '--root', str(root))
        self.assertEqual(summary.returncode, 0, summary.stdout + summary.stderr)
        text = (root / 'SUMMARY.md').read_text(encoding='utf-8')
        self.assertIn('Dwarf-Quelle', text)
        self.assertNotIn('nicht erreichbar', text)
        self.assertIn('| 60s | 1 | 48000 | -14 | -14 | -14.00 |', text)

    def test_spec_and_missing_baseline_are_rejected(self):
        bad = run_cli('import', '--root', str(self.root / 'x'),
                      '--recording', str(self.recording), '--spec', 'Jensen999:r1')
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('transformer spec', bad.stderr)
        missing = run_cli('import', '--root', str(self.root / 'y'),
                          '--recording', str(self.recording), '--spec', '60s:r1',
                          '--settle', '.25', '--measure', '.25')
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn('Keine gueltige Baseline', missing.stderr)


if __name__ == '__main__':
    unittest.main()
