"""Static bounded email UI rows with measured independent reveal/spacing cameras."""
from pathlib import Path
import json
from functools import lru_cache
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
D=Path(__file__).resolve().parent;F=D/'native-transition-v18';A=D/'assets';s=json.loads((D/'scene-combined-handoff-v18.json').read_text())
@lru_cache(maxsize=64)
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
ref=load(540);provenance=[]
def colors(a):
 r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];xx=np.arange(1920)[None,:];roi=(xx>300)&(xx<606);out={}
 for name,mask,weight in [('pink',(r-g>8)&(r-b>2)&(b-g>5),r-g),('orange',(r-g>8)&(g-b>5),r-b),('green',(g-r>5)&(g-b>2),g-r)]:
  weights=np.maximum(weight-5,0)*mask*roi;py=weights.sum(1);px=weights.sum(0)
  if py.sum()<100:continue
  yy=np.where(py>py.max()*.15)[0];xs=np.where(px>px.max()*.1)[0]
  out[name]={'cy':float(np.dot(np.arange(1080),py)/py.sum()),'top':int(yy.min()),'bottom':int(yy.max()+1),'left':int(xs.min()),'energy':float(py.sum())}
 return out
cr=colors(ref);poses=[];lastsy=1.
for f in range(518,555):
 c=colors(load(f));pairs=[(cr[k]['cy'],v['cy']) for k,v in c.items() if v['top']>1 and v['bottom']<1079 and (f<545 or k!='pink')]
 if len(pairs)>=2:
  z=np.array(pairs);sy,dy=np.linalg.lstsq(np.c_[z[:,0],np.ones(len(z))],z[:,1],rcond=None)[0];lastsy=sy
 else:
  sy=lastsy;k='green' if 'green'in c else next(iter(c));dy=c[k]['bottom']-sy*cr[k]['bottom']
 ratios=[(960-v['left'])/(960-cr[k]['left']) for k,v in c.items() if k=='green' and v['top']>1];sx=float(np.median(ratios)) if ratios else (poses[-1]['sx'] if poses else 1.04);poses.append({'frame':f,'sx':sx,'sy':float(sy),'dy':float(dy),'dx':960*(1-sx),'colors':c})
