"""Encode selected frame windows and pair the decoded result with the reference."""
import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "project"))
from render import Film

ENCODE = ["-vf", "scale=2000:2000:flags=lanczos,setsar=1", "-c:v", "libx264",
          "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
          "-video_track_timescale", "60000", "-movflags", "+faststart"]
SHOTS = [
    ("Pinned inbox entrance", 0, 9, [0,4,8], (204,280,1550,1500)),
    ("Inbox hold", 10, 41, [11,22,40], (260,360,1480,1470)),
    ("Inbox scroll", 42, 101, [43,52,56,60,62,64,69,95,101], (245,0,1520,2000)),
    ("Identity", 102, 133, [102,106,114,128,133], (540,480,920,1100)),
    ("Glossy handset", 134, 161, [134,135,136,137,138,139,145,154,161], (75,275,1850,1725)),
    ("Personal title", 162, 212, [162,168,180,187,196,201,205,209,212], (340,500,1320,800)),
    ("Dimensional portrait cluster", 213, 253, [213,218,222,226,242,249,253], (85,270,1790,1500)),
    ("Cluster wipe and profile reveal", 254, 281, [254,255,256,257,258,260,262,267,276], (80,275,1810,1420)),
    ("Profile push", 282, 312, [284,287,290,300,308,311], (120,460,1780,1230)),
    ("First phone entrance", 313, 335, [313,316,319,321,327,335], (270,0,1490,2000)),
    ("Suggestion and controls", 336, 359, [336,339,341,343,346,352,355,359], (0,150,2000,1810)),
    ("Isolated suggestion and pointer", 360, 396, [360,371,382,386,389,391,393,394,396], (560,400,1370,1470)),
    ("Calendar entry", 397, 429, [397,400,403,405,408,410,415,420,427], (110,265,1800,1250)),
    ("Violet appointment drag", 430, 451, [430,431,435,437,442,450], (225,490,1650,800)),
    ("Cyan appointment drag", 452, 473, [452,453,455,457,460,470,473], (225,435,1650,965)),
    ("Calendar mosaic and app entry", 474, 486, [474,475,476,477,478,480,483,486], (100,235,1810,1470)),
    ("App orbit", 487, 612, [487,496,530,536,550,567,586,602,612], (340,370,1320,1230)),
    ("App exit", 613, 623, [613,616,619,620,621,622,623], (280,450,1440,1550)),
    ("Second phone entrance", 624, 647, [624,626,630,632,639,647], (300,0,1510,2000)),
    ("Follow-up buttons and push", 648, 674, [648,650,653,659,665,670,674], (230,420,1500,1400)),
    ("Yes contact and withdrawal", 675, 695, [675,676,684,688,691,693,695], (145,185,1720,1540)),
    ("Closing badge entrance", 696, 716, [696,700,703,708,714,716], (570,470,860,900)),
    ("Closing copy and wash", 717, 765, [717,724,732,741,752,761,765], (400,650,1280,880)),
    ("Closing fade and black hold", 766, 777, list(range(766,778)), (0,0,2000,2000)),
]
DENSE = [(53,65),(134,141),(248,264),(313,322),(333,346),(381,402),
         (428,439),(451,460),(474,488),(529,539),(613,633),(648,655),
         (670,690),(707,725),(753,765)]


def segment(task):
    scene, cache, group = task
    film = Film(json.loads(scene.read_text()))
    for f in group:
        film.frame(f).save(cache / f"{f:06d}.png", compress_level=1)


def sheet(out, name, bounds, selected, source, candidate):
    x,y,w,h = bounds
    rect = (x//4, y//4, (x+w)//4, (y+h)//4)
    cell_w, cell_h = 164, 200
    cols = 4
    grid = Image.new("RGB", (cols*2*cell_w, ((len(selected)+cols-1)//cols)*cell_h), "#e9e9ec")
    d = ImageDraw.Draw(grid)
    for i, f in enumerate(selected):
        x0,y0 = (i%cols)*2*cell_w, (i//cols)*cell_h
        for j,(label,folder) in enumerate((("Source",source),("Decoded render",candidate))):
            pic = Image.open(folder/f"{f:06d}.png").crop(rect)
            pic.thumbnail((cell_w-8, cell_h-24))
            x = x0+j*cell_w+4
            d.text((x,y0+4),f"f{f:03d}  {label}",fill="#202023")
            grid.paste(pic,(x,y0+22))
    grid.save(out/f"{name}.jpg",quality=91)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_frames", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--final", type=Path, help="Compare against an already encoded full film")
    p.add_argument("--scene", type=Path, default=ROOT/"project/scene.json")
    p.add_argument("--shot", type=int, action="append", help="Limit to selected 1-based shot numbers")
    args = p.parse_args()
    args.out.mkdir()
    chosen = set(args.shot or range(1,len(SHOTS)+1))
    shots = [(i,s) for i,s in enumerate(SHOTS,1) if i in chosen]
    frames = {f for _,(_,_,_,samples,_) in shots for f in samples}
    for a,b in DENSE:
        if any(a<=end and start<=b for _,(_,start,end,_,_) in shots):
            frames.update(range(a,b+1))
    frames = sorted(frames)
    if not args.final:
        cache = args.out/"native"
        cache.mkdir()
        groups = [frames[i::4] for i in range(4)]
        with ProcessPoolExecutor(max_workers=4) as pool:
            list(pool.map(segment, [(args.scene,cache,group) for group in groups]))
        ordered = args.out/"ordered"
        ordered.mkdir()
        for i,f in enumerate(frames):
            (ordered/f"{i:06d}.png").hardlink_to(cache/f"{f:06d}.png")
        video = args.out/"probe-reel.mp4"
        subprocess.run(["ffmpeg","-nostdin","-v","error","-framerate","25","-i",
                        str(ordered/"%06d.png"),*ENCODE,str(video)], check=True)
    else:
        video = args.final
    decoded = args.out/"review-frames"
    decoded.mkdir()
    subprocess.run(["ffmpeg","-nostdin","-v","error","-i",str(video),"-vf",
                    "scale=500:500:flags=area","-threads","2","-start_number","0",
                    str(decoded/"%06d.png")],check=True)
    assert len(list(decoded.glob("*.png"))) == (778 if args.final else len(frames))
    mapped = args.out/"aligned"
    mapped.mkdir()
    with (args.out/"frame-map.csv").open("w",newline="") as h:
        writer = csv.writer(h)
        writer.writerow(("reel_frame","source_frame","source_seconds","whole_rgb_mae_at_500px"))
        for i,f in enumerate(frames):
            idx = f if args.final else i
            pic = decoded/f"{idx:06d}.png"
            (mapped/f"{f:06d}.png").hardlink_to(pic)
            a = np.asarray(Image.open(args.source_frames/f"{f:06d}.png"),dtype=np.int16)
            b = np.asarray(Image.open(pic),dtype=np.int16)
            writer.writerow((idx,f,f/25,round(float(np.abs(a-b).mean()),4)))
    for i,(name,start,end,samples,rect) in shots:
        label = f"{i:02d}-{name.lower().replace(' ','-')}"
        sheet(args.out,label,(0,0,2000,2000),samples,args.source_frames,mapped)
        dense = sorted(set(samples) | {f for f in frames if start<=f<=end and any(a<=f<=b for a,b in DENSE)})
        if rect != (0,0,2000,2000) or dense != samples:
            sheet(args.out,label+"-detail",rect,dense,args.source_frames,mapped)
    print(f"Decoded {len(frames)} aligned evidence frames across {len(shots)} shots.")


if __name__ == "__main__":
    main()
