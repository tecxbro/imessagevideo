from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys
from scipy.ndimage import label,binary_dilation,gaussian_filter
from scipy.optimize import minimize
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
from treatments import follow_pointer
a=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
b=Path('/tmp/sidehoe-lens.I4y7rV/combined-frames')
s=p/'project/scene.json'
j=json.loads(s.read_text())
k=j['tracks']['followPointerStage']
lean=j['tracks']['followPointerLean']
scenes={}

for f,x,y,w,h,soft,alpha in k:
 it=interpolate(lean,f)[0]
 left,top=round(x-15),round(y-10)
 width,height=round(w+it+39),round(h+35)
 box=(left,top,left+width,top+height)
 source=np.asarray(Image.open(a/f'{f:06}.png').convert('RGB').crop(box),dtype=float)
 old=np.asarray(Image.open(b/f'{f:06}.png').convert('RGB').crop(box),dtype=float)
 g=source.mean(axis=2)
 labels,_=label((g<153)&(np.ptp(source,axis=2)<33))
 vx,vy=round(x-left+w*.30),round(y-top+h*.42)
 detected=labels[vy,vx]
 if not detected:
  continue
 component=labels==detected
 target=binary_dilation(component,iterations=5)
 ink=np.clip((223-g)/223,0,1)*target
 # Exclude nearby lettering when fitting the shape below the feedback chip.
 foreign=binary_dilation((labels!=0)&(labels!=detected),iterations=1)
 weights=(target & ~foreign).astype(float)
 # White borders blend into the paper. Dark ink carries the best shape information.
 def error(state):
  px,py,ww,hh,blur_x,blur_y,opa,shear=state
  out=Image.new('RGBA',(width,height),(253,253,253))
  follow_pointer(out,px-left,py-top,ww,hh,blur_x,opa,lean=shear,vertical_softness=blur_y,rounded=True)
  luma=np.asarray(out,dtype=float)[:,:,:3].mean(axis=2)
  pred=np.clip((223-luma)/223,0,1)
  return (np.abs(pred-ink)*weights).sum() + 4*pred[~target].sum()
 def search(start):
  ranges=[(x-2.8,x+2.8),(y-2.8,y+2.8),(w-3.5,w+4),(h-4,h+5),
          (max(.18,soft-1.2),soft+1.4),(max(.18,soft-1.2),soft+1.6),
          (.975,1),(it-2.6,it+2.6)]
  return minimize(error,start,method='Powell',bounds=ranges,options={'maxiter':14,'xtol':.012,'ftol':.002})
 start=[x,y,w,h,max(.2,soft),max(.2,soft),1,it]
 r=search(start)
 loss=error(r.x)
 orig=(np.abs(np.clip((223-old.mean(axis=2))/223,0,1)-ink)*weights).sum()
 print(f,round(orig,2),round(loss,2),np.round(r.x,3))
 if loss<orig*1.24:
  scenes[str(f)]=np.round(r.x,3).tolist()
j['followPointerOptics']=scenes
s.write_text(json.dumps(j,indent=2)+'\n')
