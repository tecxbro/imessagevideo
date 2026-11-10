from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy import ndimage,optimize
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/muse-attribution-v17';old=R.parent/'orbit-identity-v17';s=json.load(open(R/'candidate-compact.json'));rows=[]
for n in [565,575]:
 parent=next(x for x in s['layers'] if x['id']==f'root-orbit-pose-{n}');node=next(x for x in parent['children'] if x['id'].endswith('middle-fly-muse'));cx=node['x']+235*node['scaleX']/2;cy=node['y']+236*node['scaleY']/2;radius=(235*node['scaleX']+236*node['scaleY'])/4;arrays={};fits={};yy,xx=np.indices((1080,1920));roi=(abs(xx-cx)<radius+12)&(abs(yy-cy)<radius+12)
 for kind,path in [('source',old/f'source/{n:06}.png'),('candidate',O/'prototype-01'/f'{n/30:.3f}.png')]:
  a=np.array(Image.open(path).convert('RGB')).astype(float);arrays[kind]=a;g=a.mean(2);chroma=a.max(2)-a.min(2);m=(chroma<12)&(g<249)&(g>170)&(abs(np.hypot(xx+.5-cx,yy+.5-cy)-radius)<30)&(xx>1)&(xx<1918)&(yy>1)&(yy<1078);y,x=np.where(m);x=x+.5;y=y+.5;w=np.clip((253-g[m])/40,.03,2);res=optimize.least_squares(lambda v:(np.hypot(x-v[0],y-v[1])-v[2])*np.sqrt(w),[cx,cy,radius],loss='soft_l1',f_scale=.6);v=res.x;spread=float(np.sqrt(np.average((np.hypot(x-v[0],y-v[1])-v[2])**2,weights=w)));blue=(a[:,:,2]-a[:,:,0]>60)&(a[:,:,2]-a[:,:,1]>20)&(a[:,:,0]<150)&roi;y2,x2=np.where(blue);fits[kind]=dict(center=v[:2].tolist(),diameter=float(2*v[2]),radialStrokeSpread=spread,blueInkBounds=[int(x2.min()),int(y2.min()),int(x2.max()+1),int(y2.max()+1)],bluePixels=int(blue.sum()))
 a,b=arrays.values();d=abs(a-b);v=fits['source'];cx,cy=v['center'];r=v['diameter']/2;ring=(abs(np.hypot(xx+.5-cx,yy+.5-cy)-r)<10)&roi;blue=np.zeros((1080,1920),bool)
 for img in arrays.values():blue|=(img[:,:,2]-img[:,:,0]>40)&(img[:,:,2]-img[:,:,1]>10)&(img[:,:,0]<180)&roi
 blue=ndimage.binary_dilation(blue,iterations=3)&roi;ring&=~blue;inside=roi&~(ring|blue);regions=[]
 for name,m in [('blueGlyphAnd3pxEdges',blue),('grayCircleAnd10pxEdges',ring),('otherInsideMuseImage',inside),('allOutsideMuseROI',~roi)]:regions.append(dict(name=name,pixels=int(m.sum()),regionMAE=float(d[m].mean()) if m.any() else 0,globalMAEContribution=float(d[m].sum()/d.size),share=float(d[m].sum()/d.sum())))
 rows.append(dict(frame=n,globalMAE=float(d.mean()),fits=fits,regions=regions));print(n,'fits',fits,'regions',[(q['name'],round(q['share']*100,1)) for q in regions])
(O/'post-pose-attribution.json').write_text(json.dumps(dict(frames=rows,notice='Actual accepted-prototype native pixels, no capture interpolation. Gray mid-stroke spread includes width, faint shadow and blur, so it is not used as a blur filter prescription. Both circle cameras now align; remaining local ink/material error is reported without a pixel-identity claim.'),indent=2))
