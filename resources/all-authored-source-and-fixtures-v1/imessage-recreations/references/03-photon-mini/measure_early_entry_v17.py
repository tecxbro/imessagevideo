"""Independent entry-message planes and unread control, measured from native source."""
from pathlib import Path
import sys,json,math,importlib.util
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent
cv2.setNumThreads(1);cv2.setRNGSeed(48317)
scene=json.loads((P/'final-v15.scene.json').read_text())
phone=next(n for n in scene['layers'] if n['id']=='p03-86')
ui=next(n for n in phone['children'] if n['id']=='early-messages-ui-v13')
backdrop=next(n for n in phone['children'] if n['id']=='early-mail-backdrop-v13')
sift=cv2.SIFT_create(nfeatures=2500,contrastThreshold=.006,edgeThreshold=12)

def matrix(node,frame):
    values={k:sample(node.get('keyframes',{}).get(k,[dict(t=0,value=node.get(k,d))]),frame/30) for k,d in [('x',0),('y',0),('scaleX',1),('scaleY',1)]}
    return np.array([[values['scaleX'],0,values['x']],[0,values['scaleY'],values['y']],[0,0,1]],float)

def ui_matrix(frame):
    return matrix(phone,frame)@matrix(ui,frame)

references={}
for identifier in ['p03-27','p03-35','p03-50']:
    group=next(n for n in ui['children'] if n['id']==identifier)
    for child in group['children']:
        if child['type']!='image' or 'post' in child['id']:
            continue
        rgba=cv2.imread(child['src'],cv2.IMREAD_UNCHANGED)
        alpha=rgba[:,:,3].astype('float32')/255
        rgb=np.uint8(rgba[:,:,:3]*alpha[:,:,None]+253*(1-alpha[:,:,None]))
        points,descriptors=sift.detectAndCompute(cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY),np.uint8(alpha>.8)*255)
        references[child['id']]=dict(group=group,image=child,width=rgba.shape[1],height=rgba.shape[0],kp=points,desc=descriptors)

def prior(ref,frame):
    child=ref['image']
    pixel=np.array([[child['width']/ref['width'],0,child.get('x',0)],[0,child['height']/ref['height'],child.get('y',0)],[0,0,1]],float)
    return ui_matrix(frame)@matrix(ref['group'],frame)@pixel

def fit(ref,frame,points,descriptors):
    matcher=cv2.BFMatcher()
    pairs=matcher.knnMatch(ref['desc'],descriptors,k=2)
    matches=[a for a,b in pairs if a.distance<.72*b.distance]
    result=dict(frame=frame,asset=ref['image']['src'],image_id=ref['image']['id'],group_id=ref['group']['id'],intrinsic=[ref['width'],ref['height']],status='rejected',ratio_matches=len(matches))
    if len(matches)<10:
        return result
    source=np.float32([ref['kp'][m.queryIdx].pt for m in matches])
    target=np.float32([points[m.trainIdx].pt for m in matches]);target[:,0]+=550
    affine,inside=cv2.estimateAffine2D(source,target,method=cv2.RANSAC,ransacReprojThreshold=1.2,maxIters=5000,confidence=.999)
    if affine is None:
        return result
    keep=inside[:,0]>0
    count=int(keep.sum())
    predictions=cv2.transform(source[None,:,:],affine)[0]
    rms=float(np.sqrt(np.mean(np.sum((predictions[keep]-target[keep])**2,axis=1))))
    anchor=np.append(np.mean(source[keep],axis=0),1)
    old=prior(ref,frame)
    distance=float(np.linalg.norm(affine@anchor-(old@anchor)[:2]))
    singular=np.linalg.svd(affine[:,:2],compute_uv=False)
    span=np.ptp(source[keep],axis=0)
    result.update(inliers=count,rms=rms,semantic_distance=distance,inlier_span=span.tolist(),matrix=affine.tolist(),prior_matrix=old[:2].tolist())
    if count>=12 and rms<1.2 and distance<100 and min(singular)>.25 and max(singular)<2 and max(singular)/min(singular)<1.3 and span[0]>40 and span[1]>8:
        result['status']='measured'
    return result

