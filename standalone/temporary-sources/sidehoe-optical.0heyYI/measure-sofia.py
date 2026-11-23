import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label, find_objects, binary_closing
path=Path('/tmp/sidehoe-hyperframes.wG3QA2')
work=Path('/tmp/sidehoe-optical-path').read_text()
scene=json.loads((Path(work)/'project/scene.json').read_text())
keys={int(row[0]):row[1:] for row in scene['tracks']['sofiaMeasuredCamera']}
def extract(im,box,test,min_h=3,min_w=15):
 x0,y0,x1,y1=map(round,box)
 x0,y0,x1,y1=max(0,x0),max(0,y0),min(1000,x1),min(1000,y1)
 if x1<=x0 or y1<=y0:return []
 a=im[y0:y1,x0:x1].astype(np.int16)
 labels,n=label(binary_closing(test(*np.moveaxis(a,2,0)),iterations=2))
 objs=[]
 for i,(yy,xx) in enumerate(find_objects(labels)):
  h,w=yy.stop-yy.start,xx.stop-xx.start
  if w<min_w or h<min_h:continue
  area=np.count_nonzero(labels[yy,xx]==i+1)
  objs.append((area,x0+xx.start,y0+yy.start,x0+xx.stop,y0+yy.stop))
 return sorted(objs,reverse=True)

def land(im,f):
 x,y,s=keys[f]
 out=[]
 for a,b in ((x-12,x+35*s),(x+365*s,x+400*s+12)):
  a,b=max(0,round(a)),min(1000,round(b))
  cols=np.median(im[320:650,a:b,:],axis=(0,2))
  ix=np.flatnonzero(cols<203)
  out.append((a+ix[0],a+ix[-1]+1) if ix.size else None)
 xx0,xx1=max(0,round(x+40*s)),min(1000,round(x+360*s))
 cols=np.median(im[0:410,xx0:xx1],axis=(1,2))
 hs=np.flatnonzero((cols>=216)&(cols<=248))
 upper=next((q for q in np.split(hs,np.flatnonzero(np.diff(hs)>1)+1) if q.size>44),np.array([]))
 head=upper[-1]+1 if upper.size else None
 ys=max(550,round(y+475*s))
 ys2=min(1000,round(y+690*s))
 a=im[ys:ys2,xx0:xx1].astype(np.int16)
 uniform=((a[:,:,0]>175)&(a[:,:,0]<230)&(a[:,:,2]-a[:,:,0]<33)).mean(axis=1)
 ix=np.flatnonzero(uniform>.74)
 keyboard=ys+int(ix[0]) if ix.size else None
 sz=lambda l,t,h,w:(x+l*s,y+t*s,x+h*s,y+w*s)
 blue=extract(im,sz(115,115,390,312),lambda R,G,B:(R<125)&(B-R>63)&(G>141),10,26)
 glyphs=extract(im,sz(10,165,330,435),lambda R,G,B:(R>=206)&(R<=244)&(B-R<13)&(B-R>=-4)&(np.abs(G-R)<9),8,35)
 gray=[v for v in glyphs if v[1]>x+15*s and v[2]>max(0, (head or y+136*s)+25*s) and v[4]-v[2]<=60*s and v[3]-v[1]>70*s]
 return [out,head,keyboard,(blue[0][1:] if blue else None),[q[1:] for q in sorted(gray[:2],key=lambda q:q[2])]]

rows={}
for f in range(320,353):
 res=[]
 for src in ('source-stage','complete-motion-frames'):
  im=np.asarray(Image.open(path/src/f'{f:06}.png').convert('RGB'))
  res.append(land(im,f))
 rows[f]=res
 if f in range(328,346) or f in (320,324,350,352):print(f,keys[f],res)
(Path(work)/'sofia-landmarks.json').write_text(json.dumps(rows,default=lambda n:int(n),indent=2))
