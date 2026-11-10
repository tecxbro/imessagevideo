"""Follow-up native entry/exit corrections proved after immutable v10 freeze."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import track,at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v10/scene.json').read_text());by={l['id']:l for l in s['layers']};fps=s['fps'];measurements=[];poses=[]
for n in range(359,364):
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'));m=a.max(2)<100;m[:700]=False;m[:,:150]=False;m[:,290:]=False;labels,_=ndimage.label(m);parts=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start;area=int((labels[sl]==i).sum())
  if 35<w<85 and 20<h<85 and(abs(w-h)<8 or yy.stop==1080)and .15<area/(w*h)<.5:parts.append(dict(bbox=[xx.start,yy.start,xx.stop,yy.stop],area=area,width=w,height=h))
 if len(parts)!=1:raise ValueError((n,parts))
 v=parts[0];b=v['bbox'];sx=v['width']/52.2;sy=sx if b[3]==1080 else v['height']/52.2;pose=dict(frame=n,time=n/fps,x=b[0]-38*sx,y=b[1]-32.15*sy,scaleX=sx,scaleY=sy);poses.append(pose);measurements.append(dict(**pose,source_plus=v,partial_bottom=b[3]==1080))
for prop in['x','y','scaleX','scaleY']:track(by['p0165'],prop,poses)
by['p0165']['start']=359/fps;by['p0165']['end']=511/fps;by['p0220']['end']=511/fps;by['v8-currentlocation']['end']=509/fps
press=json.loads((p/'measurements-v8/menu-press-v11.json').read_text())['measurements']
for c in by['p0132']['children']:
 if c['id']in['p0124','p0125']:track(c,'opacity',press)
(p/'measurements-v8/composer-gates-v11.json').write_text(json.dumps(dict(method='Native black-plus component first visible359(bottom clipped), absentthrough358; composer last visible510, suggestion lastvisible508. Original glyph camera retained364–510. Independent measured359–363pluscamera corrects entry before old firstglyphanchor.',measurements=measurements),indent=2))
# SharedLocation is already full-scale/opaque at its first actual513frame.
d=json.loads((p/'measurements-v8/shared-location-v11-parent.json').read_text());maprows=[]
for r in d['records']:
    if r['status']!='confident_source_template_pose':continue
    m=r['matrix'];maprows.append(dict(time=r['time'],x=m[0][2],y=m[1][2],scaleX=m[0][0],scaleY=m[1][1]))
by['p0223']['start']=maprows[0]['time']
for prop in['x','y','scaleX','scaleY']:track(by['p0223'],prop,maprows)
# The Spot body passes the upper crop. A clipped top is NOT y=0; retain its
# measured rigid offset from the still fully observed Where bubble.
where=by['p0155'];ref_scale=544/532;spot_scale=721/707;spotrows=[]
for n in range(458,480):
    t=n/fps;scale=at(where,'scaleX',t);ratio=scale/ref_scale
    spotrows.append(dict(time=t,x=at(where,'x',t)-7*ratio,y=at(where,'y',t)-174*ratio,scaleX=spot_scale*ratio,scaleY=spot_scale*ratio))
for prop in['x','y','scaleX','scaleY']:track(by['p0146'],prop,spotrows)
by['p0146']['end']=480/fps
s['gradients'].append(dict(id='upper-chat-glass-v11',type='linear',x1='0%',y1='0%',x2='0%',y2='100%',stops=[dict(offset='0%',color='#ffffff',opacity=.32),dict(offset='70%',color='#ffffff',opacity=0),dict(offset='100%',color='#ffffff',opacity=0)]))
pos=s['layers'].index(by['p0155']);s['layers'].insert(pos,dict(id='v11-upper-chat-glass',type='rect',x=70,y=0,width=1310,height=60,fill='url(#upper-chat-glass-v11)',start=458/fps,end=480/fps))
# Genuine physical-side material has its own measured horizontal camera; all
# screen contents stay in independent native layers.
hardware=json.loads((p/'measurements-v8/hardware-camera-v11.json').read_text())['measurements']
g=dict(id='v11-early-left-hardware',type='group',start=261/fps,end=361/fps,children=[dict(id='v11-early-left-hardware-art',type='image',src='assets/early-left-hardware-v11.png',x=30,y=0,width=96,height=1080)])
for prop in['x','scaleX','blur']:track(g,prop,hardware)
pos=s['layers'].index(by['p0109']);s['layers'].insert(pos,g);by['p0109']['start']=361/fps
# Measured abrupt favorite births are not opacity ramps from frame2.
by['p0007']['start']=3/fps;by['p0010']['start']=8/fps
for name in['p0012','p0015']:
    by[name]['start']=6/fps
    by[name].setdefault('keyframes',{})['opacity']=[dict(t=6/fps,value=1)]
# Favorite labels were false Nikki detections on2–9. Real faint inbox starts13.
ui=by['v8-inbox-rows'];ui['start']=13/fps
rows=json.loads((p/'measurements-v8/intro-inbox-birth-v11.json').read_text())['measurements'];poses=[]
for r in rows:
    if r['frame']<13:continue
    scale=r['scale'];poses.append(dict(time=r['time'],x=338-455*scale,y=r['y']+5-688*scale,scaleX=scale,scaleY=scale,opacity=r['opacity']))
for prop in['x','y','scaleX','scaleY','opacity']:track(ui,prop,poses)
# Pre687selected matches were restaurant rows under the dismissing modal.
# Native683–686lower region is exactly empty; first real card is687at y969.
by['p0262']['start']=687/fps
# First incoming Spot body is visible375, initially composer-occluded.
by['p0146']['start']=375/fps
# Raw original413has a composer-occluded Where body at205,664..726,728;
# 411/412contain none. Infer its full532width centered on that observed cap.
where=by['p0155'];where['start']=413/fps
for prop,value in[('x',199.5),('y',664),('scaleX',1),('scaleY',1)]:
    where['keyframes'][prop]=[k for k in where['keyframes'][prop]if k['t']<413/fps or k['t']>=414/fps]
    track(where,prop,[dict(time=413/fps,**{prop:value})])
for prop in['x','y','scaleX','scaleY']:
    g=by['p0146'];keys=g['keyframes'][prop];g['keyframes'][prop]=[k for k in keys if k['t']<375/fps or k['t']>=380/fps]
    values={'x':[191]*5,'y':[676,629,603,584,569],'scaleX':[1]*5,'scaleY':[1]*5}[prop]
    track(g,prop,[dict(time=n/fps,**{prop:value})for n,value in zip(range(375,380),values)])

# Source right rail remains visible after the old two-edge detector failed.
# Last full two-edge center is716.5; extend the genuine camera until actual480cut.
railrows=[]
for n in range(463,480):
    a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'));values=a[500].max(1);left=np.where(values[:65]<80)[0];right=np.where(values[-100:]<80)[0]+1340
    hi=int(right[0]);lo=int(left[-1])+1 if len(left) else None
    if lo is not None:scale=(hi-lo)/1272;x=lo-92*scale
    else:scale=(hi-716.5)/636;x=716.5-728*scale
    railrows.append(dict(frame=n,time=n/fps,x=x,scaleX=scale))
for prop in['x','scaleX']:track(by['p0109'],prop,railrows)
by['p0109']['end']=480/fps
# Actual source109left/right inner rail69/1374, native120reference285/1157.
physical=by['v8-v8-intro-physical'];sx=(1374-69)/(1157-285)
track(physical,'x',[dict(time=109/fps,x=69-285*sx)])
track(physical,'scaleX',[dict(time=109/fps,scaleX=sx)])
# Source native480has nineteen fully visible editable keyboard glyphs.
ink=json.loads((p/'measurements-v8/early-keyboard-ink-v11.json').read_text())['measurements'];keys={l['id']:l for l in by['p0220']['children']}
for r in ink:
    for prop in['x','y','scaleX','scaleY']:keys[r['id']][prop]=r[prop]
# Actual restaurant exit retains its grabbar until671, rather than the old
# fast ease toward an arbitrary1200endpoint.
measured=json.loads((p/'measurements-v8/exit-hardware-v11.json').read_text());exitrows=[r for r in measured['restaurant_exit']if 'sheet_y'in r]
track(by['p0255'],'y',exitrows,'sheet_y');by['p0255']['end']=672/fps
track(by['p0231'],'opacity',measured['restaurant_exit'],'scrim_opacity')
# Independent physical side edges correct the compact camera without moving UI.
for prop in['x','scaleX']:track(by['p0292'],prop,measured['hardware'])
# Message content passes under the opaque/frosted header, with chrome above it.
for gradient in s['gradients']:
    if gradient['id']=='small-header-glass-v10':gradient['stops']=[dict(offset='0%',color='#ffffff',opacity=1),dict(offset='85%',color='#ffffff',opacity=1),dict(offset='100%',color='#ffffff',opacity=0)]
header=by['p0298'];s['layers'].remove(header);s['layers'].insert(s['layers'].index(by['p0310'])+1,header)
for c in header['children']:
    if c['id']=='p0293':c['shadow']=dict(x=0,y=3,blur=12,color='#ededed')
    if c['id']=='p0297':c.update(text='Poke',x=405,y=160.5,scaleX=.96,scaleY=1.04)
header['children'].append(dict(id='v11-header-chevron',type='text',text='›',x=521,y=160.5,fontSize=43,fontFamily='SF Pro Display',fontWeight=600,fill='#adadad',scaleX=.8,scaleY=.84))
from v11_first_features import apply as first_feature_apply
first_feature_apply(s,p)
from v11_feature_middle import apply as middle_feature_apply
middle_feature_apply(s,p)
from v11_favorites import apply as favorite_apply
favorite_apply(s,p)
s['title']='Poke Apple Messages launch — native recreation v11 measured entrances'
s['source']['notes']+=' V11 measured exact births/cuts and independent UI/device material cameras: genuine isolated side hardware/Memoji assets; editable map/keyboard/title layers; native full-feature source measurements with clipped-bound inference. No source video or complete frame substitutes.'
(p/'scene-v11-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));print('Built v11 provisional')
