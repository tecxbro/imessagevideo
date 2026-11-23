"""Show an iOS capture's measured motion beside an editable scene, using source geometry only."""

import argparse
from dataclasses import dataclass
from hashlib import file_digest
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont

from .compare import decode, probe, select_frames
from .components import font_path


@dataclass(frozen=True)
class Capture:
    file: str
    sha256: str
    frame: int
    after: int
    title: str
    method: str


CAPTURES = {
    "send": Capture(
        "send-60fps.mp4", "23a9680f70a436a119b786334aeb88c70b59c083703ef273eb0cdad2be98cf8b",
        73, 80, "Sending a message",
        "At y >= 668, retain pixels with source G-R > 20, G-B > 17, and at least one RGB "
        "channel changing by > 20 from frame 72. Report the top and width of that changed "
        "green region, including the tail and any visible tinted composer shape.",
    ),
    "context": Capture(
        "longpress-60fps.mp4", "8e8f3cf3194c5afbfd796056be5d37eb9e50b366f9931d02f092160b3d76f2ec",
        82, 38, "Opening a message menu",
        "Measure the mean RGB channel value in logical-pixel rectangle x=25 to 64, "
        "y=440 to 507, inclusive, on the surrounding conversation backdrop. "
        "The visible milestones are labelled from a consecutive-frame strip.",
    ),
}
MILESTONES = (
    (82, "Target bubble begins to lift"),
    (83, "Backdrop begins to dim"),
    (90, "Context actions are visible"),
    (102, "Reaction marks are visible"),
    (117, "Target and both controls remain visible"),
)
FPS = 60
BEFORE = 12
DISPLAY = (402, 874)
PANEL = (334, 726)
SIZE = (864, 846)
PAPER = "#f7f5ef"
INK = "#222e31"
MUTED = "#445b61"
ACCENT = "#1b737a"
GRID = "#d5deda"


def source_samples(kind, capture, source, indices, directory):
    first, last = capture.frame - 1, max(indices)
    decode(source, first, last, DISPLAY, directory)
    samples = []
    rest = None
    if kind == "send":
        with Image.open(directory / f"{first:06d}.png") as before:
            rest = before.convert("RGB").crop((0, 668, DISPLAY[0], DISPLAY[1]))

    for frame in range(capture.frame, last + 1):
        with Image.open(directory / f"{frame:06d}.png") as image:
            if kind == "send":
                crop = image.convert("RGB").crop((0, 668, DISPLAY[0], DISPLAY[1]))
                metric = send_geometry(crop, rest)
            else:
                channels = image.convert("RGB").crop((25, 440, 65, 508)).tobytes()
                metric = {"backdropMean": round(sum(channels) / len(channels), 2)}
        pts = source["times"][frame]
        samples.append({
            "frame": frame, "pts": str(pts),
            "millisecondsFromOnset": round(1000 * float(pts - source["times"][capture.frame]), 3),
            **metric,
        })
    return samples


def send_geometry(image, rest):
    width, height = image.size
    current_channels = iter(image.tobytes())
    rest_channels = iter(rest.tobytes())
    current_pixels = zip(current_channels, current_channels, current_channels)
    rest_pixels = zip(rest_channels, rest_channels, rest_channels)
    changed = (
        index for index, ((r, g, b), (r0, g0, b0)) in enumerate(zip(current_pixels, rest_pixels))
        if g - r > 20 and g - b > 17 and max(abs(r-r0), abs(g-g0), abs(b-b0)) > 20
    )
    left, right, top = width, 0, height
    for index in changed:
        y, x = divmod(index, width)
        left, right, top = min(x, left), max(x, right), min(y, top)
    if top == height:
        raise ValueError("Expected visible outgoing color in the pinned send capture")
    return {"opticalTopPt": top + 668, "widthPt": right - left + 1}


