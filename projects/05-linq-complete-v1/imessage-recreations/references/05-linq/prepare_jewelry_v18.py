"""Restore one bounded upper static UI document and measured native entrance."""
from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;R=D.parent.parent;BASE=R/'outputs/05-linq/final-v17';s=json.loads((BASE/'scene.json').read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((BASE/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for x in o:absolute(x)
absolute(s)
old=next(q for q in s['layers'] if q['id']=='broad-v5-group-62');cam=old['children'][0];oldim=cam['children'][0]
F=D/'measurements/native-transition'
def load(f):return np.array(Image.open(F/f'{f:06d}.png').convert('RGB')).astype(np.float64)
a581=load(581);prefix=a581[219:641,198:763].astype(np.uint8)
# These four exterior columns contained the backdrop outside the source UI.
# Native rounded clipping supplies the card silhouette independently.
prefix[:,:4]=255
A=D/'assets/jewelry-v18';A.mkdir(exist_ok=True);p=A/'upper-document.png';Image.fromarray(prefix).save(p)
# Existing lower document starts at world640.417578429 in source581.
# Prefix origin219 therefore gives a measured native offset421.417578429.
offset=next(k['value']for k in cam['keyframes']['y'] if round(k['t']*30)==581)-219
lower=np.array(Image.open(oldim['src']).convert('RGB')).astype(float);pg=255-prefix.mean(2);lg=255-lower.mean(2)
# Fixed native x samples exclude outer rounded-corner/viewport optics.
xs=np.arange(30,535,3);ys=np.arange(0,720,2);xx,yy=np.meshgrid(xs,ys)
rows=[]
for f in range(578,600):
 target=255-load(f)[:,198:763].mean(2)
 oldy=next(k['value']for k in cam['keyframes']['y']if round(k['t']*30)==f)
 if f<=585:
  a=load(f);ink=np.sum(np.min(a[:,447:512],axis=2)<90,axis=1);z=np.where(ink>40)[0]
  # Restrict to the unique top handle, excluding necklace silhouettes.
  z=z[z<450];initial=float(np.median(z)-10) if len(z) else oldy-offset
 else:initial=oldy-offset
 if f in [584,585]:initial=10.5
 if f==587:initial=-96.5
 mask=(yy>=max(0,initial+25))
 # Include handle/heading below the top boundary but omit rounded side corners.
 ty=yy[mask].astype(float);tx=xx[mask].astype(float);obs=target[yy[mask],xx[mask]]
 def ink(y):
  ly=ty-y;v=np.zeros_like(ly);m=(ly>=0)&(ly<offset)
  v[m]=map_coordinates(pg,[ly[m],tx[m]],order=1,mode='constant',cval=0,prefilter=False)
  m=(ly>=offset)&(ly<offset+len(lg));v[m]=map_coordinates(lg,[ly[m]-offset,tx[m]],order=1,mode='constant',cval=0,prefilter=False)
  return v
 def residual(v):return (ink(v[0])*v[1]-obs)/40
 fit=least_squares(residual,[initial,1],bounds=([initial-10,.8],[initial+10,1.15]),max_nfev=60,diff_step=[.001,.001])
 rows.append({'frame':f,'topY':round(float(fit.x[0]),6),'inkFitAlpha':round(float(fit.x[1]),6),'initialTopY':initial,'oldLowerY':oldy,'rmse':float(np.sqrt(np.mean(residual(fit.x)**2))),'renderOpacity':1})
 print(rows[-1],flush=True)
# Native clip is independent of the fixed outer viewport and native camera.
body={'type':'group','id':'v18-jewelry-complete-document','clip':{'x':198,'y':0,'width':565,'height':offset+844,'radius':52},'children':[{'type':'image','id':'v18-jewelry-upper-static-ui','src':str(p),'x':198,'y':0,'width':565,'height':422},copy.deepcopy(oldim)]}
body['children'][1]['id']='v18-jewelry-existing-lower-ui';body['children'][1]['y']=offset
camera={'type':'group','id':'v18-jewelry-entrance-camera','children':[body],'keyframes':{'y':[{'t':r['frame']/30,'value':r['topY'],'ease':'linear'}for r in rows]}}
private={'type':'group','id':'v18-jewelry-entrance-viewport','start':578/30,'end':600/30,'clip':copy.deepcopy(old['clip']),'children':[camera]}
old['start']=600/30
s['layers'].insert(s['layers'].index(old),private)
(D/'scene-jewelry-v18.json').write_text(json.dumps(s,indent=2)+'\n')
spec={'range':[578,599],'base':'outputs/05-linq/final-v17/scene.json','offset':offset,'prefixSourceFrame':581,'prefixSourceBounds':[198,219,763,641],'prefixSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'lowerAssetSHA256':hashlib.sha256(Path(oldim['src']).read_bytes()).hexdigest(),'rows':rows,'model':'One original upper static UI crop plus accepted original lower static UI, native rounded document clip and per-frame native rigid camera. Source pixels calibrate poses; only these two static document pieces render.'}
(D/'jewelry-v18-measurements.json').write_text(json.dumps(spec,indent=2)+'\n')
(A/'provenance.json').write_text(json.dumps({k:v for k,v in spec.items()if k!='rows'},indent=2)+'\n')
