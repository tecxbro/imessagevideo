"""Isolate early glass material from independent native actors and caption ink."""
from pathlib import Path
from PIL import Image
import json,numpy as np
from scipy import ndimage
from trace_glyphs import trace_alpha
REF=Path(__file__).resolve().parent;AS=REF/'assets/root-header-birth-v3';AS.mkdir(exist_ok=True);orbit=json.load(open(REF/'root-orbit-patch.json'));poses={int(r['id'].split('-')[-1]):r for r in orbit['layers']};measure={r['frame']:r for r in orbit['measurements']};layers=[];records=[]
def outlines(alpha,prefix,semantic,levels=16):
 peak=float(alpha.max());nodes=[];prev=0
 if peak<.003:return nodes
 for i in range(levels):
  d,_=trace_alpha(alpha/peak,threshold=(i+.5)/levels)
  if not d:continue
  cumulative=(i+1)/levels;op=(cumulative-prev)/max(1-prev,1e-9);prev=cumulative;nodes.append(dict(id=prefix+f'-level-{i}',type='path',d=d,fill='#000000',opacity=op,semanticText=semantic,editability='Native semantic optical contour pose, not live text.'))
 return [dict(id=prefix,type='group',opacity=peak,children=nodes)] if nodes else []
for n in range(588,598):
 a=np.array(Image.open(REF/f'assets/root-header-birth-measure/{n:06}.png').convert('RGB'));rgb=a.astype(float);g=rgb.mean(2);neutral=rgb.max(2)-rgb.min(2)<20;yy,xx=np.indices(g.shape);provider=np.zeros(g.shape,bool);bounds=[]
 for q in measure[n]['actors']:
  name=q['name']
  if name=='muse':
   actor=next(l for l in poses[n]['children'] if l['id'].endswith('middle-fly-muse'));child=actor['children'][0];x0=actor['x'];y0=actor['y'];x1=x0+child['width']*actor['scaleX'];y1=y0+child['height']*actor['scaleY']
  elif q.get('target'):
   x0,y0,x1,y1=q['target']
  else:continue
  cx=(x0+x1)/2;cy=(y0+y1)/2;rx=(x1-x0)/2+6;ry=(y1-y0)/2+6;provider|=((xx-cx)/rx)**2+((yy-cy)/ry)**2<=1;bounds.append(dict(name=name,bounds=[x0,y0,x1,y1],margin=6))
 caption=(g<220)&neutral&~provider;caption[:80]=False;caption[800:]=False;caption[:,:460]=False;caption[:,1460:]=False
 lab,_=ndimage.label(caption,np.ones((3,3)));clean=np.zeros(caption.shape,bool)
 for i,sl in enumerate(ndimage.find_objects(lab)):
  if sl is not None:clean[sl]|=lab[sl]==i+1
 caption=clean;children=[];caption_bounds=None;plate_box=None;support=np.zeros(g.shape,bool)
 if caption.sum()>40:
  ys,xs=np.where(caption);cx0,cx1,cy0,cy1=int(xs.min()),int(xs.max()+1),int(ys.min()),int(ys.max()+1);h=cy1-cy0;caption_bounds=[cx0,cy0,cx1,cy1];pad=max(35,round(h*1.4));px0=max(0,cx0-pad);px1=min(1920,cx1+pad);py0=max(0,cy0-round(h*.9));py1=min(1080,cy1+round(h*.9));plate_box=[px0,py0,px1,py1];support=ndimage.binary_dilation(caption,iterations=3)
  region=g[py0:py1,px0:px1];mask=support[py0:py1,px0:px1];valid=(~mask)&neutral[py0:py1,px0:px1]&(~provider[py0:py1,px0:px1]);den=ndimage.gaussian_filter(valid.astype(float),6);smooth=np.divide(ndimage.gaussian_filter(region*valid,6),den,out=np.full_like(region,253),where=den>.001);background=region.copy();background[mask]=smooth[mask];plate_alpha=np.clip((253-background)/253,0,1)*(neutral[py0:py1,px0:px1])*(~provider[py0:py1,px0:px1]);plate_alpha[plate_alpha<1.5/253]=0;plate=outlines(plate_alpha,f'root-header-birth-plate-{n}','Measured pale caption/glass material',levels=64);children.append(dict(id=f'root-header-birth-plate-origin-{n}',type='group',x=px0,y=py0,children=plate))
  ink=np.clip((background-region)/np.maximum(background,1),0,1)*mask;glyphs=outlines(ink,f'root-header-birth-copy-{n}','Team Offsite, Oct 10');children_caption=[dict(id=f'root-header-birth-copy-origin-{n}',type='group',x=px0,y=py0,children=glyphs)]
 else:children_caption=[]
 # Strict physical material/refraction texture, with every independent provider
 # and native neutral caption removed. This is not a whole scene/frame asset.
 material=(abs(rgb-253).max(2)>1.5)&~provider;material[:,:400]=False;material[:,1520:]=False;material[960:]=False
 if plate_box:
  px0,py0,px1,py1=plate_box;material[py0:py1,px0:px1]&=~neutral[py0:py1,px0:px1]
 material&=~support
 ys,xs=np.where(material)
 if len(xs):
  bx0,bx1,by0,by1=int(xs.min()),int(xs.max()+1),int(ys.min()),int(ys.max()+1);rgba=np.dstack([a[by0:by1,bx0:bx1],np.uint8(material[by0:by1,bx0:bx1])*255]);file=AS/f'glass-material-{n}.png';Image.fromarray(rgba).save(file);children.append(dict(id=f'root-header-birth-material-{n}',type='image',src=str(file),x=bx0,y=by0,width=bx1-bx0,height=by1-by0,sourceFrame=n,semanticText='Isolated original physical glass/refraction material',editability='Original bounded physical material/refraction only; independent provider discs and neutral caption ink are masked out. Native actors/caption/background stay separate. No source-frame/video playback.'))
 children+=children_caption;layers.append(dict(id=f'root-header-birth-pose-{n}',type='group',start=n/30,end=(n+1)/30,children=children,sourceFrame=n));records.append(dict(frame=n,providerExclusions=bounds,captionBounds=caption_bounds,plateBounds=plate_box,materialPixels=int(material.sum()),allProviderPixelsExcluded=bool(not (material&provider).any()),allNativeCaptionSupportExcluded=bool(not(material&support).any())))
(REF/'root-header-birth-patch-v3.json').write_text(json.dumps(dict(scope=[[588,597]],layers=layers,measurements=records,notice='Source glass emerges before the old598 gate; caption appears by595. Isolated original material/refraction retains independent native provider poses and native caption/plate contours. Existing598–629 accepted formation and all other states are unchanged.'),indent=2));print([(r['frame'],r['captionBounds'],r['materialPixels']) for r in records])
