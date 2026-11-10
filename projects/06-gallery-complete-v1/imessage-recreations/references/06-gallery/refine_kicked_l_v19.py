"""Independent rigid lowercase-l collision/rotation from native silhouette."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
D=Path(__file__).resolve().parent;F=D/'native-late-v19';s=json.loads((D/'scene-soccer-v19.json').read_text());love=next(q for q in s['layers'] if q['id']=='v19-love-measured-letters');path=next(q for q in love['children'] if q['id']=='v19-love-original-l');love['children']=[q for q in love['children'] if q['id']!=path['id']];poses=[];ref=None;previous=None;lastAngle=0.;lastScale=(1,1)
for f in range(891,935):
 a=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).mean(2);mask=a<90;lab,n=label(mask);candidates=[]
 for k,sl in enumerate(find_objects(lab),1):
  if sl is None:continue
  ys,xs=np.where(lab[sl]==k);area=len(xs)
  if area<250:continue
  x=xs+sl[1].start;y=ys+sl[0].start;cov=np.cov(np.c_[x,y].T);ev,vec=np.linalg.eigh(cov)
  if ev[1]<300 or ev[1]/max(.001,ev[0])<12:continue
  candidates.append(dict(x=x,y=y,cx=float(x.mean()),cy=float(y.mean()),ev=ev,vec=vec,box=[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop],area=area))
 predict=np.array([706.5,580.5]) if previous is None else np.array([previous['cx'],previous['cy']])+np.array(previous.get('velocity',[0,0]));q=min(candidates,key=lambda q:np.hypot(q['cx']-predict[0],q['cy']-predict[1])) if candidates else None
 if q is not None and np.hypot(q['cx']-predict[0],q['cy']-predict[1])<220:
  if ref is None:ref=copy.deepcopy(q)
  v=q['vec'][:,1];v0=ref['vec'][:,1];angle=float(np.degrees(np.arctan2(v[1],v[0])-np.arctan2(v0[1],v0[0])));angle+=180*round((lastAngle-angle)/180);lastAngle=angle;cx,cy=q['cx'],q['cy'];clip=q['box'][0]<=1 or q['box'][1]<=1 or q['box'][2]>=1919 or q['box'][3]>=1079
  if clip:
   # Recover the uncut endpoint and full rod center instead of shrinking a
   # partly offscreen component to its visible length.
   if v[0]<0:v=-v
   u=np.array([-v[1],v[0]]);coordinates=np.c_[q['x'],q['y']];length=np.sqrt(12*ref['ev'][1]);along=float(np.max(coordinates@v)-length/2);across=float(np.median(coordinates@u));center=along*v+across*u;cx,cy=map(float,center);sx,sy=lastScale
  else:sx=float(np.sqrt(q['ev'][0]/ref['ev'][0]));sy=float(np.sqrt(q['ev'][1]/ref['ev'][1]));lastScale=(sx,sy)
  velocity=[0.,0.] if previous is None else [cx-previous['cx'],cy-previous['cy']];row=dict(frame=f,cx=cx,cy=cy,x=cx-ref['cx'],y=cy-ref['cy'],sx=sx,sy=sy,rotation=angle,velocity=velocity,observed=True,clipped=clip)
 else:
  if previous is None:continue
  cx,cy=predict;sx,sy=lastScale;row=dict(frame=f,cx=float(cx),cy=float(cy),x=float(cx-ref['cx']),y=float(cy-ref['cy']),sx=sx,sy=sy,rotation=lastAngle,velocity=previous.get('velocity',[0,0]),observed=False,clipped=True)
 previous=row;half=np.sqrt(12*ref['ev'][1])/2+25;row['opacity']=1. if row['cx']+half>0 and row['cx']-half<1920 else 0.;poses.append(row)
node=dict(type='group',id='v19-love-kicked-l',start=891/30,end=935/30,originX=ref['cx'],originY=ref['cy'],children=[path],keyframes={k:[dict(t=p['frame']/30,value=p[v],ease='linear') for p in poses] for k,v in [('x','x'),('y','y'),('scaleX','sx'),('scaleY','sy'),('rotation','rotation'),('opacity','opacity')]});at=next(i for i,q in enumerate(s['layers']) if q['id']==love['id'])+1;s['layers'].insert(at,node);(D/'kicked-l-v19-measurements.json').write_text(json.dumps(poses,indent=2));(D/'scene-soccer-v19.json').write_text(json.dumps(s,indent=2)+'\n');patch=json.loads((D/'soccer-v19-patch.json').read_text());patch['append']=[love if q['id']==love['id'] else q for q in patch['append']];patch['append'].insert(1,node);(D/'soccer-v19-patch.json').write_text(json.dumps(patch,indent=2));print([(p['frame'],round(p['x'],2),round(p['y'],2),round(p['rotation'],2),p['observed']) for p in poses[::5]])
