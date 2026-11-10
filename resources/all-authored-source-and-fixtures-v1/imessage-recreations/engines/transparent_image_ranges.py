#!/usr/bin/env python3
"""Find conservative native MC frames affected by the former implicit Img fill."""
import argparse,json,math
from pathlib import Path
from render_pillow import state,load_image
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--out');a=p.parse_args();path=Path(a.scene).resolve();scene=json.loads(path.read_text());count=math.floor(scene['fps']*scene['duration']+.5);alpha={};ids={}
def affected(layers,t):
 hit=False
 for layer in layers:
  s=state(layer,t)
  if t<s.get('start',0) or t>=s.get('end',scene['duration']) or s['opacity']<=0:continue
  if s['type']=='image' and s.get('fill') not in ('none','transparent'):
   src=s['src']
   if src not in alpha:alpha[src]=load_image(src,str(path.parent)).getchannel('A').getextrema()[0]<255
   if alpha[src]:hit=True;ids[s['id']]=src
  if affected(s.get('children',[]),t):hit=True
 return hit
frames=[i for i in range(count) if affected(scene['layers'],i/scene['fps'])];ranges=[]
for f in frames:
 if ranges and f==ranges[-1][1]+1:ranges[-1][1]=f
 else:ranges.append([f,f])
result={'scene':str(path),'frame_count':count,'affected_frame_count':len(frames),'inclusive_ranges':ranges,'ranges_argument':','.join(f'{first}:{last}' for first,last in ranges),'transparent_image_layers':ids,'scope':'Conservative active transparent-image intervals; ignores occlusion/off-canvas cancellation, so extra frames may be included.'}
if a.out:Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='transparent_image_layers'}))
