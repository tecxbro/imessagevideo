from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label,find_objects,gaussian_filter1d
import json,sys
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
R=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
data=json.loads((root/'measurements.json').read_text())
actors=json.loads((root/'actors.json').read_text())
scene=json.loads((root/'project/scene.json').read_text());t=scene['tracks']

def bbox(q, box, threshold=187):
 x,y,X,Y=map(lambda z:max(0,min(1000,round(z))),box)
 if x>=X or y>=Y:return None
 a=q[y:Y,x:X].astype('int16')
 m=(a[:,:,0]<threshold)&(np.ptp(a,axis=2)<20)
 ys=np.flatnonzero(m.sum(axis=1)>1)
 xs=np.flatnonzero(m.sum(axis=0)>1)
 if len(xs)<4 or len(ys)<5:return None
 return [x+int(xs[0]),y+int(ys[0]),int(xs[-1]-xs[0]+1),int(ys[-1]-ys[0]+1)]

def keyboard(q,key_rows,rail,ky,scale):
 if len(key_rows)!=10:return None
 aa=np.array(key_rows,dtype=object)
 bottom=q[:,round(rail[0])+5:round(rail[1])-5,0]
 paper=np.median(bottom,axis=1)
 first=key_rows[0][1]
 y=np.flatnonzero((paper[max(0,first-35):first-1]>182)&(paper[max(0,first-35):first-1]<234))
 top=round(first-9*scale) if not len(y) else int(y[0]+max(0,first-35))
 if top<first-9*scale-5:top=round(first-9*scale)
 sample=bottom[top+2:min(first-1,top+15)]
 rgb=[215,216,221]
 if sample.size:
  level=float(np.median(sample))
  if 195<level<235:rgb=[round(level),round(level)+1,round(level)+5]
 mats=[]
 cut=y0=top+3
 y1=min(1000,top+round(scale*190))
 a0=round(rail[0])+3; a1=round(rail[1])-2
 a=q[y0:y1,a0:a1].astype('int16')
 if a.size:
  lab,n=label((a.min(axis=2)>=244)&(np.ptp(a,axis=2)<11))
  for i,(ys,xs) in enumerate(find_objects(lab),1):
   h=ys.stop-ys.start;w=xs.stop-xs.start
   if w<22 or h<10 or w>150 or h>110:continue
   if ((lab[ys,xs]==i).sum()<160):continue
   mats.append([a0+xs.start,y0+ys.start,a0+xs.stop,y0+ys.stop])
 rows=[]
 preferred=np.median(np.asarray([x[:4] for x in key_rows])[:,[1,3]],axis=0)
 for n,letters in enumerate(('QWERTYUIOP','ASDFGHJKL','ZXCVBNM')):
  guess=float(preferred[0]+n*51*scale)
  group=sorted([v for v in mats if abs(v[1]-guess)<20],key=lambda v:v[0])
  key_size=float(preferred[1]-preferred[0])
  # The wide shift and delete shapes flank the alphabet's third row.
  if n==2 and len(group)>=9:
   group=group[1:-1]
  if n==0:group=[v[:4] for v in key_rows]
  elif len(group)!=len(letters):
   if guess>=1000:break
   if len(rows)==0:break
   x0,y0,pitch,width,hh,_=rows[0]
   count=len(letters)
   x0=x0+(pitch*.5 if n==1 else pitch*1.5)
   rows.append([x0,round(guess,2),pitch,width,hh,count])
   continue
  pos=np.array(group)
  centers=(pos[:,0]+pos[:,2])/2
  pitch,center=np.polyfit(np.arange(len(letters)),centers,1)
  width=float(np.median(pos[:,2]-pos[:,0]))
  height=float(np.percentile(pos[:,3]-pos[:,1],65))
  if height<key_size*.82:height=key_size
  rows.append([round(center-width/2,3),float(np.median(pos[:,1])),round(pitch,4),width,height,len(letters)])
 return [top,rgb,rows]

