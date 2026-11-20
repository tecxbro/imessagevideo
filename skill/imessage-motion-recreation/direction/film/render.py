#!/usr/bin/env python3
"""Render the editable 24 fps picture and its frame-addressed handoff."""
from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import stage as art


HERE = Path(__file__).resolve().parent
EDIT = json.loads((HERE / "edit.json").read_text())
WIDTH, HEIGHT = EDIT["width"], EDIT["height"]
FPS = EDIT["fps"]
FONT_ROOT = Path("/usr/share/fonts/truetype")


@lru_cache
def font(size, face="regular"):
    paths = {
        "regular": "dejavu/DejaVuSans.ttf",
        "bold": "dejavu/DejaVuSans-Bold.ttf",
        "serif": "dejavu/DejaVuSerif.ttf",
    }
    return ImageFont.truetype(str(FONT_ROOT / paths[face]), size)


def progress(frame, start, extent):
    return min(1.0, max(0.0, (frame - start) / extent))


def ease(t):
    return t * t * (3 - 2 * t)


def camera(image, scale, x=480, y=270):
    """Move the camera around image point (x, y) with subpixel sampling."""
    inverse = 1 / scale
    return image.transform(
        (WIDTH, HEIGHT), Image.Transform.AFFINE,
        (inverse, 0, x * (1 - inverse), 0, inverse, y * (1 - inverse)),
        resample=Image.Resampling.BICUBIC,
    )


def composite(dst, src, x, y, angle=0):
    if angle:
        size = src.size
        src = src.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        x -= (src.width - size[0]) / 2
        y -= (src.height - size[1]) / 2
    dst.alpha_composite(src, (round(x), round(y)))


def bubble(draw, x, y, copy, outgoing):
    color = "#2177cc" if outgoing else "#37353c"
    ink = "#ffffff" if outgoing else "#f7f2ec"
    width = math.ceil(draw.textlength(copy, font=font(24))) + 32
    edge = x - width if outgoing else x
    draw.rounded_rectangle((edge, y, edge + width, y + 52), 21, fill=color)
    tail = x - 4 if outgoing else x + 4
    direction = 1 if outgoing else -1
    draw.polygon([(tail, y + 37), (tail, y + 50),
                  (tail + direction * 13, y + 53),
                  (tail + direction * 5, y + 43)], fill=color)
    draw.text((edge + 16, y + 26), copy, font=font(24), fill=ink, anchor="lm")


def phone_panel(frame, cuts):
    """Early-cut interface. The conversation inputs are shared with the adapter."""
    panel = Image.new("RGBA", (385, 525))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle((0, 0, 384, 524), 46, fill="#110d11", outline="#7c5a4d", width=2)
    draw.rounded_rectangle((9, 9, 375, 516), 37, fill="#211e24", outline="#2f2830", width=2)
    draw.rounded_rectangle((154, 23, 232, 38), 9, fill="#0c0b0e")
    draw.line([(35, 77), (25, 88), (35, 99)], fill="#9bc7ff", width=3)
    draw.ellipse((173, 54, 211, 92), fill="#8e4c46")
    draw.text((192, 73), "SC", fill="#fff1dd", font=font(14, "bold"), anchor="mm")
    draw.text((192, 111), EDIT["conversation"], fill="#faeee5", font=font(22, "bold"), anchor="mm")
    draw.line((28, 137, 357, 137), fill="#3f3740", width=1)
    draw.text((192, 161), "iMessage", fill="#b7aeb3", font=font(16), anchor="mm")

    if frame >= cuts["send"]:
        rise = 1 - ease(progress(frame, cuts["send"], 7))
        bubble(draw, 346, 191 + round(23 * rise), EDIT["question"], True)
    if frame >= cuts["reply"]:
        rise = 1 - ease(progress(frame, cuts["reply"], 6))
        bubble(draw, 30, 257 + round(13 * rise), EDIT["answer"], False)
    draw.ellipse((25, 433, 64, 472), fill="#393139")
    draw.line((36, 452, 53, 452), fill="#f2d5c5", width=2)
    draw.line((44, 444, 44, 460), fill="#f2d5c5", width=2)
    draw.rounded_rectangle((76, 429, 356, 475), 21, outline="#62545d", width=2)
    draft = frame < cuts["send"]
    label = EDIT["question"] if draft else "iMessage"
    draw.text((89, 452), label, font=font(21), fill="#fff4eb" if draft else "#a698a2", anchor="lm")
    if draft:
        press = frame >= cuts["send"] - 2
        r = 14 if press else 17
        draw.ellipse((334 - r, 452 - r, 334 + r, 452 + r), fill="#2177cc")
        draw.line([(328, 453), (334, 447), (340, 453)], fill="white", width=2)
        draw.line((334, 448, 334, 460), fill="white", width=2)
    draw.rounded_rectangle((137, 500, 247, 504), 2, fill="#decfd3")
    return panel


