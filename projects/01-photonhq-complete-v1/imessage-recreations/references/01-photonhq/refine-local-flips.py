"""Only brief per-card source deformation textures; not a complete-frame sequence."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,hashlib
R=Path('/workspace/imessage-recreations/references/01-photonhq');M=R/'assets/flip-measure';A=R/'assets/local-flip-art';scene=json.loads((R/'scene-final-v4.json').read_text());ledger=[];new=[];intervals=[(282/30,297/30),(315/30,336/30)]
def materials(a):
 r,g,b=[a[:,:,i]/255 for i in range(3)];lo=a.min(2)/255;hi=a.max(2)/255
 return [('gray',(lo>.73)&(hi<.982)&((hi-lo)<.055)),('calls',hi<.68),('sms',(g>.76)&(r<.9)&(b<.95)&(g-r>.15)&(g-b>.10))]
for p in sorted(M.glob('source-*.png')):
 n=int(p.stem.split('-')[-1]);a=np.array(Image.open(p).convert('RGB'));components=[]
 for cls,mask in materials(a):
  mask[450:640]=False;mask=ndimage.binary_closing(mask,iterations=1);lab,num=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel())
  for li,sl in enumerate(ndimage.find_objects(lab),1):
   if not sl:continue
   y,x=sl;w=x.stop-x.start;h=y.stop-y.start;area=areas[li]
   if not((area>700 and w>65 and h>6) or ((y.start<3 or y.stop>1077) and area>120 and w>30)):continue
   if w/h<1.6 and not(x.start<3 or x.stop>1917):continue
   box=(max(0,x.start-20),max(0,y.start-20),min(1920,x.stop+20),min(1080,y.stop+20));components.append((box,cls,area))
 # Largest outer card precedes its smaller interior components; redundant exact-source overdraw is harmless.
 components.sort(key=lambda z:-(z[0][2]-z[0][0])*(z[0][3]-z[0][1]));kept=[]
 for b,cls,area in components:
  if any(q[0]<=b[0] and q[1]<=b[1] and q[2]>=b[2] and q[3]>=b[3] for q in kept):continue
  kept.append(b);tile=a[b[1]:b[3],b[0]:b[2]];digest=hashlib.sha256(tile.tobytes()).hexdigest()[:16];dest=A/f'{digest}.png';Image.fromarray(tile).save(dest);node=dict(id=f'local-flip-{n}-{len(kept)}',type='image',src='assets/local-flip-art/'+dest.name,x=b[0],y=b[1],width=b[2]-b[0],height=b[3]-b[1],start=n/30,end=(n+1)/30,sourceFrame=n,sourceBounds=list(b),editability='Brief original individual card deformation texture; native independent placement and frame timing; bitmap card copy and3D appearance.');new.append(node);ledger.append(dict(id=node['id'],sourceFrame=n,sourceBounds=list(b),material=cls,asset=node['src']))
# Keep existing measured static cards everywhere outside these two short local deformation windows.
body=[];other=[]
for l in scene['layers']:
 if l['id'].endswith('-local-flip-gate') and l.get('children'):l=l['children'][0]
 if l['id'].startswith(('ocr-wall-','edge-restore-')):
  track=[dict(t=0,value=1)]
  for st,en in intervals:track.extend([dict(t=st,value=0,ease='hold'),dict(t=en,value=1,ease='hold')])
  body.append(dict(id=l['id']+'-local-flip-gate',type='group',children=[l],keyframes={'opacity':track}))
 elif not l['id'].startswith('local-flip-'):other.append(l)
scene['layers']=body+new+other;scene['source']['notes']+=' Brief9.4–9.9 and10.5–11.2 individual card deformation textures reproduce local unreadable3D flips. Source bounds/frame recorded per card. No whole source frames or source video layers. Native headings and other measured static artwork/motion remain separate.'
# Roll the incoming native counter through the unreadable flip instead of leaving the numeral absent.
for l in scene['layers']:
 if l['id']=='source-heading-word-calls-0':
  first=min(q['t'] for q in l['keyframes']['scaleX'] if q['t']>10.8);l['start']=10.7
  for k in ['x','y','scaleX','scaleY']:
   value=l['keyframes'][k][0]['value'];l['keyframes'][k]=[dict(t=10.7,value=value)]+l['keyframes'][k]
  l['keyframes']['opacity']=[dict(t=10.7,value=0),dict(t=10.766667,value=.8)]+[q for q in l['keyframes']['opacity'] if q['t']>=first];l['keyframes']['blur']=[dict(t=10.7,value=13),dict(t=10.8,value=8),dict(t=first,value=0)]
(R/'scene-final-v4.json').write_text(json.dumps(scene,indent=2));(R/'local-flip-provenance.json').write_text(json.dumps(dict(intervals=intervals,editability='Independent card sprite poses for brief original3D deformations; native layout, timing and headings. Not editable3D geometry or live bitmap copy.',cards=ledger),indent=2));print('Localized deformation textures',len(new),'frames',len(set(x['sourceFrame'] for x in ledger)))
