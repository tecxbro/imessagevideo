#!/usr/bin/env python3
"""Render The Moon Cue and its frame-addressed sound handoff."""
from __future__ import annotations

import argparse
from functools import lru_cache
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from conversation import Conversation, SKILL_ROOT
from movement import move_to_clue, smooth, unit
import stage as art


HERE = Path(__file__).resolve().parent
EDIT = json.loads((HERE / "edit.json").read_text())
WIDTH, HEIGHT = EDIT["width"], EDIT["height"]
FPS = EDIT["fps"]
CUT = EDIT["cut"]


@lru_cache
def font(size, family):
    font_file = subprocess.check_output(["fc-match", "-f", "%{file}", family], text=True)
    return ImageFont.truetype(font_file, size)


def camera(image, scale, x=480, y=270):
    """Move the camera around image point (x, y) with subpixel sampling."""
    inverse = 1 / scale
    return image.transform(
        (WIDTH, HEIGHT), Image.Transform.AFFINE,
        (inverse, 0, x * (1 - inverse), 0, inverse, y * (1 - inverse)),
        resample=Image.Resampling.BICUBIC,
    )


def composite(dst, src, x, y, angle):
    size = src.size
    src = src.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    x -= (src.width - size[0]) / 2
    y -= (src.height - size[1]) / 2
    dst.alpha_composite(src, (round(x), round(y)))


@lru_cache(maxsize=14)
def phone_background(focus):
    plate = art.prop_table(0, 0).filter(ImageFilter.GaussianBlur(10 - 7 * focus)).convert("RGBA")
    return Image.blend(plate, Image.new("RGBA", plate.size, "#170e1a"), .55 - .32 * focus)


def phone_shot(frame, conversation):
    settle = smooth(unit(frame, CUT["phone"], 12))
    turn, focus, _ = move_to_clue(frame, CUT["search"])
    x = 232 + 23 * (1 - settle) - 112 * turn
    y = 11 + 14 * (1 - settle) + 16 * turn
    angle = -2.5 + 2.5 * settle + 6 * turn
    background = phone_background(round(focus, 3)).copy()
    panel = conversation.panel(frame)
    shadow = Image.new("RGBA", panel.size)
    shadow.putalpha(panel.getchannel("A").point(lambda opacity: opacity * .68))
    composite(background, shadow.filter(ImageFilter.GaussianBlur(12)), x + 12, y + 9, angle)
    composite(background, panel.filter(ImageFilter.GaussianBlur(1.9 * turn)), x, y, angle)
    return background.convert("RGB")


def amber_title(image, opacity):
    veil = Image.new("RGB", image.size, "#120e17")
    image = Image.blend(image, veil, opacity * .91)
    lettering = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(lettering)
    amber = (255, 226, 178, round(opacity * 255))
    cream = (255, 239, 216, round(opacity * 255))
    draw.text((480, 239), EDIT["brand"], font=font(76, "DejaVu Serif"), fill=amber, anchor="mm")
    draw.text((480, 326), EDIT["endline"], font=font(29, "DejaVu Sans"), fill=cream, anchor="mm")
    return Image.alpha_composite(image.convert("RGBA"), lettering).convert("RGB")


def render_frame(frame, conversation):
    if frame < CUT["phone"]:
        rabbit = smooth(unit(frame, 0, 20)) - .40 * smooth(unit(frame, 40, 15))
        image = art.stage(0, rabbit_motion=rabbit)
        return camera(image, 1 + .045 * smooth(unit(frame, 1, 56)), 540, 235)
    if frame < CUT["search"]:
        return phone_shot(frame, conversation)
    if frame < CUT["stage"]:
        opened = smooth(unit(frame, CUT["lid"] - 1, 14))
        raised = smooth(unit(frame, CUT["lift"] - 1, 24))
        image = art.prop_table(opened, raised)
        _, _, push = move_to_clue(frame, CUT["search"])
        return camera(image, 1 + .12 * push, 653, 304)

    # The rod is hand-driven: it runs past the mark, then comes back to it.
    rise = unit(frame, CUT["moon"] - 1, 18)
    settle = smooth(unit(frame, CUT["moon"] + 17, 8))
    moon = 1.04 * (1 - (1 - rise) ** 1.6) - .04 * settle
    rabbit = .60 + .40 * smooth(unit(frame, CUT["rabbit"] - 1, 14))
    release = smooth(unit(frame, CUT["audience"] - 2, 12)) - smooth(unit(frame, CUT["audience"] + 18, 13))
    image = art.stage(moon, rabbit_motion=rabbit, audience_motion=release)
    if frame >= CUT["brand"]:
        image = amber_title(image, smooth(unit(frame, CUT["brand"] - 1, 11)))
    return image


