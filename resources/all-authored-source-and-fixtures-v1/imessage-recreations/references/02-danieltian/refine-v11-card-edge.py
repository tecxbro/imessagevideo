"""Card bounds exclude the independent sender and avatar; diagnose before retry."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import json,numpy as np
R=Path('/workspace/imessage-recreations/references/02-danieltian');P=R/'v11-middle-refinement.json';p=json.loads(P.read_text());root=p['replacements']['group-1118'];N={n['id']:n for n in root['children']};card=N['middle-airbnb-rich-card'];label=N['middle-airbnb-card-sender-label'];RUN=json.loads((R/'middle-body-runs.json').read_text());camera=[dict(t=int(k)/30,value=v['scale']) for k,v in RUN.items()]
def sample(ks,t):
 ks=sorted(ks,key=lambda q:q['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return ks[-1]['value']
def state(n,k,t):return sample(n['keyframes'][k],t)
poses=[];labels=[]
for n in range(843,871):
 t=n/30;a=np.array(Image.open(R/'assets/middle-every-frame'/f'source-{n:04d}.png').convert('RGB')).astype(float);left=960-543*sample(camera,t);x=int(max(0,left-65));r=int(min(1920,left+900));y0=300;reg=a[y0:,x:r];mask=reg.min(2)<249;mask=ndimage.binary_closing(mask,iterations=5);lab,num=ndimage.label(mask,np.ones((3,3)));cc=[]
 for li,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if xx.start+x<left+100 and w>250 and h>150:cc.append((w*h,li,sl))
 if not cc:continue
 _,li,sl=max(cc,key=lambda q:q[0]);yy,xx=sl;local=lab[yy,xx]==li;row=local.sum(1);broad=np.flatnonzero(row>(xx.stop-xx.start)*.45)
 if not len(broad):continue
 top=yy.start+int(broad.min());bottom=yy.start+int(broad.max())+1;inner=lab[top:bottom,:]==li;col=inner.sum(0);xc=np.flatnonzero(col>(bottom-top)*.32);l=x+int(xc.min());rr=x+int(xc.max()+1);top+=y0;bottom+=y0;poses.append(dict(t=t,x=l,y=top,scaleX=(rr-l)/card['children'][0]['width'],scaleY=(bottom-top)/card['children'][0]['height']))
 S=sample(camera,t)/RUN['855']['scale'];ll=int(left+8*S);rx=int(left+190*S);ty=max(0,int(top-80*S));by=max(0,int(top-3*S));roi=a[ty:by,ll:rx];m=(roi.max(2)<180)&(roi.max(2)-roi.min(2)<25);ys,xs=np.where(m)
 if len(xs)>15:labels.append(dict(t=t,x=float(xs.min()+ll-536*S),y=float(ys.min()+ty-425*S),scaleX=S,scaleY=S))
for node,ms in [(card,poses),(label,labels)]:
 for k in ['x','y','scaleX','scaleY']:
  keep=[q for q in node['keyframes'][k] if round(q['t']*30) not in {round(m['t']*30) for m in ms}];node['keyframes'][k]=sorted(keep+[dict(t=m['t'],value=m[k]) for m in ms],key=lambda q:q['t'])
body=N['middle-message-budget-reply']['children'][0]
for q in body.get('keyframes',{}).get('height',[]):q['value']=min(body['height'],q['value'])
p['provenance'].append(dict(kind='v11 card native edge refinement',diagnosis='The all-nonwhite connected component bridged the sender label to the photo and included the bottom avatar/tail, overestimating card height. Fit broad card rows/columns only, then refit its independent sender above the actual photo.',measurements=poses,senderMeasurements=labels));P.write_text(json.dumps(p,indent=2));print('Refit card edges',len(poses),'sender',len(labels),flush=True)
