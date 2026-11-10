"""Measure actual title68–69 continuation and unmix late icon halos from blurred black copy."""
from pathlib import Path
from functools import lru_cache
import ast,json,hashlib,numpy as np
from PIL import Image
from scipy import ndimage,signal
R=Path('/workspace/imessage-recreations');REF=R/'references/02-danieltian';P=R/'verification/fidelity-review/02-intro';AS=REF/'assets/intro797-review';names={'frame','alpha','bbox','energy','fit'};tree=ast.parse((REF/'build-intro797-review.py').read_text());exec(compile(ast.Module(body=[q for q in tree.body if isinstance(q,ast.FunctionDef) and q.name in names],type_ignores=[]),'pure-fit-functions','exec'),globals())
s=json.loads((REF/'intro797-review-elements.json').read_text());roi=[150,400,1770,700];A=alpha(30,roi);core=bbox(A>.5);A=A[core[1]-3:core[3]+3,core[0]-3:core[2]+3];ax=roi[0]+core[0]-3;ay=roi[1]+core[1]-3;obs=s['measurements']['late-camera']
for f in [68,69]:
 T=alpha(f,[150,340,1770,820]);best=None
 for sc in (np.arange(.43,.641,.03) if f==68 else np.arange(.25,.531,.04)):
  for sig in ([10,12,14,16,18,20] if f==68 else [16,20,24,28,32,36]):
   q=fit(T,float(sc),float(sig))
   if q and (best is None or q['correlation']>best['correlation']):best=q
 csc,csig=best['s'],best['sigma']
 for sc in np.arange(csc-.025,csc+.026,.01):
  for sig in np.arange(csig-2,csig+2.01,1):
   q=fit(T,float(sc),float(sig))
   if q and q['correlation']>best['correlation']:best=q
 obs.append(dict(frame=f,**best));print('tail',f,best,flush=True)
late=next(q for q in s['replacement']['children'] if q['id']=='intro797-late-camera');late['end']=70/30;late['keyframes']={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','blur','opacity']};s['replacement']['end']=70/30;s['changed_frame_ranges']=[[0,69]];s['gate_overrides']={'group-801':{'start':70/30}};ledger=[]
# Gray letter blur overlaps the icon crop at the exit. Remove the measured black
# contribution before extracting a bounded original color/icon layer.
for q in obs:
 f=q['frame'];sig=q['sigma'];w=round(A.shape[1]*q['scaleX']);h=round(A.shape[0]*q['scaleY']);M=np.asarray(Image.fromarray(A,'F').resize((w,h),Image.Resampling.BILINEAR));pad=int(3*sig)+2;M=np.pad(M,pad);M=ndimage.gaussian_filter(M,sig,mode='constant') if sig else M;px=round(q['x']+ax*q['scaleX']-pad);py=round(q['y']+ay*q['scaleY']-pad);word=np.zeros((1080,1920),dtype='float32');x0=max(0,px);y0=max(0,py);x1=min(1920,px+M.shape[1]);y1=min(1080,py+M.shape[0]);word[y0:y1,x0:x1]=M[y0-py:y1-py,x0-px:x1-px]*q['opacity'];a=frame(f);D=np.maximum(0,255-a-word[:,:,None]*255)
 for name,cx,cy in [('messages',415,605),('group',1018,603)]:
  ex=q['x']+q['scaleX']*cx;ey=q['y']+q['scaleY']*cy;rad=75*q['scaleX']+3*sig+12;b=[max(150,round(ex-rad)),max(400,round(ey-rad)),min(1770,round(ex+rad)),min(730,round(ey+rad))];z=a[b[1]:b[3],b[0]:b[2]];ch=z.max(2)-z.min(2);m=((z[:,:,1]-z[:,:,0]>4)&(z[:,:,1]-z[:,:,2]>2)) if name=='messages' else (ch>4)
  bb=bbox(m,b[0],b[1]);
  if not bb:continue
  margin=max(8,int(2*sig));bb=[max(b[0],bb[0]-margin),max(b[1],bb[1]-margin),min(b[2],bb[2]+margin),min(b[3],bb[3]+margin)];d=D[bb[1]:bb[3],bb[0]:bb[2]];al=d.max(2)/255;al[al<2/255]=0;v=255-d;rgb=np.where(al[:,:,None]>0,(v-255*(1-al[:,:,None]))/np.maximum(1e-5,al[:,:,None]),0);rgba=np.concatenate((np.clip(rgb,0,255),al[:,:,None]*255),2).round().astype('uint8');p=AS/f'{name}-late-unmixed-{f}.png';Image.fromarray(rgba).save(p);id=f'intro797-icon-{name}-{f}';n=dict(type='image',id=id,src=str(p),x=bb[0],y=bb[1],width=bb[2]-bb[0],height=bb[3]-bb[1],start=f/30,end=(f+1)/30,sourceFrame=f,sourceBounds=bb,semanticText='Messages icon' if name=='messages' else 'Spinning Group Chats spheres',editability='Bounded isolated original3D icon pose; measured black-copy blur removed to avoid double compositing. Native pose/lifetime, bitmap internals.');s['replacement']['children']=[c for c in s['replacement']['children'] if c['id']!=id]+[n];ledger.append(dict(id=id,sourceFrame=f,sourceBounds=bb,asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceSHA256=hashlib.sha256((P/'source'/f'{f+1:04d}.png').read_bytes()).hexdigest(),notice=n['editability']))
s['assets']+=ledger;s['notice']+=' Source68–69 measured title continuation; group801 composer is gated to70 to remove premature plus/white overlay only within intro. Late icon extraction removes neutral black-copy blur before compositing.';(REF/'intro797-review-elements.json').write_text(json.dumps(s,indent=2));(REF/'intro797-tail-provenance.json').write_text(json.dumps(ledger,indent=2));print('tail icons',len(ledger))
