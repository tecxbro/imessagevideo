"""Compile reusable component revisions and sampled transforms into scene layers."""
from bisect import bisect_left
from copy import deepcopy

from .components import group


def loop_layers(layers):
    for layer in layers:
        yield layer
        yield from loop_layers(layer.get("children", ()))


class Tracks:
    def __init__(self, fps, count):
        self.fps = fps
        self.count = count
        self.values = {}
        self.goals = {}
        self.parts = {}

    def move(self, node, frame, duration, **targets):
        """Sample new motion from the rendered value on the preceding frame."""
        for prop, goal in targets.items():
            if frame >= self.count:
                continue
            key = node["id"], prop
            if key in self.goals and self.goals[key] == goal:
                continue
            self.goals[key] = goal
            baseline = node.get(prop, 1 if prop.startswith("scale") or prop == "opacity" else 0)
            if frame == 0 and duration == 0:
                node[prop] = goal
                continue
            track = self.values.setdefault(key, {})
            earlier = [key for key in track if key < frame]
            previous = max(earlier, default=0)
            start = track[previous] if earlier else baseline
            for key in list(track):
                if key >= frame:
                    del track[key]
            if start == goal and not earlier:
                continue
            if frame:
                track[frame - 1] = start
                track.setdefault(0, baseline)
            for index in range(max(1, min(duration, self.count - frame))):
                progress = min(1, (index + 1) / duration) if duration else 1
                ease = 1 - (1 - progress) ** 3
                track[frame + index] = round(start + (goal - start) * ease, 5)

    def value(self, node, prop, frame):
        track = self.values.get((node["id"], prop), {})
        keys = sorted(track)
        index = bisect_left(keys, frame)
        if index < len(keys) and keys[index] == frame:
            return track[frame]
        fallback = node.get(prop, 1 if prop.startswith("scale") or prop == "opacity" else 0)
        return track[keys[index - 1]] if index else fallback

    def revise(self, node, layers, frame):
        """Keep the parent stable and expose editable geometry in each content revision."""
        key = node["id"]
        previous, active = self.parts.get(key, (None, None))
        if previous == layers:
            return
        if active is not None:
            if active["start"] == frame / self.fps:
                node["children"].remove(active)
            else:
                active["end"] = frame / self.fps
        if layers:
            has_history = any(child["id"].startswith(key + "@") for child in node["children"])
            contents = deepcopy(layers)
            if has_history:
                for layer in loop_layers(contents):
                    layer["id"] += f"@{frame}"
            active = group(f"{key}@{frame}", 0, 0, contents, start=frame / self.fps)
            node["children"].append(active)
        else:
            active = None
        self.parts[key] = deepcopy(layers), active

    def finish(self, layers):
        for node in loop_layers(layers):
            for prop in ("x", "y", "scaleX", "scaleY", "rotation", "opacity"):
                track = self.values.get((node["id"], prop), {})
                if track:
                    node.setdefault("keyframes", {})[prop] = [
                        {"t": frame / self.fps, "value": track[frame], "ease": "hold"}
                        for frame in sorted(track)
                    ]
