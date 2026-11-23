from pathlib import Path
from PIL import Image
from scipy.ndimage import label, binary_closing, binary_dilation, binary_fill_holes
from scipy.optimize import least_squares
import numpy as np,sys,json
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
cfg=root/'project'/'scene.json';s=json.loads(cfg.read_text())
palette=np.array([(250,192,214),(216,205,247),(200,237,249),(250,235,167),(249,216,167),(249,216,167),
 (216,205,247),(246,178,185),(216,205,247),(200,237,249),(200,237,249),(196,250,202),(250,192,214)])
def frame_pose(x,y,d,opacity,asset,color,rgb,stage):
 r=d/2
 low,top=max(0,int(x-r*1.53)),max(0,int(y-r*1.53))
 hi,bot=min(1000,int(x+r*1.53+1)),min(1000,int(y+r*1.53+1))
 if r<=3 or hi<=low or bot<=top:
  return [x,y,d,d,opacity,None], ('small',)
 X,Y=np.meshgrid(np.arange(low,hi)+.5,np.arange(top,bot)+.5)
 relx=(X-x)/r; rely=(Y-y)/r
 good=(np.hypot(relx,rely)<1.51)
 crop=rgb[top:bot,low:hi]
 chroma=np.max(np.abs(crop-color),axis=2)
 mask=(chroma<12)&good
 lm,count=label(mask)
 if count<=0:return [x,y,d,d,opacity,None],('absent',)
 weights=np.bincount(lm.flatten(),weights=np.exp(-.50*(relx**2+rely**2)).flatten())
 weights[0]=0
 cut=lm==weights.argmax()
 # Ignore the interior boundary made by hair and pose with the outer samples.
 ys,xs=np.where(cut)
 if len(ys)<25:return [x,y,d,d,opacity,None],('sparse',)
 ang=(np.arctan2(Y[cut]-y,X[cut]-x)+np.pi)*(90/(2*np.pi))
 rr=np.hypot(X[cut]-x,Y[cut]-y)
 angles=ang.astype(int).clip(0,89)
 distance=np.full(90,-1.0);np.maximum.at(distance,angles,rr)
 points=[]
 for i in range(90):
  if distance[i]<.49*r: continue
  used=np.flatnonzero(angles==i)
  k=used[np.argmax(rr[used])]
  a,b=X[cut][k],Y[cut][k]
  if a<1.25 or a>998.75 or b<1.25 or b>998.75: continue
  points.append((a,b))
 values=np.array(points)
 if len(points)<21:return [x,y,d,d,opacity,None],('no-arc',len(points))
 def err(v):
  xx,yy,rx,ry=v
  return (np.hypot((values[:,0]-xx)/rx,(values[:,1]-yy)/ry)-1)*r
 sol=least_squares(err,(x,y,r,r),bounds=([x-r*.5,y-r*.50,.55*r,.55*r],[x+r*.5,y+r*.5,1.37*r,1.37*r]),
                   loss='soft_l1',f_scale=1.7,max_nfev=65)
 cx,cy,rx,ry=sol.x
 stage_error=np.median(np.abs(sol.fun))
 if len(points)<45 or stage_error>4 or max(rx/ry,ry/rx)>1.27:
  return [x,y,d,d,opacity,None],('uncertain',round(stage_error,1),len(points))
 # Thresholds find the last opaque inner samples. Recover roughly one antialiased pixel.
 rx+=.9;ry+=.9
 head=None
 if asset:
  in_face=np.hypot((X-cx)/rx,(Y-cy)/ry)<.956
  # Dark hair and most face pixels differ from the colored disk.
  candidate=in_face&(chroma>=32)&(crop.max(axis=2)<253)&(crop.min(axis=2)<190)
  big,n=label(binary_closing(candidate,iterations=2))
  if n:
   histogram=np.bincount(big.ravel());histogram[0]=0
   blob=binary_fill_holes(big==histogram.argmax())
   if blob.sum()>=.11*(rx*ry):
    grown=binary_dilation(blob,iterations=2)&(in_face&(chroma>=17))
    cxlo,cxhi=np.percentile(X[grown],[.20,99.8])
    cylo,cyhi=np.percentile(Y[grown],[.10,99.9])
    expand=max(1.2,min(rx,ry)*.026)
    head=[cxlo-expand,cylo-expand,cxhi+expand,cyhi+expand]
 return np.round([cx,cy,2*rx,2*ry,opacity],3).tolist()+[np.round(head,3).tolist() if head else None], (round(stage_error,3),len(points))
poses={}; errors={}
for f in range(218,254):
 image=np.array(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 group=s['tracks']['clusterEntrance' if f<=226 else 'clusterVisibleDisks']
 opts=[]; fit=[]
 for item,row,color in zip(s['cluster'],group,palette,strict=True):
  rest,error=frame_pose(*interpolate(row,f),item[0],color,image,f)
  opts.append(rest);fit.append(error)
 poses[str(f)]=opts;errors[f]=fit
 if f in (218,220,223,225,226,227,230,240,252,253):
  print(f,[(np.round(row[:4],1).tolist(),row[-1],e) for row,e in zip(opts,fit)])
s['clusterDiskContours']=poses
s['clusterDiskColors']=palette.tolist()
cfg.write_text(json.dumps(s,indent=2)+'\n')
(root/'shape-errors.json').write_text(json.dumps(errors,indent=2)+'\n')
