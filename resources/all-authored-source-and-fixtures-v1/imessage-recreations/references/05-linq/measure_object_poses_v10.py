"""Fit independent native object poses from static artwork and exact source frames."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import label,find_objects
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';OUT=D/'measurements/object-poses-v10';OUT.mkdir(parents=True,exist_ok=True)
features={x['frame']:x for x in json.loads((D/'measurements/transition-features.json').read_text())}
def load(f):return np.asarray(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
def bbox(mask):
 y,x=np.nonzero(mask)
 return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
class Actor:
 def __init__(self,name,ref,box,start,end,sample=None):
  self.name=name;self.box=box;self.start=start;self.end=end;self.art=load(ref)[box[1]:box[3],box[0]:box[2]].copy();self.H=len(self.art);self.W=self.art.shape[1];self.x=box[0];self.sample=sample;self.rows=[]
  if sample is None:profile=(255-self.art).mean(axis=1)
  else:profile=(255-load(ref)[box[1]:box[3],sample[0]:sample[1]]).mean(axis=1)
  self.ys=np.arange(-self.H+8,713);world=np.arange(720)[None,:];idx=world-self.ys[:,None];self.valid=((idx>=0)&(idx<self.H)).astype(np.float32);idx=np.clip(idx,0,self.H-1);self.models=(profile[idx]*self.valid[:,:,None]).reshape(len(self.ys),-1);self.den=np.sum(self.models*self.models,axis=1);self.safe=np.maximum(self.den,1)
 def fit(self,f,a):
  if self.sample is None:p=(255-a[:,self.x:self.x+self.W]).mean(axis=1)
  else:p=(255-a[:,self.sample[0]:self.sample[1]]).mean(axis=1)
  dot=self.models@p.reshape(-1);energy=self.valid@np.sum(p*p,axis=1);alpha=dot/self.safe;error=np.maximum(0,energy-dot*dot/self.safe)/np.maximum(energy,self.safe*.0001);error[(alpha<.05)|(alpha>1.6)]=1e5
  at=int(np.argmin(error));y=float(self.ys[at]);sub=0.
  if 0<at<len(error)-1 and max(error[at-1],error[at+1])<1e4:
   den=error[at-1]-2*error[at]+error[at+1]
   if den>0:sub=float(np.clip(.5*(error[at-1]-error[at+1])/den,-.5,.5))
  if error[at]>.15:self.rows.append({'frame':f,'y':None,'alpha':0,'mse':None})
  else:self.rows.append({'frame':f,'y':y+sub,'alpha':float(np.clip(alpha[at],0,1)),'mse':float(error[at])})
actors=[Actor('chess-preview',171,[351,107,861,500],148,205),Actor('chess-question',195,[389,448,864,548],150,205),Actor('chess-reply',195,[94,550,406,654],176,205),Actor('flight-question',276,[323,260,865,489],253,325,sample=(820,835)),Actor('flight-reply',351,[93,68,635,206],310,351),Actor('flight-preview',351,[91,231,638,690],315,351),Actor('groceries',735,[507,47,870,190],687,772),Actor('cash-reply',735,[108,204,498,297],699,772),Actor('cash-request',729,[107,321,545,690],705,772),Actor('gotit',849,[99,309,536,419],827,854)]
for f in range(148,855):
 active=[x for x in actors if x.start<=f<=x.end]
 if not active or not (F/f'{f:06}.png').exists():continue
 a=load(f)
 for actor in active:actor.fit(f,a)
for actor in actors:
 Image.fromarray(np.uint8(actor.art)).save(OUT/(actor.name+'-reference.png'));(OUT/(actor.name+'.json')).write_text(json.dumps({'name':actor.name,'reference_box':actor.box,'poses':actor.rows},indent=2));good=[x for x in actor.rows if x['alpha']>.05];print(actor.name,'first',good[:1],'last',good[-1:],flush=True)
# Direct shape measurements for independently moving Cash input/panel and chess pages.
pay=[];chess=[];gotit=[]
for f in range(705,947):
 row=features.get(f)
 if not row:continue
 if 768<=f<=840:
  a=load(f);z=a.astype(np.int16);m=(z.max(axis=2)<240);m[:,:195]=False;m[:,242:]=False;labs,n=label(m);cross=[]
  for sl in find_objects(labs):
   if sl is None:continue
   y,x=sl;w,h=x.stop-x.start,y.stop-y.start
   if 18<=w<=40 and 18<=h<=42:cross.append([x.start,y.start,x.stop,y.stop])
  candidates=[b for b in row['dark'] if b[2]-b[0]>300 and b[0]>=175 and b[2]<=790]
  b=max(candidates,key=lambda b:(b[2]-b[0])*(b[3]-b[1])) if candidates else None
  py=(b[1]-235 if b[1]>0 else b[3]-695) if b else None;cy=(cross[0][1]-160) if cross else None
  pay.append({'frame':f,'panel_y':py,'composer_y':cy,'cross':cross,'bbox':b})
 if 840<=f<=946:
  b=row.get('chess_panel_xbounds')
  x=None if b is None else ((b[0]-3+b[1]-483)/2 if b[0]>0 and b[1]<960 else b[0]-3 if b[0]>0 else b[1]-483)
  chess.append({'frame':f,'x':x,'bounds':b})
 if 827<=f<=872:
  cc=[b for b in row['gray'] if b[0]<150 and b[2]-b[0]>45 and b[3]-b[1]>45]
  b=max(cc,key=lambda b:(b[2]-b[0])*(b[3]-b[1])) if cc else None
  if b:
   left=b[0] if b[0]>0 else b[2]-433;gotit.append({'frame':f,'x':left,'y':b[1],'box':b})
(OUT/'cash-ui-cameras.json').write_text(json.dumps(pay,indent=2));(OUT/'second-chess-x.json').write_text(json.dumps(chess,indent=2));(OUT/'gotit-x.json').write_text(json.dumps(gotit,indent=2));print('Direct camera records complete',flush=True)
# First board: fit its immutable d-file (no moving pawns) for alpha and Y, while retaining the measured X.
ref=load(246);profiles=[];sigmas=[0,1,2,4,6]
for sigma in sigmas:
 im=np.asarray(Image.fromarray(np.uint8(ref)).filter(ImageFilter.GaussianBlur(sigma))).astype(float);profiles.append((255-im[:,437:445]).mean(axis=(1,2)))
ygrid=np.arange(-10,61);world=np.arange(260);models=[]
for profile in profiles:models.extend([np.interp(world-y,np.arange(720),profile,left=0,right=0) for y in ygrid])
models=np.asarray(models);den=np.sum(models*models,axis=1);board=[];lastx=152
for f in range(209,266):
 a=load(f);b=features[f].get('board_top_bounds');x=lastx
 if b and b[2]-b[0]>400:x=((b[0]+b[2]-658)/2 if b[0]>0 else b[2]-658)
 candidates=[]
 for dx in [-4,-2,0,2,4]:
  xx=int(round(441+x-152+dx));p=(255-a[:260,max(0,xx-4):min(960,xx+4)]).mean(axis=(1,2));dot=models@p;alpha=dot/den;err=np.maximum(0,np.dot(p,p)-dot*dot/den)/den;at=int(np.argmin(err));candidates.append((float(err[at]),x+dx,float(np.clip(alpha[at],0,1)),int(ygrid[at%len(ygrid)]),sigmas[at//len(ygrid)]))
 best=min(candidates);lastx=best[1];board.append({'frame':f,'x':best[1],'y':best[3],'alpha':best[2],'blur':best[4],'mse':best[0]})
(OUT/'first-board.json').write_text(json.dumps(board,indent=2));print('First board',board[0],board[1],board[49],flush=True)
