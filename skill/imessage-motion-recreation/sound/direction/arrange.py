#!/usr/bin/env python3
"""Write editable A/B plans for a measured cut of The Moon Cue."""
from pathlib import Path
import argparse
import json

PROVENANCE = "Original procedural audio from sound/direction/synthesize.py."


def cue(name, purpose, bus, gain, *, event=None, time_s=None, offset=0, impact=0,
        onset=0, fingerprint=None):
    entry = {
        "id": name, "asset": f"../assets/{name}.wav", "bus": bus, "gain_db": gain,
        "purpose": purpose, "source": PROVENANCE, "impact_ms": impact, "onset_ms": onset,
    }
    if event is None:
        entry["time_s"] = time_s
    else:
        entry.update(event=event, offset_ms=offset, tolerance_ms=25)
    if fingerprint is not None:
        entry["fingerprint_ms"] = fingerprint
    return entry


def plans(landmarks):
    common = [
        cue("seated-opening", "Establish the space and fade it as the phone takes focus.",
            "atmosphere", -6, time_s=0),
        cue("send", "Mark the stagehand's choice to ask and give the question a clean reading hold.",
            "effects", -10, event="message.question.send", impact=32, onset=24),
        cue("reply", "Shift the viewer's attention to the crew's answer without breaking its reading hold.",
            "effects", -13, event="message.answer.receive", impact=38, onset=29, offset=12),
        cue("tin", "Give the first movement of the closed tin weight and identify the prop as metal.",
            "effects", -5, event="prop.tin.open", impact=65, onset=35, offset=0, fingerprint=[47, 137]),
        cue("paper", "Make the small moon feel hand-cut and almost weightless as it leaves the tin.",
            "effects", -8, event="prop.moon.lift", impact=65, onset=35, offset=6, fingerprint=[45, 140]),
        cue("seated-return", "Return to the audience's point of view across the stage cut.",
            "atmosphere", -9, event="stage.return", offset=-85, impact=0, fingerprint=[440, 680]),
        cue("puppet", "A small cloth movement marks the rabbit's release.",
            "effects", -12, event="stage.rabbit.release", impact=65, onset=35, offset=0,
            fingerprint=[48, 141]),
        cue("audience-release", "Suggest the room exhaling once the rabbit relaxes.",
            "atmosphere", -5, event="stage.rabbit.release", impact=290, onset=155, offset=115,
            fingerprint=[230, 465]),
    ]
    room = [
        cue("seated-wait", "A nearly still seated room leads into the prop cut and clears the tin.",
            "atmosphere", -5, event="prop.table.reveal", offset=-1160, fingerprint=[535, 775]),
    ]
    music = [
        cue("tension", "A felt minor color builds a little expectation and clears before the contact.",
            "music", -12, event="prop.table.reveal", offset=-1030, fingerprint=[485, 655]),
        cue("release", "A restrained major color arrives as the stage crescent becomes legible.",
            "music", -13, event="stage.moon.enter", impact=250, onset=50, offset=18,
            fingerprint=[190, 355]),
    ]
    silence = [
        {
            "start_s": 3.8, "end_s": 4.38,
            "purpose": "Hold the unanswered question after the send.", "max_peak_dbfs": -57,
        },
    ]
    return {
        "a": {"landmarks": landmarks, "cues": common + room, "silence": silence},
        "b": {"landmarks": landmarks, "cues": common + music, "silence": silence},
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("cut", type=Path, help="folder containing landmarks.json and picture.mp4")
    folder = cli.parse_args().cut
    for version, plan in plans(json.loads((folder / "landmarks.json").read_text())).items():
        (folder / f"{version}.json").write_text(json.dumps(plan, indent=2) + "\n")
