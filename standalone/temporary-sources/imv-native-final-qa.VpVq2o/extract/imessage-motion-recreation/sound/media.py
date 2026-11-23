"""FFmpeg I/O for the 48 kHz stereo sound project."""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np

RATE = 48_000


def run(*command):
    result = subprocess.run(command, capture_output=True)
    if result.returncode:
        raise ValueError(f"{command[0]} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def probe(path, *arguments):
    return json.loads(run("ffprobe", "-v", "error", *arguments, "-of", "json", path))


def sha256(path):
    with Path(path).open("rb") as media:
        return hashlib.file_digest(media, "sha256").hexdigest()


def sample(seconds):
    """Round to the nearest output sample, with exact half-sample ties upward."""
    return math.floor(Fraction(seconds) * RATE + Fraction(1, 2))


def db(amplitude):
    return round(20 * math.log10(float(amplitude)), 2) if amplitude > 0 else None


def decode(path):
    raw = run("ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", path,
              "-map", "0:a:0", "-ac", "2", "-ar", str(RATE),
              "-c:a", "pcm_f32le", "-f", "f32le", "-")
    audio = np.frombuffer(raw, dtype="<f4").reshape(-1, 2)
    if len(audio) == 0 or not np.all(np.isfinite(audio)):
        raise ValueError(f"{path}: audio must contain finite decoded samples")
    return audio


def picture_track(path):
    streams = probe(path, "-show_streams")["streams"]
    video = [stream for stream in streams if stream["codec_type"] == "video"
             and not stream.get("disposition", {}).get("attached_pic")]
    if len(video) != 1:
        raise ValueError(f"{path}: expected one full-frame picture stream")
    stream = video[0]
    seconds = Fraction(int(stream["duration_ts"])) * Fraction(stream["time_base"])
    start = Fraction(int(stream["start_pts"])) * Fraction(stream["time_base"])
    if start != 0 or seconds <= 0:
        raise ValueError(f"{path}: conform picture to a zero start and a positive duration")
    return stream, seconds


def picture_signature(path):
    """Compare stream-copied picture bytes and the display times they carry."""
    video = probe(
        path, "-select_streams", "V:0", "-show_streams", "-show_packets",
        "-show_data_hash", "sha256", "-show_entries",
        "stream=codec_name,width,height,pix_fmt,time_base,sample_aspect_ratio,"
        "color_range,color_space,color_transfer,color_primaries,extradata_hash:"
        "stream_side_data=rotation:packet=pts,duration,data_hash",
    )
    stream, = video["streams"]
    clock = Fraction(stream["time_base"])
    fields = ("codec_name", "width", "height", "pix_fmt", "sample_aspect_ratio",
              "color_range", "color_space", "color_transfer", "color_primaries",
              "extradata_hash", "side_data_list")
    packets = [(int(packet["pts"]) * clock, int(packet["duration"]) * clock,
                packet["data_hash"]) for packet in video["packets"]]
    return tuple(stream.get(field) for field in fields), packets


def mux(picture, audio, output):
    # The WAV is already exactly the picture duration. Stream copy preserves all video frames.
    run("ffmpeg", "-nostdin", "-v", "error", "-xerror", "-y", "-i", picture,
        "-i", audio, "-map", "0:V:0", "-map", "1:a:0", "-map_metadata", "-1",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", output)


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
