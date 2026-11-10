from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-menu-games';source=R/'references/05-linq/assets/root-handoffs-measure';cap=json.load(open(P/'checkpoints-v2/capture.json'));rows=[];panels=[];(P/'baseline').mkdir(exist_ok=True)
for f,t in zip(cap['frameIndices'],cap['times']):
 b=Image.open(R/'outputs/05-linq/frames-gsap'/f'{f:06d}.png').convert('RGB');b.save(P/'baseline'/f'{f}.png');c=Image.open(P/'checkpoints-v2'/f'{t:.3f}.png').convert('RGB');row={'frame':f,'baseline_candidate_pixels_identical':np.array_equal(np.array(b),np.array(c))};sp=source/f'frame-{f}.png';ims=[]
 if sp.exists():
  a=Image.open(sp).convert('RGB');aa=np.array(a).astype(float);ims=[a]
  for label,im in [('before',b),('after',c)]:
   bb=np.array(im).astype(float);d=np.abs(aa-bb);m=np.any(aa<242,2)|np.any(bb<242,2);row[label+'_mae']=float(d.mean());row[label+'_foreground_mae']=float(d[m].mean()) if m.any() else 0
 else:a=Image.new('RGB',b.size,'white');ims=[a];row['source_not_decoded_control_only']=True
 ims+=[b,c];rows.append(row);panel=Image.new('RGB',(1440,390),'white');dr=ImageDraw.Draw(panel)
 for i,im in enumerate(ims):im.thumbnail((480,360));panel.paste(im,(i*480,24));dr.text((i*480+4,3),str(f)+' '+['source','v10','handoff repair'][i],fill='red')
 panels.append(panel)
sh=Image.new('RGB',(1440,len(panels)*390),'white')
for i,p in enumerate(panels):sh.paste(p,(0,i*390))
sh.save(P/'comparison-v2.jpg',quality=95);(P/'native-metrics-v2.json').write_text(json.dumps(dict(scene_sha256=hashlib.sha256((R/'outputs/05-linq/menu-games-handoff-review-02/scene.json').read_bytes()).hexdigest(),frames=rows),indent=2));print(rows)
