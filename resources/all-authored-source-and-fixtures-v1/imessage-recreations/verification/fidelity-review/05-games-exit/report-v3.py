from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,html
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-games-exit';out=R/'outputs/05-linq/games-exit-review-03';rows=[];panels=[]
for f in [145,146,147,148,149]:
 cap='check-v1'if f==145 else'check-v3';c=Image.open(P/cap/f'{f/30:.3f}.png').convert('RGB');b=Image.open(R/'outputs/05-linq/frames-gsap'/f'{f:06d}.png').convert('RGB');sp=R/'references/05-linq/assets/root-games-measure'/f'frame-{f:04d}.png';row={'frame':f,'baseline_candidate_pixels_identical':np.array_equal(np.array(b),np.array(c))};ims=[]
 if sp.exists():
  a=Image.open(sp).convert('RGB');aa=np.array(a).astype(float);ims=[a]
  for label,im in [('before',b),('after',c)]:
   bb=np.array(im).astype(float);d=abs(aa-bb);mask=np.any(aa<242,2)|np.any(bb<242,2);row[label+'_mae']=float(d.mean());row[label+'_foreground_mae']=float(d[mask].mean())
 else:ims=[Image.new('RGB',b.size,'white')];row['source_not_decoded_control_only']=True
 ims+=[b,c];rows.append(row);panel=Image.new('RGB',(1440,390),'white');dr=ImageDraw.Draw(panel)
 for i,im in enumerate(ims):im.thumbnail((480,360));panel.paste(im,(i*480,24));dr.text((i*480+4,3),str(f)+' '+['source','v10','reviewed exit'][i],fill='red')
 panels.append(panel)
sh=Image.new('RGB',(1440,len(panels)*390),'white')
for i,p in enumerate(panels):sh.paste(p,(0,i*390))
sh.save(P/'comparison-v3.jpg',quality=95);acceptance=dict(status='Scoped review accepted with declared AA/source-compression residuals; not100%',scene=str(out/'scene.json'),scene_sha256=hashlib.sha256((out/'scene.json').read_bytes()).hexdigest(),helper=str(R/'references/05-linq/apply-games-exit-review.py'),elements=str(out/'games-exit-review-elements.json'),changed_native_frames=[[146,148]],outside_proof='all-frame-scope-proof-v3.json',native_metrics=rows,limitations=['Actual bounded animated tile bitmap interiors and isolated148 incoming chess RGBA entry pose; no complete frame/video playback.','Header/labels use native contour paths and fitted opacity; WORDGAMES baseline shifted4px from146.','First-chess149+ and Games129–145 controls preserved. No full MP4 render here.']);(P/'acceptance.json').write_text(json.dumps(acceptance,indent=2));(P/'native-metrics-v3.json').write_text(json.dumps(rows,indent=2));print(rows)
