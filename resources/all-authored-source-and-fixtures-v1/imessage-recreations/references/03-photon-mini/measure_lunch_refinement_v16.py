"""Measured card press, return camera and source-owned copy; no scene mutation."""
from pathlib import Path
import sys,json,math
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent
BASE=P/'final-v15.scene.json'
SCENE=json.loads(BASE.read_text())
cv2.setNumThreads(1);cv2.setRNGSeed(16003)

def source(frame):
 p=P/f'lunch-refine-v16-source/{frame:04}.png' if frame<=617 else P/f'lunch-native/{frame-609:03}.png'
 return np.array(Image.open(p).convert('RGB'))
def state(n,k,d,f):return sample(n.get('keyframes',{}).get(k,[dict(t=0,value=n.get(k,d))]),f/30)
def matrix(n,f):
 x,y,sx,sy,a,ox,oy=[state(n,k,d,f) for k,d in [('x',0),('y',0),('scaleX',1),('scaleY',1),('rotation',0),('originX',0),('originY',0)]]
 a=math.radians(a);R=np.array([[math.cos(a)*sx,-math.sin(a)*sy,0],[math.sin(a)*sx,math.cos(a)*sy,0],[0,0,1]],float)
 T=np.eye(3);T[:2,2]=[x+ox,y+oy];U=np.eye(3);U[:2,2]=[-ox,-oy]
 return T@R@U

def find(n,identifier,f,parent=None):
 M=(np.eye(3) if parent is None else parent)@matrix(n,f)
 if n['id']==identifier:return n,M
 for c in n.get('children',[]):
  v=find(c,identifier,f,M)
  if v:return v
 return None

def root(identifier):return next(n for n in SCENE['layers'] if n['id']==identifier)
def rgb_at(im,point,r=2):
 x,y=np.rint(point[:2]).astype(int);return np.median(im[max(0,y-r):min(1080,y+r+1),max(0,x-r):min(1920,x+r+1)].reshape(-1,3),axis=0).tolist()

def measure_press():
 rows=[]
 for f in range(567,618):
  s=source(f);c=np.array(Image.open(P.parent.parent/f'outputs/03-photon-mini/frames-gsap/{f:06}.png').convert('RGB'))
  _,M=find(root('p03-204'),'measured-preview-inner-affine-v14',f)
  probes={}
  for name,point in {'whiteA':[440,160,1],'whiteB':[455,175,1],'whiteC':[470,160,1],'footer':[475,340,1]}.items():
   world=M@point;actual=rgb_at(s,world);old=rgb_at(c,world)
   probes[name]=dict(world=world[:2].tolist(),source_rgb=actual,candidate_rgb=old,alpha=1-float(np.mean(actual))/float(np.mean(old)))
  rows.append(dict(frame=f,probes=probes,press_alpha=float(np.median([probes[k]['alpha'] for k in ['whiteA','whiteB','whiteC']]))))
 (P/'card-press-v16-measurements.json').write_text(json.dumps(dict(frames=rows,notice='Native RGB median of three empty white food-card information-pane probes; independent gray footer verifies local press rather than whole-screen dim. Source RGB is sampled after full native root/card/inner transform.'),indent=2))
 print('press',[(r['frame'],round(r['press_alpha'],4)) for r in rows])

