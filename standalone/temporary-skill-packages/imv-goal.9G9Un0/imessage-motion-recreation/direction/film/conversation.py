"""Build the film's phone insert from the team's editable conversation adapter."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

from PIL import Image, ImageDraw


SKILL_ROOT = Path(__file__).resolve().parents[2]
PANEL_SIZE = (385, 525)
SCREEN_SIZE = (365, 486)
SCREEN_ORIGIN = (10, 23)

# Film lighting grade for the paper skin. Row identity and motion still come
# from the adapter. Geometry, text, and event tracks remain editable.
TONE = {
    "#f6f0e7": "#201d25",
    "#fffaf4": "#2b252f",
    "#2a2631": "#fcf1e9",
    "#655965": "#bfb1bd",
    "#623864": "#246fb8",
    "#e8dbe8": "#47404b",
    "#ded1d0": "#514551",
}


def design_layers(layers, press_time, frame_duration):
    for layer in layers:
        identity = layer["id"].split("@", 1)[0]
        for field in ("fill", "stroke"):
            if isinstance(layer.get(field), str):
                layer[field] = TONE.get(layer[field].lower(), layer[field])
        if identity == "ui.header.badge":
            layer["fill"] = "#874642"
        elif identity == "ui.header.service":
            layer.update(fontSize=15, y=45)
        elif identity == "ui.composer.draft":
            layer.update(fontSize=19, y=16)
        elif identity == "ui.composer.send-label":
            layer.update(text="↑", fontSize=23, y=12, fill="#fcf1e9")
        elif identity == "ui.composer.send" and layer.get("fill") == "#246fb8":
            layer.update(originX=19, originY=14.5)
            scale = [{"t": press_time - frame_duration, "value": 1, "ease": "hold"},
                     {"t": press_time, "value": .81, "ease": "hold"}]
            layer["keyframes"] = {"scaleX": scale, "scaleY": scale}
        design_layers(layer.get("children", []), press_time, frame_duration)


class Conversation:
    def __init__(self, edit, cuts, ui_root):
        sys.path.insert(0, str(ui_root.resolve()))
        sys.path.insert(0, str(SKILL_ROOT / "scripts" / "engines"))
        from ui.adapter import compile_conversation
        import render_pillow

        self.renderer = render_pillow
        self.origin = cuts["phone"]
        self.fps = edit["fps"]
        description = {
            "version": 1,
            "conversationId": "thread.stage-crew",
            "title": edit["conversation"],
            "service": "Keiki agent · iMessage",
            "participants": {"customer": "Operator", "agent.stage-crew": edit["conversation"]},
            "localSenderId": "customer",
            "display": {"width": SCREEN_SIZE[0], "height": SCREEN_SIZE[1], "textSize": 24},
            "fps": self.fps,
            "frameCount": cuts["search"] - self.origin,
            "initial": {"draft": edit["question"], "focused": False},
            "events": [
                {"id": "message.question.send", "kind": "send", "frame": cuts["send"] - self.origin,
                 "durationFrames": 7, "message": {"id": "message.question"}},
                {"id": "message.answer.receive", "kind": "receive", "frame": cuts["reply"] - self.origin,
                 "durationFrames": 6, "message": {"id": "message.answer", "senderId": "agent.stage-crew",
                                                 "text": edit["answer"]}},
            ],
        }
        self.scene = compile_conversation(description, output_dir=Path.cwd())
        graded = copy.deepcopy(self.scene)
        design_layers(graded["layers"], (cuts["send"] - self.origin - 2) / self.fps, 1 / self.fps)
        self.graded = graded
        self.renderer.register_fonts(graded, str(Path.cwd()))

        self.mask = Image.new("L", SCREEN_SIZE)
        ImageDraw.Draw(self.mask).rounded_rectangle((0, 0, 364, 485), 33, fill=255)
        self.shell = Image.new("RGBA", PANEL_SIZE)
        draw = ImageDraw.Draw(self.shell)
        draw.rounded_rectangle((0, 0, 384, 524), 46, fill="#100d14", outline="#7c5a4d", width=2)
        draw.rounded_rectangle((5, 5, 379, 520), 42, outline="#3a2b35", width=2)
        draw.rounded_rectangle((160, 9, 224, 15), 3, fill="#30222e")
        draw.rounded_rectangle((141, 512, 243, 515), 2, fill="#ad9298")

    def panel(self, frame):
        screen = self.renderer.render(self.graded, (frame - self.origin) / self.fps, str(Path.cwd()))
        panel = self.shell.copy()
        panel.paste(screen.convert("RGBA"), SCREEN_ORIGIN, self.mask)
        return panel

    def mapped_events(self):
        for event in self.scene["timeline"]["events"]:
            yield {**event, "frame": event["frame"] + self.origin}
