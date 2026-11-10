from pathlib import Path
from PIL import Image
import json,copy
from hardware_fit_v13 import fit_hardware
p=Path(__file__).parent;s=json.loads((p/'final-v12.scene.json').read_text());lunch=next(x for x in s['layers'] if x['id']=='p03-204');mont=next(x for x in s['layers'] if x['id']=='p03-371');out=[]
def sample(track,t):
 if t<=track[0]['t']:return track[0]['value']
 for a,b in zip(track,track[1:]):
  if t<=b['t']:
   u=(t-a['t'])/(b['t']-a['t']);return a['value']*(1-u)+b['value']*u
 return track[-1]['value']
for f in range(618,891):
 g=lunch if f<800 else mont;t=f/30;ini={k:sample(g['keyframes'][k],t) for k in ['x','y','scaleX']};ini['scale']=ini.pop('scaleX');folder='lunch-native' if f<800 else 'montage-native';index=f-609 if f<800 else f-794;im=Image.open(p/folder/f'{index:03}.png');bands=[(ini['x']-30,ini['x']+65*ini['scale']),(ini['x']+735*ini['scale'],ini['x']+825*ini['scale'])]
 # New montage cut starts huge before settling back to the small stage phone.
 if 800<=f<=806:
  boxes=json.loads((p/'montage-v13-changes.json').read_text())['poses'];q=boxes[str(f)];ini={'x':q['x'],'y':q['y'],'scale':q['scaleX']};bands=[(ini['x']-20,ini['x']+80*ini['scale']),(ini['x']+720*ini['scale'],ini['x']+820*ini['scale'])]
 r=fit_hardware(im,ini,y_radius=120,edge_bands=bands);r['frame']=f;r['t']=t;out.append(r)
 if f%30==0:print(f,r['hardware_cost'],r['scale'],r['y'],flush=True)
(p/'late-hardware-v13-measurements.json').write_text(json.dumps(out,indent=2));print('done',len(out))
