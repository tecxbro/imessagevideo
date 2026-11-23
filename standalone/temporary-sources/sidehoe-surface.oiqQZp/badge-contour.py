from pathlib import Path
from PIL import Image
from scipy.optimize import least_squares
import numpy as np,json,sys
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
root=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
candidate=Path('/tmp/sidehoe-lens.I4y7rV/combined-frames')
j=json.loads((p/'project/scene.json').read_text())['tracks']
for f in (701,702,704,706,707,708,709,710,712,719,736,749):
 cx,cy,w,h=interpolate(j['closingMeasuredBox'],f)
 print('f',f,np.round((cx,cy,w,h),2))
 for r in (root,candidate):
  q=np.asarray(Image.open(r/f'{f:06}.png').convert('L'),dtype=float)
  lo,top,hi,bot=map(round,(cx-w/2-8,cy-h/2-8,cx+w/2+8,cy+h/2+8))
  hs=q[top:bot,lo:hi]
  center_y,center_x=round(cy-top),round(cx-lo)
  px=np.median(hs[center_y-22:center_y+22],axis=0)
  # Avoid the card art when measuring the top face and bottom of the tile.
  py=hs[:,center_x]
  def spans(arr,offset):
   xx=np.flatnonzero(arr<151)
   if not len(xx):return [],[]
   i,j=xx[0],xx[-1]
   low=(i if i==0 else i-1+(arr[i-1]-151)/(arr[i-1]-arr[i]))+offset
   high=(j if j==len(arr)-1 else j+(151-arr[j])/(arr[j+1]-arr[j]))+offset
   return low,high
  u,v=spans(px,lo)
  l,r=spans(py,top)
  print(np.round([(u+v)/2,(l+r)/2,v-u,r-l],3),np.round([u,l,v,r],3))