by={r['frame']:r for r in poses};centers=[8,104,192,278,364,450,538,626,714,802,890,978,1066,1154,1242,1330];bands=[]
for side,x0,x1 in [('left',0,622),('right',1250,1920),('middle',622,1250)]:
 for i,cy in enumerate(centers):
  y0=0 if i==0 else round((centers[i-1]+cy)/2);y1=round((cy+centers[i+1])/2) if i+1<len(centers) else 1374;h=y1-y0;w=x1-x0
  captured=None
  if side=='middle':
   ar=np.full((h,w,3),255,np.float32);captured=np.zeros((h,w),bool);yy,xx=np.mgrid[y0:y1,x0:x1];sources=[]
   for f in range(540,555):
    p=by[f];source=load(f);wide=(source[:,850:1070].max(2)<105).sum(1)>190;rim=np.where(wide)[0];top=float(rim[0]-15) if len(rim) else -1
    profile=source[int(max(0,top+150)):1000].mean((0,2));dark=np.where((profile<150)&(np.arange(1920)>450)&(np.arange(1920)<1450))[0];left=float(dark.min()-15) if len(dark) else 600.;right=float(dark.max()+15) if len(dark) else 1280.
    owners=[q for q in bands if q['id'] in [f'email-v18-left-row-{i}',f'email-v18-right-row-{i}']];j=f-518;delta=float(np.mean([q['yCorrections'][j]['value'] for q in owners])) if owners else 0.
    wx=p['sx']*xx+p['dx'];wy=p['sx']*(yy-cy)+p['dy']+p['sy']*cy+delta;valid=(wy>=0)&((wy<top)|(wx<left)|(wx>right))&(wx>=0)&(wx<1919)&~captured
    if not valid.any():continue
    for c in range(3):ar[:,:,c][valid]=map_coordinates(source[:,:,c],[wy[valid],wx[valid]],order=1)
    captured|=valid;sources.append(f)
   sourceframe=sources
  elif y1<=1080:ar=ref[y0:y1,x0:x1].copy();sourceframe=540
  else:
   p=by[554];yy,xx=np.mgrid[y0:y1,x0:x1];sx=p['sx'];worldx=sx*xx+p['dx'];worldy=sx*(yy-cy)+p['dy']+p['sy']*cy;source=load(554);ar=np.stack([map_coordinates(source[:,:,c],[worldy,worldx],order=1,mode='constant',cval=255) for c in range(3)],2);sourceframe=554
  # White source background is discarded, preserving every original UI color.
  alpha=(ar.min(2)<253).astype(np.uint8)*255
  if captured is not None:alpha*=captured
  if not alpha.any():continue
  rgba=np.dstack([np.uint8(ar),alpha]);path=A/f'v18-email-{side}-row-{i:02}.png';Image.fromarray(rgba).save(path)
  provenance.append({'path':str(path),'source_frame':sourceframe,'canonical_band':[x0,y0,x1,y1],'kind':'bounded static email-list UI row segment; internal text bitmap; independent camera/reveal'})
  # Estimate each row's reveal amplitude against the same static UI identity.
  yy,xx=np.mgrid[0:h:3,0:w:3];tp=np.maximum(0,252-ar[::3,::3]);mask=np.ones(tp.shape[:2],bool)
  # Keep fitting away from the actual phone's edge throughout its native camera.
  mask&=((xx+x0)<590) if side=='left' else ((xx+x0)>1280)
  xx=xx[mask]+x0;yy=yy[mask]+y0;t=tp[mask];den=np.sum(t*t);opacity=[];corrections=[]
  for p in poses:
   wx=p['sx']*xx+p['dx'];wy=p['sx']*(yy-cy)+p['dy']+p['sy']*cy;valid=(wx>=0)&(wx<1919)&(wy>=0)&(wy<1079);a=load(p['frame']);obs=np.maximum(0,252-np.stack([map_coordinates(a[:,:,c],[wy[valid],wx[valid]],order=1) for c in range(3)],1));value=float(np.clip(np.sum(obs)/max(1,np.sum(t[valid])),0,1)) if valid.sum()>5 else 0.;delta=0.
   if side!='middle' and value>.2 and y0*p['sx']+p['dy']+(p['sy']-p['sx'])*cy>22 and y1*p['sx']+p['dy']+(p['sy']-p['sx'])*cy<1058:
    # Match each static row's vertical silhouette independently; the two sides
    # have slightly different perspective/curvature under the real fan camera.
    cols=np.arange(w);cols=cols[(cols+x0<590) if side=='left' else (cols+x0>1280)];template=np.maximum(0,252-ar[:,cols]).mean(1);hh=int(round(h*p['sx']));tt=np.stack([np.interp(np.arange(hh)/p['sx'],np.arange(h),template[:,c]) for c in range(3)],1);start=y0*p['sx']+p['dy']+(p['sy']-p['sx'])*cy;starts=np.arange(round(start)-20,round(start)+21);yl=np.arange(starts.min(),starts.max()+hh);xworld=p['sx']*(cols+x0)+p['dx'];ys,xs=np.meshgrid(yl,xworld,indexing='ij');profile=np.maximum(0,252-np.stack([map_coordinates(a[:,:,c],[ys,xs],order=1) for c in range(3)],2)).mean(1);windows=np.stack([profile[z:z+hh] for z in range(41)]);dots=np.sum(windows*tt,axis=(1,2));energy=np.sum(windows*windows,axis=(1,2));err=np.maximum(0,energy-dots*dots/max(1,np.sum(tt*tt)))/np.maximum(energy,1);at=int(np.argmin(err));delta=float(starts[at]-start);value=float(np.clip(np.sum(windows[at])/max(1,np.sum(tt)),0,1))
   opacity.append({'t':p['frame']/30,'value':value,'ease':'linear'});corrections.append({'t':p['frame']/30,'value':delta,'ease':'linear'})
  if side=='middle':
   left=next((q for q in bands if q['id']==f'email-v18-left-row-{i}'),None);right=next((q for q in bands if q['id']==f'email-v18-right-row-{i}'),None);available=[q for q in [left,right] if q]
   if available:
    opacity=[{'t':p['frame']/30,'value':float(np.mean([q['keyframes']['opacity'][j]['value'] for q in available])),'ease':'linear'} for j,p in enumerate(poses)]
    corrections=[{'t':p['frame']/30,'value':float(np.mean([q['yCorrections'][j]['value'] for q in available])),'ease':'linear'} for j,p in enumerate(poses)]
  child=dict(type='image',id=f'email-v18-{side}-row-{i}-art',src=str(path),x=x0,y=y0,width=w,height=h)
  node=dict(type='group',id=f'email-v18-{side}-row-{i}',children=[child],yCorrections=corrections,keyframes={'x':[{'t':p['frame']/30,'value':p['dx']} for p in poses],'y':[{'t':p['frame']/30,'value':p['dy']+(p['sy']-p['sx'])*cy+corrections[j]['value']} for j,p in enumerate(poses)],'scaleX':[{'t':p['frame']/30,'value':p['sx']} for p in poses],'scaleY':[{'t':p['frame']/30,'value':p['sx']} for p in poses],'opacity':opacity});bands.append(node)
g=dict(type='group',id='measured-email-panes-v13',start=518/30,end=18.5,children=bands)
s['layers']=[g if q['id']=='measured-email-panes-v13' else q for q in s['layers'] if q['id']!='context-v8-inbox-75']
(D/'email-v18-camera.json').write_text(json.dumps(poses,indent=2));(D/'assets/email-v18-provenance.json').write_text(json.dumps(provenance,indent=2));(D/'scene-email-v18.json').write_text(json.dumps(s,indent=2)+'\n');print('poses',[(p['frame'],round(p['sx'],3),round(p['sy'],3),round(p['dy'],1)) for p in poses if p['frame']%3==0])
