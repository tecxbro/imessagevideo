#!/usr/bin/env python3
"""Build a picture-locked, source-audio-free launch mix and review manifest."""

import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np
from soundscape import band, field_bed, graphite


RATE = 48_000
LANES = ("environment", "hands", "motion", "payoff")


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def probe(picture):
    result = run(
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=avg_frame_rate,nb_frames,start_time,duration", "-of", "json",
        str(picture), capture_output=True,
    )
    stream, = json.loads(result.stdout)["streams"]
    return Fraction(stream["avg_frame_rate"]), int(stream["nb_frames"]), stream


def decode(path):
    result = run(
        "ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "2",
        "-ar", str(RATE), "-f", "f32le", "-", capture_output=True,
    )
    return np.frombuffer(result.stdout, dtype="<f4").reshape(-1, 2).copy()


def foley(design):
    """Authored, deterministic foley. The landmark is the intended gesture peak."""
    duration_ms = design["duration_ms"]
    impact_ms = design["landmark_ms"]
    t = np.arange(round(duration_ms * RATE / 1000)) / RATE
    impact, duration = impact_ms / 1000, duration_ms / 1000
    rng = np.random.default_rng(design["seed"])
    rising = np.minimum(t / impact, 1)
    falling = np.maximum((duration - t) / (duration - impact), 0)
    envelope = np.sin(rising * np.pi / 2) ** 2 * falling ** design.get("release_power", 2)
    low, high = design["band_hz"]
    noise = band(rng.standard_normal(len(t)), low, high, RATE)
    side = band(rng.standard_normal(len(t)), low, high, RATE)
    texture = np.cos(2 * np.pi * 3.5 * t) * 0.10 + 0.90
    center = noise * texture
    if "body_hz" in design:
        frequency = design["body_hz"] * np.exp(-t * design.get("pitch_fall", 1.8))
        phase = 2 * np.pi * np.cumsum(frequency) / RATE
        body = np.sin(phase) * 0.6 + np.sin(phase * 1.68) * 0.14
        center = 0.62 * center + body * design.get("body_level", 0.5)
    return np.column_stack((center + 0.18 * side, center - 0.18 * side)) * envelope[:, None]


