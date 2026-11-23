from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
from scipy.optimize import differential_evolution
d=Path(__file__).parent
sys.path.insert(0,str(d/'project'))
from render import cursor
p=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
N=98;c=N//2
Y,X=np.mgrid[:N,:N]
rows=[]
for f,cx,cy,rotation in [(399,984,890,-78),(400,963,824,-70),(401,938,732,-58),(402,916,632,-65),(403,906,553,-69),(404,900,500,-72),(405,897,463,-74),(406,887,430,-84),(407,873,406,-84),(408,854,390,-96)]:
 x0,y0=cx-c,cy-c
 a=Image.new('RGB',(N,N),'#fdfdfd')
 src=Image.open(p/f'{f:06}.png').convert('RGB')
 a.paste(src.crop((x0,y0,min(1000,x0+N),y0+N)),(0,0))
 rgb=np.array(a,dtype=float)
 gray=rgb.mean(axis=2)
 width=(X+x0)<1000
 neutral=np.ptp(rgb,axis=2)<24
 near=(np.abs(X-c)<42)&(np.abs(Y-c)<44)
 valid=width&near
 ref=(253-gray).clip(0,255)*neutral*valid
 ref[ref<7]=0
 mx=(X*ref).sum()/ref.sum(); my=(Y*ref).sum()/ref.sum()
 def eval(par,full=False):
  rot,scale,h,v,opacity,dx,dy=par
  art=Image.new('RGBA',(N,N),'#fdfdfd')
  cursor(art,c+dx,c+dy,rot,opacity,scale,softness=(h,v))
  other=(253-np.asarray(art)[:,:,0].astype(float)).clip(0,255)
  err=(np.abs(other-ref)*valid).sum()+2*(abs(dx)+abs(dy))
  if full:return [f,*[round(float(z),4) for z in [cx+dx,cy+dy,rot,scale,opacity,h,v]]]
  return err
 start=(rotation,.93,2.5,8 if f<=402 else 3,.9, (mx-c)-16,(my-c)+9)
 bounds=[(rotation-33,rotation+30),(.50,1.35),(.1,10),(.4,24),(.37,1),(-39,16),(-28,25)]
 sol=differential_evolution(eval,bounds,maxiter=37,popsize=7,seed=f,polish=False)
 row=eval(sol.x,True);rows.append(row)
 print(row,round(sol.fun,2),flush=True)
(d/'calendar-cursor-fit.json').write_text(json.dumps(rows,indent=2))
