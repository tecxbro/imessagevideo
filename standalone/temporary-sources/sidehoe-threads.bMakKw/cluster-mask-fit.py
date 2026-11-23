from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter1d
r=Path(__file__).parent;rr=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
pose=json.loads((r/'cluster-pose.json').read_text())
A=np.asarray(Image.open(rr/'000253.png').convert('RGB'),dtype=float)
out={}
bins={
254:[113,169,238,284,331,368,397,455,531,544,574,619,657,706,756,785,841],
255:[105,173,207,238,284,330,366,397,453,532,544,574,619,656,706,756,784,846],
256:[110,166,203,243,285,332,372,448,456,507,534,571,624,653,704,721,758,784,842],
257:[101,165,203,251,283,348,372,448,507,536,566,622,695,752,828,867],
}
for f,steps in bins.items():
 dx,dy,sx,sy=pose[str(f)]
 Y,X=np.mgrid[:1000,:1000:1]
 U=(X-dx-500)/sx+500;V=(Y-dy-500)/sy+500
 authored=np.stack([map_coordinates(A[:,:,u],[V,U],order=1,cval=253,prefilter=False) for u in range(3)],axis=-1)
 target=np.asarray(Image.open(rr/f'{f:06}.png').convert('RGB'),dtype=float)
 ink=np.max(253-authored,axis=2)
 visible=np.max(253-target,axis=2)
 # Score the axis-aligned wipes only where the unmasked source has a colored actor.
 strength=np.clip(ink-9,0,55)
 confidence=strength*(visible<8)
 rect=[]
 for ya,yb in zip(steps,steps[1:]):
  s0=strength[ya+2:yb-1].sum(axis=0); s1=confidence[ya+2:yb-1].sum(axis=0)
  total=gaussian_filter1d(s0,4)
  lost=gaussian_filter1d(s1,4)/(total+1e-3)
  state=(lost>(.81 if f<257 else .89))&(total>75)
  cols=np.flatnonzero(state)
  for group in np.split(cols,np.flatnonzero(np.diff(cols)>1)+1):
   if len(group)<16:continue
   l,x=int(group[0]),int(group[-1])+1
   if f>=256 and l<40:l=max(0,l-3)
   rect.append([l,int(ya),x,int(yb)])
 print(f,rect)
 out[str(f)]=dict(pose=pose[str(f)],masks=rect)
out['258']=dict(pose=[-423,-2,1,1],survivors=[[215,248,279,281],[241,351,365,523],[0,538,74,623],[0,678,69,793],[230,692,289,742]])
(r/'cluster-wipe.json').write_text(json.dumps(out,indent=2))
