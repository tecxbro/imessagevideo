from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects, gaussian_filter1d
from scipy.signal import find_peaks
import json,sys
r=Path(__file__).parent
sys.path.insert(0,str(r/'project'))
from render import interpolate
s=json.loads((r/'project/scene.json').read_text())['tracks']
a=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
b=Path('/tmp/sidehoe-reveal-clean.DeKHma/frames')

def across(q,ylo,yhi,x0,x1):
 d=np.median(q[max(0,ylo):min(yhi,1000),max(x0,0):min(1000,x1),:3],axis=(0,2))
 x=max(x0,0)
 bands=[]
 for cut in (220,160,100,48,20):
  dark=np.flatnonzero(d<cut)
  if len(dark):bands.append([int(dark[0]+x),int(dark[-1]+x+1)])
  else:bands.append([])
 return bands

def keys(q,x,y,w,h):
 a,b=max(0,int(x)),max(0,int(y))
 A,B=min(1000,int(x+w)),min(1000,int(y+h))
 c=q[b:B,a:A].astype('int16')
 white=(c.min(axis=2)>=245)&(np.ptp(c,axis=2)<=9)
 labs,n=label(white)
 data=[]
 for idx,(yy,xx) in enumerate(find_objects(labs),1):
  v=labs[yy,xx]==idx
  wid=xx.stop-xx.start;hei=yy.stop-yy.start
  if wid>9 and hei>9 and wid<200 and hei<130 and v.sum() > 100:
   data.append([xx.start+a,yy.start+b,xx.stop+a,yy.stop+b,int(v.sum())])
 return sorted(data,key=lambda t:t[1])

def sample(f,path):
 q=np.array(Image.open(path/f'{f:06}.png'))
 follow=f>=624
 x,y,v=interpolate(s['followMeasuredCamera' if follow else 'sofiaMeasuredCamera'],f)
 r=x+400*v
 k=543+interpolate(s['followKeyboardOffset'],f)[0] if follow else interpolate(s['sofiaKeyboardY'],f)[0]
 ky=round(y+k*v)
 out=[across(q,240,780,int(x)-15,int(x)+80),across(q,240,780,int(r)-80,int(r)+15)]
 # White keys are isolated by the darker tray. Detect their rows independently
 # from the composer and each individual alphabet column.
 key=keys(q,round(x+11*v),ky-18,round(378*v),229)
 key_row=[c for c in key if abs(c[1]-ky-9*v)<28 and 20<c[2]-c[0]<105]
 key_row=sorted(key_row,key=lambda c:c[0])
 pos=[]
 for i in range(10):
  if i>=len(key_row):break
  c=key_row[i]
  rel=q[c[1]:c[3],c[0]:c[2]]
  dark=(rel.max(2)<132)
  j=np.argwhere(dark)
  glyph=(j.min(0).tolist(),j.max(0).tolist()) if len(j)>2 else None
  pos.append([*c[:4],glyph])
 return {'rails':out,'keys':pos,'est':[x,y,v,ky]}
rows={}
for f in [*range(337,358),*range(665,696)]:
 rows[f]=[sample(f,d) for d in (a,b)]
 if f%3==0 or f in (348,674,679,693):
  print(f,rows[f][0]['est'],*[m['rails'][0:2] for m in rows[f]])
  for m in rows[f]:
   print('keys',len(m['keys']),m['keys'][:2],m['keys'][-2:])
(r/'measurements.json').write_text(json.dumps(rows,indent=2))
