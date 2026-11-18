#!/usr/bin/env python3
"""Verify a picture-locked AAC export with independent cue fingerprints."""
from __future__ import annotations

import argparse
from array import array
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

MATCH_RATE = 8000
PCM_RATE = 48000
TEMPLATE_WINDOW_S = 0.08


def run(*command: str | Path) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, check=True)


def probe(path: Path, *args: str) -> dict:
    return json.loads(run("ffprobe", "-v", "error", *args, "-of", "json", path).stdout)


def decode(path: Path, rate: int, channels: int, *, matcher: bool = False) -> array:
    filters = f"aresample={rate}:async=1000:first_pts=0"
    if matcher:
        filters = (
            "aformat=channel_layouts=stereo,pan=mono|c0=0.5*c0+0.5*c1,"
            f"{filters},highpass=f=90"
        )
    output = run("ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", path,
                 "-map", "0:a:0", "-af", filters, "-ac", str(channels),
                 "-c:a", "pcm_f32le", "-f", "f32le", "-").stdout
    samples = array("f")
    samples.frombytes(output)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as media:
        for block in iter(lambda: media.read(1 << 20), b""):
            sha.update(block)
    return sha.hexdigest()


def picture_signature(path: Path) -> tuple[dict, list[tuple]]:
    video = probe(
        path, "-select_streams", "v:0", "-show_streams", "-show_packets",
        "-show_data_hash", "sha256", "-show_entries",
        "stream=codec_name,profile,width,height,pix_fmt,time_base,field_order,"
        "sample_aspect_ratio,color_space,color_range,color_transfer,color_primaries,"
        "chroma_location,extradata_hash:stream_side_data=rotation:"
        "packet=pts,dts,duration,data_hash",
    )
    metadata, = video["streams"]
    # Muxers may drop advisory tags such as the encoder name during stream copy.
    metadata.pop("tags", None)
    time_base = Fraction(metadata.pop("time_base"))
    packets = [
        (
            int(packet["pts"]) * time_base, int(packet["dts"]) * time_base,
            int(packet["duration"]) * time_base, packet["data_hash"],
        )
        for packet in video["packets"]
    ]
    return metadata, packets


def db(amplitude: float) -> float | None:
    return round(20 * math.log10(amplitude), 2) if amplitude > 0 else None


def peaks(path: Path) -> tuple[float | None, float | None]:
    output = run("ffmpeg", "-nostdin", "-hide_banner", "-i", path, "-vn",
                 "-af", "ebur128=peak=true", "-f", "null", "-").stderr.decode()
    summary = output.rsplit("Summary:", 1)[-1]
    peak = re.search(r"Peak:\s*(-?\d+(?:\.\d+)?|-inf) dBFS", summary)
    integrated = re.search(r"I:\s*(-?\d+(?:\.\d+)?|-inf) LUFS", summary)
    if peak is None or integrated is None:
        raise ValueError("FFmpeg did not report true peak and integrated loudness")
    return tuple(float(value) if value != "-inf" else None
                 for value in (peak.group(1), integrated.group(1)))


def energy_prefix(samples: array) -> list[float]:
    prefix = [0.0]
    for sample in samples:
        prefix.append(prefix[-1] + sample * sample)
    return prefix


def dot(left: array, right: array) -> float:
    if hasattr(math, "sumprod"):
        return math.sumprod(left, right)
    return sum(a * b for a, b in zip(left, right))


def check_cue(cue: dict, decoded: array, energy: list[float], base: Path) -> dict:
    template = decode(base / cue["template"], MATCH_RATE, 1, matcher=True)
    begin = round(cue.get("template_begin_s", 0) * MATCH_RATE)
    end = begin + round(cue.get("template_duration_s", len(template) / MATCH_RATE) * MATCH_RATE)
    snippet = template[begin:end]
    if len(snippet) < round(0.01 * MATCH_RATE) or begin < 0:
        raise ValueError(f'{cue["id"]}: template slice must be at least 10 ms')
    window = min(len(snippet), round(TEMPLATE_WINDOW_S * MATCH_RATE))
    template_energy = energy_prefix(snippet)
    offset = max(
        range(0, len(snippet) - window + 1),
        key=lambda start: template_energy[start + window] - template_energy[start],
    )
    reference = snippet[offset:offset + window]
    ref_energy = template_energy[offset + window] - template_energy[offset]
    if ref_energy < 1e-10:
        raise ValueError(f'{cue["id"]}: silent cue template')

    expected = round(cue["start_s"] * MATCH_RATE)
    search = round(cue.get("search_ms", 500) / 1000 * MATCH_RATE)
    tolerance = round(cue.get("tolerance_ms", 25) / 1000 * MATCH_RATE)
    impact_offset = cue["impact_offset_s"]
    min_correlation = cue.get("min_correlation", 0.65)
    min_gain = 10 ** (cue.get("min_gain_db", -20) / 20)
    if (expected < 0 or not 0 <= tolerance <= search or not 0 <= min_correlation <= 1
            or not 0 <= impact_offset < len(snippet) / MATCH_RATE):
        raise ValueError(f'{cue["id"]}: invalid cue timing, window or threshold')

    best_near, best_elsewhere, strongest = None, None, None
    for start in range(max(0, expected - search), min(len(decoded) - offset - window,
                                                       expected + search) + 1):
        index = start + offset
        audio_energy = energy[index + window] - energy[index]
        if audio_energy < ref_energy * min_gain ** 2:
            continue
        projection = dot(reference, decoded[index:index + window])
        correlation = projection / math.sqrt(ref_energy * audio_energy)
        gain = projection / ref_energy
        match = (correlation, gain, -abs(start - expected), start)
        if strongest is None or match > strongest:
            strongest = match
        if gain < min_gain or correlation < min_correlation:
            continue
        if abs(start - expected) <= tolerance:
            if best_near is None or match > best_near:
                best_near = match
        elif best_elsewhere is None or match > best_elsewhere:
            best_elsewhere = match

    result = {
        "id": cue["id"],
        "expected_sample_start_s": cue["start_s"],
        "expected_impact_landmark_s": round(cue["start_s"] + impact_offset, 6),
        "picture_anchor_s": cue.get("picture_anchor_s"),
        "tolerance_ms": cue.get("tolerance_ms", 25),
        "search_ms": cue.get("search_ms", 500),
    }
    match = best_near or best_elsewhere
    if match is None:
        return {**result, "status": "missing",
                "best_correlation": round(strongest[0], 3) if strongest else None}
    correlation, gain, _, start = match
    delta_ms = 1000 * (start - expected) / MATCH_RATE
    return {
        **result,
        "status": "pass" if best_near else ("late" if delta_ms > 0 else "early"),
        "measured_sample_start_s": round(start / MATCH_RATE, 6),
        "estimated_impact_landmark_s": round(start / MATCH_RATE + impact_offset, 6),
        "delta_ms": round(delta_ms, 3),
        "correlation": round(correlation, 3),
        "matched_gain_db": db(gain),
    }


