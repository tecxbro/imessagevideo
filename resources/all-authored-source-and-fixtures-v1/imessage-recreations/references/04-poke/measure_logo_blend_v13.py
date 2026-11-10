"""Fit native genuine-logo material blend after fixing clip-coordinate ownership."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;s=json.loads((p/'scene-v13-candidate.json').read_text());out=[]
for g in s['layers']:
    if not g['id'].startswith('v10-logo-morph-'):continue
    n=int(g['id'].rsplit('-',1)[1]);a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(float);x0,y0,x1,y1=450,100,1000,720;target=a[y0:y1,x0:x1];m=(target[:,:,2]-target[:,:,0]>20)&(target[:,:,2]-target[:,:,1]>0)&(target[:,:,0]<150);m=ndimage.binary_erosion(m,iterations=6);materials={}
    for parent in g['children']:
        if parent.get('type')!='group':continue
        node=parent['children'][0];name='circle'if'circle'in node['id']else'square';im=Image.open(p/node['src']).convert('RGBA');sx=g['scaleX']*node['width']/im.width;sy=g['scaleY']*node['height']/im.height;ox=g['x']+g['scaleX']*node['x'];oy=g['y']+g['scaleY']*node['y'];v=np.array(im.transform((x1-x0,y1-y0),Image.Transform.AFFINE,(1/sx,0,(x0-ox)/sx,0,1/sy,(y0-oy)/sy),Image.Resampling.BICUBIC)).astype(float);materials[name]=v
    c=materials['circle'];b=c[:,:,3:4]/255*c[:,:,:3]+(1-c[:,:,3:4]/255)*np.array([36,73,100]);q=materials['square'];d=q[:,:,3:4]/255*(q[:,:,:3]-b);blend=float(np.clip(np.sum((target-b)[m]*d[m])/np.sum(d[m]**2),0,1));old=next(c['children'][0]['opacity']for c in g['children']if c.get('type')=='group'and'square'in c['id']);out.append(dict(frame=n,old_blend=old,blend=blend,roi_source_pixels=int(m.sum()),old_mae=float(abs(target-b-old*d)[m].mean()),fitted_mae=float(abs(target-b-blend*d)[m].mean())))
(p/'measurements-v8/logo-material-blend-v13.json').write_text(json.dumps(dict(method='Original blue core only,6px eroded, palm excluded. Two existing static authentic material projections after parent clip-coordinate correction; bounded least-squares alpha. Browser proof remains mandatory.',measurements=out),indent=2));print(out)
