"""Close native booking/commerce transitions identified by every-frame v10 QA."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from scipy.signal import correlate
from scipy.ndimage import label,find_objects,gaussian_filter1d
from native_components import native_bubble,asset,image,group,rect,provenance
from component_pose_fit import Actor
D=Path(__file__).resolve().parent;R=D.parent.parent;F=D/'measurements/native-transition';BASE=R/'outputs/05-linq/final-v10';O=D/'measurements/middle-v11';O.mkdir(exist_ok=True)
s=json.loads((BASE/'scene.json').read_text())
def restore(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str):o[k]=str((BASE/v).resolve())
   else:restore(v)
 elif isinstance(o,list):
  for x in o:restore(x)
restore(s);ls=s['layers']
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
def get(id):return next(q for q in ls if q['id']==id)
def replace(id,node):ls[ls.index(get(id))]=node
def key(rr,k):return [{'t':r['frame']/30,'value':float(r[k]),'ease':'linear'} for r in rr]
def unique(o,prefix):
 o['id']=prefix+o['id']
 for q in o.get('children',[]):unique(q,prefix)
def actor(name,id,ref,box,start,end,semantic=None,raster=False):
 a=Actor(name,ref,box,start,end)
 for f in range(start,end+1):a.fit(f,load(f))
 rr=[r for r in a.rows if r['alpha']>.05 and r['mse'] is not None and r['mse']<.08]
 ar=np.uint8(a.art);parts=[image(name+'-raster',asset('v11-'+name,ar,box,ref),0,0,ar.shape[1],ar.shape[0])] if raster else native_bubble('v11-'+name,ar,semantic)
 g=group(id,parts,x=box[0],start=rr[0]['frame']/30,end=(rr[-1]['frame']+1)/30,keyframes={'y':key(rr,'y'),'opacity':key(rr,'alpha')})
 (O/(name+'.json')).write_text(json.dumps({'box':box,'rows':a.rows},indent=2));return g,rr

booked,rr=actor('booked','g-567',500,[95,178,582,515],475,513,'Your flight is booked! ✈️\n\nFrontier Airlines\nJuly 2 | 1 passenger\nAircraft: Airbus A321');replace('g-567',booked)
question,rr=actor('necklaces-question','g-572',530,[493,222,865,380],511,542,'i wanna check out\nsome necklaces');replace('g-572',question)
hot,hr=actor('hot-reply','v11-hot-reply',560,[93,184,637,277],533,578,"Here’s what’s hot right now 🔥")
link,lr=actor('jewelry-link','v11-jewelry-link',560,[93,293,489,453],540,578,raster=True)
replace('g-580',group('g-580',[hot,link],start=min(hot['start'],link['start']),end=579/30))
bg=get('broad-v5-group-59');bg.update(children=[copy.deepcopy(hot),copy.deepcopy(link)],start=579/30,end=657/30,opacity=1,blur=10)
for q in bg['children']:q.pop('start',None);q.pop('end',None);unique(q,'background-v11-')
confirm,cr=actor('confirmed','g-595',670,[94,292,581,433],649,686,"Order confirmed, I’ll ping you\nwhen tracking’s ready 📦");replace('g-595',confirm)
get('broad-v5-background-45')['end']=468/30
get('broad-v5-group-59')['end']=651/30
# Exact early overlap: the next groceries bubble is already visible at685–686.
early=Actor('groceries-early',735,[507,47,870,190],680,686)
for f in range(680,687):early.fit(f,load(f))
er=[r for r in early.rows if r['alpha']>.05 and r['mse'] is not None and r['mse']<.08]
gro=get('broad-v5-group-25')
if er:
 gro['start']=er[0]['frame']/30
 for k,v in [('y','y'),('opacity','alpha')]:gro['keyframes'][k]=key(er,v)+gro['keyframes'][k]
# Sample opacity inside the remaining clipped Cash body, never below it.
cash=get('linq-measured-v6-group-36');panel=next(q for q in cash['children'] if q['id']=='v10-cash-panel');cams={r['frame']:r for r in json.loads((D/'measurements/object-poses-v10/cash-ui-cameras.json').read_text())}
for k in panel['keyframes']['opacity']:
 f=round(k['t']*30)
 if f<834 or f not in cams or not cams[f]['bbox']:continue
 bb=cams[f]['bbox'];y=max(bb[1],min(bb[1]+60,bb[3]-8));v=float(np.median(load(f)[y:y+3,390:420]));k['value']=float(np.clip((255-v)/238,0,1))

def fit_art(ar,x,frames,ymin,ymax,sigmas=(0,),mse_limit=.12):
 ar=ar.astype(np.float32);H=len(ar);W=ar.shape[1];ys=np.arange(ymin,ymax+1);world=np.arange(720)[None,:];idx=world-ys[:,None];valid=(idx>=0)&(idx<H);ix=np.clip(idx,0,H-1);profiles=[]
 for sigma in sigmas:
  p=(255-ar).mean(1)
  if sigma:p=gaussian_filter1d(p,sigma,axis=0,mode='constant')
  profiles.append((p[ix]*valid[:,:,None]).reshape(len(ys),-1))
 models=np.concatenate(profiles);den=np.sum(models*models,1);rr=[]
 for f in frames:
  p=(255-load(f)[:,x:x+W]).mean(1);dots=models@p.ravel();alpha=dots/np.maximum(1,den);energy=np.tile(valid@np.sum(p*p,1),len(sigmas));err=np.maximum(0,energy-dots*dots/np.maximum(1,den))/np.maximum(energy,1);err[(alpha<.015)|(alpha>1.5)]=1e6;k=int(np.argmin(err));iy=k%len(ys);sub=0
  if 0<iy<len(ys)-1:
   dd=err[k-1]-2*err[k]+err[k+1]
   if dd>0:sub=float(np.clip(.5*(err[k-1]-err[k+1])/dd,-.5,.5))
  if err[k]<mse_limit:rr.append({'frame':f,'y':float(ys[iy]+sub),'alpha':float(np.clip(alpha[k],0,1)),'blur':sigmas[k//len(ys)],'mse':float(err[k])})
 return rr

# The selected seat UI scrolls upward and fades through475, before the booked reply.
ar=load(465)[:,188:770];exit=fit_art(ar,188,range(468,479),-500,20,(0,1,2,3,4,6,8,12),.12);p=asset('v11-seat-exit-static-ui',np.uint8(ar),[188,0,770,720],465)
out=group('v11-seat-exit',[image('seat-exit-art',p,188,0,582,720)],start=468/30,end=(exit[-1]['frame']+1)/30,keyframes={'y':key(exit,'y'),'opacity':key(exit,'alpha'),'blur':key(exit,'blur')})
get('rich-group-6')['end']=468/30;ls.insert(ls.index(get('rich-group-6'))+1,out)
(O/'seat-exit.json').write_text(json.dumps(exit,indent=2))

# Actual grid document scroll, followed by a separate product-detail sheet that
# rises over it. The old whole-grid zoom incorrectly enlarged every product.
grid=np.full((844,565,3),255,np.float32);grid[:720]=load(600)[:,198:763];grid[650:]=load(620)[526:720,198:763]
gp=asset('v11-jewelry-tall-grid',np.uint8(grid),[198,0,763,720],600,'bounded static two-column product-grid document, lower rows stitched from620 after measured124px scroll')
gr=fit_art(grid,198,range(577,621),-160,700,(0,),.12)
g=get('broad-v5-group-62');g.update(children=[image('grid-document',gp,198,0,565,844)],x=0,start=gr[0]['frame']/30,end=627/30,clip={'x':198,'y':0,'width':565,'height':720},keyframes={'y':key(gr,'y'),'opacity':key(gr,'alpha')})
# Fixed viewport wrapper, with moving document inside it.
inner=copy.deepcopy(g);inner['id']='v11-jewelry-grid-camera';inner.pop('clip');replace('broad-v5-group-62',group('broad-v5-group-62',[inner],start=g['start'],end=g['end'],clip={'x':198,'y':0,'width':565,'height':720}))

# Register the unchanged full-size necklace photograph across the rising detail
# sheet. Source625 shows its upper curve,640 reveals its pendant/metadata.
t=255-load(640)[:400,322:636].mean(2);v=255-load(625)[:,322:636].mean(2);dots=correlate(v,t,mode='valid',method='fft')[:,0];en=np.r_[0,np.cumsum(np.sum(v*v,1))];err=en[400:]-en[:-400]+np.sum(t*t)-2*dots;k=int(np.argmin(err));sub=0.
if 0<k<len(err)-1:
 dd=err[k-1]-2*err[k]+err[k+1]
 if dd>0:sub=float(np.clip(.5*(err[k-1]-err[k+1])/dd,-.5,.5))
offset=k+sub;K=int(round(offset));apex_ref=80-offset;blackH=513-apex_ref;photoH=K+513-80+4
photo=np.full((photoH,327,3),255,np.float32);photo[:640]=load(625)[80:720,316:643];photo[600:]=load(640)[600-K+80:photoH-K+80,316:643]
dpH=468+K+200;doc=np.full((dpH,565,3),255,np.float32);doc[28:28+photoH,118:445]=photo;doc[468+K:]=load(640)[520:720,198:763]
dp=asset('v11-jewelry-detail-document',np.uint8(doc),[198,0,763,720],640,'bounded static product detail document; original photograph reconstructed from625/640 registration; UI metadata static bitmap')
dr=fit_art(doc,198,range(621,658),-600,400,(0,1,2,4,8),.12)
detail=get('g-590');detail.update(children=[image('detail-document',dp,198,0,565,dpH)],start=621/30,end=(dr[-1]['frame']+1)/30,keyframes={'y':key(dr,'y'),'opacity':key(dr,'alpha'),'blur':key(dr,'blur')})
# Its original top margin28 rises with the sheet and naturally wipes the old grid.
fixed=group('g-590',[detail|{'id':'v11-detail-camera'}],start=detail['start'],end=detail['end'],clip={'x':198,'y':0,'width':565,'height':720});replace('g-590',fixed)
(O/'grid.json').write_text(json.dumps(gr,indent=2));(O/'detail.json').write_text(json.dumps({'registrationOffset':offset,'apexReference640':apex_ref,'photoHeight':photoH,'rows':dr},indent=2));(D/'assets/middle-v11-provenance.json').write_text(json.dumps(provenance,indent=2));(D/'scene-middle-v11.json').write_text(json.dumps(s,indent=2)+'\n');print('Seat',exit);print('Grid',gr[:2],gr[-1:]);print('Detail offset',offset,dr[:2],dr[-1:]);print('Confirmation',cr[:2],cr[-1:])
