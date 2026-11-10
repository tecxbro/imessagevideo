from pathlib import Path
import json,sys,numpy as np
from scipy.optimize import least_squares
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/muse-attribution-v17';sys.path.insert(0,str(R));from apply import signature,apply
base=json.load(open(R.parent/'orbit-identity-v17/candidate-compact.json'));rows=json.load(open(R/'circle-dense-553-587.json'))['frames'];native={x['frame']:x for x in json.load(open(R/'native-poses.json'))};parents={p['id']:p for p in base['layers']};ops=[]
for row in rows:
 n=row['frame'];parent=parents[f'root-orbit-pose-{n}'];node=next(c for c in parent['children'] if c['id'].endswith('middle-fly-muse'));properties=dict(clip=dict(width=235,height=236,radius=117.5));notes=[];target=row['source'];ref=row['native'];pose=native[n]
 if n==553:properties['opacity']=0;notes.append('Source ROI0:400×0:160 is exactlyRGB253, all64000pixels; native already draws circle+pink crop corner. True first visible source cap is554. No extrapolation to552.')
 else:
  if n==554:
   # The short cap cannot uniquely determine all three circle parameters.
   # Radius is supported by the immediate same-source555 continuation.
   fixed=next(x for x in rows if x['frame']==555)['source']['radius'];pts=np.array(target['pointCloud']);x,y,w=pts.T;res=least_squares(lambda v:(np.hypot(x-v[0],y-v[1])-fixed)*np.sqrt(w),[target['center'][0],target['center'][1]+target['radius']-fixed],loss='soft_l1',f_scale=.6);target=dict(center=res.x.tolist(),radius=fixed,model='554shortcap: radius continuation from same-source555, not a fully observed disk. Free radius fit has6.7px uncertainty and is rejected.',weightedPointCount=len(x));properties['opacity']=1;notes.append('Source554 border reachesRGB214, same as555; it is opaque and at a different pose, not a held .666 fade. Colored glyph is still offstage.')
  assert ref.get('radius') and target.get('radius');ratio=target['radius']/ref['radius'];assert .85<ratio<1.15
  delta=np.linalg.norm(np.array(target['center'])-ref['center']);dd=abs(2*(target['radius']-ref['radius']))
  if n==554 or delta>1 or dd>1:
   properties.update(x=target['center'][0]-(ref['center'][0]-pose['x'])*ratio,y=target['center'][1]-(ref['center'][1]-pose['y'])*ratio,scaleX=pose['scaleX']*ratio,scaleY=pose['scaleY']*ratio)
  else:notes.append('Already aligned within1px center/diameter; retain actual camera, add only true component circle clip.')
 op=dict(frame=n,parent=parent['id'],id=node['id'],oldSignature=signature(node),properties=properties,evidence=dict(target={k:v for k,v in target.items() if k!='pointCloud'},native={k:v for k,v in ref.items() if k!='pointCloud'},notes=notes,clipReason='Original source585rectangular artwork contains neighboring pink Airbnb pixels in its outer corner. The true Muse component is circular. Preserve original genuine M/body artwork but remove non-Muse exterior, matching the already accepted588+ clipping.'))
 ops.append(op)
spec=dict(baseScene='outputs/02-danieltian/final-v16/scene.json',baseSHA256='6cc308bf03330758ec17cc97ece6054e74da42694310c463aae029f77758dcfa',acceptedOtherHelper='references/02-danieltian/orbit-identity-v17/release.json',scope=[[553,587]],operations=ops,notice='Independent Muse actor/crop/lifecycle correction only. No source video, frame or new artwork. Preserve accepted green/Lyft helper, every other actor, header/glass and global metadata. Source-gray stroke spread is not treated as a Gaussian blur prescription.');(R/'patch-spec.json').write_text(json.dumps(spec,indent=2));candidate=apply(base);candidate['title']='Independent measured Muse component prototype over accepted green/Lyft helper';(R/'candidate-compact.json').write_text(json.dumps(candidate,indent=2));print('ops',len(ops),'554',ops[1]['properties'])
