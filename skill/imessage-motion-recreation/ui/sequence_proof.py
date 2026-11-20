"""Render the standalone interaction fixtures and verify their moving pictures."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .adapter import compile_conversation
from .compare import contact_sheet, probe
from .components import FOOTER, GUTTER, HEADER
from .state import require
from .tracks import loop_layers


SKILL_DIR = Path(__file__).resolve().parent.parent
EXAMPLES = SKILL_DIR / "ui" / "examples"
CASES = ("send-keyboard", "tapback-scroll", "photos-fixed-header")


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def frame_value(layer, field, frame, fps):
    keys = layer.get("keyframes", {}).get(field, [])
    default = 1 if field == "opacity" else 0
    return next((key["value"] for key in reversed(keys) if key["t"] <= frame / fps),
                layer.get(field, default))


def event_message(event):
    return next(item for item in event["uiState"]["messages"] if item["id"] == event["target"])


def decode(path, scene, fps):
    info = probe(path)
    width, height = scene["width"], scene["height"]
    count = scene["timeline"]["picture"]["frameCount"]
    require((info["width"], info["height"]) == (width, height), "wrong picture dimensions")
    require(info["times"] == [Fraction(f, fps) for f in range(count)]
            and info["end"] == Fraction(count, fps), "wrong decoded frame clock")
    picture = subprocess.check_output([
        "ffmpeg", "-v", "error", "-xerror", "-threads", "1", "-i", str(path), "-map", "0:v:0",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-threads", "1", "pipe:1",
    ])
    return np.frombuffer(picture, dtype=np.uint8).reshape(count, height, width, 3), info["sha256"]


def delta(first, second):
    return float(np.abs(first.astype(np.int16) - second).mean())


def send_proof(events, initial, layers, picture, value):
    send, receipt = events
    frame = send["frame"]
    target = send["target"]
    name = f"ui.message/{target}"
    row, body, fill = (layers[name + suffix] for suffix in ("", "/body", ".ink"))
    require(initial["composer"]["text"] and event_message(send)["text"] == initial["composer"]["text"],
            "the sent row must contain the draft")
    require(event_message(send)["senderId"] == "alex" and receipt["target"] == target,
            "the draft and receipt must belong to the outgoing row")
    require(initial["composer"]["keyboardVisible"] and
            send["uiState"]["composer"] == {"text": "", "focused": True, "keyboardVisible": True},
            "send must clear the draft while retaining focus")
    composer = layers["ui.composer"]
    field_before = round(value(composer, "y", frame - 1))
    field_after = round(value(composer, "y", frame))
    draft_change = delta(picture[frame - 1, field_before + 18:field_before + 34, 65:310],
                         picture[frame, field_after + 18:field_after + 34, 65:310])
    require(draft_change > 2, "the decoded composer field did not change on send")
    settled = 34
    top = value(row, "y", settled)
    right = value(body, "x", settled) + fill["width"]
    require(right == picture.shape[2] - GUTTER and top < value(row, "y", frame)
            and top == value(row, "y", settled + 1), "outgoing row must rise and settle at its right-hand seat")
    ky = int(value(layers["ui.keyboard"], "y", frame)) + 8
    keyboard_end = picture.shape[1] - FOOTER
    keyboard_change = max(delta(picture[frame - 1, ky:keyboard_end], frame_image[ky:keyboard_end])
                          for frame_image in picture[frame:settled + 2])
    require(keyboard_change < 1.2, "keyboard moved or changed during send")
    cx, cy = round(right - 27), HEADER + round(top + 30)
    entrance = HEADER + round(value(row, "y", frame)) + 25
    require(delta(picture[frame - 1, entrance:entrance + 5, cx:cx + 10],
                  picture[frame, entrance:entrance + 5, cx:cx + 10]) > 20,
            "decoded outgoing row did not enter at the authored send frame")
    seat = picture[settled, cy:cy + 5, cx:cx + 10]
    require(float(seat[:, :, 2].mean()) - float(seat[:, :, 0].mean()) > 30
            and delta(seat, picture[settled + 1, cy:cy + 5, cx:cx + 10]) < 2.5,
            "decoded outgoing blue row did not hold at the measured seat")
    return {"settledFrame": settled, "rowRight": right, "keyboardMeanRgbDeltaMax": keyboard_change,
            "composerMeanRgbDeltaOnSend": draft_change}, [
        range(frame - 2, frame + 4), range(settled - 2, settled + 4), range(receipt["frame"] - 1, receipt["frame"] + 5)
    ]


def tapback_proof(events, layers, picture, value):
    context, reaction, scroll = events
    mark_frame, scroll_frame = reaction["frame"], scroll["frame"]
    target = reaction["target"]
    name = f"ui.message/{target}"
    row, badge, chip, transcript = (layers[key] for key in
                                     (name, name + "/reaction", name + "/reaction-chip", "ui.transcript"))
    require(context["target"] == target and badge in row["children"]
            and reaction["layerIds"] == [badge["id"]], "reaction must belong to its selected row")
    require(value(badge, "opacity", mark_frame - 1) == 0 < value(badge, "opacity", mark_frame),
            "badge must first appear at the authored action")
    after = next(item for item in scroll["uiState"]["messages"] if item["id"] == target)
    require(event_message(reaction)["reactions"] == after["reactions"] and bool(after["reactions"]),
            "scroll lost the reaction or changed the target ID")

    def decoded_badge(frame):
        x = round(value(badge, "x", frame)) + 3
        y = round(HEADER + value(row, "y", frame) + value(transcript, "y", frame)) + 2
        return picture[frame, y:y + 15, x:x + int(chip["width"]) - 6], y

    settled = 65
    before_crop, before_y = decoded_badge(scroll_frame - 1)
    after_crop, after_y = decoded_badge(settled)
    actual_shift = after_y - before_y
    relative_change = delta(before_crop, after_crop)
    require(actual_shift == scroll["uiState"]["viewport"]["scrollOffset"] > 0
            and np.ptp(before_crop) > 35 and relative_change < 4,
            "the decoded reaction did not travel with the same message row")
    return {"target": target, "reaction": after["reactions"], "badgeShiftPx": actual_shift,
            "badgeMeanRgbDeltaAfterTranslation": relative_change, "settledFrame": settled}, [
        range(context["frame"] - 2, context["frame"] + 4), range(mark_frame - 2, mark_frame + 4),
        range(scroll_frame - 2, scroll_frame + 4), range(settled - 2, settled + 4)
    ]


def photo_proof(events, layers, picture, value):
    swipe, back = events
    frame, return_frame = swipe["frame"], back["frame"]
    target = swipe["target"]
    name = f"ui.message/{target}"
    row, media, window, rail = (layers[name + suffix]
                                for suffix in ("", "/media", "/media-window", "/rail"))
    require(window in media["children"] and rail in window["children"] and window["clip"],
            "photos must move inside their attachment clip")
    settled = 26
    require(value(rail, "x", frame) < value(rail, "x", frame - 1) and
            value(rail, "x", settled) == value(rail, "x", settled + 1) < 0
            and value(rail, "x", 51) == 0, "photo rail did not advance, settle and return")
    require(event_message(swipe)["page"] == 1 and event_message(back)["page"] == 0,
            "page readback disagrees with the rail")
    header_change = max(delta(picture[frame - 1, :HEADER], image[:HEADER]) for image in picture)
    x = round(value(media, "x", frame)) + 10
    y = round(HEADER + value(row, "y", frame) + value(media, "y", frame)) + 10
    box = picture[:, y:y + int(window["clip"]["height"]) - 20, x:x + int(window["clip"]["width"]) - 20]
    photo_change = delta(box[frame - 1], box[settled])
    require(header_change < 1.2 and photo_change > 8 and delta(box[frame - 1], box[51]) < 3,
            "decoded photo rail failed to change and return behind a fixed header")
    return {"target": target, "attachmentOrder": event_message(swipe)["attachmentIds"],
            "headerMeanRgbDeltaMax": header_change, "photoMeanRgbDelta": photo_change,
            "settledFrame": settled}, [
        range(frame - 2, frame + 4), range(settled - 2, settled + 4), range(return_frame - 2, return_frame + 4)
    ]


def payment_proof(events, layers, picture, value):
    card, approval, dismiss, result = events
    require(len({event["target"] for event in events}) == 1, "payment states must refer to the same card")
    require([event["uiState"]["viewport"]["surface"] for event in events] ==
            ["conversation", "payment-approval", "conversation", "conversation"],
            "the separate mock approval must dismiss to the thread")
    card_layer = layers["ui.message/request/card"]
    require([node["start"] for node in card_layer["children"]] ==
            [card["frame"] / 24, result["frame"] / 24], "the result must replace the original card's contents")
    require(value(layers["ui.overlay"], "opacity", 58) == 1
            and value(layers["ui.overlay"], "opacity", 66) == 0, "approval sheet did not dismiss")
    require(delta(picture[33], picture[41]) > 10 and delta(picture[33], picture[67]) < 1.2,
            "decoded mock approval must appear and clear before the result")
    require(delta(picture[77, HEADER:350], picture[78, HEADER:350]) > 0.5,
            "decoded card contents did not change at the result event")
    return {"capture": "labeled test mock", "target": card["target"], "dismissedFrame": 66}, [
        range(event["frame"] - 2, event["frame"] + 4) for event in events
    ]


def sheet(picture, windows, path, fps):
    panels = []
    width = 176
    height = round(picture.shape[1] * width / picture.shape[2])
    font = ImageFont.load_default(size=12)
    for frames in windows:
        for frame in frames:
            panel = Image.new("RGB", (width, height + 23), "#25212b")
            panel.paste(Image.fromarray(picture[frame]).resize((width, height)), (0, 0))
            ImageDraw.Draw(panel).text((7, height + 4), f"f{frame} · {frame/fps:.3f} s", fill="white", font=font)
            panels.append(panel)
    contact_sheet(panels, path, 6)


def run_case(name, work, out, resolver):
    path = EXAMPLES / (name + ".json")
    scene = compile_conversation(read(path), input_dir=EXAMPLES, output_dir=work)
    scene_path = work / (name + ".scene.json")
    scene_path.write_text(json.dumps(scene), encoding="utf8")
    video = work / (name + ".mp4")
    subprocess.run([sys.executable, str(SKILL_DIR / "scripts/engines/render_pillow.py"),
                    "--scene", str(scene_path), "--out", str(video)], check=True)
    subprocess.run([sys.executable, str(resolver), str(scene_path),
                    "--out", str(out / (name + ".events.json"))], check=True)
    fps = scene["fps"]
    picture, sha = decode(video, scene, fps)
    layers = {node["id"]: node for node in loop_layers(scene["layers"])}
    events = scene["timeline"]["events"]

    def value(layer, field, frame):
        return frame_value(layer, field, frame, fps)

    case = name.removesuffix("-edited")
    if case == "send-keyboard":
        measurements, windows = send_proof(events, scene["timeline"]["initialUI"], layers, picture, value)
    else:
        check = {"tapback-scroll": tapback_proof, "photos-fixed-header": photo_proof,
                 "payment-mock": payment_proof}[case]
        measurements, windows = check(events, layers, picture, value)
    shutil.copyfile(video, out / video.name)
    sheet(picture, windows, out / (name + "-frames.jpg"), fps)
    return {"sha256": sha, "frames": len(picture), "fps": fps, **measurements,
            "frameWindows": [[frames.start, frames.stop - 1] for frames in windows]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--resolver", type=Path, default=SKILL_DIR / "contracts/timeline.py")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="ui-sequence-scenes-") as temp:
        runs = [name for case in CASES for name in (case, case + "-edited")] + ["payment-mock"]
        results = {name: run_case(name, Path(temp), args.out_dir.resolve(), args.resolver.resolve())
                   for name in runs}
    require(all(results[case]["sha256"] != results[case + "-edited"]["sha256"] for case in CASES),
            "an edited input produced the unchanged picture")
    (args.out_dir / "proof.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
