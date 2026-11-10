"""Bounded semantic neutral typography reconstruction. No source-frame image layer."""
from pathlib import Path
import json,copy,re,sys
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent))
from trace_glyphs import trace_alpha
reason=json.loads((R/'reason-v5-measured-camera.json').read_text())
old=copy.deepcopy(reason)
rows=reason['children'][:7]
for row in rows[1:]:
    row['children'][0]['opacity']=0
for node in reason['children'][7:]:
    if node['id'].startswith('peak-reasoning-exit-glyphs-'):node['opacity']=0
clusters={q['frame']:q['clusters']for q in json.loads((R/'reasoning-color-clusters.json').read_text())}
magnifier=json.loads((R.parent/'v11-boundary-refinement.json').read_text())['replacements']['group-1007']
mag={int(n['id'].split('-')[-1]):n for n in magnifier['children']if n['id'].startswith('peak-native-magnifier-')}
def sample(node,key,f):
    arr=node.get('keyframes',{}).get(key,[])
    if not arr:return node.get(key,1 if key.startswith('scale')else 0)
    t=f/30
    if t<=arr[0]['t']:return arr[0]['value']
    for a,b in zip(arr,arr[1:]):
        if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
    return arr[-1]['value']
def ring_mask(node):
    polygons=[]
    for loop in re.findall(r'M([^Z]+)Z',node['d']):
        coords=np.array(list(map(float,re.findall(r'-?\d+(?:\.\d+)?',loop)))).reshape(-1,2)
        polygons.append(np.rint(coords*16).astype(np.int32))
    mask=np.zeros((1080,1920),np.uint8)
    cv2.fillPoly(mask,polygons,255,shift=4)
    return cv2.dilate(mask,np.ones((5,5),np.uint8))>0
colors=[251,247,239,227,215,203,195,187,175,163,147,131,115,99,83,67,51,35,19,3]
semantics=[r['children'][0].get('semanticText','')for r in rows]
records=[]
for f in range(272,375):
    rgb=np.asarray(Image.open(R/'reasoning-source'/f'source-{f:04d}.png').convert('RGB')).astype(float)
    gray=rgb.mean(2)
    valid=(rgb.max(2)-rgb.min(2)<16)&(gray<252)
    if f<=360:
        ylimit=int(np.ceil(sample(rows[0],'y',f)+274.768*sample(rows[0],'scaleY',f)+9))
        valid[:ylimit]=False
    if f in mag:valid[ring_mask(mag[f])]=False
    for cluster in clusters.get(f,[]):
        x0,y0,x1,y1=cluster['bounds']
        # Full original art bounds, including neutral wheels, pin stem and blur halo.
        pad=5
        if f>=361:
            pad=max(1,round(5*(x1-x0)/34))
        if 450<x0<1000:
            y1=max(y1,round(y0+72*(x1-x0)/36))
        valid[max(0,y0-pad):min(1080,y1+pad),max(0,x0-pad):min(1920,x1+pad)]=False
    valid[:,:150]=False
    if f<=360:valid[:,1800:]=False
    # Remove isolated compression noise, keeping glyph punctuation and tiny iris text.
    labels,count=ndimage.label(valid)
    sizes=np.bincount(labels.ravel());valid&=sizes[labels]>=2
    gray=np.where(valid,gray,253)
    projection=np.any(gray<251.7,axis=1)
    projection=ndimage.binary_closing(projection,iterations=3)
    labels,count=ndimage.label(projection)
    emitted=[]
    for band,yslice in enumerate(ndimage.find_objects(labels)):
        if yslice is None:continue
        y0,y1=yslice[0].start,yslice[0].stop
        ys,xs=np.nonzero(gray[y0:y1]<251.7)
        if len(xs)<3:continue
        x0,x1=max(0,int(xs.min())-2),min(1920,int(xs.max())+3)
        y0=max(0,y0-2);y1=min(1080,y1+2)
        crop=gray[y0:y1,x0:x1]
        children=[];last=253
        for level in colors:
            threshold=(last+level)/2
            if np.any(crop<threshold):
                d,stats=trace_alpha((253-crop).astype(np.float32),threshold=253-threshold)
                if d:children.append({'id':f'reason-neutral-{f}-{band}-{level}','type':'path','d':d,'fill':'#'+f'{level:02x}'*3})
            last=level
        if not children:continue
        centers=[sample(row,'y',f)+(sample(row,'scaleY',f)*(312.466+375.75)/2 if i==1 else sample(row,'scaleY',f)*([242,344,440,548,643,744,852][i])) for i,row in enumerate(rows)]
        nearest=min(range(7),key=lambda i:abs(centers[i]-(y0+y1)/2))
        actor={'id':f'reason-neutral-native-{f}-{band}','type':'group','start':f/30,'end':(f+1)/30,'x':x0,'y':y0,'children':children,'semanticText':semantics[nearest] if f<=360 else 'Reasoning plan shrinking inside search iris; query begins Se at374','sourceFrame':f,'sourceBounds':[x0,y0,x1,y1],'editability':'Native bounded semantic glyph contours; not live-font text. Opaque neutral tone layers reconstruct measured blur.'}
        reason['children'].append(actor)
        emitted.append({'bounds':[x0,y0,x1,y1],'paths':len(children),'semantic':actor['semanticText']})
    records.append({'frame':f,'bands':emitted})
    if f in [272,275,280,293,320,360,361,363,367,370,374]:print(f,len(emitted),sum(x['paths']for x in emitted),flush=True)
(R/'reasoning-neutral-candidate.json').write_text(json.dumps({'id':reason['id'],'replacement':reason,'changedFrames':list(range(272,375)),'provenance':records},separators=(',',':')))
print('written',flush=True)