def phone_shot(frame, cuts, variant):
    age = frame - cuts["phone"]
    background = art.prop_table(0, 0).filter(ImageFilter.GaussianBlur(10)).convert("RGBA")
    background = Image.blend(background, Image.new("RGBA", background.size, "#170e1a"), .55)
    settle = ease(progress(age, 0, 12))
    turn = ease(progress(frame, cuts["search"] - 9, 9)) if variant == "final" else 0
    x = 232 + 23 * (1 - settle) - 61 * turn
    y = 11 + 14 * (1 - settle) + 4 * turn
    angle = -2.5 + 2.5 * settle + 3 * turn
    panel = phone_panel(frame, cuts)
    shadow = Image.new("RGBA", panel.size)
    shadow.putalpha(panel.getchannel("A").point(lambda a: a * .68))
    composite(background, shadow.filter(ImageFilter.GaussianBlur(12)), x + 12, y + 9, angle)
    composite(background, panel, x, y, angle)
    return background.convert("RGB")


def amber_title(image, opacity):
    veil = Image.new("RGB", image.size, "#120e17")
    image = Image.blend(image, veil, opacity * .91)
    lettering = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(lettering)
    amber = (255, 226, 178, round(opacity * 255))
    cream = (255, 239, 216, round(opacity * 255))
    draw.text((480, 239), EDIT["brand"], font=font(76, "serif"), fill=amber, anchor="mm")
    draw.text((480, 326), EDIT["endline"], font=font(29), fill=cream, anchor="mm")
    return Image.alpha_composite(image.convert("RGBA"), lettering).convert("RGB")


def render_frame(frame, cuts, variant):
    if frame < cuts["phone"]:
        rabbit = ease(progress(frame, 3, 19)) - .40 * ease(progress(frame, 40, 15))
        image = art.stage(0, rabbit_motion=rabbit)
        return camera(image, 1 + .045 * ease(progress(frame, 1, 56)), 540, 235)
    if frame < cuts["search"]:
        return phone_shot(frame, cuts, variant)
    if frame < cuts["stage"]:
        opened = ease(progress(frame, cuts["lid"] - 1, 14))
        raised = ease(progress(frame, cuts["lift"] - 1, 24))
        image = art.prop_table(opened, raised)
        if variant == "rough":
            return image
        move = progress(frame, cuts["search"] - 5, 16)
        return camera(image, 1 + .12 * ease(move), 653, 304)
    moon = progress(frame, cuts["moon"] - 1, 22)
    rabbit = .60 + .40 * ease(progress(frame, cuts["rabbit"] - 1, 14))
    image = art.stage(moon, rabbit_motion=rabbit)
    if frame >= cuts["brand"]:
        image = amber_title(image, ease(progress(frame, cuts["brand"] - 1, 11)))
    return image


