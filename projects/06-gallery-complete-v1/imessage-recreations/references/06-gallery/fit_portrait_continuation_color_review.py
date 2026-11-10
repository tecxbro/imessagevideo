"""Measured RGB contrast of independent genuine photographs, static alpha unchanged."""
from pathlib import Path
import copy,json,sys,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(P/'continuation-fit.scene.json'));rp.register_fonts(S,str(BASE));rows=[]
def median(v,w):
 idx=np.argsort(v);vv=v[idx];ww=w[idx];return float(vv[np.searchsorted(np.cumsum(ww),ww.sum()/2)])
for f in [616,617,618]:
 ref=np.array(Image.open(P/'source'/f'{f:06}.png').convert('RGB'),dtype=float);t=f/30
 for idx,n in enumerate(S['layers']):
  if not n.get('semanticPhotoId')or not(n.get('start',0)<=t<n.get('end',99))or rp.state(n,t)['opacity']<=.01:continue
  child=n['children'][0];file=Path(child['src']);file=file if file.is_absolute()else BASE/file;im=Image.open(file).convert('RGBA');white=Image.new('RGBA',im.size,'white');white.putalpha(im.getchannel('A'));wp=P/f'continuation-white-photo-{f}-{idx}.png';white.save(wp);q=copy.deepcopy(S);q['layers'][idx]['children'][0]['src']=str(wp);F=np.array(rp.render(S,t,str(BASE)),dtype=float);W=np.array(rp.render(q,t,str(BASE)),dtype=float);D=W-F;T=W-ref;gains=[]
  for ch in range(3):
   mask=D[:,:,ch]>25
   if mask.sum()<50:gains.append(1.);continue
   gains.append(float(np.clip(median((T[:,:,ch]/np.maximum(.1,D[:,:,ch]))[mask],D[:,:,ch][mask]),.8,1.2)))
  a=np.array(im,dtype=float);a[:,:,:3]=255-(255-a[:,:,:3])*np.array(gains);a=np.uint8(np.clip(a,0,255).round());out=P/f'continuation-color-photo-{f}-{idx}.png';Image.fromarray(a).save(out);q['layers'][idx]['children'][0]['src']=str(out);C=np.array(rp.render(q,t,str(BASE)),dtype=float);before=float(abs(F-ref).mean());after=float(abs(C-ref).mean());accepted=after<before-.005
  if accepted:S=q
  row=dict(frame=f,id=n['id'],photo=n['semanticPhotoId'],gains=gains,before=before,after=after,accepted=accepted,source=str(file),material=str(out));rows.append(row);print(row,flush=True);(P/'continuation-color.json').write_text(json.dumps(rows,indent=2));(P/'continuation-color.scene.json').write_text(json.dumps(S,indent=2));rp.LEAF_CACHE.clear();rp.GROUP_CACHE.clear();rp.FAST_CACHE.clear()
 rp.render(S,t,str(BASE)).save(P/f'continuation-color-{f}.png')
