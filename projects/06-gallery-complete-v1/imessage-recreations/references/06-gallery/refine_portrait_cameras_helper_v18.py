"""Source-native photographed-disc cameras with explicit anchored occlusion.
Only bounded static photos are output assets; analysis frames are measurement.
"""
from pathlib import Path
import json,copy,argparse
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import map_coordinates
from scipy.optimize import minimize
from scipy.interpolate import PchipInterpolator
P=Path(__file__).parent;B=P/'portrait-helper-v18';F=P/'native-transition-v18';S=json.load(open(P/'scene.json'));old=json.load(open(P/'portrait-cameras-v18.json'));global_fits=json.load(open(B/'coarse-identity-search.json'));faces={g['id'].split('-')[-1]:copy.deepcopy(g)for g in S['layers']if g['id'].startswith('rene-final11-group-')and g.get('start')==20.5}
for q in json.load(open(B/'new-portrait-provenance.json')):
 p=Path(q['src']).resolve();w,h=Image.open(p).size;faces[q['id']]={'id':'rene-portrait-'+q['id'],'type':'group','children':[{'id':'rene-portrait-image-'+q['id'],'type':'image','src':str(p),'width':w,'height':h}],'semanticText':q['id'],'provenance':q}
card_bounds={q['frame']:q for q in json.load(open(P/'notification-v18-world-bounds.json'))}
anchors={k:{}for k in faces}
for id,g in faces.items():
 for r in old.get(g['id'],[]):
  f=r['frame']
  if f in [612,615,618,621,624,627,630,633,636,639,642,645,648,651,654,657,660,663,666,669,672,675,678,681,683] and r['diameter']>70 and r['mse']<1000 and r['visibleFraction']>.2:anchors[id][f]=[r['cx'],r['cy'],r['diameter']]
# These actual observed poses prevent the old swapped/occluded tracker from
# replacing a large entering face with an unrelated tiny neighboring face.
manual={'81':{609:[-142,931,446]},'95':{609:[1750,1100,650],612:[1500,770,350]},'71':{615:[521,120,237]},'75':{624:[850,550,110]},'85':{618:[1108,818,128]},'87':{609:[915,-100,500],612:[940,70,330],615:[1006,243,180],654:[1120,310,225],681:[1105,315,225]},'89':{618:[1117,35,207],654:[802,240,187],681:[806,241,180]},'new-blond-male':{615:[130,575,624],618:[465,620,288],624:[606,637,150]},'new-foliage-woman':{618:[643,931,195],624:[850,805,124]}}
for id,rows in manual.items():anchors[id].update(rows)
for key,rs in global_fits.items():
 id,f=key.rsplit('-',1);f=int(f)
 if id in ['new-blond-male','new-foliage-woman'] and f>=630 and rs[0]['mse']<(400 if id=='new-blond-male' else 300):anchors[id][f]=[rs[0][k]for k in ['cx','cy','diameter']]
# Occluded small foliage disc has no unique full template in630–645; keep a
# continuous prior until it becomes observable to the right of the front photos.
for f,v in {660:[1116,696,112],681:[1128,690,104]}.items():anchors['new-foliage-woman'].setdefault(f,v)
for f,v in {660:[990,480,90],681:[1020,486,88]}.items():anchors['new-blond-male'].setdefault(f,v)
# The tiny-score failures after645 are behind the birthday card, not a real
# diameter collapse. Only positive-depth observations enter the camera prior.
(B/'anchor-priors.json').write_text(json.dumps(anchors,indent=2)+'\n')

def projective_curve(id,f):
 d=anchors[id];ts=np.array(sorted(d));xyz=np.array([d[t]for t in ts]);q=1/xyz[:,2];uv=np.column_stack([(xyz[:,0]-960)*q,(xyz[:,1]-540)*q,q]);values=[]
 for k in range(3):
  if f<ts[0]:v=uv[0,k]+(f-ts[0])*(uv[1,k]-uv[0,k])/(ts[1]-ts[0])
  elif f>ts[-1]:v=uv[-1,k]+(f-ts[-1])*(uv[-1,k]-uv[-2,k])/(ts[-1]-ts[-2])
  else:v=float(PchipInterpolator(ts,uv[:,k])(f))
  values.append(v)
 u,v,q=values
 if q<=1/30000:return np.array([0.,0.,0.])
 D=1/q;return np.array([960+u*D,540+v*D,D])

templates={};template_photos={};blur_levels=np.array([0,.5,1,2,3,5,8,12])/65
vv,uu=np.mgrid[-.57:.571:35j,-.57:.571:35j];keep=uu*uu+vv*vv<.57*.57;u=uu[keep].ravel();v=vv[keep].ravel()
for id,g in faces.items():
 child=g['children'][0];p=Path(child['src']);p=p if p.is_absolute()else P/p;child['src']=str(p.resolve());ar=Image.open(p).convert('RGBA').resize((65,65),Image.Resampling.LANCZOS);pad=18;alpha=Image.new('L',(101,101));alpha.paste(ar.getchannel('A'),(pad,pad));shadow=alpha.filter(ImageFilter.GaussianBlur(65*.06));shadow=np.uint8(np.array(shadow)*.133);sha=Image.new('RGBA',(101,101),(0,0,0,0));sha.putalpha(Image.fromarray(shadow));rgb=Image.new('RGBA',(101,101),'white');rgb.alpha_composite(sha,(0,4));rgb.alpha_composite(ar,(pad,pad));rgb=rgb.convert('RGB');template_photos[id]=rgb.copy();ts=[]
 for frac in blur_levels:
  a=np.array(rgb.filter(ImageFilter.GaussianBlur(float(frac*65)))).astype(np.float32);ts.append(np.stack([map_coordinates(a[:,:,c],[(v+.5)*65+pad-.5,(u+.5)*65+pad-.5],order=1,mode='nearest')for c in range(3)],1))
 templates[id]=np.array(ts)

