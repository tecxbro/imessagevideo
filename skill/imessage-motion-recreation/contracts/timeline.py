#!/usr/bin/env python3
"""Resolve the v3 extension to the measured scene format."""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import re

SAMPLE_RATE = 48_000
ID = re.compile(r"[a-z0-9][a-z0-9._:-]*")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def shape(value, required, optional=()):
    require(isinstance(value, dict), "expected an object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    require(not missing and not extra, f"missing keys {sorted(missing)}; unexpected keys {sorted(extra)}")


def integer(value, name, minimum=None):
    require(type(value) is int, f"{name} must be an integer")
    require(minimum is None or value >= minimum, f"{name} must be at least {minimum}")
    return value


def identifier(value, name):
    require(isinstance(value, str) and ID.fullmatch(value), f"invalid {name}: {value!r}")
    return value


def unique(values, name):
    require(isinstance(values, list), f"{name} must be a list")
    result = set()
    for value in values:
        key = identifier(value, name)
        require(key not in result, f"duplicate {name}: {key}")
        result.add(key)
    return result


def ui_state(state):
    if state is None:
        return
    shape(state, ("conversationId", "messages", "composer", "viewport"))
    identifier(state["conversationId"], "conversation ID")
    messages = state["messages"]
    require(isinstance(messages, list), "messages must be a list")
    for message in messages:
        shape(message, ("id", "senderId", "text"), ("attachmentIds",))
        identifier(message["senderId"], "sender ID")
        require(isinstance(message["text"], str), "message text must be a string")
        unique(message.get("attachmentIds", []), "attachment ID")
    message_ids = unique([message["id"] for message in messages], "message ID")
    composer = state["composer"]
    shape(composer, ("text", "focused"))
    require(isinstance(composer["text"], str), "composer text must be a string")
    require(type(composer["focused"]) is bool, "composer focused must be a boolean")
    viewport = state["viewport"]
    shape(viewport, ("surface", "anchorMessageId"), ("selection",))
    identifier(viewport["surface"], "surface")
    anchor = viewport["anchorMessageId"]
    require(anchor is None or isinstance(anchor, str) and anchor in message_ids, "unknown viewport anchor message")
    if "selection" in viewport:
        unique(viewport["selection"], "selected message ID")
        require(set(viewport["selection"]) <= message_ids, "unknown selected message")


def layer_ids(layers):
    require(isinstance(layers, list), "layers must be a list")
    ids = set()
    for layer in layers:
        require(isinstance(layer, dict), "layer must be an object")
        layer_id = layer.get("id")
        require(isinstance(layer_id, str) and layer_id, "every layer must have a nonempty string ID")
        subtree = {layer_id}
        if "children" in layer:
            children = layer_ids(layer["children"])
            require(layer_id not in children, f"duplicate layer ID: {layer_id}")
            subtree.update(children)
        require(not ids.intersection(subtree), f"duplicate layer IDs: {sorted(ids.intersection(subtree))}")
        ids.update(subtree)
    return ids


def frame_sample(frame, rate):
    """Round a nonnegative rational timestamp to the nearest sample, ties upward."""
    return math.floor(Fraction(frame * SAMPLE_RATE, 1) / rate + Fraction(1, 2))


def resolve(scene):
    require(isinstance(scene, dict), "scene must be an object")
    integer(scene.get("width"), "width", 1)
    integer(scene.get("height"), "height", 1)
    timeline = scene.get("timeline")
    shape(timeline, ("version", "picture", "initialUI", "events", "cues"))
    require(integer(timeline["version"], "timeline version") == 1, "unsupported timeline version")
    picture = timeline["picture"]
    shape(picture, ("fpsNum", "fpsDen", "frameCount"))
    numerator = integer(picture["fpsNum"], "fpsNum", 1)
    denominator = integer(picture["fpsDen"], "fpsDen", 1)
    frames = integer(picture["frameCount"], "frameCount", 1)
    rate = Fraction(numerator, denominator)
    require(rate >= 1 and math.gcd(numerator, denominator) == 1, "picture rate must be reduced and at least 1 fps")
    for key, expected in (("fps", rate), ("duration", frames / rate)):
        value = scene.get(key)
        require(type(value) in (int, float) and math.isfinite(value)
                and math.isclose(value, float(expected), rel_tol=1e-12, abs_tol=0),
                f"scene {key} must project the picture clock: {float(expected)}")
    ids = layer_ids(scene.get("layers"))
    ui_state(timeline["initialUI"])
    events = {}
    ordered_events = []
    current_ui = timeline["initialUI"]
    previous_frame = -1
    state_frame = -1
    require(isinstance(timeline["events"], list), "events must be a list")
    for event in timeline["events"]:
        shape(event, ("id", "kind", "target", "frame"), ("layerIds", "uiState"))
        key = identifier(event["id"], "event ID")
        identifier(event["kind"], "event kind")
        identifier(event["target"], "event target")
        require(key not in events, f"duplicate event ID: {key}")
        frame = integer(event["frame"], f"{key} frame", 0)
        require(previous_frame <= frame < frames, f"{key}: events must be ordered and inside the picture")
        previous_frame = frame
        declared_layers = event.get("layerIds", [])
        require(isinstance(declared_layers, list) and all(isinstance(i, str) for i in declared_layers)
                and len(set(declared_layers)) == len(declared_layers), f"{key}: layerIds must be unique strings")
        require(set(declared_layers) <= ids, f"{key}: unknown layer IDs {sorted(set(declared_layers) - ids)}")
        if "uiState" in event:
            require(state_frame != frame, f"{key}: only one state change per frame")
            ui_state(event["uiState"])
            current_ui = event["uiState"]
            state_frame = frame
        entry = {**event, "sample": frame_sample(frame, rate), "uiState": current_ui}
        events[key] = entry
        ordered_events.append(entry)
    cue_ids = set()
    cues = []
    sample_count = frame_sample(frames, rate)
    require(isinstance(timeline["cues"], list), "cues must be a list")
    for cue in timeline["cues"]:
        shape(cue, ("id", "eventId", "offsetSamples"))
        key = identifier(cue["id"], "cue ID")
        event_id = identifier(cue["eventId"], "cue event ID")
        require(key not in cue_ids, f"duplicate cue ID: {key}")
        cue_ids.add(key)
        require(event_id in events, f"{key}: unknown event ID {event_id}")
        event = events[event_id]
        sample = event["sample"] + integer(cue["offsetSamples"], f"{key} sample offset")
        require(0 <= sample < sample_count, f"{key}: cue onset lies outside the picture")
        cues.append({**cue, "frame": event["frame"], "sample": sample})
    return {
        "version": 1, "picture": picture, "sampleRate": SAMPLE_RATE, "sampleCount": sample_count,
        "initialUI": timeline["initialUI"], "events": ordered_events, "cues": cues,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        report = resolve(json.loads(args.scene.read_text(encoding="utf-8")))
        result = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            args.out.write_text(result, encoding="utf-8")
        else:
            print(result, end="")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{args.scene}: {exc}\n")


if __name__ == "__main__":
    main()
