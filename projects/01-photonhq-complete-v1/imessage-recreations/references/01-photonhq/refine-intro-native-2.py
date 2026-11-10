from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,sys,hashlib,copy
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations');REF=R/'references/01-photonhq';P=R/'verification/fidelity-review/01-intro';AS=REF/'assets/intro-review';spec=json.loads((REF/'intro-review-elements.json').read_text());base=json.loads((REF/'scene-intro-base-v4.json').read_text());extra=json.loads((P/'source-extra-map.json').read_text())
def tk(ps):return [dict(t=n/30,value=float(v),ease='linear') for n,v in ps]
def bbox(m,x0=0,y0=0):
 yy,xx=np.where(m);return [int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+1+x0),int(yy.max()+1+y0)] if len(xx) else None
# A standalone Introducing word is centered before Photon arrives. Restrict color,
# not its rightedge, so the complete neutral word remains measurable at0.1s.
cb=next(a['coreBounds'] for a in spec['assets'] if a.get('id')=='intro-black-main');obs=[]
for n in range(1,45):
 a=np.array(Image.open(P/'source-crops'/f'{n+1:04d}.png').convert('RGB'))[50:330].astype(float);alpha=np.clip((255-a.mean(2))/255,0,1);alpha[a.max(2)-a.min(2)>12]=0;pk=float(alpha.max());b=bbox(alpha>max(.025,pk*.5),0,400);sx=(b[2]-b[0])/(cb[2]-cb[0]);sy=(b[3]-b[1])/(cb[3]-cb[1]);obs.append(dict(frame=n,sourceBounds=b,x=b[0]-cb[0]*sx,y=b[1]-cb[1]*sy,scaleX=sx,scaleY=sy,opacity=pk))
p=next(c for c in spec['replacements']['group-3']['children'] if c['id']=='intro-black-main');p['keyframes']={k:tk([(o['frame'],o[k]) for o in obs]) for k in ['x','y','scaleX','scaleY','opacity']};spec['measurements']['Introducing']=obs
# Exact full-native channel observations replace sparse motion and interpolated
# reciprocalclips. Each icon is a bounded authenticgraphic; labelcopy is native.
frames={n:np.array(Image.open(P/extra[str(n)]).convert('RGB')) for n in range(132,196)}
assert np.array_equal(frames[135][350:800],np.array(Image.open(P/'source-crops/0136.png').convert('RGB')))
records={};seen6=False;counts=[];raw={i:[] for i in range(6)}
for n,a0 in frames.items():
 a=a0.astype(float);m=(a.max(2)-a.min(2)>50)&(a.min(2)<225)&(a.max(2)>140);m=ndimage.binary_closing(m,iterations=2);lab,num=ndimage.label(m,np.ones((3,3)));bs=[]
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  y,x=sl;w=x.stop-x.start;h=y.stop-y.start;area=np.count_nonzero(lab[sl]==j)
  if w>=4 and h>10 and area>35:bs.append((area,[x.start,y.start,x.stop,y.stop]))
 if len(bs)>6:bs=sorted(bs,reverse=True)[:6]
 bs=sorted([b for _,b in bs],key=lambda b:b[1]);c=len(bs);counts.append(dict(frame=n,count=c,bounds=bs));seen6|=c==6;rows=list(range(6-c,6)) if seen6 else list(range(c))
 for row,b in zip(rows,bs):raw[row].append(dict(frame=n,visibleBounds=b))
