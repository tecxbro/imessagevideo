from PIL import Image,ImageDraw
from pathlib import Path
from scipy.ndimage import map_coordinates, gaussian_filter
from scipy.optimize import differential_evolution
import numpy as np,json
p=Path(__file__).parent; r=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
q=lambda f: np.asarray(Image.open(r/f'{f:06}.png').convert('RGB')).astype(float)
A=q(253)
Y,X=np.mgrid[80:880:4,0:900:4]
prior=np.array([gaussian_filter((253-A[:,:,c])/255,4) for c in range(3)])
out={}
for f in range(254,258):
 B=q(f)
 v=(253-B[Y,X])/255
 wanted=(v.max(axis=2)>.073)
 if f>=257:wanted &= (np.ptp(v,axis=2)>.046)
 cols,rows=X[wanted],Y[wanted]
 f0=v[wanted]
 def est(par):
  dx,dy,sx,sy=par
  u=(cols-500-dx)/sx+500
  w=(rows-500-dy)/sy+500
  observed=np.stack([map_coordinates(a,[w,u],order=1,cval=0,prefilter=False) for a in prior],axis=-1)
  e=np.abs(observed-f0)
  return np.minimum(e,.17).mean()+np.mean(np.abs([sx-1,sy-1]))*.018
 anchors=[(-12,1),(-40,1),(-83,3),(-140,0)]
 dx,dy=anchors[f-254]
 res=differential_evolution(est,[(dx-59,dx+54),(-50,50),(.90,1.19),(.90,1.19)],maxiter=40,popsize=6,polish=False,seed=f)
 out[f]=np.round(res.x,3).tolist()
 print(f,out[f],round(res.fun,5),flush=True)
(p/'cluster-pose.json').write_text(json.dumps(out,indent=2))
fig=Image.new('RGB',(1500,1110),'#fafafa')
d=ImageDraw.Draw(fig)
for i,f in enumerate(range(254,259)):
 a=Image.open(r/f'{f:06}.png').crop((0,120,860,880)).resize((490,410))
 dx=i%3*500;dy=i//3*550
 fig.paste(a,(dx,dy+18)); d.text((dx+4,dy+2),str(f),fill='black')
 for x in range(0,860,50):
  px=dx+round(x*490/860)
  d.line((px,dy+18,px,dy+428),fill='#d2cee3',width=1)
  d.text((px+1,dy+429),str(x),fill='black')
 for k in range(150,880,50):
  py=dy+18+round((k-120)*410/760)
  d.line((dx,py,dx+490,py),fill='#d2cee3',width=1)
  d.text((dx+4,py+1),str(k),fill='black')
fig.save(p/'cluster-grid.jpg',quality=95)
