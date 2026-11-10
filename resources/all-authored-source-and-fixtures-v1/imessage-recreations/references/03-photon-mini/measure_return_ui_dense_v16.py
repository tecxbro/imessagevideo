"""Measure only independent MessagesUI photo plane; physical/worldfood are untouched."""
from measure_lunch_refinement_v16 import *
ui=root('measured-lunch-ui-v13');sift=cv2.SIFT_create(nfeatures=2500,contrastThreshold=.006,edgeThreshold=12)
node,_=find(ui,'lunch13-food-preview-original-interior-v4',750)
a=np.array(Image.open(node['src']).convert('RGBA'));h,w=a.shape[:2];alpha=a[:,:,3]/255;rgb=np.uint8(a[:,:,:3]*alpha[:,:,None]+253*(1-alpha[:,:,None]))
kp,desc=sift.detectAndCompute(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),np.uint8(alpha>.8)*255)
data=json.loads((P/'return-camera-v16-measurements.json').read_text());existing={r['frame']:r for r in data['frames']};rows=[]
for f in range(735,800):
 if f<=744:
  rows.append(existing[f]);continue
 im=source(f);roi=im[:,700:1230];target,d2=sift.detectAndCompute(cv2.cvtColor(roi,cv2.COLOR_RGB2GRAY),None)
 good=[a for a,b in cv2.BFMatcher().knnMatch(desc,d2,k=2) if a.distance<.70*b.distance]
 left=np.float32([kp[m.queryIdx].pt for m in good]);right=np.float32([target[m.trainIdx].pt for m in good]);right[:,0]+=700
 A,inside=cv2.estimateAffine2D(left,right,method=cv2.RANSAC,ransacReprojThreshold=1.1,maxIters=5000,confidence=.999)
 keep=inside[:,0]>0;pred=cv2.transform(left[None],A)[0];rms=float(np.sqrt(np.mean(np.sum((pred[keep]-right[keep])**2,axis=1))))
 node,current=find(ui,node['id'],f);current=current@np.diag([node['width']/w,node['height']/h,1])
 measured=np.vstack([A,[0,0,1]])@np.linalg.inv(current)@matrix(ui,f)
 inliers=int(keep.sum());span=np.ptp(left[keep],axis=0)
 if inliers<40 or rms>.6 or min(span)<150:raise ValueError(('unobserved',f,inliers,rms,span))
 row=dict(frame=f,inliers=inliers,rms=rms,reference_span=span.tolist(),ui_matrix=measured.tolist(),scrim_alpha=0,notice='UI-only update. Original physical device/bezel cameras remain untouched after744. Strong original static-photo features validate this independently from the outer hardware.')
 rows.append(row)
 if f%10==0:print(f,inliers,rms,flush=True)
data.update(frames=rows,notice='Full735–799 UI return phase has direct original-photo SIFT support, not interpolated hardware inference. Physical aperture/width correction remains735–744 only; all independently owned world food/Order actors remain fixed.')
(P/'return-camera-v16-dense-measurements.json').write_text(json.dumps(data,indent=2))
print('All65UIposes measured')
