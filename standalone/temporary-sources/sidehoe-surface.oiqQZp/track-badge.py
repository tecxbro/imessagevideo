from pathlib import Path
from PIL import Image
from scipy.optimize import least_squares
import numpy as np,json,sys
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
root=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
config=p/'project/scene.json'
s=json.loads(config.read_text())
track=s['tracks']['closingMeasuredBox']
out=[]
for f in range(701,766):
 cx,cy,w,h=interpolate(track,f)
 q=np.asarray(Image.open(root/f'{f:06}.png').convert('L'),dtype=float)
 lo,top,hi,bot=map(round,(cx-w/2-11,cy-h/2-10,cx+w/2+11,cy+h/2+10))
 crop=q[top:bot,lo:hi]
 ysize,xsize=crop.shape
 pts=[]
 def crossing(line,offset,obvious):
    options=np.where(line<151)[0]
    if not len(options):
      return None
    i,j=options[0],options[-1]
    if (i==0 or j==len(line)-1 or (obvious is not None and not i<=obvious<=j)):
      return None
    low=i-1+(line[i-1]-151)/(line[i-1]-line[i])
    high=j+(151-line[j])/(line[j+1]-line[j])
    return low+offset+.5,high+offset+.5
 for y in range(14,ysize-13,6):
      pair=crossing(crop[y],lo,None)
      if pair and pair[1]-pair[0]>w*.63:
          pts.extend([(x,y+top+.5) for x in pair])
 for x in range(14,xsize-13,6):
      pair=crossing(crop[:,x],top,None)
      if pair and pair[1]-pair[0]>h*.63:
          pts.extend([(x+lo+.5,y) for y in pair])
 vector=np.array(pts)
 def err(state):
    x,y,wide,tall,relative=state
    radius_x=wide*relative/256
    radius_y=tall*relative/256
    inv=np.array([1/wide,1/tall])*256
    local=np.abs(vector-[x,y])*inv-128+relative
    return np.hypot(*np.maximum(local,0).T)+np.minimum(np.max(local,axis=1),0)-relative
 fit=least_squares(err,(cx,cy,w,h,52),
       bounds=([cx-4,cy-4,w-9,h-10,36],[cx+4,cy+4,w+9,h+10,66]),loss='soft_l1',f_scale=.55)
 clip=np.mean(np.abs(fit.fun))
 if clip>1.85:
     print('uncertain',f,round(clip,2))
     continue
 out.append([f,*np.round(fit.x,3).tolist()])
 if f in [701,702,704,706,707,710,712,719,736,749,765]:
     print(f,'prior',np.round([cx,cy,w,h,52],2),'measured',np.round(fit.x,3),'fit residual',round(clip,3))
s['tracks']['closingBadgeShape']=out
config.write_text(json.dumps(s,indent=2)+'\n')
