"""Use a fully colored original emoji pose, then fit its source opacity; avoid fading an already faded asset twice."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/root-early-end-measure';A=R/'assets/early-end-art';P=R/'early-end-refinement.json';patch=json.loads(P.read_text());root=patch['replacements']['reason-v5-measured-camera'];records=[p for p in patch['provenance'] if p.get('kind')=='native reasoning row timing'];ledger=[]
def ar(n):return np.array(Image.open(M/f'frame-{n:04d}.png').convert('RGB')).astype(float)
BOXES={}
def measured_rows(n):
 if n not in BOXES:
  aa=ar(n);mask=aa.max(2)<245;rr=ndimage.binary_closing(mask.sum(1)>3,iterations=3);labels,count=ndimage.label(rr);boxes=[]
  for sl in ndimage.find_objects(labels):
   yy=sl[0]
   if yy.stop-yy.start<15:continue
   ys,xs=np.where(mask[yy.start:yy.stop]);boxes.append([int(xs.min()),yy.start,int(xs.max()+1),yy.stop])
  BOXES[n]=boxes
 return BOXES[n]
for i,row in enumerate(root['children']):
 images=[c for c in row['children'] if c['type']=='image']
 rec=records[i];b=rec['sourceBounds'];candidates=[]
 # Measure each isolated row's own bounds: colored emoji/antialias and text rows do not have identical ink-height ratios.
 for m in rec['measurements']:
  n=round(m['t']*30);q=measured_rows(n)[i];sx=(q[2]-q[0])/(b[2]-b[0]);sy=(q[3]-q[1])/(b[3]-b[1]);m.update(x=q[0]-b[0]*sx,y=q[1]-b[1]*sy,scaleX=sx,scaleY=sy)
 row['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in rec['measurements']] for k in ['x','y','scaleX','scaleY']})
 if not images:continue
 for m in rec['measurements']:
  n=round(m['t']*30);q=[round(b[0]*m['scaleX']+m['x']),round(b[1]*m['scaleY']+m['y']),round(b[2]*m['scaleX']+m['x']),round(b[3]*m['scaleY']+m['y'])];a=ar(n);roi=a[q[1]:q[3],q[0]:q[2]];spread=float(np.quantile(roi.max(2)-roi.min(2),.995));candidates.append((spread,n,m,q))
 strength,n,pose,q=max(candidates,key=lambda z:z[0]);a=ar(n);roi=a[q[1]:q[3],q[0]:q[2]];color=(roi.max(2)-roi.min(2)>22)&(roi.min(2)<235);lab,num=ndimage.label(ndimage.binary_dilation(color,iterations=4),np.ones((3,3)));boxes=[]
 for sl in ndimage.find_objects(lab):
  if not sl:continue
  yy,xx=sl
  if xx.stop-xx.start<12 or yy.stop-yy.start<12:continue
  boxes.append([max(q[0],q[0]+xx.start-3),max(q[1],q[1]+yy.start-3),min(q[2],q[0]+xx.stop+3),min(q[3],q[1]+yy.stop+3)])
 boxes.sort();new=[];opacity=[dict(t=m['t'],value=min(1,sp/max(1,strength))) for sp,nn,m,qq in candidates]
 for j,box in enumerate(boxes):
  path=A/f'reason-full-color-{i}-{j}.png';Image.fromarray(a.astype('uint8')).crop(box).save(path);new.append(dict(id=f'early-reason-emoji-full-{i}-{j}',type='image',src=str(path),x=(box[0]-pose['x'])/pose['scaleX'],y=(box[1]-pose['y'])/pose['scaleY'],width=(box[2]-box[0])/pose['scaleX'],height=(box[3]-box[1])/pose['scaleY'],sourceFrame=n,sourceBounds=box,keyframes={'opacity':opacity}));ledger.append(dict(kind='independent full-color emoji with measured source fade',sourceFrame=n,sourceBounds=box,asset=str(path),row=i,measurements=opacity))
 row['children']=[c for c in row['children'] if c['type']!='image']+new
root['children'][0]['keyframes']['opacity']=[dict(t=8.7,value=0),dict(t=8.88,value=1)]
root['children'][-1]['children'][0]['semanticText']='Let me find agents who can help...'
patch['provenance']=[q for q in patch['provenance'] if q.get('kind')!='reasoning emoji checkpoint refinement']+[dict(kind='reasoning emoji checkpoint refinement',diagnosis='Canonical12s emoji were already faded. Applying a second fade made the earlier saturated states too pale. Choose the strongest original emoji pose and fit its measured source saturation/opacity.',assets=ledger)];P.write_text(json.dumps(patch,indent=2));print('Refined full-color reasoning emoji',len(ledger))
