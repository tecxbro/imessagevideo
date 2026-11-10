"""Correct measured phone checkpoint associations after source-native visual inspection."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,copy
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/root-early-end-measure';A=R/'assets/early-end-art';P=R/'early-end-refinement.json';patch=json.loads(P.read_text());G=patch['replacements']['group-995'];record=next(l for l in patch['provenance'] if l.get('kind')=='native measured phone reveal');oldphone=record['measurements'];ledger=[]
def ar(n):return np.array(Image.open(M/f'frame-{n:04d}.png').convert('RGB')).astype(float)
def comps(mask):
 lab,num=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());out=[]
 for li,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  y,x=sl;out.append(dict(box=[x.start,y.start,x.stop,y.stop],area=int(areas[li]),label=li))
 return out,lab
def art(n,box,name):
 p=A/(name+'.png');Image.fromarray(ar(n).astype('uint8')).crop(box).save(p);ledger.append(dict(kind='bounded original phone-header UI artwork',sourceFrame=n,sourceBounds=list(box),asset=str(p),editability='Independent original UI artwork; internal Muse label copy is bitmap.'));return dict(id='phone-checkpoint-'+name,type='image',src=str(p),x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1])
def sample(points,t,key='y'):
 pts=sorted(points,key=lambda q:q['t'])
 if t<=pts[0]['t']:return pts[0][key]
 for a,b in zip(pts,pts[1:]):
  if t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']);return a[key]+f*(b[key]-a[key])
 return pts[-1][key]
# The avatar portrait has a small internal motion. The rigid back-arrow/phone hardware provides the correct common camera translation.
def back_arrow(a,limit):
 cc,labels=comps(a[:limit,465:540].max(2)<160);valid=[]
 for c in cc:
  l,t,r,b=c['box'];w=r-l;h=b-t;cx=(l+r)/2+465
  if 18<w<45 and 30<h<75 and 480<cx<520 and c['area']>100:valid.append(c)
 if not valid:return None
 return min(valid,key=lambda c:abs((c['box'][0]+c['box'][2])/2+465-500))['box']
ref=back_arrow(ar(225),200);refTop=ref[1];refBot=ref[3];phone=[]
for m in oldphone:
 n=round(m['t']*30);a=ar(n);arrow=back_arrow(a,650 if n<198 else 200);avatar=m.get('avatarY',m['y']);y=avatar
 if arrow is not None:y=float(arrow[3]-refBot if arrow[1]<2 else arrow[1]-refTop)
 phone.append(dict(t=m['t'],y=y,avatarY=avatar))
G['keyframes']['y']=[dict(t=m['t'],value=m['y']) for m in phone];y183=next(m['y'] for m in phone if abs(m['t']-6.1)<.001)
for c in G['children']:
 if c['id'].startswith('early-art-phone-') and c.get('sourceFrame')==183:c['y']=c['sourceBounds'][1]-y183
 if c['id']=='img-974':c.setdefault('keyframes',{})['y']=[dict(t=m['t'],value=m['avatarY']-m['y']) for m in phone]
 if c['id']=='bubble-983':
  for q in c['keyframes']['y']:q['value']+=sample(oldphone,q['t'])-sample(phone,q['t'])
# Complete the cropped top of the portrait's gray circle; the original cropped portrait remains independently posed above it.
if not any(c['id']=='phone-checkpoint-avatar-circle' for c in G['children']):
 ix=next(i for i,c in enumerate(G['children']) if c['id']=='img-974');G['children'].insert(ix,dict(id='phone-checkpoint-avatar-circle',type='circle',x=855,y=-15,width=210,height=210,fill='#DDDDDD',stroke='#EEEEEE',strokeWidth=2))
# Retain authentic small glass UI without substituting a visibly different font or flat button material.
G['children']=[c for c in G['children'] if c['id'] not in ['rect-975','text-976','text-977','circle-978','path-979','phone-checkpoint-muse-label','phone-checkpoint-back-button']]
G['children'].extend([art(225,(810,170,1100,285),'muse-label'),art(225,(420,10,580,175),'back-button')])
# Actual incoming body components occur in the left message column. The Muse header pill at x817 is not a typing bubble.
typ=[];sure=[]
for m in phone:
 n=round(m['t']*30);a=ar(n);mask=(a.min(2)>190)&(a.max(2)<245)&(a.max(2)-a.min(2)<18);mask[:450]=False;mask[:,:380]=False;mask[:,1400:]=False;cc,ll=comps(mask);valid=[c for c in cc if 380<c['box'][0]<600 and c['box'][2]-c['box'][0]>150 and c['box'][3]-c['box'][1]>60]
 if not valid:continue
 c=max(valid,key=lambda q:q['area']);b=c['box'];rec=dict(t=n/30,x=b[0],y=b[1]-m['y'],width=b[2]-b[0],height=b[3]-b[1])
 if b[2]-b[0]<400:typ.append(rec)
 else:sure.append(rec)
# Trace the original typing silhouette once; its tail stays native and its pop is measured independently of the phone.
a=ar(225);box=(400,616,640,767);roi=a[box[1]:box[3],box[0]:box[2]];bg=np.array([231,230,233]);alpha=np.clip((253-roi.mean(2))/(253-bg.mean()),0,1);alpha[ndimage.binary_fill_holes(alpha>.35)]=1;d,st=trace_alpha(alpha);children=[dict(id='phone-checkpoint-typing-shape',type='path',d=d,fill='#E7E6E9')]
for i,(cx,cy) in enumerate([(72.5,64.5),(120.5,64.5),(168.5,64.5)]):
 fills=[]
 for m in typ:
  n=round(m['t']*30);a=ar(n);S=m['width']/240;gx=m['x']+cx*S;gy=m['y']+sample(phone,m['t'])+cy*S;color=a[min(1079,max(0,round(gy))),min(1919,max(0,round(gx)))].astype(int);fills.append(dict(t=m['t'],value='#'+''.join(f'{v:02x}' for v in color)))
 children.append(dict(id='phone-checkpoint-typing-dot-'+str(i),type='circle',x=cx-14.5,y=cy-14.5,width=29,height=29,fill='#D2D1D5',keyframes={'fill':fills}))
tnode=dict(id='bubble-987',type='group',children=children,start=typ[0]['t'],end=sure[0]['t'],keyframes={'x':[dict(t=m['t'],value=m['x']) for m in typ],'y':[dict(t=m['t'],value=m['y']) for m in typ],'scaleX':[dict(t=m['t'],value=m['width']/240) for m in typ],'scaleY':[dict(t=m['t'],value=m['height']/151) for m in typ]})
G['children']=[c for c in G['children'] if c['id'] not in ['bubble-987','circle-988','circle-989','circle-990']]+[tnode]
# The following reply grows from the typing indicator; preserve the observed body size and clip text rather than compressing its glyphs.
cn=255;a=ar(cn);box=(400,574,1248,725);roi=a[box[1]:box[3],box[0]:box[2]];alpha=np.clip((253-roi.mean(2))/(253-bg.mean()),0,1);alpha[ndimage.binary_fill_holes(alpha>.35)]=1;bd,bst=trace_alpha(alpha);neut=(roi.max(2)<150)&(roi.max(2)-roi.min(2)<15);vals,cnt=np.unique(roi[neut].astype('uint8'),axis=0,return_counts=True);ink=vals[cnt.argmax()];aa=np.clip((float(bg.mean())-roi.mean(2))/(float(bg.mean())-ink.mean()),0,1);dd,gst=trace_alpha(aa);glyph=dict(id='phone-checkpoint-reply-glyphs',type='path',d=dd,fill='#'+''.join(f'{v:02x}' for v in ink),semanticText='sure. lemme bring in some friends.',sourceFrame=cn)
# Paired reciprocal clip keys are sampled at every rendered frame, so they cancel exactly instead of stretching between sparse keys.
widths=[]
for fn in range(round(sure[0]['t']*30),262):
 tt=fn/30;val=sample(sure,tt,'width');widths.append(dict(t=tt,value=val/848))
bodyWidths=widths;_,gx=np.where(aa>.5);rightPadding=848-(int(gx.max())+1);widths=[dict(t=q['t'],value=max(.01,(q['value']*848-rightPadding)/848)) for q in bodyWidths]
clip=dict(id='phone-checkpoint-reply-clip',type='group',clip=dict(x=0,y=0,width=848,height=151),keyframes={'scaleX':widths},children=[dict(id='phone-checkpoint-reply-inverse',type='group',keyframes={'scaleX':[dict(t=q['t'],value=1/max(.001,q['value'])) for q in widths]},children=[glyph])]);snode=dict(id='bubble-994',type='group',children=[dict(id='phone-checkpoint-reply-shape',type='path',d=bd,fill='#E7E6E9',keyframes={'scaleX':bodyWidths}),clip],start=sure[0]['t'],end=8.73,keyframes={'x':[dict(t=m['t'],value=m['x']) for m in sure],'y':[dict(t=m['t'],value=m['y']) for m in sure]});G['children']=[c for c in G['children'] if c['id']!='bubble-994']+[snode]
# The early sent-message flight retains dark gray copy. Fit colors directly on the253 stage, avoiding a second opacity fade of already composited source colors.
ca=ar(225);cbox=(624,354,1520,582);crop=ca[cbox[1]:cbox[3],cbox[0]:cbox[2]];blue=(crop[:,:,2]-crop[:,:,0]>45)&(crop[:,:,0]<160);vals,cnt=np.unique(crop[blue].astype('uint8'),axis=0,return_counts=True);bbg=vals[cnt.argmax()];ga=np.clip((crop[:,:,0]-bbg[0])/(253-bbg[0]),0,1);ga*=ndimage.binary_fill_holes(blue)
flight=next(l for l in patch.get('new_layers',[]) if l['id']=='early-sent-message-flight');body,glyph=flight['children'];bodyfills=[];textfills=[]
for m in record['flightMeasurements']:
 n=round(m['t']*30);a=ar(n);w=max(1,round((cbox[2]-cbox[0])*m['scaleX']));h=max(1,round((cbox[3]-cbox[1])*m['scaleY']));mask=np.array(Image.fromarray((ga*255).astype('uint8')).resize((w,h),Image.Resampling.BILINEAR))/255;xx=round(m['x']);yy=round(m['y']);x0=max(0,xx);y0=max(0,yy);x1=min(1920,xx+w);y1=min(1080,yy+h)
 if x1<=x0 or y1<=y0:continue
 rr=a[y0:y1,x0:x1];mm=mask[y0-yy:y1-yy,x0-xx:x1-xx];text=rr[mm>.7];bodypix=rr[(mm<.1)&(rr[:,:,2]-rr[:,:,0]>10)]
 bgc=np.median(bodypix,0).astype(int) if len(bodypix) else bbg;inkc=np.median(text[text.mean(1)<np.quantile(text.mean(1),.35)],0).astype(int) if len(text) else np.array([80,95,105]);bodyfills.append(dict(t=m['t'],value='#'+''.join(f'{v:02x}' for v in bgc)));textfills.append(dict(t=m['t'],value='#'+''.join(f'{v:02x}' for v in inkc)))
body['keyframes']={'fill':bodyfills};glyph['keyframes']={'fill':textfills};flight['keyframes'].pop('opacity',None)
record['measurements']=phone;record['firstTyping']=typ[0]['t'];record['typingBodyMeasurements']=typ;record['replyBodyMeasurements']=sure;patch['provenance']=[q for q in patch['provenance'] if q.get('kind')!='phone checkpoint refinement']+[dict(kind='phone checkpoint refinement',rigidPhoneMeasurements=phone,typingMeasurements=typ,replyMeasurements=sure,assets=ledger,diagnosis='Header Muse capsule falsely matched as typing; constrain to left message column. Rigid back arrow provides common camera; portrait keeps separate internal motion. Flight source colors were already composited and must not be faded a second time.')];P.write_text(json.dumps(patch,indent=2));print('Phone checkpoint refined; typing starts',typ[0]['t'],'reply starts',sure[0]['t'],flush=True)
