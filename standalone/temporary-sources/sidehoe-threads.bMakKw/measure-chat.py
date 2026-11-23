from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects, binary_closing
import json
root=Path(__file__).parent
m=json.loads((root/'measurements.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-reveal-clean.DeKHma/frames')
def blocks(q,box,mask,wh):
 l,t,r,b=box
 img=q[t:b,l:r].astype(np.int16)
 R,G,B=np.moveaxis(img,2,0)
 labs,n=label(binary_closing(mask(R,G,B),iterations=1))
 out=[]
 for i,(yy,xx) in enumerate(find_objects(labs),1):
  if xx.stop-xx.start<wh[0] or yy.stop-yy.start<wh[1]:continue
  a=l+xx.start; c=l+xx.stop; d=t+yy.start; e=t+yy.stop
  v=np.asarray(q[d:e,a:c])
  region=labs[yy,xx]==i
  n=region.sum()
  if n<280:continue
  vals=np.median(v[region],axis=0)
  out.append((n,[a,d,c,e],np.rint(vals).astype(int).tolist()))
 return sorted(out,key=lambda k:k[1][1])
def spans(q,b,mode):
 a,d,c,e=b
 x0=a+20; x1=c-18
 y0=d+13; y1=e-11
 im=q[y0:y1,x0:x1].astype('int16')
 R,G,B=np.moveaxis(im,2,0)
 if mode=='blue':mask=(R>140)&(B>224)&(G>210)
 else:mask=(R<145)&(abs(R-G)<13)&(abs(R-B)<14)
 yy=np.flatnonzero(mask.sum(axis=1)>2)
 out=[]
 for zz in np.split(yy,np.flatnonzero(np.diff(yy)>3)+1):
  if zz.size<7:continue
  xx=np.flatnonzero(mask[zz].sum(axis=0)>2)
  if not xx.size:continue
  out.append([int(x0+xx[0]),int(y0+zz[0]),int(x0+xx[-1]+1),int(y0+zz[-1]+1)])
 return out
def measure(q,f):
 d=m[str(f)][0];x,y,s,ky=d['est']; follow=f>=624
 # Camera fitting masks drawn optical or only flat source values inside each viewport.
 left=max(0,round(x+18*s)); right=min(1000,round(x+380*s))
 box=(left,0,right,min(1000,ky-96))
 gray=blocks(q,box,lambda R,G,B:(R>=221)&(R<=240)&(abs(R-G)<9)&(abs(R-B)<13),(88,29))
 if follow:
  blue=blocks(q,box,lambda R,G,B:(R>168)&(R<235)&(B-R>14)&(G-R>10),(92,36))
 else:
  blue=blocks(q,box,lambda R,G,B:(R<140)&(G>155)&(B>218),(92,22))
 def result(actors,typ):
  return [(b,c,spans(q,b,typ)) for _,b,c in actors if b[3]-b[1]<165]
 return [result(gray,'gray'),result(blue,'blue')]
out={}
for f in [*range(337,358),*range(669,696)]:
 result=[measure(np.asarray(Image.open(d/f'{f:06}.png').convert('RGB')),f) for d in [src,old]]
 if f in (340,345,348,351,354,669,672,675,679,683,686,689,692,693,694,695):print(f,*result,sep='\n')
 out[f]=result
(root/'actors.json').write_text(json.dumps(out,indent=2))
