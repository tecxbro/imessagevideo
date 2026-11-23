#!/usr/bin/env python3
"""Resolve a plan against picture, build stems, and verify the encoded MP4."""
import argparse
import json
from pathlib import Path
import sys

from media import dump
from project import landmark_rows, mix, resolved_cues
from verify import verify


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    resolve = commands.add_parser("resolve", help="print picture-derived anchors and placement samples")
    build = commands.add_parser("mix", help="create four editable stems, WAV, MP4 and manifest")
    check = commands.add_parser("verify", help="check the final decoded H.264/AAC export")
    for command in (resolve, build, check):
        command.add_argument("plan", type=Path)
        command.add_argument("picture", type=Path)
    build.add_argument("output", type=Path)
    build.add_argument("--replace-audio", action="store_true")
    check.add_argument("export", type=Path)
    check.add_argument("manifest", type=Path)
    check.add_argument("--report", type=Path)
    args = cli.parse_args()
    try:
        if args.command == "resolve":
            _, _, landmarks, cues = resolved_cues(args.plan, args.picture)
            result = {"landmarks": landmark_rows(landmarks), "cues": cues}
        elif args.command == "mix":
            result = mix(args.plan, args.picture, args.output, replace_audio=args.replace_audio)
        else:
            result = verify(args.plan, args.picture, args.export, args.manifest)
    except (ValueError, OSError, KeyError, TypeError) as error:
        result = {"pass": False, "failures": [str(error)]}
    if getattr(args, "report", None):
        dump(args.report, result)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result.get("pass", True) else 1


if __name__ == "__main__":
    sys.exit(main())
