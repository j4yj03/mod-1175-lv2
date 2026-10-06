#!/usr/bin/env python3
"""Offline acceptance for the MOD Dwarf load test: /proc parsing, statistics,
plugin instance counting, xrun deltas and report handling. No device needed."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import dwarf_loadtest as loadtest


def write_atomic(path, text):
    # procfs never exposes a half written file, so the fixture must not either.
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(text, encoding='utf-8')
    tmp.replace(path)


def stat_line(pid, comm, utime, stime, state='S'):
    # Field layout of /proc/<pid>/stat after the comm field.
    fields = [state, '1', str(pid), str(pid), '0', '-1', '0', '0', '0', '0', '0',
              str(utime), str(stime), '0', '0', '20', '0', '3', '0', '100']
    return '%d (%s) %s\n' % (pid, comm, ' '.join(fields))


class FakeProcess:
    """Minimal synthetic /proc/<pid> whose CPU counters grow over time."""

    def __init__(self, root, pid=42, plugin_instances=0, plugin_path=None):
        self.root = Path(root)
        self.pid = pid
        self.plugin_instances = plugin_instances
        self.plugin_path = plugin_path
        base = self.root / str(pid)
        (base / 'task' / str(pid)).mkdir(parents=True, exist_ok=True)
        (base / 'comm').write_text('jackd\n', encoding='utf-8')
        (base / 'cmdline').write_bytes(b'jackd\x00-r\x00/dev/DWARF\x00-p\x00128\x00')
        (base / 'task' / str(pid) / 'comm').write_text('jackd\n', encoding='utf-8')
        self.threads = [str(pid), str(pid + 1)]
        for tid in self.threads:
            (base / 'task' / tid).mkdir(parents=True, exist_ok=True)
            (base / 'task' / tid / 'comm').write_text('jackd\n', encoding='utf-8')
        self.ticks = {tid: 0 for tid in self.threads}
        self.write()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def write(self):
        base = self.root / str(self.pid)
        total = sum(self.ticks.values())
        write_atomic(base / 'stat', stat_line(self.pid, 'jackd', total, 0))
        for tid in self.threads:
            write_atomic(base / 'task' / tid / 'stat',
                         stat_line(int(tid), 'jackd rt', self.ticks[tid], 0))
        lines = []
        for _ in range(self.plugin_instances):
            lines.append('7f0000-7f1000 r-xp 00000000 08:01 1   %s' % self.plugin_path)
            lines.append('7f1000-7f2000 r--p 00001000 08:01 1   %s' % self.plugin_path)
            lines.append('7f2000-7f3000 rw-p 00002000 08:01 1   %s' % self.plugin_path)
        lines.append('7f4000-7f5000 r-xp 00000000 08:01 2   /lib/libc.so.6')
        write_atomic(base / 'maps', '\n'.join(lines) + '\n')

    def run(self):
        # The audio thread burns more than the helper thread, as on the device.
        rate = {self.threads[0]: 3, self.threads[1]: 1}
        while not self.stop.wait(0.01):
            for tid in self.threads:
                self.ticks[tid] += rate[tid]
            self.write()

    def close(self):
        self.stop.set()
        self.thread.join()


class LoadTestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / 'lv2' / loadtest.PLUGIN_NAME
        self.binary.parent.mkdir(parents=True)
        self.binary.write_bytes(b'green-stripe-76')
        self.processes = []

    def tearDown(self):
        for process in self.processes:
            process.close()

    def wait_for_ticks(self, process, timeout=2.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if any(process.ticks.values()):
                return
            time.sleep(0.01)
        raise AssertionError('fixture produced no CPU ticks')

    def start(self, instances):
        process = FakeProcess(self.root, plugin_instances=instances,
                              plugin_path=self.binary)
        self.processes.append(process)
        return process

    def arguments(self, **overrides):
        values = dict(label='GS76x1', note='', frames=128, seconds=0.6, interval=0.1,
                      expect_instances=1, expect_sha256='', jackd_pid=None, clk_tck=100,
                      plugin_name=loadtest.PLUGIN_NAME, xrun_command=[['true']],
                      report=None, markdown=None, self_test=False)
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_find_jackd_and_cmdline(self):
        self.start(0)
        self.assertEqual(loadtest.find_jackd(self.root), 42)
        self.assertIn('/dev/DWARF', loadtest.read_cmdline(self.root, 42))

    def test_find_jackd_missing(self):
        self.root.mkdir(exist_ok=True)
        with self.assertRaises(SystemExit):
            loadtest.find_jackd(self.root)

    def test_cpu_ticks_survives_comm_with_spaces(self):
        process = self.start(0)
        self.wait_for_ticks(process)
        # Stop the fixture writer so the hand written counters stay untouched.
        process.close()
        self.processes.remove(process)
        base = self.root / '42'
        (base / 'task' / '42' / 'stat').write_text(
            stat_line(42, 'jack rt (x) y', 700, 300), encoding='utf-8')
        (base / 'task' / '42' / 'comm').write_text('jack rt (x) y\n', encoding='utf-8')
        (base / 'stat').write_text(stat_line(42, 'jack rt (x) y', 1200, 700), encoding='utf-8')
        total, threads = loadtest.cpu_ticks(self.root, 42)
        self.assertEqual(threads['42'], (1000, 'jack rt (x) y'))
        self.assertEqual(total, 1900)
        self.assertEqual(threads['43'][1], 'jackd')

    def test_plugin_instances_counted_from_text_segments(self):
        for instances in (0, 1, 4):
            process = self.start(instances)
            maps = loadtest.plugin_maps(self.root, process.pid)
            self.assertEqual(maps['text_segments'], instances, maps)
            self.assertEqual(len(maps['segments']), 3 * instances)
            self.assertEqual(maps['binaries'], [] if instances == 0 else [str(self.binary)])
            if instances:
                identity = maps['identity'][str(self.binary)]
                self.assertTrue(identity['readable'])
                self.assertEqual(identity['bytes'], len(b'green-stripe-76'))
                self.assertTrue(loadtest.verify_identity(maps, identity['sha256']))
                self.assertFalse(loadtest.verify_identity(maps, '0' * 64))
            process.close()
            self.processes.remove(process)

    def test_verify_identity_ignores_hash_case_and_surrounding_space(self):
        maps = {'identity': {'/x/green-stripe-76.so': {'sha256': 'ab' * 32}}}
        self.assertTrue(loadtest.verify_identity(maps, 'AB' * 32))
        self.assertTrue(loadtest.verify_identity(maps, '  ' + 'ab' * 32 + '\n'))
        self.assertFalse(loadtest.verify_identity(maps, 'cd' * 32))
        self.assertIsNone(loadtest.verify_identity(maps, ''))

    def test_unreadable_plugin_binary_is_reported_not_fatal(self):
        process = self.start(1)
        binary = process.plugin_path
        binary.chmod(0o000)
        self.addCleanup(binary.chmod, 0o644)
        maps = loadtest.plugin_maps(self.root, process.pid)
        identity = maps['identity'][str(binary)]
        if identity.get('readable'):
            self.skipTest('filesystem ignores the permission bits')
        self.assertIn('error', identity)
        self.assertFalse(loadtest.verify_identity(maps, 'x'))

    def test_measurement_percentages_and_threads(self):
        self.start(2)
        args = self.arguments(seconds=1.0, interval=0.2, expect_instances=2)
        condition = loadtest.measure(args, self.root, 42, 100)
        self.assertEqual(condition['measured_text_segments'], 2)
        self.assertTrue(condition['instances_match_expectation'])
        # 400 ticks/s of a 100 Hz clock is 400 % of one core across two threads.
        self.assertGreater(condition['process_percent_mean'], 250)
        self.assertLess(condition['process_percent_mean'], 550)
        self.assertEqual(len(condition['threads']), 2)
        self.assertGreater(condition['threads'][0]['percent_of_one_core'],
                           condition['threads'][1]['percent_of_one_core'])
        self.assertEqual(condition['clk_tck'], 100)
        self.assertEqual(condition['samples'], 5)

    def test_expectation_mismatch_is_flagged_not_fatal(self):
        self.start(1)
        args = self.arguments(seconds=0.4, interval=0.1, expect_instances=4)
        condition = loadtest.measure(args, self.root, 42, 100)
        self.assertFalse(condition['instances_match_expectation'])

    def test_xrun_delta_counts_only_the_window(self):
        # The counter grows by four between the before and after snapshot of one
        # window, which is exactly what an xrun burst during playback looks like.
        calls = []
        script = 'printf "ALSA: xrun: at least one XRUN\\n"; printf "ALSA: snd ok\\n"'

        def source(_):
            calls.append(1)
            return [{'command': 'fixture', 'available': True, 'returncode': 0,
                     'xrun_lines': 3 if len(calls) == 1 else 7}]

        original = loadtest.xrun_sources
        loadtest.xrun_sources = source
        self.addCleanup(setattr, loadtest, 'xrun_sources', original)
        self.start(0)
        args = self.arguments(seconds=0.4, interval=0.1)
        condition = loadtest.measure(args, self.root, 42, 100)
        self.assertEqual(condition['xrun_sources'][0]['before'], 3)
        self.assertEqual(condition['xrun_sources'][0]['after'], 7)
        self.assertEqual(condition['xrun_sources'][0]['during_window'], 4)
        self.assertTrue(loadtest.XRUN_PATTERN.search(script.split(';')[0].replace('printf "', '')))
        self.assertFalse(loadtest.XRUN_PATTERN.search('ALSA: snd_pcm_start ok'))

    def test_xrun_source_reports_unavailable_command(self):
        self.start(0)
        args = self.arguments(seconds=0.3, interval=0.1,
                              xrun_command=[['/nonexistent/xrun-tool']])
        condition = loadtest.measure(args, self.root, 42, 100)
        source = condition['xrun_sources'][0]
        self.assertFalse(source['available'])
        self.assertIn('error', source)

    def test_xrun_command_string_is_split_not_iterated(self):
        result = loadtest.xrun_sources(['echo ALSA xrun here'])
        self.assertEqual(result[0]['command'], 'echo ALSA xrun here')
        self.assertEqual(result[0]['xrun_lines'], 1)

    def test_summary_delta_per_instance(self):
        self.start(0)
        rows = []
        for label, percent, segments in (('GS76x0', 10.0, 0), ('GS76x2', 36.0, 2)):
            rows.append({'label': label, 'note': '', 'frames': 128,
                         'expected_instances': None, 'measured_text_segments': segments,
                         'plugin_binaries': [], 'plugin_identity': {},
                         'instances_match_expectation': None, 'md5_or_sha_match': None,
                         'measured_at': '2026-10-05T00:00:00+00:00', 'clk_tck': 100,
                         'window_seconds': 20.0, 'samples': 40, 'interval_seconds': 0.5,
                         'process_percent_mean': percent, 'process_percent_median': percent,
                         'process_percent_peak': percent + 1.0, 'process_ticks_total': 1,
                         'threads': [{'tid': '1', 'name': 'jackd',
                                      'percent_of_one_core': percent}],
                         'xrun_sources': [{'command': 'dmesg', 'during_window': 0}]})
        table = loadtest.summarise({'conditions': rows})
        self.assertIn('| GS76x0 | 128 | 0 | 10.00 % |', table)
        self.assertIn('| GS76x2 | 128 | 2 | 36.00 % |', table)
        self.assertIn('| GS76x2 | 128 | +26.00 % | +13.00 % |', table)
        self.assertIn('Kein Echtzeit', table)

    def test_report_append_keeps_conditions_and_rejects_other_schema(self):
        self.start(0)
        report = self.root / 'report.json'
        for label in ('GS76x0', 'GS76x1'):
            self.main(['--label', label, '--seconds', '0.3', '--interval', '0.1',
                       '--proc-root', str(self.root), '--report', str(report),
                       '--xrun-command', 'true'])
        stored = json.loads(report.read_text(encoding='utf-8'))
        self.assertEqual([row['label'] for row in stored['conditions']],
                         ['GS76x0', 'GS76x1'])
        self.assertEqual(stored['conditions'][0]['jackd_pid'], 42)
        broken = self.root / 'broken.json'
        broken.write_text(json.dumps({'schema': 99, 'conditions': []}), encoding='utf-8')
        with self.assertRaises(SystemExit):
            self.main(['--label', 'GS76x2', '--seconds', '0.3', '--interval', '0.1',
                       '--proc-root', str(self.root), '--report', str(broken),
                       '--xrun-command', 'true'])

    def main(self, argv):
        previous = sys.argv
        sys.argv = ['dwarf_loadtest.py'] + argv
        captured = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured):
                return loadtest.main()
        finally:
            sys.argv = previous


if __name__ == '__main__':
    unittest.main(verbosity=2)