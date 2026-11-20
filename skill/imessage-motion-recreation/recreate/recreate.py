#!/usr/bin/env python3
"""Measure, inspect and compare iMessage source video and independent exports."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from analyze import analyze, inspect, read_range
from compare import compare
from media import write_json


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    measure = commands.add_parser("analyze", help="decode the complete source and cache measurements")
    measure.add_argument("source")
    measure.add_argument("--out", required=True)
    view = commands.add_parser("inspect", help="export selected consecutive native frames")
    view.add_argument("source")
    view.add_argument("--out", required=True)
    view.add_argument("--frames", required=True, help="inclusive spans, e.g. 12:20,45,100:105")
    view.add_argument("--crop", nargs=4, type=int, metavar=("X", "Y", "WIDTH", "HEIGHT"))
    view.add_argument("--ocr", action="store_true")
    view.add_argument("--sheet-width", type=int, default=300)
    check = commands.add_parser("compare", help="decode both complete videos and test native-clock and pixel gates")
    check.add_argument("reference")
    check.add_argument("candidate")
    check.add_argument("--checks", help="JSON thresholds and interaction windows")
    check.add_argument("--out", required=True)
    check.add_argument("--sheets", action="store_true", help="make comparison sheets")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        if args.command == "analyze":
            report = analyze(args.source, args.out)
            print(f"{report['picture_decoded_frames']} decoded frames; {Path(args.out) / 'analysis.json'}")
        elif args.command == "inspect":
            inspect(args.source, args.out, [read_range(item) for item in args.frames.split(",")],
                    args.crop, args.ocr, args.sheet_width)
        else:
            report = compare(args.reference, args.candidate, args.out, args.checks, args.sheets)
            print(f"{report['verdict']}  {report['compared_frames']} compared frames  {Path(args.out) / 'report.json'}")
            for failure in report["failures"]:
                print(json.dumps(failure))
            return 0 if report["verdict"] == "PASS" else 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        if args.command == "compare":
            write_json(Path(args.out) / "report.json",
                       {"schema": 1, "verdict": "ERROR", "decode_completed": False, "message": str(error)})
        print(f"ERROR  {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
