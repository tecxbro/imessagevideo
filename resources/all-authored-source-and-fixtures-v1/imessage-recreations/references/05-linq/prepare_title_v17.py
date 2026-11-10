"""Original native title glyphs, independent word springs, and two genuine icons."""
from pathlib import Path
import json,copy,importlib.util
from functools import lru_cache
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects,binary_dilation,map_coordinates,gaussian_filter1d
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;ROOT=D.parent.parent;F=D/'closing-title-v17-measure';INPUT=ROOT/'outputs/05-linq/final-v16/scene.json';scene=json.loads(INPUT.read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((INPUT.parent/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(scene)
@lru_cache(maxsize=8)
def rgb(f):return np.asarray(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float)/255
@lru_cache(maxsize=8)
def gray(f):return rgb(f).mean(2)
def sample_source(f,wx,wy):return map_coordinates(gray(f),[wy-160,wx],order=1,mode='constant',cval=1)
sp=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(sp);sp.loader.exec_module(trace);ref=rgb(1320);assetdir=D/'assets/title-v17';assetdir.mkdir(exist_ok=True)
# Twelve original glyphs; merge the separate i dot/stem using overlapping X.
x0,y0,x1,y1=345,300,680,360;ink=1-gray(1320)[y0-160:y1-160,x0:x1];labs,n=label(ink>.35);components=[]
for k,sl in enumerate(find_objects(labs),1):
 if sl is not None and (labs[sl]==k).sum()>12:components.append(dict(left=sl[1].start,right=sl[1].stop,mask=labs==k))
components.sort(key=lambda r:r['left']);merged=[]
for c in components:
 if merged and c['left']<merged[-1]['right']:
  merged[-1]['right']=max(merged[-1]['right'],c['right']);merged[-1]['mask']|=c['mask']
 else:merged.append(c)
assert len(merged)==12,len(merged);glyphs=[]
for j,(ch,c) in enumerate(zip('iMessageApps',merged)):
 ys,xs=np.where(c['mask']);left=max(0,int(xs.min())-2);right=min(ink.shape[1],int(xs.max())+3);top=max(0,int(ys.min())-2);bottom=min(ink.shape[0],int(ys.max())+3);a=(ink*binary_dilation(c['mask'],iterations=2))[top:bottom,left:right];gx=x0+left;gy=y0+top;path,stats=trace.trace_alpha(a,gx,gy);pad=15;glyphs.append(dict(char=ch,index=j,art=np.pad(a,pad),x=gx-pad,y=gy-pad,path=path,stats=stats))
print('glyphs',[(g['char'],g['x']+15,g['y']+15) for g in glyphs],flush=True)
def at(g,wx,wy,dx=0.,dy=0.):return map_coordinates(g['art'],[wy-g['y']-dy,wx-g['x']-dx],order=1,mode='constant',cval=0)
# One settled real Messages icon and one settled colored Apple robot, never a frame layer.
iconbox=[282,300,342,361];robotbox=[619,359,673,423]
for name,box in [('messages',iconbox),('robot',robotbox)]:
 bx,by,ex,ey=box;Image.fromarray(np.uint8(np.round(ref[by-160:ey-160,bx:ex]*255))).save(assetdir/(name+'.png'))
def green(f):
 a=rgb(f)[110:260,270:350];v=np.maximum(0,a[:,:,1]-(a[:,:,0]+a[:,:,2])/2);Y,X=np.mgrid[:v.shape[0],:v.shape[1]];mass=float(v.sum());return dict(mass=mass,x=float((v*X).sum()/max(mass,1e-9)+270),y=float((v*Y).sum()/max(mass,1e-9)+270),vx=float((v*X**2).sum()/max(mass,1e-9)-((v*X).sum()/max(mass,1e-9))**2),vy=float((v*Y**2).sum()/max(mass,1e-9)-((v*Y).sum()/max(mass,1e-9))**2))
gref=green(1320);S=glyphs[-1];G=glyphs[6];gY,gX=np.mgrid[347:355,490:585];gd=at(G,gX,gY);gmu=float((gd*gX).sum()/gd.sum());poses=[];prev_a=np.zeros(9);iconRef=ref[140:201,282:342]-1 # world300..361
for f in range(1268,1339):
 row=dict(frame=f,textY=31.,iMessageX=0.,appsX=0.,glyphOpacity=[0.]*8,appsOpacity=0.,iconX=0.,iconY=31.,iconScale=1.,iconOpacity=0.)
 # Icon pop is fitted independently from the lettering; its low opacity does
 # not get mistaken for a small or displaced text footprint.
 gf=green(f)
 if f>=1284 and gf['mass']>gref['mass']*.015:
  initialScale=float(np.clip(np.sqrt(max(.01,gf['vx'])/gref['vx']),.65,1.05));cx,cy=312.,330.;initialX=gf['x']-cx-initialScale*(gref['x']-cx);initialY=gf['y']-cy-initialScale*(gref['y']-cy);wy,wx=np.mgrid[275:410:2,270:350:2];target=rgb(f)[115:250:2,270:350:2]-1
  def ir(v):
   dx,dy,sc,a=v;qx=(wx-cx-dx)/sc+cx-282;qy=(wy-cy-dy)/sc+cy-300;pred=np.stack([map_coordinates(iconRef[:,:,c],[qy,qx],order=1,mode='constant',cval=0) for c in range(3)],2)*a;return (pred-target).ravel()
  ini=[float(np.clip(initialX,-4.9,4.9)),float(np.clip(initialY,-4.9,39.9)),initialScale,float(np.clip(gf['mass']/gref['mass']/initialScale**2,.01,.999))];fit=least_squares(ir,ini,bounds=([-5,-5,.6,0],[5,40,1.08,1]),diff_step=.004,max_nfev=55,ftol=.0002,xtol=.0002);ix,iy,isc,ia=map(float,fit.x);row.update(iconX=ix,iconY=iy,iconScale=isc,iconOpacity=ia)
 if f>=1278:
  yguess=31. if f<1296 else float(gf['y']-gref['y']);yguess=float(np.clip(yguess,-3,35))
  if f>=1280:
   lo=max(160,int(316+yguess));hi=min(560,int(350+yguess));rr=1-gray(f)[lo-160:hi-160,636:700];peak=rr.max();ll,nn=label(rr>max(.01,peak*.3));cs=[]
   for k,sl in enumerate(find_objects(ll),1):
    if sl is not None and (ll[sl]==k).sum()>6:cs.append((sl[1].stop,sl))
   if cs:
    _,sl=max(cs,key=lambda r:r[0]);bx=636+sl[1].start;ex=636+sl[1].stop;by=lo+sl[0].start;ey=lo+sl[0].stop;dx0=(bx+ex)/2-659.5;dy0=(by+ey)/2-332.5;wy,wx=np.mgrid[max(160,by-1):min(560,ey+1),max(0,bx-1):min(960,ex+1)];target=1-sample_source(f,wx,wy)
    def sr(v):return (at(S,wx,wy,v[0],v[1])*v[2]-target).ravel()
    fit=least_squares(sr,[dx0,dy0,min(.99,max(.05,float(peak)))],bounds=([dx0-3,dy0-3,0],[dx0+3,dy0+3,1]),diff_step=.005,max_nfev=45,ftol=.0002,xtol=.0002);xa,ty,aa=map(float,fit.x);row.update(appsX=xa,textY=ty,appsOpacity=aa)
   else:row['textY']=yguess
  if f<1280:row['textY']=31.
  if f<1296:
   v=1-sample_source(f,gX,gY+row['textY']);v=np.maximum(0,v);mass=v.sum();row['iMessageX']=float(np.clip((v*gX).sum()/max(mass,1e-9)-gmu,-3,60))
  else:row['iMessageX']=row['appsX']
  if f<=1296:
   lo=max(160,int(304+row['textY']));hi=min(560,int(360+row['textY']));wy,wx=np.mgrid[lo:hi,340:705];target=1-sample_source(f,wx,wy);masks=[at(g,wx,wy,row['iMessageX'],row['textY']) for g in glyphs[:8]];masks.append(np.clip(sum(at(g,wx,wy,row['appsX'],row['textY']) for g in glyphs[8:]),0,1));alphas=prev_a.copy();alphas[8]=row['appsOpacity']
   if f<1280:alphas[8]=0
   for _ in range(5):
    for j in list(range(7,-1,-1))+[8]:
     if j==8 and f<1280:continue
     other=np.ones_like(target)
     for k,m in enumerate(masks):
      if k!=j:other*=1-alphas[k]*m
     v=masks[j]*other;res=target-(1-other);alphas[j]=float(np.clip(np.sum(res*v)/max(1e-9,np.sum(v*v)),0,1))
   row['glyphOpacity']=[0. if z<.008 else float(z) for z in alphas[:8]];row['appsOpacity']=0. if alphas[8]<.008 else float(alphas[8]);prev_a=alphas
  else:row['glyphOpacity']=[1.]*8;row['appsOpacity']=1.
 poses.append(row);print('line1',row,flush=True)
# Original lower-line type is a single static graphic. Its birth/retirement has
# a shared pop/translation; the colored robot remains a separate real image.
leftbox=[125,355,617,425];rightbox=[675,355,840,425];bodyNodes=[];bodyArt=np.zeros((115,760),float)
for name,box,text in [('left',leftbox,'that supercharge your'),('right',rightbox,'agents')]:
 bx,by,ex,ey=box;a=1-gray(1320)[by-160:ey-160,bx:ex];path,stats=trace.trace_alpha(a,bx,by);bodyNodes.append(dict(type='path',id='v17-body-'+name,d=path,fill='#000000',semanticText=text,sourceFrame=1320,sourceBounds=box));bodyArt[by-340:ey-340,bx-100:ex-100]=a
bodyPoses=[];posemap={p['frame']:p for p in poses};robotRef=ref[199:263,619:673]-1;cx,cy=480.,390.
for f in range(1268,1338):
 row=dict(frame=f,x=0.,y=0.,scale=1.,opacity=0.,sigmaY=0.,robotOpacity=0.)
 if 1300<=f<=1337:
  if f<=1308 or f>=1334:
   wy,wx=np.mgrid[355:450:2,100:860:2];target=1-sample_source(f,wx,wy);cut=max(355,353+posemap[f]['textY']+4);valid=(wy>=cut)&~((wx>=600)&(wx<680));targetRGB=rgb(f)[195:290:2,100:860:2];valid&=(targetRGB.max(2)-targetRGB.min(2))<.12
   def br(v):
    dx,dy,sc,a,b=v;ar=gaussian_filter1d(bodyArt,max(.001,b/sc),axis=0,mode='constant');qx=(wx-cx-dx)/sc+cx-100;qy=(wy-cy-dy)/sc+cy-340;pred=map_coordinates(ar,[qy,qx],order=1,mode='constant',cval=0)*a;return (pred-target)[valid].ravel()
   init=[0,4 if f<=1302 else 0 if f<1334 else 3 if f==1334 else 10 if f==1335 else 17,.96 if f<=1302 else 1,.12 if f==1300 else .4 if f<=1302 else .95 if f<1334 else .82,.2]
   fit=least_squares(br,init,bounds=([-5,-5,.85,0,0],[5,30,1.08,1,4]),diff_step=.004,max_nfev=70,ftol=.0002,xtol=.0002);dx,dy,sc,a,b=map(float,fit.x);row.update(x=dx,y=dy,scale=sc,opacity=a,sigmaY=b if b>.25 else 0.)
  else:row['opacity']=1.
  # Fit colored artwork amplitude only; reference pixels are one static emoji.
  dx,dy,sc=row['x'],row['y'],row['scale'];b=row['sigmaY'];wy,wx=np.mgrid[355:440,612:680];qx=(wx-cx-dx)/sc+cx-619;qy=(wy-cy-dy)/sc+cy-359;temp=np.stack([map_coordinates(gaussian_filter1d(robotRef[:,:,c],max(.001,b/sc),axis=0,mode='constant'),[qy,qx],order=1,mode='constant',cval=0) for c in range(3)],2);target=np.stack([map_coordinates(rgb(f)[:,:,c],[wy-160,wx],order=1,mode='constant',cval=1) for c in range(3)],2)-1;row['robotOpacity']=float(np.clip(np.sum(temp*target)/max(1e-9,np.sum(temp*temp)),0,1))
 bodyPoses.append(row);print('line2',row,flush=True)
def keys(rows,name):return [dict(t=r['frame']/30,value=r[name],ease='hold') for r in rows]
icon=dict(type='image',id='v17-original-messages-icon',src=str(assetdir/'messages.png'),x=iconbox[0],y=iconbox[1],width=iconbox[2]-iconbox[0],height=iconbox[3]-iconbox[1],sourceFrame=1320,sourceBounds=iconbox)
iconGroup=dict(type='group',id='v17-message-icon-camera',originX=312,originY=330,children=[icon],keyframes={'x':keys(poses,'iconX'),'y':keys(poses,'iconY'),'scaleX':keys(poses,'iconScale'),'scaleY':keys(poses,'iconScale'),'opacity':keys(poses,'iconOpacity')})
iNodes=[];aNodes=[]
for j,g in enumerate(glyphs):
 n=dict(type='path',id=f'v17-title-glyph-{j}',d=g['path'],fill='#000000',semanticText=g['char'],sourceFrame=1320)
 if j<8:n['keyframes']={'opacity':[dict(t=r['frame']/30,value=r['glyphOpacity'][j],ease='hold') for r in poses]};iNodes.append(n)
 else:aNodes.append(n)
iGroup=dict(type='group',id='v17-imessage-word',children=iNodes,keyframes={'x':keys(poses,'iMessageX'),'y':keys(poses,'textY')});aGroup=dict(type='group',id='v17-apps-word',children=aNodes,keyframes={'x':keys(poses,'appsX'),'y':keys(poses,'textY'),'opacity':keys(poses,'appsOpacity')});first=dict(type='group',id='g-1065',start=1268/30,end=1339/30,children=[iconGroup,iGroup,aGroup])
textGroup=dict(type='group',id='v17-body-native-type',children=bodyNodes,keyframes={'opacity':keys(bodyPoses,'opacity')});robot=dict(type='image',id='v17-original-colored-robot',src=str(assetdir/'robot.png'),x=robotbox[0],y=robotbox[1],width=robotbox[2]-robotbox[0],height=robotbox[3]-robotbox[1],sourceFrame=1320,sourceBounds=robotbox,keyframes={'opacity':keys(bodyPoses,'robotOpacity')});layout=dict(type='group',id='v17-body-layout',originX=480,originY=390,children=[textGroup,robot],keyframes={'x':keys(bodyPoses,'x'),'y':keys(bodyPoses,'y'),'scaleX':keys(bodyPoses,'scale'),'scaleY':keys(bodyPoses,'scale')})
# The only new effect is the already supported reciprocal native shutter.
inv=dict(type='group',id='v17-body-inverse-shutter',children=[layout],keyframes={'scaleX':[dict(t=r['frame']/30,value=1/.3 if r['sigmaY'] else 1,ease='hold') for r in bodyPoses],'scaleY':[dict(t=r['frame']/30,value=1/r['sigmaY'] if r['sigmaY'] else 1,ease='hold') for r in bodyPoses]});second=dict(type='group',id='g-1067',start=1268/30,end=1338/30,children=[inv],keyframes={'blur':[dict(t=r['frame']/30,value=1 if r['sigmaY'] else 0,ease='hold') for r in bodyPoses],'scaleX':[dict(t=r['frame']/30,value=.3 if r['sigmaY'] else 1,ease='hold') for r in bodyPoses],'scaleY':[dict(t=r['frame']/30,value=r['sigmaY'] if r['sigmaY'] else 1,ease='hold') for r in bodyPoses]})
for i,q in enumerate(scene['layers']):
 if q['id']=='g-1065':scene['layers'][i]=first
 elif q['id']=='g-1067':scene['layers'][i]=second
cta=next(q for q in scene['layers'] if q['id']=='g-1069');cta['start']=1339/30
# Preserve every accepted later CTA pose; repair only its true opaque birth/cut.
referenceGray=gray(1350);yy,xx=np.where(referenceGray<.5);topRef=int(yy.min()+160);ctap=[]
for f in range(1339,1344):
 yy,xx=np.where(gray(f)<.5);top=int(yy.min()+160);ctap.append(dict(frame=f,y=top-topRef,opacity=1.))
cta['keyframes']['y']=keys(ctap,'y');cta['keyframes']['opacity']=keys(ctap,'opacity')
(D/'title-v17-measurements.json').write_text(json.dumps(dict(referenceFrame=1320,sourceCropOriginY=160,line1=poses,line2=bodyPoses,ctaBoundary=ctap,glyphs=[{k:g[k] for k in ['char','index','x','y','stats']} for g in glyphs],staticArtwork=[dict(name='messages',bounds=iconbox),dict(name='robot',bounds=robotbox)]),indent=2)+'\n');(D/'scene-title-v17.json').write_text(json.dumps(scene,indent=2)+'\n')
