from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image,ImageDraw
R=Path('/workspace/imessage-recreations');REF=R/'references/06-gallery';P=R/'verification/fidelity-review/06-intro';AS=REF/'assets/intro-review';s=json.loads((REF/'intro-review-elements.json').read_text());g=s['insert_before']['g-1129'][0];ns={q['id']:q for q in g['children']};ledger=[]
def frame(f):return np.array(Image.open(P/'source'/f'{f+1:04d}.png').convert('RGB')).astype(float)
def peaks(f):
 a=frame(f);prof=np.median(a[120:1000].mean(2),axis=0);L=int(np.argmin(prof[100:450])+100);R=int(np.argmin(prof[1450:1850])+1450);return L,R,min(1,(255-min(prof[L],prof[R]))/250)
L0,R0,_=peaks(39);obs=[]
for f in range(28,54):
 L,RR,alpha=peaks(f);scale=(RR-L)/(R0-L0);obs.append(dict(frame=f,L=L,R=RR,scale=scale,x=L-L0*scale,alpha=alpha))
for side in ['left','right']:
 n=ns['rene-intro-precut-'+side];orig=np.array(Image.open(n['src']).convert('RGBA'));im=np.concatenate((orig,np.tile(orig[-120:],(8,1,1))),0);p=AS/(n['id']+'-hardware3.png');Image.fromarray(im).save(p);n['src']=str(p);n['height']=im.shape[0];b=n['sourceBounds'];n['keyframes']['x']=[dict(t=q['frame']/30,value=q['x']+b[0]*q['scale'],ease='linear') for q in obs];n['keyframes']['y']=[dict(t=28/30,value=0)];n['keyframes']['scaleX']=[dict(t=q['frame']/30,value=q['scale'],ease='linear') for q in obs];n['keyframes']['scaleY']=[dict(t=q['frame']/30,value=q['scale'],ease='linear') for q in obs];n['keyframes']['opacity']=[dict(t=q['frame']/30,value=q['alpha'],ease='linear') for q in obs];ledger.append(dict(id=n['id'],asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),notice='Independent per-frame horizontal physical-bezel positions. Long vertical source bezel texture continues below viewport; unobserved continuation repeats last120 rows. Vertical button trajectory remains approximate.'))
# Correct the header top-corner mask while preserving its feathered background margin.
n=ns['rene-intro-postcut-header'];cb=n['sourceBounds'];a=frame(69)[cb[1]:cb[3],cb[0]:cb[2]].copy()
for gy in range(480,550):
 yy=gy-cb[1];a[yy,285:525]=np.median(a[yy,180:270],axis=0)
mask=Image.new('L',(a.shape[1],a.shape[0]),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,a.shape[1],2000),radius=95,fill=255);m=np.array(mask)/255;Y=np.arange(cb[1],cb[3])[:,None];m*=np.where(Y<449,1,np.clip((550-Y)/101,0,1));alpha=(255-a.min(2))/255*m;alpha[alpha<2/255]=0;rgb=np.where(alpha[:,:,None]>0,(a-255*(1-alpha[:,:,None]))/np.maximum(1e-5,alpha[:,:,None]),0);im=np.concatenate((np.clip(rgb,0,255),alpha[:,:,None]*255),2).round().astype('uint8');p=AS/(n['id']+'-hardware3.png');Image.fromarray(im).save(p);n['src']=str(p);ledger.append(dict(id=n['id'],asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),notice='Header mask preserves rounded screen opening and feathered background margin.'))
s['assets']+=ledger;s['measurements']['precut-hardware-independent']=obs;(REF/'intro-review-elements.json').write_text(json.dumps(s,indent=2));(REF/'intro-hardware3-provenance.json').write_text(json.dumps(ledger,indent=2));print(obs)
