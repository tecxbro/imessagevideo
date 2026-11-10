"""Measure only the newly exposed gray Messages page at source354."""
from pathlib import Path
import sys,json,copy
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
P=Path(__file__).resolve().parent
image=np.array(Image.open(P/'mail-edit-v17-source/0354.png').convert('RGB'))
gray=image.mean(2)
neutral=image.max(2)-image.min(2)<5
region=np.zeros(gray.shape,bool)
region[:,660:1260]=True
mask=np.uint8(neutral&(abs(gray-140)<=3)&region)
count,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
index=1+int(np.argmax(stats[1:,4]))
body=labels==index
fill=int(round(float(np.median(gray[body]))))
left=[]
right=[]
for y in range(101):
 points=np.where(body[y])[0]
 if not len(points):
  raise ValueError('Gray material boundary not observed at'+str(y))
 l=int(points.min())
 r=int(points.max())
 def half_edge(center,direction):
  if direction=='left':
   candidates=range(max(0,l-5),l+2)
   for x in candidates:
    if gray[y,x]<fill/2<=gray[y,x+1]:
     return x+(fill/2-gray[y,x])/(gray[y,x+1]-gray[y,x])+.5
   return l
  candidates=range(r-1,min(1919,r+5))
  for x in candidates:
   if gray[y,x]>=fill/2>gray[y,x+1]:
    return x+(fill/2-gray[y,x])/(gray[y,x+1]-gray[y,x])+.5
  return r+1
 left.append([float(half_edge(l,'left')),y+.5])
 right.append([float(half_edge(r,'right')),y+.5])
flat_left=float(np.median([v[0]for v in left[80:]]))
flat_right=float(np.median([v[0]for v in right[80:]]))
points=[[left[0][0],-1],[right[0][0],-1]]+right+[[flat_right,1081],[flat_left,1081]]+list(reversed(left))
def fmt(value):
 return f'{value:.4f}'.rstrip('0').rstrip('.')
d='M'+fmt(points[0][0])+' '+fmt(points[0][1])+' '+' '.join('L'+fmt(x)+' '+fmt(y)for x,y in points[1:])+' Z'
spec=dict(scope=[354,354],fill='#'+f'{fill:02x}'*3,path=d,source_gray_component=stats[index,:4].tolist(),observed_fill=fill,left_boundary=left,right_boundary=right,visible_bottom_censored=True,visible_top_censored=True,notice='Only native constant gray material geometry; actual source exposes fullMessagespage at354, prior345–353show onlybacksheetsmallcap. Shape is measured from largestuniformgray component and halflevel outerboundary, not tracedcopy/photo/frame. ForegroundMailpane andhardware stay independent. Only the visible footprint is known; top/bottomcontinueoutsideviewport. No new runtime rasterasset.')
(P/'mail-gray354-v18-elements.json').write_text(json.dumps(spec,indent=2))
print(fill,flat_left,flat_right,'graypixels',int(body.sum()))
