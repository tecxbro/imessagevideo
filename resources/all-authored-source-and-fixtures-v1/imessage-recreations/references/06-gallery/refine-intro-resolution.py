"""Use a fully resolved large canonical UI crop before the cut, avoiding small-text upsampling."""
from pathlib import Path
import copy,json,hashlib,numpy as np
from PIL import Image
from scipy import ndimage
R=Path('/workspace/imessage-recreations');REF=R/'references/06-gallery';P=R/'verification/fidelity-review/06-intro';AS=REF/'assets/intro-review';s=json.loads((REF/'intro-review-elements.json').read_text());g=s['insert_before']['g-1129'][0];by={q['id']:q for q in g['children']};ledger=[]
configs=[('marcus',15,[285,328,1582,722],[[490,410,1578,720],[285,442,465,623],[562,328,870,408]]),('priya',39,[280,637,1377,940],[[436,692,1372,938],[280,751,415,889],[485,637,720,695]]),('date',39,[820,204,1120,313],[[820,204,1120,313]])]
for name,cf,cb,boxes in configs:
 old=by['rene-intro-'+name];n=copy.deepcopy(old);n['id']=old['id']+'-precut-hires';n['end']=54/30;old['start']=54/30;a=np.array(Image.open(P/'source'/f'{cf+1:04d}.png').convert('RGB')).astype(float)[cb[1]:cb[3],cb[0]:cb[2]];mask=np.zeros(a.shape[:2],bool)
 for j,b in enumerate(boxes):
  xl=max(0,b[0]-cb[0]);xr=min(a.shape[1],b[2]-cb[0]);yl=max(0,b[1]-cb[1]);yr=min(a.shape[0],b[3]-cb[1]);v=a[yl:yr,xl:xr];m=v.mean(2)<(230 if name=='date' or j==2 else 244)
  if j==0 and name!='date':m=ndimage.binary_fill_holes(m)
  mask[yl:yr,xl:xr]|=ndimage.binary_dilation(m,iterations=2)
 al=(255-a.min(2))/255*mask;al[al<2/255]=0;rgb=np.where(al[:,:,None]>0,(a-255*(1-al[:,:,None]))/np.maximum(1e-5,al[:,:,None]),0);rgba=np.concatenate((np.clip(rgb,0,255),al[:,:,None]*255),2).round().astype('uint8');p=AS/(n['id']+'.png');Image.fromarray(rgba).save(p);n.update(src=str(p),width=cb[2]-cb[0],height=cb[3]-cb[1],sourceFrame=cf,sourceBounds=cb);obs=s['measurements'][name];ref=next(q for q in obs if q['frame']==cf);vals=[]
 for q in obs:
  if q['frame']>=54:continue
  sx=q['scaleX']/ref['scaleX'];sy=q['scaleY']/ref['scaleY'];vals.append(dict(frame=q['frame'],x=q['x']+(cb[0]-ref['x'])*sx,y=q['y']+(cb[1]-ref['y'])*sy,scaleX=sx,scaleY=sy,opacity=q['opacity']))
 n['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in vals] for k in ['x','y','scaleX','scaleY','opacity']};i=g['children'].index(old);g['children'].insert(i,n);ledger.append(dict(id=n['id'],sourceFrame=cf,sourceBounds=cb,asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceSHA256=hashlib.sha256((P/'source'/f'{cf+1:04d}.png').read_bytes()).hexdigest(),notice='Fully resolved static message/date source artwork for enlarged pre-cut view; semantic silhouette, native measured poses. Avoids enlarging small raster text. Bitmap internal copy.'))
s['assets']+=ledger;(REF/'intro-review-elements.json').write_text(json.dumps(s,indent=2));(REF/'intro-hires-provenance.json').write_text(json.dumps(ledger,indent=2));print('assets',len(ledger))
