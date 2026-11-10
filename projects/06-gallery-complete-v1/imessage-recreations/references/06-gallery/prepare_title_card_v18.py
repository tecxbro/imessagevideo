"""Measure native heading zoom; actual bounded notification UI with native camera."""
from pathlib import Path
import json,copy,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
D=Path(__file__).resolve().parent;F=D/'native-transition-v18';A=D/'assets';s=json.loads((D/'scene-combined-handoff-v18.json').read_text())
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float)
def get(id):return next(q for q in s['layers'] if q['id']==id)
def key(rows,k):return [{'t':r['frame']/30,'value':r[k],'ease':'linear'} for r in rows]
ref=load(600);roi=ref[480:600,358:1562].mean(2);alpha=1-roi/255;path,stats=trace.trace_alpha(alpha,358,480)
yy,xx=np.nonzero((ref.mean(2)<35)&(np.indices(ref.shape[:2])[0]>480)&(np.indices(ref.shape[:2])[0]<600));sel=np.linspace(0,len(xx)-1,1100).astype(int);xx,yy=xx[sel],yy[sel];scales=np.arange(.32,1.021,.001);mx=960+(xx[None,:]-960)*scales[:,None];my=540+(yy[None,:]-540)*scales[:,None];poses=[];last=1.
for f in range(597,687):
 a=load(f).mean(2);samples=map_coordinates(a,[my,mx],order=1);cost=np.sort(samples,axis=1)[:,:880].mean(1)
 if f<607:cost[np.abs(scales-1)>.015]=1e5
 elif f>633:cost[np.abs(scales-last)>.06]=1e5
 else:cost[np.abs(scales-last)>.11]=1e5
 at=int(np.argmin(cost));sc=float(scales[at]);last=sc;vals=samples[at];dark=vals[vals<220];hist=np.histogram(dark,bins=np.arange(0,225,5))[0];binAt=int(np.argmax(hist));near=dark[(dark>=binAt*5)&(dark<(binAt+1)*5)];ink=float(np.median(near)) if len(near) else 255.;opacity=float(np.clip((255-ink)/255,0,1));poses.append({'frame':f,'scale':sc,'opacity':opacity,'inkMean':float(cost[at]),'modalInk':ink})
g=get('g-1239');old=g['keyframes'];g.update(children=[{'type':'path','id':'v18-remembers-native-original-outline','d':path,'fill':'#000000','semanticText':'Remembers your people'}],end=689/30)
g['keyframes']={'y':old['y'],'scaleX':[q for q in old['scaleX'] if q['t']<597/30]+key(poses,'scale'),'scaleY':[q for q in old['scaleY'] if q['t']<597/30]+key(poses,'scale'),'opacity':[q for q in old['opacity'] if q['t']<597/30]+key(poses,'opacity')}

# A single bounded static notification card preserves original glyphs/emoji and
# glass interior; source video and source frame playback are never used.
ar=np.uint8(load(663)[62:322,356:1564]);mask=Image.new('L',(1208,260));ImageDraw.Draw(mask).rounded_rectangle((0,0,1207,259),radius=102,fill=255);rgba=np.dstack([ar,np.array(mask)]);p=A/'v18-notification-original-ui.png';Image.fromarray(rgba).save(p)
cardposes=json.loads((D/'notification-v18-world-bounds.json').read_text());card=dict(type='group',id='context-v8-birthday-card-84',start=cardposes[0]['frame']/30,end=690/30,children=[dict(type='image',id='v18-notification-ui',src=str(p),x=356,y=62,width=1208,height=260)],keyframes={k:key(cardposes,v) for k,v in [('x','x'),('y','y'),('scaleX','sx'),('scaleY','sy'),('opacity','opacity'),('blur','blur')]})
card['keyframes']['opacity'].append({'t':690/30,'value':0})
s['layers']=[card if q['id']=='context-v8-birthday-card-84' else q for q in s['layers']]

# Native birthday phone is already entering at684, before the old687 start.
phone=get('g-1306');early=[]
for f in range(675,687):
 a=load(f);wide=(a[:,850:1070].max(2)<105).sum(1)>190;ys=np.where(wide&(np.arange(1080)>550))[0]
 if not len(ys):continue
 center=a[:,945:975].mean((1,2))<105;valid=np.where(center&(np.arange(1080)>=ys[0]-10)&(np.arange(1080)<ys[0]+20))[0]
 early.append({'frame':f,'y':float(valid.min()-10)})
front=copy.deepcopy(phone);front['id']='v18-birthday-phone-early-foreground';front['start']=early[0]['frame']/30;front['end']=690/30
front['keyframes']['y']=key(early,'y')+[q for q in phone['keyframes']['y'] if 687/30<=q['t']<690/30]
def prefix(o):
 o['id']='early-'+o['id']
 if o.get('id')=='early-phone-v17-message-Emma':o['start']=early[0]['frame']/30
 for q in o.get('children',[]):prefix(q)
prefix(front);phone['start']=690/30;s['layers'].append(front)
(D/'title-camera-v18.json').write_text(json.dumps(poses,indent=2));(D/'birthday-early-v18.json').write_text(json.dumps(early,indent=2));(D/'scene-title-card-v18.json').write_text(json.dumps(s,indent=2)+'\n');(D/'title-card-v18-patch.json').write_text(json.dumps({'replace':{q['id']:q for q in s['layers'] if q['id'] in ['g-1239','context-v8-birthday-card-84','g-1306']},'append':[front]},indent=2))
(A/'title-card-v18-provenance.json').write_text(json.dumps([{'element':'g-1239','source_frame':600,'box':[358,480,1562,600],'kind':'static original typography traced to editable native outline with measured zoom/opacity','trace':stats},{'path':str(p),'source_frame':663,'box':[356,62,1564,322],'kind':'single bounded static rich notification UI; internal text and frosted portrait imprint bitmap; outer native camera/blur/opacity measured independently'}],indent=2))
print('Title',[(r['frame'],round(r['scale'],3),round(r['opacity'],3)) for r in poses if r['frame'] in [600,609,615,618,624,630,645,681,684,686]]);print('Phone',early)
