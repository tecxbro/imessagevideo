from pathlib import Path
import json,sys
from PIL import Image
import numpy as np
from scipy.ndimage import label,find_objects,gaussian_filter1d
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-surface.oiqQZp/final-frames')
d=Path('/tmp/sidehoe-threads.bMakKw')
m=json.loads((d/'measurements.json').read_text())
act=json.loads((d/'actors.json').read_text())
cfg=p/'project/scene.json'; j=json.loads(cfg.read_text()); s=j['tracks']
def bounds(q, x0, y0, x1, y1, v, min_x_px=2, min_y_px=2):
 a=q[y0:y1,x0:x1]
 n=(a.mean(axis=2)<v)&(np.ptp(a,axis=2)<30)
 i=np.flatnonzero(n.sum(axis=0)>min_x_px)
 m=np.flatnonzero(n.sum(axis=1)>min_y_px)
 if not len(i) or not len(m):return None
 return [x0+int(i[0]),y0+int(m[0]),int(i[-1]-i[0]+1),int(m[-1]-m[0]+1)]
for f in range(337,342):
 q=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype='int16')
 old=np.asarray(Image.open(prior/f'{f:06}.png').convert('RGB'),dtype='int16')
 row=m[str(f)][0]
 x,y,scale,ky=row['est']
 lx,rx=row['rails']
 l=lx[0][-1];r=rx[0][0]
 subset=(l,r)
 ystart={337:733,338:754,339:776,340:795,341:806}[f]
 measurements=row['keys']
 # Merge repeated x spans produced where a wide glyph cuts across a key cap.
 keys={box[0]:box[:4] for box in measurements}
 if len(keys)<10:
  # Independently locate the rightmost key that falls outside the old rectangle.
  peak=max(keys.values())
  w=int(np.median([t[2]-t[0] for t in keys.values()]))
  pitch=int(np.median(np.diff(sorted(keys))))
  left=peak[0]+pitch
  keys[left]=[left,peak[1],left+w,peak[3]]
 cases=sorted(keys.values())
 pos=np.array(cases)
 pitch,center=np.polyfit(np.arange(len(cases)),(pos[:,0]+pos[:,2])/2,1)
 width=float(np.median(pos[:,2]-pos[:,0]))+{337:3,338:4,339:3,340:3,341:2}[f]
 first_y=float(np.median(pos[:,1]))-{337:2,338:2,339:2,340:1,341:1}[f]
 height=float(np.percentile(pos[:,3]-pos[:,1],65))+{337:4,338:4,339:3,340:2,341:1}[f]
 x0=center-width/2
 # Recover the alternate key rows where they are visible in the source.
 rows=[]
 for stage,count in enumerate((10,9,7)):
  offset={0:0,1:.50,2:1.50}[stage]
  yy=first_y+stage*51.2*scale
  xx=x0+offset*pitch
  if stage:
   y2=min(1000,round(yy)+36)
   closeness=np.median(q[max(0,round(yy)):y2,l+6:r-6,:],axis=(2))
   if closeness.size:
    av=np.mean(closeness>240,axis=1)
    if any(av>.14):
     yy += min(np.flatnonzero(av>.14)[0],7)-2
  if yy<1000:
   rows.append([round(xx,3),round(yy,3),round(pitch,3),width,height,count])
 # Use the source's leading keyboard plane for the screen fill.
 tray=np.percentile(q[ystart+3:ystart+10,l+12:r-12,:].reshape(-1,3),48,axis=0).astype(int)
 tray=np.clip(tray,207,228).tolist()
 captures,blue=act[str(f)][0]
 grays=[part for part in captures if part[0][0]<l+80 and part[0][2]<r-90 and 37<part[0][3]-part[0][1]<97]
 assert len(grays)==2,(f,grays)
 items=[]
 for rect,_,ink in grays:
   l0,y0,r0,y1=rect
   bb=bounds(q,l0+17,y0+8,r0-10,y1-8,166)
   if bb is None:
    term=ink[0]
    bb=[term[0],term[1],term[2]-term[0],term[3]-term[1]]
   items.append([rect,[[*bb]]])
 today_top=grays[1][0][3]+18
 today_end=blue[1][0][1]-9
 today=bounds(q,450,today_top,550,today_end,191)
 if today is None:
    today=[466,today_top+17,60,16]
 ext=[]
 for side,(begin,end) in enumerate([lx[0],rx[0]]):
    begin,maxx=begin-10,end+10
    shade=np.median(q[220:695,begin:maxx+1,:],axis=(0,2))
    ramp=np.interp(np.linspace(begin,maxx,24),np.arange(begin,maxx+1),shade).round().astype(int).tolist()
    ext.append([begin,maxx,ramp])
 blue_box=blue[0][0]
 top0, right0 = blue_box[1],blue_box[2]
 bx,by,bw,bh=blue_box[0]+17,top0+12,right0-blue_box[0]-30,blue_box[3]-top0-18
 area=q[by:by+bh,bx:bx+bw]
 dark=(area[:,:,0]>143)&(area[:,:,1]>222)&(area[:,:,2]>241)
 ys,xs=np.where(dark)
 if len(xs)>50:
    blue_ink=[int(xs.min())+bx,int(ys.min())+by,int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1)]
 else:
    blue_ink=[blue_box[0]+(blue_box[3]-blue_box[1])*.36,top0+(blue_box[3]-top0)*.32,
      (right0-blue_box[0])*.83,(blue_box[3]-top0)*.35]
 config=dict(rails=subset,keys=[ystart,tray,rows],items=items,today=today,blue=blue_box,blueInk=blue_ink,
   bluePaint=blue[0][1],edgeRamps=ext,corners=[round((rect[3]-rect[1])*.44,1) for rect,_,_ in grays],
   railStart={337:58,338:0,339:0,340:0,341:0}[f],
   focus=[(4.3,6.3,.78),(4.1,6.1,.8),(3.3,4.6,.8),(1.5,2.6,.83),(0,0,.88)][f-337])
 j['threadRegistration']['sofia'][str(f)]=config
 print(f,rows,grays,today,blue_ink)
cfg.write_text(json.dumps(j,indent=2)+'\n')
