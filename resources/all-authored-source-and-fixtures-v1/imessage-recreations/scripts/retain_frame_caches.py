#!/usr/bin/env python3
"""Retain in-progress lossless intermediates by hardlink so targeted fixes stay cheap."""
from pathlib import Path
import argparse,time,json,os

p=argparse.ArgumentParser();p.add_argument('--seconds',type=int,default=1800);a=p.parse_args()
out=Path(__file__).resolve().parents[1]/'outputs/retained-frames';out.mkdir(parents=True,exist_ok=True)
until=time.monotonic()+a.seconds;counts={}
while time.monotonic()<until:
    for prefix in ['measured-frames-','remotion-measured-frames-']:
        for source in Path('/tmp').glob(prefix+'*'):
            pngs=list(source.glob('*.png'))
            if not pngs:continue
            dest=out/source.name;dest.mkdir(exist_ok=True)
            for f in pngs:
                try:os.link(f,dest/f.name)
                except FileExistsError:pass
                except FileNotFoundError:pass
            counts[source.name]=len(list(dest.glob('*.png')))
    (out/'inventory.json').write_text(json.dumps({'notice':'Raw retained iteration frames, not final deliveries. Map to a verified engine/scene before reuse.','directories':counts},indent=2))
    time.sleep(4)
print(json.dumps(counts))
