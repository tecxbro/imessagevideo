from pathlib import Path
from PIL import Image
import numpy as np,json,subprocess
from scipy import ndimage
REF=Path(__file__).resolve().parent;ROOT=REF.parents[1];rows=json.load(open(REF/'root-orbit-base.json'));records=[]
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',"select='between(n,548,597)'",'-fps_mode','passthrough','-pix_fmt','rgb24','-threads','1','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
def box(a,name,prior):
 a=a.astype(float);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 if name=='lyft':m=(r>175)&(b>120)&(g<135)
 elif name=='airbnb':m=(r>175)&(g<135)&(b>65)&(b<170)
 elif name=='resy':m=(r>165)&(g<140)&(b<85)
 elif name=='green':m=(g>150)&(r<180)&(b<155)&(g-r>40)&(g-b>20)
 else:m=(b-r>70)&(b-g>30)&(r<150)&(g<190)
 yy,xx=np.indices(m.shape);m&=(abs(xx-prior[0])<260)&(abs(yy-prior[1])<260)
 if name=='muse':
  ys,xs=np.where(m)
  if len(xs)<20:return None
  return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 lab,_=ndimage.label(m,np.ones((3,3)));options=[]
 for i,sl in enumerate(ndimage.find_objects(lab)):
  if sl is None:continue
  y,x=sl;count=int((lab[sl]==i+1).sum())
  if count<100:continue
  cx=(x.start+x.stop)/2;cy=(y.start+y.stop)/2;score=(cx-prior[0])**2+(cy-prior[1])**2;options.append((score,[x.start,y.start,x.stop,y.stop]))
 return max(options,key=lambda r:(r[1][2]-r[1][0])*(r[1][3]-r[1][1]))[1] if options else None
for row in rows:
 n=row['frame'];raw=p.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3;a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3);b=np.array(Image.open(ROOT/f'outputs/02-danieltian/frames-gsap/{n:06}.png').convert('RGB'));data=[]
 for l in row['layers']:
  name=l['id'].split('middle-fly-')[-1]
  if name not in ('lyft','airbnb','resy','green','muse'):continue
  prior=(l['x']+45*l['scaleX'],l['y']+45*l['scaleY']);native=box(b,name,prior)
  if native is None:data.append(dict(name=name,status='no-native-detection'));continue
  center=((native[0]+native[2])/2,(native[1]+native[3])/2);target=box(a,name,center)
  if target is None:data.append(dict(name=name,status='no-source-detection',native=native));continue
  clippedX=target[0]<=1 or target[2]>=1919 or native[0]<=1 or native[2]>=1919;clippedY=target[1]<=1 or target[3]>=1079 or native[1]<=1 or native[3]>=1079
  if name=='muse' and (clippedX or clippedY):data.append(dict(name=name,status='clipped-ink-preserved',native=native,target=target));continue
  rx=(target[2]-target[0]-1)/max(1,native[2]-native[0]-1);ry=(target[3]-target[1]-1)/max(1,native[3]-native[1]-1)
  if clippedX and not clippedY:rx=ry
  elif clippedY and not clippedX:ry=rx
  elif clippedX and clippedY:data.append(dict(name=name,status='both-axes-clipped-preserved',native=native,target=target));continue
  if not .7<rx<1.4 or not .7<ry<1.4:data.append(dict(name=name,status='implausible-ratio-preserved',native=native,target=target,ratio=[rx,ry]));continue
  ax=0 if target[0]>1 and native[0]>1 else 2;ay=1 if target[1]>1 and native[1]>1 else 3
  newx=target[ax]-(native[ax]-l['x'])*rx;newy=target[ay]-(native[ay]-l['y'])*ry;old=[l['x'],l['y'],l['scaleX'],l['scaleY']];l.update(x=newx,y=newy,scaleX=l['scaleX']*rx,scaleY=l['scaleY']*ry);data.append(dict(name=name,status='measured',native=native,target=target,oldPose=old,newPose=[l['x'],l['y'],l['scaleX'],l['scaleY']],clipped=[clippedX,clippedY]))
 records.append(dict(frame=n,actors=data))
p.stdout.close();assert p.wait()==0
layers=[dict(id=f"root-orbit-pose-{r['frame']}",type='group',start=r['frame']/30,end=(r['frame']+1)/30,children=r['layers']) for r in rows]
(REF/'root-orbit-patch.json').write_text(json.dumps(dict(scope=[[548,597]],layers=layers,measurements=records,notice='Independent measured native actor cameras on existing original logo artwork; no source-frame/video texture. Clipping is not resizing: one uncut axis anchors clipped discs; clipped Muse ink and implausible weak matches are preserved pending visual review. Original header598+ is untouched.'),indent=2));print({'frames':len(rows),'measured':sum(q['status']=='measured' for r in records for q in r['actors'])})
