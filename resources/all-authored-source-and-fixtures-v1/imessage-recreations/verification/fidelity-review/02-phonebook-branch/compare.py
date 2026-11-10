from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
P=Path('/workspace/imessage-recreations/verification/fidelity-review/02-phonebook-branch');frames=[390,399,406,411,414,415,465,477,480,489,495,499];out=[];sheet=Image.new('RGB',(1950,len(frames)*160),'white');d=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
 isq=f<460;kind='query' if isq else 'uber';crop=(300,430,1600,660) if isq else (1160,150,1840,380);ref=Image.open(P/f'{kind}-{f}.png');rr=np.array(ref).astype(float)
 metrics={};panes=[ref]
 for name in ['base','patch']:
  p=P/f'{name}-{f}.png'
  if not p.exists():continue
  cand=Image.open(p).crop(crop);cc=np.array(cand).astype(float);metrics[name+'_crop_mae']=float(np.abs(rr-cc).mean());mask=np.any(rr<240,2)|np.any(cc<240,2);metrics[name+'_foreground_mae']=float(np.abs(rr-cc)[mask].mean()) if mask.any() else 0;panes.append(cand)
 out.append(dict(frame=f,time=f/30,region=kind,**metrics))
 for j,pane in enumerate(panes):
  pane.thumbnail((640,135));sheet.paste(pane,(j*650,i*160+20));d.text((j*650,i*160),f'{kind} {f} '+['source','baseline','patch'][j],fill='red')
(P/'comparison.jpg').write_bytes(b'') if False else None
sheet.save(P/'comparison.jpg',quality=93);(P/'metrics.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=1))
