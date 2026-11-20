"""Compile an editable conversation into the repository's measured scene."""
import argparse
import base64
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import os

from PIL import Image, ImageOps

from .components import PALETTES, font_path
from .layout import Layout
from .state import KINDS, Conversation, copy, identifier, integer, number, require
from .tracks import loop_layers

IMAGE_FORMATS = {"PNG", "JPEG", "WEBP"}
PROFILE = "film-paper"
MOTION = {
    "focus": 7, "draft": 4, "send": 17, "receive": 7, "typing": 5, "reaction": 5,
    "scroll": 12, "camera": 12, "edit": 6, "unsend": 6, "receipt": 4, "overlay": 8,
    "media.page": 8, "suggestion": 6, "search.query": 0, "card.update": 6, "card.vote": 4,
}


def asset_paths(doc, input_dir, output_dir):
    result = {}
    assets = doc.get("assets", {})
    require(isinstance(assets, dict), "assets must map IDs to local image paths")
    for id, value in assets.items():
        identifier(id, "asset ID")
        value = copy(value, f"asset path for {id}", False)
        require("://" not in value and not value.startswith("data:"), "use local image paths")
        path = (input_dir / value).resolve(strict=True)
        with Image.open(path) as image:
            require(image.format in IMAGE_FORMATS and getattr(image, "n_frames", 1) == 1,
                    f"{id}: use a still PNG, JPEG or WEBP")
            src = os.path.relpath(path, output_dir)
            if image.getexif().get(274, 1) != 1:
                image = ImageOps.exif_transpose(image)
                buffer = BytesIO()
                image.convert("RGBA").save(buffer, format="PNG")
                src = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
            result[id] = (src, *image.size)
    return result


def inbox_entries(doc):
    entries = doc.get("inbox", [{"id": doc["conversationId"], "title": doc["title"], "preview": ""}])
    require(isinstance(entries, list), "inbox is a list of entries")
    ids = set()
    for entry in entries:
        id = identifier(entry["id"], "inbox entry ID")
        require(id not in ids, f"duplicate inbox entry {id}")
        ids.add(id)
        copy(entry["title"], "inbox title", False)
        copy(entry["preview"], "inbox preview")
    return entries


def initial_state(doc):
    people = doc["participants"]
    require(isinstance(people, dict) and len(people) >= 2, "participants must map at least two IDs to names")
    for id, name in people.items():
        identifier(id, "participant ID")
        copy(name, "participant name", False)
    owner = identifier(doc["localSenderId"], "local sender ID")
    require(owner in people, "localSenderId is an unknown participant")
    initial = doc.get("initial", {})
    require(isinstance(initial, dict), "initial must be an object")
    state = Conversation(identifier(doc["conversationId"], "conversation ID"), owner, people)
    require(type(initial.get("focused", False)) is bool, "initial.focused must be boolean")
    state.focused = initial.get("focused", False)
    state.draft = copy(initial.get("draft", ""), "initial draft")
    messages = initial.get("messages", [])
    require(isinstance(messages, list), "initial messages must be an array")
    for message in messages:
        state.add(message)
    return state


def validate_attachments(state, assets):
    for message in state.messages.values():
        for aid in message["attachmentIds"]:
            require(aid in assets, f"{message['id']}: unknown asset {aid}")