def conversation_state(question=False, answer=False):
    messages = []
    if question:
        messages.append({"id": "message.question", "senderId": "customer", "text": EDIT["question"]})
    if answer:
        messages.append({"id": "message.answer", "senderId": "agent.stage-crew", "text": EDIT["answer"]})
    return {
        "conversationId": "thread.stage-crew", "messages": messages,
        "composer": {"text": "" if question else EDIT["question"], "focused": False},
        "viewport": {"surface": "conversation",
                     "anchorMessageId": messages[-1]["id"] if messages else None},
    }


def event_map(cuts, variant):
    keys = [
        (3, "stage.rabbit.wait", "puppet.pose", "rabbit"),
        (cuts["phone"], "conversation.open", "ui.enter", "thread.stage-crew", conversation_state()),
        (cuts["send"] - 2, "message.question.press", "ui.press", "composer.send"),
        (cuts["send"], "message.question.send", "message.send", "message.question", conversation_state(True)),
        (cuts["reply"], "message.answer.receive", "message.receive", "message.answer", conversation_state(True, True)),
        (cuts["search"], "prop.table.reveal", "edit.cut", "prop.red-tin", None),
        (cuts["lid"], "prop.tin.open", "prop.open", "prop.red-tin"),
        (cuts["lift"], "prop.moon.lift", "prop.lift", "prop.crescent"),
        (cuts["stage"], "stage.return", "edit.cut", "stage"),
        (cuts["moon"], "stage.moon.enter", "prop.enter", "stage.crescent"),
        (cuts["rabbit"], "stage.rabbit.release", "puppet.pose", "rabbit"),
        (cuts["brand"], "brand.enter", "title.enter", "brand.keiki"),
    ]
    events = []
    for frame, name, kind, target, *states in keys:
        event = {"id": name, "kind": kind, "target": target, "frame": frame}
        if states:
            event["uiState"] = states[0]
        events.append(event)
    anchors = [
        ("room.start", "stage.rabbit.wait", -6000),
        ("send.press", "message.question.press", 0),
        ("send.release", "message.question.send", 0),
        ("reply.arrival", "message.answer.receive", 0),
        ("tin.contact", "prop.tin.open", 0),
        ("paper.rustle", "prop.moon.lift", 0),
        ("puppet.release", "stage.rabbit.release", 0),
    ]
    return {
        "name": EDIT["title"],
        "cut": variant,
        "width": WIDTH,
        "height": HEIGHT,
        "fps": FPS,
        "duration": EDIT["frameCount"] / FPS,
        "layers": [],
        "timeline": {
            "version": 1,
            "picture": {"fpsNum": FPS, "fpsDen": 1, "frameCount": EDIT["frameCount"]},
            "initialUI": None,
            "events": events,
            "cues": [{"id": name, "eventId": event, "offsetSamples": offset}
                     for name, event, offset in anchors],
        },
    }


def encode(cuts, variant, destination):
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
            "-pixel_format", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS),
            "-i", "pipe:0", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
            "-preset", "fast", "-movflags", "+faststart", str(destination)]
    with subprocess.Popen(args, stdin=subprocess.PIPE) as process:
        try:
            for frame in range(EDIT["frameCount"]):
                process.stdin.write(render_frame(frame, cuts, variant).tobytes())
        finally:
            process.stdin.close()
        if process.wait():
            raise RuntimeError(f"ffmpeg exited with {process.returncode}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cut", choices=EDIT["cuts"], default="final")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--frame", type=int, help="Render one numbered picture frame to PNG.")
    parser.add_argument("--map-only", action="store_true")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cuts = EDIT["cuts"][args.cut]
    if args.frame is not None:
        if not 0 <= args.frame < EDIT["frameCount"]:
            parser.error("frame is outside the edit")
        render_frame(args.frame, cuts, args.cut).save(args.out)
        return
    args.out.with_suffix(".events.json").write_text(json.dumps(event_map(cuts, args.cut), indent=2) + "\n")
    if not args.map_only:
        encode(cuts, args.cut, args.out)


if __name__ == "__main__":
    main()
