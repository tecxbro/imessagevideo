"""The first held-camera fit regressed24 because Chats still overshoots independently.
Measure every sharp word separately through63, retaining native semantic contours.
"""
from pathlib import Path
from functools import lru_cache
import json,copy,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');REF=R/'references/02-danieltian';P=R/'verification/fidelity-review/02-intro';s=json.loads((REF/'intro797-review-elements.json').read_text());by={q['id']:q for q in s['replacement']['children']};rows=[dict(roi=[200,400,1750,550],prefix='intro797-row0-',births=[6,8,11,13]),dict(roi=[150,550,1770,700],prefix='intro797-row1-',births=[15,17,20,22])]
@lru_cache(maxsize=5)
def frame(f):return np.array(Image.open(P/'source'/f'{f+1:04d}.png').convert('RGB')).astype(float)
def alpha(f,b):
 a=frame(f)[b[1]:b[3],b[0]:b[2]];v=(255-a.mean(2))/255;v[a.max(2)-a.min(2)>12]=0;return v

def bb(m,x,y):
 yy,xx=np.where(m);return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+1+x),int(yy.max()+1+y)]
added=[];audit={}
for phase,frames in [('artifact',range(3)),('main',range(6,64))]:
 observations={}
 for f in frames:
  for row in rows:
   live=[i for i,b in enumerate(row['births']) if phase=='artifact' or b<=f]
   if not live:continue
   b=row['roi'];a=alpha(f,b);xs=np.where((a>.5).any(0))[0];inds=sorted(np.argsort(np.diff(xs))[-(len(live)-1):]) if len(live)>1 else [];cuts=[b[0]]+[int((xs[i]+xs[i+1])/2)+b[0] for i in inds]+[b[2]]
   for i,lo,hi in zip(live,cuts,cuts[1:]):
    id=row['prefix']+'word'+str(i);n=by[id];bounds=n['sourceBounds'];cb=[bounds[0]+2,bounds[1]+2,bounds[2]-2,bounds[3]-2];B=bb(a[:,lo-b[0]:hi-b[0]]>.5,lo,b[1]);sx=(B[2]-B[0])/(cb[2]-cb[0]);sy=(B[3]-B[1])/(cb[3]-cb[1]);observations.setdefault(id,[]).append(dict(frame=f,sourceBounds=B,x=B[0]-cb[0]*sx,y=B[1]-cb[1]*sy,scaleX=sx,scaleY=sy))
 for id,obs in observations.items():
  n=copy.deepcopy(by[id]);n['id']=('artifact-' if phase=='artifact' else '')+id;n['start']=obs[0]['frame']/30;n['end']=(3 if phase=='artifact' else 64)/30;n['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY']};added.append(n);audit[phase+'-'+id]=obs
# Late measured group/icons remain untouched; first native entry poses6–23 stay exact.
s['replacement']['children']=[q for q in s['replacement']['children'] if q['id'] not in by or (q['id'] not in ['intro797-artifact','intro797-held'] and not q['id'].startswith(('intro797-row0-','intro797-row1-')))]+added;s['measurements']['all-sharp-words']=audit;s['notice']+=' Independent per-word source bounds continue through63; this avoids interpreting the last arriving Chats overshoot as a whole-title camera.';(REF/'intro797-review-elements.json').write_text(json.dumps(s,indent=2));print('sharp nodes',len(added))
