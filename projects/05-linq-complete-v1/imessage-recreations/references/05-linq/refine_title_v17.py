"""Refine measured pop support and text shutter; preserve all unrelated groups."""
from pathlib import Path
import json,copy,importlib.util
from functools import lru_cache
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter1d
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'closing-title-v17-measure';scene=json.loads((D/'scene-title-v17.json').read_text());data=json.loads((D/'title-v17-measurements.json').read_text());line1=data['line1'];body=data['line2'];sp=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(sp);sp.loader.exec_module(trace)
@lru_cache(maxsize=8)
def rgb(f):return np.asarray(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float)/255
@lru_cache(maxsize=8)
def gray(f):return rgb(f).mean(2)
def source(f,wx,wy):return map_coordinates(gray(f),[wy-160,wx],order=1,mode='constant',cval=1)
def keys(rows,name):return [dict(t=r['frame']/30,value=round(float(r[name]),6),ease='hold') for r in rows]
# Full-line Y/shutter fit avoids confusing one glyph's antialiasing with motion.
typeArt=np.pad(1-gray(1320)[140:200,345:680],20);tx,ty=325,280
for r in line1:
 r['textSigmaY']=0.
 f=r['frame']
 if not (1296<=f<=1308 or 1334<=f<=1338):continue
 guess=r['iconY'];lo=max(160,int(310+guess));hi=min(560,int(356+guess));wy,wx=np.mgrid[lo:hi,345:705];target=1-source(f,wx,wy)
 def residual(v):
  dx,dy,b=v;ar=gaussian_filter1d(typeArt,max(.001,b),axis=0,mode='constant');pred=map_coordinates(ar,[wy-ty-dy,wx-tx-dx],order=1,mode='constant',cval=0);return (pred-target).ravel()
 fit=least_squares(residual,[0,guess,1.5],bounds=([-2,guess-3,0],[2,guess+3,4]),max_nfev=55,diff_step=.004,ftol=.0002,xtol=.0002);dx,dy,b=map(float,fit.x);r.update(iMessageX=dx,appsX=dx,textY=dy,textSigmaY=b if b>.25 else 0.);print('text-shutter',f,r['textY'],r['textSigmaY'],flush=True)
first=next(q for q in scene['layers'] if q['id']=='g-1065');iGroup=next(q for q in first['children'] if q['id']=='v17-imessage-word');aGroup=next(q for q in first['children'] if q['id']=='v17-apps-word');iGroup['keyframes'].update(x=keys(line1,'iMessageX'),y=keys(line1,'textY'));aGroup['keyframes'].update(x=keys(line1,'appsX'),y=keys(line1,'textY'))
def shutter(id,children,rows,prop):
 sx=lambda r:.3 if r[prop] else 1.;sy=lambda r:r[prop] if r[prop] else 1.
 inv=dict(type='group',id=id+'-inverse',children=children,keyframes={'scaleX':[dict(t=r['frame']/30,value=round(1/sx(r),6),ease='hold') for r in rows],'scaleY':[dict(t=r['frame']/30,value=round(1/sy(r),6),ease='hold') for r in rows]})
 return dict(type='group',id=id,children=[inv],keyframes={'blur':[dict(t=r['frame']/30,value=1 if r[prop] else 0,ease='hold') for r in rows],'scaleX':[dict(t=r['frame']/30,value=sx(r),ease='hold') for r in rows],'scaleY':[dict(t=r['frame']/30,value=round(sy(r),6),ease='hold') for r in rows]})
first['children']=[q for q in first['children'] if q['id'] not in ['v17-imessage-word','v17-apps-word']]+[shutter('v17-first-type-shutter',[iGroup,aGroup],line1,'textSigmaY')]
# Refit birth scale from complete observed support, not a local guess.
art=np.zeros((115,760),float)
for box in [[125,355,617,425],[675,355,840,425]]:
 x0,y0,x1,y1=box;art[y0-340:y1-340,x0-100:x1-100]=1-gray(1320)[y0-160:y1-160,x0:x1]
