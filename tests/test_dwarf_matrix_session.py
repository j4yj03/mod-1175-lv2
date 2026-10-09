#!/usr/bin/env python3
"""Offline acceptance fuer tools/dwarf_matrix_session.py.

Abgedeckt: Chirp-Erkennung (block_correlate/find_playbacks), Zusammenfassung
naher Treffer, Ratenpruefung, Reihenfolgezuordnung und Schnittgrenzen von
do_cut. Nicht abgedeckt: do_analyze/do_report (benoetigen die scarlett_test-
Analysekette, die von test_scarlett_test.py/test_scarlett_matrix.py
abgedeckt wird) und den echten Geraetelauf.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import soundfile as sf

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import dwarf_matrix_session as session  # noqa: E402


class DwarfMatrixSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Kurzes 'all'-Programm: der Pilot-Chirp liegt unabhaengig von
        # settle/measure fest bei Frame 24000 (0,5 s Vorstille + 0,12 s Chirp).
        plan = session.measurement.generate(self.root / 'stim', rate=session.RATE,
                                            level=session.LEVEL, kind='all',
                                            frequency=1000, settle=0.25, measure=0.25,
                                            max_level=-0.1)
        self.stimulus = self.root / 'stim' / 'stimulus.wav'
        self.stim_frames = plan['frames']
        self._old_stim = session._STIM
        session._STIM = self.stimulus
        self.addCleanup(setattr, session, '_STIM', self._old_stim)
        stim, rate = sf.read(str(self.stimulus), dtype='float64', always_2d=True)
        self.assertEqual(rate, session.RATE)
        self.stim = stim
        self.chirp = np.ascontiguousarray(stim[session.CHIRP_START:
                                               session.CHIRP_START + session.CHIRP_FRAMES, 0])

    def build_recording(self, playbacks, rate=session.RATE, noise=1e-4):
        """Spielt das Programm n-mal mit Pausen ein; Rueckgabe: Startframes."""
        gap = round(2.0 * rate)
        pre = round(1.0 * rate)
        total = pre + playbacks * (self.stim_frames + gap) + round(1.0 * rate)
        rng = np.random.default_rng(20261008)
        signal = noise * rng.standard_normal((total, 2))
        starts = []
        for i in range(playbacks):
            begin = pre + i * (self.stim_frames + gap)
            signal[begin:begin + self.stim_frames] += self.stim * 0.7
            starts.append(begin + session.CHIRP_START)
        path = self.root / 'recording.wav'
        sf.write(str(path), signal, rate, subtype='PCM_24')
        return path, starts

    def test_block_correlate_finds_isolated_hits(self):
        path, starts = self.build_recording(3)
        data, _ = sf.read(str(path), dtype='float64', always_2d=True)
        hits = session.block_correlate(np.ascontiguousarray(data[:, 0]), self.chirp)
        self.assertEqual(len(hits), 3)
        for (quality, pos), start in zip(hits, starts):
            self.assertGreater(quality, 0.9)
            self.assertLessEqual(abs(pos - start), 2)

    def test_block_correlate_merges_close_hits(self):
        # Zwei Chirps 0,5 s apart: innerhalb der Merge-Schwelle (1 s) -> ein Treffer.
        n = len(self.chirp)
        signal = np.zeros(4 * session.RATE)
        for begin in (session.RATE, session.RATE + n // 2):
            signal[begin:begin + n] += self.chirp
        hits = session.block_correlate(signal, self.chirp)
        self.assertEqual(len(hits), 1)

    def test_block_correlate_stays_silent_without_chirp(self):
        rng = np.random.default_rng(7)
        signal = 1e-3 * rng.standard_normal(2 * session.RATE)
        self.assertEqual(session.block_correlate(signal, self.chirp), [])

    def test_find_playbacks_rejects_wrong_rate(self):
        path = self.root / 'wrong-rate.wav'
        sf.write(str(path), np.zeros((1000, 2)), 44100, subtype='PCM_24')
        with self.assertRaises(SystemExit):
            session.find_playbacks(path, self.stim_frames)

    def test_find_playbacks_maps_positions(self):
        path, starts = self.build_recording(3)
        _, plays = session.find_playbacks(path, self.stim_frames)
        self.assertEqual([p['start'] for p in plays], starts)
        for play, start in zip(plays, starts):
            self.assertEqual(play['program_begin'], start - session.CHIRP_START)
            self.assertGreater(play['quality'], 0.9)

    def test_do_cut_assigns_order_and_bounds(self):
        path, starts = self.build_recording(3)
        out = self.root / 'cuts'
        session.do_cut(type('Args', (), dict(recording=path, output=out))())
        index = json.loads((out / 'cuts.json').read_text(encoding='utf-8'))
        self.assertEqual([e['label'] for e in index['playbacks']],
                         session.ORDER[:3])
        self.assertEqual(index['order'], session.ORDER)
        data_frames = sf.info(str(path)).frames
        for entry, start in zip(index['playbacks'], starts):
            expected_begin = max(0, entry['program_begin'] - session.GUARD)
            expected_end = min(data_frames, entry['program_begin'] + self.stim_frames + session.GUARD)
            info = sf.info(str(out / entry['file']))
            self.assertEqual(info.frames, expected_end - expected_begin)
            self.assertEqual(info.samplerate, session.RATE)
            self.assertEqual(entry['start'], start)

    def test_do_cut_warns_on_unexpected_count(self):
        path, _ = self.build_recording(2)
        out = self.root / 'cuts2'
        import contextlib
        import io
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            session.do_cut(type('Args', (), dict(recording=path, output=out))())
        self.assertIn('WARNUNG: 2 Wiedergaben gefunden, 11 erwartet', buffer.getvalue())
        index = json.loads((out / 'cuts.json').read_text(encoding='utf-8'))
        self.assertEqual([e['label'] for e in index['playbacks']], session.ORDER[:2])

    def test_order_is_wellformed(self):
        self.assertEqual(session.ORDER[0], 'reference')
        self.assertEqual(len(session.ORDER), len(set(session.ORDER)))
        self.assertIn('60s', session.ORDER)
        self.assertIn('col100', session.ORDER)


if __name__ == '__main__':
    unittest.main()
