"""Measure independent physical device, Messages UI, and four Memoji poses."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import ConvexHull
p=Path(__file__).parent

def circle(component, side=None):
 h,w=component.shape;points=[]
 for y in range(0,h,2):
  xs=np.flatnonzero(component[y])
  if len(xs)>2:
   for x in ([int(xs.min())] if side=='left' else [int(xs.max())] if side=='right' else [int(xs.min()),int(xs.max())]):
    if 2<x<w-3 and 2<y<h-3:points.append((x,y))
 for x in (range(0,w,2) if side is None else []):
  ys=np.flatnonzero(component[:,x])
  if len(ys)>2:
   for y in [int(ys.min()),int(ys.max())]:
    if 2<x<w-3 and 2<y<h-3:points.append((x,y))
 if len(points)<15:return None
 xy=np.array(points)
 if side is None:
  try:xy=xy[ConvexHull(xy).vertices]
  except Exception:return None
 x,y=xy[:,0],xy[:,1];v=np.linalg.lstsq(np.column_stack([x,y,np.ones_like(x)]),-(x*x+y*y),rcond=None)[0];cx,cy=-v[:2]/2;r2=cx*cx+cy*cy-v[2]
 if r2<=0:return None
 radius=np.sqrt(r2);res=np.abs(np.hypot(x-cx,y-cy)-radius).mean()
 return {'cx':float(cx),'cy':float(cy),'radius':float(radius),'residual':float(res)}

def components(mask,minarea=60):
 labeled,n=ndimage.label(mask);out=[]
 for label,box in enumerate(ndimage.find_objects(labeled),1):
  if box is None:continue
  if (labeled[box]==label).sum()<minarea:continue
  out.append((labeled==label,box))
 return out

def color_mask(a,kind):
 r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 if kind=='bob':return (r<240)&(g>200)&(b>230)&(b-g>3)&(b-r>12)
 if kind=='laptop':return (r>230)&(g>180)&(b<185)
 if kind=='robot':return (g>225)&(b>225)&(r<235)&(g-r>12)&(b-g<4)
 return (r>240)&(g>210)&(g<245)&(b>195)&(b<240)&(r-g>10)&(g-b>2)

old=json.loads((p/'transition-14/independent-avatar-poses.json').read_text());prev={name:{'cx':info['base_xy'][0]+info['world']['cx'],'cy':info['base_xy'][1]+info['world']['cy'],'radius':info['world']['radius']} for name,info in old.items()};rows=[];prev_t=None
for i,file in enumerate(sorted((p/'entrance-native').glob('*.png'))):
 t=14.5+i/30;a=np.array(Image.open(file).convert('RGB'),dtype='int16');row={'t':t,'frame':435+i,'avatars':{}}
 for name in ['bob','laptop','robot','alice']:
  choices=[]
  for mask,box in components(color_mask(a,name)):
   result=circle(mask,'right' if name in ['bob','laptop'] else 'left')
   if result is None or result['radius']<4 or result['residual']>5:continue
   prior=prev[name]
   if not prior['radius']*.35<result['radius']<prior['radius']*1.4:continue
   distance=np.hypot(result['cx']-prior['cx'],result['cy']-prior['cy'])/(prior['radius']+10);size=abs(np.log(result['radius']/prior['radius']));score=distance+size+result['residual']*.07;choices.append((score,result))
  if choices:
   best=min(choices,key=lambda q:q[0])[1];row['avatars'][name]=best;prev[name]=best
 # First T is the leftmost title glyph; it is left of all header-Memoji faces.
 # Its top horizontal bar and narrow lower stem distinguish it from hair/eyes.
 dark=a.max(2)<80;dark[:250]=False;candidates=[]
 for mask,box in components(dark,20):
  y,x=box;w=x.stop-x.start;h=y.stop-y.start
  if not (8<w<230 and 10<h<300 and .4<w/h<1.5):continue
  if x.start<80 or x.start>930:continue
  if t<14.6:continue
  if prev_t is None and (x.start>600 or y.start<800):continue
  if prev_t and not prev_t['x']-30<x.start<prev_t['x']+220:continue
  part=mask[box];upper=part[int(.03*h):max(int(.03*h)+1,int(.2*h))].mean();lower=part[int(.45*h):].mean()
  if upper>.75 and lower<.5:candidates.append({'x':x.start,'y':y.start,'w':w,'h':h,'score':abs(x.start-(prev_t['x'] if prev_t else 200))})
 if candidates:
  tt=min(candidates,key=lambda q:q['score']);prev_t=tt;row['first_T']=tt
  scale=tt['w']/18;roi=(max(0,tt['x']-3),max(0,round(tt['y']-2*scale)),min(1920,round(tt['x']+193*scale+20)),min(1080,round(tt['y']+24*scale+4)));x0,y0,x1,y1=roi;m=dark[y0:y1,x0:x1];yy,xx=np.where(m)
  if len(xx):row['title_ink']=[x0+int(xx.min()),y0+int(yy.min()),x0+int(xx.max()+1),y0+int(yy.max()+1)]
 # The island is physically independent from the Messages UI transform.
 candidates=[]
 island=a.max(2)<65;island[450:]=False
 for mask,box in components(island,200):
  y,x=box;w=x.stop-x.start;h=y.stop-y.start
  if w>100 and h>5 and w/h>3 and abs((x.start+x.stop)/2-960)<100:candidates.append((w*h,[x.start,y.start,x.stop,y.stop]))
 if candidates:row['island']=max(candidates)[1]
 # Neutral gray header plate; skip ambiguous broad stage/rim components.
 gray=(a.max(2)-a.min(2)<4)&(a.mean(2)>231)&(a.mean(2)<252.5);graychoices=[]
 target=np.mean([[q['cx'],q['cy']] for q in row['avatars'].values()],0) if row['avatars'] else [960,400]
 for mask,box in components(gray,100):
  result=circle(mask)
  if result is None or result['residual']>4 or not 30<result['radius']<1100:continue
  dist=np.hypot(result['cx']-target[0],result['cy']-target[1])
  if dist>result['radius']*.8:continue
  result['gray']=float(np.median(a[mask].mean(1)));graychoices.append((dist,result))
 if graychoices:row['gray_circle']=min(graychoices,key=lambda q:q[0])[1]
 rows.append(row)
(p/'entrance-v13-measurements.json').write_text(json.dumps(rows,indent=2));print('frames',len(rows),'T',sum('first_T'in r for r in rows),'island',sum('island'in r for r in rows),'gray',sum('gray_circle'in r for r in rows));print(json.dumps([r for r in rows if r['frame'] in [439,457,472,495]],indent=2))
