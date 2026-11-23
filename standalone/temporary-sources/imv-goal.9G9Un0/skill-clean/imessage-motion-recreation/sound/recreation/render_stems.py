"""Print one picture-length editable WAV track for each Train options cue."""
import json
from pathlib import Path
import sys

import numpy as np
from scipy.io import wavfile

from media import RATE, decode, sha256
from project import read_plan


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python3 -m recreation.render_stems PLAN MIX_DIRECTORY")
    plan_path, output = map(Path, sys.argv[1:])
    manifest = json.loads((output / "manifest.json").read_text())
    if sha256(plan_path) != manifest["plan_sha256"]:
        raise ValueError("the score differs from the rendered manifest")
    plan, cues = read_plan(plan_path)
    shape = (manifest["sample_count"], 2)
    total = np.zeros(shape, dtype=np.float32)
    edits = {}
    for cue, row in zip(cues, manifest["cues"], strict=True):
        if cue.id != row["id"] or sha256(cue.asset) != row["asset_sha256"]:
            raise ValueError(f"{cue.id}: the score or asset differs from the rendered manifest")
        start, end = row["asset_start_sample"], row["asset_end_sample"]
        audio = np.zeros(shape, dtype=np.float32)
        audio[start:end] = decode(cue.asset) * 10 ** (cue.gain_db / 20)
        audio *= 10 ** (float(plan.get("bus_gain_db", {}).get(cue.bus, 0)) / 20)
        edits[cue.id] = audio
        total += audio
    if not np.array_equal(total, decode(output / "mix.wav")):
        raise ValueError("individual edit tracks do not sum to the approved mix")
    folder = output / "cue-stems"
    folder.mkdir(exist_ok=True)
    for name, audio in edits.items():
        wavfile.write(folder / f"{name}.wav", RATE, audio)


if __name__ == "__main__":
    main()
