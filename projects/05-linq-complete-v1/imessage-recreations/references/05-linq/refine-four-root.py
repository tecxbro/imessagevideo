"""Measure the original Four in a Row panel and individual native counter poses."""
from pathlib import Path
import json,subprocess,numpy as np
from PIL import Image
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent
OUT=REF/'assets/root-late';OUT.mkdir(exist_ok=True)
scene=json.loads((ROOT/'outputs/05-linq/final-v9/scene.json').read_text())
old=next(l for l in scene['layers'] if l['id']=='rich-group-10')
asset=ROOT/'outputs/05-linq/final-v9'/old['children'][0]['src']
base=np.array(Image.open(asset).convert('RGB'))
def navy(a):
 return (a[:,:,0]<40)&(a[:,:,1]<45)&(a[:,:,2]<65)&(a[:,:,2].astype(np.int16)-a[:,:,0]>3)
ys,xs=np.where(navy(base));local_left=int(xs.min());local_right=int(xs.max())+1
red=(base[:,:,0]>180)&(base[:,:,1]<120)&(base[:,:,2]<150)
yellow=(base[:,:,0]>180)&(base[:,:,1]>140)&(base[:,:,2]<100)
labels,count=ndimage.label(red|yellow)
empty=Image.fromarray(base).crop((42,163,108,229))
clean=Image.fromarray(base)
for i,sl in enumerate(ndimage.find_objects(labels)):
 if sl is None or (labels[sl]==i+1).sum()<500:continue
 y,x=sl;cx=(x.start+x.stop)/2;cy=(y.start+y.stop)/2
 clean.paste(empty,(round(cx-33),round(cy-33)))
clean.save(OUT/'four-board-empty.png')

first,last=920,1010;w,h=960,720
cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),
 '-vf',f"select='between(n,{first},{last})'",'-fps_mode','passthrough','-threads','1',
 '-pix_fmt','rgb24','-f','rawvideo','pipe:1']
proc=subprocess.Popen(cmd,stdout=subprocess.PIPE)
poses=[];observations=[]
for n in range(first,last+1):
 data=proc.stdout.read(w*h*3)
 if len(data)!=w*h*3:raise ValueError('Incomplete native source decode')
 a=np.frombuffer(data,np.uint8).reshape(h,w,3)
 labels,count=ndimage.label(navy(a));candidates=[]
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is None:continue
  y,x=sl
  if y.stop-y.start>680 and x.stop-x.start>3:candidates.append((int((labels[sl]==i+1).sum()),x.start,x.stop))
 if not candidates:continue
 _,left,right=max(candidates)
 x=right-local_right if left<=1 else left-local_left
 if x>956 or x+486<4:continue
 # Threshold masks can lose a compressed edge pixel. Align the static branded
 # header in a small local search instead of propagating that offset to counters.
 def header_error(candidate):
  lo=max(0,int(candidate));hi=min(w,int(candidate)+486)
  if hi-lo<20:return float('inf')
  piece=base[:130,lo-int(candidate):hi-int(candidate)].astype(np.float32)
  return float(((piece-a[:130,lo:hi].astype(np.float32))**2).mean())
 x=min(range(round(x)-5,round(x)+6),key=header_error)
 poses.append((n,float(x)))
 local=a.copy();valid=np.zeros((h,w),bool);valid[140:590,max(0,int(x)):min(w,int(x+486))]=True
 for color,mask in [('red',(a[:,:,0]>180)&(a[:,:,1]<120)&(a[:,:,2]<150)),
                    ('yellow',(a[:,:,0]>180)&(a[:,:,1]>140)&(a[:,:,2]<100))]:
  lab,_=ndimage.label(mask&valid)
  for i,sl in enumerate(ndimage.find_objects(lab)):
   if sl is None:continue
   yy,xx=sl;area=int((lab[sl]==i+1).sum())
   if area<500 or yy.stop-yy.start<20 or xx.stop-xx.start<15:continue
   cx=(xx.start+xx.stop)/2-x;cy=(yy.start+yy.stop)/2
   col=int(np.argmin(np.abs(np.array([75,144,211,278,344,411])-cx)))
   if abs(cx-[75,144,211,278,344,411][col])>10:continue
   observations.append(dict(frame=n,col=col,color=color,x=cx,y=cy,width=xx.stop-xx.start,height=yy.stop-yy.start))
proc.stdout.close();proc.wait()
if len(poses)<20:raise ValueError('Insufficient panel observations')
gstart,gend=poses[0][0]/30,(poses[-1][0]+1)/30
tracks={}
for n,x in poses:
 for col in range(6):
  coins=sorted([o for o in observations if o['frame']==n and o['col']==col],key=lambda c:-c['y'])
  for rank,c in enumerate(coins):tracks.setdefault((col,rank),[]).append(c)
layers=[dict(id='root-four-empty-board',type='image',src=str(OUT/'four-board-empty.png'),x=0,y=0,width=486,height=720,
 semanticText='Four in a Row board and original branded UI; counters removed for independent animation',editability='Static original panel artwork, internal text is bitmap')]
for (col,rank),items in tracks.items():
 colors={c['color'] for c in items}
 if len(colors)!=1:raise ValueError(f'Ambiguous counter identity {col}/{rank}: {colors}')
 start=gstart if items[0]['frame']<955 else items[0]['frame']/30
 keys={name:[] for name in ['x','y','width','height']}
 for item in items:
  width,height=item['width']+1,item['height']+1
  values=dict(x=item['x']-width/2,y=item['y']-height/2,width=width,height=height)
  for name,value in values.items():keys[name].append(dict(t=item['frame']/30,value=value))
 layers.append(dict(id=f'root-four-counter-{col}-{rank}',type='circle',x=items[0]['x']-27,
  y=items[0]['y']-27,width=54,height=54,fill='#FF3550' if items[0]['color']=='red' else '#FFC914',
  start=start,end=gend,keyframes=keys,semanticText=f"{items[0]['color']} counter, column {col+1}, stack {rank+1}"))
new=dict(id=old['id'],type='group',x=poses[0][1],y=0,start=gstart,end=gend,
 keyframes={'x':[dict(t=n/30,value=x) for n,x in poses]},children=layers)
report=dict(source='source.mp4',sourceFrames=[p[0] for p in poses],panelWidth=486,panelLocalMaskBounds=[local_left,local_right],
 poses=poses,counterObservations=observations,counterTracks=len(tracks),lifetime=[gstart,gend],
 note='Source-native panel silhouette measurements and independently drawn native counters. No full-frame or video layer.')
(OUT/'four-measurements.json').write_text(json.dumps(report,indent=2))
(REF/'root-four-patch.json').write_text(json.dumps({'replacements':{old['id']:new},'changed_ranges':[[920,1010]],'provenance':report},indent=2))
print(json.dumps({'panel_frames':len(poses),'first':poses[0],'last':poses[-1],'counters':len(tracks)}))
