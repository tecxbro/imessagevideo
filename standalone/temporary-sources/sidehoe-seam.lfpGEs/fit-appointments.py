from pathlib import Path
from PIL import Image
import numpy as np,json,sys, math
from scipy.optimize import least_squares
from scipy.special import ndtr
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
root=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
current=Path('/tmp/sidehoe-surface.oiqQZp/final-frames')
cfg=p/'project'/'scene.json'
scene=json.loads(cfg.read_text())
t=scene['tracks']
generated={}
for f in range(397,418):
 a=np.array(Image.open(root/f'{f:06}.png').convert('RGB'),float)
 b=np.array(Image.open(current/f'{f:06}.png').convert('RGB'),float)
 e=interpolate(t['calendarAppointmentExposure'],f)
 aa,=interpolate(t['calendarArrivalOpacity'],f)
 s=scene['calendarHandoff'].get(str(f))
 bar_bias=s[-1] if s else 0
 blue_top,blue_high,blue_alpha,purple_top,purple_high,purple_alpha,base=e
 lo=math.floor(blue_top-54)
 y=np.arange(lo, min(1000,math.ceil(purple_top+purple_high+42)))
 back=np.median(a[y,16:92],axis=1)
 target=np.median(a[y,383:798],axis=1)
 existing=np.median(b[y,383:798],axis=1)
 # Fit moving edge coverage and the two physical pigments against the clean strip.
 x0=np.array([blue_top+bar_bias,blue_top+bar_bias+blue_high,base,base,139,217,252,
              purple_top+bar_bias,purple_top+bar_bias+purple_high,base,base,182,138,241])
 limits=np.array([19,24,base*.85,base*.85,47,38,15,19,25,base*.85,base*.85,43,30,28])
 lo0=x0-limits;hi0=x0+limits
 hi0[[4,5,6,11,12,13]]=np.minimum(hi0[[4,5,6,11,12,13]],255)
 lo0[[2,3,9,10]]=np.maximum(lo0[[2,3,9,10]],.8)
 def sample(v):
  out=back.copy()
  for j,a0 in enumerate([blue_alpha,purple_alpha]):
   top,bottom,g1,g2,R,G,B=v[7*j:7*(j+1)]
   val=np.clip(ndtr((y+.5-top)/g1)-ndtr((y+.5-bottom)/g2),0,1)*a0*aa/255
   out=out*(1-val[:,None])+np.array([R,G,B])*val[:,None]
  return out
 def residual(v):
  delta=(sample(v)-target).ravel()
  return np.r_[delta, (v-x0)*.40]
 result=least_squares(residual,x0,bounds=(lo0,hi0),loss='soft_l1',max_nfev=100)
 print(f,round(np.abs(existing-target).mean(),3),round(np.abs(sample(result.x)-target).mean(),3),
     np.round(result.x,2).tolist())
 generated[str(f)]=np.round(result.x,3).tolist()
scene['calendarBarShutter']=generated
cfg.write_text(json.dumps(scene,indent=2)+'\n')
