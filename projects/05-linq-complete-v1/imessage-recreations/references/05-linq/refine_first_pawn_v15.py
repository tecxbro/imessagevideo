"""Native e7→e5 pawn pose from its original neutral outline, independent of board."""
from pathlib import Path
import json
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;ROOT=D.parent.parent;s=json.loads((D/'scene-restaurant-v15.json').read_text());g=next(q for q in s['layers'] if q['id']=='broad-v5-group-20');piece=next(q for q in g['children'] if q['id']=='broad-v5-image-18');xp={round(q['t']*30):q['value'] for q in g['keyframes']['x']};yp={round(q['t']*30):q['value'] for q in g['keyframes']['y']};rows=[]
# The authentic static sprite is acquired at source246; its bright core is at localY13.
for f in range(209,266):
 pose=126. if f<=242 else 280.
 if 243<=f<=253:
  a=np.asarray(Image.open(D/'measurements/native-transition'/f'{f:06}.png').convert('RGB'));cx=int(518+xp[f]-152);r=a[126:370,cx-27:cx+28].astype(float);mask=(r.min(2)>190)&((r.max(2)-r.min(2))<35);rr=np.where(mask.sum(1)>=3)[0];pose=float(rr.min()+126-13-yp[f])
 rows.append(dict(frame=f,y=pose))
piece['keyframes']['y']=[dict(t=r['frame']/30,value=r['y'],ease='linear') for r in rows]
(D/'first-pawn-v15-measurements.json').write_text(json.dumps(dict(referenceSpriteFrame=246,referenceWhiteCoreLocalTop=13,poses=rows),indent=2)+'\n');(D/'scene-restaurant-pawn-v15.json').write_text(json.dumps(s,indent=2)+'\n')
