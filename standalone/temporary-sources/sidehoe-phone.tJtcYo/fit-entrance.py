from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,sys,json
from scipy.optimize import minimize
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import Film,entrance_casing,layer,interpolate
q=p/'project/scene.json'
j=json.loads(q.read_text());tracks=j['tracks']; scene=Film(j)
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
baseline=Path('/tmp/sidehoe-portraits.if793d/full-frames')
out={}
for f in range(313,334):
 x,y,base=scene.track("sofiaMeasuredCamera",f)
 ky,=scene.track("sofiaKeyboardY",f)
 history,heading,_,_=scene.track("sofiaPlateRegistration",f)
 history,heading=(history,heading) if f>=320 else (0,None)
 if f>=331: break
 bevel=[round(np.interp(f,[313,317,322,327,330],s),3) for s in
       ([25,24,20,19,18],[24,22,19,18.5,18],[22,24,20,17,17])]
 hardware=entrance_casing(scene.thread_plate("sofia",f,ky,history_offset=history,heading_height=heading),*bevel)
 reply=layer(hardware.width,hardware.height)
 scene.bubble(reply,227,366,132,32,scene.c['sofia'][4],True,paint="#13c4fa")
 dest=np.asarray(hardware.convert('RGBa'))
 add=np.asarray(reply.convert('RGBa'))
 xstart=220; extent=(290,500); ratio=.5
 target=np.asarray(Image.open(reference/f'{f:06}.png').convert('RGB').crop((xstart,0,xstart+580,1000)).resize(extent,Image.Resampling.BOX),np.int16)
 earlier=np.asarray(Image.open(baseline/f'{f:06}.png').convert('RGB').crop((xstart,0,xstart+580,1000)).resize(extent,Image.Resampling.BOX),np.int16)
 y0=np.interp(f,[313,314,315,316,317,318,319,322,330],[1,31,30,22,15,11,6,0,0])
 by0=np.interp(f,[313,314,315,316,317,318,319,320,321,322,330],[34,26,19,15,10,5,3,2,1.2,.58,.45])
 bx0=np.interp(f,[313,317,323,330],[1.4,1.1,.67,.40])
 start=[0,y0,1,1,bx0,by0,.75 if f==313 else 1.]
 bounds=[(-5,4),(y0-17,y0+12),(.974,1.035),(.958,1.044),(.21,3.4),
         (max(.15,by0-11),by0+15),(.02,1) if f<=314 else (.72,1)]
 def objective(v):
   dx,dy,sx,sy,bx,by,opacity=v
   a=add[:,:,3:4]/255*opacity
   combined=np.rint(dest*(1-a)+add*opacity).astype(np.uint8)
   scaled=Image.fromarray(combined,mode='RGBa')
   kx=1/(base*sx*ratio);ky=1/(base*sy*ratio)
   matrix=(kx,0,-(x+dx-xstart)*ratio*kx,0,ky,-(y+dy)*ratio*ky)
   shutter=scaled.transform(extent,Image.Transform.AFFINE,matrix,Image.Resampling.BILINEAR)
   shutter=shutter.filter(ImageFilter.GaussianBlur((bx*ratio,by*ratio)))
   r=np.asarray(shutter,np.int16); alpha=r[:,:,3:4]/255
   rgb=r[:,:,:3]+(1-alpha)*253
   err=np.abs(rgb-target)
   return err.mean()+.045*abs(dx)+.0035*abs(dy-y0)+.06*abs(sy-1)*100
 res=minimize(objective,start,method='Powell',bounds=bounds,options={'maxiter':10,'ftol':.015,'xtol':.10})
 before=np.abs(earlier-target).mean()
 v=res.x
 print(f,round(before,3),round(res.fun,3),np.round(v,3).tolist(),bevel,flush=True)
 if res.fun<before*.995:
   out[str(f)]=np.round(v,4).tolist()+bevel
j['sofiaEarlyOptics']=out
q.write_text(json.dumps(j,indent=2)+'\n')
