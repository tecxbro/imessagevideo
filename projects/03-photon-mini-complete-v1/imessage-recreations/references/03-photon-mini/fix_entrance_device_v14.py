"""Reject phone-body false positives in five native island observations."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;s=json.loads((p/'projection-v14.scene.json').read_text());device=next(x for x in s['layers'] if x['id']=='measured-entrance-device-v13');records=[]
for f in range(467,472):
 a=np.array(Image.open(p/'entrance-native'/f'{f-434:03}.png'));l,n=ndimage.label(a.max(2)<35);candidates=[]
 for i,b in enumerate(ndimage.find_objects(l),1):
  if b is None:continue
  y,x=b;w=x.stop-x.start;h=y.stop-y.start
  if 100<w<1000 and 35<h<300 and 3<w/h<4 and abs((x.start+x.stop)/2-960)<100:candidates.append([x.start,y.start,x.stop,y.stop])
 if len(candidates)!=1:raise ValueError((f,candidates))
 b=candidates[0];sx=(b[2]-b[0])*1.035/234;sy=(b[3]-b[1])*1.035/67;x=(b[0]+b[2])/2-400*sx;y=b[3]-(162-35)/1.035*sy;pose={'x':x,'y':y,'scaleX':sx,'scaleY':sy}
 for key,value in pose.items():
  q=next(z for z in device['keyframes'][key] if abs(z['t']-f/30)<1e-6);q['value']=value
 records.append({'frame':f,'rejected_v13':'Phone-body component ended atROI y450 and jumped scale2.68→8.17.','island_bbox':b,'pose':pose})
s['source']['notes']+=' V14 physical island correction467–471: reject the entering phone body component, use unique aperture aspect/center/size semantic gates. No other device/UI/Memoji phase changed.'
(p/'entrance-v14.scene.json').write_text(json.dumps(s,indent=2));(p/'entrance-device-v14-changes.json').write_text(json.dumps(records,indent=2));print(records)
