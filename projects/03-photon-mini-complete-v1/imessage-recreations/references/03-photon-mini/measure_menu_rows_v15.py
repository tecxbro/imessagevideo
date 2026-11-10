"""Measure six static rich-app UI row planes against source-native frames."""
from pathlib import Path
import sys,json,time,math
import numpy as np
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent;D=P/'menu-rows-v15';cv2.setNumThreads(1);cv2.setRNGSeed(57041);scene=json.loads((P/'final-v14.scene.json').read_text());assets=json.loads((D/'assets.json').read_text())['rows'];clip=next(x for x in scene['layers'] if x['id']=='measured-menu-clip-v13');menu=clip['children'][0];body=next(x for x in menu['children'] if x['id']=='menu13-p03-202');rows=body['children'];sift=cv2.SIFT_create(nfeatures=3000,contrastThreshold=.008,edgeThreshold=12)
def matrix(l,f):
 t=f/30;st={k:l.get(k,v) for k,v in {'x':0,'y':0,'scaleX':1,'scaleY':1,'rotation':0,'originX':0,'originY':0}.items()}
 for k in st:
  if k in l.get('keyframes',{}):st[k]=sample(l['keyframes'][k],t)
 x,y,sx,sy,r,ox,oy=[st[k] for k in ['x','y','scaleX','scaleY','rotation','originX','originY']];r=math.radians(r);R=np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]]);A=R@np.diag([sx,sy]);out=np.eye(3);out[:2,:2]=A;out[:2,2]=[x+ox,y+oy]-A@[ox,oy];return out
def photo(i,f):
 row=rows[i];im=next(x for x in row['children'] if x['type']=='image');M=np.eye(3)
 for l in [clip,menu,body,row,im]:M=M@matrix(l,f)
 return M@np.array([im['width']/2,im['height']/2,1]),M
for r in assets:
 rgba=cv2.imread(r['asset'],cv2.IMREAD_UNCHANGED);alpha=rgba[:,:,3]/255;rgb=rgba[:,:,:3].astype('float32')*alpha[:,:,None]+253*(1-alpha[:,:,None]);gray=cv2.cvtColor(rgb.astype('uint8'),cv2.COLOR_BGR2GRAY);kp,desc=sift.detectAndCompute(gray,np.uint8(alpha>0)*255);r.update(rgba=rgba,rgb=rgb,kp=kp,desc=desc);ref,_=photo(r['row'],r['source_frame']);r['reference_photo_point']=np.array([ref[0]-r['source_crop'][0],ref[1]-r['source_crop'][1],1.0])
records=[];birth=[624,627,630,633,636,639];started=time.time()
for f in range(618,730):
 source=cv2.imread(str(P/'lunch-native'/f'{f-609:03}.png'));roi=source[:,560:1360];ks,ds=sift.detectAndCompute(cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY),None);matcher=cv2.FlannBasedMatcher(dict(algorithm=1,trees=4),dict(checks=64));
 if ds is not None:matcher.add([ds]);matcher.train()
 frame={'frame':f,'rows':[]}
 for r in assets:
  i=r['row'];expected,expectedM=photo(i,f);q={'row':i,'expected_photo_center':[float(expected[0]),float(expected[1])],'status':'not_observed','cause':'No validated source feature model'}
  if f<birth[i]:q['status']='prebirth';q['cause']='Native source row staggering';frame['rows'].append(q);continue
  if expected[1]-140>1080 or expected[1]+140<0:q['status']='offstage';q['cause']='Entire semantic row beyond viewport under measured prior';frame['rows'].append(q);continue
  if ds is None or r['desc'] is None:frame['rows'].append(q);continue
  pairs=matcher.knnMatch(r['desc'],k=2);good=[a for a,b in pairs if a.distance<.72*b.distance];q['ratio_matches']=len(good)
  if len(good)>=8:
   a=np.float32([r['kp'][m.queryIdx].pt for m in good]);b=np.float32([ks[m.trainIdx].pt for m in good]);b[:,0]+=560;M,inside=cv2.estimateAffine2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=1.2,maxIters=5000,confidence=.999)
   if M is not None:
    keep=inside[:,0]>0;n=int(keep.sum());pred=cv2.transform(a[None,:,:],M)[0];err=float(np.sqrt(np.mean(np.sum((pred[keep]-b[keep])**2,axis=1))));H,W=r['rgba'].shape[:2];corners=cv2.transform(np.float32([[[0,0],[W,0],[W,H],[0,H]]]),M)[0];sv=np.linalg.svd(M[:,:2],compute_uv=False);point=M@r['reference_photo_point'];distance=float(np.linalg.norm(point-expected[:2]));span=np.ptp(a[keep],axis=0);valid=n>=12 and err<1.2 and .2<min(sv)<max(sv)<2.5 and np.linalg.det(M[:,:2])>0 and distance<100 and span[0]>60
    q.update(inliers=n,inlier_RMS=err,measured_photo_center=point.tolist(),semantic_anchor_distance=distance,inlier_span=span.tolist(),candidate_matrix=M.tolist(),candidate_bounds=[float(corners[:,0].min()),float(corners[:,1].min()),float(corners[:,0].max()),float(corners[:,1].max())])
    if valid:
     alpha=r['rgba'][:,:,3].astype('float32')/255;warp=cv2.warpAffine(r['rgb'],M,(1920,1080),flags=cv2.INTER_LINEAR,borderValue=(253,253,253));wa=cv2.warpAffine(alpha,M,(1920,1080));m=(wa>.99)&(np.linalg.norm(warp-253,axis=2)>35);v=(warp-253)[m];z=(source.astype('float32')-253)[m];ratios=np.sum(v*z,axis=1)/np.maximum(1,np.sum(v*v,axis=1));gain=float(np.clip(np.median(ratios),0,1));error=float(np.median(np.mean(abs(253+gain*v-(253+z)),axis=1)));q.update(status='measured',cause='Validated independent original row UI feature plane',matrix=M.tolist(),corners=corners.tolist(),opacity=gain,median_photometric_error=error,visible_ink_pixels=int(m.sum()))
  frame['rows'].append(q)
 records.append(frame)
 if (f-618)%12==0:(D/'measurements-progress.json').write_text(json.dumps({'frames':records,'elapsed':time.time()-started},indent=2))
result={'source':'../source.mp4','baseline':'../final-v14.scene.json','scope':[618,729],'static_assets':'assets.json','notice':'All transforms measured from six static separately bounded row UI artworks; no target frame or video is a runtime asset. Semantic photo anchor rejects cross-row/background matches. Bitmap row internals are disclosed. Missing/partial models require explicit fallback diagnosis before scene construction.','frames':records,'elapsed':time.time()-started};(D/'measurements.json').write_text(json.dumps(result,indent=2));print('seconds',result['elapsed']);print({str(i):sum(q['status']=='measured' for f in records for q in f['rows'] if q['row']==i) for i in range(6)})
