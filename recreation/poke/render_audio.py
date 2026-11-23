#!/usr/bin/env python3
"""Retime the existing independently designed Poke UI mix and verify its AAC attack."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from prepare import ROOT, RATE, SELECTION_FRAME


AUDIO = ROOT / "resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation"
MIX = AUDIO / "ui-mixes/04-poke"
SCHEDULE_SHA = "b2b44c5d35fff0f441b1216c2e388599cbd42f0804c9ae743f8fffcf5b87ad00"
MUSIC_SHA = "d7324ced6a9d6c01d36943fcacbad48628a5ae1657e916a0c498ff9c568d1bf1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path, help="New directory for the sound stems and evidence")
    parser.add_argument("--picture", type=Path, required=True, help="Corrected silent GSAP export")
    args = parser.parse_args()

    sys.path.insert(0, str(AUDIO / "scripts"))
    import numpy as np
    from render_ui import build_ui, library, listening, render_event, target_sample
    from render_mix import decode, encode, sha256, validate_export

    schedule, music_path = MIX / "schedule.snapshot.json", MIX / "music.flac"
    if sha256(schedule) != SCHEDULE_SHA or sha256(music_path) != MUSIC_SHA:
        raise ValueError("The pinned independent score or cue schedule changed")
    for asset in library.manifest()["assets"]:
        if sha256(library.ROOT / asset["prepared_file"]) != asset["prepared_sha256"]:
            raise ValueError(f"Prepared asset hash mismatch: {asset['id']}")

    baseline = json.loads(schedule.read_text())
    revised = deepcopy(baseline)
    ordinal, = [i for i, e in enumerate(revised["events"]) if e["group"] == "restaurant-selection"]
    event = revised["events"][ordinal]
    old_frame = event["frame"]
    if old_frame != 645:
        raise ValueError(f"Expected the historical cue on frame 645, got {old_frame}")
    event.update(frame=SELECTION_FRAME, time=float(SELECTION_FRAME / RATE),
                 preview_frame=SELECTION_FRAME, discrepancy_frames=0,
                 description="Zareen’s blue selected circle and checkmark appear.",
                 action_inference="The selected state is visible. No pointer is shown.",
                 sample_offset_48000=target_sample(SELECTION_FRAME, revised),
                 event_id=f"04-poke:tap:{SELECTION_FRAME}:{ordinal}")
    event.pop("actual_encoded_preview_verified", None)

    old_ui, old_events = build_ui(baseline)
    ui, events = build_ui(revised)
    old, new = old_events[ordinal], events[ordinal]
    if old_events[:ordinal] + old_events[ordinal + 1:] != events[:ordinal] + events[ordinal + 1:]:
        raise ValueError("Another cue changed")
    support = np.ones(len(ui), dtype=bool)
    for record in (old, new):
        start = record["written_start_sample"]
        support[start:start + record["written_samples"]] = False
    if not np.array_equal(old_ui[support], ui[support]):
        raise ValueError("UI samples changed outside the old and new cue spans")
    clip, _ = render_event(event, revised, ordinal)
    old_clip, _ = render_event(baseline["events"][ordinal], baseline, ordinal)
    if not np.array_equal(clip, old_clip):
        raise ValueError("The selection sound changed as well as its timing")

    music = decode(music_path).astype(np.float64)
    if music.shape != ui.shape:
        raise ValueError("Independent music and picture lengths differ")
    args.work.mkdir(parents=True)
    encode(args.work / "ui.flac", ui, aac=False)
    encode(args.work / "full_mix.flac", ui + music, aac=False)
    mix = args.work / "full_mix.m4a"
    encoded = listening(mix, ui + music, len(ui), "256k")
    movie = args.work / "poke-corrected.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-n", "-i", str(args.picture), "-i", str(mix),
        "-map", "0:v:0", "-map", "1:a:0", "-c", "copy",
        "-movie_timescale", "240000", "-movflags", "+faststart", str(movie),
    ], check=True)
    mux_validation = validate_export(movie, len(ui), None, aac=True)

    # Subtract the known independent music bed from the muxed AAC for cue detection.
    # Codec residuals remain, so look for the complete cue in a local window.
    gain = 10 ** (encoded["codec_gain_db"] / 20)
    completed = (decode(movie)[:len(music)] - music * gain).mean(axis=1)
    attack = new["clip_alignment_offset_samples"]
    template = clip.mean(axis=1)

    def match(center):
        radius = 800
        block = completed[center - radius:center + radius + len(template)].astype(np.float64)
        energy = np.convolve(block ** 2, np.ones(len(template)), mode="valid")
        similarities = np.correlate(block, template, mode="valid") / np.maximum(
            np.sqrt(energy) * np.linalg.norm(template), 1e-12
        )
        index = int(similarities.argmax())
        return center - radius + index + attack, float(similarities[index])

    actual, similarity = match(new["event_sample"] - attack)
    _, old_similarity = match(old["event_sample"] - attack)
    if abs(actual - new["event_sample"]) > 24 or similarity < 0.75 or old_similarity >= 0.75:
        raise ValueError(f"Encoded selection cue mismatched: {actual}, {similarity}, old slot {old_similarity}")
    report = {
        "reference_audio_used": False,
        "music_sha256": MUSIC_SHA,
        "previous_schedule_sha256": SCHEDULE_SHA,
        "other_cue_receipts_identical": True,
        "ui_samples_outside_both_cue_spans_identical": int(support.sum()),
        "before": old,
        "after": new,
        "encoded_attack_sample": actual,
        "encoded_attack_error_samples": actual - new["event_sample"],
        "matched_correlation": similarity,
        "old_slot_correlation": old_similarity,
        "aac": encoded,
        "mux_validation": mux_validation,
    }
    (args.work / "schedule.json").write_text(json.dumps(revised, indent=2) + "\n")
    (args.work / "audio-report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"frame": SELECTION_FRAME, "encoded_attack_sample": actual, "error_samples": report["encoded_attack_error_samples"]}))


if __name__ == "__main__":
    main()
