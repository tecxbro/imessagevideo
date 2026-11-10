"""Freeze native component measurements before changing the v5 retained cache."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy import ndimage
from PIL import Image

p=Path(__file__).parent;root=p.parent.parent
target=p/'component-fit-v5.json'
if target.exists():raise SystemExit('Refusing to overwrite frozen component-fit-v5.json')
source=np.array(Image.open(p/'native/28.0.png').convert('RGB'))
candidate_path=root/'outputs/retained-frames/measured-frames-jRBOzF/000840.png'
candidate=np.array(Image.open(candidate_path).convert('RGB'))

def component(array,roi,predicate):
 x1,y1,x2,y2=roi;crop=array[y1:y2,x1:x2];lab,_=ndimage.label(predicate(crop));counts=np.bincount(lab.ravel());counts[0]=0;mask=lab==counts.argmax();mask=ndimage.binary_fill_holes(mask);yy,xx=np.where(mask)
 return mask,[int(xx.min()+x1),int(yy.min()+y1),int(xx.max()+x1),int(yy.max()+y1)]

def ink(array,roi,predicate):
 x1,y1,x2,y2=roi;c=array[y1:y2,x1:x2];m=predicate(c);yy,xx=np.where(m)
 return {'bbox':[int(xx.min()+x1),int(yy.min()+y1),int(xx.max()+x1),int(yy.max()+y1)],'pixels':int(m.sum())}

def simplify(points,tolerance):
 if len(points)<3:return points
 a,b=points[0],points[-1];d=b-a;length=float(np.dot(d,d))
 if length:dist=np.abs(d[0]*(points[:,1]-a[1])-d[1]*(points[:,0]-a[0]))/length**.5
 else:dist=np.linalg.norm(points-a,axis=1)
 i=int(dist.argmax())
 if dist[i]>tolerance:return np.vstack([simplify(points[:i+1],tolerance)[:-1],simplify(points[i:],tolerance)])
 return points[[0,-1]]

def vector_outline(mask,roi,origin,scale=1):
 # Directed exposed pixel edges form an editable closed contour. Simplify below one
 # native pixel, then use quadratic corner controls to remove pixel stair steps.
 ys,xs=np.where(mask);edges={}
 for x,y in zip(xs,ys):
  if y==0 or not mask[y-1,x]:edges[(int(x),int(y))]=(int(x+1),int(y))
  if x==mask.shape[1]-1 or not mask[y,x+1]:edges[(int(x+1),int(y))]=(int(x+1),int(y+1))
  if y==mask.shape[0]-1 or not mask[y+1,x]:edges[(int(x+1),int(y+1))]=(int(x),int(y+1))
  if x==0 or not mask[y,x-1]:edges[(int(x),int(y+1))]=(int(x),int(y))
 start=min(edges,key=lambda q:(q[1],q[0]));points=[start];v=edges[start]
 while v!=start:
  points.append(v);v=edges[v]
  if len(points)>20000:raise ValueError('Contour did not close')
 points=np.asarray(points,dtype=float);cut=len(points)//2
 pts=np.vstack([simplify(points[:cut+1],.8)[:-1],simplify(np.vstack([points[cut:],points[:1]]),.8)[:-1]])
 pts=(pts+np.array(roi[:2])-np.array(origin))/scale
 mids=(pts+np.roll(pts,-1,axis=0))/2
 d=f'M {mids[-1,0]:.4f} {mids[-1,1]:.4f} '
 for q,m in zip(pts,mids):d+=f'Q {q[0]:.4f} {q[1]:.4f} {m[0]:.4f} {m[1]:.4f} '
 return d+'Z'

audio_roi=(430,350,1240,720)
audio_mask,audio_box=component(source,audio_roi,lambda c:(np.abs(c.astype(int)-[158,163,174]).max(2)<12))
distance_roi=(220,210,900,370)
distance_mask,distance_box=component(source,distance_roi,lambda c:(np.abs(c.astype(int)-[236,236,236]).max(2)<5))
white=(source[400:515,600:1065].min(2)>225)
lab,_=ndimage.label(white);bars=[]
for sl in ndimage.find_objects(lab):
 if sl is None:continue
 sy,sx=sl;w,h=sx.stop-sx.start,sy.stop-sy.start
 if 2<=w<=9 and h>=8:bars.append({'x':sx.start+600-audio_box[0],'y':sy.start+400-audio_box[1],'width':w,'height':h,'radius':w/2})
black=lambda c:c.max(2)<80
caption=lambda c:(c.min(2)>185)&(c.max(2)<245)&((c.max(2)-c.min(2))<30)
grayink=lambda c:(c.min(2)>150)&(c.max(2)<235)&((c.max(2)-c.min(2))<8)
ledger={'source_frame':840,'time':840*1001/30000,'inputs':{'scene_v5_sha256':hashlib.sha256((p/'scene-v5-artwork.json').read_bytes()).hexdigest(),'candidate_png_sha256':hashlib.sha256(candidate_path.read_bytes()).hexdigest()},'audio':{'bbox':audio_box,'outline':vector_outline(audio_mask,audio_roi,audio_box[:2]),'waveform_bars':bars,'caption_source':ink(source,(495,520,1150,640),caption),'caption_candidate':ink(candidate,(495,520,1150,640),caption)},'distance':{'bbox':distance_box,'outline':vector_outline(distance_mask,distance_roi,distance_box[:2],1.45),'ink_source':ink(source,(250,240,900,325),black),'ink_candidate':ink(candidate,(250,230,900,310),black)},'composer':{'source_ink':ink(source,(390,710,1000,850),grayink),'candidate_ink':ink(candidate,(390,710,1000,850),grayink)},'anchors':[]}
for n,sec in [(810,'27.0'),(840,'28.0'),(870,'29.0')]:
 a=np.array(Image.open(p/f'native/{sec}.png').convert('RGB'))
 _,mapbox=component(a,(180,0,1000,225),lambda c:(np.abs(c.astype(int)-[227,227,224]).max(2)<5))
 # The distance bubble moves to the top by29s; fit the actual component separately.
 droi=(200,210,950,380) if n<870 else(200,55,950,220)
 _,dbox=component(a,droi,lambda c:(np.abs(c.astype(int)-[236,236,236]).max(2)<5))
 ledger['anchors'].append({'frame':n,'time':n*1001/30000,'map_footer_bbox':mapbox,'distance_bbox':dbox})
# Only genuine narrow hardware strips, with alpha excluding every screen pixel.
hardware=[]
for name,box,inner in [('left',(126,0,174,1080),170),('right',(1273,0,1320,1080),1276)]:
 x1,y1,x2,y2=box;crop=Image.open(p/'native/28.0.png').convert('RGBA').crop(box);a=np.array(crop);xx=np.arange(x1,x2)[None,:];valid=xx<=inner if name=='left' else xx>=inner;a[:,:,3]=np.where(np.broadcast_to(valid,a.shape[:2]),255,0);file=p/'assets'/f'phone-{name}-native28.png';Image.fromarray(a).save(file);hardware.append({'src':'assets/'+file.name,'source_frame':840,'source_crop':list(box),'alpha_policy':f'Only exterior hardware pixels, inner boundary x{inner}; screen pixels transparent.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
ledger['hardware_assets']=hardware
target.write_text(json.dumps(ledger,indent=2));print(target);print('audio',audio_box,'distance',distance_box,'bars',len(bars));print(ledger['anchors'])
