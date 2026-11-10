"""Two authentic native status outlines and a bounded directional shutter pulse."""
from pathlib import Path
import json,copy,importlib.util
from functools import lru_cache
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;ROOT=D.parent.parent;INPUT=ROOT/'outputs/05-linq/final-v15/scene.json';s=json.loads(INPUT.read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((INPUT.parent/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s);ids=['broad-v5-group-2','broad-v5-group-7','broad-v5-group-15'];actors=[q for q in s['layers'] if q['id'] in ids];question=next(q for q in actors if q['id']=='broad-v5-group-7')
def value(q,k,t,default=0):
 keys=q.get('keyframes',{}).get(k)
 if not keys:return q.get(k,default)
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if a['t']<=t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return keys[-1]['value']
@lru_cache(maxsize=4)
def source(f):return np.asarray(Image.open(D/'measurements/native-transition'/f'{f:06}.png').convert('RGB')).astype(np.float32)/255
# Fit the global scroll shutter without allowing the missing receipt to bias it.
poses={f:dict(frame=f,sigmaX=0.,sigmaY=0.,dy=0.,adopted=False) for f in range(149,206)};yy,xx=np.mgrid[0:720:3,80:875:3]
cache=D/'preview-v16-shutter-cache.json'
if cache.exists():
 for r in json.loads(cache.read_text()):poses[r['frame']]=r
else:
 for f in range(184,194):
  M=np.asarray(Image.open(ROOT/f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB')).astype(np.float32)/255;R=source(f);target=R[0:720:3,80:875:3];qy=value(question,'y',f/30);mask=~((xx>=645)&(xx<840)&(yy>=qy+85)&(yy<qy+145))
  def residual(v):
   sx,sy,dy=v;p=gaussian_filter(M,[max(.001,sy),max(.001,sx),0],mode='nearest');p=np.stack([map_coordinates(p[:,:,c],[yy-dy,xx],order=1,mode='nearest') for c in range(3)],2);return (p-target)[mask].ravel()
  fit=least_squares(residual,[.4,3,0],bounds=([0,0,-2],[3,10,2]),max_nfev=30,diff_step=.01,ftol=.0003,xtol=.0003);old=float(np.abs(residual([0,0,0])).mean()*255);new=float(np.abs(residual(fit.x)).mean()*255);row=poses[f];row.update(oldBodyRoiMAE=old,newBodyRoiMAE=new)
  if new<old-.02:row.update(sigmaX=max(.3,float(fit.x[0])),sigmaY=max(.3,float(fit.x[1])),dy=float(fit.x[2]),adopted=True)
  print('shutter',row,flush=True)
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace);templates=[];assetdir=D/'assets/preview-status-v16';assetdir.mkdir(exist_ok=True)
for name,f,box,text in [('delivered',171,[700,600,830,637],'Delivered'),('read',180,[657,598,830,638],'Read 1:10 PM')]:
 x0,y0,x1,y1=box;rgb=source(f)[y0:y1,x0:x1]*255;gray=rgb.mean(2);neutral=(rgb.max(2)-rgb.min(2))<30;ink=(255-gray)*neutral;v=gray[ink>ink.max()*.7];fill=float(np.quantile(v,.02));alpha=np.clip((255-gray)/(255-fill),0,1)*neutral;path,stats=trace.trace_alpha(alpha,x0-value(question,'x',f/30),y0-value(question,'y',f/30));node=dict(type='path',id='v16-status-'+name+'-outline',d=path,fill='#'+''.join(f'{round(fill):02x}' for _ in range(3)),semanticText=text,sourceFrame=f,sourceBounds=box);pad=30;art=np.pad(alpha,pad);templates.append(dict(name=name,frame=f,box=box,fill=fill,art=art,x=x0-value(question,'x',f/30)-pad,y=y0-value(question,'y',f/30)-pad,node=node,stats=stats));Image.fromarray(np.uint8(np.round(rgb))).save(assetdir/(name+'-original-static.png'))
delivered,read=templates;reference=delivered['art'];iy,ix=np.where(reference>.5);anchorX=float((ix.min()+ix.max())/2+delivered['x']);anchorY=float((iy.min()+iy.max())/2+delivered['y']);receipts=[]
for f in range(149,206):
 qx=value(question,'x',f/30);qy=value(question,'y',f/30);p=poses[f];top=max(0,int(np.floor(qy+84)));bottom=min(720,int(np.ceil(qy+145)))
 if f<160 or f>=192 or bottom<=top:
  receipts.append(dict(frame=f,deliveredOpacity=0.,readOpacity=0.,deliveredScale=1.,deliveredDY=0.));continue
 wy,wx=np.mgrid[top:bottom,645:830];target=(1-source(f)[top:bottom,645:830].mean(2));colors=source(f)[top:bottom,645:830];valid=(colors.max(2)-colors.min(2))<.12
 def masks(scale,dy):
  arr=[]
  for j,g in enumerate(templates):
   sc=scale if j==0 else 1.;dyy=dy if j==0 else 0.;ar=gaussian_filter(g['art'],[p['sigmaY']/sc,p['sigmaX']/sc],mode='constant');tx=(wx-qx-anchorX)/sc+anchorX-g['x'];ty=(wy-qy-p['dy']-dyy-anchorY)/sc+anchorY-g['y'];arr.append(map_coordinates(ar,[ty,tx],order=1,mode='constant',cval=0)*(255-g['fill'])/255)
  return arr
 def residual(v):
  ad,ar,sc,dy=v;d,r=masks(sc,dy);pred=1-(1-ad*d)*(1-ar*r);return (pred-target)[valid].ravel()
 initial=[1 if f<174 else 0,0 if f<173 else 1,.7 if f==160 else .8 if f in [161,162] else .9 if f==163 else 1,2 if f<164 else 0]
 if f<165:
  def early(v):return residual([v[0],0,v[1],v[2]])
  fit=least_squares(early,[initial[0],initial[2],initial[3]],bounds=([0,.55,-5],[1,1.12,5]),max_nfev=55,diff_step=.005,ftol=.0002,xtol=.0002);ad,sc,dy=map(float,fit.x);ar=0.
 elif f<173 or f>=177:
  d,r=masks(1,0);k=d if f<173 else r;ad=float(np.clip(np.sum((k*target)[valid])/max(1e-9,np.sum((k*k)[valid])),0,1)) if f<173 else 0.;ar=float(np.clip(np.sum((k*target)[valid])/max(1e-9,np.sum((k*k)[valid])),0,1)) if f>=177 else 0.;sc=1.;dy=0.
 else:
  def residual2(v):return residual([v[0],v[1],1,0])
  fit=least_squares(residual2,initial[:2],bounds=([0,0],[1,1]),max_nfev=40,diff_step=.005,ftol=.0002,xtol=.0002);ad,ar=map(float,fit.x);sc=1.;dy=0.
 if ad<.01:ad=0.
 if ar<.01:ar=0.
 row=dict(frame=f,deliveredOpacity=ad,readOpacity=ar,deliveredScale=sc,deliveredDY=dy);receipts.append(row);print('status',row,flush=True)
def keys(name):return [dict(t=r['frame']/30,value=r[name],ease='hold') for r in receipts]
for g in templates:
 node=g['node'];parent=dict(type='group',id='v16-status-'+g['name'],start=160/30,end=192/30,children=[node],originX=anchorX,originY=anchorY,keyframes={'opacity':keys(g['name']+'Opacity')})
 if g['name']=='delivered':parent['keyframes'].update(scaleX=keys('deliveredScale'),scaleY=keys('deliveredScale'),y=keys('deliveredDY'))
 question['children'].append(parent)
# Reciprocal held transforms give exact geometry at every measured sample and
# between samples. Only the local shutter interval changes the raster effect.
def posekeys(fn):return [dict(t=f/30,value=fn(poses[f]),ease='hold') for f in range(149,206)]
inner=dict(type='group',id='v16-preview-inverse-stretch',children=actors,keyframes={'scaleX':posekeys(lambda p:1/p['sigmaX'] if p['adopted'] else 1),'scaleY':posekeys(lambda p:1/p['sigmaY'] if p['adopted'] else 1)})
outer=dict(type='group',id='v16-preview-directional-shutter',start=149/30,end=206/30,children=[inner],keyframes={'blur':posekeys(lambda p:1 if p['adopted'] else 0),'scaleX':posekeys(lambda p:p['sigmaX'] if p['adopted'] else 1),'scaleY':posekeys(lambda p:p['sigmaY'] if p['adopted'] else 1),'y':posekeys(lambda p:p['dy'])})
at=min(i for i,q in enumerate(s['layers']) if q['id'] in ids);s['layers']=[q for q in s['layers'] if q['id'] not in ids];s['layers'].insert(at,outer);(D/'preview-v16-measurements.json').write_text(json.dumps(dict(shutter=list(poses.values()),status=receipts,anchor=[anchorX,anchorY],originalArt=[{k:g[k] for k in ['name','frame','box','fill','stats']} for g in templates]),indent=2)+'\n');(D/'scene-preview-v16.json').write_text(json.dumps(s,indent=2)+'\n')
