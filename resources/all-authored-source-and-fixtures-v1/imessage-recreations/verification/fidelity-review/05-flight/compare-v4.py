from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-flight';cap=json.load(open(P/'check-v4/capture.json'));rows=[];panels=[]
for f,t in zip(cap['frameIndices'],cap['times']):
 c=Image.open(P/'check-v4'/f'{t:.3f}.png').convert('RGB');bp=R/'outputs/05-linq/frames-gsap'/f'{f:06d}.png';b=Image.open(bp).convert('RGB') if bp.exists() else c;sp=P/('source' if 355<=f<=413 else 'pre-source')/f'{f-354 if 355<=f<=413 else f-349:04d}.png';row={'frame':f,'baseline_candidate_pixels_identical':np.array_equal(np.array(b),np.array(c))};ims=[]
 if sp.exists():
  a=Image.open(sp).convert('RGB');aa=np.array(a).astype(float);ims=[a]
  for label,im in [('before',b),('after',c)]:
   bb=np.array(im).astype(float);d=np.abs(aa-bb);m=np.any(aa<242,2)|np.any(bb<242,2);row[label+'_mae']=float(d.mean());row[label+'_foreground_mae']=float(d[m].mean()) if m.any() else 0
 else:ims=[Image.new('RGB',b.size,'white')];row['source_not_decoded_control_only']=True
 ims+=[b,c];rows.append(row);panel=Image.new('RGB',(1440,390),'white');dr=ImageDraw.Draw(panel)
 for i,im in enumerate(ims):im.thumbnail((480,360));panel.paste(im,(i*480,24));dr.text((i*480+4,3),str(f)+' '+['source','v10','flight repair'][i],fill='red')
 panels.append(panel)
sh=Image.new('RGB',(1440,len(panels)*390),'white')
for i,p in enumerate(panels):sh.paste(p,(0,i*390))
sh.save(P/'comparison-v4.jpg',quality=95);(P/'native-metrics-v4.json').write_text(json.dumps(dict(scene=cap['scene'],scene_sha256=cap['sceneSHA256'],frames=rows),indent=2));print(rows)
