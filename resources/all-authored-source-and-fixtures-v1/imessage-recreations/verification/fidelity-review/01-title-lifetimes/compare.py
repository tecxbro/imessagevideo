from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,hashlib
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/01-title-lifetimes';cap=json.load(open(P/'checkpoints-v1/capture.json'));rows=[];panels=[]
for f,t in zip(cap['frameIndices'],cap['times']):
 a=Image.open(P/'source'/f'{f-449:04d}.png').convert('RGB');aa=np.array(a).astype(float);ims=[a];row={'frame':f,'target_roi':[0,350,1920,800]}
 for label,path in [('before',R/'outputs/01-photonhq/frames-gsap'/f'{f:06d}.png'),('after',P/'checkpoints-v1'/f'{t:.3f}.png')]:
  b=Image.open(path).convert('RGB').crop((0,350,1920,800));bb=np.array(b).astype(float);d=np.abs(aa-bb);m=np.any(aa<242,2)|np.any(bb<242,2);row[label+'_crop_mae']=float(d.mean());row[label+'_foreground_mae']=float(d[m].mean()) if m.any() else 0;ims.append(b)
 row['control_equal']=np.array_equal(np.array(ims[1]),np.array(ims[2]));rows.append(row);p=Image.new('RGB',(1920,180),'white');dr=ImageDraw.Draw(p)
 for i,b in enumerate(ims):b.thumbnail((640,150));p.paste(b,(640*i,24));dr.text((640*i+3,3),f'{f} '+['source','v5','repair'][i],fill='red')
 panels.append(p)
for st in range(0,len(panels),8):
 ps=panels[st:st+8];sh=Image.new('RGB',(1920,len(ps)*180),'white')
 for i,p in enumerate(ps):sh.paste(p,(0,i*180))
 sh.save(P/f'comparison-{st//8+1}.jpg',quality=95)
(P/'native-metrics.json').write_text(json.dumps(dict(scene_sha256=hashlib.sha256((R/'outputs/01-photonhq/title-lifetime-review-01/scene.json').read_bytes()).hexdigest(),frames=rows),indent=2));print([(q['frame'],round(q['before_crop_mae'],3),round(q['after_crop_mae'],3)) for q in rows])