def badge(image,frame):
    rgb=np.asarray(image)
    pred=ui_matrix(frame)@np.array([140,190,1.])
    mask=np.uint8(np.max(rgb[:300,600:800],axis=2)<100)
    number,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
    proposals=[]
    for index in range(1,number):
        x,y,w,h,area=stats[index]
        if not (8<w<60 and 4<h<65 and area>45):
            continue
        shape=np.uint8(labels==index)
        contours,_=cv2.findContours(shape,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        points=max(contours,key=cv2.contourArea)[:,0,:].astype(float)
        points[:,0]+=600
        points=points[(points[:,1]>0)&(points[:,1]<299)]
        # Remove an occluding horizontal cap, retaining only the actual circle arc.
        if h<w-2:
            points=points[points[:,1]<points[:,1].max()]
        if len(points)<15:
            continue
        design=np.column_stack([2*points[:,0],2*points[:,1],np.ones(len(points))])
        fit_values=np.linalg.lstsq(design,np.sum(points*points,axis=1),rcond=None)[0]
        cx,cy=fit_values[:2]
        radius=math.sqrt(max(0,fit_values[2]+cx*cx+cy*cy))
        rms=float(np.sqrt(np.mean((np.linalg.norm(points-[cx,cy],axis=1)-radius)**2)))
        if 10<radius<25 and rms<1.2 and abs(cx-pred[0])<30 and abs(cy-pred[1])<45:
            proposals.append(dict(center=[float(cx),float(cy)],radius=radius,rms=rms,bbox=[int(x+600),int(y),int(x+600+w),int(y+h)],visible_pixels=int(area)))
    return dict(frame=frame,predicted_center=pred[:2].tolist(),proposals=proposals)

rows=[];controls=[]
for frame in range(211,230):
    file=P/'early-entry-v17-source'/f'{frame-210:03}.png'
    image=Image.open(file).convert('RGB');bgr=cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
    points,descriptors=sift.detectAndCompute(cv2.cvtColor(bgr[:,550:1370,:800] if False else bgr[:800,550:1370],cv2.COLOR_BGR2GRAY),None)
    chosen=['early-blue-original-skin-v13','early-original-working-skin-v13','early-mail-pressed-skin-v13' if frame<214 else 'early-mail-pre-skin-v13']
    for identifier in chosen:
        rows.append(fit(references[identifier],frame,points,descriptors))
    controls.append(badge(image,frame))

spec=importlib.util.spec_from_file_location('glyphtrace',P.parent/'02-danieltian/trace_glyphs.py');tr=importlib.util.module_from_spec(spec);spec.loader.exec_module(tr)
refcontrol=next(row for row in controls if row['frame']==215)
if len(refcontrol['proposals'])!=1:
    raise ValueError('Reference unread badge is not unique')
ref=refcontrol['proposals'][0]
image=np.asarray(Image.open(P/'early-entry-v17-source/005.png').convert('RGB')).astype(float)
cx,cy=ref['center'];radius=ref['radius']+.25
left=int(math.floor(cx-radius));top=max(0,int(math.floor(cy-radius)));right=int(math.ceil(cx+radius));bottom=int(math.ceil(cy+radius))
yy,xx=np.mgrid[top:bottom,left:right]
gray=image[top:bottom,left:right].mean(2)
inner=(xx-cx)**2+(yy-cy)**2<(radius*.80)**2
black=float(np.median(gray[inner&(gray<100)]))
white=float(np.percentile(gray[inner],95))
alpha=np.clip((gray-black)/(white-black),0,1)*inner
count_path,metadata=tr.trace_alpha(alpha,x0=left,y0=top,threshold=.5)
# The independently visible chevron is bounded to the left of the count capsule.
x0=int(cx-65);x1=int(cx-22);y0=max(0,int(cy-22));y1=int(cy+22)
gray2=image[y0:y1,x0:x1].mean(2)
background=float(np.median(gray2[gray2>180]));foreground=float(np.percentile(gray2[gray2<100],10))
a=np.clip((background-gray2)/(background-foreground),0,1)
chevron_path,chevron_meta=tr.trace_alpha(a,x0=x0,y0=y0,threshold=.5)
ys,xs=np.where(a>.5)
chevron_box=[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+1+x0),int(ys.max()+1+y0)]
dim=sample(backdrop['keyframes']['opacity'],215/30)
fill=int(round(black/(1-dim)))
arrow_fill=int(round(foreground/(1-dim)))
control_reference=dict(frame=215,badge=ref,draw_radius=radius,badge_fill=fill,chevron_fill=arrow_fill,count_path=count_path,count_metadata=metadata,chevron_path=chevron_path,chevron_metadata=chevron_meta,chevron_bbox=chevron_box,pill_bbox=[chevron_box[0]-34,cy-41,cx+radius+30,cy+41],notice='Native circle/pill plus original semantic glyph outlines. Source glyph alpha is recovered before existing measured page dimming; no control screenshot is used.')
last_visible={'p03-27':217,'p03-35':216,'p03-50':215}
for row in rows:
    if row['frame']>last_visible[row['group_id']] and row['status']=='measured':
        row['status']='rejected_actual_occlusion'
        row['rejection_cause']='Native source confirms this original message/card is already behind the opaque foreground Mail pane. Similar foreground copy caused a false descriptor correspondence.'
result=dict(scope=[211,229],visibility_lifetimes=last_visible,messages=rows,controls=controls,control_reference=control_reference,notice='Existing static bounded message skins are measured independently in intrinsic pixel coordinates, preserving transparent crop insets. The full phone→UI→group→image transform is the semantic prior. Weak/occluded fits are rejected and retain original native state.')
(P/'early-entry-v17-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
print('Measured messages',[(r['frame'],r['group_id'],r['inliers'],round(r['rms'],3)) for r in rows if r['status']=='measured'])
print('Badge proposals',[(r['frame'],r['proposals']) for r in controls if r['proposals']])
print('Reference pill',control_reference['pill_bbox'],'badgeFill',fill)
