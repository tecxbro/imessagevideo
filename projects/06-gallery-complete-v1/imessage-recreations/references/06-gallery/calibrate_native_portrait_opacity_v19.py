"""Calibrate early opacity from actual native per-disc RGBA compositing.
The arrays are measurement-only; output remains the same15static native nodes.
"""
from pathlib import Path
import copy,json,sys
import numpy as np
from PIL import Image
P=Path(__file__).parent;B=P/'portrait-helper-v18';sys.path.insert(0,str(P.parents[1]/'engines'));import render_pillow
S=json.load(open(B/'combined-validation.scene.json'));data=json.load(open(B/'camera-fit-frozen-v18.json'));W,H=480,270
eligible={'71':614,'75':621,'79':613,'85':618,'89':617,'93':614,'new-foliage-woman':614,'77':613}
def id_of(g):
 semantic=g['semanticPhotoId']
 return next(id for id in data if semantic in['rene-final11-group-'+id,'rene-portrait-'+id])
def draw(ls,f,transparent=False):
 def rgb(background):
  scene={**S,'layers':ls,'background':background};im=render_pillow.render(scene,f/30,str(P)).resize((W,H),Image.Resampling.LANCZOS).convert('RGB');return np.asarray(im,dtype=np.float32)/255
 if not transparent:return rgb(S.get('background','#ffffff')),np.ones((H,W,1),np.float32)
 # The native export API returns RGB. Recover its true transparent layer by
 # rendering on black/white measurement mattes; never assume convert(RGBA)
 # can restore discarded alpha. Output scenes/assets are unaffected.
 black=rgb('#000000');white=rgb('#ffffff');alpha=np.clip(1-np.mean(white-black,axis=2,keepdims=True),0,1);return np.minimum(black,alpha),alpha
report=[]
for f in range(603,621):
 t=f/30;active=[(i,g)for i,g in enumerate(S['layers'])if g.get('semanticPhotoId')and g.get('start',0)<=t<g.get('end',S['duration'])];indices=[i for i,g in active];bg,_=draw(S['layers'][:min(indices)],f);fg,fa=draw(S['layers'][max(indices)+1:],f,True);photos=[];prefixes=[];C=bg.copy()
 for i,g in active:
  id=id_of(g);r=next(r for r in data[id]if r['frame']==f);p=float(r['opacity']);allowed=f>=eligible.get(id,603)
  if not allowed:p=0.
  pure=copy.deepcopy(g);pure.setdefault('keyframes',{}).pop('opacity',None);pure['opacity']=1.;rgb,alpha=draw([pure],f,True);photos.append({'id':id,'rgb':rgb,'alpha':alpha,'p':p,'allowed':allowed});prefixes.append(C.copy());C=rgb*p+C*(1-alpha*p)
 F=fg+C*(1-fa);ref=np.asarray(Image.open(P/f'native-transition-v18/{f:06d}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS),dtype=np.float32)/255;before=float(abs(F-ref).mean()*255);T=1-fa
 for photo,prefix in reversed(list(zip(photos,prefixes))):
  old=photo['p'];d=T*(photo['rgb']-photo['alpha']*prefix);den=float(np.sum(d*d));p=old
  if photo['allowed']and den>1e-5:p=float(np.clip(old+np.sum(d*(ref-F))/den,0,1))
  delta=p-old;F+=delta*d;T*=1-photo['alpha']*p;photo['p']=p
  r=next(r for r in data[photo['id']]if r['frame']==f);r['opacity']=p;r['opacityMeasurement']='Actual native RGBA layer energy, not OCR confidence; bounded near-plane photometric fit.'
 after=float(abs(F-ref).mean()*255);row={'frame':f,'native_prediction_mae_before':before,'native_prediction_mae_after':after,'opacities':{p['id']:p['p']for p in photos}};report.append(row);print(f,before,after,flush=True)
(B/'camera-fit-native-opacity-v19.json').write_text(json.dumps(data,indent=2)+'\n');(B/'native-opacity-calibration-v19.json').write_text(json.dumps(report,indent=2)+'\n')
