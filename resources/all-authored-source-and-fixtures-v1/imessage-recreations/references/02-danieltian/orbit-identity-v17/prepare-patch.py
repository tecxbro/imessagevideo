from pathlib import Path
import json,sys,numpy as np
from scipy.optimize import least_squares
from PIL import Image
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));from apply import signature,apply
s=json.load(open(HERE/'base-compact.json'));parents={p['id']:p for p in s['layers']};comps={r['frame']:r for r in json.load(open(HERE/'component-ledger.json'))};ell=json.load(open(HERE/'green-ellipse-ledger.json'));erows={r['frame']:r for r in ell['frames']};ops=[]
def actor(n,name):return next(c for c in parents[f'root-orbit-pose-{n}']['children'] if c['id'].endswith('middle-fly-'+name))
# Full-stage semantic magenta, same rule in source and native; not the old red-ring rule.
n=565;node=actor(n,'lyft');a=comps[n]['source'][0]['bounds'];b=comps[n]['native'][0]['bounds'];rx=(a[2]-a[0]-1)/(b[2]-b[0]-1);ry=(a[3]-a[1]-1)/(b[3]-b[1]-1)
pose=dict(x=a[0]-(b[0]-node['x'])*rx,y=a[1]-(b[1]-node['y'])*ry,scaleX=node['scaleX']*rx,scaleY=node['scaleY']*ry)
ops.append(dict(kind='update',frame=n,parent=f'root-orbit-pose-{n}',id=node['id'],oldSignature=signature(node),pose=pose,evidence=dict(sourceBounds=a,nativeBounds=b,clipped=False,reason='Old native detection confused Airbnb with Lyft and the source search ROI clipped the true target. Full-stage hue identity restores the actual measured glyph/body pose.')))
# Native contour calibration retains the original raster and its local alpha/edge sampling.
cal=actor(566,'green');native=erows[566]['native']
for n in range(560,566):
 row=erows[n];target=row.get('sourceCircleAlternative',row['source'])
 if n==560:
  # Only two exposed stage rows. Fix radius from the immediately following same-source near-circle;
  # fit just the visible cap center; do not claim an observed hidden full ellipse.
  a=np.array(Image.open(HERE/'source/000560.png')).astype(float);r,g,b=a.transpose(2,0,1);m=(g-r>40)&(g-b>20)&(g>150);yy,xx=np.where(m[:-1]);x=xx.astype(float)+.5;y=yy.astype(float)+.5;radius=erows[561]['sourceCircleAlternative']['rx'];res=least_squares(lambda v:np.hypot(x-v[0],y-v[1])-radius,[float(x.mean()),1078+radius],loss='soft_l1',f_scale=.4);target=dict(cx=float(res.x[0]),cy=float(res.x[1]),rx=radius,ry=radius,rms=float(np.sqrt(np.mean(res.fun**2))),model='Fixed same-source561 radius; only a2px censored cap is observed. Hidden geometry is a continuation model, not a full observed dimension.')
 if n<564:node=cal;ref=native;kind='add-clone'
 else:node=actor(n,'green');ref=row['native'];kind='update'
 rx=target['rx']/ref['rx'];ry=target['ry']/ref['ry'];pose=dict(x=target['cx']-(ref['cx']-node['x'])*rx,y=target['cy']-(ref['cy']-node['y'])*ry,scaleX=node['scaleX']*rx,scaleY=node['scaleY']*ry)
 op=dict(kind=kind,frame=n,parent=f'root-orbit-pose-{n}',id=f'root-orbit-{n}-middle-fly-green',pose=pose,evidence=dict(target={k:v for k,v in target.items() if k!='edgePoints'},nativeCalibration={k:v for k,v in ref.items() if k!='edgePoints'},reason='Actual source entry precedes missing actor560–563. Uncut exposed ellipse arc gives height independently of stage clipping;564/565 were falsely flattened from clipped visible height.'))
 if kind=='update':op['oldSignature']=signature(node)
 else:op.update(cloneParent='root-orbit-pose-566',cloneID=cal['id'],cloneSignature=signature(cal))
 ops.append(op)
spec=dict(baseScene='outputs/02-danieltian/final-v16/scene.json',baseSceneSHA256=s['helperBaseSHA256'],scope=[[560,565]],sourceFramesMeasured=[547,598],operations=ops,notice='Native editable actor transforms and existing genuine logo artwork only. All other actors, hardware/glass/caption/font/asset bytes remain unchanged. Green560 hidden radius is a documented continuation model supported by subsequent same-source circle contours.');(HERE/'patch-spec.json').write_text(json.dumps(spec,indent=2));out=apply(s);out['title']='ID-scoped orbit identity and censored-entry prototype';(HERE/'candidate-compact.json').write_text(json.dumps(out,indent=2));print({'operations':len(ops),'changedFrames':sorted(set(o['frame'] for o in ops)),'lyft565':ops[0]['pose'],'green560':ops[1]['pose']})
