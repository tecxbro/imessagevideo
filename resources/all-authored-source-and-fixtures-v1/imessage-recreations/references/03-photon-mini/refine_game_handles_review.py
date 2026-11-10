"""Recover the source blue-gray handle using contrast against the sheet fill."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
REF=Path(__file__).parent;P=REF.parent.parent/'verification/fidelity-review/03-game'
path=REF/'game-entry-review-elements.json';spec=json.load(open(path));measure=[]
for root in spec['insert_before']['p03-371']:
    f=int(root['id'].rsplit('-',1)[1]);source=np.asarray(Image.open(REF/'montage-native'/f'{f-794:03}.png').convert('RGB')).astype(float)
    display=next(n for n in root['children']if n['id']==f'game-review-display-{f}')
    rows=display['children'][0]['children'];first=min(n['y']for n in rows);last=max(n['y']+n['height']for n in rows);bg=np.zeros((1080,120,3))
    for row in rows:
        c=row['fill'];rgb=[int(c[i:i+2],16)for i in [1,3,5]];bg[row['y']:row['y']+row['height']]=rgb
    crop=source[:,900:1020];delta=crop-bg;mask=(crop[:,:,0]>75)&(crop.mean(2)<bg.mean(2)-15)&(delta.max(2)-delta.min(2)<20)
    region=np.zeros(mask.shape,bool);region[first+4:min(1080,first+22)]=True
    original=mask&region
    linked=ndimage.binary_closing(original,structure=np.ones((3,9)))
    labels,count=ndimage.label(linked);choices=[]
    for index,box in enumerate(ndimage.find_objects(labels),1):
        if box is None:continue
        yy,xx=box;w=xx.stop-xx.start;h=yy.stop-yy.start
        if 30<w<95 and h<=7:choices.append((w,index,box))
    display['children']=[n for n in display['children']if n['id']!=f'game-review-handle-{f}']
    if choices:
        _,index,box=max(choices);yy,xx=box;color=np.median(crop[(labels==index)&original],axis=0)
        node=dict(id=f'game-review-handle-{f}',type='rect',x=900+xx.start,y=yy.start,width=xx.stop-xx.start,height=yy.stop-yy.start,radius=(yy.stop-yy.start)/2,fill='#'+''.join(f'{round(v):02x}'for v in color))
        display['children'].append(node);measure.append(dict(frame=f,box=[node['x'],node['y'],node['x']+node['width'],node['y']+node['height']],RGB=color.tolist()))
spec['provenance']['handleCorrection']='Blue-gray source handle has the same chroma as the sheet. Detect its dark contrast relative to the clean sheet, not neutral RGB; native rounded rectangles remain editable.'
path.write_text(json.dumps(spec,indent=2));(P/'handle-measurements.json').write_text(json.dumps(measure,indent=2));print('native handles',len(measure));print(measure[:4])
