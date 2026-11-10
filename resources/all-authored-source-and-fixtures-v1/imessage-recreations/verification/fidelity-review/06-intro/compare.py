from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,hashlib
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-intro'
for version in [1,2]:
 cap=json.load(open(P/f'checkpoints-v{version}/capture.json'));rows=[];panels=[]
 for f,t in zip(cap['frameIndices'],cap['times']):
  a=Image.open(P/'source'/f'{f+1:04d}.png').convert('RGB');aa=np.array(a).astype(float);ims=[a];row={'frame':f}
  for label,path in [('before',R/'outputs/06-gallery/frames-gsap'/f'{f:06d}.png'),('after',P/f'checkpoints-v{version}'/f'{t:.3f}.png')]:
   b=Image.open(path).convert('RGB');bb=np.array(b).astype(float);d=np.abs(aa-bb);m=np.any(aa<242,2)|np.any(bb<242,2);row[label+'_mae']=float(d.mean());row[label+'_foreground_mae']=float(d[m].mean()) if m.any() else 0;ims.append(b)
  row['control_equal']=np.array_equal(np.array(ims[1]),np.array(ims[2]));rows.append(row);p=Image.new('RGB',(1920,390),'white');dr=ImageDraw.Draw(p)
  for i,b in enumerate(ims):b.thumbnail((640,360));p.paste(b,(640*i,24));dr.text((640*i+3,3),f'{f} '+['source','v17','repair'][i],fill='red')
  panels.append(p)
 for st in range(0,len(panels),6):
  ps=panels[st:st+6];sh=Image.new('RGB',(1920,len(ps)*390),'white')
  for i,p in enumerate(ps):sh.paste(p,(0,i*390))
  sh.save(P/f'comparison-v{version}-{st//6+1}.jpg',quality=95)
 out=dict(scene_sha256=hashlib.sha256((R/f'outputs/06-gallery/intro-review-0{version}/scene.json').read_bytes()).hexdigest(),frames=rows);(P/f'native-metrics-v{version}.json').write_text(json.dumps(out,indent=2));print('version',version,[(q['frame'],round(q['before_mae'],3),round(q['after_mae'],3)) for q in rows],flush=True)