def event(frame, identity, kind, target, **state):
    return {"frame": frame, "id": identity, "kind": kind, "target": target, **state}


def event_map(conversation):
    open_ui = conversation.scene["timeline"]["initialUI"]
    events = [
        event(2, "stage.rabbit.wait", "puppet.pose", "rabbit"),
        event(CUT["phone"], "conversation.open", "ui.enter", "thread.stage-crew", uiState=open_ui),
        event(CUT["send"] - 2, "message.question.press", "ui.press", "composer.send"),
    ]
    for entry in conversation.mapped_events():
        entry.pop("layerIds", None)
        entry["kind"] = "message." + entry["kind"]
        events.append(entry)
    events.extend([
        event(CUT["search"], "prop.table.reveal", "edit.cut", "prop.red-tin", uiState=None),
        event(CUT["lid"], "prop.tin.open", "prop.open", "prop.red-tin"),
        event(CUT["lift"], "prop.moon.lift", "prop.lift", "prop.crescent"),
        event(CUT["stage"], "stage.return", "edit.cut", "stage"),
        event(CUT["moon"], "stage.moon.enter", "prop.enter", "stage.crescent"),
        event(CUT["rabbit"], "stage.rabbit.release", "puppet.pose", "rabbit"),
        event(CUT["audience"], "stage.audience.release", "audience.lean", "audience"),
        event(CUT["brand"], "brand.enter", "title.enter", "brand.keiki"),
    ])
    anchors = [
        ("room.start", "stage.rabbit.wait", -4000),
        ("send.press", "message.question.press", 0),
        ("send.release", "message.question.send", 0),
        ("reply.arrival", "message.answer.receive", 0),
        ("tin.contact", "prop.tin.open", 0),
        ("paper.rustle", "prop.moon.lift", 0),
        ("puppet.release", "stage.rabbit.release", 0),
        ("audience.release", "stage.audience.release", 0),
    ]
    return {
        "name": EDIT["title"], "width": WIDTH, "height": HEIGHT,
        "fps": FPS, "duration": EDIT["frameCount"] / FPS, "layers": [],
        "timeline": {
            "version": 1,
            "picture": {"fpsNum": FPS, "fpsDen": 1, "frameCount": EDIT["frameCount"]},
            "initialUI": None,
            "events": events,
            "cues": [{"id": name, "eventId": target, "offsetSamples": offset}
                     for name, target, offset in anchors],
        },
    }


def encode(conversation, destination):
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
            "-pixel_format", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS),
            "-i", "pipe:0", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
            "-preset", "fast", "-movflags", "+faststart", str(destination)]
    with subprocess.Popen(args, stdin=subprocess.PIPE) as process:
        try:
            for frame in range(EDIT["frameCount"]):
                process.stdin.write(render_frame(frame, conversation).tobytes())
        finally:
            process.stdin.close()
        if process.wait():
            raise RuntimeError(f"ffmpeg exited with {process.returncode}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ui-root", type=Path, default=SKILL_ROOT, help="Directory containing the team's ui package.")
    parser.add_argument("--frame", type=int, help="Render one numbered picture frame to PNG.")
    parser.add_argument("--map-only", action="store_true")
    args = parser.parse_args()
    if not (args.ui_root / "ui" / "adapter.py").is_file():
        parser.error("the team UI adapter is missing; see the film README for the pinned checkout")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    conversation = Conversation(EDIT, CUT, args.ui_root)
    if args.frame is not None:
        if not 0 <= args.frame < EDIT["frameCount"]:
            parser.error("frame is outside the edit")
        render_frame(args.frame, conversation).save(args.out)
        return
    args.out.with_suffix(".events.json").write_text(json.dumps(event_map(conversation), indent=2) + "\n")
    if not args.map_only:
        encode(conversation, args.out)


if __name__ == "__main__":
    main()
