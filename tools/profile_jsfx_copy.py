#!/usr/bin/env python3
"""Create a separate instrumented JSFX copy for operation counts, not CPU timing.

Never edits the source package. Use an empty temporary output directory.
Instrumenting changes execution overhead, so run timing on unmodified files.
"""
import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit("Choose an empty output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    for source in args.source.iterdir():
        if source.is_file():
            shutil.copy2(source, args.output / source.name)
    core = args.output / "GreenStripe76-Core.jsfx-inc"
    text = core.read_text()
    target_anchor = "  all===1 ? rectified" if "function gs_requested_db" in text else "  left=abs(gs_tap"
    release_anchor = "    cachedRelease!==releaseTime" if "cachedRelease!==releaseTime" in text else "    time=releaseTime*"
    replacements = [
        (target_anchor, "  gs_profile_targets+=1;\n" + target_anchor),
        ("  lagged=gs_zap(lagged+gs_lag", "  gs_profile_controllers+=1;\n  lagged=gs_zap(lagged+gs_lag"),
        (release_anchor, "    gs_profile_release+=1;\n" + release_anchor),
        ("        wanted=this.gs_target", "        gs_profile_iterations+=1;\n        wanted=this.gs_target"),
    ]
    for old, new in replacements:
        if text.count(old) != 1:
            raise SystemExit("Instrumentation anchor changed: " + old)
        text = text.replace(old, new)
    core.write_text(text, encoding="utf-8")
    print("Instrumented copy:", args.output)


if __name__ == "__main__":
    main()
