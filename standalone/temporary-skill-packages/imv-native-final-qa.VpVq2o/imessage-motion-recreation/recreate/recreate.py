#!/usr/bin/env python3
"""Measure, inspect and compare iMessage source video and independent exports."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from analyze import analyze, inspect, measure_landmarks, read_range
from compare import compare
from encode import encode_measured_clock
from media import write_json
from review import prepare_review, verify_review


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    measure = commands.add_parser("analyze", help="decode the complete source and cache measurements")
    measure.add_argument("source")
    measure.add_argument("--out", required=True)
    measure.add_argument("--reuse", action="store_true", help="use a complete saved measurement for the same source SHA")
    view = commands.add_parser("inspect", help="export selected consecutive native frames")
    view.add_argument("source")
    view.add_argument("--out", required=True)
    view.add_argument("--frames", required=True, help="inclusive spans, e.g. 12:20,45,100:105")
    view.add_argument("--crop", nargs=4, type=int, metavar=("X", "Y", "WIDTH", "HEIGHT"))
    view.add_argument("--ocr", action="store_true")
    view.add_argument("--ocr-mode", choices=("sparse", "line", "block"), default="sparse")
    view.add_argument("--sheet-width", type=int, default=300)
    view.add_argument("--measurements", help="reuse and verify a saved source timeline")
    locate = commands.add_parser("landmarks", help="track flat-colored landmarks in native frame windows")
    locate.add_argument("source")
    locate.add_argument("--plan", required=True)
    locate.add_argument("--out", required=True)
    locate.add_argument("--measurements", help="reuse and verify a saved source timeline")
    check = commands.add_parser("compare", help="decode both complete videos and test native-clock and pixel gates")
    check.add_argument("reference")
    check.add_argument("candidate")
    check.add_argument("--checks", help="JSON thresholds and interaction windows")
    check.add_argument("--out", required=True)
    check.add_argument("--sheets", action="store_true", help="make comparison sheets")
    check.add_argument("--pairs", action="store_true", help="export a browsable side-by-side pair for every aligned frame")
    check.add_argument("--exact", action="store_true", help="fail on any changed RGB channel or presentation time")
    check.add_argument("--crops", action="store_true", help="write native PNG evidence for named regions")
    tasks = commands.add_parser("prepare-review", help="prepare evidence-linked visual review tasks from the decoded comparison")
    tasks.add_argument("--plan", required=True)
    tasks.add_argument("--comparison", required=True)
    tasks.add_argument("--out", required=True, help="write the review task and unanswered result JSON")
    review = commands.add_parser("verify-review", help="check that one decoded candidate passes every locked shot criterion")
    review.add_argument("candidate")
    review.add_argument("--plan", required=True)
    review.add_argument("--review", required=True)
    review.add_argument("--comparison", required=True, help="report.json from compare for this candidate")
    review.add_argument("--scoped", action="store_true", help="report against an explicitly agreed narrower scope")
    review.add_argument("--out", required=True, help="write the acceptance result to this JSON file")
    encode = commands.add_parser("encode-clock", help="encode an authored PNG cache with the measured frame clock")
    encode.add_argument("frames", help="directory with authored 000000.png onward")
    encode.add_argument("--measurements", required=True)
    encode.add_argument("--out", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        if args.command == "analyze":
            report = analyze(args.source, args.out, args.reuse)
            print(f"{report['picture_decoded_frames']} decoded frames; {Path(args.out) / 'analysis.json'}")
        elif args.command == "inspect":
            inspect(args.source, args.out, [read_range(item) for item in args.frames.split(",")],
                    args.crop, args.ocr, args.sheet_width, args.ocr_mode, args.measurements)
        elif args.command == "landmarks":
            measure_landmarks(args.source, args.plan, args.out, args.measurements)
        elif args.command == "encode-clock":
            report = encode_measured_clock(args.frames, args.measurements, args.out)
            print(f"{report['matched_presentation_timestamps']} exact timestamps; end {report['matched_end_seconds']}s")
        elif args.command == "prepare-review":
            result = prepare_review(args.plan, args.comparison, args.out)
            write_json(Path(args.out), result)
            print(f"{len(result['tasks'])} review tasks  {args.out}")
        elif args.command == "verify-review":
            result = verify_review(args.plan, args.review, args.comparison, args.candidate, scoped=args.scoped)
            write_json(Path(args.out), result)
            print(f"{result['verdict']}  {result['passed_shots']}/{result['shot_count']} shots pass ({result['scope']})  {args.out}")
            return 0 if result["verdict"] in ("PASS", "SCOPED_PASS") else 1
        else:
            report = compare(args.reference, args.candidate, args.out, args.checks, args.sheets, args.pairs,
                             exact=args.exact, crops=args.crops)
            print(f"{report['verdict']}  {report['compared_frames']} compared frames  {Path(args.out) / 'report.json'}")
            pixels = report["pixel_equality"]
            print(f"{pixels['identical_frames']}/{report['compared_frames']} frames identical in decoded RGB")
            if not report["regions"]:
                print("Coverage: picture-level checks; add native interaction windows for event-level validation.")
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
