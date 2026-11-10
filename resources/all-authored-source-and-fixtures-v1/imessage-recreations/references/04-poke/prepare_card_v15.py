"""Freeze source card poses and independently measured header material field."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v14/scene.json').read_text());fps=s['fps'];scale=.48828125;early=json.loads((p/'measurements-v8/selected-photo-scale-v15.json').read_text());title=json.loads((p/'measurements-v8/selected-header-title-v15.json').read_text());late=json.loads((p/'measurements-v8/selected-header-title-late-v15.json').read_text());localy=title['title_local_origin'][1];by={r['frame']:r['source']for r in title['measurements']};by.update({r['frame']:r['source']for r in late['measurements']});poses=[]
for n in range(734,800):
 if n<=736:
  photo=next(r['best']['photo_y']for r in early['measurements']if r['frame']==n);y=photo-17*scale;method='Opaque original thumbnail, native69x70 correlation >.975; scale interval supports original.48828125.'
 elif n==753:
  y=((294-17*scale)+(314-localy*scale))/2;method='Partly foreground-occluded. Independent red photo and title estimates agree within.14px; position uncertainty about1px.'
 elif n<=788:
  r=by[n];assert r['correlation']>.7,(n,r);y=r['title_ink_y']-localy*scale;method='Original visible title tail registered with foreground masks; source pose includes independent scroll.'
 else:y=poses[-1]['y'];method='Source content absent from789. Retained position is an inactive diagnostic horizon only; full actor ends789 after the799regression control rejected background persistence.'
 poses.append(dict(frame=n,time=n/fps,x=664.0,y=float(y),scaleX=scale,scaleY=scale,method=method))
(p/'measurements-v8/selected-card-camera-v15.json').write_text(json.dumps(dict(source_scale_interval=[.486,.493],chosen_scale=scale,source_scale_reason='Actual69x70thumbnail projection; original compact UI scale is125/256. Candidate control matches at its expected poses before any source change.',source_last_confirmed_title_frame=788,first_title_absence=789,content_end=789/fps,body_end=789/fps,measurements=poses),indent=2))
# A clean earlier screen is essential: late789 still contains the gray body,
# despite its title disappearing, so it cannot be a no-card background sample.
bg=np.median([np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(float)for n in[720,721,722]],axis=0)[:,940:1000].mean(1);fg=np.array([227.,228.,231.]);den=255-fg;observations={};details=[]
for pose in poses:
 n=pose['frame']
 if n>788:continue
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(float);ys=np.arange(round(pose['y'])+15,round(pose['y'])+76);rgb=a[ys,940:1000].mean(1);T=((bg[ys]-rgb)*den).sum(1)/(den*den).sum()
 for y,v in zip(ys,T):observations.setdefault(int(y),[]).append(float(v))
 details.append(dict(frame=n,first_y=int(ys[0]),last_y=int(ys[-1]),transparency_median=float(np.median(T))))
y=np.array(sorted(observations));raw=np.array([np.median(observations[int(v)])for v in y]);weights=np.array([len(observations[int(v)])for v in y]);raw=gaussian_filter1d(np.clip(raw,0,.94),2)
# Weighted PAVA enforces only the physical monotonic gradient, no frame pose.
blocks=[]
for i,(v,w)in enumerate(zip(raw,weights)):
 blocks.append([i,i,float(v*w),float(w)])
 while len(blocks)>1 and blocks[-2][2]/blocks[-2][3]>blocks[-1][2]/blocks[-1][3]:
  b=blocks.pop();a=blocks.pop();blocks.append([a[0],b[1],a[2]+b[2],a[3]+b[3]])
fit=np.zeros_like(raw)
for a,b,total,w in blocks:fit[a:b+1]=total/w
header=next(g for g in s['layers']if g['id']=='p0298');from v8_utils import at
t=758/fps;gy=at(header,'y',t);sy=at(header,'scaleY',t);bottom=float(y.max()+30);height=(bottom-gy)/sy;stops=[];samples=[]
for yy in[gy,*range(int(y.min()),int(y.max())+1,8),float(y.max()),bottom]:
 if yy<y.min():T=0.
 elif yy<=y.max():T=float(np.interp(yy,y,fit))
 else:T=1.
 opacity=1-T;B=np.array([np.interp(yy,np.arange(len(bg)),bg[:,c])for c in range(3)]);color=np.clip(np.rint((B-T*255)/max(.0001,opacity)),0,255).astype(int)if opacity>.001 else np.array([255,255,255]);stops.append(dict(offset=f'{100*(yy-gy)/(bottom-gy):.6f}%',color='#'+''.join(f'{v:02x}'for v in color),opacity=float(opacity)));samples.append(dict(native_y=float(yy),transparency=T,clean_background=B.tolist(),color=color.tolist(),opacity=opacity))
gradient=dict(id='small-header-glass-v15',type='linear',x1='0%',y1='0%',x2='0%',y2='100%',stops=stops)
(p/'measurements-v8/header-material-v15.json').write_text(json.dumps(dict(method='Independent source gray-card material field. Original720–722clean screen baseline; source702gray foreground. Per-row x940:1000flat card samples at measured bodyY+15:75; title/photo excluded. Median observations and weighted monotonic PAVA fit transparency; native gradient color solves clean source screen color over255base. No source image is an output layer.',header_reference_y=gy,header_reference_scale=sy,height=height,gradient=gradient,samples=samples,per_frame=details),indent=2));print('camera',len(poses),'field',int(y.min()),int(y.max()),'height',height,'stops',len(stops));print([(v['native_y'],round(v['opacity'],3),v['color'])for v in samples[::5]])
