"""Native independent end-card objects and measured source entrance poses."""
from pathlib import Path
import json,importlib.util
from functools import lru_cache
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;s=json.loads((D/'scene-endcard-v20.json').read_text())
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
parts=[('qr',[608,474,740,606],[550,450,780,630],1548),('domain',[820,470,1340,600],[780,450,1400,630],1550)]
children=[dict(type='rect',id='v20-endcard-native-stage',x=0,y=0,width=1920,height=1080,fill='#fdffff',start=1365/30,end=s['duration'])];records={}
for name,box,roi,first in parts:
 x0,y0,x1,y1=box;ref=np.asarray(Image.open(D/'assets'/f'endcard-{name}-v20-source.png').convert('RGB')).mean(2);ar=np.maximum(0,(254.333-ref)/254.333);path,stats=trace.trace_alpha(ar,x0,y0);pad=80;art=np.pad(ar,pad);ax=x0-pad;ay=y0-pad;rx0,ry0,rx1,ry1=roi;yy,xx=np.mgrid[ry0:ry1:2,rx0:rx1:2];rows=[];prev=np.array([-22,0,1,1,.1,2.],float)
 for f in range(first,1566):
  im=np.asarray(Image.open(D/'endcard-v20-measure'/f'{f:06}.png').convert('RGB')).mean(2);target=np.maximum(0,(254.333-im[ry0-400:ry1-400:2,rx0-520:rx1-520:2])/254.333)
  def residual(v):
   dx,dy,sx,sy,a,b=v;blur=gaussian_filter(art,b,mode='constant');pred=a*map_coordinates(blur,[(yy-y0-dy)/sy+y0-ay,(xx-x0-dx)/sx+x0-ax],order=1,mode='constant',cval=0);return (pred-target).ravel()
  best=None
  for sigma in [0,.5,1,2,3,5,8]:
   blurred=gaussian_filter(art,sigma,mode='constant')
   for dx0 in range(-80,26,2):
    for dy0 in [-1,0,1]:
     k=map_coordinates(blurred,[yy-ay-dy0,xx-ax-dx0],order=1,mode='constant',cval=0);den=float(np.sum(k*k));amp=float(np.clip(np.sum(k*target)/max(den,1e-9),0,1.05));cost=float(np.mean((amp*k-target)**2))
     if best is None or cost<best[0]:best=(cost,np.array([dx0,dy0,1,1,amp,sigma],float))
  seed=best[1]
  fit=least_squares(residual,seed,bounds=([-80,-5,.96,.96,0,0],[25,5,1.04,1.04,1.05,8]),max_nfev=65,diff_step=.004,ftol=.0002,xtol=.0002);dx,dy,sx,sy,a,b=map(float,fit.x);prev=fit.x;rows.append(dict(sourceFrame=f,frame=f-181,dx=dx,dy=dy,sx=sx,sy=sy,opacity=min(1,a),blur=b,cost=float(np.mean(residual(fit.x)**2))))
  print(name,f,rows[-1],flush=True)
 # Canonical held original from1566 onward.
 rows.append(dict(sourceFrame=1566,frame=1385,dx=0,dy=0,sx=1,sy=1,opacity=1,blur=0,cost=0));records[name]=dict(box=box,poses=rows)
 node=dict(type='path',id='v20-endcard-'+name,d=path,fill='#000000',semanticText='rene.co' if name=='domain' else 'Original QR code',sourceFrame=1625,sourceBounds=box,originX=x0,originY=y0,start=(first-181)/30,end=s['duration'],keyframes={k:[dict(t=r['frame']/30,value=r[v],ease='linear') for r in rows] for k,v in [('x','dx'),('y','dy'),('scaleX','sx'),('scaleY','sy'),('opacity','opacity'),('blur','blur')]});children.append(node)
 # Persist only isolated static artwork for reproducible path derivation.
 # Original component crop is already persisted beside its provenance.
# Divider appears with domain; measured native one-pixel pale line.
children.append(dict(type='rect',id='v20-endcard-divider',x=788,y=502,width=1,height=77,fill='#c8c8c8',start=1370/30,end=s['duration']))
g=next(q for q in s['layers'] if q['id']=='g-1360');g.clear();g.update(dict(type='group',id='g-1360',start=1365/30,end=s['duration'],children=children))
(D/'endcard-v20-measurements.json').write_text(json.dumps(records,indent=2));(D/'endcard-v20-patch.json').write_text(json.dumps(dict(replace={'g-1360':g},provenance='Two static original bounded graphics traced into native paths, independent measured native cameras; no frame playback.'),indent=2));(D/'scene-endcard-v20.json').write_text(json.dumps(s,indent=2)+'\n')
