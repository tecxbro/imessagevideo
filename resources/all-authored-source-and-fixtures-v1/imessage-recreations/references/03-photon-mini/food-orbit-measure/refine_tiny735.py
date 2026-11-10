from pathlib import Path
import sys,json,copy,math
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from scipy.optimize import differential_evolution, minimize
R=Path(__file__).resolve().parents[1];D=R/'food-orbit-measure';asset=cv2.imread(str(R/'assets/apple-pizza.png'),-1).astype(float);source=cv2.imread(str(R/'lunch-native/126.png')).astype(float);x0,y0=1242,100;target=source[y0:140,x0:1280];alpha=asset[:,:,3:]/255;premult=np.concatenate([(253-asset[:,:,:3])*alpha,alpha],2);base=json.loads((D/'verified-tiny-food-states.json').read_text())[-2];original=np.array(base['matrix']);best={}
def matrix(v):
 sx,sy,rot,tx,ty,a=v;c,s=math.cos(rot),math.sin(rot);return np.array([[sx*c,-sy*s,tx],[sx*s,sy*c,ty]])
def loss(v):
 M=matrix(v);M[:,2]-=[x0,y0];warp=cv2.warpAffine(premult,M,(38,40),flags=cv2.INTER_LINEAR);pred=253-warp[:,:,:3]*v[-1];return np.mean(np.abs(pred-target))
bounds=[(.065,.135),(.085,.15),(-.3,.3),(1249,1256),(109,115),(.75,1)]
fit=differential_evolution(loss,bounds,tol=.002,popsize=12,maxiter=100,seed=735,workers=1,polish=False);v=fit.x;M=matrix(v);report=dict(frame=735,previous=base,parameters=v.tolist(),matrix=M.tolist(),fitMAE=fit.fun,opacity=float(v[-1]),method='Measured bounded native tiny pose after fixed full-art bounds produced a pale misplaced glyph. Fit opacity/scale/rotation/translation against isolated white source ROI. No scene/image playback.')
(D/'tiny735-refined.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
spec=json.loads((R/'food-orbit-proposals.json').read_text());id='authentic-food-pizza-tiny-right';node=spec['replacements'][id];U,sv,V=np.linalg.svd(M[:,:2]);
if np.linalg.det(U)<0:U[:,1]*=-1;sv[1]*=-1
if np.linalg.det(V)<0:V[1,:]*=-1;sv[1]*=-1
W,H=asset.shape[1],asset.shape[0];center=M@np.array([W/2,H/2,1]);row=dict(n=735,x=float(center[0]),y=float(center[1]),rotation=math.degrees(math.atan2(U[1,0],U[0,0])),innerRotation=math.degrees(math.atan2(V[1,0],V[0,0])),scaleX=float(sv[0]),scaleY=float(sv[1]),opacity=float(v[-1]))
for k in ['x','y','rotation','scaleX','scaleY','opacity']:
 for q in node['keyframes'][k]:
  if abs(q['t']-735/30)<1e-9:q['value']=row[k]
for q in node['children'][0]['keyframes']['rotation']:
 if abs(q['t']-735/30)<1e-9:q['value']=row['innerRotation']
for root in spec['provenance']['roots']:
 if root['id']==id:
  for q in root['measurements']:
   if q['n']==735:q.update(row)
(R/'food-orbit-proposals.json').write_text(json.dumps(spec,indent=2));raw=json.loads((D/'food-refined-measurements.json').read_text());raw['735']=[m for m in raw['735'] if m.get('verifiedTinySourceBounds')!=base['sourceBounds']];corn=cv2.transform(np.float32([[[0,0],[W,0],[W,H],[0,H]]]),M)[0];raw['735'].append(dict(kind='pizza',matrix=M.tolist(),center=center.tolist(),corners=corn.tolist(),opacity=float(v[-1]),inliers=0,fitMAE=float(fit.fun),verifiedTinySourceBounds=base['sourceBounds'],manualRefinement=True));(D/'food-refined-measurements.json').write_text(json.dumps(raw,indent=2));scene=json.loads((R/'food-orbit-prototype-v2.scene.json').read_text());scene['layers']=[copy.deepcopy(spec['replacements'].get(n['id'],n)) for n in scene['layers']];(R/'food-orbit-prototype-v3.scene.json').write_text(json.dumps(scene,indent=2))
