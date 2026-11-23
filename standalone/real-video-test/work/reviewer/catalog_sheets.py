"""Compose review sheets from every decoded bundled preview and fresh replay."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def sheets(folder):
    reports = [json.loads(line) for line in (folder / 'results.jsonl').read_text().splitlines()]
    groups = [reports[i:i + 7] for i in range(0, len(reports), 7)]
    dest = folder / 'contact-sheets'
    dest.mkdir(exist_ok=True)
    font = ImageFont.load_default(size=15)
    caption = ImageFont.load_default(size=13)
    for page, rows in enumerate(groups, 1):
        grid, row_height = 1425, 209
        canvas = Image.new('RGB', (grid, row_height * len(rows)), '#202733')
        draw = ImageDraw.Draw(canvas)
        for i, r in enumerate(rows):
            sid = r['id']
            pos = i * row_height
            src = folder / sid / 'strip.jpg'
            draw.text((9, pos + 1), f'{sid} — {r["moves"]}', font=font, fill='white')
            draw.text((9, pos + 19), f'{r["fixed"]} | bundled preview above / fresh render below', font=caption, fill='#b9c3d0')
            if src.exists():
                strip = Image.open(src)
                frames = r['sample_frames']
                frame_width, frame_height = 145, 79
                for j, f in enumerate(frames):
                    x = 9 + j * (frame_width + 2)
                    draw.text((x + 2, pos + 35), str(f), font=caption, fill='#b9c3d0')
                    for band, top in enumerate((39, 160)):
                        box = (j * 180, top, (j + 1) * 180, top + 120)
                        frame = strip.crop(box)
                        frame.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)
                        canvas.paste(frame, (x, pos + 50 + band * frame_height))
        canvas.save(dest / f'{page:02d}.jpg', quality=90)


if __name__ == '__main__':
    sheets(Path(sys.argv[1]))
