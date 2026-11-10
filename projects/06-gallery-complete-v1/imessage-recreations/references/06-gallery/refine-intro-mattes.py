"""Remove unrelated background rectangles from static UI crops; retain only semantic silhouettes.
The rejected v1 revealed rectangular fields and a short hardware strip at107.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
R=Path('/workspace/imessage-recreations');REF=R/'references/06-gallery';P=R/'verification/fidelity-review/06-intro';AS=REF/'assets/intro-review';s=json.loads((REF/'intro-review-elements.json').read_text());group=s['insert_before']['g-1129'][0];nodes={q['id']:q for q in group['children']};ledger=[]
def rgba(a,mask):
 alpha=(255-a.min(2))/255*mask;alpha[alpha<2/255]=0;rgb=np.where(alpha[:,:,None]>0,(a-255*(1-alpha[:,:,None]))/np.maximum(1e-5,alpha[:,:,None]),0);return np.concatenate((np.clip(rgb,0,255),alpha[:,:,None]*255),2).round().astype('uint8')
def update(n,im):
 p=AS/(n['id']+'-matte2.png');Image.fromarray(im).save(p);n['src']=str(p);n['width']=im.shape[1];n['height']=im.shape[0];ledger.append(dict(id=n['id'],asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceFrame=n['sourceFrame'],sourceBounds=n['sourceBounds'],notice='Semantic silhouette mask removes unrelated screen-background rectangles; bitmap internals, native poses.'))
configs={'marcus':[[674,583,1118,711],[594,598,672,683],[700,540,860,582]],'priya':[[675,749,1183,876],[594,775,672,879],[700,709,850,752]],'dan':[[675,914,1129,1041],[594,937,673,1044],[700,875,850,920]],'rene':[[675,887,1131,1000],[594,923,674,1004],[700,850,850,890]]}
for name,boxes in configs.items():
 n=nodes['rene-intro-'+name];cb=n['sourceBounds'];a=np.array(Image.open(P/'source'/f'{n["sourceFrame"]+1:04d}.png').convert('RGB')).astype(float)[cb[1]:cb[3],cb[0]:cb[2]];mask=np.zeros(a.shape[:2],bool)
 for j,b in enumerate(boxes):
  xl=max(0,b[0]-cb[0]);xr=min(a.shape[1],b[2]-cb[0]);yl=max(0,b[1]-cb[1]);yr=min(a.shape[0],b[3]-cb[1]);v=a[yl:yr,xl:xr];m=v.mean(2)<(244 if j<2 else 230)
  if j==0:m=ndimage.binary_fill_holes(m)
  m=ndimage.binary_dilation(m,iterations=2);mask[yl:yr,xl:xr]|=m
 update(n,rgba(a,mask))
for id,threshold in [('rene-intro-date',225),('rene-intro-precut-composer',232)]:
 n=nodes[id];cb=n['sourceBounds'];a=np.array(Image.open(P/'source'/f'{n["sourceFrame"]+1:04d}.png').convert('RGB')).astype(float)[cb[1]:cb[3],cb[0]:cb[2]];mask=ndimage.binary_dilation(a.mean(2)<threshold,iterations=2);update(n,rgba(a,mask))
# Extend just the physical side edges. The below-source continuation is disclosed inference.
n=nodes['rene-intro-postcut-hardware'];im=np.array(Image.open(n['src']).convert('RGBA'));ext=np.tile(im[-50:],(5,1,1));im=np.concatenate((im,ext),0);update(n,im);ledger[-1]['notice']='Genuine bezel-only texture, transparent screen. Native continuation repeats the last50 visible bezel rows below source crop; inferred unseen physical texture.'
# Header background has a feathered lower margin; no rectangular cut at the title baseline.
n=nodes['rene-intro-postcut-header'];old=n['sourceBounds'];cb=[old[0],old[1],old[2],550];a=np.array(Image.open(P/'source/0070.png').convert('RGB')).astype(float)[cb[1]:cb[3],cb[0]:cb[2]]
# Remove the independently animated date from this static header backing.
for gy in range(480,550):
 yy=gy-cb[1];bg=np.median(a[yy,180:270],axis=0);a[yy,285:525]=bg
mask=Image.new('L',(a.shape[1],a.shape[0]),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,a.shape[1],2000),radius=95,fill=255);m=np.array(mask)/255;Y=np.arange(cb[1],cb[3])[:,None];m*=np.clip((550-Y)/101,0,1);m[Y[:,0]<449]=1;n['sourceBounds']=cb;update(n,rgba(a,m))
# A native soft background reproduces the diffuse field before the phone cut.
if not any(q['id']=='rene-intro-soft-background' for q in group['children']):group['children'].insert(0,dict(type='circle',id='rene-intro-soft-background',x=330,y=-350,width=1260,height=650,fill='#f7f7f7',blur=100,start=0,end=54/30))
s['assets']+=ledger;s['measurements']['matte-diagnosis']='Rejected rectangular screen-background seams in v1. Semantic masks retain each message/avatar/name, date and composer; feathered header backing and genuine bezel-only continuation remove cut edges.';(REF/'intro-review-elements.json').write_text(json.dumps(s,indent=2));(REF/'intro-matte2-provenance.json').write_text(json.dumps(ledger,indent=2));print('updated',len(ledger))
