#!/usr/bin/env python3
"""Combine two uninstrumented ysfx benchmark JSON runs with source provenance."""
import argparse
import hashlib
import json
from pathlib import Path


def hashes(directory):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.glob('*.jsfx*'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--before-source', type=Path, required=True)
    parser.add_argument('--after-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
# read_text() without an encoding uses the locale encoding, which on Windows
#     is cp1252 and mangles the UTF-8 dashes in data/*.json.
    before, after = json.loads(args.before.read_text(encoding='utf-8')), json.loads(args.after.read_text(encoding='utf-8'))
    for key in ('rate', 'block', 'frames', 'repeats', 'gui'):
        if before[key] != after[key]:
            raise SystemExit('Benchmark protocols differ: ' + key)
    old = {(row['variant'], row['scenario']): row for row in before['cases']}
    results = []
    for new in after['cases']:
        previous = old[(new['variant'], new['scenario'])]
        a, b = previous['seconds_per_audio_second'], new['seconds_per_audio_second']
        results.append(dict(variant=new['variant'], scenario=new['scenario'],
                            before_seconds_per_audio_second=a, after_seconds_per_audio_second=b,
                            reduction_percent=100 * (1 - b / a), speedup=a / b))
    report = dict(
        test_host='JoepVanlier/ysfx 5c3452fee62583aa3d1b7e877d0c758c4024af89, x86_64 WSL, GCC15.2',
        protocol={key: before[key] for key in ('rate', 'block', 'frames', 'repeats', 'gui')},
        limitations='Same local host and vectors, compilation/GUI excluded; sequential median runs are hardware/load dependent. Not REAPER CPU%, Dwarf CPU%, or a comparison with unidentified other JSFX.',
        before_source_hashes=hashes(args.before_source), after_source_hashes=hashes(args.after_source),
        cases=results,
    )
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    for row in results:
        print(row['variant'], row['scenario'], f"{row['reduction_percent']:.1f}% less time", f"{row['speedup']:.2f}x")


if __name__ == '__main__':
    main()
