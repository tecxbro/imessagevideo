"""Close the remaining observed reaction/late-fade/sender clipping artifacts without changing other sections."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/middle-dense';A=R/'assets/middle-art';P=R/'middle-refinement.json';p=json.loads(P.read_text());root=p['replacements']['group-1118'];nodes={l['id']:l for l in root['children']};records=[];RUN=json.loads((R/'middle-body-runs.json').read_text());camera=[dict(t=int(k)/30,value=v['scale']) for k,v in RUN.items()];s0=RUN['855']['scale']
def ar(n):return np.array(Image.open(M/f'source-{n:04d}.png').convert('RGB')).astype(float)
def sample(ks,t):
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:
   f=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*f
 return ks[-1]['value']
def state(l,k,t):return sample(l['keyframes'][k],t)
# An unmasked reaction crop included a piece of the underlying Lyft text/blue reply. Limit the original art to the actual plate silhouette.
for name,n,box,ellipses in [('command-like',735,(1310,367,1450,526),[(1310,367,1440,497),(1401,476,1436,511),(1430,503,1448,521)]),('budget-like',810,(1068,665,1195,803),[(1070,667,1194,795),(1177,773,1195,800)])]:
 a=Image.fromarray(ar(n).astype('uint8')).crop(box).convert('RGBA');w,h=a.size;matte=Image.new('L',(w*4,h*4));d=ImageDraw.Draw(matte)
 for l,t,r,b in ellipses:d.ellipse(((l-box[0])*4,(t-box[1])*4,(r-box[0])*4,(b-box[1])*4),fill=255)
 a.putalpha(matte.resize((w,h),Image.Resampling.LANCZOS));path=A/(name+'-isolated.png');a.save(path);nodes['middle-reaction-'+name]['children'][0]['src']=str(path);records.append(dict(kind='isolated original reaction plate',sourceFrame=n,sourceBounds=list(box),asset=str(path),diagnosis='The broad nonwhite matte also selected text/blue fill behind the reaction. Use the plate/connector silhouette only.'))
cmd=nodes['middle-reaction-command-like'];im=cmd['children'][0];seen=[]
for n in range(714,835,3):
 t=n/30;x=state(cmd,'x',t)+im['x']*state(cmd,'scaleX',t);y=state(cmd,'y',t)+im['y']*state(cmd,'scaleY',t);w=im['width']*state(cmd,'scaleX',t);h=im['height']*state(cmd,'scaleY',t);l=max(0,int(x));top=max(0,int(y));r=min(1920,int(x+w));b=min(1080,int(y+h))
 if r<=l or b<=top:continue
 a=ar(n)[top:b,l:r];yellow=(a[:,:,0]>200)&(a[:,:,1]>135)&(a[:,:,2]<165)&(a[:,:,1]<a[:,:,0]*.96)&(a[:,:,2]<a[:,:,1]*.8)
 if yellow.sum()>15:seen.append(t)
if seen:cmd['end']=min(cmd['end'],seen[-1]+.1)
# Keep only the protruding blue tail. The earlier source chunk also covered part of the body with a flat fill, leaving a visible rectangular color seam over its gradient.
from trace_glyphs import trace_alpha
for name,cn in [('budget-reply',780),('love-it',930)]:
 node=nodes['middle-message-'+name];body=node['children'][0];tail=next(c for c in node['children'] if c['id']=='middle-outgoing-tail-'+name);W,H=body['width'],body['height'];Rr=body['radius'];cx=state(node,'x',cn/30);cy=state(node,'y',cn/30);x0=int(cx+W-100);y0=int(cy+H-40);x1=min(1920,int(cx+W+15));y1=min(1080,int(cy+H+30));a=ar(cn)[y0:y1,x0:x1];gid=body['fill'][5:-1];gradient=next(g for g in p['gradients'] if g['id']==gid);color=gradient['stops'][-1]['color'];red=int(color[1:3],16);aa=np.clip((253-a[:,:,0])/(253-red),0,1);aa[ndimage.binary_fill_holes(aa>.35)]=1;yy,xx=np.indices(aa.shape);xx=xx+x0-cx+.5;yy=yy+y0-cy+.5;qx=np.maximum(np.abs(xx-W/2)-(W/2-Rr),0);qy=np.maximum(np.abs(yy-H/2)-(H/2-Rr),0);inside=(qx*qx+qy*qy<(Rr-1.5)**2)&(xx>1.5)&(xx<W-1.5)&(yy>1.5)&(yy<H-1.5);aa[inside]=0;dd,stats=trace_alpha(aa,x0-cx,y0-cy);tail['d']=dd;tail['fill']=color;records.append(dict(kind='native protruding outgoing tail',sourceFrame=cn,sourceBounds=[x0,y0,x1,y1],diagnosis='Remove the body-sized source chunk from the flat tail path so it cannot overpaint the body gradient.',**stats))
# The late Love it bubble is pale, so a hard blue threshold misses it. Fit its actual composite color instead of an arbitrary fade value.
love=nodes['middle-message-love-it'];ref=ar(930)[710:785,1305:1467];sel=(ref[:,:,2]-ref[:,:,0]>30)&(ref[:,:,0]<150);base=np.median(ref[sel],0);opacity=[]
for n in range(972,1006,3):
 t=n/30;x=state(love,'x',t);y=state(love,'y',t);sx=state(love,'scaleX',t);sy=state(love,'scaleY',t);w=love['children'][0]['width']*sx;h=love['children'][0]['height']*sy;l=max(0,int(x+10));top=max(0,int(y+10));r=min(1920,int(x+w-10));b=min(1080,int(y+h-10))
 if r<=l or b<=top:continue
 a=ar(n)[top:b,l:r];sel=(a[:,:,2]-a[:,:,0]>10)&(a[:,:,1]-a[:,:,0]>5)
 alpha=0.
 if sel.sum()>80:
  observed=np.median(a[sel],0);alpha=float(np.clip((253-observed[0])/(253-base[0]),0,1))
 opacity.append(dict(t=t,value=alpha))
if opacity:love['keyframes']['opacity']=[dict(t=30.4,value=1),dict(t=32.3,value=1)]+opacity
# If only the bottom of the Airbnb sender label remains at the viewport edge, align its bottom instead of moving the entire word back into view.
label=nodes.get('middle-airbnb-card-sender-label');card=nodes['middle-airbnb-rich-card'];ms=[]
if label:
 for n in range(822,1000,3):
  t=n/30;S=sample(camera,t)/s0 # sender typography follows the main camera, not the card's entry spring
  top=state(card,'y',t) if t>=28.25 else 788-(t-27.5)*150;left=960+(417-960)*sample(camera,t);x0=max(0,int(left+8*S));x1=min(1920,int(left+190*S));y0=max(0,int(top-80*S));y1=max(0,int(top-5*S))
  if x1<=x0 or y1<=y0:continue
  a=ar(n)[y0:y1,x0:x1];mask=(a.max(2)<200)&(a.max(2)-a.min(2)<25);ys,xs=np.where(mask)
  if len(xs)<15:continue
  targetX=float(xs.min()+x0-536*S);targetY=float(ys.min()+y0-425*S)
  if y0==0 and ys.min()==0:targetY=float(ys.max()+y0+1-452*S)
  ms.append(dict(t=t,x=targetX,y=targetY,scaleX=S,scaleY=S))
 if ms:label['keyframes'].update({k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']});label['end']=min(33.3,ms[-1]['t']+.1)
p['provenance'].append(dict(kind='final middle observed-artifact checkpoint',reactionAssets=records,commandReactionLastSeen=seen[-1] if seen else None,lateReplyOpacity=opacity,senderLabelMeasurements=ms));P.write_text(json.dumps(p,indent=2));print('Closed reaction background artifact; command reaction ends',cmd['end'])
