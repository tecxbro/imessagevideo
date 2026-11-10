"""Fit the native gallery camera against exact original anchor frames.

The full composite below is a measurement fixture only. Runtime delivery keeps
eight independent original phone artworks and a native parent camera.
"""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.optimize import minimize

ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent
BASE=ROOT/'outputs/05-linq/final-v9';scene=json.loads((BASE/'scene.json').read_text())
group=next(l for l in scene['layers'] if l['id']=='broad-v5-group-72')
assets=[(c,Image.open(BASE/c['src']).convert('RGBA')) for c in group['children']]
size=(240,180);records=[]
ns=list(range(1200,1227))+[1230,1245,1260,1268]
def y_at(c,t):
 keys=c.get('keyframes',{}).get('y',[])
 a=next((k['value'] for k in keys if k['t']==41.5),c['y'])
 if c['id']=='broad-v5-image-70':a=701;b=685
 b=next((k['value'] for k in keys if k['t']==42),a)
 return a+(t-41.5)*(b-a)/.5
for n in ns:
 t=n/30;template=Image.new('RGBA',(1920,2160),'white')
 for c,im in assets:
  art=im.resize((round(c['width']),round(c['height'])),Image.Resampling.LANCZOS)
  template.alpha_composite(art,(round(c['x']+480),round(y_at(c,t)+720)))
 template=template.convert('RGB')
 ref_image=Image.open(REF/f'assets/root-late-measure/frame-{n:04d}.png').convert('RGB')
 ref=np.array(ref_image.transform(size,Image.Transform.AFFINE,(4,0,0,0,4,0),Image.Resampling.BILINEAR),dtype=np.float32)
 def render(v):
  s,tx,ty=v
  picture=template.transform(size,Image.Transform.AFFINE,(4/s,0,960-(480+tx)/s,0,4/s,1080-(360+ty)/s),Image.Resampling.BILINEAR)
  return np.array(picture,dtype=np.float32)
 def blended(v):
  picture=render(v);alpha=1.
  s,tx,ty=v
  # Fit the complete central phone independently. Incomplete edge phones and
  # their column drift must not bias the common camera's scale/translation.
  main=next(c for c in group['children'] if c['id']=='rich-asset-15')
  lo=max(0,round((480+s*(345-480)+tx)/4));hi=min(240,round((480+s*(617-480)+tx)/4))
  top=max(0,round((360+s*(y_at(main,t)-360)+ty)/4));bottom=min(180,round((360+s*(y_at(main,t)+556-360)+ty)/4))
  region=(slice(top,bottom),slice(lo,hi))
  if n>=1260:
   delta=picture[region]-255;alpha=float(np.clip((delta*(ref[region]-255)).sum()/max((delta*delta).sum(),1),0,1))
  return picture*alpha+255*(1-alpha),alpha,region
 def objective(v):
  picture,alpha,region=blended(v)
  if picture[region].size<3000:return 1e9
  return float(((picture[region]-ref[region])**2).mean())
 # The original broad Powell search jumped into a wrong scale basin after the
 # rapid zoom. Coarse global seeds plus a bounded local fit prevent that retry.
 seeds=[(objective((s,0,y)),np.array([s,0.,y])) for s in np.arange(.95,4.31,.15) for y in [-60.,-20.,20.,60.,100.]]
 seeds.append((objective((1,0,0)),np.array([1.,0.,0.])))
 _,seed=min(seeds,key=lambda p:p[0]);bounds=[(max(.85,seed[0]-.20),min(4.5,seed[0]+.20)),(-20,20),(seed[2]-60,seed[2]+60)]
 result=minimize(objective,seed,method='Powell',bounds=bounds,options={'xtol':.00002,'ftol':.00002,'maxiter':60})
 last=result.x if result.fun<=objective(seed) else seed;picture,alpha,region=blended(last)
 if n==1245:
  # This exact original art was cropped at this native source pose. It is a
  # proven anchor, stronger evidence than an optimizer in a neighboring basin.
  last=np.array([1.,0.,0.]);picture,alpha,region=blended(last)
 row=dict(frame=n,time=t,scale=float(last[0]),x=float(last[1]),y=float(last[2]),opacity=alpha,mse=objective(last),optimizerMSE=result.fun,mae=float(np.abs(picture-ref).mean()))
 records.append(row)
 Image.fromarray(np.uint8(np.clip(picture,0,255))).save(REF/f'assets/root-late-measure/fit-{n:04d}.png')
 print(json.dumps(row),flush=True)
(REF/'assets/root-late/gallery-camera-fit.json').write_text(json.dumps(records,indent=2))
