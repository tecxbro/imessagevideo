#!/usr/bin/env python3
"""Conservative active effect ranges for the native alpha/coordinate corrections.

This reads authored layer lifetimes/opacity, not reference pixels. Off-canvas or
occluded effects may add unnecessary frames, but no active effect is omitted.
"""
import argparse, json, math
from pathlib import Path
from render_pillow import state

def compact(frames):
 result=[]
 for frame in frames:
  if result and frame==result[-1][1]+1: result[-1][1]=frame
  else: result.append([frame,frame])
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--out');a=p.parse_args()
 path=Path(a.scene).resolve();scene=json.loads(path.read_text());count=math.floor(scene['duration']*scene['fps']+.5);ids={'pillow':set(),'motion-canvas':set()}
 def affected(layers,t):
  flags={'pillow':False,'motion-canvas':False}
  for layer in layers:
   s=state(layer,t)
   if t<s.get('start',0) or t>=s.get('end',scene['duration']) or s['opacity']<=0:continue
   has_blur=bool(s.get('blur',0));has_shadow=bool(s.get('shadow'))
   if has_blur:flags['pillow']=True;ids['pillow'].add(s['id'])
   if has_blur or has_shadow:flags['motion-canvas']=True;ids['motion-canvas'].add(s['id'])
   nested=affected(s.get('children',[]),t)
   for method in flags:flags[method]|=nested[method]
  return flags
 frames={m:[] for m in ids}
 for i in range(count):
  flags=affected(scene['layers'],i/scene['fps'])
  for method,hit in flags.items():
   if hit:frames[method].append(i)
 result={'scene':str(path),'frame_count':count,'scope':'Conservative active effects, including unscaled/occluded effects. Pillow: any blur. Motion Canvas: any blur or shadow.','methods':{m:{'affected_frame_count':len(f),'inclusive_ranges':compact(f),'ranges_argument':','.join(f'{a}:{b}' for a,b in compact(f)),'layer_ids':sorted(ids[m])} for m,f in frames.items()}}
 if a.out:Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({m:{k:v for k,v in r.items() if k!='layer_ids'} for m,r in result['methods'].items()}))
if __name__=='__main__':main()
