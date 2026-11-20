"""Compose custom booking art with the shared editable Messages interface."""
import argparse
import json
from pathlib import Path

from ui.adapter import compile_conversation
from ui.components import TextLayout, group, rect, text
from ui.tracks import loop_layers


OPEN_ID = "recreate.train.drawer"
CLOSE_ID = "recreate.train.drawer-close"
SELECTION_ID = "recreate.train.seat-selection"
SELECTION_LAYER = "booking.choice.checked"


def place_selection(scene, frame, open_frame, close_frame):
    fps = scene["fps"]
    layer = {node["id"]: node for node in loop_layers(scene["layers"])}
    tile = layer["ui.overlay.tray.item.0"]
    tile_body = layer["ui.overlay.tray.item.0.body"]
    tile_label = layer["ui.overlay.tray.item.0.label"]
    layer["ui.overlay.tray.heading"]["text"] = "Pick a train"
    x = tile_body["width"] - 27
    y = tile_body["height"] / 2 - 9
    available_width = x - tile_label["x"] - 5
    lines = TextLayout().wrap(
        tile_label["text"], available_width, tile_label["fontSize"], tile_label["fontWeight"])
    tile_label["text"] = "\n".join(lines)
    tile_label["y"] = (tile_body["height"] - tile_label["lineHeight"] * len(lines)) / 2
    tile["children"].extend([
        rect("booking.choice.outline", x, y, 18, 18, "#fffaf4", 5,
             stroke="#786579", strokeWidth=1.5, start=open_frame / fps, end=frame / fps),
        group(SELECTION_LAYER, x, y, [
            rect("booking.choice.fill", 0, 0, 18, 18, "#623864", 5),
            {"id": "booking.choice.glyph", "type": "path", "d": "M 4 9 L 7.5 12.5 L 14 5.5",
             "fill": "none", "stroke": "#ffffff", "strokeWidth": 1.7},
        ], start=frame / fps, end=close_frame / fps),
    ])


def build_scene(description, input_dir, output_dir, edit):
    selection_frame = edit.get("selectionFrame", description.pop("seatSelectionFrame"))
    by_id = {event["id"]: event for event in description["events"]}
    if "copy" in edit:
        by_id["recreate.train.request"]["message"]["text"] = edit["copy"]
    open_frame = by_id[OPEN_ID]["frame"]
    close_frame = by_id[CLOSE_ID]["frame"]
    if type(selection_frame) is not int or not open_frame < selection_frame < close_frame:
        raise ValueError("Select a frame between opening and closing the tray.")

    scene = compile_conversation(description, input_dir=input_dir, output_dir=output_dir)
    place_selection(scene, selection_frame, open_frame, close_frame)
    fps, width, height = scene["fps"], scene["width"], scene["height"]
    cut = 18
    camera, = scene["layers"]
    camera["start"] = cut / fps
    scene["layers"].insert(0, group("booking.title-shot", 0, 0, [
        rect("booking.title-backdrop", 0, 0, width, height, "#242342"),
        text("booking.title-kicker", "RAIL PLANNER", width / 2, height * .38, 13,
             fill="#c2befa", textAnchor="middle", letterSpacing=2.2, fontWeight=700),
        text("booking.title-copy", "Train options", width / 2, height * .43, 39,
             fill="#ffffff", textAnchor="middle", fontWeight=700),
    ], end=cut / fps))

    timeline = scene["timeline"]
    timeline["events"].extend([
        {"id": "recreate.train.conversation", "kind": "conversation.open",
         "frame": cut, "target": description["conversationId"], "layerIds": [camera["id"]],
         "uiState": timeline["initialUI"]},
        {"id": SELECTION_ID, "kind": "picker.select", "frame": selection_frame,
         "target": "train.first", "layerIds": [SELECTION_LAYER]},
    ])
    timeline["initialUI"] = None
    timeline["events"].sort(key=lambda event: event["frame"])
    timeline["cues"].append({
        "id": SELECTION_ID + ".cue", "eventId": SELECTION_ID, "offsetSamples": 0,
    })
    return scene


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conversation", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--edit", type=Path)
    args = parser.parse_args()
    output = args.out.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    scene = build_scene(load(args.conversation), args.conversation.resolve().parent,
                        output.parent, load(args.edit) if args.edit else {})
    write(output, scene)
    write(output.with_suffix(".events.json"), scene["timeline"])


if __name__ == "__main__":
    main()
