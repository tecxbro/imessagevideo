"""Robust per-frame coherent grid camera/aspect from original/native controls."""
from pathlib import Path
from itertools import combinations
import numpy as np,json
p=Path(__file__).parent
raw=json.loads((p/'measurements-v8/grid-held-1169-1214-v18-parent.json').read_text())
points=np.array([[0,0],[225,0],[0,225],[225,225],[112.5,112.5]],float)
output=[]
for frame in raw['records']:
 inputs=[];targets=[];weights=[];anchors=[]
 for row in frame['records']:
  a=row['measurements']['source'];b=row['measurements']['candidate'];x,y,scale=row['declared']
  declared=np.array([[scale,0,x],[0,scale,y]])
  corrected=np.array(a['matrix'])+declared-np.array(b['matrix'])
  inputs.extend(points@declared[:,:2].T+declared[:,2]);targets.extend(points@corrected[:,:2].T+corrected[:,2])
  weight=1/(.15+a['rms']**2+b['rms']**2);weights.extend([weight]*5)
  anchors.append(dict(id=row['id'],weight=weight,declared=declared.tolist(),control_corrected_source=corrected.tolist()))
 inputs=np.array(inputs);targets=np.array(targets);weights=np.sqrt(np.array(weights))
 def fit(ids):
  selected=np.repeat([i in ids for i in range(6)],5);params=[];prediction=np.zeros_like(targets)
  for k in [0,1]:
   design=np.column_stack([inputs[:,k],np.ones(len(inputs))]);coef=np.linalg.lstsq(design[selected]*weights[selected,None],targets[selected,k]*weights[selected],rcond=None)[0];params.append(coef);prediction[:,k]=design@coef
  residual=np.sqrt(((prediction-targets)**2).sum(1));per=np.sqrt((residual.reshape(6,5)**2).mean(1))
  return params,residual,per
 trials=[]
 for ids in combinations(range(6),4):
  params,residual,per=fit(ids);accepted=tuple(int(i)for i in np.where(per<1.)[0]);score=(-len(accepted),float(np.minimum(per,1.) .sum()))
  trials.append((score,accepted if len(accepted)>=4 else ids))
 _,accepted=min(trials,key=lambda x:x[0])
 for iteration in range(3):
  params,residual,per=fit(accepted);new=tuple(int(i)for i in np.where(per<1.)[0])
  if len(new)<4 or new==accepted:break
  accepted=new
 params,residual,per=fit(accepted);(ax,bx),(ay,by)=params
 maximum_shift=float(np.abs(np.array([[0,0],[1440,1080]])*np.array([ax-1,ay-1])+[bx,by]).max());snap=bool(maximum_shift<.1)
 if snap:ax=ay=1.;bx=by=0.
 for i,a in enumerate(anchors):a.update(accepted_coherent_anchor=i in accepted,coherent_camera_RMS=float(per[i]))
 output.append(dict(frame=frame['frame'],time=frame['frame']*1001/30000,ax=float(ax),ay=float(ay),bx=float(bx),by=float(by),snapped_identity_within_point1px_uncertainty=snap,fit_RMS=float(np.sqrt((residual**2).mean())),inlier_RMS=float(np.sqrt((residual.reshape(6,5)[list(accepted)]**2).mean())),fit_max_residual=float(residual.max()),accepted_anchor_ids=[anchors[i]['id']for i in accepted],anchors=anchors))
result=dict(method='Independent coherent diagonal affine/aspect per exact native frame. Six source genuine-art SIFT matrices are corrected by actual candidate controlbias. Four-corner+center correspondences use 1/(.15+sourceRMS²+controlRMS²) weights. Exhaustive4-anchor consensus,1nativepx per-anchor RMS threshold and up to3refits reject a registration that cannot share the coherent camera. Original raw matrices and all rejected anchor residuals remain. Sub.1pxstage corrections snap to identity. No constant camera, branding asset replacement or guessed row offsets. Full interval native validation follows.',measurements=output)
(p/'measurements-v8/grid-camera-v18.json').write_text(json.dumps(result,indent=2))
print([(r['frame'],[round(r[k],6)for k in ['ax','ay','bx','by']],round(r['inlier_RMS'],3),r['accepted_anchor_ids'],r['snapped_identity_within_point1px_uncertainty'])for r in output if r['frame']in [1169,1173,1180,1190,1200,1214]])
