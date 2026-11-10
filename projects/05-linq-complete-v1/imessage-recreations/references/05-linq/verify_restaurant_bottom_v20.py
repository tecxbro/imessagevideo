from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
D=Path('verification/05-restaurant-bottom-v20')
rows=[]
for f in range(1143,1151):
    a=np.asarray(Image.open(f'references/05-linq/measurements/native-transition/{f:06}.png').convert('RGB')).astype(np.int16)
    b=np.asarray(Image.open(D/f'{f/30:.3f}.png').convert('RGB')).astype(np.int16)
    c=np.asarray(Image.open(f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB')).astype(np.int16)
    rows.append({'frame':f,'oldMAE':float(abs(a-c).mean()),'newMAE':float(abs(a-b).mean()),'maxDelta':int(abs(b-c).max())})
f=1145
crop=(180,480,780,720)
a=Image.open(f'references/05-linq/measurements/native-transition/{f:06}.png')
b=Image.open(D/f'{f/30:.3f}.png')
out=Image.new('RGB',(1200,265),'white')
out.paste(a.crop(crop),(0,25))
out.paste(b.crop(crop),(600,25))
ImageDraw.Draw(out).text((5,5),'Source1145 | extended static document',fill='black')
out.save(D/'1145-pair.png')
report={'rows':rows,'allChangedImprove':all(x['newMAE']<=x['oldMAE'] for x in rows if 1144<=x['frame']<=1149),'controlsExact':all(x['maxDelta']==0 for x in rows if x['frame'] in [1143,1150])}
(D/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
