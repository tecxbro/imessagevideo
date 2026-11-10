#!/usr/bin/env python3
"""Retain an already-running native MC PNG sequence without interrupting it."""
import argparse,json,os,shutil,time,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--temporary',required=True);p.add_argument('--destination',required=True);p.add_argument('--scene',required=True);p.add_argument('--out',required=True);a=p.parse_args();src=Path(a.temporary);dest=Path(a.destination).resolve();dest.mkdir(parents=True,exist_ok=True);scene=Path(a.scene).resolve();s=json.loads(scene.read_text());count=round(s['duration']*s['fps']);done=set();last=-1
while len(done)<count:
 for frame in range(count):
  if frame in done:continue
  f=src/f'{frame:06d}.png';target=dest/f.name
  if not f.exists():continue
  try:
   data=f.read_bytes()
   if not data.startswith(b'\x89PNG') or b'IEND' not in data[-12:]:continue
   if target.exists():target.unlink()
   try:os.link(f,target)
   except OSError:target.write_bytes(data)
   done.add(frame)
  except FileNotFoundError:pass
 if len(done)!=last:print(json.dumps({'retained_frames':len(done),'total':count,'destination':str(dest)}),flush=True);last=len(done)
 if not src.exists() and len(done)<count:raise RuntimeError('Temporary sequence disappeared before complete retention')
 if len(done)<count:time.sleep(.5)
meta=Path(a.out+'.render.json')
while not meta.exists():time.sleep(1)
m=json.loads(meta.read_text());m['frameDirectory']=str(dest);m['retention']='Native PNGs retained by hardlink/copy before temporary cleanup; no video decoding';tmp=meta.with_name(meta.name+'.tmp-retain');tmp.write_text(json.dumps(m,indent=2)+'\n');tmp.replace(meta);(dest/'native-cache.json').write_text(json.dumps({'width':s['width'],'height':s['height'],'fps':s['fps'],'frames':count,'scene':str(scene),'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'native_png_retention':True},indent=2)+'\n');print('Native cache retention complete',flush=True)
