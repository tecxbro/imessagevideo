from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[2];rows=[];contact=Image.new('RGB',(1050,150*5),'#eee');d=ImageDraw.Draw(contact)
for i,f in enumerate(range(737,742)):
 s=Image.open(ROOT/'references/03-photon-mini/lunch-native'/f'{f-609:03d}.png').convert('RGB');b=Image.open(R/'native-baseline'/f'{f/30:.3f}.png').convert('RGB');c=Image.open(R/'native-candidate'/f'{f/30:.3f}.png').convert('RGB');a=np.array(s).astype(float);bb=np.array(b).astype(float);cc=np.array(c).astype(float);roi=(slice(0,115),slice(780,950));row={'frame':f,'globalBeforeMAE':float(abs(a-bb).mean()),'globalAfterMAE':float(abs(a-cc).mean()),'pizzaROIBeforeMAE':float(abs(a[roi]-bb[roi]).mean()),'pizzaROIAfterMAE':float(abs(a[roi]-cc[roi]).mean()),'nativeBaselineCandidateMax':float(abs(bb-cc).max())};rows.append(row)
 for j,(im,label) in enumerate([(s,'reference'),(b,'before'),(c,'after')]):
  crop=im.crop((760,0,1000,115)).resize((330,140));contact.paste(crop,(j*350,i*150));d.text((j*350+2,i*150+2),f'{f} {label}',fill='red')
assert all(q['nativeBaselineCandidateMax']==0 for q in rows if q['frame']in[737,741])
assert all(q['globalAfterMAE']<q['globalBeforeMAE'] for q in rows if q['frame']in[738,739,740])
(R/'native-metrics.json').write_text(json.dumps({'rows':rows,'source':'Native full-resolution original frames; same-adapter genuine GSAP baseline and append-only candidate, five consecutive frames.','notExact':'Affine pose retains actual original Apple pizza pixels; source compression, antialiasing and local non-affine texture remain.'},indent=2));contact.save(R/'native-pizza-contact.jpg');print(json.dumps(rows,indent=2))
