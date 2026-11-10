"""Dense measured affine registration of genuine static mail artwork only."""
from pathlib import Path
import sys,json,copy,math
import cv2,numpy as np
from PIL import Image
p=Path(__file__).parent;root=p.parents[1];sys.path.insert(0,str(root/'engines'));from render_pillow import state
srcPath=root/'outputs/01-photonhq/final-v8/scene.json';scene=json.load(open(srcPath));cards=[n for n in scene['layers'] if n['id'].startswith('early-wall-native-v7-mail-') and n['type']=='image'];cache={};cv2.setNumThreads(1)
for n in cards:
 im=Image.open(srcPath.parent/n['src']).convert('RGBA');base=Image.new('RGBA',im.size,(255,255,255,255));base.alpha_composite(im);a=np.array(base.convert('RGB').resize((n['width'],n['height']),Image.Resampling.LANCZOS));cache[n['id']]=a
poses=[];diagnosis=[]
for frame in list(range(297,300))+list(range(301,315)):
 source=np.array(Image.open(p/'early-walls-v7-measure'/f'frame-{frame-263:03}.png').convert('RGB'));records=[]
 for n in cards:
  s=state(n,frame/30)
  if not(s.get('start',0)<=frame/30<s.get('end',scene['duration']) and s['opacity']>0):continue
  a=cache[n['id']];h,w=a.shape[:2];X,Y=np.meshgrid(np.arange(w,dtype='float32'),np.arange(h,dtype='float32'));mx=s['x']+X*s['scaleX'];my=s['y']+Y*s['scaleY'];valid=(mx>2)&(mx<1917)&(my>2)&(my<1077);b=cv2.remap(source,mx.astype('float32'),my.astype('float32'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(255,255,255));before=float(np.abs(a.astype(float)-b.astype(float))[valid].mean()) if valid.any() else 0;r={'id':n['id'],'frame':frame,'beforeLocalMae':before,'accepted':False}
  if valid.mean()<.15:r['reason']='Insufficient visible source support';records.append(r);continue
  W=np.eye(2,3,dtype='float32')
  try:
   score,W=cv2.findTransformECC(cv2.cvtColor(a,cv2.COLOR_RGB2GRAY).astype('float32')/255,cv2.cvtColor(b,cv2.COLOR_RGB2GRAY).astype('float32')/255,W,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,100,1e-6),valid.astype('uint8')*255,3)
  except cv2.error:r['reason']='Affine registration did not converge';records.append(r);continue
  singular=np.linalg.svd(W[:,:2],compute_uv=False);reasonable=score>=.86 and np.linalg.det(W[:,:2])>0 and min(singular)>.85 and max(singular)<1.15 and max(abs(W[0,2]),abs(W[1,2]))<12 and max(abs(W[0,1]),abs(W[1,0]))<.08
  if not reasonable:r.update(reason='Weak support or transform outside measured near-camera bounds',ecc=float(score),matrix=W.tolist());records.append(r);continue
  warped=cv2.warpAffine(a,W,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(255,255,255));after=float(np.abs(warped.astype(float)-b.astype(float))[valid].mean());axis=W.copy();axis[0,1]=0;axis[1,0]=0;simple=cv2.warpAffine(a,axis,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(255,255,255));axisAfter=float(np.abs(simple.astype(float)-b.astype(float))[valid].mean());mode='affine'
  if axisAfter<=after+.05 and abs(W[0,1])*h+abs(W[1,0])*w<.25:W=axis;after=axisAfter;mode='axis-affine'
  if after>=before-.2:r.update(reason='No meaningful forward-projection improvement',ecc=float(score),afterLocalMae=after,matrix=W.tolist());records.append(r);continue
  M=np.diag([s['scaleX'],s['scaleY']])@W[:,:2];origin=np.array([s['x'],s['y']])+np.diag([s['scaleX'],s['scaleY']])@W[:,2]
  pose={'originalId':n['id'],'frame':frame,'matrixWorld':M.tolist(),'originWorld':origin.tolist(),'mode':mode,'baselineWidth':w,'baselineHeight':h,'measuredLocalMatrix':W.tolist(),'ecc':float(score),'beforeLocalMae':before,'afterLocalMae':after};poses.append(pose);r.update(accepted=True,mode=mode,ecc=float(score),afterLocalMae=after,matrix=W.tolist());records.append(r)
 diagnosis.append({'frame':frame,'cards':records});tmp=p/'v9-repair/mail-spec-working.json.tmp';tmp.write_text(json.dumps({'baseline':str(srcPath),'scope':[[297,299],[301,314]],'preservedFrame':300,'poses':poses,'diagnosis':diagnosis},indent=2)+'\n');tmp.replace(p/'v9-repair/mail-spec-working.json');print(frame,'accepted',sum(r['accepted'] for r in records),'of',len(records),flush=True)
print('complete',len(poses),flush=True)
