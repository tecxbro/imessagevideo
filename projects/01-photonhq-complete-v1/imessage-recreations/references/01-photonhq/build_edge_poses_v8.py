"""Two-frame repair of individually clipped call controls/strips only."""
from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;folder=p/'assets/edge-call-v8';folder.mkdir(exist_ok=True)
regions={5:[0,0,50,20],6:[130,0,920,20],7:[990,0,1860,20],8:[1860,0,1920,20],15:[1820,240,1920,435],16:[0,240,95,435],21:[0,850,95,1047],24:[1815,850,1920,1047],25:[0,1060,490,1080],26:[540,1060,1430,1080],27:[1420,1060,1920,1080]};nodes=[];meta=[]
for f in (337,338):
 image=Image.open(p/'wall-v6-measure/wall'/f'{f-335:03}.png').convert('RGB');a=np.array(image)
 for index,roi in regions.items():
  x0,y0,x1,y1=roi;sub=a[y0:y1,x0:x1];mask=sub.min(2)<245;labels,n=ndimage.label(mask);areas=np.bincount(labels.ravel());areas[0]=0
  if not areas[1:].size or areas.max()<10:continue
  label=areas.argmax();ys,xs=np.where(labels==label);box=[max(x0,x0+int(xs.min())-2),max(y0,y0+int(ys.min())-2),min(x1,x0+int(xs.max())+3),min(y1,y0+int(ys.max())+3)];crop=image.crop(box);file=folder/f'edge-{index:02}-{f}.png';crop.save(file)
  entry={'source_frame':f,'source_box':box,'analysis_roi':roi,'component':'Clipped original call control/partial strip','bitmapInternalText':True,'noNeighborComponents':True,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()};meta.append({**entry,'file':str(file)})
  nodes.append({'id':f'call-edge-v8-{index}-{f}','type':'image','src':str(file.resolve()),'x':box[0],'y':box[1],'width':box[2]-box[0],'height':box[3]-box[1],'start':f/30,'end':(f+1)/30,'provenance':entry})
spec={'scope':[337,338],'baselineSha256':'82ed4b2cc153210574abb9a455ad9bb478e00ddc087939b5c7bcacfefa080f6d','gates':[f'edge-restore-calls-{i}-local-flip-gate' for i in regions],'nodes':nodes,'kind':'Two native frames of individually bounded edge material; main call bodies, caption and all other states unchanged.'};(p/'entrance-v8-measure/edge-poses-spec.json').write_text(json.dumps(spec,indent=2)+'\n');(folder/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n');print('nodes',len(nodes))
