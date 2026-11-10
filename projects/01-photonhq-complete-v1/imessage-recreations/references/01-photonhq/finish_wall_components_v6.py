"""Finish a fresh tracker output: reject nested controls, continue clipped bodies.
Run exactly once after track_wall_cards_v6.py, before refine_wall_v6.py.
"""
import json,hashlib,copy
from pathlib import Path
from PIL import Image
P=Path(__file__).parent;B=P/'wall-v6-measure';ls=json.loads((B/'wall-native-layers.json').read_text());ps=json.loads((B/'wall-card-provenance.json').read_text());records={p['id']:p for p in ps['cards']}
def box_at(l,t):
 d={k:next((q['value'] for q in v if abs(q['t']-t)<1e-7),None)for k,v in l['keyframes'].items()}
 if None in d.values():return None
 return [d['x'],d['y'],d['x']+l['width']*d['scaleX'],d['y']+l['height']*d['scaleY']]
rejected=[];out=[]
for l in ls:
 p=records[l['id']];x1,y1,x2,y2=p['source_bounds'];f=p['source_frame'];t=f/30
 if p['material']!='calls' and f<357:
  if any(records[c['id']]['material']=='calls' and (b:=box_at(c,t)) and x1>=b[0]-3 and y1>=b[1]-3 and x2<=b[2]+3 and y2<=b[3]+3 for c in ls):rejected.append(l['id']);continue
 if p['material']=='gray' and f<357:
  # A white avatar clipped at the viewport has an open contour. Filling only
  # enclosed alpha holes discards its own colored logo, so retain its bounded
  # original white component crop. The crop contains no adjacent component.
  a=Image.open(B/('wall' if f<391 else 'wall-late')/f'{f-(335 if f<391 else 390):03d}.png').convert('RGB').crop(p['source_bounds']);a.save(l['src']);p['sha256']=hashlib.sha256(Path(l['src']).read_bytes()).hexdigest()
 if p['material']=='calls' and (x1<3 or x2>1917):
  # A partial reference cannot be stretched to the current clipped span: the
  # viewport changes what is visible, not the component's internal geometry.
  # Keep uniform scale. Fill only the opaque black middle with native geometry.
  bk={k:[]for k in ['x','y','width','height','opacity']}
  for i,sy in enumerate(l['keyframes']['scaleY']):
   x=l['keyframes']['x'][i]['value'];y=l['keyframes']['y'][i]['value'];h=sy['value']*l['height'];end=x+l['width']*sy['value'];bx=x+h/2 if x2>1917 else 0;w=1920-bx if x2>1917 else end-h/2
   for k,v in [('x',bx),('y',y),('width',max(1,w)),('height',h),('opacity',int(w>0))]:bk[k].append({'t':sy['t'],'value':v,'ease':'hold' if k=='opacity' else 'linear'})
  out.append({'id':l['id']+'-native-clipped-backdrop','type':'rect','fill':'#000000','start':l['start'],'end':l['end'],'keyframes':bk,'editability':'Native opaque continuation of an edge-clipped black capsule; internal artwork retains uniform scale.'})
 out.append(l)
ps['cards']=[p for p in ps['cards'] if p['id'] not in rejected];ps['rejected_enclosed_controls']=rejected
(B/'wall-native-layers.json').write_text(json.dumps(out,indent=2)+'\n');(B/'wall-card-provenance.json').write_text(json.dumps(ps,indent=2)+'\n');print('Rejected enclosed controls',rejected)
