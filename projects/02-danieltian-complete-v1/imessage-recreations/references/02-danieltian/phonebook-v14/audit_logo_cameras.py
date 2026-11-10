from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;data=json.loads((R/'dense-measurements.json').read_text());logos={q['id']:q for q in json.loads((R/'frame486-layered-details.json').read_text())};rows=[]
for ftext,frame in data.items():
 f=int(ftext);src=np.asarray(Image.open(R/'source-native'/f'{f:06d}.png')).astype(float)
 for q in frame['caps']:
  id=q['id'];l,t,r,b=q['bbox'];z=src[t:b,l:min(r,l+130)];rr,gg,bb=z[:,:,0],z[:,:,1],z[:,:,2]
  if id=='pb-uber-eats':continue
  mask=(rr>gg+45)&(rr>130);yy,xx=np.nonzero(mask)
  if len(xx)<50:continue
  actual=np.array([l+(xx.min()+xx.max())/2,t+(yy.min()+yy.max())/2]);cl,ct,cr,cb=logos[id]['logoCrop'];pred=np.array(q['matrix'])@[(cl+cr)/2,(ct+cb)/2,1];dist=float(np.linalg.norm(pred-actual));rows.append(dict(frame=f,id=id,distance=dist,predicted=pred.tolist(),observed=actual.tolist(),fit=q['fit'],quality=q['quality']))
(R/'logo-camera-audit.json').write_text(json.dumps(rows,indent=2));print('red/pink logo landmarks',len(rows),'worst',sorted(rows,key=lambda q:q['distance'],reverse=True)[:8])
