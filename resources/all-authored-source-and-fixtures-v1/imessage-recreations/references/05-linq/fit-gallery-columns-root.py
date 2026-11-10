"""Fit independent column drift after the common gallery camera is measured."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.optimize import minimize_scalar
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent
BASE=ROOT/'outputs/05-linq/final-v9';scene=json.loads((BASE/'scene.json').read_text())
group=next(l for l in scene['layers'] if l['id']=='broad-v5-group-72')
records=json.loads((REF/'assets/root-late/gallery-camera-fit.json').read_text())
size=(240,180)
def y_at(c,t):
 keys=c.get('keyframes',{}).get('y',[]);a=next((k['value'] for k in keys if k['t']==41.5),c['y']);b=next((k['value'] for k in keys if k['t']==42),a)
 if c['id']=='broad-v5-image-70':a,b=701,685
 return a+(t-41.5)*(b-a)/.5
for row in records:
 n=row['frame'];t=n/30;s=row['scale'];tx=row['x'];ty=row['y'];alpha=row['opacity']
 ref=np.array(Image.open(REF/f'assets/root-late-measure/frame-{n:04d}.png').convert('RGB').transform(size,Image.Transform.AFFINE,(4,0,0,0,4,0),Image.Resampling.BILINEAR),np.float32)
 for col,x1,x2 in [('left',30,301),('right',662,932)]:
  lo=max(0,round((480+s*(x1-480)+tx)/4));hi=min(240,round((480+s*(x2-480)+tx)/4))
  if hi-lo<8:row[col+'_dy']=0.;continue
  template=Image.new('RGBA',(1920,2160),(255,255,255,255))
  for c in group['children']:
   if not (x1<=c['x']<x2):continue
   file=REF/'assets/root-late/gallery-left-chat-extended-preserving-hold.png' if c['id']=='rich-asset-17' else BASE/c['src']
   image=Image.open(file).convert('RGBA');template.alpha_composite(image,(round(c['x']+480),round(y_at(c,t)+720)))
  template=template.convert('RGB')
  def error(dy):
   picture=np.array(template.transform(size,Image.Transform.AFFINE,(4/s,0,960-(480+tx)/s,0,4/s,1080-(360+ty)/s-dy),Image.Resampling.BILINEAR),np.float32)
   picture=picture*alpha+255*(1-alpha)
   return float(((picture[:,lo:hi]-ref[:,lo:hi])**2).mean())
  seed=min(np.arange(-140,141,4),key=error)
  fit=minimize_scalar(error,bounds=(seed-4,seed+4),method='bounded',options={'xatol':.0001})
  row[col+'_dy']=float(fit.x);row[col+'_mse']=float(fit.fun)
 print(json.dumps({k:v for k,v in row.items() if k in ['frame','left_dy','right_dy','left_mse','right_mse']}),flush=True)
(REF/'assets/root-late/gallery-camera-columns-fit.json').write_text(json.dumps(records,indent=2))
