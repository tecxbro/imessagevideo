from pathlib import Path
import json,sys,numpy as np,time
from PIL import Image
R=Path('/workspace/imessage-recreations');sys.path.insert(0,str(R/'engines'));import render_pillow as rp
P=R/'references/05-linq/games-pop-v18-measure';A=R/'outputs/05-linq/final-v17/scene.json';a=json.load(open(A));b=json.load(open(P/'candidate.scene.json'));rp.register_fonts(a,str(A.parent));rows=[];out=P/'native';out.mkdir(exist_ok=True)
for f in list(range(130,146))+[127,128,129,146,147,148]:
 source=Image.open(P/'source'/f'{f:06}.png').convert('RGB');before=rp.render(a,f/30,str(A.parent));after=rp.render(b,f/30,str(P));after.save(out/f'{f:06}.png');arr=np.array(source,dtype=float);delta=abs(np.array(before,dtype=float)-np.array(after,dtype=float));r={'frame':f,'before':float(abs(arr-np.array(before,dtype=float)).mean()),'after':float(abs(arr-np.array(after,dtype=float)).mean()),'oldNewMax':int(delta.max())};rows.append(r);(P/'native-metrics.json').write_text(json.dumps(rows,indent=2)+'\n');print(r,flush=True)
