"""Extract authored head sprites from an evenly spaced transparent portrait atlas."""
import argparse
from pathlib import Path

from PIL import Image

ROWS = [
    ["marie", "sydney", "darla", "eleanor"],
    ["ella", "margot", "danielle", "lisa"],
    ["maria", "rae", "lisa-wink", None],
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("atlas", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    atlas = Image.open(args.atlas).convert("RGBA")
    if atlas.getchannel("A").getextrema() != (0, 255):
        raise ValueError("portrait atlas needs clear background and opaque subjects")
    args.out.mkdir(exist_ok=True)
    for row, names in enumerate(ROWS):
        for col, name in enumerate(names):
            if not name:
                continue
            box=(round(col*atlas.width/4),round(row*atlas.height/3),
                 round((col+1)*atlas.width/4),round((row+1)*atlas.height/3))
            cell=atlas.crop(box)
            bounds=cell.getchannel("A").point(lambda x: 255 if x>=40 else 0).getbbox()
            if not bounds or bounds[2]-bounds[0] < cell.width*.3 or bounds[3]-bounds[1] < cell.height*.35:
                raise ValueError(f"missing or incomplete subject in {name}")
            pic=cell.crop(bounds)
            pic.thumbnail((360,360), Image.Resampling.LANCZOS)
            pic.save(args.out/f"{name}.png", optimize=True)


if __name__ == "__main__":
    main()
