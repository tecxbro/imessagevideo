"""Fit the portrait's actual gray circular background, including its independent movement between command messages."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/middle-dense';P=R/'middle-refinement.json';p=json.loads(P.read_text());root=p['replacements']['group-1118'];muse=next(l for l in root['children'] if l['id']=='middle-avatar-muse');old=copy.deepcopy(muse);RUN=json.loads((R/'middle-body-runs.json').read_text());seed=[dict(t=int(k)/30,left=v['left'],scale=v['scale']) for k,v in RUN.items()]
def sample(ks,t):
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*f
 return ks[-1]['value']
def state(l,k,t):return sample(l['keyframes'][k],t)
im=np.array(Image.open(muse['children'][0]['src']).convert('RGB')).astype(float);mask=(im.min(2)>170)&(im.max(2)<245)&(im.max(2)-im.min(2)<18);iy,ix=np.where(mask);ib=[ix.min(),iy.min(),ix.max()+1,iy.max()+1];iw=126*(ib[2]-ib[0])/im.shape[1];ih=126*(ib[3]-ib[1])/im.shape[0];ms=[]
for n in range(630,856,3):
 t=n/30
 if not muse['start']<=t<muse['end']:continue
 L=sample([dict(t=q['t'],value=q['left']) for q in seed],t);S=(960-L)/543;left=max(0,int(L-210));right=int(L-10);a=np.array(Image.open(M/f'source-{n:04d}.png').convert('RGB')).astype(float);reg=a[:,left:right];mask=(reg.min(2)>170)&(reg.max(2)<245)&(reg.max(2)-reg.min(2)<18);lab,c=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());valid=[]
 for li,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  y,x=sl;w=x.stop-x.start;h=y.stop-y.start
  if w>50 and h>35 and .6<w/h<1.6 and areas[li]>500:valid.append([x.start+left,y.start,x.stop+left,y.stop])
 if not valid:continue
 target=state(old,'y',t)+63*S;b=min(valid,key=lambda b:abs((b[1]+b[3])/2-target));sx=(b[2]-b[0])/iw;sy=(b[3]-b[1])/ih;y=b[1]
 if b[1]<2:sy=sx;y=b[3]-ih*sy
 if b[3]>1077:sy=sx
 ms.append(dict(t=t,x=float(b[0]-126*ib[0]/im.shape[1]*sx),y=float(y-126*ib[1]/im.shape[0]*sy),scaleX=float(sx),scaleY=float(sy)))
if ms:muse['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']})
p['provenance'].append(dict(kind='dense portrait checkpoint',diagnosis='The portrait moves independently during message birth; deriving it from a future body bottom can put it below the viewport. Fit the actual neutral circular background in the left avatar column.',measurements=ms));P.write_text(json.dumps(p,indent=2));print('Measured native portrait poses',len(ms))
