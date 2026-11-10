from pathlib import Path
import json,sys,csv
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).parent;B=P/'early-v13-measure';sys.path.insert(0,str(P.parents[1]/'engines'));import render_pillow as r
s=json.loads((P/'early-v13.scene.json').read_text());r.register_fonts(s,str(P));D=B/'native-check';D.mkdir(exist_ok=True);frames=[0,3,15,53,58,59,83,98,150,177,205,220,311,334,350,358,390];old={int(v['candidate_frame']):float(v['mae'])for v in csv.DictReader(open(P.parents[1]/'verification/timeline-scans/03-photon-mini-v12/frames.csv'))};metrics=[]
for i,f in enumerate(frames):
 im=r.render(s,f/30,str(P),1);im.save(D/f'{f:04d}.png');source=Image.open(B/'validation-source'/f'{i+1:03d}.png').convert('RGB');a=np.asarray(im).astype(float);b=np.asarray(source).astype(float);mae=float(abs(a-b).mean());metrics.append({'frame':f,'new_native_pillow_mae':mae,'old_gsap_mae':old[f]});pair=Image.new('RGB',(1920,570),'#ddd');pair.paste(source.resize((960,540)),(0,30));pair.paste(im.resize((960,540)),(960,30));ImageDraw.Draw(pair).text((10,8),f'Source frame{f}',fill='black');ImageDraw.Draw(pair).text((970,8),f'Native candidate MAE{mae:.3f} oldGSAP{old[f]:.3f}',fill='black');pair.save(D/f'{f:04d}-pair.jpg');print(metrics[-1],flush=True)
(D/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
