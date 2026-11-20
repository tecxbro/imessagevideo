"""Display-order video, exact presentation clocks, and reusable media fingerprints."""
from contextlib import contextmanager
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np


class MediaError(ValueError):
    pass


def digest(path):
    with Path(path).open("rb") as media:
        return sha256_file(media)


def sha256_file(media):
    checksum = sha256()
    for block in iter(lambda: media.read(1 << 20), b""):
        checksum.update(block)
    return checksum.hexdigest()


def probe(path, *options):
    result = subprocess.run(
        ["ffprobe", "-v", "error", *options, "-of", "json", str(Path(path).resolve())],
        capture_output=True, text=True,
    )
    if result.returncode or result.stderr.strip():
        raise MediaError(f"ffprobe failed for {path}: {result.stderr.strip()}")
    return json.loads(result.stdout)


@lru_cache(maxsize=1)
def alpha_formats():
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_pixel_formats", "-show_entries",
         "pixel_format=name:pixel_format_flags=alpha", "-of", "json"],
        capture_output=True, text=True, check=True,
    )
    return {item["name"] for item in json.loads(result.stdout)["pixel_formats"]
            if item.get("flags", {}).get("alpha")}


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as temporary:
        json.dump(data, temporary, indent=2, allow_nan=False)
        temporary.write("\n")
    Path(temporary.name).replace(path)


@dataclass
class Clock:
    stream: dict
    pts: list[int]
    end_pts: int | None
    end_basis: str

    @property
    def base(self):
        return Fraction(self.stream["time_base"])

    @property
    def rate(self):
        return Fraction(self.stream["r_frame_rate"])

    @property
    def width(self):
        return self.stream["width"]

    @property
    def height(self):
        return self.stream["height"]

    @property
    def orientation(self):
        return next((entry["rotation"] for entry in self.stream.get("side_data_list", [])
                     if "rotation" in entry), 0) % 360

    @property
    def display_matrix(self):
        for entry in self.stream.get("side_data_list", []):
            if "displaymatrix" in entry:
                return tuple(int(value) for row in entry["displaymatrix"].splitlines()
                             for value in row.partition(":")[2].split())
        return (65536, 0, 0, 0, 65536, 0, 0, 0, 1073741824)

    @property
    def has_alpha(self):
        flags = self.stream.get("tags", {})
        return (bool(self.stream.get("alpha_present"))
                or flags.get("alpha_mode", flags.get("ALPHA_MODE")) == "1")

    @property
    def crop(self):
        sides = ("crop_top", "crop_bottom", "crop_left", "crop_right")
        entry = next((entry for entry in self.stream.get("side_data_list", [])
                      if any(side in entry for side in sides)), {})
        return tuple(int(entry.get(side, 0)) for side in sides)

    @property
    def sar(self):
        value = self.stream.get("sample_aspect_ratio", "1:1")
        return Fraction(value.replace(":", "/")) if value not in ("N/A", "0:1") else Fraction(1)

    @property
    def origin(self):
        return self.pts[0] * self.base

    @property
    def times(self):
        return [(pts - self.pts[0]) * self.base for pts in self.pts]

    @property
    def end(self):
        return None if self.end_pts is None else (self.end_pts - self.pts[0]) * self.base

    def summary(self):
        elapsed = self.times
        interval = Fraction(1, 1) / self.rate if self.rate else None
        return {
            "width": self.width, "height": self.height, "sample_aspect_ratio": str(self.sar),
            "rotation_degrees": self.orientation, "display_matrix": self.display_matrix,
            "container_crop_top_bottom_left_right": self.crop,
            "time_base": str(self.base),
            "declared_rate": str(self.rate), "declared_average_rate": self.stream["avg_frame_rate"],
            "start_pts": self.pts[0], "end_pts_exclusive": self.end_pts, "end_basis": self.end_basis,
            "end_seconds": float(self.end) if self.end is not None else None,
            "frames": len(self.pts),
            "cadence": ("single-frame" if len(elapsed) == 1 else
                        "constant" if interval and all(abs(time - n * interval) <= self.base / 2
                                                       for n, time in enumerate(elapsed)) else "variable"),
            "pixel_format": self.stream.get("pix_fmt"), "alpha_present": self.has_alpha,
            "color_range": self.stream.get("color_range"),
            "color_space": self.stream.get("color_space"),
            "color_primaries": self.stream.get("color_primaries"),
            "color_transfer": self.stream.get("color_transfer"),
        }


