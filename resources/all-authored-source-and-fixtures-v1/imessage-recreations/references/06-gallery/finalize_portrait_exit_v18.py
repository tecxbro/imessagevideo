"""Measured shared native background camera; phone/card remain independent."""
from pathlib import Path
import json,copy,shutil
P=Path(__file__).parent;B=P/'portrait-helper-v18';f=B/'camera-fit.json';data=json.load(open(f));original=json.load(open(P/'portrait-cameras-v18.json'));titles={r['frame']:r for r in json.load(open(P/'title-camera-v18.json'))};reference=683
if not (B/'camera-fit-before-exit-rig.json').exists():shutil.copyfile(f,B/'camera-fit-before-exit-rig.json')
base={id:next(r for r in rows if r['frame']==reference)for id,rows in data.items()};controls=[]
for frame in range(684,689):
 # The observed title/93 relation proves this center and scale through686.
 # At687/688 the incoming phone hides the reference; continue the measured
 # acceleration, with those inferred states explicitly identified in evidence.
 scale=titles[frame]['scale'] if frame in titles else {687:.340,688:.256}[frame];s=scale/titles[reference]['scale'];r93=next((r for r in original['rene-final11-group-93']if r['frame']==frame),None);opacity=r93['opacity']if frame<=686 else {687:.32,688:.15}[frame]
 control={'frame':frame,'scale':s,'origin':[960,540],'opacity':opacity,'camera_observed':frame<=686,'opacity_observed':frame<=686};controls.append(control)
 for id,rs in data.items():
  r=copy.deepcopy(base[id]);r.update(frame=frame,cx=960+(r['cx']-960)*s,cy=540+(r['cy']-540)*s,diameter=r['diameter']*s,opacity=opacity,blurFraction=max(r['blurFraction'],1/65 if frame>=685 else .5/65),mse=None,sharedNativeCamera=True)
  rs[:]=[x for x in rs if x['frame']!=frame];rs.append(r);rs.sort(key=lambda x:x['frame'])
f.write_text(json.dumps(data,indent=2)+'\n');(B/'exit-camera-rig.json').write_text(json.dumps({'reference_frame':reference,'proof':'Independent title scale .408/.516 predicts source93 center701.75,501.37 andD133.94, versus observed701.35,501.53,D133.29. Same native origin960,540; lower faces must not be fitted against the incoming phone.','controls':controls},indent=2)+'\n');print('Applied measured shared rig684–688')
