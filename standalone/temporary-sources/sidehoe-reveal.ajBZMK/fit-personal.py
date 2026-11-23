from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import map_coordinates, gaussian_filter
from scipy.optimize import least_squares
r=Path(__file__).parent
sys.path.insert(0,str(r/'project'))
from render import interpolate,measured_wash
from artwork import messages_font
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
d=json.loads((r/'project/scene.json').read_text());t=d['tracks']
for j,w in enumerate((620,700),1):
 line=d['copy']['personal'][j-1]
 face=messages_font(160,w)
 p=Image.new('L',(int(face.getlength(line))+20,186))
 ImageDraw.Draw(p).text((4,4),line,font=face,fill=255,anchor='lt')
 p=p.crop(p.getbbox()).resize((620,145),Image.Resampling.BICUBIC)
 shape=np.asarray(p).astype('float32')/255
 out=[]
 for f in range(184,213):
  x0,y0,span,oldh=interpolate(t[f'personalLine{j}'],f)
  if y0+oldh<2: continue
  src_im=np.asarray(Image.open(src/f'{f:06}.png')).astype('float32')
  lighting=np.asarray(measured_wash(tuple(interpolate(t['titleWashFields'],f))))[:,:,:3].astype('float32')
  c=src_im[round(max(0,y0-10)):round(y0+oldh+12),round(x0):round(x0+span)]
  dark=c[c.mean(-1)<np.quantile(c.mean(-1),.21)]
  ink = np.quantile(dark,.34,axis=0) if len(dark) else [0,0,0]
  if f>199: ink=np.minimum(ink,[15,16,15])
  x,y=np.meshgrid(np.arange(round(x0-12),round(x0+span+13),2),np.arange(max(0,round(y0-17)),round(y0+oldh+23),2))
  b=lighting[y,x]; a=src_im[y,x]
  chroma=(a[:,:,2]-a[:,:,1])-(b[:,:,2]-b[:,:,1])
  lip=np.clip((b[:,:,0]-a[:,:,0])/np.maximum(1,b[:,:,0]-ink[0]),0,1.03)
  sure=np.where((chroma>40)&(lip<.44),.16,1)
  if j==1 and f<187: sure*=np.where(lip<.11,.62,1)
  blurx=.45+np.interp(f,[184,202,205,208,210,212],[0,0,.5,.9,1.5,2.1])
  blury=.47+np.interp(f,[184,202,205,208,210,212],[0,0,.7,1.4,2.8,7.2])
  smooth=gaussian_filter(shape,(blury*144/oldh,blurx*619/span))
  def resid(u):
    bx,by,bw,bh,op=u
    v=map_coordinates(smooth,[(y-by)*144/bh,(x-bx)*619/bw],order=1,mode='constant',cval=0,prefilter=False)
    return ((v*op-lip)*sure).ravel()
  lb=[x0-8,y0-16,span*.95,oldh*.66,.44]
  ub=[x0+8,y0+12,span*1.06,oldh*1.13,1.04]
  seed=[x0,y0,span,oldh,.99]
  g=least_squares(resid,seed,bounds=(lb,ub),diff_step=.0016,max_nfev=40)
  out.append([f,*np.round(g.x,4).tolist(),round(blurx,4),round(blury,4),*np.clip(np.rint(ink),0,245).astype(int).tolist()])
  print(j,f,out[-1],round(np.mean(np.abs(g.fun)),4),flush=True)
 (r/f'personal-type-{j}.json').write_text(json.dumps(out,indent=2))
