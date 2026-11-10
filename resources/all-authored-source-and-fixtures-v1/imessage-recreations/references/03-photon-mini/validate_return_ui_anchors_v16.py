"""Read-only UI anchors validate the return camera independently of a noisy rim."""
from pathlib import Path
import sys,json,math
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent
cv2.setNumThreads(1);cv2.setRNGSeed(73816)
scene=json.loads((P/'final-v15.scene.json').read_text())
root=next(n for n in scene['layers'] if n['id']=='measured-lunch-ui-v13')
frame=738
source=np.array(Image.open(P/'lunch-native/129.png').convert('RGB'))
candidate=np.array(Image.open(P.parent.parent/'outputs/03-photon-mini/frames-gsap/000738.png').convert('RGB'))

def state(n,k,d):return sample(n.get('keyframes',{}).get(k,[dict(t=0,value=n.get(k,d))]),frame/30)
def matrix(n):
    x,y,sx,sy,angle,ox,oy=[state(n,k,d) for k,d in [('x',0),('y',0),('scaleX',1),('scaleY',1),('rotation',0),('originX',0),('originY',0)]]
    theta=math.radians(angle);R=np.array([[math.cos(theta)*sx,-math.sin(theta)*sy,0],[math.sin(theta)*sx,math.cos(theta)*sy,0],[0,0,1]],float)
    T=np.eye(3);T[:2,2]=[x+ox,y+oy];U=np.eye(3);U[:2,2]=[-ox,-oy]
    return T@R@U

def find(n,identifier,parent):
    M=parent@matrix(n)
    if n['id']==identifier:return n,M
    for child in n.get('children',[]):
        result=find(child,identifier,M)
        if result:return result
    return None

node,current=find(root,'lunch13-food-preview-original-interior-v4',np.eye(3))
asset=np.array(Image.open(node['src']).convert('RGBA'))
height,width=asset.shape[:2];alpha=asset[:,:,3].astype(float)/255
rgb=np.uint8(asset[:,:,:3]*alpha[:,:,None]+253*(1-alpha[:,:,None]))
pixel=np.diag([node['width']/width,node['height']/height,1.])
current=current@pixel
sift=cv2.SIFT_create(nfeatures=3000,contrastThreshold=.006,edgeThreshold=12)
kp,desc=sift.detectAndCompute(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),np.uint8(alpha>.8)*255)
target_points,target_desc=sift.detectAndCompute(cv2.cvtColor(source,cv2.COLOR_RGB2GRAY),None)
pairs=cv2.BFMatcher().knnMatch(desc,target_desc,k=2)
good=[a for a,b in pairs if a.distance<.70*b.distance]
left=np.float32([kp[m.queryIdx].pt for m in good]);right=np.float32([target_points[m.trainIdx].pt for m in good])
affine,inside=cv2.estimateAffine2D(left,right,method=cv2.RANSAC,ransacReprojThreshold=1.1,maxIters=5000,confidence=.999)
keep=inside[:,0]>0;prediction=cv2.transform(left[None],affine)[0]
rms=float(np.sqrt(np.mean(np.sum((prediction[keep]-right[keep])**2,axis=1))))
world=np.vstack([affine,[0,0,1]])
delta=world@np.linalg.inv(current)
new_ui=delta@matrix(root)
photo=dict(inliers=int(keep.sum()),rms=rms,reference_span=np.ptp(left[keep],axis=0).tolist(),measured_pixel_to_world=world.tolist(),candidate_pixel_to_world=current.tolist(),world_delta=delta.tolist(),inferred_ui_matrix=new_ui.tolist(),notice='Existing static photo/app interior; actual features matched independently of hardware. Partial pizza occlusion is handled by RANSAC, not interpreted as camera movement.')

avatars=[]
for identifier in ['lunch13-p03-114','lunch13-p03-120']:
    node,M=find(root,identifier,np.eye(3));corners=M@np.array([[0,node['width'],node['width'],0],[0,0,node['height'],node['height']],[1,1,1,1]])
    x=int(math.floor(corners[0].min()))-1;y=int(math.floor(corners[1].min()))-1;x2=int(math.ceil(corners[0].max()))+1;y2=int(math.ceil(corners[1].max()))+1
    template=cv2.cvtColor(candidate[y:y2,x:x2],cv2.COLOR_RGB2GRAY)
    roi=cv2.cvtColor(source[max(0,y-16):min(1080,y2+16),max(0,x-16):min(1920,x2+16)],cv2.COLOR_RGB2GRAY)
    choices=[]
    for scale in np.arange(.95,1.0501,.002):
        w=max(1,int(round(template.shape[1]*scale)));h=max(1,int(round(template.shape[0]*scale)))
        resized=cv2.resize(template,(w,h),interpolation=cv2.INTER_LINEAR)
        values=cv2.matchTemplate(roi,resized,cv2.TM_CCOEFF_NORMED)
        _,score,_,location=cv2.minMaxLoc(values)
        choices.append(dict(scale=float(scale),score=float(score),location=[location[0]+x-16,location[1]+y-16],size=[w,h]))
    best=max(choices,key=lambda q:q['score'])
    old_center=[(x+x2)/2,(y+y2)/2];new_center=[best['location'][0]+best['size'][0]/2,best['location'][1]+best['size'][1]/2]
    avatars.append(dict(id=identifier,candidate_bbox=[x,y,x2,y2],best=best,candidate_center=old_center,source_center=new_center,photo_delta_predicted_center=(delta@np.array([*old_center,1]))[:2].tolist(),near_best_scale_interval=[min(q['scale'] for q in choices if q['score']>best['score']-.002),max(q['scale'] for q in choices if q['score']>best['score']-.002)],notice='Independent native rendered-avatar color/shape registration; bounded±16px translation and±5% scale. Scale resolution is limited by this small raster.') )
result=dict(frame=frame,photo=photo,avatars=avatars,notice='Read-only return-camera attribution. No scene/assets modified. A physical rim proposal alone was insufficient; compare independent photo and two avatar anchors before applying a UI-camera change.')
(P/'return-camera-738-v16-attribution.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
