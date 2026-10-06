#!/usr/bin/env python3
"""Generate 24-bit PCM WAV test tones for direct playback on the MOD Dwarf.

The Dwarf file player replaces the Scarlett stimulus path: player -> GS76 ->
Dwarf output -> Scarlett input (recording only). The stimuli are byte-identical
to what tools/scarlett_matrix.py --dwarf-source generates per run, so plan.json
and the sync-marker analysis stay compatible.

Output: one directory per kind (mono reference + plan.json, exactly like the
measurement driver creates it) plus flat upload copies in mono and stereo
(L=R). A MANIFEST lists SHA256 hashes, upload notes and the matching driver
commands.

Offline only: numpy + soundfile. See docs/MESSTECHNIK.md, section
'Dwarf als Signalquelle'.
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import scarlett_test as measurement  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def level_tag(level):
    return f'{level:g}'.replace('.', 'p').replace('-', 'm')


# Keep in sync with ANCHORS_DBFS in tools/scarlett_matrix.py.
ANCHORS_DBFS = (-14.0, -8.0, -2.0)


def anchors_reachable(level, anchors=ANCHORS_DBFS):
    # The levels series of an 'all' file covers level-24..level in 6 dB steps.
    series = [level - step for step in (24, 18, 12, 6, 0)]
    missing = [a for a in anchors if not any(abs(a - s) < 1e-9 for s in series)]
    return not missing


def stereo_copy(mono_path, stereo_path):
    import numpy as np
    import soundfile as sf
    data, rate = sf.read(str(mono_path), dtype='float32')
    sf.write(str(stereo_path), np.column_stack((data, data)), rate, subtype='PCM_24')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('test-results/dwarf-tones'))
    parser.add_argument('--rate', type=int, default=48000)
    parser.add_argument('--level', type=float, default=-2,
                        help='Peak level of the matrix file in dBFS; -2 aligns the '
                             '20-Hz anchors -14/-8/-2 dBFS with the levels series')
    parser.add_argument('--frequency', type=float, default=1000)
    parser.add_argument('--settle', type=float, default=2,
                        help='Must match the driver run (--settle default 2)')
    parser.add_argument('--measure', type=float, default=1,
                        help='Must match the driver run (--measure default 1)')
    args = parser.parse_args(argv)
    if not anchors_reachable(args.level):
        parser.exit(1, f'Level {args.level:g} dBFS misses the -14/-8/-2 dBFS anchors; '
                       'use -2 dBFS (or a value 6 dB apart from them).\n')
    if args.rate != 48000:
        parser.exit(1, 'The Dwarf runs at 48 kHz; other rates are not supported here.\n')
    out = args.output
    if out.exists():
        parser.exit(1, f'{out} already exists; delete it to regenerate the tones.\n')
    tag = level_tag(args.level)
    kinds = [('all', f'matrix-all-{tag}'), ('tone', f'gainmatch-tone-{tag}')]
    entries = []
    for kind, name in kinds:
        source = out / 'runs' / name
        plan = measurement.generate(source, rate=args.rate, level=args.level,
                                    kind=kind, frequency=args.frequency,
                                    settle=args.settle, measure=args.measure,
                                    max_level=-0.1)
        mono = out / f'gs76-{name}-mono.wav'
        stereo = out / f'gs76-{name}-stereo.wav'
        shutil.copy2(source / 'stimulus.wav', mono)
        stereo_copy(source / 'stimulus.wav', stereo)
        seconds = plan['frames'] / args.rate
        segments = len(plan['segments'])
        print(f'{kind}: {segments} Segmente, {seconds:.1f} s, '
              f'{stereo.name} + {mono.name}')
        entries.append(dict(kind=kind, name=name, seconds=round(seconds, 2),
                            segments=segments, level_dbfs=args.level,
                            frequency_hz=args.frequency, rate=args.rate,
                            settle_s=args.settle, measure_s=args.measure,
                            stimulus_sha256=plan['stimulus_sha256'],
                            upload_stereo=stereo.name, upload_mono=mono.name,
                            mono_sha256=sha(mono), stereo_sha256=sha(stereo)))
    manifest = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
                    generator_sha256=sha(Path(__file__)),
                    scarlett_test_sha256=sha(TOOLS / 'scarlett_test.py'),
                    files=entries, upload_hint='24-bit PCM WAV, 48 kHz, auf den Dwarf '
                                               'hochladen; Stereo-Datei (L=R) bevorzugen')
    with (out / 'MANIFEST.json').open('w', encoding='utf-8', newline='') as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    matrix = next(e for e in entries if e['kind'] == 'all')
    tone = next(e for e in entries if e['kind'] == 'tone')
    lines = [
        '# Dwarf-Testtöne (Green Stripe 76)',
        '',
        f'Erzeugt am {manifest["created_utc"]}; Parameter: {args.rate} Hz, '
        f'{args.level:g} dBFS Peak, {args.frequency:g} Hz, settle {args.settle:g} s, '
        f'measure {args.measure:g} s, PCM_24.',
        '',
        '## Hochladen (Dwarf, Web-UI Dateimanager oder SCP)',
        '',
        f'- `{matrix["upload_stereo"]}` — Matrix-/Baseline-Datei, '
        f'{matrix["segments"]} Segmente, {matrix["seconds"]} s',
        f'- `{tone["upload_stereo"]}` — Gainmatch-Ton, '
        f'{tone["segments"]} Segment, {tone["seconds"]} s',
        '- Mono-Varianten (`*-mono.wav`) nur falls der Player Stereo verweigert.',
        '',
        'Die Stereo-Dateien sind L=R-Kopien; die Auswertung korreliert je Kanal '
        'gegen die Mono-Referenz in `runs/*/stimulus.wav`. SHA256 der '
        'Hochladedateien steht in `MANIFEST.json`.',
        '',
        '## Messreihe (Windows-Testrechner, Aufnahme 48 kHz/24 bit, '
        'Signalverbesserungen aus)',
        '',
        'Pedalboard auf dem Dwarf: File-Player -> Green Stripe 76 -> Ausgänge.',
        '',
        '```bat',
        f'python tools\\scarlett_matrix.py gainmatch  --dwarf-source --level {args.level:g} \\',
        f'    --frequency {args.frequency:g} --settle {args.settle:g} --measure {args.measure:g} --root <Messreihe>',
        'python tools\\scarlett_matrix.py baseline   --dwarf-source --level '
        f'{args.level:g} --root <Messreihe>',
        'python tools\\scarlett_matrix.py matrix     --dwarf-source --level '
        f'{args.level:g} --root <Messreihe>',
        'python tools\\scarlett_matrix.py full       --dwarf-source --level '
        f'{args.level:g} --root <Messreihe>',
        '```',
        '',
        f'Bei `-2 dBFS` liegen die Anker −14/−8/−2 dBFS exakt auf den Pegelstufen; '
        'der Loop-Gewinn betrifft nur noch den Aufnahmepegel (Dwarf-OUTPUT-Knopf '
        'runterdrehen, wenn Aufnahmen clippen; Zielbereich grob −6…+3 dB).',
        '',
        'Ablauf je Lauf: Enter im Skript drücken, dann SOFORT die Datei auf dem '
        'Dwarf starten. Die Aufnahme hat 10 s Vorlauf (`--pad`); '
        '`--max-delay` folgt dem Pad.',
        '',
        'Bypass-Baseline: GS76 enabled/bypass OFF, sonst Regler unverändert. '
        'DUT: Transformator einstellen, Compression ON, Bypass AUS.',
        '',
    ]
    with (out / 'MANIFEST.md').open('w', encoding='utf-8', newline='') as stream:
        stream.write('\n'.join(lines))
    print(f'Manifest: {out / "MANIFEST.md"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
