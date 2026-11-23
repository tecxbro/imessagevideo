from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, maximum_filter, minimum_filter
from scipy.optimize import least_squares
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'project'))
from artwork import curved_heart
from render import interpolate
scene=json.loads((ROOT/'project/scene.json').read_text())
tracks=scene['tracks']['personalHearts']
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
texture=np.array(curved_heart(124,124,(247,143,253)).getchannel('A'),float)/255
pink=np.array([247.,143.,253.])
result=[[] for track in tracks]
for f in sorted(set([178,180,182,184,186,188,190,191,192,194,196,198,200,202,204,206,208])):
 base=np.array(Image.open(ROOT/'heart-base'/f'{f:06}.png'),dtype=float)
 target=np.array(Image.open(src/f'{f:06}.png'),dtype=float)
 for group in ((0,1,2),(3,4),(5,6,7,8)):
  seed=np.array([interpolate(tracks[i],f) for i in group],dtype=float)
  mx,my,mw,mh=seed[:,:4].T
  left=int(min(mx-mw*.78)-14); right=int(max(mx+mw*.78)+15)
  top=int(min(my-mh*.78)-14); bottom=int(max(my+mh*.78)+15)
  xi,yi=np.meshgrid(np.arange(left,right,2),np.arange(top,bottom,2))
  a, b=target[yi,xi],base[yi,xi]
  sharp=np.ptp(b,axis=2)
  g=base[:,:,1]
  edge=(maximum_filter(g,size=5)-minimum_filter(g,size=5))[yi,xi]
  match=lambda p:np.stack((p[:,:,0]-p[:,:,1],p[:,:,2]-p[:,:,1],p[:,:,1]),axis=-1)
  actual=match(a)
  weights=np.where(edge>26,.24,1.)[:,:,None]*[1,1,.11]
  allowed=np.abs(a[:,:,2]-b[:,:,2])<140
  weights*=allowed[:,:,None]
  def loss(flat):
   out=b.copy()
   for x,y,w,h,angle,opacity in flat.reshape(-1,6):
    angle=np.deg2rad(angle)
    cos=np.cos(angle);sin=np.sin(angle)
    dx=xi-x;dy=yi-y
    rx=(cos*dx-sin*dy)/w+.5
    ry=(sin*dx+cos*dy)/h+.5
    alpha=(map_coordinates(texture,[ry*123,rx*123],order=1,mode='constant',cval=0,prefilter=False)*opacity)[:,:,None]
    out=out*(1-alpha)+pink*alpha
   d=(match(out)-actual)*weights
   regular=(flat.reshape(-1,6)-seed)*np.array([.95,.95,.60,.60,.18,7])
   return np.concatenate([d.ravel(),regular.ravel()])
  low=seed+[-19,-20,-20,-20,-27,-1]
  high=seed+[19,20,21,21,27,1]
  low[:,2:4]=np.maximum(8,low[:,2:4]);low[:,-1]=.00001
  high[:,-1]=.995
  seed=np.clip(seed,low+.00001,high-.00001)
  sol=least_squares(loss,seed.ravel(),bounds=(low.ravel(),high.ravel()),loss='soft_l1',
     f_scale=8,diff_step=.004,max_nfev=24)
  print(f,group,round(np.mean(np.abs(loss(seed.ravel()))),3),round(np.mean(np.abs(sol.fun)),3),flush=True)
  for k,line in zip(group,sol.x.reshape(-1,6)):
   result[k].append([f,*np.round(line,4).tolist()])
(ROOT/'hearts-fit.json').write_text(json.dumps(result,indent=2))