def fit(a,id,pred,foreground,frame):
 if pred[2]<15:return dict(cx=0.,cy=0.,diameter=0.,blurFraction=0.,opacity=0.,mse=None,visibleFraction=0.)
 D=pred[2];sigma=max(15,D*.16);limits=[(pred[0]-sigma,pred[0]+sigma),(pred[1]-sigma,pred[1]+sigma),(D*.72,D*1.32)];ts=templates[id]
 def score(z,detail=False):
  xx=(z[0]+u*z[2])/2;yy=(z[1]+v*z[2])/2;valid=(xx>=1)&(xx<959)&(yy>=1)&(yy<539)
  for other in foreground:
   if other[2]>z[2]*1.025:valid&=(xx-other[0]/2)**2+(yy-other[1]/2)**2>(other[2]*.50/2)**2
  # Temporary conservative rectangle for the birthday notification. This does
  # not render a rectangle; it prevents white foreground UI from shrinking a face.
  card=card_bounds.get(frame)
  if card and card['opacity']>.5:
   x0,y0,x1,y1=card['bbox'];valid&=~((xx>x0/2)&(xx<x1/2)&(yy>y0/2)&(yy<y1/2))
  if frame>=687:
   top={687:478,688:387}.get(frame,387);valid&=~((xx>310)&(xx<651)&(yy>top/2))
  vis=float(valid.mean())
  if valid.sum()<30:return (1e6,0.,vis,1.)if detail else 1e6
  obs=np.stack([map_coordinates(a[:,:,c],[yy[valid],xx[valid]],order=1)for c in range(3)],1);al=np.ones(len(blur_levels));tc=255-ts[:,valid];oc=255-obs
  if frame>=684:al=np.clip(np.sum(tc*oc[None,:,:],axis=(1,2))/np.maximum(1,np.sum(tc*tc,axis=(1,2))),.001,1)
  error=np.mean((oc[None,:,:]-al[:,None,None]*tc)**2,2);cost=np.mean(np.minimum(error,5000),axis=1);i=int(np.argmin(cost));penalty=20*(((z[0]-pred[0])/sigma)**2+((z[1]-pred[1])/sigma)**2)+60*np.log(z[2]/D)**2
  return (float(cost[i]),float(blur_levels[i]),vis,float(al[i]))if detail else float(cost[i]+penalty)
 before=score(pred,True)
 if before[0]>9e5:result=pred;detail=before
 else:
  r=minimize(score,pred,method='Powell',bounds=limits,options={'xtol':.1,'ftol':.0004,'maxiter':5});result=r.x;detail=score(result,True)
  if detail[0]>before[0]*1.1:result=pred;detail=before
 mse,blur,vis,opacity=detail
 first_observable={'71':614,'75':621,'79':614,'85':618,'89':617,'93':614,'new-foliage-woman':614}.get(id,603)
 if frame<first_observable:opacity=0.
 if frame<617 and mse>3000 and vis<.3:opacity=0.
 return dict(cx=float(result[0]),cy=float(result[1]),diameter=float(result[2]),blurFraction=blur,opacity=opacity,mse=None if mse>9e5 else mse,visibleFraction=vis)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--anchors-only',action='store_true');parser.add_argument('--frames');args=parser.parse_args();results={id:[]for id in faces};frames=[615,618,624,630,645,660,681,686] if args.anchors_only else list(range(603,689))
 if args.frames:
  frames=[f for part in args.frames.split(',') for f in range(int(part.split(':')[0]),int(part.split(':')[-1])+1)]
  if (B/'camera-fit.json').exists():
   previous=json.load(open(B/'camera-fit.json'));results={id:[r for r in rs if r['frame'] not in frames] for id,rs in previous.items()}
 for f in frames:
  a=np.array(Image.open(F/f'{f:06d}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS)).astype(np.float32);preds={id:projective_curve(id,min(f,683))for id in faces}
  # Derive the fast closing camera from the reliable large-disc observations,
  # then refine each still-editable photo independently on the actual source.
  if f>=684:
   obs=[]
   for id in ['91','93','95']:
    r=next((r for r in old[faces[id]['id']]if r['frame']==min(f,687)),None)
    if r and r['mse']<500:obs.append((id,r))
   if obs:
    sc=float(np.median([r['diameter']/preds[id][2]for id,r in obs]));tx=float(np.median([r['cx']-(960+(preds[id][0]-960)*sc)for id,r in obs]));ty=float(np.median([r['cy']-(540+(preds[id][1]-540)*sc)for id,r in obs]))
    for id,p in preds.items():preds[id]=np.array([960+(p[0]-960)*sc+tx,540+(p[1]-540)*sc+ty,p[2]*sc])
  front=[]
  for id in sorted(faces,key=lambda k:preds[k][2],reverse=True):
   r=fit(a,id,preds[id],front,f);r['frame']=f;results[id].append(r);front.append(np.array([r['cx'],r['cy'],r['diameter']])) if r['opacity']>.5 else None
  if f%3==0 or args.anchors_only:print('fit frame',f,flush=True);(B/'camera-fit-partial.json').write_text(json.dumps(results,indent=2)+'\n')
 for rows in results.values():rows.sort(key=lambda r:r['frame'])
 (B/('camera-fit-anchors.json'if args.anchors_only else'camera-fit.json')).write_text(json.dumps(results,indent=2)+'\n');print('complete',flush=True)

if __name__=='__main__':main()