yr,xr=np.where(art>.25);refLeft,refRight=float(xr.min()+100),float(xr.max()+101);refTop=float(yr.min()+340);cx,cy=480.,390.;posemap={r['frame']:r for r in line1};robotRef=rgb(1320)[199:263,619:673]-1
for r in body:
 f=r['frame']
 if not 1300<=f<=1312:continue
 wy,wx=np.mgrid[355:450:2,100:860:2];target=1-source(f,wx,wy);cut=max(355,353+posemap[f]['textY']+4);valid=(wy>=cut)&~((wx>=600)&(wx<680));tc=rgb(f)[195:290:2,100:860:2];valid&=(tc.max(2)-tc.min(2))<.12
 full=1-gray(f)[195:290,100:860];fc=rgb(f)[195:290,100:860];Y,X=np.mgrid[355:450,100:860];mask=(Y>=cut)&((fc.max(2)-fc.min(2))<.12);peak=float(full[mask].max());mask&=full>max(.01,peak*.25);ys,xs=np.where(mask);left=float(xs.min()+100);right=float(xs.max()+101);top=float(ys.min()+355);sc0=float(np.clip((right-left)/(refRight-refLeft),.72,1.05));dx0=(left+right)/2-(cx+sc0*((refLeft+refRight)/2-cx));dy0=top-(cy+sc0*(refTop-cy))
 def residual(v):
  dx,dy,sc,a,b=v;ar=gaussian_filter1d(art,max(.001,b/sc),axis=0,mode='constant');qx=(wx-cx-dx)/sc+cx-100;qy=(wy-cy-dy)/sc+cy-340;pred=map_coordinates(ar,[qy,qx],order=1,mode='constant',cval=0)*a;return (pred-target)[valid].ravel()
 ini=[float(np.clip(dx0,-4.9,4.9)),float(np.clip(dy0,-4.9,29.9)),sc0,float(np.clip(peak,.01,.9999)),.2];fit=least_squares(residual,ini,bounds=([-5,-5,max(.7,sc0-.012),0,0],[5,30,min(1.08,sc0+.012),1,4]),max_nfev=70,diff_step=.004,ftol=.0002,xtol=.0002);dx,dy,sc,a,b=map(float,fit.x);r.update(x=dx,y=dy,scale=sc,opacity=a,sigmaY=b if b>.25 else 0.,measuredSupportScale=sc0)
 # Refit only the colored image amplitude with the correct geometric pop.
 wy2,wx2=np.mgrid[350:445,585:690];qx=(wx2-cx-dx)/sc+cx-619;qy=(wy2-cy-dy)/sc+cy-359;temp=np.stack([map_coordinates(gaussian_filter1d(robotRef[:,:,c],max(.001,r['sigmaY']/sc),axis=0,mode='constant'),[qy,qx],order=1,mode='constant',cval=0) for c in range(3)],2);targetRGB=np.stack([map_coordinates(rgb(f)[:,:,c],[wy2-160,wx2],order=1,mode='constant',cval=1) for c in range(3)],2)-1;r['robotOpacity']=float(np.clip(np.sum(temp*targetRGB)/max(1e-9,np.sum(temp*temp)),0,1));print('pop-refit',r,flush=True)
second=next(q for q in scene['layers'] if q['id']=='g-1067');layout=second['children'][0]['children'][0];layout['keyframes'].update(x=keys(body,'x'),y=keys(body,'y'),scaleX=keys(body,'scale'),scaleY=keys(body,'scale'));text=layout['children'][0];robot=layout['children'][1];text['keyframes']['opacity']=keys(body,'opacity');robot['keyframes']['opacity']=keys(body,'robotOpacity');replacement=shutter('g-1067',[layout],body,'sigmaY');replacement.update(start=1268/30,end=1338/30);scene['layers'][scene['layers'].index(second)]=replacement
# Original question glyphs; later accepted camera/opacity remains exactly0/1.
cta=next(q for q in scene['layers'] if q['id']=='g-1069');box=[260,325,700,400];x0,y0,x1,y1=box;alpha=1-gray(1350)[y0-160:y1-160,x0:x1];path,stats=trace.trace_alpha(alpha,x0,y0);glyph=dict(type='path',id='t-1068',d=path,fill='#000000',semanticText='What will you build?',sourceFrame=1350,sourceBounds=box);padded=np.pad(alpha,20);ax,ay=x0-20,y0-20;ctap=[]
for f in range(1339,1373):
 r=dict(frame=f,y=0.,opacity=1.,sigmaY=0.)
 if f<=1342:
  wy,wx=np.mgrid[330:425,260:700];target=1-source(f,wx,wy);guess=18 if f==1339 else 11 if f==1340 else 5
  def residual(v):
   dy,b=v;ar=gaussian_filter1d(padded,max(.001,b),axis=0,mode='constant');pred=map_coordinates(ar,[wy-ay-dy,wx-ax],order=1,mode='constant',cval=0);return (pred-target).ravel()
  fit=least_squares(residual,[guess,1.5],bounds=([guess-3,0],[guess+3,4]),max_nfev=55,diff_step=.004,ftol=.0002,xtol=.0002);dy,b=map(float,fit.x);r.update(y=dy,sigmaY=b if b>.25 else 0.)
 ctap.append(r)
cta['start']=1339/30;cta['children']=[shutter('v17-cta-native-shutter',[glyph],ctap,'sigmaY')];cta['keyframes']={'y':keys(ctap,'y'),'opacity':keys(ctap,'opacity')}
# Quantize pose VALUES only to the real timeline's six-decimal precision;
# frame/fps timestamps remain exact and unchanged.
def quantize(q):
 for k,ks in q.get('keyframes',{}).items():
  for v in ks:
   if isinstance(v['value'],(int,float)):v['value']=round(v['value'],6)
 for c in q.get('children',[]):quantize(c)
for q in scene['layers']:
 if q['id'] in ['g-1065','g-1067','g-1069']:quantize(q)
data.update(line1=line1,line2=body,ctaBoundary=ctap,ctaGlyph=dict(sourceFrame=1350,sourceBounds=box,stats=stats));(D/'title-v17-measurements-refined.json').write_text(json.dumps(data,indent=2)+'\n');(D/'scene-title-v17-refined.json').write_text(json.dumps(scene,indent=2)+'\n')
