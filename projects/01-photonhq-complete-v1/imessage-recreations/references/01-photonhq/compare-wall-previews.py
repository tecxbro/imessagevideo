from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np,json
R=Path('/workspace/imessage-recreations/references/01-photonhq');O=Path('/workspace/imessage-recreations/outputs/01-photonhq');frames=[246,252,258,264,270,276,282,288,294,318,324,330,336,342,348,351,354,360,366,372,378,384,387,390,393,396,402,408,414,420,423,426,429,432,438,444,450,456,462,465,468,471];rows=[]
for n in frames:
 a=np.array(Image.open(R/f'assets/wall-art/measure/{n:04d}.png').convert('RGB'),dtype=float);b=np.array(Image.open(O/f'wall-v4-{n}.png').convert('RGB'),dtype=float);d=np.abs(a-b);rows.append(dict(frame=n,time=n/30,mae=float(d.mean()),title_band_mae=float(d[470:620].mean()),outside_title_mae=float(np.concatenate([d[:470],d[620:]]).mean())))
(O/'wall-v4-dense-metrics.json').write_text(json.dumps(rows,indent=2));print('mean',np.mean([r['mae'] for r in rows]),'median',np.median([r['mae'] for r in rows]),flush=True);print('worst',sorted(rows,key=lambda r:r['mae'],reverse=True)[:12],flush=True)
selected=[258,270,324,336,354,372,384,387,390,393,396,408,426,429,444,462]
can=Image.new('RGB',(1280,len(selected)*380),'#ddd');d=ImageDraw.Draw(can)
for i,n in enumerate(selected):
 a=Image.open(R/f'assets/wall-art/measure/{n:04d}.png').convert('RGB');b=Image.open(O/f'wall-v4-{n}.png').convert('RGB');m=next(r for r in rows if r['frame']==n);d.text((0,i*380),f'{n/30:.2f}s reference | v4 candidate MAE{m["mae"]:.2f}',fill='black');can.paste(a.resize((640,360)),(0,i*380+20));can.paste(b.resize((640,360)),(640,i*380+20))
can.save(O/'wall-v4-boundary-contact.jpg');
