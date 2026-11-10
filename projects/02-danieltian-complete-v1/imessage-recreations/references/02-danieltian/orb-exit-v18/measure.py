from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from scipy import ndimage
D=Path(__file__).resolve().parent;REF=D.parent;cached=json.loads((REF/'v17-refinement/group-1118.json').read_text());ids=['middle-avatar-how-about','middle-avatar-airbnb-booked'];nodes={n['id']:n for n in cached['children']if n['id']in ids}
def sample(n,k,f):
 a=n['keyframes'][k];t=f/30
 if t<=a[0]['t']:return a[0]['value']
 for l,r in zip(a,a[1:]):
  if t<=r['t']:return l['value']+(r['value']-l['value'])*(t-l['t'])/(r['t']-l['t'])
 return a[-1]['value']
measures=[];replacements={}
for identity,node in nodes.items():
 img=node['children'][0];rgba=np.asarray(Image.open(img['src']).convert('RGBA')).astype(float);red=(rgba[:,:,0]-rgba[:,:,1]>40)&(rgba[:,:,2]-rgba[:,:,1]>10)&(rgba[:,:,3]>60);y,x=np.nonzero(red)
 local=np.array([x.min(),y.min(),x.max()+1,y.max()+1],float);local[[0,2]]*=img['width']/rgba.shape[1];local[[1,3]]*=img['height']/rgba.shape[0];local[[0,2]]+=img.get('x',0);local[[1,3]]+=img.get('y',0)
 new=copy.deepcopy(node)
 for f in range(1020,1024):
  a=np.asarray(Image.open(REF/'assets/middle-every-frame'/f'source-{f:04d}.png').convert('RGB')).astype(float);mask=(a[:,:,0]-a[:,:,1]>40)&(a[:,:,2]-a[:,:,1]>10);mask[:,:400]=False;mask[:,610:]=False
  labels,count=ndimage.label(mask);objects=[]
  for lab,slice in enumerate(ndimage.find_objects(labels),1):
   if slice is None:continue
   yy,xx=slice;pixels=np.sum(labels[slice]==lab)
   if pixels<100:continue
   objects.append([xx.start,yy.start,xx.stop,yy.stop,int(pixels)])
  expectedY=sample(node,'y',f)+63*sample(node,'scaleY',f);near=[q for q in objects if abs((q[1]+q[3])/2-expectedY)<100];box=max(near,key=lambda q:q[4])[:4];sx=(box[2]-box[0])/(local[2]-local[0]);sy=(box[3]-box[1])/(local[3]-local[1]);pose={'x':float(box[0]-local[0]*sx),'y':float(box[1]-local[1]*sy),'scaleX':float(sx),'scaleY':float(sy)}
  measures.append({'id':identity,'frame':f,'sourceColorBounds':box,'assetLogicalColorBounds':local.tolist(),'pose':pose,'originalPose':{k:sample(node,k,f)for k in pose}})
  if f in[1021,1022]:
   for k,v in pose.items():
    key=next(q for q in new['keyframes'][k]if round(q['t']*30)==f);key['value']=v
 replacements[identity]=new
(D/'patch-spec.json').write_text(json.dumps({'replacements':replacements,'measurements':measures,'changedFrames':[1021,1022],'diagnosis':'Two isolated Airbnborb keys selected a partial pink component and shrank both provider avatars. Full connected pink silhouette in bounded independent provider region restores each authentic static asset, while preserving all neighboring poses.'},indent=2));print(json.dumps(measures,indent=2))