def compile_conversation(description, *, input_dir=Path.cwd(), output_dir=Path.cwd()):
    """Return an editable scene. Asset paths resolve from the specified output directory."""
    doc = deepcopy(description)
    require(isinstance(doc, dict), "conversation must be an object")
    require(type(doc.get("version")) is int and doc["version"] == 1, "conversation version must be 1")
    require(doc.get("skin", PROFILE) in PALETTES, f"unknown skin; use one of {', '.join(PALETTES)}")
    fps = integer(doc.get("fps", 24), "fps", 1, 120)
    frames = integer(doc["frameCount"], "frameCount", 1, fps * 600)
    assets = asset_paths(doc, Path(input_dir), Path(output_dir))
    state = initial_state(doc)
    validate_attachments(state, assets)
    layout = Layout(doc, assets, inbox_entries(doc), fps, frames)
    initial = state.timeline_state(*layout.render_state(state, 0, 0))
    timeline = []
    ids = set()
    previous = -1
    state_frame = -1
    events = doc.get("events", [])
    require(isinstance(events, list), "events must be an array")
    for event in events:
        require(isinstance(event, dict), "each event must be an object")
        id = identifier(event["id"], "event ID")
        require(id not in ids, f"duplicate event ID: {id}")
        ids.add(id)
        kind = event["kind"]
        require(kind in KINDS, f"{id}: unsupported event kind {kind!r}")
        frame = integer(event["frame"], "event frame", 0, frames - 1)
        require(previous <= frame, f"{id}: events must be ordered by frame")
        previous = frame
        duration = integer(event.get("durationFrames", round(MOTION[kind] * fps / 24)),
                           "motion duration", 0, fps * 5)
        target = state.apply(event)
        entry = {"id": id, "kind": kind, "target": target, "frame": frame}
        if kind == "camera":
            scale = number(event["scale"], "camera scale", .25, 6)
            x = number(event.get("x", 0), "camera x", -layout.width * 6, layout.width * 6)
            y = number(event.get("y", 0), "camera y", -layout.height * 6, layout.height * 6)
            layout.tracks.move(layout.camera, frame, duration, x=x + layout.center_x, y=y + layout.center_y,
                               scaleX=scale, scaleY=scale)
        else:
            require(frame != state_frame, f"{id}: one conversation action per frame")
            state_frame = frame
            validate_attachments(state, assets)
            screen = layout.render_state(state, frame, duration, action=kind, target=target)
            entry["uiState"] = state.timeline_state(*screen)
        entry["layerIds"] = layout.event_layers(kind, target)
        timeline.append(entry)
    cues = doc.get("cues", [])
    verify_cues(cues, timeline, fps, frames)
    layers = [layout.camera]
    layout.tracks.finish(layers)
    layer_ids = [layer["id"] for layer in loop_layers(layers)]
    require(len(layer_ids) == len(set(layer_ids)), "internal error: duplicate scene layer ID")
    return {
        "width": layout.canvas_width, "height": layout.canvas_height, "fps": fps, "duration": frames / fps,
        "background": "#27212a", "title": doc["title"], "layers": layers,
        "fonts": [
            {"family": "DejaVu Sans", "weight": weight,
             "src": os.path.relpath(font_path(weight), output_dir)}
            for weight in (400, 700)
        ],
        "timeline": {
            "version": 1, "picture": {"fpsNum": fps, "fpsDen": 1, "frameCount": frames},
            "initialUI": initial, "events": timeline, "cues": cues,
        },
    }


def verify_cues(cues, events, fps, frames):
    require(isinstance(cues, list), "cues must be an array")
    frame_by_id = {event["id"]: event["frame"] for event in events}
    ids = set()
    for cue in cues:
        require(isinstance(cue, dict) and set(cue) == {"id", "eventId", "offsetSamples"},
                "cue needs id, eventId and offsetSamples")
        id = identifier(cue["id"], "cue ID")
        event = identifier(cue["eventId"], "cue event ID")
        offset = cue["offsetSamples"]
        require(id not in ids and event in frame_by_id and type(offset) is int, f"invalid cue {id}")
        ids.add(id)
        sample = (frame_by_id[event] * 96_000 + fps) // (2 * fps) + offset
        require(0 <= sample < (frames * 96_000 + fps) // (2 * fps), f"{id}: cue lies outside picture")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conversation", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        scene = compile_conversation(json.loads(args.conversation.read_text(encoding="utf8")),
                                     input_dir=args.conversation.resolve().parent,
                                     output_dir=args.out.resolve().parent)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(1, f"{args.conversation}: {exc}\n")


if __name__ == "__main__":
    main()
