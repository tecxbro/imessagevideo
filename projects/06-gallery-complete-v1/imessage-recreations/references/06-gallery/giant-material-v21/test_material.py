"""Single actor higher-resolution material attribution; physical camera unchanged."""
from pathlib import Path
import sys,json,copy,hashlib
import numpy as np
from PIL import Image,ImageDraw
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));import render_pillow as rp
p=root/'references/06-gallery/giant-material-v21';src=root/'outputs/06-gallery/final-v20/scene.json';s=json.load(open(src))
def absolute(ls):
 for n in ls:
  if n.get('src') and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((src.parent/n['src']).resolve())
  absolute(n.get('children',[]))
absolute(s['layers']);f=622;q=next(n for n in s['layers']if n.get('semanticPhotoId')=='rene-final11-group-79'and n.get('start',0)<=f/30<n.get('end',99));st=rp.state(q,f/30);w,h=q['children'][0]['width'],q['children'][0]['height'];D=w*st['scaleX'];N=512;box=(st['x'],st['y'],st['x']+D,st['y']+D);ref=Image.open(root/'references/06-gallery/native-transition-v18'/f'{f:06}.png').convert('RGB');sample=ref.transform((N,N),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC);alpha=Image.open(q['children'][0]['src']).convert('RGBA').getchannel('A').resize((N,N),Image.Resampling.BICUBIC);rgba=sample.convert('RGBA');rgba.putalpha(alpha);file=p/'portrait79-source622-material.png';rgba.save(file)
spec={'sourceNativeFrame':f,'sourceWorldBox':box,'sampledPhoto':'rene-final11-group-79','intrinsicSourceDiameter':D,'outputTextureSize':[N,N],'alpha':'Preserved existing static portrait alpha silhouette in normalized UV; source RGB sampled only for this photographed actor.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()};(p/'material-provenance.json').write_text(json.dumps(spec,indent=2)+'\n')
rows=[]
for frame in (614,615):
 t=frame/30;trial=copy.deepcopy(s);g=next(n for n in trial['layers']if n.get('semanticPhotoId')=='rene-final11-group-79'and n.get('start',0)<=t<n.get('end',99));old=rp.state(g,t);child=g['children'][0];ow,oh=child['width'],child['height'];child.update(src=str(file),width=N,height=N);g['keyframes']['scaleX']=[{**k,'value':k['value']*ow/N}for k in g['keyframes']['scaleX']];g['keyframes']['scaleY']=[{**k,'value':k['value']*oh/N}for k in g['keyframes']['scaleY']];g['keyframes']['blur']=[{**k,'value':k['value']*N/ow}for k in g['keyframes']['blur']]
 for k in ('x','y','blur'):g['shadow'][k]*=N/ow
 reference=Image.open(root/'references/06-gallery/native-transition-v18'/f'{frame:06}.png').convert('RGB');before=rp.render(s,t,str(src.parent));after=rp.render(trial,t,str(src.parent));after.save(p/f'{frame:06}-trial.png');before.save(p/f'{frame:06}-baseline.png');a=np.array(reference,dtype=float);r={'frame':frame,'before':float(abs(a-np.array(before,dtype=float)).mean()),'after':float(abs(a-np.array(after,dtype=float)).mean()),'worldCameraPreserved':{'oldBox':[old['x'],old['y'],ow*old['scaleX'],oh*old['scaleY']],'newBox':[old['x'],old['y'],N*rp.state(g,t)['scaleX'],N*rp.state(g,t)['scaleY']],'oldBlurWorld':old['blur']*old['scaleX'],'newBlurWorld':rp.state(g,t)['blur']*rp.state(g,t)['scaleX']}};rows.append(r);(p/'material-test.json').write_text(json.dumps(rows,indent=2)+'\n');print(r,flush=True)
 sheet=Image.new('RGB',(1440,296),'#ddd');d=ImageDraw.Draw(sheet)
 for j,(label,im)in enumerate((('source',reference),('V20 native',before),('source622 material',after))):sheet.paste(im.resize((480,270)),(j*480,26));d.text((j*480+10,5),f'{frame} {label}',fill='black')
 sheet.save(p/f'{frame:06}-contact.jpg')
