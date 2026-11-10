from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/01-intro';frames=json.loads((P/'anchor-final-v2-frames.json').read_text());extra=json.loads((P/'source-extra-map.json').read_text());rows=[];panels=[]
def source(f):
 if str(f) in extra:return Image.open(P/extra[str(f)]).convert('RGB'),True
 if 510<=f<=525:return Image.open(P/'source-onus-exit'/f'{f-509:04d}.png').convert('RGB'),True
 if 42<=f<=55:return Image.open(P/'source-full-early-pill'/f'{f-41:04d}.png').convert('RGB'),True
 if 54<=f<=85:return Image.open(P/'source-full-click'/f'{f-53:04d}.png').convert('RGB'),True
 if f<240:return Image.open(P/'source-crops'/f'{f+1:04d}.png').convert('RGB'),False
 return Image.open(next((R/'verification/fidelity-review/reference-native-cache/01-photonhq').iterdir())/f'{f:06d}.png').convert('RGB'),True
for f in frames:
 a,full=source(f);roi=(0,350,1920,800) if f<240 else (0,0,1920,1080)
 a=a.crop(roi) if full else a
 aa=np.asarray(a).astype(float);row={'frame':f,'time':f/30,'roi':list(roi),'full_source_available':full};panes=[a]
 for kind in ['base','patch-final-v2']:
  b=Image.open(P/kind/f'{f}.png').convert('RGB').crop(roi);bb=np.asarray(b).astype(float);delta=np.abs(aa-bb);mask=np.any(aa<242,2)|np.any(bb<242,2);row[kind+'_mae']=float(delta.mean());row[kind+'_foreground_mae']=float(delta[mask].mean()) if mask.any() else 0;panes.append(b)
 row['base_patch_pixels_identical']=np.array_equal(np.asarray(panes[1]),np.asarray(panes[2]));rows.append(row)
 height=180 if f<240 else 380;panel=Image.new('RGB',(1920,height),'white');d=ImageDraw.Draw(panel)
 for j,b in enumerate(panes):
  b.thumbnail((640,height-24));panel.paste(b,(j*640,24));d.text((j*640+5,3),f'{f/30:.3f}s [{f}] '+['source','v4 before','repair'][j],fill='red')
 panels.append((f,panel))
for section, subset in [('intro',[p for f,p in panels if f<240]),('cta',[p for f,p in panels if f>=510])]:
 for st in range(0,len(subset),8):
  batch=subset[st:st+8];sh=Image.new('RGB',(1920,sum(p.height for p in batch)),'white');y=0
  for p in batch:sh.paste(p,(0,y));y+=p.height
  sh.save(P/f'comparison-final-v2-{section}-{st//8+1}.jpg',quality=95)
report={'scene_sha256':hashlib.sha256((R/'outputs/01-photonhq/intro-cta-review-02/scene.json').read_bytes()).hexdigest(),'frames':rows,'note':'Intro target crop only; CTA full frame. Direct unencoded native PNGs. AA and approximate solid glyph fills remain.'}
(P/'native-metrics-final-v2.json').write_text(json.dumps(report,indent=2));print(json.dumps(rows,indent=1))