class Trace:
    def __init__(self, kind, capture, samples, render_directory):
        self.kind = kind
        self.capture = capture
        self.samples = samples
        self.render_directory = render_directory
        self.fonts = {
            name: ImageFont.truetype(str(font_path(weight)), size)
            for name, weight, size in [("title", 700, 27), ("heading", 700, 17), ("body", 400, 15), ("tick", 400, 12)]
        }

    def label(self, draw, x, y, value, style="body", fill=INK, **kwargs):
        draw.text((x, y), value, font=self.fonts[style], fill=fill, **kwargs)

    def plot(self, draw, offset, sample, field, title, origin, limits, ticks, time_ticks, invert=False):
        left, right = 59, 470
        upper, lower = origin + 28, origin + 171

        def x_coord(ms):
            return left + (ms + 200) * (right - left) / (self.capture.after * 1000 / FPS + 212)

        def y_coord(value):
            fraction = (value - limits[0]) / (limits[1] - limits[0])
            return upper + (fraction if invert else 1 - fraction) * (lower - upper)

        self.label(draw, 24, origin, title, "heading")
        for value in ticks:
            y = y_coord(value)
            draw.line((left, y, right, y), fill=GRID)
            self.label(draw, left - 8, y, str(value), "tick", MUTED, anchor="rm")
        for ms in time_ticks:
            x = x_coord(ms)
            draw.line((x, upper, x, lower), fill=GRID)
            self.label(draw, x, lower + 6, str(ms), "tick", MUTED, anchor="mt")
        draw.line([(x_coord(item["millisecondsFromOnset"]), y_coord(item[field]))
                   for item in self.samples], width=2, fill=ACCENT)
        x = x_coord(offset * 1000 / FPS)
        draw.line((x, upper, x, lower), width=2, fill="#a17554")
        if sample:
            y = y_coord(sample[field])
            draw.ellipse((x-4, y-4, x+4, y+4), fill=ACCENT)

    def frame(self, offset, source_frame, render_frame):
        image = Image.new("RGB", SIZE, PAPER)
        draw = ImageDraw.Draw(image)
        self.label(draw, 24, 19, self.capture.title, "title")
        self.label(draw, 24, 58, f"{offset * 1000 / FPS:+.0f} ms from the action", fill=MUTED)
        self.label(draw, 24, 117, "iOS 26.0 simulator · SMS capture", "heading")
        self.label(draw, 24, 146, "iPhone 17 Pro · 402 × 874 pt", fill=MUTED)
        self.label(draw, 24, 170, f"Source frame {source_frame} · geometric trace", fill=MUTED)
        self.label(draw, 506, 55, f"Editable scene · frame {render_frame}", "heading")
        with Image.open(self.render_directory / f"{render_frame:06d}.png") as rendered:
            image.paste(rendered, (506, 90))
        draw.rectangle((505, 89, 840, 816), outline="#cbbfbe")
        sample = self.samples[source_frame - self.capture.frame] if source_frame >= self.capture.frame else None
        if self.kind == "send":
            time_ticks = (0, 330, 690, 1017, 1333)
            self.plot(draw, offset, sample, "opticalTopPt", "Top edge from screen top (pt)",
                      220, (660, 825), (660, 710, 760, 810), time_ticks, invert=True)
            self.plot(draw, offset, sample, "widthPt", "Visible span (pt)",
                      446, (0, 320), (0, 100, 200, 300), time_ticks)
            self.label(draw, 24, 647, "Milliseconds from source onset", "tick", MUTED)
            self.label(draw, 24, 700, "The send shape enters at the composer,")
            self.label(draw, 24, 723, "contracts, rises, overshoots and settles.")
            self.label(draw, 24, 755, "The receipt handoff begins after one second.")
        else:
            self.plot(draw, offset, sample, "backdropMean", "Mean backdrop channel value",
                      220, (180, 255), (190, 210, 230, 250), (0, 150, 300, 450, 600))
            self.label(draw, 24, 419, "Milliseconds from source onset", "tick", MUTED)
            self.label(draw, 24, 471, "Events in the capture", "heading")
            for index, (frame, label) in enumerate(MILESTONES):
                active = source_frame >= frame
                y = 510 + index * 35
                self.label(draw, 24, y, f"f{frame}", "tick", ACCENT if active else MUTED)
                self.label(draw, 69, y - 2, label, fill=INK if active else MUTED)
        return image


def encode(out, images):
    temporary = out.with_name(f".{out.stem}.pending.mp4")
    try:
        with subprocess.Popen([
            "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-video_size",
            f"{SIZE[0]}x{SIZE[1]}", "-framerate", str(FPS), "-i", "pipe:", "-an", "-c:v", "libx264",
            "-threads", "2", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(temporary),
        ], stdin=subprocess.PIPE) as encoder:
            for image in images:
                encoder.stdin.write(image.tobytes())
            encoder.stdin.close()
            if encoder.wait():
                raise ValueError("Trace encode failed")
        temporary.replace(out)
    finally:
        temporary.unlink(missing_ok=True)


def trace(args):
    capture = CAPTURES[args.kind]
    source = probe(args.native_dir / capture.file)
    if source["sha256"] != capture.sha256:
        raise ValueError(f"{capture.file} differs from the pinned source capture")
    render = probe(args.render)
    offsets = range(-BEFORE, capture.after + 1)
    source_frames = select_frames(source, capture.frame, offsets, FPS)
    render_frames = select_frames(render, args.render_frame, offsets, FPS)
    conversation = json.loads(args.conversation.read_text(encoding="utf8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    video = args.out_dir / f"{args.kind}-motion-trace.mp4"
    with TemporaryDirectory(prefix="messages-trace-") as scratch:
        directory = Path(scratch)
        samples = source_samples(args.kind, capture, source, source_frames, directory / "source")
        decode(render, min(render_frames), max(render_frames), PANEL, directory / "render")
        drawing = Trace(args.kind, capture, samples, directory / "render")
        encode(video, (drawing.frame(offset, source_index, render_index) for offset, source_index, render_index
                       in zip(offsets, source_frames, render_frames)))

    with video.open("rb") as file:
        video_sha = file_digest(file, "sha256").hexdigest()
    metadata = {
        "reference": {
            "file": capture.file, "sha256": source["sha256"], "anchorFrame": capture.frame,
            "device": "iPhone 17 Pro simulator", "os": "iOS 26.0 (23A343)", "service": "SMS",
            "logicalViewport": list(DISPLAY), "comparisonPixelScale": 1,
        },
        "method": "Decode without interpolating frames, scale each frame to 402 by 874, and read RGB. " + capture.method,
        "render": {
            "file": render["path"].name, "sha256": render["sha256"], "anchorFrame": args.render_frame,
            "conversation": conversation,
        },
        "comparison": {
            "file": video.name, "sha256": video_sha, "frames": len(offsets), "fps": FPS, "anchorFrame": BEFORE,
        },
        "samples": samples,
    }
    if args.kind == "context":
        metadata["milestones"] = [{"sourceFrame": frame, "label": label} for frame, label in MILESTONES]
    video.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf8")
    print(f"{video} ({len(offsets)} frames at {FPS} fps, sha256 {video_sha})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=CAPTURES)
    parser.add_argument("--native-dir", type=Path, required=True)
    parser.add_argument("--render", type=Path, required=True)
    parser.add_argument("--render-frame", type=int, required=True)
    parser.add_argument("--conversation", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    try:
        trace(parser.parse_args())
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
