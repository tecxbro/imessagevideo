"""Rasterize evaluated SVG frames on FFmpeg builds without librsvg."""
from pathlib import Path
import sys

import cairosvg


if __name__ == "__main__":
    folder = Path(sys.argv[1])
    first, last = (int(value) for value in sys.argv[2:])
    for frame in range(first, last + 1):
        source = folder / f"{frame:08d}.svg"
        cairosvg.svg2png(bytestring=source.read_bytes(), write_to=str(source.with_suffix(".png")))
