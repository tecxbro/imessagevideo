"""Apply a catalog motion to events in an existing editable Messages conversation."""
import argparse
from copy import deepcopy
from hashlib import file_digest
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from contracts.timeline import resolve
from ui.adapter import compile_conversation
from ui.adapter import MOTION as DEFAULT_DURATIONS
from ui.components import clusters
from ui.tracks import loop_layers


# Durations belong to the interaction renderer. Distinct catalog previews
# may illustrate a different implementation of the same observable action.
EVENTS = {
    "composer-type": ("draft",),
    "draft-send-flight": ("send",),
    "typing-indicator-cycle": ("typing",),
    "reply-makes-room": ("receive",),
    "delivery-receipt-handoff": ("send", "receipt"),
    "edit-message-reflow": ("edit",),
    "undo-send-remove": ("unsend",),
    "reaction-attach": ("overlay", "reaction"),
    "long-press-actions": ("overlay",),
    "keyboard-focus-reflow": ("focus",),
    "app-drawer": ("overlay",),
    "photos-under-fixed-heading": ("media.page",),
    "conversation-handoff": ("draft", "send", "receive"),
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    with path.open("rb") as handle:
        return file_digest(handle, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def select_events(document, motion, binding):
    require(motion in EVENTS, f"{motion} needs authored production bindings. Its catalog preview remains playable.")
    require(isinstance(binding, dict) and set(binding) == {"events"}, "Binding needs an events array")
    changes = binding["events"]
    require(isinstance(changes, list) and changes, "Name one or more existing event IDs")
    known = {event["id"]: event for event in document.get("events", [])}
    selected = []
    for change in changes:
        require(isinstance(change, dict) and "id" in change and set(change) <= {"id", "frame", "durationFrames"},
                "An event binding takes id, frame and durationFrames")
        event = known.get(change["id"])
        require(event is not None, f"Unknown conversation event {change['id']}")
        for field in ("frame", "durationFrames"):
            if field in change:
                require(type(change[field]) is int and change[field] >= 0, f"{field} must be a nonnegative integer")
                event[field] = change[field]
        selected.append(event)
    require(len({event["id"] for event in selected}) == len(selected), "An event can only be bound once")
    kinds = tuple(event["kind"] for event in selected)
    if motion == "composer-type":
        require(len(kinds) >= 2 and set(kinds) == {"draft"}, "Bind at least two consecutive draft revisions")
        values = [list(clusters(event["text"])) for event in selected]
        require(all(len(a) < len(b) and a == b[:len(a)] for a, b in zip(values, values[1:])),
                "Draft revisions must grow by complete graphemes")
    else:
        require(kinds == EVENTS[motion], f"{motion} needs these event kinds in order: {', '.join(EVENTS[motion])}")
    frames = [event["frame"] for event in selected]
    require(all(a < b for a, b in zip(frames, frames[1:])), "Bound events must advance through the picture")
    if motion in {"long-press-actions", "reaction-attach", "app-drawer"}:
        require(selected[0]["surface"] == ("tray" if motion == "app-drawer" else "context"),
                "The selected action uses a different interface surface")
    if motion == "reaction-attach":
        require(selected[0]["messageId"] == selected[1]["messageId"], "Context and reaction must share a message")
    if motion == "delivery-receipt-handoff":
        require(selected[0]["message"]["id"] == selected[1]["messageId"], "The receipt must follow the selected send")
    if motion == "typing-indicator-cycle":
        require(selected[0]["active"], "Bind the frame where a remote sender starts typing")
    if motion == "keyboard-focus-reflow":
        require(selected[0]["focused"], "Bind the frame that opens the keyboard")
    document["events"].sort(key=lambda event: event["frame"])
    if motion == "composer-type":
        interval = [event for event in document["events"] if frames[0] <= event["frame"] <= frames[-1]]
        require(interval == selected, "Typing revisions must be consecutive on the conversation timeline")
    return selected


def authored_change(layer, property, first, last, fps):
    tracks = layer.get("keyframes", {}).get(property, [])
    start = next((key["value"] for key in reversed(tracks) if round(key["t"] * fps) <= first),
                 layer.get(property, 0))
    return any(first < round(key["t"] * fps) <= last and key["value"] != start for key in tracks)


def layer_check(scene, motion, selected):
    by_id = {entry["id"]: entry for entry in scene["timeline"]["events"]}
    layers = {layer["id"]: layer for layer in loop_layers(scene["layers"])}
    for id in ("ui.header", "ui.composer", "ui.transcript"):
        require(id in layers, f"Missing component {id}")
    state = scene["timeline"]["initialUI"]
    before = {}
    for entry in scene["timeline"]["events"]:
        before[entry["id"]] = state
        state = entry.get("uiState", state)
    if motion == "delivery-receipt-handoff":
        prior_messages = before[selected[0]["id"]]["messages"]
        previous = [message for message in prior_messages if message["receipt"]]
        require(previous, "A receipt handoff needs an earlier receipt in the thread")
    rows = []
    for action in selected:
        entry = by_id[action["id"]]
        prior = before[entry["id"]]
        target = entry["target"]
        require(all(id in layers for id in entry["layerIds"]), f"Unresolved component for {entry['id']}")
        require(prior != entry.get("uiState"), f"{entry['id']} does not change the selected conversation state")
        fps = scene["fps"]
        duration = action.get("durationFrames", round(DEFAULT_DURATIONS[action["kind"]] * fps / 24))
        first = entry["frame"]
        last = first + max(1, duration) - 1
        require(last < scene["timeline"]["picture"]["frameCount"],
                f"{entry['id']} needs its complete motion interval through frame {last}")
        if action["kind"] == "send" and motion in {"draft-send-flight", "conversation-handoff"}:
            prior_draft = prior["composer"]["text"]
            resulting = next(message["text"] for message in entry["uiState"]["messages"] if message["id"] == target)
            require(prior_draft.strip() and prior_draft == resulting, "The send needs the same message visibly drafted first")
            if motion == "draft-send-flight":
                require(authored_change(layers[entry["layerIds"][0]], "y", first, last, fps),
                        "A send flight needs an outgoing bubble that travels after the send. Use an ordinary send for a cut.")
        if motion == "keyboard-focus-reflow":
            require(not prior["composer"]["keyboardVisible"] and entry["uiState"]["composer"]["keyboardVisible"],
                    "Keyboard must open from a hidden state")
        if motion == "photos-under-fixed-heading":
            rail = f"ui.message/{target}/rail"
            require(f"ui.message/{target}/media" in layers and f"ui.message/{target}/rail" in layers,
                    "The selected message does not supply an attachment rail")
            require(authored_change(layers[rail], "x", first, last, fps),
                    "A sliding rail needs intermediate motion. Use page selection for an immediate change.")
        if motion == "reply-makes-room":
            require(authored_change(layers["ui.transcript"], "y", max(0, first - 1), last, fps),
                    "A reply makes room when prior rows move. Use an ordinary receive for a short thread.")
        if motion == "typing-indicator-cycle":
            dots = ["ui.typing.dot.1", "ui.typing.dot.2", "ui.typing.dot.3"]
            cycle_end = min(
                first + fps, scene["timeline"]["picture"]["frameCount"] - 1,
                next((e["frame"] - 1 for e in scene["timeline"]["events"] if e["frame"] > first and "uiState" in e
                      and target not in e["uiState"]["typingSenderIds"]), first + fps),
            )
            require(all(dot in layers and authored_change(layers[dot], "opacity", first, cycle_end, fps)
                        for dot in dots), "A typing cycle needs a profile with animated dots in the selected window")
        rows.append({"id": entry["id"], "frame": entry["frame"], "roleLayers": entry["layerIds"]})
    return rows


def bind(motion, source, binding, output):
    require(not output.exists(), f"Choose a new output directory: {output}")
    original = read(source)
    edited = deepcopy(original)
    selected = select_events(edited, motion, binding)
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".motion-", dir=output.parent) as scratch:
        stage = Path(scratch) / output.name
        stage.mkdir()
        paths = edited.get("assets", {})
        require(isinstance(paths, dict), "assets must map IDs to local image paths")
        reserved = {"scene.json", "conversation.json", "events.json", "motion.json", "fonts"}
        for relative in paths.values():
            asset = Path(relative)
            require(asset.parts and not asset.is_absolute() and ".." not in asset.parts and asset.parts[0] not in reserved,
                    f"Use a portable conversation asset path: {relative}")
            destination = stage / asset
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                shutil.copyfile(source.parent / asset, destination)
        scene = compile_conversation(edited, input_dir=stage, output_dir=stage)
        roles = layer_check(scene, motion, selected)
        fonts = stage / "fonts"
        fonts.mkdir()
        notices = set()
        for font in scene["fonts"]:
            original_font = (stage / font["src"]).resolve()
            shutil.copyfile(original_font, fonts / original_font.name)
            font["src"] = f"fonts/{original_font.name}"
            with TTFont(original_font) as face:
                notice = face["name"].getDebugName(13)
                if notice:
                    notices.add(notice)
        if notices:
            (fonts / "LICENSE.txt").write_text("\n\n".join(sorted(notices)) + "\n", encoding="utf-8")
        write(stage / "conversation.json", edited)
        write(stage / "scene.json", scene)
        write(stage / "events.json", resolve(scene))
        last = min(scene["timeline"]["picture"]["frameCount"] - 1, max(
            event["frame"] + max(1, event.get("durationFrames", round(DEFAULT_DURATIONS[event["kind"]] * scene["fps"] / 24))) - 1
            for event in selected
        ))
        first = max(0, selected[0]["frame"] - 1)
        validation = subprocess.run(
            ["node", "--input-type=module", "-e", """
import {readFileSync} from 'node:fs';
import {inferAdapterBindings, validateMotionBinding} from './components.mjs';
const [motion, path, rawIds, rawWindow] = process.argv.slice(1);
const scene = JSON.parse(readFileSync(path, 'utf8'));
const eventIds = JSON.parse(rawIds);
const window = JSON.parse(rawWindow);
const bindings = inferAdapterBindings(motion, scene, eventIds);
const verification = validateMotionBinding(motion, {scene, bindings, eventIds, window});
console.log(JSON.stringify({bindings, verification, window}));
""", motion, str(stage / "scene.json"), json.dumps([event["id"] for event in selected]),
             json.dumps([first, last]) if first < last else "null"],
            cwd=ROOT / "motion", capture_output=True, text=True,
        )
        require(validation.returncode == 0, validation.stderr.strip() or "Could not check motion bindings")
        mapped = json.loads(validation.stdout)
        require(mapped["verification"]["ok"], json.dumps(mapped["verification"]["issues"]))
        proof = {
            "id": motion, "sourceSHA256": digest(source), "sceneSHA256": digest(stage / "scene.json"),
            "events": roles, **mapped, "status": "compiled-messages-interaction",
        }
        write(stage / "motion.json", proof)
        stage.rename(output)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("motion")
    parser.add_argument("source", type=Path)
    parser.add_argument("--binding", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        proof = bind(args.motion, args.source.resolve(), read(args.binding), args.out.resolve())
        print(json.dumps({**proof, "scene": str(args.out / "scene.json")}, indent=2))
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
