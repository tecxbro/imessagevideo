from pathlib import Path
from PIL import Image
import json,numpy as np,math
R=Path(__file__).resolve().parents[1];D=R/'food-orbit-measure';s=json.loads((R/'food-orbit-proposals.json').read_text());observed=json.loads((D/'food-refined-measurements.json').read_text());errs=[];count=0
for actor in s['provenance']['roots']:
 if actor['kind'] not in ['pizza','ramen']:continue
 kind=actor['kind'];W,H=Image.open(R/'assets'/('apple-pizza.png' if kind=='pizza' else 'apple-ramen.png')).size
 for row in actor['measurements']:
  n=row['n']
  if n not in actor['observedFrames']:continue
  matches=[m for m in observed[str(n)] if m['kind']==kind];target=min(matches,key=lambda m:np.linalg.norm(np.array(m['center'])-[row['x'],row['y']]));M=np.array(target['matrix']);u,v=map(math.radians,[row['rotation'],row['innerRotation']]);rot=lambda x:np.array([[math.cos(x),-math.sin(x)],[math.sin(x),math.cos(x)]]);A=rot(u)@np.diag([row['scaleX'],row['scaleY']])@rot(v);t=np.array([row['x'],row['y']])-A@[W/2,H/2];reconstructed=np.column_stack([A,t]);points=np.array([[0,0,1],[W,0,1],[W,H,1],[0,H,1],[W/2,H/2,1]]).T;err=float(np.max(np.abs(reconstructed@points-M@points)));errs.append(err);count+=1
report=dict(observedAffinePosesChecked=count,maxProjectedPixelError=max(errs),meanProjectedPixelError=float(np.mean(errs)),notice='Independent numeric recomposition of native T(center) R(U) S(sigma) R(Vt) and centered original image against the measured source affine matrix. Source3D/light/texture error is separate.');(D/'affine-reconstruction-proof.json').write_text(json.dumps(report,indent=2));print(report)
if max(errs)>1e-6:raise SystemExit('Native affine reconstruction mismatch')
