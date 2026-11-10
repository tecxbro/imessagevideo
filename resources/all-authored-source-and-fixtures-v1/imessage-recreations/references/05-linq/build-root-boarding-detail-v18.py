from pathlib import Path
import json,copy,importlib.util,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
REF=Path(__file__).resolve().parent;ROOT=REF.parents[1];BASE=ROOT/'outputs/05-linq/final-v17/scene.json';OUT=REF/'assets/root-boarding-detail-v18';OUT.mkdir(exist_ok=True,parents=True)
spec=importlib.util.spec_from_file_location('pil',ROOT/'engines/render_pillow.py');pil=importlib.util.module_from_spec(spec);spec.loader.exec_module(pil)
s=json.load(open(BASE));g=next(n for n in s['layers'] if n['id']=='broad-v5-group-72');im=next(n for n in g['children'] if n['id']=='rich-asset-15');assert not im.get('keyframes',{}).get('opacity');assert not g.get('clip') and not im.get('clip');units=4;f=1204;t=f/30;gs=pil.state(g,t);q=pil.state(im,t);M=pil.matrix(gs)@pil.matrix(q);assert abs(M[0,1])+abs(M[1,0])<1e-9
old=Image.open(BASE.parent/im['src']).convert('RGBA');original=np.array(old.resize((old.width*units,old.height*units),Image.Resampling.LANCZOS));r=Image.open(ROOT/'verification/final/05-linq/peak1204-native/source.png').convert('RGB');native=Image.open(ROOT/'verification/final/05-linq/peak1204-native/native.png').convert('RGB');a=np.array(r,dtype=float);b=np.array(native,dtype=float);yy,xx=np.indices(a.shape[:2]);mask=np.zeros(a.shape[:2],bool)
# Only white/gray UI lettering/icon ink and the two actual panel-edge bands.
for rgb in [a,b]:
 hi=rgb.max(2);lo=rgb.min(2);neutral=hi-lo<60;mask|=((yy<345)&(lo>135)&neutral);mask|=((yy>395)&(xx>78)&(xx<870)&(hi<210)&(hi-lo<35))
mask=ndimage.binary_dilation(mask,iterations=7)
# Rounded white passenger panel and inset gray field: bounded edge material only.
for x0,y0,x1,y1,radius in [(53,365,901,1600,43),(94,578,858,1400,39)]:
 cx=np.clip(xx,x0+radius,x1-radius);cy=np.clip(yy,y0+radius,y1-radius);inside=((xx-cx)**2+(yy-cy)**2<=radius**2)&(xx>=x0)&(xx<=x1)&(yy>=y0)&(yy<=y1);edge=ndimage.binary_dilation(inside,iterations=5)^ndimage.binary_erosion(inside,iterations=5);mask|=edge
# Explicitly exclude all original device edge/hardware and non-screen material.
uvx=(xx-M[0,2])/M[0,0];uvy=(yy-M[1,2])/M[1,1];mask&=(uvx>13)&(uvx<259)&(uvy>90)&(uvy<320)&(yy>3)&(yy<716)
soft=ndimage.gaussian_filter(mask.astype(float),.8);maskImage=Image.fromarray(np.uint8(np.clip(soft,0,1)*255));maskImage.save(OUT/'source-ink-and-panel-mask.png')
coef=(M[0,0]/units,0,M[0,2],0,M[1,1]/units,M[1,2]);target=r.transform((old.width*units,old.height*units),Image.Transform.AFFINE,coef,resample=Image.Resampling.BICUBIC);weight=maskImage.transform(target.size,Image.Transform.AFFINE,coef,resample=Image.Resampling.BILINEAR);w=np.array(weight,dtype=float)[:,:,None]/255;new=original.copy();new[:,:,:3]=np.uint8(np.clip(np.array(target)*w+original[:,:,:3]*(1-w),0,255));file=OUT/'boarding-detail.png';Image.fromarray(new).save(file);assert np.array_equal(new[:,:,3],original[:,:,3])
track={k:[] for k in ['x','y','scaleX','scaleY','opacity']}
for n in range(1200,1221):
 p=pil.state(g,n/30);c=pil.state(im,n/30);assert not p.get('blur') and not p.get('shadow') and not c.get('blur') and not c.get('shadow');W=pil.matrix(p)@pil.matrix(c);assert abs(W[0,1])+abs(W[1,0])<1e-9;values=dict(x=float(W[0,2]),y=float(W[1,2]),scaleX=float(W[0,0]/units),scaleY=float(W[1,1]/units),opacity=p['opacity']*c['opacity'])
 for k,value in values.items():track[k].append(dict(t=n/30,value=value,ease='hold'))
layer=dict(id='root-boarding-detail-v18',type='image',src=str(file.resolve()),width=old.width*units,height=old.height*units,start=1200/30,end=1221/30,keyframes=track,semanticText='Original ATL to SFO boarding-pass UI material',authoringUnitsPerCanvasUnit=units,editability='One static genuine UI ink/panel-edge detail material. No complete frame or source-video layer. Native camera/geometry/opacity remain independent; internal UI pixels are bitmap.',provenance=dict(sourceNativeFrame=1204,oldAssetSHA256=hashlib.sha256((BASE.parent/im['src']).read_bytes()).hexdigest(),sourceMask=str((OUT/'source-ink-and-panel-mask.png').resolve()),sourceMaskPixels=int(mask.sum()),sourceMaskFraction=float(mask.mean()),alphaUnchanged=True,screenUVBounds=[13,90,259,320],nativeCameraFlattenedToWorldOnlyToPreserveRasterResolution=True))
patch=dict(scope=[[1200,1220]],layer=layer,gateOriginalId=im['id'],parentId=g['id']);(REF/'root-boarding-detail-v18-patch.json').write_text(json.dumps(patch,indent=2));print(layer['provenance'])
