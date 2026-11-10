"""Analysis only: measure identity-specific app-plane trajectories from source features.
The output is pose measurements, never a source-frame playback asset.
"""
from pathlib import Path
import sys,json,cv2,numpy as np
p=Path(__file__).parent;sys.path.insert(0,str(p.parent.parent/'engines'))
from render_pillow import state
s=json.load(open(p.parent.parent/'outputs/03-photon-mini/final-v14/scene.json'))
cards=next(x for x in s['layers'] if x['id']=='measured-collage-v13')['children']
out=p/'collage-v15-measure';out.mkdir(exist_ok=True)
cv2.setNumThreads(1);sift=cv2.SIFT_create(nfeatures=18000,contrastThreshold=.025,edgeThreshold=15)
ref=cv2.imread(str(p/'collage-native/040.png'));ref=cv2.cvtColor(ref,cv2.COLOR_BGR2GRAY)
kp,des=sift.detectAndCompute(ref,None);rp=np.array([k.pt for k in kp],np.float32);queries=[]
for index,c in enumerate(cards):
 st=state(c,31);x,y=st['x'],st['y'];w,h=390*st['scaleX'],280*st['scaleY'];m=(rp[:,0]>max(0,x+5))&(rp[:,0]<min(1920,x+w-5))&(rp[:,1]>max(0,y+5))&(rp[:,1]<min(1080,y+h-5));indices=np.where(m)[0];queries.append((indices,des[indices],st));print('ref',index,len(indices),[x,y,w,h],flush=True)
matcher=None
records=json.loads((out/'source-feature-tracks.json').read_text()) if (out/'source-feature-tracks.json').exists() else []
done={r['frame'] for r in records}
for frame in range(903,975):
 if frame in done:continue
 target=cv2.imread(str(p/'collage-native'/f'{frame-890:03}.png'));target=cv2.cvtColor(target,cv2.COLOR_BGR2GRAY);tk,td=sift.detectAndCompute(target,None);tp=np.array([k.pt for k in tk],np.float32);row={'frame':frame,'cards':[]}
 if td is None:
  row['cards']=[{'index':i,'matches':0,'diagnosis':'No image features remain; source is blank at this frame.'} for i in range(20)];records.append(row);(out/'source-feature-tracks.json').write_text(json.dumps(records,indent=2));continue
 matcher=cv2.FlannBasedMatcher(dict(algorithm=1,trees=5),dict(checks=80));matcher.add([td]);matcher.train()
 for index,(indices,qd,st) in enumerate(queries):
  pairs=matcher.knnMatch(qd,k=2);good=[a for a,b in pairs if a.distance<.7*b.distance];record={'index':index,'matches':len(good),'base':{k:st[k] for k in ('x','y','scaleX','scaleY')}}
  if len(good)>=5:
   a=np.array([rp[indices[m.queryIdx]] for m in good],np.float32);b=np.array([tp[m.trainIdx] for m in good],np.float32)
   A,mask=cv2.estimateAffine2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=4000,confidence=.995,refineIters=10)
   H,hm=cv2.findHomography(a,b,cv2.RANSAC,3,maxIters=4000,confidence=.995)
   if A is not None:
    mask=mask.ravel().astype(bool);errors=np.linalg.norm(a@A[:,:2].T+A[:,2]-b,axis=1)
    record.update(affine=A.tolist(),inliers=int(mask.sum()),affineRms=float(np.sqrt(np.mean(errors[mask]**2))),pointsFrom=a[mask].tolist(),pointsTo=b[mask].tolist())
   if H is not None:record.update(homography=H.tolist(),homographyInliers=int(hm.sum()))
  row['cards'].append(record)
 records.append(row)
 if frame%5==0:print('frame',frame,[(r['index'],r.get('inliers',0)) for r in row['cards']],flush=True)
 (out/'source-feature-tracks.json').write_text(json.dumps(records,indent=2))
print('complete',len(records))
