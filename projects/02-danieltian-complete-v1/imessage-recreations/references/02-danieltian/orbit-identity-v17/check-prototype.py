from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys
R=Path(__file__).resolve().parent;O=R.parents[2]/'outputs/02-danieltian/orbit-identity-v17';P=O/(sys.argv[1] if len(sys.argv)>1 else 'prototype-01');cap=json.load(open(P/'capture.json'));rows=[]
frames=cap['frameIndices'];contact=Image.new('RGB',(1440,290*len(frames)),'white');d=ImageDraw.Draw(contact)
for i,n in enumerate(frames):
 imgs=[Image.open(R/f'source/{n:06}.png').convert('RGB'),Image.open(O/f'baseline-native16/{n:06}.png').convert('RGB'),Image.open(P/f'{n/30:.3f}.png').convert('RGB')];a,b,c=[np.array(x).astype(float) for x in imgs];before=abs(a-b);after=abs(a-c);eng=abs(b-c);regions={'global':(0,0,1920,1080),'lyft565':(980,440,1250,780),'greenEntry':(1400,760,1920,1080)};q=dict(frame=n,regions={})
 for name,(x1,y1,x2,y2) in regions.items():q['regions'][name]=dict(beforeMAE=float(before[y1:y2,x1:x2].mean()),afterMAE=float(after[y1:y2,x1:x2].mean()),vsActualV16MAE=float(eng[y1:y2,x1:x2].mean()))
 rows.append(q)
 for j,img in enumerate(imgs):contact.paste(img.resize((480,270)),(480*j,290*i+20));d.text((480*j,290*i),f'{n} '+['source','actual16','prototype'][j],fill='black')
 print(n,q['regions'])
contact.save(P/'contact.jpg');(P/'metrics.json').write_text(json.dumps(rows,indent=2));print('global before/after',np.mean([x['regions']['global']['beforeMAE'] for x in rows]),np.mean([x['regions']['global']['afterMAE'] for x in rows]))
