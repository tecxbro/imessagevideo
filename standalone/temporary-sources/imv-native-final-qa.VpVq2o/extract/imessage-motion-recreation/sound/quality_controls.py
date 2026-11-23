#!/usr/bin/env python3
"""Exercise audio quality checks with encoded negative controls."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from example import FIXTURE, synthesize
from media import RATE, dump, mux, run, sha256
from project import mix
from verify import verify


def controls(output):
    output.mkdir(parents=True, exist_ok=True)
    picture = FIXTURE / "picture.mp4"
    t = np.arange(RATE) / RATE
    bed = .12 * np.sin(2 * np.pi * 271 * t)
    wavfile.write(output / "bed.wav", RATE, np.column_stack((bed, bed)).astype(np.float32))
    synthesize(output / "accent.wav")
    plan = output / "plan.json"
    dump(plan, {"landmarks": {}, "cues": [
        {"id": "bed", "bus": "atmosphere", "asset": "bed.wav",
         "time_s": 0, "source": "Procedural test signal", "purpose": "Continuous audio control."},
        {"id": "accent", "bus": "effects", "asset": "accent.wav",
         "time_s": .5, "source": "Original example recipe", "purpose": "Test a quiet overlay."},
    ]})
    approved = output / "approved"
    manifest = mix(plan, picture, approved)
    _, audio = wavfile.read(approved / "mix.wav")
    cases = {"unmodified": approved / "mix.mp4"}
    for label, waveform in (
        ("missing_overlay", np.column_stack((bed, bed))),
        ("dropout", audio * ((t < .24) | (t >= .42))[:, None]),
        ("clipping", audio * 12),
        ("short_audio", audio[:RATE // 2]),
    ):
        wav = output / f"{label}.wav"
        export = output / f"{label}.mp4"
        wavfile.write(wav, RATE, waveform.astype(np.float32))
        mux(picture, wav, export)
        cases[label] = export

    discontinuity = output / "discontinuous_pts.mp4"
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", picture, "-i", approved / "mix.wav",
        "-map", "0:V:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", "aselect=not(between(t\\,0.25\\,0.40))", discontinuity)
    cases["discontinuous_pts"] = discontinuity

    required = {
        "unmodified": None,
        "missing_overlay": "decoded audio differs materially from the approved PCM",
        "dropout": "decoded audio has energy dropouts relative to the approved PCM",
        "clipping": "decoded audio clips or exceeds full scale between samples",
        "short_audio": "audio duration differs from picture beyond MP4 rounding/AAC padding",
        "discontinuous_pts": "decoded audio PTS has a nonzero start or gaps/overlaps",
    }
    outcomes = {}
    for label, export in cases.items():
        # Its approved WAV stays unchanged. Updating the export hash cannot authorize bad audio.
        test_manifest = approved / "control-manifest.json"
        dump(test_manifest, {**manifest, "export_sha256": sha256(export)})
        report = verify(plan, picture, export, test_manifest)
        dump(output / f"{label}.json", report)
        failures = report["failures"]
        if (required[label] is None and failures
                or required[label] is not None and required[label] not in failures):
            raise SystemExit(f"Unexpected verdict for {label}: {report}")
        outcomes[label] = failures
    return outcomes


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("output", type=Path)
    print(json.dumps(controls(cli.parse_args().output), indent=2))
