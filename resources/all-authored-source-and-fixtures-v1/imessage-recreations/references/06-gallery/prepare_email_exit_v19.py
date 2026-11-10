"""Independent measured static email-row exit555–560; preserve all<=554 art."""
from pathlib import Path
import copy,json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.fft import rfft,irfft,next_fast_len
D=Path(__file__).resolve().parent;A=D/'assets';F=D/'native-late-v19';snap=D.parent.parent/'outputs/06-gallery/final-v18';s=json.loads((snap/'scene.json').read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((snap/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s);old=next(q for q in s['layers'] if q['id']=='measured-email-panes-v13');nodes={q['id']:q for q in old['children']};centers=[8,104,192,278,364,450,538,626,714,802,890,978,1066,1154,1242,1330];frames=range(555,561);images={f:np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32) for f in frames};sx=next(iter(nodes.values()))['keyframes']['scaleX'][-1]['value'];dx=960*(1-sx);rows={};fits={};candidates={};templates={}
for side in ['left','right']:
 worldX=np.arange(400,612,4) if side=='left' else np.arange(1300,1584,4)
 for i,cy in enumerate(centers):
  name=f'email-v18-{side}-row-{i}';node=nodes.get(name)
  if node is None:continue
  image=node['children'][0];rgba=np.array(Image.open(image['src']).convert('RGBA')).astype(np.float32);ar=rgba[:,:,:3]*(rgba[:,:,3:]/255)+255*(1-rgba[:,:,3:]/255);ys,xs=np.mgrid[0:ar.shape[0],0:len(worldX)];xx=(worldX-dx)/sx-image['x'];sample=np.stack([map_coordinates(ar[:,:,c],[ys,np.broadcast_to(xx,ys.shape)],order=1,mode='constant',cval=255) for c in range(3)],2);energy=(255-sample).sum((1,2));valid=np.where(energy>energy.max()*.06)[0]
  if not len(valid):continue
  c0=max(0,int(valid.min())-3);c1=min(ar.shape[0],int(valid.max())+4);H=max(2,round((c1-c0)*sx/2));ty=np.arange(H)*2/sx+c0;yy,xx0=np.meshgrid(ty,xx,indexing='ij');T=np.stack([255-map_coordinates(ar[:,:,c],[yy,xx0],order=1,mode='constant',cval=255) for c in range(3)],2);TD=float(np.sum(T*T));templates[(side,i)]=dict(T=T,TD=TD,worldX=worldX,c0=c0,canonStart=image['y']+c0,ar=ar,image=image,node=node)
  for f in frames:
   source=255-images[f][::2,worldX];L=len(source);nfft=next_fast_len(L+H-1);dot=irfft(rfft(source,nfft,axis=0)*rfft(T[::-1],nfft,axis=0),nfft,axis=0).sum((1,2))[H-1:L];E=np.convolve(np.sum(source*source,axis=(1,2)),np.ones(H),'valid');score=np.maximum(dot,0)**2/np.maximum(1,E*TD);amp=np.maximum(dot,0)/max(1,TD);rank=np.argsort(score)[::-1];selected=[]
   for at in rank:
    if any(abs(int(at)-r['at'])<12 for r in selected):continue
    selected.append(dict(at=int(at),start=float(at*2),score=float(score[at]),opacity=float(min(1.1,amp[at])),pointY=float(at*2-sx*(image['y']+c0-cy))))
    if len(selected)==5:break
   candidates[(f,side,i)]=selected
print('templates',len(templates),flush=True)
prevSY=.911;prevDY=-258.;camera=[]
for f in frames:
 points=[(i,centers[i],q['pointY'],q['score'],q['opacity']) for (ff,side,i),cs in candidates.items() if ff==f and side=='right' for q in cs if q['score']>.18 and q['opacity']>.025];best=None
 for a in points:
  for b in points:
   if b[0]<=a[0]:continue
   sy=(b[2]-a[2])/(b[1]-a[1]);dy=a[2]-sy*a[1]
   if not(.45<sy<1.18 and -1900<dy<prevDY+10):continue
   scores={}
   for i,x,y,quality,amp in points:scores[i]=max(scores.get(i,0),quality*np.exp(-((y-(dy+sy*x))/15)**2))
   value=sum(scores.values())-.015*((sy-prevSY)/.1)**2
   if best is None or value>best[0]:best=(value,sy,dy)
 if best is None:sy=prevSY;dy=prevDY-200
 else:_,sy,dy=best
 prevSY,prevDY=sy,dy;camera.append(dict(frame=f,sx=sx,sy=sy,dx=dx,dy=dy,consensus=best[0] if best else 0));print('camera',f,round(sy,3),round(dy,1),flush=True)
 for (side,i),t in templates.items():
  cy=centers[i];predict=dy+sy*cy+sx*(t['canonStart']-cy);cs=candidates[(f,side,i)];choices=[q for q in cs if abs(q['start']-predict)<32];q=max(choices,key=lambda q:q['score']) if choices else None;opacity=0.;start=predict;blur=0.
  if q is not None:
   start=q['start'];source=255-images[f][::2,t['worldX']];at=q['at'];T=t['T'];target=source[at:at+len(T)];bestBlur=None
   for sigma in [0,.5,1,2,3,4,6,8]:
    V=gaussian_filter(T,(sigma/2,sigma/4,0),mode='constant',cval=0);den=float(np.sum(V*V));dot=float(np.sum(V*target));amp=float(np.clip(dot/max(1,den),0,1));cost=float(np.sum((target-amp*V)**2));quality=dot*dot/max(1,float(np.sum(target*target))*den)
    if bestBlur is None or cost<bestBlur[0]:bestBlur=(cost,sigma,amp,quality)
   _,blur,opacity,quality=bestBlur
   if quality<.22:opacity=0.
  translation=start-sx*t['canonStart'];fits.setdefault((side,i),[]).append(dict(frame=f,x=dx,y=translation,scale=sx,opacity=opacity,blur=blur/sx))
# Left fields may contain the incoming title; a vanished right-hand identity
# cannot spawn an unrelated left list row over that title.
for (side,i),rs in fits.items():
 if side=='left' and ('right',i) in fits:
  for r,rr in zip(rs,fits[('right',i)]):r['opacity']=min(r['opacity'],rr['opacity']*1.5+.025)
# Extend only missing static middle-row artwork from exposed UI after the phone
# descends. Never include its hardware, text, or the new heading in those assets.
phoneTops=json.loads((D/'root-phone-exit-patch.json').read_text())['measurements']['nativeDarkHardwareTops'];new=[];provenance=[]
for (side,i),rs in list(fits.items()):
 node=copy.deepcopy(templates[(side,i)]['node']);node['id']=f'email-v19-exit-{side}-row-{i}';node.pop('yCorrections',None);node['children'][0]['id']=node['id']+'-art';node['keyframes']={k:[dict(t=r['frame']/30,value=r[v],ease='linear') for r in rs] for k,v in [('x','x'),('y','y'),('scaleX','scale'),('scaleY','scale'),('opacity','opacity'),('blur','blur')]};new.append(node)
for i,cy in enumerate(centers):
 available=[fits[(side,i)] for side in ['left','right'] if (side,i) in fits]
 if not available:continue
 rs=[dict(frame=f,x=dx,y=float(np.mean([z[j]['y'] for z in available])),scale=sx,opacity=float(np.mean([z[j]['opacity'] for z in available])),blur=float(np.mean([z[j]['blur'] for z in available]))) for j,f in enumerate(frames)];owner=templates.get(('left',i),templates.get(('right',i)));child=owner['image'];y0=child['y'];h=child['height'];w=628;x0=622;ar=np.full((h,w,3),255,np.float32);captured=np.zeros((h,w),bool);oldMid=nodes.get(f'email-v18-middle-row-{i}')
 if oldMid:
  rgba=np.array(Image.open(oldMid['children'][0]['src']).convert('RGBA')).astype(np.float32);ar=rgba[:,:,:3];captured=rgba[:,:,3]>0
 yy,xx=np.mgrid[y0:y0+h,x0:x0+w];sources=[]
 for r in rs:
  if r['opacity']<.04:continue
  f=r['frame'];wx=sx*xx+dx;wy=sx*yy+r['y'];top=phoneTops[str(f)]-12;valid=(wx>=0)&(wx<1919)&(wy>=0)&(wy<1079)&((wy<top)|(wx<615)|(wx>1250))&~captured
  if f>=556:valid&=~((wy>430)&(wy<650))
  if not valid.any():continue
  for c in range(3):
   value=map_coordinates(images[f][:,:,c],[wy[valid],wx[valid]],order=1);ar[:,:,c][valid]=np.clip(255-(255-value)/r['opacity'],0,255)
  captured|=valid;sources.append(f)
 alpha=(ar.min(2)<253)&captured
 if not alpha.any():continue
 path=A/f'v19-email-exit-middle-row-{i:02}.png';Image.fromarray(np.dstack([np.uint8(ar),alpha.astype(np.uint8)*255])).save(path);node=dict(type='group',id=f'email-v19-exit-middle-row-{i}',children=[dict(type='image',id=f'email-v19-exit-middle-row-{i}-art',src=str(path),x=x0,y=y0,width=w,height=h)],keyframes={k:[dict(t=r['frame']/30,value=r[v],ease='linear') for r in rs] for k,v in [('x','x'),('y','y'),('scaleX','scale'),('scaleY','scale'),('opacity','opacity')]});new.append(node);provenance.append(dict(path=str(path),source_frames=sources,kind='single static bounded email UI middle-row, only original UI exposed above/beside actual phone; title and hardware excluded; native independent exit camera'))
g=dict(type='group',id='email-v19-measured-exit',start=555/30,end=561/30,children=new);idx=next(i for i,q in enumerate(s['layers']) if q['id']==old['id'])+1;s['layers'].insert(idx,g);(D/'email-exit-v19-patch.json').write_text(json.dumps(dict(insert_after='measured-email-panes-v13',layers=[g]),indent=2));(D/'email-exit-v19-measurements.json').write_text(json.dumps(dict(camera=camera,rows={str(k):v for k,v in fits.items()}),indent=2));(A/'email-exit-v19-provenance.json').write_text(json.dumps(provenance,indent=2));(D/'scene-email-exit-v19.json').write_text(json.dumps(s,indent=2)+'\n');print('wrote',len(new),'row segments')
