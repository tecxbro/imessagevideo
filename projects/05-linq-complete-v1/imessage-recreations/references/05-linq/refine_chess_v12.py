"""Measured source-native dim/win lifecycles, isolated from all other groups."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';A=D/'assets';s=json.loads((D.parent.parent/'outputs/05-linq/final-v11/scene.json').read_text());snap=D.parent.parent/'outputs/05-linq/final-v11'
def restore(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((snap/v).resolve())
   else:restore(v)
 elif isinstance(o,list):
  for q in o:restore(q)
restore(s)
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
board=next(q for q in s['layers'] if q['id']=='broad-v5-group-41');dim=next(q for q in board['children'] if q['id']=='broad-v5-rect-40');base=load(888)[85:110,400:500].mean((0,1));dimrows=[]
for f in range(888,899):
 observed=load(f)[85:110,400:500].mean((0,1));alpha=float(np.median(1-observed/base));dimrows.append(dict(frame=f,opacity=max(0,alpha)))
dim['keyframes']['opacity']=[dict(t=28.6666666667,value=0)]+[dict(t=p['frame']/30,value=p['opacity'],ease='linear') for p in dimrows]
# Actual held yellow panel with its true rounded alpha, avoiding the original
# bitmap's opaque wood pixels in the four outside corners.
ref=load(909);box=[341,315,620,406];art=ref[315:406,341:620];mask=(art[:,:,0]>210)&(art[:,:,1]>210)&(art[:,:,2]<65);mask=binary_fill_holes(mask);rgba=np.dstack([np.uint8(art),mask.astype(np.uint8)*255]);path=A/'v12-winning-badge-ui.png';Image.fromarray(rgba).save(path);my,mx=np.where(mask);refbox=[mx.min(),my.min(),mx.max()+1,my.max()+1];poses=[]
for f in range(903,933):
 a=load(f);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];yy,xx=np.indices(r.shape);m=(r>210)&(g>210)&(b<65)&(xx>300)&(xx<650)&(yy>260)&(yy<450);ys,xs=np.where(m)
 if not len(xs):continue
 sx=(xs.max()+1-xs.min())/(refbox[2]-refbox[0]);sy=(ys.max()+1-ys.min())/(refbox[3]-refbox[1]);poses.append(dict(frame=f,sx=float(sx),sy=float(sy),x=float(xs.min()-refbox[0]*sx),y=float(ys.min()-refbox[1]*sy)))
label=next(q for q in s['layers'] if q['id']=='broad-v5-group-43');label.update(x=0,y=0,originX=0,originY=0,start=903/30,children=[dict(type='image',id='v12-winning-badge-ui',src=str(path),width=279,height=91,semanticText='YOU WON!!')])
def key(k):return [dict(t=p['frame']/30,value=p[k],ease='linear') for p in poses]
label['keyframes']={'x':key('x'),'y':key('y'),'scaleX':key('sx'),'scaleY':key('sy'),'opacity':[dict(t=903/30,value=1)]}
# Preserve exact board-coupled late exit after the last held native sample.
for p in board['keyframes']['x']:
 if p['t']>=933/30:label['keyframes']['x'].append(dict(t=p['t'],value=p['value']+104.0,ease='linear'))
(D/'chess-v12-measurements.json').write_text(json.dumps(dict(dim=dimrows,badge=poses,provenance=dict(path=str(path),source_frame=909,box=box,kind='single bounded static app badge; internal copy bitmap; native measured position/scale/lifecycle; alpha excludes board corners')),indent=2));(D/'scene-chess-v12.json').write_text(json.dumps(s,indent=2)+'\n');print('dim',dimrows,'badgefirst',poses[0])
