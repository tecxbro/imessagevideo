#!/usr/bin/env python3
"""Replay the contract example, including intentional final-export failures."""
import argparse
from pathlib import Path
import shutil

import numpy as np
from scipy.io import wavfile

from media import RATE, dump, mux, sha256
from project import mix
from retime_control import stale_audio_control
from verify import verify

FIXTURE = Path(__file__).resolve().parent / "fixtures"


def synthesize(path):
    """Original small mechanical click with a pitched tail and two attack moments."""
    t = np.arange(RATE // 5) / RATE
    rng = np.random.default_rng(271)
    texture = rng.normal(0, 1, len(t))
    attack = np.exp(-((t - .030) / .0028) ** 2) * texture * .23
    preparatory = np.exp(-((t - .014) / .0015) ** 2) * texture * .045
    tail_t = np.maximum(0, t - .030)
    tail = (t >= .030) * np.sin(2 * np.pi * (900 * tail_t - 820 * tail_t ** 2))
    tail *= np.exp(-tail_t * 46) * np.minimum(tail_t / .002, 1) * .25
    sound = (attack + preparatory + tail) * np.minimum(1, (t[-1] - t) / .005)
    stereo = np.stack((sound, sound * .91), axis=1)
    wavfile.write(path, RATE, stereo.astype(np.float32))


def corrupt(picture, source, destination, manifest, variant):
    destination.mkdir(exist_ok=True)
    _, audio = wavfile.read(source / "mix.wav")
    shift = RATE // 5
    broken = np.zeros_like(audio)
    if variant != "missing":
        broken[shift:] = audio[:-shift]
    wavfile.write(destination / "mix.wav", RATE, broken)
    mux(picture, destination / "mix.wav", destination / "mix.mp4")
    metadata = {**manifest, "mix_sha256": sha256(destination / "mix.wav"),
                "export_sha256": sha256(destination / "mix.mp4")}
    if variant == "jointly_shifted":
        # Move the manifest's purported event and cue together by 200 ms.
        metadata["landmarks"] = {key: {**landmark, "pts": "7/10", "sample": landmark["sample"] + shift,
                                       "frame": 17}
                                 for key, landmark in metadata["landmarks"].items()}
        metadata["cues"] = [{**cue, "event_frame": 17,
                             **{key: cue[key] + shift for key in (
                                 "asset_start_sample", "asset_end_sample",
                                 "onset_marker_sample", "impact_sample")}}
                            for cue in metadata["cues"]]
    dump(destination / "manifest.json", metadata)


def run(output, selected_picture=None):
    output.mkdir(parents=True, exist_ok=True)
    plan = output / "plan.json"
    shutil.copyfile(FIXTURE / "plan.json", plan)
    synthesize(output / "send.wav")

    def verify_export(picture, destination):
        report = verify(plan, picture, destination / "mix.mp4", destination / "manifest.json")
        dump(destination / "verify.json", report)
        return report

    if selected_picture:
        mix(plan, selected_picture, output)
        result = verify_export(selected_picture, output)
        if not result["pass"]:
            raise SystemExit("Selected picture failed verification. See verify.json.")
        return result

    original = FIXTURE / "picture.mp4"
    corrected = FIXTURE / "revised.mp4"
    good = output / "correct"
    manifest = mix(plan, original, good)
    results = {"correct": verify_export(original, good)}
    for variant in ("late", "missing", "jointly_shifted"):
        corrupt(original, good, output / variant, manifest, variant)
        results[variant] = verify_export(original, output / variant)
    # Old timing against revised picture, then a new mix from the same editorial plan.
    results["stale"] = stale_audio_control(plan, corrected, good / "manifest.json",
                                           output / "stale")
    mix(plan, corrected, output / "remapped")
    results["remapped"] = verify_export(corrected, output / "remapped")

    verdicts = {label: (outcome["pass"], outcome["cues"][0]["verdict"])
                for label, outcome in results.items()}
    expected = {"correct": (True, "pass"), "late": (False, "late"),
                "missing": (False, "missing"), "jointly_shifted": (False, "late"),
                "stale": (False, "early"), "remapped": (True, "pass")}
    if verdicts != expected:
        raise SystemExit(f"Wrong export checker verdicts: {verdicts}; see verify.json per case")
    return {label: {"pass": result["pass"], "verdict": result["cues"][0]["verdict"],
                    "frame": result["landmarks"]["demo.message.send"]["frame"],
                    "error_ms": result["cues"][0].get("error_ms")}
            for label, result in results.items()}


if __name__ == "__main__":
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--picture", type=Path, help="mix an independently supplied cut")
    options = parser.parse_args()
    print(json.dumps(run(options.output, options.picture), indent=2))
