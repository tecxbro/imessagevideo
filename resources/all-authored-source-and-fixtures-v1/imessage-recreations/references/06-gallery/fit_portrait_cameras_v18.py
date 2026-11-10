"""Fit individual photographed discs to native motion, using static identities.
Only native x/y/scale/blur tracks are produced; source analysis frames are not assets.
"""
from pathlib import Path
import json,argparse
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import map_coordinates
from scipy.optimize import minimize
D=Path(__file__).resolve().parent;F=D/'native-transition-v18';s=json.loads((D/'scene.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--anchors-only',action='store_true');args=parser.parse_args()
faces=[g for g in s['layers'] if g['id'].startswith('rene-final11-group-') and g.get('start')==20.5]
v,u=np.mgrid[-.43:.431:25j,-.43:.431:25j];valid=u*u+v*v<.43*.43;u,v=u[valid].ravel(),v[valid].ravel();templates={};initial={}
for g in faces:
 n=g['children'][0];ar=Image.open(D/n['src']).convert('RGBA');rgb=Image.new('RGBA',ar.size,'white');rgb.alpha_composite(ar);rgb=rgb.convert('RGB').resize((65,65),Image.Resampling.LANCZOS);levels=[0,.5,1,2,3,5]
 ts=[]
 for blur in levels:
  a=np.array(rgb.filter(ImageFilter.GaussianBlur(blur))).astype(float);ts.append(np.stack([map_coordinates(a[:,:,c],[(v+.5)*64,(u+.5)*64],order=1) for c in range(3)],1))
 templates[g['id']]=(np.asarray(ts),levels)
 initial[g['id']]={}
 for anchor in [630,645]:
  get=lambda k:next(q['value'] for q in g['keyframes'][k] if q['t']==anchor/30)
  w=n['width']*get('scaleX');h=n['height']*get('scaleY');initial[g['id']][anchor]=np.array([get('x')+w/2,get('y')+h/2,(w+h)/2])

def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS)).astype(float)
def fit(a,name,pred,anchor=False,foreground=None,allowFade=False):
 pred=pred.copy();pred[2]=np.clip(pred[2],25,5000);ts,levels=templates[name];cx,cy,w=pred;delta=max(45,w*.28) if not anchor else 60
 low=[cx-delta,cy-delta,max(20,w*(.65 if not anchor else .6))];high=[cx+delta,cy+delta,max(low[2]+1,min(5000,w*(1.48 if not anchor else 1.4)))]
 def cost(z,detail=False):
  xx=(z[0]+u*z[2])/2;yy=(z[1]+v*z[2])/2;valid=(xx>=1)&(xx<959)&(yy>=1)&(yy<539)
  for p in foreground or []:valid&=((xx-p[0]/2)**2+(yy-p[1]/2)**2>(p[2]*.47/2)**2)
  if valid.sum()<25:return (1e6,0,0,1) if detail else 1e6
  obs=np.stack([map_coordinates(a[:,:,c],[yy[valid],xx[valid]],order=1) for c in range(3)],1);err=np.mean((ts[:,valid]-obs[None,:,:])**2,2)
  # Huber-style clipping prevents another disc or the heading from pulling a
  # mostly visible identity away from its own face during genuine overlap.
  alphas=np.ones(len(levels))
  if allowFade:
   tc=255-ts[:,valid];oc=255-obs;alphas=np.clip(np.sum(tc*oc[None,:,:],axis=(1,2))/np.maximum(1,np.sum(tc*tc,axis=(1,2))),.01,1);err=np.mean((oc[None,:,:]-alphas[:,None,None]*tc)**2,2)
   score=np.mean(np.minimum(err,5000),axis=1)/max(1,np.mean(oc*oc))*1000
  else:score=np.mean(np.minimum(err,5000),axis=1)
  at=int(np.argmin(score));value=float(score[at])
  return (value,levels[at],float(valid.mean()),float(alphas[at])) if detail else value
 if cost(pred)>1e5:
  return dict(cx=float(pred[0]),cy=float(pred[1]),diameter=float(pred[2]),blurFraction=0.,opacity=1.,mse=1e6,visibleFraction=0.)
 result=minimize(cost,pred,method='Powell',bounds=list(zip(low,high)),options={'xtol':.06,'ftol':.0002,'maxiter':8})
 score,blur,vis,alpha=cost(result.x,True);z=result.x
 return dict(cx=float(z[0]),cy=float(z[1]),diameter=float(z[2]),blurFraction=float(blur/65),opacity=alpha,mse=score,visibleFraction=vis)

results={g['id']:[] for g in faces}
def finished_front(f,exclude):
 out=[]
 for name,rows in results.items():
  if name in exclude:continue
  r=next((x for x in rows if x['frame']==f),None)
  if r:out.append(np.array([r['cx'],r['cy'],r['diameter']]))
 return out
for anchor,subset in [(645,faces[5:]),(630,faces[:5])]:
 names=[g['id'] for g in subset];a=load(anchor);states={};front=finished_front(anchor,names)
 for g in reversed(subset):
  name=g['id'];r=fit(a,name,initial[name][anchor],True,front);r['frame']=anchor;results[name].append(r);states[name]=np.array([r['cx'],r['cy'],r['diameter']]);front.append(states[name]);print(name,r,flush=True)
 if not args.anchors_only:
  for direction,frames in [(-1,range(anchor-1,602,-1)),(1,range(anchor+1,688))]:
   prev={k:v.copy() for k,v in states.items()};velocity={k:np.zeros(3) for k in states}
   for f in frames:
    a=load(f);front=finished_front(f,names)
    for g in reversed(subset):
     name=g['id'];prediction=prev[name]+velocity[name]*.7;r=fit(a,name,prediction,foreground=front,allowFade=f>=684);r['frame']=f;results[name].append(r);now=np.array([r['cx'],r['cy'],r['diameter']]);velocity[name]=now-prev[name];prev[name]=now;front.append(now)
    if f%6==0:
     print('anchor',anchor,'frame',f,flush=True);(D/'portrait-cameras-v18-partial.json').write_text(json.dumps(results,indent=2))
for v in results.values():v.sort(key=lambda x:x['frame'])
(D/('portrait-anchor-v18.json' if args.anchors_only else 'portrait-cameras-v18.json')).write_text(json.dumps(results,indent=2))
