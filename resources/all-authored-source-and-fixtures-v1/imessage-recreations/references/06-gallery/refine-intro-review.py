from pathlib import Path
import ast,json,numpy as np
from PIL import Image
from scipy import signal,ndimage
from functools import lru_cache
R=Path('/workspace/imessage-recreations');REF=R/'references/06-gallery';P=R/'verification/fidelity-review/06-intro';AS=REF/'assets/intro-review'
# Load only pure measurement functions, never replay the full authoring pipeline.
names={'frame','box','ink','energy','match','fit'};tree=ast.parse((REF/'build-intro-review.py').read_text());exec(compile(ast.Module(body=[q for q in tree.body if isinstance(q,ast.FunctionDef) and q.name in names],type_ignores=[]),'pure-intro-functions','exec'),globals())
s=json.loads((REF/'intro-review-elements.json').read_text());group=s['insert_before']['g-1129'][0];nodes={q['id']:q for q in group['children']};log=[]
configs=[('marcus',69,[704,604,1109,682]),('priya',69,[704,774,1176,850]),('dan',69,[704,940,1125,1018]),('rene',99,[704,900,1128,981])]
for name,cf,tb in configs:
 n=nodes['rene-intro-'+name];cb=n['sourceBounds'];raw=ink(frame(cf)[tb[1]:tb[3],tb[0]:tb[2]]);bb=box(raw>.08);A=raw[bb[1]:bb[3],bb[0]:bb[2]];tx=tb[0]+bb[0];ty=tb[1]+bb[1];obs=s['measurements'][name]
 for f in [105,106,107]:
  q=fit(f,A,[590,200,1300,1080],1,spread=.025);assert q and q['score']>.85,(name,f,q)
  obs.append(dict(frame=f,correlation=q['score'],x=q['x']+q['sx']*(cb[0]-tx),y=q['y']+q['sy']*(cb[1]-ty),scaleX=q['sx'],scaleY=q['sy'],opacity=q['alpha']));log.append([name,f,q['score']])
 # Partial first-line matching recovers genuine message arrival below the viewport.
 if name in ['dan','rene']:
  partial=A[:round(A.shape[0]*.45)];lo=54 if name=='dan' else 76;hi=58 if name=='dan' else 84
  for f in range(lo,hi):
   q=fit(f,partial,[590,850,1300,1080],1.0,spread=.045)
   if q and q['score']>.88 and q['alpha']>.05:
    obs.append(dict(frame=f,correlation=q['score'],partialTemplate=True,x=q['x']+q['sx']*(cb[0]-tx),y=q['y']+q['sy']*(cb[1]-ty),scaleX=q['sx'],scaleY=q['sy'],opacity=q['alpha']));log.append([name,f,q['score']])
 obs.sort(key=lambda q:q['frame']);n['start']=obs[0]['frame']/30;n['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','opacity']}
# A specific chevron provides the physical Y when the top bezel is clipped at105–107.
a=frame(69);b=[610,250,680,350];raw=a[b[1]:b[3],b[0]:b[2]];bb=box(raw.max(2)<90);assert bb;referenceY=b[1]+bb[1]
for q in s['measurements']['post-camera']:
 f=q['frame'];sc=q['scaleX'];xl=round(q['x']+610*sc);xr=round(q['x']+680*sc);a=frame(f);m=a[:500,max(0,xl):min(1920,xr)].max(2)<90;lab,num=ndimage.label(m);cands=[]
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if 25*sc<h<95*sc and 10*sc<w<65*sc:cands.append([h,yy.start])
 if cands:q['y']=max(cands)[1]-referenceY*sc;q['sourceChevronTop']=max(cands)[1]
for id in ['rene-intro-postcut-hardware','rene-intro-postcut-header']:
 n=nodes[id];bx,by=n['sourceBounds'][:2];n['keyframes']['y']=[dict(t=q['frame']/30,value=q['y']+by*q['scaleY'],ease='linear') for q in s['measurements']['post-camera']]
s['measurements']['refinement']=log;(REF/'intro-review-elements.json').write_text(json.dumps(s,indent=2));print(log);print('camera107',s['measurements']['post-camera'][-1])
