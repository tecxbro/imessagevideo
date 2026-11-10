"""Single canonical late UI row artwork; measured native scroll/fade/blur."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d,gaussian_filter,map_coordinates
from scipy.signal import find_peaks
from scipy.fft import rfft,irfft,next_fast_len
D=Path(__file__).resolve().parent;A=D/'assets';F=D/'native-late-v19';snap=D.parent.parent/'outputs/06-gallery/final-v18';s=json.loads((snap/'scene.json').read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((snap/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s);images={f:np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32) for f in range(555,561)};ref=images[555];r,g,b=ref[:,410:600,0],ref[:,410:600,1],ref[:,410:600,2];profile=gaussian_filter1d((np.maximum(b-r-3,0)*(b-g>2)).sum(1),2);peaks,_=find_peaks(profile,distance=45,prominence=profile.max()*.06);energy=(255-ref[:,:610]).sum((1,2))+(255-ref[:,1260:]).sum((1,2));energy=gaussian_filter1d(energy,2);bounds=[0]
for p,q in zip(peaks[:-1],peaks[1:]):
 lo=int(p)+20;hi=int(q)-20;bounds.append(int(lo+np.argmin(energy[lo:hi])) if hi>lo else int((p+q)/2))
bounds.append(min(1080,int(peaks[-1])+65));phone=json.loads((D/'root-phone-exit-patch.json').read_text())['measurements']['nativeDarkHardwareTops'];fits={};assets=[];children=[]
for side,x0,x1,featureX in [('left',0,610,np.arange(390,606,4)),('right',1260,1920,np.arange(1300,1620,4))]:
 for i,(y0,y1) in enumerate(zip(bounds[:-1],bounds[1:])):
  art=ref[y0:y1,x0:x1].copy();T=(255-art[::2,featureX-x0]);H=len(T);TD=float(np.sum(T*T));rows=[]
  for f,image in images.items():
   if f==555:rows.append(dict(frame=f,y=0.,opacity=1.,blur=0.));continue
   predict=-1.14*(phone[str(f)]-phone['555']);startPred=y0+predict
   if y1+predict<-10:rows.append(dict(frame=f,y=predict,opacity=0.,blur=0.));continue
   source=255-image[::2,featureX];pad=80;source=np.pad(source,((pad,pad),(0,0),(0,0)));L=len(source);nfft=next_fast_len(L+H-1);SF=rfft(source,nfft,axis=0);E=np.convolve(np.sum(source*source,axis=(1,2)),np.ones(H),'valid');valid=np.arange(len(E));starts=(valid-pad)*2;selection=(starts>startPred-36)&(starts<startPred+36);best=None
   if not selection.any():rows.append(dict(frame=f,y=predict,opacity=0.,blur=0.));continue
   for sigma in [0,.5,1,2,3,4,6,8,12]:
    V=gaussian_filter(T,(sigma/2,sigma/4,0),mode='constant',cval=0);den=float(np.sum(V*V));dot=irfft(SF*rfft(V[::-1],nfft,axis=0),nfft,axis=0).sum((1,2))[H-1:L];amp=np.maximum(dot,0)/max(1,den);score=np.maximum(dot,0)**2/np.maximum(1,E*den);score[~selection]=-1;at=int(np.argmax(score));quality=float(score[at]);alpha=float(min(4,amp[at]));cost=1-quality
    if best is None or cost<best[0]:best=(cost,float(starts[at]-y0),alpha,sigma,quality)
   _,dy,alpha,sigma,quality=best
   if quality<.35:alpha=0.
   rows.append(dict(frame=f,y=dy,opacity=alpha,blur=sigma,quality=quality))
  fits[(side,i)]=rows;maximum=max(1,max(q['opacity'] for q in rows));strong=np.clip(255-(255-art)*maximum,0,255);alpha=(strong.min(2)<254).astype(np.uint8)*255;path=A/f'v19-email-exit-static555-{side}-row-{i:02}.png';Image.fromarray(np.dstack([np.uint8(strong),alpha])).save(path);assets.append(dict(path=str(path),source_frame=555,box=[x0,y0,x1,y1],kind='single bounded original late email UI row; internal copy bitmap; contrast normalized over white for native measured fading'))
  node=dict(type='group',id=f'email-v19-canonical555-{side}-row-{i}',children=[dict(type='image',id=f'email-v19-canonical555-{side}-row-{i}-art',src=str(path),x=x0,y=y0,width=x1-x0,height=y1-y0)],keyframes={'y':[dict(t=q['frame']/30,value=q['y'],ease='linear') for q in rows],'opacity':[dict(t=q['frame']/30,value=q['opacity']/maximum,ease='linear') for q in rows],'blur':[dict(t=q['frame']/30,value=q['blur'],ease='linear') for q in rows]});children.append(node)
# Middle UI is sampled once when its whole native row is exposed above the
# descending physical phone; no device or incoming heading enters the asset.
for i,(y0,y1) in enumerate(zip(bounds[:-1],bounds[1:])):
 l=fits[('left',i)];r=fits[('right',i)];rows=[dict(frame=f,y=(ll['y']+rr['y'])/2,opacity=(ll['opacity']+rr['opacity'])/2,blur=(ll['blur']+rr['blur'])/2) for f,ll,rr in zip(images,l,r)];capture=None
 for row in rows:
  if row['opacity']<.04:continue
  top=y0+row['y'];bottom=y1+row['y']
  if top>=0 and bottom<phone[str(row['frame'])]-15 and bottom<490:capture=row;break
 if capture is None:continue
 f=capture['frame'];yy,xx=np.mgrid[y0:y1,610:1260];wy=yy+capture['y'];sample=np.stack([map_coordinates(images[f][:,:,c],[wy,xx],order=1,mode='constant',cval=255) for c in range(3)],2);maximum=max(1,max(q['opacity'] for q in rows));baseA=capture['opacity']/maximum;strong=np.clip(255-(255-sample)/max(.01,baseA),0,255);alpha=(strong.min(2)<254).astype(np.uint8)*255
 if not alpha.any():continue
 path=A/f'v19-email-exit-static555-middle-row-{i:02}.png';Image.fromarray(np.dstack([np.uint8(strong),alpha])).save(path);assets.append(dict(path=str(path),source_frame=f,canonical_box=[610,y0,1260,y1],sample_translation=capture['y'],kind='single bounded original email UI row, acquired only while exposed above physical phone; no foreground device/heading; native measured exit'))
 node=dict(type='group',id=f'email-v19-canonical555-middle-row-{i}',children=[dict(type='image',id=f'email-v19-canonical555-middle-row-{i}-art',src=str(path),x=610,y=y0,width=650,height=y1-y0)],keyframes={'y':[dict(t=q['frame']/30,value=q['y'],ease='linear') for q in rows],'opacity':[dict(t=q['frame']/30,value=q['opacity']/maximum,ease='linear') for q in rows],'blur':[dict(t=q['frame']/30,value=float(np.sqrt(max(0,q['blur']**2-capture['blur']**2))),ease='linear') for q in rows]});children.append(node)
g=dict(type='group',id='email-v19-measured-exit',start=555/30,end=561/30,children=children);idx=next(i for i,q in enumerate(s['layers']) if q['id']=='measured-email-panes-v13')+1;s['layers'].insert(idx,g);(D/'email-exit-v19-patch.json').write_text(json.dumps(dict(insert_after='measured-email-panes-v13',layers=[g]),indent=2));(D/'email-exit-static555-v19-measurements.json').write_text(json.dumps(dict(bounds=bounds,rows={str(k):v for k,v in fits.items()}),indent=2));(A/'email-exit-static555-v19-provenance.json').write_text(json.dumps(assets,indent=2));(D/'scene-email-exit-v19.json').write_text(json.dumps(s,indent=2)+'\n');print('rows',bounds,'nodes',len(children))
