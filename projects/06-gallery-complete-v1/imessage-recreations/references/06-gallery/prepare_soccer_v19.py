"""Measured native love exit, three message components and original football."""
from pathlib import Path
import copy,json,importlib.util,math
from functools import lru_cache
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects,binary_fill_holes,binary_closing,binary_erosion,map_coordinates,gaussian_filter
from scipy.signal import correlate
from scipy.optimize import minimize_scalar
D=Path(__file__).resolve().parent;F=D/'native-late-v19';A=D/'assets';snap=D.parent.parent/'outputs/06-gallery/final-v18';s=json.loads((snap/'scene.json').read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((snap/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s)
@lru_cache(maxsize=4)
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
def comps(mask,minArea=1):
 lab,n=label(mask);out=[]
 for k,sl in enumerate(find_objects(lab),1):
  if sl is None:continue
  m=lab[sl]==k;area=int(m.sum())
  if area<minArea:continue
  ys,xs=np.where(m);out.append(dict(box=[sl[1].start,sl[0].start,sl[1].stop,sl[0].stop],area=area,cx=float(xs.mean()+sl[1].start),cy=float(ys.mean()+sl[0].start),mask=m))
 return out
# Gray body identities are ordered vertically; blue is a separate saturated UI.
bodies={};balls={};prevBall=None
for f in range(891,1049):
 a=load(f);lo=a.min(2);hi=a.max(2);gray=a.mean(2);gm=(hi-lo<5)&(gray>225)&(gray<253);gs=[]
 for q in comps(gm,1000):
  ax,ay,bx,by=q['box'];w=bx-ax;h=by-ay
  if not(h>55 and (w>300 or (bx>=1918 and w>20) or (by>=1079 and w>150))):continue
  if f<945 and bx<1918:continue
  counts=q['mask'].sum(1);wide=np.where(counts>w*.25)[0]
  if not len(wide):continue
  trim=int(wide.min());q['mask']=q['mask'][trim:];q['box'][1]+=trim;q['area']=int(q['mask'].sum());ys1,xs1=np.where(q['mask']);q['cx']=float(xs1.mean()+ax);q['cy']=float(ys1.mean()+q['box'][1]);gs.append(q)
 gs.sort(key=lambda q:q['box'][1]);bm=(a[:,:,2]>a[:,:,0]+15)&(a[:,:,1]>a[:,:,0]+8)&(a[:,:,2]>220);bs=comps(bm,300);blue=max(bs,key=lambda q:q['area']) if bs else None
 # Football has a dense round neutral silhouette, distinct from the small ink
 # glyphs and wide message bodies. Prediction only disambiguates candidates.
 fm=(hi-lo<70)&(gray<252)
 for q in gs:
  gx,gy,gr,gb=q['box']
  if gr-gx>300 and gb-gy>100:fm[gy:gb,gx:gr]=False
 fm=binary_closing(fm,iterations=3);cs=[]
 for q in comps(fm,1800):
  x0,y0,x1,y1=q['box'];w=x1-x0;h=y1-y0
  if not(75<w<200 and 75<h<200 and .75<w/h<1.3 and q['area']/(w*h)>.65):continue
  cs.append(q)
 if prevBall is None:predict=np.array([843,613.])
 else:predict=np.array([prevBall['cx'],prevBall['cy']])+np.array(prevBall.get('velocity',[0,0]))
 ball=min(cs,key=lambda q:np.hypot(q['cx']-predict[0],q['cy']-predict[1])) if cs else None
 if ball and np.hypot(ball['cx']-predict[0],ball['cy']-predict[1])<250:
  mask=binary_fill_holes(binary_closing(ball['mask'],iterations=1));edge=mask&~binary_erosion(mask);yy,xx=np.where(edge);xx=xx+ball['box'][0];yy=yy+ball['box'][1];coef=np.linalg.lstsq(np.c_[2*xx,2*yy,np.ones(len(xx))],xx*xx+yy*yy,rcond=None)[0];cx,cy=map(float,coef[:2]);radius=float(np.sqrt(max(1,coef[2]+cx*cx+cy*cy)));vel=[0.,0.] if prevBall is None else [cx-prevBall['cx'],cy-prevBall['cy']];balls[f]=dict(frame=f,cx=cx,cy=cy,radius=radius,box=ball['box'],velocity=vel,observed=True);prevBall=balls[f]
 elif prevBall is not None:
  cx,cy=predict;balls[f]=dict(frame=f,cx=float(cx),cy=float(cy),radius=prevBall['radius'],box=prevBall['box'],velocity=prevBall.get('velocity',[0,0]),observed=False);prevBall=balls[f]
 bodies[f]=dict(gray=gs,blue=blue)
 if f%20==0:print('segmented',f,flush=True)
# Static native body and copy shapes are traced once, never frame playback.
ref=load(1048);rg=bodies[1048]['gray'];print('referencegray',[(q['box'],q['area']) for q in rg],flush=True);assert len(rg)==2,len(rg);blue=bodies[1048]['blue'];refs=[rg[0],blue,rg[1]];nodes=[];poseRecords={};provenance=[]
for idx,(kind,obj,text) in enumerate(zip(['first','blue','second'],refs,["It’s official: United signed their\nstriker. Announced 2 min ago 🚨","LETS GOOOO","€85M, five years. You called\nthis back in June, btw"])):
 box=obj['box'];x0,y0,x1,y1=box;pad=3;ar=ref[max(0,y0-pad):min(1080,y1+pad),max(0,x0-pad):min(1920,x1+pad)];ox=max(0,x0-pad);oy=max(0,y0-pad)
 if kind=='blue':
  fill=np.median(ref[y0:y1,x0:x1][(ref[y0:y1,x0:x1,2]>ref[y0:y1,x0:x1,0]+70)],axis=0);bodyAlpha=np.clip((255-ar[:,:,0])/(255-fill[0]),0,1);inside=binary_fill_holes(bodyAlpha>.5);bodyAlpha[inside]=1;copyBox=[x0+25,y0+18,x1-25,y1-18];crop=ref[copyBox[1]:copyBox[3],copyBox[0]:copyBox[2]];copyAlpha=np.clip((crop[:,:,0]-fill[0])/(255-fill[0]),0,1);ink='#ffffff'
 else:
  fill=np.array([237,237,237]);bodyAlpha=np.clip((255-ar.mean(2))/18,0,1);inside=binary_fill_holes(bodyAlpha>.5);bodyAlpha[inside]=1;copyBox=[x0+20,y0+15,x1-15,y1-30];crop=ref[copyBox[1]:copyBox[3],copyBox[0]:copyBox[2]];copyAlpha=np.clip((237-crop.mean(2))/(237-21),0,1);ink='#151515'
 bodyPath,bodyStats=trace.trace_alpha(bodyAlpha,ox,oy);children=[dict(type='path',id=f'v19-soccer-{kind}-body',d=bodyPath,fill='#'+''.join(f'{round(c):02x}' for c in fill))]
 if kind=='first':
  r,g,b=crop[:,:,0],crop[:,:,1],crop[:,:,2];red=(r>g+55)&(r>b+35)&(r>150);ey,ex=np.where(red);eb=[max(copyBox[0],int(ex.min()+copyBox[0])-5),max(copyBox[1],int(ey.min()+copyBox[1])-5),min(copyBox[2],int(ex.max()+copyBox[0])+7),min(copyBox[3],int(ey.max()+copyBox[1])+7)];emoji=ref[eb[1]:eb[3],eb[0]:eb[2]];ep=A/'v19-soccer-siren-original.png';Image.fromarray(np.uint8(emoji)).save(ep);children.append(dict(type='image',id='v19-soccer-original-siren',src=str(ep),x=eb[0],y=eb[1],width=eb[2]-eb[0],height=eb[3]-eb[1]));copyAlpha[eb[1]-copyBox[1]:eb[3]-copyBox[1],eb[0]-copyBox[0]:eb[2]-copyBox[0]]=0;provenance.append(dict(path=str(ep),source_frame=1048,box=eb,kind='bounded genuine siren emoji artwork inside independently native bubble/copy'))
 copyPath,copyStats=trace.trace_alpha(copyAlpha,copyBox[0],copyBox[1]);children.append(dict(type='path',id=f'v19-soccer-{kind}-copy',d=copyPath,fill=ink,semanticText=text));poses=[];rw=x1-x0;rh=y1-y0
 my,mx=np.where(obj['mask']);refcx=mx.mean()+x0;refcy=my.mean()+y0;refcov=np.cov(np.c_[mx,my].T);ev,evec=np.linalg.eigh(refcov);refMajor=float(ev[1]);refMinor=float(ev[0]);rv=evec[:,1];refAngle=float(np.degrees(np.arctan2(rv[1],rv[0])))
 for f in range(891,1049):
  if kind=='blue':actual=bodies[f]['blue']
  elif kind=='first':actual=bodies[f]['gray'][0] if bodies[f]['gray'] else None
  else:actual=bodies[f]['gray'][1] if len(bodies[f]['gray'])>1 else None
  if actual is None:continue
  ax,ay,bx,by=actual['box'];w=bx-ax;h=by-ay
  if kind=='first' and (h<100 or actual['area']<3000):continue
  if kind=='second' and w<150:continue
  if bx<1919 and by<1079 and ax>0 and ay>0:
   my,mx=np.where(actual['mask']);cx=float(mx.mean()+ax);cy=float(my.mean()+ay);cov=np.cov(np.c_[mx,my].T);ev,evec=np.linalg.eigh(cov);vec=evec[:,1];angle=float(np.degrees(np.arctan2(vec[1],vec[0])))-refAngle;angle=((angle+90)%180)-90;sxx=float(np.sqrt(max(.01,ev[1]/refMajor)));syy=float(np.sqrt(max(.01,ev[0]/refMinor)));xkey=cx-refcx;ykey=cy-refcy
  else:
   if kind=='blue':sxx=syy=1.
   elif bx>=1919:sxx=syy=h/rh
   else:sxx=syy=w/rw
   angle=0.;xkey=(ax-x0*sxx)+refcx*(sxx-1);ykey=(ay-y0*syy)+refcy*(syy-1)
  image=load(f);raw=image[ay:by,ax:bx][actual['mask']];medianR=float(np.median(raw[:,0]));opacity=float(np.clip((255-medianR)/max(1,255-fill[0]),0,1));poses.append(dict(frame=f,x=xkey,y=ykey,sx=sxx,sy=syy,rotation=angle,opacity=opacity))
 if not poses:raise ValueError(kind)
 def keys(k):return [dict(t=p['frame']/30,value=p[k],ease='linear') for p in poses]
 node=dict(type='group',id=f'v19-soccer-{kind}-message',start=poses[0]['frame']/30,end=1049/30,children=children,keyframes={k:keys(v) for k,v in [('x','x'),('y','y'),('scaleX','sx'),('scaleY','sy'),('rotation','rotation'),('opacity','opacity')]})
 node.update(originX=refcx,originY=refcy)
 nodes.append(node);poseRecords[kind]=poses
# Sparse original l/ve outlines are registered together against the native
# black silhouette. Their gap contains the independently animated football.
refL=load(891).mean(2);K=np.zeros((240,550),np.float32);ly,lx=465,685
for box in [[690,470,727,693],[938,526,1234,697]]:
 x0,y0,x1,y1=box;K[y0-ly:y1-ly,x0-lx:x1-lx]=(255-refL[y0:y1,x0:x1])/255
paths=[]
for name,box in [('l',[690,470,727,693]),('ve',[938,526,1234,697])]:
 x0,y0,x1,y1=box;path,stats=trace.trace_alpha((255-refL[y0:y1,x0:x1])/255,x0,y0);paths.append(dict(type='path',id=f'v19-love-original-{name}',d=path,fill='#000000',semanticText=name))
colEnergy=np.sum(K*K,axis=0);prefix=np.r_[0,np.cumsum(colEnergy)];love=[];previousX=0.
for f in range(891,947):
 I=(255-load(f).mean(2)[350:760])/255;C=correlate(I,K,mode='full',method='fft');dxs=np.arange(-1250,81);dys=np.arange(-65,21);xpos=lx+dxs;visibleEnergy=np.array([prefix[min(550,max(0,1920-x))]-prefix[min(550,max(0,-x))] for x in xpos]);iy=ly+dys-350+K.shape[0]-1;ix=xpos+K.shape[1]-1;cost=visibleEnergy[None,:]-2*C[np.ix_(iy,ix)]
 if f==891:cost[:,np.abs(dxs)>2]=1e6
 else:cost[:,(dxs>previousX+4)|(dxs<previousX-300)]=1e6
 at=np.unravel_index(np.argmin(cost),cost.shape);dy=float(dys[at[0]]);dx0=float(dxs[at[1]]);previousX=dx0;visible=float(visibleEnergy[at[1]]);opacity=1. if visible>1 else 0.;love.append(dict(frame=f,x=dx0,y=dy,opacity=opacity))
loveNode=dict(type='group',id='v19-love-measured-letters',start=891/30,end=947/30,children=paths,keyframes={k:[dict(t=p['frame']/30,value=p[k],ease='linear') for p in love] for k in ['x','y','opacity']});nodes.insert(0,loveNode);poseRecords['love']=love
# Rotate the same genuine static football artwork at its measured circle pose.
original=next(q for q in s['layers'] if q['id']=='g-1314')['children'][1];ballArt=np.array(Image.open(original['src']).convert('RGBA')).astype(np.float32);alpha=ballArt[:,:,3]/255;premult=ballArt[:,:,:3]*alpha[:,:,None];refBall=balls[891];ballRows=[];prevAngle=0.;u=np.linspace(5,150,40);vv,uu=np.meshgrid(u,u,indexing='ij');center=77.5
for f,r in balls.items():
 scale=r['radius']/refBall['radius'];w=h=156*scale;x=r['cx']-(refBall['cx']-(765+78))*scale-w/2;y=r['cy']-(refBall['cy']-(535+78))*scale-h/2;target=np.stack([map_coordinates(load(f)[:,:,c],[y+vv/156*h,x+uu/156*w],order=1,mode='constant',cval=255) for c in range(3)],2)
 def cost(angle):
  a=np.deg2rad(angle);sx0=np.cos(a)*(uu-center)+np.sin(a)*(vv-center)+center;sy0=-np.sin(a)*(uu-center)+np.cos(a)*(vv-center)+center;aa=map_coordinates(alpha,[sy0,sx0],order=1,mode='constant',cval=0);rgb=np.stack([map_coordinates(premult[:,:,c],[sy0,sx0],order=1,mode='constant',cval=0) for c in range(3)],2);pred=rgb+255*(1-aa[:,:,None]);return float(np.mean((pred-target)**2))
 if r['observed']:
  angles=np.arange(0,360,10);values=[cost(a) for a in angles];best=float(angles[int(np.argmin(values))]);fit=minimize_scalar(cost,bounds=(best-10,best+10),method='bounded',options={'xatol':.04});angle=float(fit.x);angle+=360*round((prevAngle-angle)/360);prevAngle=angle
 else:angle=prevAngle
 ballRows.append(dict(frame=f,x=x,y=y,scale=scale,rotation=angle,opacity=1. if x<1920 and x+w>0 else 0.,observed=r['observed']))
for p in ballRows:p['renderX']=p['x']+78*(p['scale']-1);p['renderY']=p['y']+78*(p['scale']-1)
ballNode=dict(type='group',id='v19-soccer-measured-ball',start=891/30,end=1049/30,originX=78,originY=78,children=[dict(type='image',id='v19-soccer-original-football',src=original['src'],width=156,height=156)],keyframes={k:[dict(t=p['frame']/30,value=p[v],ease='linear') for p in ballRows] for k,v in [('x','renderX'),('y','renderY'),('scaleX','scale'),('scaleY','scale'),('rotation','rotation'),('opacity','opacity')]});nodes.append(ballNode);poseRecords['ball']=ballRows
# All replaced original roots are confined to891–1048; subsequent graphics
# start after the removed live-action interval and retain their exact mapping.
replacements={}
for q in s['layers']:
 if q['id'] in ['g-1314','g-1319','g-1323','g-1328','g-1330']:q['start']=q['end']=1049/30;replacements[q['id']]=q
s['layers'].extend(nodes);(D/'soccer-v19-measurements.json').write_text(json.dumps(poseRecords,indent=2));(D/'soccer-v19-patch.json').write_text(json.dumps(dict(replace=replacements,append=nodes),indent=2));(A/'soccer-v19-provenance.json').write_text(json.dumps(provenance,indent=2));(D/'scene-soccer-v19.json').write_text(json.dumps(s,indent=2)+'\n');print('wrote',[(k,len(v)) for k,v in poseRecords.items()])