def entry(f):
 a,b=data[str(f)]
 gray,blue=actors[str(f)][0]
 q=np.asarray(Image.open(R/f'{f:06}.png').convert('RGB'))
 x,y,s,ky=a['est']
 r=x+s*400
 rail=[a['rails'][0][0][-1],a['rails'][1][0][0]]
 coeff=keyboard(q,a['keys'],rail,ky,s)
 if coeff is None:
  return
 gray=[u for u in gray if u[0][0]<355 and (42 if f>=624 else 54)<u[0][3]-u[0][1]<159 and u[0][2]-u[0][0]>260 and u[0][0]>rail[0] and (f<624 or u[0][1]>100)]
 if len(gray)!=2:return
 bubbles=[]
 visual='sofia' if f<624 else 'follow'
 for j,(b,_,ink) in enumerate(gray):
  x0,y0,x1,y1=b
  h=y1-y0;w=x1-x0
  if visual=='sofia':
   lines=[bbox(q,(x0+10,y0+10,x1-12,y1-10),160)]
  else:
   cuts=(.09,.48,.87) if j==0 else (.10,.37,.64,.93)
   lines=[bbox(q,(x0+.058*w,y0+lo*h,x1-20,y0+hi*h),202 if j==0 else 165)
          for lo,hi in zip(cuts,cuts[1:])]
  if any(v is None for v in lines):
   dots=[ink[i] if i<len(ink) else None for i in range(1 if visual=='sofia' else j+2)]
   for i,line in enumerate(lines):
    if line is not None:continue
    term=dots[i]
    lines[i]=[term[0],term[1],term[2]-term[0],term[3]-term[1]] if term else [
      round(x0+.067*w),round(y0+h*(.23+i*.255)),round(.87*w if i==0 else (.61*w if i==1 else .12*w)),round(h*.19 if j else h*.31)]
  bubbles.append([b,lines])
 gap_lo=gray[0][0][3]+14
 gap_hi=gray[1][0][1]-15
 if visual=='sofia':
  gap_lo=gray[1][0][3]+27
  gap_hi=gray[1][0][3]+103
 today=bbox(q,(450,max(0,gap_lo),550,min(1000,gap_hi)),217 if 660<=f<=668 else 194)
 later_led = None
 if visual=='follow':
  colors=[]
  for yy in range(480,571):
   rr=np.asarray(q[yy,round(rail[0])+25:415,:],dtype='int16')
   good=(rr[:,0]>=190)&(rr[:,0]<233)&(np.ptp(rr,axis=1)<12)
   run=np.flatnonzero(good)
   if len(run)>50:
    # Bounds need to include the dark printed caption inside the fill.
    left0=round(rail[0])+25+int(run.min())
    right0=round(rail[0])+26+int(run.max())
    if right0-left0<205:colors.append((yy,left0,right0))
  if len(colors)>=18:
   groups=np.split(np.array(colors),np.flatnonzero(np.diff(np.array(colors)[:,0])>3)+1)
   rows=max(groups,key=len)
   if 24<len(rows)<65:
    later_led=[int(np.percentile(rows[:,1],7)),int(rows[0,0]),
                int(np.percentile(rows[:,2],93)),int(rows[-1,0]+1)]
 upper=bubbles[0][0]
 active_blue=None
 if visual=='follow':
  hits=[b for b,_,_ in blue if b[3]<upper[1] and b[0]>200]
  if hits:
   x0,y0,x1,y1=max(hits,key=lambda v:v[2]-v[0]);hh=(48*s)
   active_blue=[x0,round(y1-hh),x1,y1]
 return dict(rails=rail,keys=coeff,items=bubbles,today=today,no=later_led,blue=active_blue)

def rows(first,last):
 out={}
 for f in range(first,last+1):
  value=entry(f)
  if value:out[str(f)]=value
  else:print('missing',f)
 return out
out={'follow':rows(660,673)}
(root/'inside-staging.json').write_text(json.dumps(out,indent=2))
for f in ('667','669','671','672'):
 print(f,out['follow'].get(f))
