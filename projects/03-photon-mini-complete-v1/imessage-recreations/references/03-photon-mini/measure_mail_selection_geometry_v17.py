"""Fit native circle/stem controls to observed blue UI, retaining the raw outline fallback."""
from pathlib import Path
import json,sys,copy,math
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
P=Path(__file__).resolve().parent
spec=json.loads((P/'mail-edit-v17-elements.json').read_text())
rows=[]
for selection in spec['selections']:
 frame=selection['frame']
 rgb=np.array(Image.open(P/f'mail-edit-v17-source/{frame:04}.png').convert('RGB'))[630:780,790:1275].astype(float)
 chroma=rgb[:,:,2]-rgb[:,:,0]
 rect=selection['highlight']
 rx,ry=rect['x']-790,rect['y']-630
 rw,rh=rect['width'],rect['height']
 background=np.zeros(chroma.shape)
 fill=tuple(int(rect['fill'][i:i+2],16)for i in [1,3,5])
 background[max(0,ry):min(150,ry+rh),max(0,rx):min(485,rx+rw)]=fill[2]-fill[0]
 alpha=np.clip((chroma-background)/(chroma.max()-background),0,1)
 count,labels,stats,centers=cv2.connectedComponentsWithStats(np.uint8(alpha>.5))
 candidates=[(index,stat)for index,stat in enumerate(stats[1:],1)if stat[4]>100 and stat[2]>15 and stat[3]>25]
 if len(candidates)!=2:
  raise ValueError(('No two native selection controls',frame,[q.tolist()for _,q in candidates]))
 candidates.sort(key=lambda q:q[1][0])
 children=[]
 measurements=[]
 for order,(index,stat)in enumerate(candidates):
  x,y,width,height,area=map(int,stat)
  mask=np.uint8(labels==index)
  row_width=[]
  for yy in range(y,y+height):
   xs=np.where(mask[yy])[0]
   row_width.append(len(xs))
  fat=np.where(np.array(row_width)>.85*max(row_width))[0]+y
  cy=float(np.mean(fat))
  points=[]
  contour=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[0][0][:,0,:].astype(float)
  cx=float(np.mean(np.where(mask[fat])[1]))
  estimated=width/2
  keep=(abs(contour[:,1]-cy)<estimated+1)&(abs(contour[:,0]-cx)>2)
  points=contour[keep]
  def loss(value):
   return np.linalg.norm(points-value[:2],axis=1)-value[2]
  fit=least_squares(loss,[cx,cy,estimated],loss='soft_l1',f_scale=.5)
  cx,cy,radius=fit.x
  radius+=.45
  # The narrow stem is measured at the middle of the selected-line rectangle.
  yy=int(round(ry+rh/2))
  lo=max(0,int(cx)-7)
  hi=min(alpha.shape[1],int(cx)+8)
  values=alpha[yy,lo:hi]
  inside=np.where(values>.5)[0]
  if not len(inside):
   raise ValueError(('Missing observed stem',frame,order))
  left=lo+inside.min()-.5
  right=lo+inside.max()+.5
  stem_center=(left+right)/2
  if order==0:
   stem_top=cy
   stem_bottom=ry+rh
  else:
   stem_top=ry
   stem_bottom=cy
  color=selection['handles']['fill']
  children.append(dict(id=f'mail-selection-circle-{frame}-{order}-v17',type='circle',x=float(cx+790-radius),y=float(cy+630-radius),width=float(radius*2),height=float(radius*2),fill=color))
  children.append(dict(id=f'mail-selection-stem-{frame}-{order}-v17',type='rect',x=float(left+790),y=float(stem_top+630),width=float(right-left),height=float(stem_bottom-stem_top),fill=color))
  measurements.append(dict(center=[float(cx+790),float(cy+630)],radius=float(radius),circle_RMS=float(np.sqrt(np.mean(loss(fit.x)**2))),observed_body_bounds=[x+790,y+630,x+790+width,y+630+height],stem_bounds=[float(left+790),float(stem_top+630),float(right+790),float(stem_bottom+630)]))
 group=dict(id=selection['handles']['id'],type='group',children=children,semanticText='Native text selection circles and stems',provenance=dict(kind='Source-measured native selection primitives',source_frame=frame,measurements=measurements,notice='Separate native circles/verticalstems avoid pixel-contour teeth. Source field/black copy remain separate. Original raw native control outline retained as diagnostic fallback.'))
 rows.append(dict(frame=frame,group=group,measurements=measurements))
(P/'mail-selection-geometry-v17.json').write_text(json.dumps(dict(frames=rows),indent=2))
print('Native controls',len(rows),'maxRMS',max(m['circle_RMS']for r in rows for m in r['measurements']))
