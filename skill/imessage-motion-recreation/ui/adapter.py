"""Compile an editable conversation into the repository's measured scene."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import os

from PIL import Image

from .accessories import KEYBOARD_HEIGHT, context_menu, keyboard, media_viewer, tray
from .components import (
    FOOTER, GUTTER, HEADER, INK, LAVENDER, MUTED, PAPER, PLUM, TextLayout,
    bubble, clip, composer, font_path, group, header, rect, text, typing,
)
from .state import KINDS, Conversation, copy, identifier, integer, number, require
from .tracks import Tracks, loop_layers

IMAGE_FORMATS = {"PNG", "JPEG", "WEBP"}
PROFILE = "film-paper"
MOTION = {
    "focus": 7, "draft": 4, "send": 10, "receive": 7, "typing": 5, "reaction": 5,
    "scroll": 12, "camera": 12, "edit": 6, "unsend": 6, "receipt": 4, "overlay": 8,
    "media.page": 8,
}


def mount(nodes, parent):
    parent["children"].extend(nodes)
    return parent


class Layout:
    def __init__(self, doc, assets, fps, frames):
        display = doc.get("display", {})
        self.width = integer(display.get("width", 390), "display width", 320, 1080)
        self.height = integer(display.get("height", 720), "display height", 480, 1920)
        self.size = integer(display.get("textSize", 16), "text size", 13, 24)
        self.measure = TextLayout()
        self.assets = assets
        self.tracks = Tracks(fps, frames)
        self.rows = {}
        self.transcript = group("ui.transcript", 0, 0, [])
        self.typing = group("ui.typing", GUTTER, 0, [], opacity=0)
        self.viewport = group("ui.viewport", 0, HEADER, [self.transcript],
                              clip=clip(self.width, self.height - HEADER - FOOTER))
        self.keyboard = group("ui.keyboard", 0, self.height, keyboard(self.width))
        self.composer = group("ui.composer", 0, 0, [])
        self.overlay = group("ui.overlay", 0, self.height, [], opacity=0)
        self.camera = group("ui.camera", 0, 0, [
            rect("ui.paper", 0, 0, self.width, self.height, PAPER),
            self.viewport, self.keyboard, self.composer,
            rect("ui.footer", 0, self.height - FOOTER, self.width, FOOTER, PAPER),
            header(self.width, copy(doc["title"], "title", False), copy(doc.get("service", "Messages"), "service"), self.measure),
            self.overlay,
        ], originX=self.width / 2, originY=self.height / 2)
        mount([self.typing], self.transcript)

    def photo(self, id, asset_id, x, y, width, height):
        src, iw, ih = self.assets[asset_id]
        scale = min(width / iw, height / ih)
        w, h = round(iw * scale, 3), round(ih * scale, 3)
        return dict(id=id, type="image", src=src, x=x + (width - w) / 2,
                    y=y + (height - h) / 2, width=w, height=h)

    def new_row(self, mid, frame):
        id = f"ui.message/{mid}"
        row = group(id, 0, 0, [], start=frame / self.tracks.fps)
        row["children"] = [
            group(id + "/body", 0, 0, []),
            group(id + "/media", 0, 0, []),
            group(id + "/reaction", 0, 0, [], opacity=0),
            group(id + "/receipt", 0, 0, []),
        ]
        self.transcript["children"].insert(-1, row)
        self.rows[mid] = row
        return row

    def media_stack(self, id, attachments, width):
        stride = width + 8
        height = round(min(width * .63, 190))
        tiles = []
        for i, aid in enumerate(attachments):
            tiles.extend([
                rect(id + f"/{aid}/matte", i * stride, 0, width, height, LAVENDER, 9),
                self.photo(id + f"/{aid}/image", aid, i * stride, 0, width, height),
            ])
        return height, stride, tiles

    def message(self, state, message, joined, frame, duration):
        mid = message["id"]
        row = self.rows.get(mid)
        new = row is None
        if new:
            row = self.new_row(mid, frame)
        id = row["id"]
        body, media, reaction, receipt = row["children"]
        outgoing = message["senderId"] == state.owner
        unsent = message["unsent"]
        show_name = len(state.people) > 2 and not outgoing
        cursor = 0
        parts = []
        attachments = [] if unsent else message["attachmentIds"]
        marks = {} if unsent else message["reactions"]
        if marks:
            cursor += 13
        if show_name:
            name = self.measure.ellipsis(state.people[message["senderId"]], self.width - GUTTER * 2, 11)
            parts.append(text(id + "/sender", name, 0, cursor, 11, fill=MUTED))
            cursor += 17
        if message["replyTo"] and not unsent:
            quoted = state.messages[message["replyTo"]]
            original = "Message removed" if quoted["unsent"] else quoted["text"] or "Attachment"
            snippet = self.measure.ellipsis(original, self.width * .66 - 18, 11)
            parts.extend([
                rect(id + "/quote-rule", 0, cursor + 2, 2, 13, PLUM, 1),
                text(id + "/quote", snippet, 8, cursor, 11, fill=MUTED),
            ])
            cursor += 20
        copy = "Message removed" if unsent else message["text"]
        media_width = min(250, round(self.width * .71)) if attachments else 0
        bubble_width = 0
        if copy:
            bubble_width, h, bubble_parts = bubble(id, copy, outgoing, self.width, self.measure,
                                                   joined, self.size, color="#786579" if unsent else None)
            parts.append(group(id + "/text", 0, cursor, bubble_parts))
            cursor += h
        width = max(bubble_width, media_width)
        x = self.width - GUTTER - width if outgoing else GUTTER
        if copy and outgoing and bubble_width < width:
            parts[-1]["x"] = width - bubble_width
        self.tracks.move(body, frame, 0 if new else duration, x=x)
        if attachments:
            if copy:
                cursor += 5
            height, stride, tiles = self.media_stack(id + "/tiles", attachments, media_width)
            if not media["children"]:
                rail = group(id + "/rail", 0, 0, tiles)
                media["children"].append(group(id + "/media-window", 0, 0, [rail],
                                                clip=clip(media_width, height, 9)))
            rail = media["children"][0]["children"][0]
            self.tracks.move(rail, frame, 0 if new else duration, x=-message["page"] * stride)
            self.tracks.move(media, frame, 0 if new else duration,
                             x=self.width - GUTTER - media_width if outgoing else GUTTER, y=cursor,
                             opacity=1)
            cursor += height
            if len(attachments) > 1:
                parts.append(text(id + "/page", f"{message['page'] + 1} / {len(attachments)}",
                                  width / 2, cursor + 3, 10, textAnchor="middle", fill=MUTED))
                cursor += 17
        elif media["children"]:
            self.tracks.move(media, frame, 0, opacity=0)
        self.tracks.revise(body, parts, frame)
        if marks:
            label = self.measure.ellipsis("  ".join(marks.values()), self.width * .52 - 16, 11, 700)
            badge_width = self.measure.width(label, 11, 700) + 16
            self.tracks.revise(reaction, [
                rect(id + "/reaction-chip", 0, 0, badge_width, 20, "#fffaf4", 7, stroke=PLUM, strokeWidth=1),
                text(id + "/reaction-mark", label, badge_width / 2, 3, 11, fill=PLUM,
                     textAnchor="middle", fontWeight=700),
            ], frame)
            self.tracks.move(reaction, frame, 0, x=max(GUTTER, x + width - badge_width - 6))
            self.tracks.move(reaction, frame, duration, opacity=1)
        else:
            self.tracks.move(reaction, frame, 0, opacity=0)
        detail = []
        if message["edited"] and not unsent:
            detail.append("Edited")
        if state.receipt_id == mid and message["receipt"] and not unsent:
            detail.append(message["receipt"])
        self.tracks.revise(receipt, [
            text(id + "/status", " · ".join(detail), 0, 0, 10, fill=MUTED,
                 textAnchor="end" if outgoing else "start")
        ] if detail else [], frame)
        self.tracks.move(receipt, frame, 0, x=x + width if outgoing else x, y=cursor + 3)
        return row, new, cursor + (16 if detail else 0)

    def render_state(self, state, frame, duration, new_message=False):
        keyboard_height = KEYBOARD_HEIGHT if state.focused and not (
            state.overlay and state.overlay["surface"] == "tray") else 0
        composer_height, composer_parts = composer(self.width, state.draft, state.focused, self.measure)
        composer_y = self.height - FOOTER - keyboard_height - composer_height
        self.tracks.revise(self.composer, composer_parts, frame)
        self.tracks.move(self.composer, frame, duration, y=composer_y)
        self.tracks.move(self.keyboard, frame, duration, y=self.height - FOOTER - keyboard_height)
        messages = list(state.messages.values())
        cursor = 11
        bounds = []
        for i, message in enumerate(messages):
            joined = (i + 1 < len(messages) and message["senderId"] == messages[i + 1]["senderId"]
                      and not (message["unsent"] or messages[i + 1]["unsent"]))
            row, new, height = self.message(state, message, joined, frame, duration)
            bounds.append((message, cursor, cursor + height))
            if new:
                row["y"] = cursor + (11 if frame else 0)
                if frame:
                    row["opacity"] = .38
                    self.tracks.move(row, frame, duration, opacity=1)
            self.tracks.move(row, frame, duration, y=cursor)
            cursor += height + (4 if joined else 10)
        if state.typist:
            self.tracks.revise(self.typing, typing("ui.typing", state.people[state.typist], self.width, self.measure), frame)
            self.tracks.move(self.typing, frame, 0, y=cursor)
            self.tracks.move(self.typing, frame, duration, opacity=1)
            cursor += 39
        else:
            self.tracks.move(self.typing, frame, 0, opacity=0)
        live_height = composer_y - HEADER
        bottom = min(0, live_height - cursor)
        scroll_y = min(0, bottom + state.scroll)
        if new_message and frame and state.scroll == 0 and scroll_y < self.tracks.value(self.transcript, "y", frame - 1):
            # Advance enough on the first action frame for the new row to enter the viewport.
            previous_y = self.tracks.value(self.transcript, "y", frame - 1)
            self.tracks.move(self.transcript, frame, 0, y=max(scroll_y, previous_y - 32))
            self.tracks.move(self.transcript, frame + 1, max(0, duration - 1), y=scroll_y)
        else:
            self.tracks.move(self.transcript, frame, duration, y=scroll_y)
        self.render_overlay(state, bounds, scroll_y, live_height, frame, duration)
        return next((m["id"] for m, top, end in reversed(bounds)
                     if not m["unsent"] and end + scroll_y > 0 and top + scroll_y < live_height), None)

    def render_overlay(self, state, bounds, scroll_y, live_height, frame, duration):
        overlay = state.overlay
        if overlay is None:
            self.tracks.move(self.overlay, frame, duration, opacity=0)
            return
        width = self.width
        surface = overlay["surface"]
        if surface == "tray":
            height = min(190, self.height - HEADER - FOOTER)
            layers = tray(width, height, overlay["items"])
            y = self.height - FOOTER - height
            x = 0
        elif surface == "context":
            width = min(276, self.width - GUTTER * 2)
            height = 162
            labels = ["Reply", "Copy", "More"]
            layers = context_menu(width, height, labels, reaction_labels=["Like", "Love", "Wow"])
            selected = next((b for b in bounds if b[0]["id"] == overlay["messageId"]))
            row_y = HEADER + scroll_y + selected[1]
            row_end = HEADER + scroll_y + selected[2]
            y = row_end + 7 if row_end + height + 7 < HEADER + live_height else row_y - height - 7
            y = max(HEADER + 4, min(self.height - FOOTER - height, y))
            x = self.width - GUTTER - width if selected[0]["senderId"] == state.owner else GUTTER
        else:
            message = state.messages[overlay["messageId"]]
            asset = self.assets[message["attachmentIds"][message["page"]]]
            layers = media_viewer(width, self.height, f"Photo {message['page'] + 1}", asset[0],
                                  image_size=asset[1:])
            x, y = 0, 0
        if self.tracks.value(self.overlay, "opacity", max(0, frame - 1)) == 0:
            self.tracks.move(self.overlay, frame, 0, x=x, y=y + 10)
            self.tracks.move(self.overlay, frame + 1, max(0, duration - 1), x=x, y=y)
        else:
            self.tracks.move(self.overlay, frame, duration, x=x, y=y)
        self.tracks.revise(self.overlay, layers, frame)
        self.tracks.move(self.overlay, frame, duration, opacity=1)

    def event_layers(self, kind, target):
        row = self.rows.get(target)
        if kind == "camera":
            return ["ui.camera"]
        if kind in {"draft", "focus"}:
            return ["ui.composer", "ui.keyboard"] if kind == "focus" else ["ui.composer"]
        if kind == "scroll":
            return ["ui.transcript"]
        if kind == "typing":
            return ["ui.typing"]
        if kind == "overlay":
            return ["ui.overlay"]
        suffix = {"reaction": "/reaction", "media.page": "/media", "receipt": "/receipt"}
        return [row["id"] + suffix.get(kind, "")]


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
            result[id] = (os.path.relpath(path, output_dir), *image.size)
    return result


def initial_state(doc):
    people = doc["participants"]
    require(isinstance(people, dict) and len(people) >= 2, "participants must map at least two IDs to names")
    for id, name in people.items():
        identifier(id, "participant ID")
        copy(name, "participant name", False)
    owner = identifier(doc["localSenderId"], "local sender ID")
    require(owner in people, "localSenderId is an unknown participant")
    initial = doc.get("initial", {})
    state = Conversation(identifier(doc["conversationId"], "conversation ID"), owner, people)
    require(type(initial.get("focused", False)) is bool, "initial.focused must be boolean")
    state.focused = initial.get("focused", False)
    state.draft = copy(initial.get("draft", ""), "initial draft")
    for message in initial.get("messages", []):
        state.add(message)
    return state


def validate_attachments(state, assets):
    for message in state.messages.values():
        for aid in message["attachmentIds"]:
            require(aid in assets, f"{message['id']}: unknown asset {aid}")


def compile_conversation(description, *, input_dir=Path.cwd(), output_dir=Path.cwd()):
    """Return an editable scene. Asset paths resolve from the specified output directory."""
    doc = deepcopy(description)
    require(doc.get("version") == 1, "conversation version must be 1")
    require(doc.get("skin", PROFILE) == PROFILE, f"unknown skin; use {PROFILE}")
    fps = integer(doc.get("fps", 24), "fps", 1, 120)
    frames = integer(doc["frameCount"], "frameCount", 1, fps * 600)
    assets = asset_paths(doc, Path(input_dir), Path(output_dir))
    state = initial_state(doc)
    validate_attachments(state, assets)
    layout = Layout(doc, assets, fps, frames)
    anchor = layout.render_state(state, 0, 0)
    initial = state.timeline_state(anchor)
    timeline = []
    ids = set()
    previous = -1
    state_frame = -1
    for event in doc.get("events", []):
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
            layout.tracks.move(layout.camera, frame, duration, x=x, y=y, scaleX=scale, scaleY=scale)
        else:
            require(frame != state_frame, f"{id}: one conversation action per frame")
            state_frame = frame
            validate_attachments(state, assets)
            anchor = layout.render_state(state, frame, duration, new_message=kind in {"send", "receive"})
            entry["uiState"] = state.timeline_state(anchor)
        entry["layerIds"] = layout.event_layers(kind, target)
        timeline.append(entry)
    cues = doc.get("cues", [])
    verify_cues(cues, timeline, fps, frames)
    layers = [layout.camera]
    layout.tracks.finish(layers)
    layer_ids = [layer["id"] for layer in loop_layers(layers)]
    require(len(layer_ids) == len(set(layer_ids)), "internal error: duplicate scene layer ID")
    return {
        "width": layout.width, "height": layout.height, "fps": fps, "duration": frames / fps,
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
