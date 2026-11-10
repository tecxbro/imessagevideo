"""Measure early-pop label opacity/blur; preserve all held states from133."""
from pathlib import Path
import json,sys,copy,hashlib
import numpy as np
from PIL import Image,ImageFilter
P=Path(__file__).parent;R=P.parents[1];M=P/'games-pop-v18-measure';O=P/'assets/games-pop-v18';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
scene=json.load(open(M/'candidate.scene.json'));g=next(n for n in scene['layers']if n['id']=='g-138');by={n['id']:n for n in g['children']};spec=json.load(open(M/'spec-working.json'));reports=[]
# The omitted first blurred header is one bounded component pose, matching the
# already-authorized one-frame blurred-label material treatment.
ref=Image.open(M/'source/000130.png').convert('RGB');box=[375,55,610,134];a=np.array(ref);assert a[129:134,375:610].min()>=250 and a[55:58,375:610].min()>=250,'Header separator is not clean';file=O/'header-blur-130.png';ref.crop(box).save(file);meta={'sourceFrame':130,'sourceBounds':box,'kind':'Single original Games header/icon blurred entrance pose only; native held header and icon resume131. No drawer/card/body pixels.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()};spec['materialNodes'].append({'id':'games-pop-v18-header-130','type':'image','src':str(file.resolve()),'x':box[0],'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':130/30,'end':131/30,'semanticText':'Games header','provenance':meta});spec['materialLedger'].append(meta)
for f in (131,132):
 source=np.array(Image.open(M/'source'/f'{f:06}.png').convert('RGB'),dtype=float);meas=next(x for x in spec['measurements']if x['frame']==f)['tiles']
 for i in range(6):
  id=f'root-games-label-{i}';n=by[id];rgb=np.array(rp.render({**scene,'layers':[n],'background':'#ffffff'},f/30,str(M)),dtype=float);ink=np.mean(rp.rgba(n['fill'])[:3]);alpha=np.clip((255-rgb.mean(2))/(255-ink),0,1);yy,xx=np.where(alpha>.02);x0=max(0,int(xx.min())-10);x1=min(960,int(xx.max())+11);y0=max(meas[i]['observedFullBox'][3]+2,int(yy.min())-10);y1=min(720,int(yy.max())+11);target=np.clip((255-source[y0:y1,x0:x1].mean(2))/(255-ink),0,1);mask=Image.fromarray(np.uint8(np.rint(alpha*255)));best=None;baseline=float(np.mean((alpha[y0:y1,x0:x1]-target)**2))
  for blur in (0,.25,.5,.75,1,1.5,2,2.5,3):
   pred=np.asarray(mask.filter(ImageFilter.GaussianBlur(blur)),dtype=float)[y0:y1,x0:x1]/255;opacity=float(np.clip(np.sum(pred*target)/max(np.sum(pred*pred),1e-9),.5,1));loss=float(np.mean((pred*opacity-target)**2));rec={'frame':f,'label':id,'blur':blur,'opacity':opacity,'beforeMse':baseline,'afterMse':loss}
   if best is None or loss<best['afterMse']:best=rec
  accepted=best['afterMse']<baseline*.85;best['accepted']=accepted;reports.append(best)
  if accepted:
   rows=spec['labelUpdates'].setdefault(id,[]);u=next((q for q in rows if q['frame']==f),None)
   if u is None:
    st=rp.state(n,f/30);u={'frame':f,'x':st['x'],'y':st['y'],'ncc':None};rows.append(u)
   u.update(blur=best['blur'],opacity=best['opacity']);rows.sort(key=lambda q:q['frame'])
  print(best,flush=True)
spec['opticsMeasurements']=reports;(M/'spec-optics-working.json').write_text(json.dumps(spec,indent=2)+'\n');(O/'provenance.json').write_text(json.dumps(spec['materialLedger'],indent=2)+'\n')