def measure_return():
 ui=root('measured-lunch-ui-v13');device=root('measured-lunch-device-v13')
 sift=cv2.SIFT_create(nfeatures=3000,contrastThreshold=.006,edgeThreshold=12)
 art,_=find(ui,'lunch13-food-preview-original-interior-v4',738)
 rgba=np.array(Image.open(art['src']).convert('RGBA'));h,w=rgba.shape[:2]
 alpha=rgba[:,:,3]/255;rgb=np.uint8(rgba[:,:,:3]*alpha[:,:,None]+253*(1-alpha[:,:,None]))
 kp,desc=sift.detectAndCompute(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),np.uint8(alpha>.8)*255)
 rows=[]
 for f in list(range(735,745))+[750]:
  s=source(f);c=np.array(Image.open(P.parent.parent/f'outputs/03-photon-mini/frames-gsap/{f:06}.png').convert('RGB'))
  node,current=find(ui,art['id'],f);current=current@np.diag([node['width']/w,node['height']/h,1])
  target,target_desc=sift.detectAndCompute(cv2.cvtColor(s,cv2.COLOR_RGB2GRAY),None)
  pairs=cv2.BFMatcher().knnMatch(desc,target_desc,k=2);good=[a for a,b in pairs if a.distance<.70*b.distance]
  left=np.float32([kp[m.queryIdx].pt for m in good]);right=np.float32([target[m.trainIdx].pt for m in good])
  A,inside=cv2.estimateAffine2D(left,right,method=cv2.RANSAC,ransacReprojThreshold=1.1,maxIters=5000,confidence=.999)
  keep=inside[:,0]>0;pred=cv2.transform(left[None],A)[0];rms=float(np.sqrt(np.mean(np.sum((pred[keep]-right[keep])**2,axis=1))))
  new_ui=np.vstack([A,[0,0,1]])@np.linalg.inv(current)@matrix(ui,f)
  old=matrix(device,f);center=old[0,2]+400*old[0,0]
  def runs(mask):
   out=[]
   for y in np.where(mask)[0]:
    if out and y==out[-1][1]+1:out[-1][1]=int(y)
    else:out.append([int(y),int(y)])
   return out
  def anchors(im):
   gray=im[:180,int(center-15):int(center)].max(2)
   ints=runs(np.mean(gray<30,axis=1)>.65);choices=[v for v in ints if v[1]-v[0]+1>20]
   # Source735 is still top-cropped; camera can use bottom and its cropped physical upper rim only after aperture is visible.
   pill=None if len(choices)!=1 else (choices[0][0]+choices[0][1]+1)/2
   gray=im[850:,int(center-40):int(center+40)].mean(2);ints2=runs(np.mean(gray<80,axis=1)>.8)
   bottom=None if not ints2 else ints2[-1][1]+851
   return dict(pill_center=pill,pill_runs=choices,bottom=bottom,bottom_runs=ints2)
  ca=anchors(c);sa=anchors(s)
  def horizontal_edges(im):
   g=im.mean(2);out=[]
   for yy in range(420,750,3):
    edges=[]
    for lo,hi in [(int(center-310),int(center-180)),(int(center+180),int(center+310))]:
     v=g[yy,lo:hi];inds=np.where(v<75)[0]
     if not len(inds):break
     j=int(inds[0] if lo<center else inds[-1])
     if lo<center:
      a=max(0,j-1);b=j;pos=a+(75-v[a])/(v[b]-v[a]) if v[b]!=v[a] else j
     else:
      a=j;b=min(len(v)-1,j+1);pos=a+(75-v[a])/(v[b]-v[a]) if v[b]!=v[a] else j
     edges.append(lo+float(pos))
    if len(edges)==2:out.append(edges)
   return np.median(out,axis=0).tolist()
  ce=horizontal_edges(c);se=horizontal_edges(s)
  scale_x=old[0,0]*(se[1]-se[0])/(ce[1]-ce[0]);position_x=se[0]-(ce[0]-old[0,2])/old[0,0]*scale_x
  # Horizontal opaque bezel modes, independent from UI photo.
  gray=s.mean(2);mask=gray[250:800]<55
  left_band=np.arange(int(center-290),int(center-170));right_band=np.arange(int(center+170),int(center+290))
  counts=mask.sum(0);lx=int(left_band[np.argmax(counts[left_band])]);rx=int(right_band[np.argmax(counts[right_band])])
  # Mode point is not consistently the same rim subpixel. Prefer exact hardware fitter, but expose confidence.
  from hardware_fit_v13 import fit_hardware
  fit=fit_hardware(Image.fromarray(s),dict(scale=float(old[0,0]),x=float(old[0,2]),y=float(old[1,2])),y_radius=80,edge_bands=[[float(center-290),float(center-170)],[float(center+170),float(center+290)]])
  ph=None
  if ca['pill_center'] is not None and sa['pill_center'] is not None and ca['bottom'] is not None and sa['bottom'] is not None:
   cp=(ca['pill_center']-old[1,2])/old[1,1];cb=(ca['bottom']-old[1,2])/old[1,1]
   sy=(sa['bottom']-sa['pill_center'])/(cb-cp);y=sa['pill_center']-sy*cp
   sx=scale_x;x=position_x;ph=[[sx,0,x],[0,sy,y],[0,0,1]]
  # Source/candidate blank page is sampled at an unoccluded canonical point.
  blank=new_ui@np.array([700,1100,1]);srgb=rgb_at(s,blank,3)
  rows.append(dict(frame=f,inliers=int(keep.sum()),rms=rms,reference_span=np.ptp(left[keep],axis=0).tolist(),ui_matrix=new_ui.tolist(),hardware_fit=fit,native_horizontal_edges=ce,source_horizontal_edges=se,scale_x=scale_x,position_x=position_x,native_anchors=ca,source_anchors=sa,physical_matrix=ph,blank_page_world=blank[:2].tolist(),blank_page_rgb=srgb,scrim_alpha=max(0,1-float(np.mean(srgb))/253)))
 print([(r['frame'],r['inliers'],round(r['rms'],3),r['source_anchors']['pill_center'],r['source_anchors']['bottom'],round(r['hardware_fit']['hardware_cost'],2),r['blank_page_rgb']) for r in rows])
 (P/'return-camera-v16-measurements.json').write_text(json.dumps(dict(frames=rows,notice='UI plane independently fitted from the one genuine static food/photo interior, physical width from outer rim, physical Y/height from actual aperture/bottom anchors. No food/Order actors modified. Hardware photometric Y rejected; aperture must be unambiguously visible.'),indent=2))

if __name__=='__main__':
 if len(sys.argv)==1 or sys.argv[1]=='press':measure_press()
 if len(sys.argv)==1 or sys.argv[1]=='return':measure_return()