canonold=json.loads((REF/'channel-stack-provenance.json').read_text());names=['iMessage','Whatsapp','Telegram','SMS','Email','Phone Call'];channelledger=[]
for row,name in enumerate(names):
 oldbox=canonold[row]['sourceBounds'];W0=oldbox[2]-oldbox[0];H0=oldbox[3]-oldbox[1];H0=W0 if row==4 else H0
 full=[q for q in raw[row] if q['visibleBounds'][0]>2 and q['visibleBounds'][1]>2 and q['visibleBounds'][2]<1918 and q['visibleBounds'][3]<1078 and .8<(q['visibleBounds'][2]-q['visibleBounds'][0])/(q['visibleBounds'][3]-q['visibleBounds'][1])<1.2]
 if not full:raise ValueError('No full canonical icon '+name)
 canon=max(full,key=lambda q:(q['visibleBounds'][2]-q['visibleBounds'][0])*(q['visibleBounds'][3]-q['visibleBounds'][1]));b=canon['visibleBounds'];cw,ch=b[2]-b[0],b[3]-b[1];ratio=float(np.median([(q['visibleBounds'][2]-q['visibleBounds'][0])/(q['visibleBounds'][3]-q['visibleBounds'][1]) for q in full]));box=[max(0,b[0]-8),max(0,b[1]-8),min(1920,b[2]+8),min(1080,b[3]+8)];dest=AS/f'channel-{row}-full.png';Image.fromarray(frames[canon['frame']]).crop(box).save(dest);poses=[];labels=[]
 for q in raw[row]:
  n=q['frame'];x,y,x1,y1=q['visibleBounds'];w,h=x1-x,y1-y
  if x1>=1918:w=h*ratio
  if y<=2:h=w/ratio;y=y1-h
  if y1>=1078:h=w/ratio
  sx,sy=w/W0,h/H0;v=dict(frame=n,x=float(x),y=float(y),scaleX=float(sx),scaleY=float(sy),fullBounds=[float(x),float(y),float(x+w),float(y+h)],visibleBounds=q['visibleBounds']);poses.append(v)
  roi=[max(0,int(x+w+5)),max(0,int(y-15*sy)),min(1920,int(x+700*sx)),min(1080,int(y+h+30*sy))]
  if roi[2]<=roi[0] or roi[3]<=roi[1]:continue
  a=frames[n][roi[1]:roi[3],roi[0]:roi[2]].astype(float);alpha=np.clip((255-a.mean(2))/255,0,1);alpha[a.max(2)-a.min(2)>12]=0;peak=float(alpha.max());bb=bbox(alpha>max(.06,peak*.5),roi[0],roi[1]);width=(bb[2]-x+3)/sx if bb else 1
  labels.append(dict(frame=n,roi=roi,sourceBounds=bb,visibleWidth=float(width),opacity=peak if bb else 0,x=x,y=y,sx=sx,sy=sy))
 complete_labels=[q for q in labels if q['sourceBounds'] and q['sourceBounds'][1]>2 and q['sourceBounds'][3]<1078]
 lc=max(complete_labels or labels,key=lambda q:q['visibleWidth'] if q['sourceBounds'] else 0);bb=lc['sourceBounds'];roi=[max(0,bb[0]-2),max(0,bb[1]-2),min(1920,bb[2]+2),min(1080,bb[3]+2)];a=frames[lc['frame']][roi[1]:roi[3],roi[0]:roi[2]].astype(float);alpha=np.clip((255-a.mean(2))/255,0,1);alpha[a.max(2)-a.min(2)>12]=0;d,stats=trace_alpha(alpha)
 path=dict(type='path',id=f'intro-channel-label-path-{row}',d=d,fill='#000000',x=(roi[0]-lc['x'])/lc['sx'],y=(roi[1]-lc['y'])/lc['sy'],scaleX=1/lc['sx'],scaleY=1/lc['sy'],semanticText=name,sourceFrame=lc['frame'],sourceBounds=roi,editability='Native source glyph outlines; canonical label chosen at its maximum observed complete width.')
 labelmap={q['frame']:q for q in labels};fk=[];ik=[];op=[]
 for q in poses:
  n=q['frame'];ll=labelmap.get(n,{});f=max(1,float(ll.get('visibleWidth',1)))/900;fk.append((n,f));ik.append((n,1/f));op.append((n,ll.get('opacity',0)))
 counter=dict(type='group',id=f'intro-channel-label-counter-{row}',keyframes={'scaleX':tk(ik)},children=[path]);clip=dict(type='group',id=f'channel-label-clip-{row}',clip=dict(x=0,y=-30,width=900,height=250),keyframes=dict(scaleX=tk(fk),opacity=tk(op)),children=[counter]);icon=dict(type='image',id=f'channel-icon-{row}',src=str(dest),x=(box[0]-b[0])*W0/cw,y=(box[1]-b[1])*H0/ch,width=(box[2]-box[0])*W0/cw,height=(box[3]-box[1])*H0/ch,sourceFrame=canon['frame'],sourceBounds=box,editability='Independent bounded original icon artwork, fully visible canonical observation.')
 group=dict(type='group',id=f'measured-channel-row-{row}',start=poses[0]['frame']/30,end=(poses[-1]['frame']+1)/30,children=[icon,clip],keyframes={k:tk([(q['frame'],q[k]) for q in poses]) for k in ['x','y','scaleX','scaleY']},semanticText=name)
 spec['replacements'][group['id']]=group;spec['assets'].append(dict(id=icon['id'],kind='bounded original app icon',asset=str(dest),sourceFrame=canon['frame'],sourceBounds=box,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()));spec['assets'].append(dict(id=path['id'],kind='native glyph outlines',semanticText=name,sourceFrame=lc['frame'],sourceBounds=roi,**stats));channelledger.append(dict(row=row,name=name,canonicalIcon=canon,canonicalLabel=lc,poses=poses,labels=labels));spec['measurements'][f'channel-{row}']=poses
spec['changed_frame_ranges']=[[0,239]];spec['notice']='Prototype2 pending native checks: standalone title neutralROI fixed; all six source-channel icons/labels measured at every native frame, unclipped icon artwork, explicit source lifetimes, reciprocal clipping pairs exact at nativeframes.';(REF/'intro-review-elements.json').write_text(json.dumps(spec,indent=2));(P/'channel-native-measurements.json').write_text(json.dumps(dict(counts=counts,rows=channelledger),indent=2));print(json.dumps(dict(channel_rows=[dict(row=q['row'],first=q['poses'][0]['frame'],last=q['poses'][-1]['frame'],iconFrame=q['canonicalIcon']['frame'],labelFrame=q['canonicalLabel']['frame']) for q in channelledger]),indent=2))
