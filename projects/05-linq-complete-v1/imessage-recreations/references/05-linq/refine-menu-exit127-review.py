"""Native127 diagnosis: missing thin card border/long bottom shadow and soft label edges."""
from pathlib import Path
import json,hashlib,io,numpy as np
from PIL import Image
from scipy import ndimage
import cairosvg
R=Path('/workspace/imessage-recreations');REF=R/'references/05-linq';SRC=REF/'assets/root-handoffs-measure/frame-127.png';AS=REF/'assets/menu-games-handoff-review';s=json.loads((REF/'menu-games-handoff-review-elements.json').read_text());g=s['insert_before']['g-138'][0];a=np.array(Image.open(SRC).convert('RGB')).astype(float);ledger=[];chrome=[]
# These three disjoint strips contain only actual panel chrome, no menu items.
for name,b in [('left',[80,0,175,674]),('right',[790,0,880,674]),('bottom',[80,674,880,720])]:
 v=a[b[1]:b[3],b[0]:b[2]];al=(255-v.min(2))/255;al[al<2/255]=0;rgb=np.where(al[:,:,None]>0,(v-255*(1-al[:,:,None]))/np.maximum(1e-5,al[:,:,None]),0);rgba=np.concatenate((np.clip(rgb,0,255),al[:,:,None]*255),2).round().astype('uint8');p=AS/f'menu-chrome-{name}-127.png';Image.fromarray(rgba).save(p);id='handoff-menu-chrome-'+name;chrome.append(dict(type='image',id=id,src=str(p),x=b[0],y=b[1],width=b[2]-b[0],height=b[3]-b[1],sourceFrame=127,sourceBounds=b,semanticText='Menu panel '+name+' chrome',editability='Genuine isolated panel edge/shadow; native geometry/lifetime, bitmap texture.'));ledger.append(dict(id=id,sourceFrame=127,sourceBounds=b,asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceSHA256=hashlib.sha256(SRC.read_bytes()).hexdigest()))
fits=[]
for n in g['children']:
 if n['type']!='path' or n['semanticText']=='Polls':continue
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="720"><path fill="black" d="{n["d"]}"/></svg>';buf=cairosvg.svg2png(bytestring=svg.encode());p=np.array(Image.open(io.BytesIO(buf)).convert('RGBA'))[:,:,3]/255;bb=n['sourceBounds'];b=[max(0,bb[0]-6),max(0,bb[1]-6),min(960,bb[2]+6),min(720,bb[3]+6)];A=(255-a[b[1]:b[3],b[0]:b[2]].mean(2))/255;best=None
 for sig in [0,.3,.5,.7,1,1.3,1.7,2,2.5,3,4]:
  P=ndimage.gaussian_filter(p,sig,mode='constant') if sig else p;P=P[b[1]:b[3],b[0]:b[2]];op=min(1,float((A*P).sum()/max(1e-9,(P*P).sum())));err=float(((A-op*P)**2).mean());q=dict(id=n['id'],blur=sig,opacity=op,mse=err)
  if best is None or err<best['mse']:best=q
 n['opacity']=best['opacity'];n['blur']=best['blur'];fits.append(best)
g['children']=chrome+[n for n in g['children'] if n['id']!='handoff-menu-white-card'];s['assets']+=ledger;s['exit127_refinement']=dict(cause='Native difference attribution: missing source panel borderRGB218 atx108 and long bottom shadow dominated non-UI error; binary contour edge too sharp for faded soft copy.',fits=fits);(REF/'menu-games-handoff-review-elements.json').write_text(json.dumps(s,indent=2));(REF/'menu-games-exit127-provenance.json').write_text(json.dumps(dict(assets=ledger,fits=fits),indent=2));print(fits)
