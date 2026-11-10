"""Close four explicitly inspected small-food states below stable SIFT resolution.
Changes four native poses only; original Apple asset remains unchanged.
"""
from pathlib import Path
from PIL import Image
import sys,json,copy,numpy as np,math
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
R=Path(__file__).resolve().parents[1];D=R/'food-orbit-measure';P=R/'food-orbit-proposals.json';s=json.loads(P.read_text());data=json.loads((D/'food-refined-measurements.json').read_text());img=np.array(Image.open(R/'assets/apple-pizza.png').convert('RGBA'));H,W=img.shape[:2];rr=img[:,:,0].astype(float);gg=img[:,:,1].astype(float);bb=img[:,:,2].astype(float);mask=(rr>100)&(rr-gg>12)&(rr-bb>30)&(img[:,:,3]>220);yy,xx=np.where(mask);colorPoints=np.stack([xx+.5,yy+.5],1);records=[]
verified=[('authentic-food-pizza-top',731,[776,56,788,70],'color',732),('authentic-food-pizza-left',732,[554,236,564,248],'color',733),('authentic-food-pizza-tiny-right',735,[1251,110,1264,125],'full',737),('authentic-food-pizza-tiny-right',736,[1266,78,1308,128],'color',737)]
def setkey(node,k,n,v):
 ks=node['keyframes'][k];q=next(q for q in ks if round(q['t']*30)==n);q['value']=float(v)
def rot(x):return np.array([[math.cos(x),-math.sin(x)],[math.sin(x),math.cos(x)]])
for id,n,b,mode,refn in verified:
 actor=next(a for a in s['provenance']['roots'] if a['id']==id);oldrow=next(q for q in actor['measurements'] if q['n']==refn);ref=min([m for m in data[str(refn)] if m['kind']=='pizza'],key=lambda m:np.linalg.norm(np.array(m['center'])-[oldrow['x'],oldrow['y']]));A=np.array(ref['matrix'])[:,:2];points=np.array([[0,0],[W,0],[W,H],[0,H]]) if mode=='full' else colorPoints;project=points@A.T;span=np.ptp(project,axis=0);targetSpan=np.array([b[2]-b[0],b[3]-b[1]],float) if mode=='full' else np.array([b[2]-b[0]-1,b[3]-b[1]-1],float);B=np.diag(targetSpan/span)@A;low=(points@B.T).min(0);translation=np.array(b[:2],float)+(0 if mode=='full' else .5)-low;M=np.column_stack([B,translation]);center=M@[W/2,H/2,1]
 # Fit actual tiny-actor contrast over the native near-white stage.
 source=np.array(Image.open(R/'lunch-native'/f'{n-609:03d}.png').convert('RGB'));corn=np.array([[0,0,1],[W,0,1],[W,H,1],[0,H,1]])@M.T;l=max(0,int(np.floor(corn[:,0].min()))-2);t=max(0,int(np.floor(corn[:,1].min()))-2);r=min(1920,int(np.ceil(corn[:,0].max()))+2);bot=min(1080,int(np.ceil(corn[:,1].max()))+2);local=M.copy();local[:,2]-=[l,t];warped=cv2.warpAffine(img,local,(r-l,bot-t));sel=warped[:,:,3]>220;paint=warped[:,:,:3][sel].astype(float);obs=source[t:bot,l:r][sel].astype(float);v=253-paint;alpha=float(np.clip(np.sum(v*(253-obs))/max(1,np.sum(v*v)),0,1));error=float(np.mean(abs(253-v*alpha-obs)))
 U,sv,V=np.linalg.svd(B)
 if np.linalg.det(U)<0:U[:,1]*=-1;sv[1]*=-1
 if np.linalg.det(V)<0:V[1,:]*=-1;sv[1]*=-1
 u=math.degrees(math.atan2(U[1,0],U[0,0]));vAngle=math.degrees(math.atan2(V[1,0],V[0,0]));prev=next(q for q in actor['measurements'] if q['n']==n);choices=[]
 for swap in [False,True]:
  a,c=(u,vAngle) if not swap else(u+90,vAngle-90);sigma=sv if not swap else sv[::-1]
  for k in range(-3,4):
   aa,cc=a+180*k,c-180*k;choices.append((abs(aa-prev['rotation'])+abs(cc-prev['innerRotation']),aa,cc,sigma))
 _,u,vAngle,sigma=min(choices,key=lambda q:q[0]);values=dict(x=center[0],y=center[1],rotation=u,scaleX=sigma[0],scaleY=sigma[1],opacity=alpha,innerRotation=vAngle);node=s['replacements'][id]
 for key,val in values.items():
  if key=='innerRotation':setkey(node['children'][0],'rotation',n,val)
  else:setkey(node,key,n,val)
 prev.update({k:float(v) for k,v in values.items()});prev['verifiedTinySourceBounds']=b
 if n not in actor['observedFrames']:actor['observedFrames']=sorted(actor['observedFrames']+[n])
 actor['interpolatedFrames']=[k for k in actor['interpolatedFrames'] if k!=n];model=dict(kind='pizza',matrix=M.tolist(),center=center.tolist(),corners=corn.tolist(),inliers=0,fitMAE=error,opacity=alpha,verifiedTinySourceBounds=b,measurement='Native colored-support observation; orientation from the immediately adjacent verified original-asset pose. Full source735 outer bounds are independently measured.')
 data[str(n)].append(model);records.append(dict(id=id,frame=n,sourceBounds=b,boundsKind=mode,opacity=alpha,fitMAE=error,matrix=M.tolist()))
s['provenance']['verifiedTinyStates']=records;P.write_text(json.dumps(s,indent=2));(D/'food-refined-measurements.json').write_text(json.dumps(data,indent=2));(D/'verified-tiny-food-states.json').write_text(json.dumps(records,indent=2))
scene=json.loads((R/'food-orbit-prototype.scene.json').read_text());scene['layers']=[copy.deepcopy(s['replacements'].get(q['id'],q)) for q in scene['layers']];(R/'food-orbit-prototype-v2.scene.json').write_text(json.dumps(scene,indent=2));print('Verified four tiny poses',records,flush=True)
