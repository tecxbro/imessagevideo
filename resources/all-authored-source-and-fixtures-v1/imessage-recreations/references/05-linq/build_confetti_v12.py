"""Track observed colored particles as native editable vector objects."""
from pathlib import Path
import json,importlib.util,copy
import numpy as np
from scipy.optimize import linear_sum_assignment
D=Path(__file__).resolve().parent;s=json.loads((D/'scene-chess-tap-glow-v12.json').read_text());data={int(k):v for k,v in json.loads((D/'confetti-v12-components.json').read_text()).items()};spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
def classify(c):
 r,g,b=c
 if b>r+15 and g>r+10:return 'blue'
 if g>r+15 and g>b+8:return 'green'
 if r>g+25 and b>g-15:return 'pink'
 return 'gold'
tracks=[]
for f,rows in sorted(data.items()):
 for r in rows:
  x0,y0,x1,y1=r['box'];r.update(frame=f,x=float(x0),y=float(y0),cx=(x0+x1)/2,cy=(y0+y1)/2,colorClass=classify(r['color']))
 active=[t for t in tracks if f-t['rows'][-1]['frame']<=2];cost=np.full((len(active),len(rows)),1e6)
 for i,t in enumerate(active):
  last=t['rows'][-1];vx=vy=0.
  if len(t['rows'])>1:
   prev=t['rows'][-2];dt=last['frame']-prev['frame'];vx=(last['cx']-prev['cx'])/dt;vy=(last['cy']-prev['cy'])/dt
  gap=f-last['frame'];px=last['cx']+vx*gap;py=last['cy']+vy*gap
  for j,r in enumerate(rows):
   distance=np.hypot(r['cx']-px,r['cy']-py)
   if r['colorClass']==last['colorClass'] and distance<55:cost[i,j]=distance+abs(np.log((r['area']+.1)/(last['area']+.1)))*7
 used=set()
 if len(active) and len(rows):
  ii,jj=linear_sum_assignment(cost)
  for i,j in zip(ii,jj):
   if cost[i,j]<80:active[i]['rows'].append(rows[j]);used.add(j)
 for j,r in enumerate(rows):
  if j not in used:tracks.append(dict(id=f'v12-observed-confetti-{len(tracks):03}',rows=[r]))
nodes=[];record=[]
for t in tracks:
 rs=t['rows'];# Each particle keeps one logical native object; shape states
 # preserve its actual tumble while positions/color remain explicit tracks.
 frames={r['frame']:r for r in rs};keys={k:[] for k in ['x','y','d','fill','opacity']}
 for f in range(rs[0]['frame'],rs[-1]['frame']+1):
  r=frames.get(f)
  if r is None:keys['opacity'].append(dict(t=f/30,value=0,ease='hold'));continue
  path,stats=trace.trace_alpha(np.array(r['mask'],np.float32),0,0);color='#'+''.join(f'{int(np.clip(round(c),0,255)):02x}' for c in r['color'])
  for k,v in [('x',r['x']),('y',r['y']),('d',path),('fill',color),('opacity',1)]:keys[k].append(dict(t=f/30,value=v,ease='hold' if k in ['d','opacity'] else 'linear'))
 if not keys['d'] or not keys['d'][0]['value']:continue
 node=dict(type='path',id=t['id'],start=rs[0]['frame']/30,end=(rs[-1]['frame']+1)/30,d=keys['d'][0]['value'],fill=keys['fill'][0]['value'],blur=.22,keyframes=keys,editability='Independent native vector particle with measured position/color/shape/lifetime. No source-frame image asset.');nodes.append(node);record.append(dict(id=t['id'],frames=[r['frame'] for r in rs],colorClass=rs[0]['colorClass']))
g=next(q for q in s['layers'] if q['id']=='g-831');g.update(start=907/30,end=947/30,children=nodes);g['keyframes']={};(D/'confetti-v12-tracks.json').write_text(json.dumps(record,indent=2));(D/'scene-final-v12-prototype.json').write_text(json.dumps(s,indent=2)+'\n');print('tracked',len(nodes),'native particles','observations',sum(len(t['rows']) for t in tracks))