def video_clock(path):
    data = probe(
        path, "-select_streams", "V:0", "-show_streams", "-show_frames", "-show_entries",
        "stream=index,width,height,sample_aspect_ratio,time_base,r_frame_rate,avg_frame_rate,"
        "start_pts,duration_ts,pix_fmt,color_range,color_space,color_primaries,color_transfer:stream_tags=alpha_mode:"
        "stream_side_data=rotation,displaymatrix,crop_top,crop_bottom,crop_left,crop_right:frame=best_effort_timestamp,duration,pkt_duration,width,height,sample_aspect_ratio,pix_fmt",
    )
    streams, frames = data.get("streams", []), data.get("frames", [])
    if not streams or not frames:
        raise MediaError(f"No decoded picture in {path}")
    stream = streams[0]
    alpha = alpha_formats()
    stream["alpha_present"] = (stream.get("pix_fmt") in alpha
                               or any(frame.get("pix_fmt") in alpha for frame in frames))
    if any((frame.get("width"), frame.get("height")) != (stream["width"], stream["height"])
           for frame in frames):
        raise MediaError(f"Picture dimensions change midstream in {path}; compare each format span separately")
    expected_sar = stream.get("sample_aspect_ratio", "1:1")
    if any(frame.get("sample_aspect_ratio", expected_sar) not in (expected_sar, "0:1", "N/A")
           for frame in frames):
        raise MediaError(f"Sample aspect ratio changes midstream in {path}")
    try:
        pts = [int(frame["best_effort_timestamp"]) for frame in frames]
    except KeyError as error:
        raise MediaError(f"Decoded picture lacks a presentation timestamp in {path}") from error
    if any(after <= before for before, after in zip(pts, pts[1:])):
        raise MediaError(f"Decoded presentation timestamps are not strictly increasing in {path}")
    duration = frames[-1].get("duration") or frames[-1].get("pkt_duration")
    if duration and int(duration) > 0:
        end = pts[-1] + int(duration)
        basis = "last decoded frame duration"
    elif "duration_ts" in stream and "start_pts" in stream:
        end = int(stream["start_pts"]) + int(stream["duration_ts"])
        basis = "stream start + stream duration"
    else:
        end, basis = None, "unavailable"
    if end is not None and end <= pts[-1]:
        raise MediaError(f"Invalid final presentation duration in {path}")
    return Clock(stream, pts, end, basis)


@contextmanager
def video_frames(path, clock):
    """Strict full decode. Native coded geometry, display order, no rate conversion."""
    args = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-xerror",
        "-threads", "2", "-noautorotate", "-apply_cropping", "codec", "-i", str(Path(path).resolve()), "-map", "0:V:0",
        "-an", "-sn", "-dn", "-filter_threads", "2", "-fps_mode", "passthrough",
        "-enc_time_base", str(clock.base),
        "-c:v", "rawvideo", "-threads:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
    ]
    with tempfile.TemporaryFile() as errors, subprocess.Popen(args, stdout=subprocess.PIPE, stderr=errors) as proc:
        size = clock.width * clock.height * 3

        def read():
            count = 0
            while buffer := proc.stdout.read(size):
                if len(buffer) != size:
                    raise MediaError(f"{path} returned a partial RGB frame at index {count}")
                count += 1
                yield np.frombuffer(buffer, dtype=np.uint8).reshape(clock.height, clock.width, 3)
            status = proc.wait()
            errors.seek(0)
            stderr = errors.read().decode(errors="replace").strip()
            if status or stderr:
                raise MediaError(f"FFmpeg failed decoding {path} at frame {count}: {stderr}")
            if count != len(clock.pts):
                raise MediaError(f"{path} decoded {count} RGB frames, but ffprobe found {len(clock.pts)} timestamps")

        try:
            yield read()
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()


def audio_streams(path):
    return probe(
        path, "-select_streams", "a", "-show_streams", "-show_entries",
        "stream=index,codec_name,sample_rate,channels,channel_layout,time_base,start_pts,duration_ts",
    ).get("streams", [])


def audio_samples(path, stream, rate):
    start = probe(path, "-select_streams", str(stream["index"]), "-read_intervals", "%+#12",
                  "-show_frames", "-show_entries", "frame=best_effort_timestamp").get("frames", [])
    start_pts = next((frame["best_effort_timestamp"] for frame in start
                      if "best_effort_timestamp" in frame), stream.get("start_pts"))
    if start_pts is None:
        raise MediaError(f"Audio stream {stream['index']} has no measurable start timestamp")
    first = int(start_pts) * Fraction(stream["time_base"])
    cmd = [
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-copyts", "-i", str(Path(path).resolve()),
        "-map", f"0:{stream['index']}", "-vn", "-sn", "-dn",
        "-af", f"asetpts=PTS-STARTPTS,aresample={rate}:async=1:first_pts=0",
        "-c:a", "pcm_f32le", "-f", "f32le", "pipe:1",
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode or result.stderr:
        raise MediaError(f"FFmpeg audio decode {path}: {result.stderr.decode(errors='replace').strip()}")
    samples = np.frombuffer(result.stdout, dtype="<f4").reshape(-1, stream["channels"])
    if not samples.size or not np.isfinite(samples).all():
        raise MediaError(f"Missing or invalid decoded audio in stream {stream['index']} of {path}")
    return first, samples
