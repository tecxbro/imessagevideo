from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy import optimize
R=Path(__file__).resolve().parent;ROOT=R.parents[2];OLD=R.parent/'orbit-identity-v17';s=json.load(open(OLD/'base-compact.json'));rows=[]
for n in range(553,588):
 node=next(v for v in json.load(open(R/'native-poses.json')) if v['frame']==n);cx=node['x']+235*node['scaleX']/2;cy=node['y']+236*node['scaleY']/2;rx=235*node['scaleX']/2;ry=236*node['scaleY']/2;row=dict(frame=n,declaredNativeImageBounds=[node['x'],node['y'],node['x']+2*rx,node['y']+2*ry])
 for kind,path in [('source',OLD/f'source/{n:06}.png'),('native',ROOT/f'outputs/02-danieltian/orbit-identity-v17/baseline-native16/{n:06}.png')]:
  a=np.array(Image.open(path).convert('RGB')).astype(float);g=a.mean(axis=2);chroma=a.max(axis=2)-a.min(axis=2);yy,xx=np.indices(g.shape);dist=np.hypot(xx+.5-cx,yy+.5-cy);m=(chroma<12)&(g<249)&(g>170)&(abs(dist-(rx+ry)/2)<42)&(xx>1)&(xx<1918)&(yy>1)&(yy<1078);y,x=np.where(m);x=x+.5;y=y+.5;weights=(253-g[m])/40;weights=np.clip(weights,.03,2)
  if len(x)<20:row[kind]=dict(status='insufficient-visible-contour',points=len(x));continue
  def residual(v):return (np.hypot(x-v[0],y-v[1])-v[2])*np.sqrt(weights)
  res=optimize.least_squares(residual,[cx,cy,(rx+ry)/2],loss='soft_l1',f_scale=.6);v=res.x;rad=np.hypot(x-v[0],y-v[1]);rms=float(np.sqrt(np.average((rad-v[2])**2,weights=weights)));cov=np.linalg.pinv(res.jac.T@res.jac)*np.mean(res.fun**2);q=dict(center=v[:2].tolist(),radius=float(v[2]),diameter=float(v[2]*2),parameterStd=np.sqrt(np.diag(cov)).tolist(),weightedRadialStd=rms,weightedPointCount=len(x),pointCloud=np.stack([x,y,weights],axis=-1).tolist(),method='Direct neutral-gray silhouette/stroke pixel cloud; excludes colorful M ink and stage border. Huber-weighted circle mid-stroke fit, not a full observed disk bbox. Radial spread includes stroke width and blur; not pure Gaussian sigma.');row[kind]=q;print(n,kind,{k:v for k,v in q.items() if k!='pointCloud'})
 rows.append(row)
(R/'circle-dense-553-587.json').write_text(json.dumps(dict(frames=rows,notice='Read-only measured direct silhouette controls; source565 left-censored,575 bottom-censored,585 fully visible. No camera or material mutation.'),indent=2))
