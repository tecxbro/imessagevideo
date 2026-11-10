"""Track each original phone column at every native frame after zoom settles."""
from pathlib import Path
import json,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent;BASE=ROOT/'outputs/05-linq/final-v9'
scene=json.loads((BASE/'scene.json').read_text());group=next(l for l in scene['layers'] if l['id']=='broad-v5-group-72')
specs=[('left','rich-asset-17',30,332,50),('center','rich-asset-15',345,100,-32),('right','rich-asset-16',662,51,50)]
assets={name:np.array(Image.open(BASE/next(c for c in group['children'] if c['id']==identity)['src']).convert('RGB'),float)[:180] for name,identity,x,a,slope in specs}
opacity={r['frame']:r['value'] for r in json.loads((REF/'assets/root-late/gallery-opacity.json').read_text())};records=[];last={}
for n in range(1227,1272):
 alpha=opacity.get(n,1);alpha=1 if alpha>.98 else alpha
 source=np.array(Image.open(REF/f'assets/root-late-measure/frame-{n:04d}.png').convert('RGB'),float)
 row={'frame':n,'time':n/30,'scale':1.,'x':0.,'y':0.,'opacity':alpha,'columnY':{},'columnMSE':{}}
 for name,identity,x,a,slope in specs:
  expected=a+(n/30-41.5)*slope;reference=assets[name];h,w=reference.shape[:2]
  if alpha<.3:
   value=last[name]+slope/30
  else:
   decoded=np.clip((source-255)/max(alpha,.001)+255,0,255)
   def score(y):return float(((decoded[y:y+h,x:x+w]-reference)**2).mean())
   candidates=[(score(y),y) for y in range(max(0,round(expected)-16),min(720-h,round(expected)+16)+1)]
   cost,y=min(candidates);fm,fp=score(y-1),score(y+1);den=fm-2*cost+fp;fraction=float(np.clip(.5*(fm-fp)/den,-.5,.5)) if abs(den)>1e-6 else 0
   value=y+fraction;row['columnMSE'][name]=cost
  row['columnY'][name]=value;last[name]=value
 records.append(row)
(REF/'assets/root-late/gallery-late-native-poses.json').write_text(json.dumps(records,indent=2))
print(json.dumps({'frames':len(records),'first':records[0],'last':records[-1]}))
