"""Write exact-index preview images and a local viewer from decoded RGB pairs."""
import json
from pathlib import Path
from shutil import copyfile

from PIL import Image


class FramePairs:
    def __init__(self, output, native_size):
        self.output = output
        self.directory = output / "pairs"
        self.directory.mkdir()
        scale = min(1.0, 720 / max(native_size))
        self.size = tuple(max(1, round(value * scale)) for value in native_size)
        self.frames = []

    def add(self, index, pts, source, render, mae, peak):
        width, height = self.size
        pair = Image.new("RGB", (2 * width, height))
        for x, picture in ((0, source), (width, render)):
            preview = Image.fromarray(picture).resize(self.size, Image.Resampling.LANCZOS)
            pair.paste(preview, (x, 0))
        pair.save(self.directory / f"{index:06d}.jpg", quality=93, subsampling=0)
        self.frames.append({"seconds": str(pts), "mae": round(mae, 6), "exact": peak == 0})

    def finish(self):
        metadata = json.dumps(self.frames, separators=(",", ":"))
        (self.output / "frame-data.js").write_text(f"const frameData = {metadata};\n", encoding="utf-8")
        copyfile(Path(__file__).with_name("pair-viewer.html"), self.output / "index.html")
