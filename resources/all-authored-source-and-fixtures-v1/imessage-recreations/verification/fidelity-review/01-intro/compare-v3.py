from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/01-intro';frames=json.loads((P/'anchor-v3-frames.json').read_text());ms=[];panels=[]
for f in frames:
 # Compare exact source native crop; no approximation from neighboring10fps frames.
 a=Image.open(P/'source-crops'/f'{f+1:04d}.png').convert('RGB') if f<240 else Image.open(next((R/'verification/fidelity-review/reference-native-cache/01-photonhq').iterdir())/f'{f:06d}.png').convert('RGB').crop((0,350,1920,800));aa=np.array(a).astype(float);row={};panes=[a]
 for kind in ['base','patch-v3']:
  b=Image.open(P/kind/f'{f}.png').convert('RGB').crop((0,350,1920,800));bb=np.array(b).astype(float);delta=np.abs(aa-bb);mask=np.any(aa<242,2)|np.any(bb<242,2);row[kind+'_crop_mae']=float(delta.mean());row[kind+'_foreground_mae']=float(delta[mask].mean()) if mask.any() else 0;panes.append(b)
 eq=np.array_equal(np.array(panes[1]),np.array(panes[2]));ms.append(dict(frame=f,time=f/30,base_patch_crop_identical=eq,**row));panel=Image.new('RGB',(1920,170),'white');d=ImageDraw.Draw(panel)
 for j,b in enumerate(panes):b.thumbnail((640,150));panel.paste(b,(j*640,20));d.text((j*640+5,0),f'{f/30:.3f}s [{f}] '+['source','v4','intro repair'][j],fill='red')
 panels.append(panel)
for st in range(0,len(panels),12):
 batch=panels[st:st+12];sh=Image.new('RGB',(1920,170*len(batch)),'white')
 for i,p in enumerate(batch):sh.paste(p,(0,170*i))
 sh.save(P/f'comparison-v3-{st//12+1}.jpg',quality=94)
(P/'native-metrics-v3.json').write_text(json.dumps(ms,indent=2));print(json.dumps(ms,indent=1))