def effect(asset, manifest_dir):
    if "file" in asset:
        path = manifest_dir / asset["file"]
        if sha256(path) != asset["sha256"]:
            raise ValueError(f"Asset hash changed: {path}")
        audio = decode(path)
        if "trim_ms" in asset:
            audio = audio[: round(asset["trim_ms"] * RATE / 1000)]
        fade = min(144, len(audio) // 2)
        audio[-fade:] *= np.linspace(1, 0, fade)[:, None]
        # Center the click's short attack by default. Movement uses its design landmark.
        attack = int(np.argmax(np.max(np.abs(audio[: RATE // 20]), axis=1)))
        offset = attack
    else:
        audio = graphite(asset, RATE) if asset.get("kind") == "graphite" else foley(asset)
        offset = round(asset["landmark_ms"] * RATE / 1000)
    if not np.isfinite(audio).all() or np.max(np.abs(audio)) == 0:
        raise ValueError("Asset is empty, silent, or non-finite")
    return audio / np.max(np.abs(audio)), offset


def write_audio(path, audio):
    run(
        "ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(RATE), "-ac", "2",
        "-i", "-", "-c:a", "flac", "-sample_fmt", "s32", "-bits_per_raw_sample", "24",
        str(path), input=audio.astype("<f4").tobytes(),
    )


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def build(picture, plan_path, out, faults=False):
    config = json.loads(plan_path.read_text())
    picture_hash = sha256(picture)
    if picture_hash != config["picture_sha256"]:
        raise ValueError(f"Picture hash changed: {picture_hash}")
    fps, frames, stream = probe(picture)
    if (str(fps), frames) != (config["fps"], config["frames"]):
        raise ValueError(f"Unexpected picture clock: {stream}")
    out.mkdir(parents=True, exist_ok=True)
    count = round(Fraction(frames, 1) / fps * RATE)
    stems = {lane: np.zeros((count, 2), dtype=np.float64) for lane in LANES}
    output_gain_db = config.get("output_gain_db", 0)
    if "field_bed" in config:
        environment = field_bed(count, RATE, float(fps), config["field_bed"])
        stems["environment"] += environment * 10 ** (output_gain_db / 20)
    rendered = []
    controls = []
    source = config.get("asset_manifest")
    assets = config["assets"] if source is None else json.loads((plan_path.parent / source).read_text())
    asset_base = plan_path.parent if source is None else (plan_path.parent / source).parent

    for cue in config["cues"]:
        audio, landmark = effect(assets[cue["asset"]], asset_base)
        audio *= 10 ** ((cue["peak_dbfs"] + output_gain_db) / 20)
        frame = cue["anchor_frame"]
        if not 0 <= frame < frames:
            raise ValueError(f"Cue anchor outside picture: {cue['id']}")
        impact = round(Fraction(frame + cue.get("impact_after_frames", 0), 1) / fps * RATE)
        impact += round(cue.get("impact_delta_ms", 0) * RATE / 1000)
        start = impact - landmark
        if start < 0 or start + len(audio) > count:
            raise ValueError(f"Cue outside picture: {cue['id']}")
        actual = start
        active = True
        if faults:
            fault = config.get("faults", {}).get(cue["id"], {})
            actual += round(Fraction(fault.get("delay_frames", 0), 1) / fps * RATE)
            active = not fault.get("remove", False)
        if active:
            if actual < 0 or actual + len(audio) > count:
                raise ValueError(f"Delayed cue outside picture: {cue['id']}")
            stems[cue["lane"]][actual:actual + len(audio)] += audio
        result = {
            **cue, "anchor_s": float(Fraction(frame, 1) / fps),
            "sample_start": start, "sample_start_s": start / RATE,
            "design_impact_s": impact / RATE, "landmark_offset_ms": landmark * 1000 / RATE,
            "largest_sample_s": (start + int(np.argmax(np.max(np.abs(audio), axis=1)))) / RATE,
            "rendered_sample_start": actual if active else None, "samples": len(audio),
        }
        rendered.append(result)
        if cue.get("verify"):
            name = f"{cue['id']}.flac"
            write_audio(out / "templates" / name, audio)
            controls.append({
                "id": cue["id"], "template": f"templates/{name}", "start_s": start / RATE,
                "impact_offset_s": landmark / RATE, "tolerance_ms": 24, "search_ms": 440,
            })

    for lane, audio in stems.items():
        if np.any(audio):
            write_audio(out / f"{lane}.flac", audio)
    mix = sum(stems.values())
    peak = np.max(np.abs(mix))
    if peak > 10 ** (-3 / 20):
        raise ValueError(f"Insufficient PCM headroom: {20 * np.log10(peak):.2f} dBFS")
    write_audio(out / "master.flac", mix)
    run(
        "ffmpeg", "-y", "-v", "error", "-i", str(picture), "-i", str(out / "master.flac"),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-map_metadata", "-1", "-movflags", "+faststart", str(out / "mix.mp4"),
    )
    write_json(out / "timing.json", {
        "picture_sha256": picture_hash, "picture_commit": config["picture_commit"],
        "fps": str(fps), "frames": frames, "pcm_samples_per_channel": count,
        "fault_control": faults, "output_gain_db": output_gain_db, "cues": rendered,
    })
    write_json(out / "qc.json", {
        "picture_sha256": picture_hash, "max_true_peak_dbtp": -1, "cues": controls,
        "silences": config.get("silences", []),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("picture", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path, help="Fresh output directory")
    parser.add_argument("--faults", action="store_true", help="Inject declared review faults")
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output directory is already populated")
    (args.output / "templates").mkdir(parents=True, exist_ok=True)
    build(args.picture, args.plan, args.output, args.faults)


if __name__ == "__main__":
    main()
