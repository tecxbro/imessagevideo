from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.special import ndtr
from scipy.optimize import least_squares
p=Path('/tmp/sidehoe-hyperframes.wG3QA2')
w=Path('/tmp/sidehoe-optical-path').read_text()
t=json.loads((Path(w)/'project/scene.json').read_text())['tracks']
def interp(name,f):
 keys=np.asarray(t[name])
 return [np.interp(f,keys[:,0],keys[:,j]) for j in range(1,keys.shape[1])]
out={}
for f in range(397,418):
 y0,h=interp('calendarCamera',f)[1:]
 q1,q2=[y0+h*interp(key,f)[0] for key in ('calendarLisa','calendarMarie')]
 a=np.asarray(Image.open(p/'source-stage'/f'{f:06}.png').convert('RGB'),dtype=np.float64)
 o=np.asarray(Image.open(p/'complete-motion-frames'/f'{f:06}.png').convert('RGB'),dtype=np.float64)
 y=np.arange(1000)+.5
 px=np.median(a[:,620:796,:],axis=1)
 oy=np.median(o[:,620:796,:],axis=1)
 hit=(y>=max(0,q1-80))&(y<=q2+1.1*h+80)
 y=y[hit]; rgb=px[hit]; old=oy[hit]
 def eval(p):
  blue_top,blue_h,violet_top,violet_h,soft,ab,av,base=p
  col1=(ndtr((y-blue_top)/soft)-ndtr((y-blue_top-blue_h)/soft))*ab
  col2=(ndtr((y-violet_top)/soft)-ndtr((y-violet_top-violet_h)/soft))*av
  rgb=base+col1[:,None]*np.array([-114,-36,-8])
  return rgb*(1-col2[:,None])+col2[:,None]*np.array([182,138,241])
 vals=[q1,1.5*h,q2,1.01*h,10,.36,.36,253]
 low=[q1-45,h*1.1,q2-38,h*.7,.85,.12,.12,249]
 high=[q1+45,h*1.9,q2+38,h*1.45,51,.69,.69,255]
 fit=least_squares(lambda q:(eval(q)-rgb).ravel(),vals,bounds=(low,high),loss='soft_l1',f_scale=3).x
 row= [f,*np.round(fit,3)]
 out[f]=row
 print(f,'in',[round(q1,1),round(q2,1)],'fit',np.round(fit,2).tolist(),
       'err',round(np.abs(rgb-old).mean(),2),round(np.abs(eval(fit)-rgb).mean(),2))
(Path(w)/'calendar-exposure.json').write_text(json.dumps(out,indent=2))
