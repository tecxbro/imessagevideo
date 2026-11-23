#!/usr/bin/env python3
"""Mux approved stale audio onto a revised picture and report decoded timing."""
import argparse
import json
from pathlib import Path
import shutil

from media import dump, mux, sha256
from verify import verify


def stale_audio_control(plan, revised_picture, previous_manifest, output):
    manifest = json.loads(previous_manifest.read_text())
    approved_pcm = previous_manifest.parent / "mix.wav"
    picture_hash = sha256(revised_picture)
    if manifest["picture_sha256"] == picture_hash:
        raise ValueError("the revised picture is identical to the previous picture")
    if manifest["plan_sha256"] != sha256(plan):
        raise ValueError("the supplied plan differs from the previous mix plan")
    if manifest["mix_sha256"] != sha256(approved_pcm):
        raise ValueError("the previous mix WAV does not match its manifest")

    pcm = output / "mix.wav"
    export = output / "mix.mp4"
    control_manifest = output / "manifest.json"
    report_path = output / "verify.json"
    inputs = {path.resolve() for path in (plan, revised_picture, previous_manifest, approved_pcm)}
    if inputs & {path.resolve() for path in (pcm, export, control_manifest, report_path)}:
        raise ValueError("negative-control output would overwrite an input")
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(approved_pcm, pcm)
    mux(revised_picture, pcm, export)
    # Bind the control to the actual mux but keep the original cue placements.
    dump(control_manifest, {**manifest, "picture_sha256": picture_hash,
                            "export_sha256": sha256(export)})
    report = verify(plan, revised_picture, export, control_manifest)
    dump(report_path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("revised_picture", type=Path)
    parser.add_argument("previous_manifest", type=Path)
    parser.add_argument("output", type=Path, help="directory for the negative control")
    args = parser.parse_args()
    try:
        report = stale_audio_control(args.plan, args.revised_picture, args.previous_manifest,
                                     args.output)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
