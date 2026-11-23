#!/usr/bin/env python3
"""Route a film request, render an editable scene, or verify its export."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINES = ROOT / "scripts" / "engines"
sys.path.insert(0, str(ROOT / "contracts"))
from timeline import resolve  # noqa: E402

RENDERERS = ("pillow", "html", "gsap", "remotion", "motion-canvas")
ROUTES = json.loads((Path(__file__).with_name("routes.json")).read_text(encoding="utf-8"))
CLUES = {
    "sound": r"\b(?:audio|sound|soundtrack|music|mix|mux|sfx|stems?|foley|silence|cue|clicks?)\b",
    "interaction": r"\b(?:interaction|keyboard|composer|tapback|reaction|reply|thread|swipe|gesture|long[ -]press|conversation|interface|ui)\b",
    "motion": (
        r"\b(?:motion|animation|animate|ease|easing|timing|camera|zoom|transition|orbit|pan|slide|settle|takeoff)\b"
        r"|\b(?:move|lift|float|pin) (?:the |this )?(?:heading|title|photos?|pictures?|snapshots?|card)\b"
        r"|\b(?:heading|title|photos?|pictures?|snapshots?)\b.{0,40}\b(?:stays? (?:fixed|pinned)|travels?)\b"
        r"|\bcount(?:er)? (?:climbs?|rolls?|rises?|ticks?)\b"
    ),
    "dataset": r"\b(?:dataset|intake|footage archive|fingerprint|exclusion|scout footage|source archive)\b",
    "recreation": r"\b(?:rebuild|recreat\w*|reconstruct\w*|match (?:the|this)|reference film|reference video)\b",
    "direction": r"\b(?:product brief|launch|brand film|original film|new film|teaser|storyboard|direct|promo)\b",
}
SCOPED_EDIT = re.compile(r"\b(?:add|remove|replace|retime|edit|fix|tweak|move|slow|speed up|shorten|lengthen|tighten|change|try|make(?= .{0,48} (?:softer|quieter|faster|slower|louder)\b))\b")
FULL_FILM = re.compile(r"\b(?:create|make|build|produce|direct|deliver|design|cut|need|want)\b.{0,40}\b(?:film|video|spot|teaser|promo)\b")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def route(request, input_kind, explicit):
    text = request.casefold()
    full_film = FULL_FILM.search(text) and not re.search(r"\b(?:quieter|louder|softer|slower|faster|only)\b", text)
    hits = {name: re.search(pattern, text) for name, pattern in CLUES.items()}
    copy = re.search(r"\b(?:rebuild|recreat\w*|reconstruct\w*|match (?:the|this))\b", text)
    inspiration = re.search(r"\b(?:as inspiration|for inspiration|original film|new film|new product video)\b", text)
    if explicit:
        name, reason = explicit, "explicit route"
    elif hits["dataset"]:
        name, reason = "dataset", "footage intake or archive request"
    elif inspiration and full_film and not copy:
        name, reason = "direction", "asked for an original film using a reference as inspiration"
    elif hits["recreation"] and (input_kind == "reference" or input_kind is None):
        name, reason = ("recreation", "asked to reconstruct a reference") if copy or not SCOPED_EDIT.search(text) else (None, None)
    else:
        name, reason = None, None
    if name is None and not full_film and (SCOPED_EDIT.search(text) or input_kind == "project"):
        edit = SCOPED_EDIT.search(text)
        local_text = text[edit.start():] if edit else text
        choices = ("sound", "motion", "interaction")
        scoped_hits = [(hit.start(), candidate) for candidate in choices if (hit := re.search(CLUES[candidate], local_text))]
        if scoped_hits:
            name, reason = min(scoped_hits)[1], "asked to change one part of a project"
    if name is None:
        if input_kind == "reference":
            name, reason = "recreation", "reference film supplied for a recreation workflow"
        elif input_kind == "brief" or hits["direction"] or full_film:
            name, reason = "direction", "product brief or original film request"
        else:
            matched = [candidate for candidate in ("sound", "motion", "interaction") if hits[candidate]]
            if len(matched) == 1:
                name, reason = matched[0], "single specialist request"
    if name is None:
        raise ValueError("route is ambiguous; supply --input-kind or --route")
    config = ROUTES[name]
    entry = config["specialist"]
    supplied = (ROOT / entry).is_file()
    return {
        "route": name, "reason": reason,
        "workflow": "specialist" if supplied else "base",
        "read": [entry] if supplied else config["base"],
        "contracts": ["contracts/README.md"],
        "deliver": config["deliver"],
    }


def local_video(command, path, arguments, *, decode=False, raw=False):
    prefix = [command, "-v", "error", "-protocol_whitelist", "file,pipe,crypto"]
    if decode:
        prefix += ["-xerror", "-nostdin"]
    input_args = ["-i", str(path.resolve())] if command == "ffmpeg" else []
    trailing = [str(path.resolve())] if command == "ffprobe" else []
    return subprocess.run(prefix + input_args + arguments + trailing, check=True,
                          capture_output=True, text=not raw).stdout


def picture_stream(video):
    channels = json.loads(local_video("ffprobe", video, [
        "-select_streams", "v:0", "-show_streams", "-show_entries",
        "stream=width,height,avg_frame_rate,time_base,codec_name,duration_ts", "-of", "json",
    ]))["streams"]
    if len(channels) != 1:
        raise ValueError("expected a video stream")
    return channels[0]


def audit_video(video, scene=None):
    stream = picture_stream(video)
    frame_data = json.loads(local_video("ffprobe", video, [
        "-select_streams", "v:0", "-show_frames", "-show_entries",
        "frame=best_effort_timestamp", "-of", "json",
    ]))["frames"]
    pts = [int(frame["best_effort_timestamp"]) for frame in frame_data]
    if not pts or any(left >= right for left, right in zip(pts, pts[1:])):
        raise ValueError("decoded picture timestamps must be present and strictly increasing")
    local_video("ffmpeg", video, ["-map", "0:v:0", "-an", "-f", "null", "-"], decode=True)
    timebase = Fraction(stream["time_base"])
    rate = Fraction(stream["avg_frame_rate"])
    if scene is not None:
        clock = resolve(scene)["picture"]
        expected = Fraction(clock["fpsNum"], clock["fpsDen"])
        if (stream["width"], stream["height"], rate, len(pts)) != (
                scene["width"], scene["height"], expected, clock["frameCount"]):
            raise ValueError("decoded width, height, rational rate, or frame count differs from the scene")
        for index, stamp in enumerate(pts):
            if stamp * timebase != Fraction(index) / expected:
                raise ValueError(f"decoded timestamp differs from the picture clock at frame {index}")
        if "duration_ts" not in stream or stream["duration_ts"] * timebase != len(pts) / expected:
            raise ValueError("encoded track duration differs from the picture clock")
    with video.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    return {
        "sha256": sha256, "width": stream["width"], "height": stream["height"],
        "codec": stream["codec_name"], "fps": f"{rate.numerator}/{rate.denominator}",
        "frameCount": len(pts), "firstFrame": 0, "lastFrame": len(pts) - 1,
        "firstFrameTime": str(pts[0] * timebase), "lastFrameTime": str(pts[-1] * timebase),
        "fullDecode": True,
    }


def inspect_video(video, folder, frame_numbers):
    report = audit_video(video)
    last = report["lastFrame"]
    checkpoints = {round(last * index / 11) for index in range(12)}
    for frame in frame_numbers:
        if not 0 <= frame <= last:
            raise ValueError(f"frame {frame} lies outside 0–{last}")
        checkpoints.update(range(max(0, frame - 2), min(last, frame + 2) + 1))
    checkpoints.update(range(max(0, last - 3), last + 1))
    folder.mkdir(parents=True, exist_ok=True)
    frames = sorted(checkpoints)
    columns = min(len(frames), 4)
    rows = math.ceil(len(frames) / columns)
    selected = "+".join(rf"eq(n\,{frame})" for frame in frames)
    graph = f"select={selected},scale=240:-2,tile={columns}x{rows}:padding=4:margin=4"
    output = folder / "contact-sheet.png"
    local_video("ffmpeg", video, [
        "-y", "-map", "0:v:0", "-filter_threads", "1", "-vf", graph,
        "-frames:v", "1", "-threads", "1", "-update", "1", str(output.resolve()),
    ], decode=True)
    report.update(contactSheet=output.name, contactSheetFrames=frames)
    write_json(report, folder / "inspection.json")
    return report


def render(scene_path, output, method):
    scene = read_json(scene_path)
    events = resolve(scene)
    if output.suffix.lower() != ".mp4":
        raise ValueError("output must have an .mp4 extension")
    output.parent.mkdir(parents=True, exist_ok=True)
    if method == "pillow":
        command = [sys.executable, str(ENGINES / "render_pillow.py")]
    elif method == "motion-canvas":
        command = ["node", str(ENGINES / "render_motion_canvas.mjs")]
    else:
        command = ["node", str(ENGINES / "render.mjs"), "--method", method]
    subprocess.run(command + ["--scene", str(scene_path.resolve()), "--out", str(output.resolve())],
                   stdout=sys.stderr, check=True)
    report = audit_video(output, scene)
    write_json(events, output.with_suffix(".events.json"))
    write_json(report, output.with_suffix(".picture.json"))
    return report


def smoke(methods, folder):
    source = ROOT / "contracts" / "example.scene.json"
    event = resolve(read_json(source))["events"][0]
    expected_frame = 12
    if event["frame"] != expected_frame or event["sample"] != 24_000:
        raise ValueError("contract fixture event clock changed")
    results = {}
    for method in methods:
        output = folder / f"{method}.mp4"
        report = render(source, output, method)
        raw = local_video("ffmpeg", output, [
            "-vf", r"select=eq(n\,11)+eq(n\,12)", "-fps_mode", "passthrough",
            "-pix_fmt", "rgb24", "-threads", "1", "-f", "rawvideo", "-",
        ], decode=True, raw=True)
        width, height = report["width"], report["height"]
        stride = width * height * 3
        if len(raw) != stride * 2:
            raise ValueError(f"{method}: expected two decoded marker frames")
        measured = []
        for frame in range(2):
            row = frame * stride + width * 90 * 3
            measured.append([list(raw[row + x * 3:row + x * 3 + 3]) for x in (48, 248)])
        left, right = measured
        for amber, dark in ((left[0], left[1]), (right[1], right[0])):
            if amber[0] < 200 or dark[0] > 60:
                raise ValueError(f"{method}: marker at unexpected frame or position: {measured}")
        results[method] = {
            **report, "event": event["id"], "eventFrame": expected_frame,
            "eventSample": event["sample"], "markerPixelsAtFrames11And12": measured,
        }
    write_json(results, folder / "smoke.json")
    return results


def write_json(value, destination=None):
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if destination:
        stage = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
        try:
            stage.write_text(encoded, encoding="utf-8")
            stage.replace(destination)
        finally:
            stage.unlink(missing_ok=True)
    else:
        print(encoded, end="")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    chooser = actions.add_parser("route", help="select the smallest workflow for a request")
    chooser.add_argument("request")
    chooser.add_argument("--input-kind", choices=["reference", "brief", "project"])
    chooser.add_argument("--route", choices=ROUTES)
    renderer = actions.add_parser("render", help="export and verify a v3 scene")
    renderer.add_argument("scene", type=Path)
    renderer.add_argument("--out", type=Path, required=True)
    renderer.add_argument("--method", choices=RENDERERS, default="pillow")
    verifier = actions.add_parser("verify", help="decode a complete film and check picture timing")
    verifier.add_argument("video", type=Path)
    verifier.add_argument("--scene", type=Path)
    inspector = actions.add_parser("inspect", help="make a contact sheet including the end and event windows")
    inspector.add_argument("video", type=Path)
    inspector.add_argument("--out", type=Path, required=True)
    inspector.add_argument("--frame", type=int, action="append", default=[])
    checker = actions.add_parser("smoke", help="render the shared scene and verify the marker frame")
    checker.add_argument("--out", type=Path, required=True)
    checker.add_argument("--method", choices=(*RENDERERS, "all"), default="pillow")
    args = parser.parse_args()
    try:
        if args.action == "route":
            data = route(args.request, args.input_kind, args.route)
        elif args.action == "render":
            data = render(args.scene, args.out, args.method)
        elif args.action == "verify":
            data = audit_video(args.video, read_json(args.scene) if args.scene else None)
        elif args.action == "inspect":
            data = inspect_video(args.video, args.out, args.frame)
        else:
            data = smoke(RENDERERS if args.method == "all" else [args.method], args.out)
        write_json(data)
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
        parser.exit(1, f"{Path(exc.cmd[0]).name} failed ({exc.returncode})\n{details or ''}")
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