def check_export(export: Path, picture: Path, manifest: Path) -> dict:
    config = json.loads(manifest.read_text())
    streams = probe(export, "-show_streams")["streams"]
    video = [stream for stream in streams if stream["codec_type"] == "video"]
    audio = [stream for stream in streams if stream["codec_type"] == "audio"]
    if len(video) != 1 or len(audio) != 1:
        return {"passed": False, "errors": ["expected one video and one audio stream"]}

    video, = video
    audio, = audio
    errors = []
    if video["codec_name"] != "h264" or audio["codec_name"] != "aac":
        errors.append("expected H.264 video and AAC audio")

    channels = config.get("channels", 2)
    if audio["channels"] != channels or int(audio["sample_rate"]) != PCM_RATE:
        errors.append(f"expected {channels}-channel {PCM_RATE} Hz audio")

    picture_hash = digest(picture)
    if config.get("picture_sha256", picture_hash) != picture_hash:
        errors.append("picture master SHA-256 differs from cue manifest")
    picture_matches = picture_signature(picture) == picture_signature(export)
    if not picture_matches:
        errors.append("video packet bytes, metadata or timestamps differ from picture master")

    video_duration = float(video["duration"])
    audio_duration = float(audio["duration"])
    if abs(audio_duration - video_duration) > config.get("max_duration_delta_ms", 35) / 1000:
        errors.append("audio and video stream durations differ beyond tolerance")
    if abs(float(video["start_time"])) > 0.001 or abs(float(audio["start_time"])) > 0.001:
        errors.append("audio/video edit does not start at timeline zero")

    pcm = decode(export, PCM_RATE, channels)
    decoded_duration = len(pcm) / (PCM_RATE * channels)
    if abs(decoded_duration - video_duration) > config.get("max_duration_delta_ms", 35) / 1000:
        errors.append("decoded audio and video durations differ beyond tolerance")

    true_peak, integrated = peaks(export)
    max_true_peak = config.get("max_true_peak_dbtp", -1)
    if true_peak is not None and true_peak > max_true_peak:
        errors.append(f"true peak exceeds {max_true_peak} dBTP")

    windows = []
    for window in config.get("silences", []):
        start = round(window["start_s"] * PCM_RATE) * channels
        end = round(window["end_s"] * PCM_RATE) * channels
        if not 0 <= start < end:
            raise ValueError(f'{window["id"]}: invalid silence window')
        if end > len(pcm):
            windows.append({**window, "measured_peak_dbfs": None, "passed": False})
            errors.append(f'{window["id"]}: protected silence is truncated')
            continue
        measured = max(map(abs, pcm[start:end]))
        passed = measured <= 10 ** (window["max_peak_dbfs"] / 20)
        windows.append({**window, "measured_peak_dbfs": db(measured), "passed": passed})
        if not passed:
            errors.append(f'{window["id"]}: protected silence exceeds peak ceiling')

    # Fingerprint the decoded waveform. Its alignment estimates a template landmark,
    # while the impact offset and its relationship to picture come from editorial review.
    matcher_audio = decode(export, MATCH_RATE, 1, matcher=True)
    matcher_energy = energy_prefix(matcher_audio)
    cues = [check_cue(cue, matcher_audio, matcher_energy, manifest.parent) for cue in config["cues"]]
    errors.extend(f'{cue["id"]}: {cue["status"]}' for cue in cues if cue["status"] != "pass")

    return {
        "passed": not errors,
        "export_sha256": digest(export),
        "picture_sha256": picture_hash,
        "video_packets_and_timestamps_match": picture_matches,
        "video_duration_s": video_duration,
        "audio_duration_s": audio_duration,
        "decoded_audio_duration_s": decoded_duration,
        "integrated_lufs": integrated,
        "true_peak_dbtp": true_peak,
        "max_true_peak_dbtp": max_true_peak,
        "cues": cues,
        "silences": windows,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="muxed H.264/AAC MP4 to decode")
    parser.add_argument("--picture", required=True, type=Path, help="picture-locked MP4 source")
    parser.add_argument("--manifest", required=True, type=Path, help="QC cues and silence windows")
    args = parser.parse_args()
    try:
        report = check_export(args.export, args.picture, args.manifest)
    except subprocess.CalledProcessError as error:
        print(error.stderr.decode(errors="replace"), file=sys.stderr)
        return 2
    except (KeyError, TypeError, ValueError, OSError) as error:
        print(f"Invalid export or QC manifest: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
