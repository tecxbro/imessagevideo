"""Keep phone camera independent from message pose during its fast source exit."""
from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json
R=Path('/workspace/imessage-recreations/references/02-danieltian');P=R/'v11-boundary-refinement.json';p=json.loads(P.read_text());g=p['replacements']['group-995'];N={n['id']:n for n in g['children']};records=[]
def comps(mask):
 ll,num=ndimage.label(mask,np.ones((3,3)));out=[]
 for sl in ndimage.find_objects(ll):
  yy,xx=sl;out.append([xx.start,yy.start,xx.stop,yy.stop])
 return out
def insert(node,k,n,v):
 ks=node.setdefault('keyframes',{}).setdefault(k,[]);ks[:]=sorted([q for q in ks if round(q['t']*30)!=n]+[dict(t=n/30,value=v)],key=lambda q:q['t'])
for n in range(260,266):
 a=np.array(Image.open(R/'assets/peak-v10-measure'/f'frame-{n:04d}.png').convert('RGB')).astype(float);reg=a[:350,800:1150];gray=(reg.min(2)>190)&(reg.max(2)<247)&(reg.max(2)-reg.min(2)<15);boxes=[b for b in comps(gray) if b[2]-b[0]>150 and b[3]-b[1]>30];G=max((b[3] for b in boxes),default=-25)-277
 blue=[b for b in comps((a[:,:,2]-a[:,:,0]>30)&(a[:,:,2]>180)) if b[2]-b[0]>400 and b[3]-b[1]>40];blueY=max(blue,key=lambda b:(b[2]-b[0])*(b[3]-b[1]))[1] if blue else 50
 if n==265:G=blueY-352
 insert(g,'y',n,G);insert(N['bubble-983'],'y',n,blueY-G)
 m=(a.min(2)>190)&(a.max(2)<246)&(a.max(2)-a.min(2)<15);grayBodies=[b for b in comps(m) if b[0]<600 and b[2]-b[0]>500 and b[3]-b[1]>45 and b[1]>300];replyY=grayBodies[0][1]-G if grayBodies else 616;insert(N['bubble-994'],'y',n,replyY)
 overlay=N[f'peak-phone-exit-overlay-{n}'];overlay['y']=-G;records.append(dict(frame=n,cameraY=G,sentLocalY=blueY-G,replyLocalY=replyY))
p['provenance'].append(dict(kind='independent source phone camera versus bubble exit',diagnosis='The old8.7 camera fallback lost the header and folded approximately33px of global movement into the sent/reply local coordinates. Fit the native Muse-pill bottom relative to its held277px anchor; keep actual sent/reply coordinates independent. Native white fade remains in world coordinates.',measurements=records));p['changed_frames']=[[259,269],[361,389]];P.write_text(json.dumps(p,indent=2));print('Independent phone camera exit',records,flush=True)
