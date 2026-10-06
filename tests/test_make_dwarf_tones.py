#!/usr/bin/env python3
"""Offline acceptance for the Dwarf test-tone generator."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import make_dwarf_tones as tones


class DwarfToneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_generates_upload_files_and_matching_reference(self):
        out = self.root / 'tones'
        exit_code = tones.main(['--output', str(out), '--settle', '.25',
                                '--measure', '.25'])
        self.assertEqual(exit_code, 0)
        stereo = out / 'gs76-matrix-all-m2-stereo.wav'
        mono = out / 'gs76-matrix-all-m2-mono.wav'
        tone = out / 'gs76-gainmatch-tone-m2-stereo.wav'
        for path in (stereo, mono, tone):
            self.assertTrue(path.is_file(), path)
        info = sf.info(str(stereo))
        self.assertEqual(info.subtype, 'PCM_24')
        self.assertEqual(info.samplerate, 48000)
        self.assertEqual(info.channels, 2)
        data, _ = sf.read(str(stereo), dtype='float32')
        self.assertEqual(data.ndim, 2)
        self.assertTrue((data[:, 0] == data[:, 1]).all(), 'stereo upload must be L=R')
        # The mono upload copy must be byte-identical to the run reference
        # the analysis driver generates.
        self.assertEqual(hashlib.sha256(mono.read_bytes()).hexdigest(),
                         hashlib.sha256((out / 'runs/matrix-all-m2/stimulus.wav')
                                        .read_bytes()).hexdigest())
        manifest = json.loads((out / 'MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['files']), 2)
        by_kind = {entry['kind']: entry for entry in manifest['files']}
        self.assertEqual(by_kind['all']['segments'], 19)
        self.assertEqual(by_kind['all']['stimulus_sha256'],
                         by_kind['all']['mono_sha256'])
        text = (out / 'MANIFEST.md').read_text(encoding='utf-8')
        self.assertIn('--dwarf-source --level -2', text)

    def test_rejects_levels_that_miss_the_anchors(self):
        with self.assertRaises(SystemExit):
            tones.main(['--output', str(self.root / 'bad'), '--level', '-12'])


if __name__ == '__main__':
    unittest.main()
