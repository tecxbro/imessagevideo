"""Native first-composer lifecycle and Cash tail; all source frames are analysis only."""
from pathlib import Path
import json,copy,hashlib,importlib.util
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,label,find_objects
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;R=D.parent.parent;B=R/'outputs/05-linq/final-v18';F=D/'measurements/composer-v19/native';s=json.loads((B/'scene.json').read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src'and isinstance(v,str)and not v.startswith(('data:','/','http:','https:')):o[k]=str((B/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s)
def load(f):return np.array(Image.open(F/f'source-{f:06d}.png').convert('RGB')).astype(float)
src={f:load(f)for f in range(100)}
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
anchor=json.loads((D/'measurements/composer-v19/intro-anchor-diagnostic.json').read_text());textdiag=json.loads((D/'measurements/composer-v19/intro-text-diagnostic.json').read_text());td={r['frame']:r for r in textdiag['rows']}
# The genuine completed composer defines the coordinate system for its closing camera.
ref=src[87].mean(2).copy();ref[335:388,669:680]=255;cams={f:{'x':0.,'y':0.,'scaleX':1.,'scaleY':1.}for f in range(99)}
for f in range(89,99):
 a=src[f].mean(2);bb=td[f]['blue'];tb=td[f]['text'];sx=((bb[0]+bb[2])/2-tb[0])/(726.5-305);sy=(bb[3]-bb[1])/56;tx=tb[0]-sx*305;ty=(bb[1]+bb[3])/2-sy*360
 x0=max(0,int(tx+sx*280)-8);x1=min(960,int(tx+sx*785)+8);y0=max(0,int(ty+sy*310)-8);y1=min(720,int(ty+sy*408)+8);xx,yy=np.meshgrid(np.arange(x0,x1,2),np.arange(y0,y1,2));u=(xx-tx)/sx;v=(yy-ty)/sy;keep=~((u>666)&(u<682)&(v>330)&(v<395));xx=xx[keep];yy=yy[keep];target=a[yy,xx]
 def residual(q):
  x,y,sx,sy=q;model=map_coordinates(ref,[(yy-y)/sy,(xx-x)/sx],order=1,mode='constant',cval=255,prefilter=False);return(model-target)/30
 fit=least_squares(residual,[tx,ty,sx,sy],bounds=([tx-15,ty-15,sx-.05,sy-.08],[tx+15,ty+15,sx+.05,sy+.08]),max_nfev=65,diff_step=[.0001,.0001,.0001,.0001]);cams[f]=dict(zip(['x','y','scaleX','scaleY'],map(float,fit.x)));print('closing',f,cams[f],flush=True)

def traced(name,frame,box,kind='gray'):
 ar=src[frame][box[1]:box[3],box[0]:box[2]];gray=ar.mean(2)
 if kind=='white':
  alpha=np.clip(ar[:,:,0]/255,0,1);color='#ffffff';ink=alpha*255
 else:
  valid=(gray<220)&(ar.max(2)-ar.min(2)<20);fg=float(np.percentile(gray[valid],5));alpha=np.clip((255-gray)/(255-fg),0,1);alpha[(ar[:,:,2]-ar[:,:,0]>40)&(ar[:,:,2]>170)]=0;color='#'+('%02x'%round(fg))*3;ink=alpha*(255-fg)
 d,stats=trace.trace_alpha(alpha);return {'type':'path','id':'v19-'+name+'-glyphs','d':d,'fill':color},ink,stats
plus,pi,pstats=traced('plus',87,[196,338,241,381]);mic,mi,mstats=traced('mic',21,[715,334,756,390]);placeholder,hi,hstats=traced('placeholder',21,[299,337,451,387]);phrase,ti,tstats=traced('typed-phrase',87,[300,340,668,387]);phrase['semanticText']="Yo i'm bored, chess battle?";placeholder['semanticText']='iMessage';plus['semanticText']='+'
arrow,ai,astats=traced('send-arrow',87,[706,339,740,382],'white')
# Generic independent component calibration against one original static graphic.
def fit_component(frame,ink,box,roi,exclude_caret=False):
 ar=src[frame];target=255-ar.mean(2);target[ar[:,:,2]-ar[:,:,0]>20]=0;x0,y0,x1,y1=roi;xx,yy=np.meshgrid(np.arange(x0,x1),np.arange(y0,y1));keep=np.ones(xx.shape,bool)
 if exclude_caret:keep &= xx>309
 xx=xx[keep];yy=yy[keep];obs=target[yy,xx];weight=np.maximum(obs-8,0);total=weight.sum()
 if total<30:return {'x':float(box[0]),'y':float(box[1]),'scaleX':1.,'scaleY':1.,'opacity':0.}
 ry,rx=np.mgrid[:ink.shape[0],:ink.shape[1]];rw=np.maximum(ink-8,0);rn=rw.sum();rcx=float((rx*rw).sum()/rn);rcy=float((ry*rw).sum()/rn);cx=float((xx*weight).sum()/total);cy=float((yy*weight).sum()/total)
 sx=float(np.clip(np.sqrt((weight*(xx-cx)**2).sum()/total/max((rw*(rx-rcx)**2).sum()/rn,1)),.65,1.3));sy=float(np.clip(np.sqrt((weight*(yy-cy)**2).sum()/total/max((rw*(ry-rcy)**2).sum()/rn,1)),.45,1.5));x=cx-sx*rcx;y=cy-sy*rcy
 def sample(q):return map_coordinates(ink,[(yy-q[1])/q[3],(xx-q[0])/q[2]],order=1,mode='constant',cval=0,prefilter=False)
 def evaluate(q):
  model=sample(q);op=float(np.clip(model@obs/max(model@model,1),0,1));return(model*op-obs)/30,op
 fit=least_squares(lambda q:evaluate(q)[0],[x,y,sx,sy],bounds=([x-20,y-30,.4,.25],[x+20,y+30,1.6,1.8]),max_nfev=55,diff_step=[.0001,.0001,.0001,.0001]);op=evaluate(fit.x)[1];return dict(zip(['x','y','scaleX','scaleY'],map(float,fit.x)),opacity=op if op>.01 else 0.)
plusrows=[];microws=[];hrows=[]
for f in range(99):
 p=anchor['rows'][f]['detection'];pb=p.get('plus')if p else None
 if pb:
  sx=(pb[2]-pb[0])/29;sy=(pb[3]-pb[1])/29;pose={'x':pb[0]-sx*8,'y':pb[1]-sy*6,'scaleX':sx,'scaleY':sy,'opacity':1.}
 else:pose=fit_component(f,pi,[196,338,241,381],[175,300,265,455])
 plusrows.append(dict(frame=f,**pose))
 if f<23:
  microws.append(dict(frame=f,**fit_component(f,mi,[715,334,756,390],[695,285,780,465])))
  hrows.append(dict(frame=f,**fit_component(f,hi,[299,337,451,387],[290,285,465,465],True)))
# White body entry is measured on empty shadow regions, independently of glyph births.
bodyref=src[21].mean(2).copy();bodyref[325:395,195:247]=255;bodyref[332:392,296:455]=255;bodyref[330:396,710:762]=255;bi=255-bodyref;xx,yy=np.meshgrid(np.r_[np.arange(160,190,3),np.arange(250,270,3),np.arange(470,635,3)],np.arange(250,480,2));xx=xx.ravel();yy=yy.ravel();bodyrows=[]
for f in range(23):
 obs=255-src[f].mean(2)[yy,xx]
 if obs.max()<.5:bodyrows.append({'frame':f,'x':0.,'y':0.,'scaleX':1.,'scaleY':1.,'opacity':0.});continue
 def evaluate(q):
  dy,sy=q;model=map_coordinates(bi,[(yy-dy)/sy,xx],order=1,mode='constant',cval=0,prefilter=False);op=float(np.clip(model@obs/max(model@model,1),0,1));return(model*op-obs)/5,op
 initial=[35 if f<3 else 8 if f==3 else 3 if f==4 else 0,1.];fit=least_squares(lambda q:evaluate(q)[0],initial,bounds=([-60,.4],[120,1.5]),max_nfev=55,diff_step=[.001,.0001]);bodyrows.append({'frame':f,'x':0.,'y':float(fit.x[0]),'scaleX':1.,'scaleY':float(fit.x[1]),'opacity':evaluate(fit.x)[1]})
# Actual prefix support and actual cursor color are measured frame by frame.
cols=np.any(ti>80,axis=0);runs=[];start=None
for x,v in enumerate(np.r_[cols,False]):
 if v and start is None:start=x
 if not v and start is not None:runs.append((start,x));start=None
clips=[];carets=[];send=[]
for f in range(99):
 a=src[f];cam=cams[f];tx,ty,sx,sy=[cam[k]for k in ['x','y','scaleX','scaleY']];v=a.mean(2);xx,yy=np.mgrid[0:720,0:960];u=(yy-tx)/sx;w=(xx-ty)/sy;mask=(u>295)&(u<678)&(w>330)&(w<393);chroma=np.maximum(a[:,:,2]-a[:,:,0],0)*mask;strong=(chroma>18);labs,n=label(strong);choices=[]
 for k,sl in enumerate(find_objects(labs),1):
  if sl is None:continue
  yr,xr=sl;wid=xr.stop-xr.start;hei=yr.stop-yr.start
  if wid<12 and hei>24:choices.append((float(chroma[sl].sum()),[xr.start,yr.start,xr.stop,yr.stop]))
 if choices:
  _,bb=max(choices);x0=max(0,bb[0]-2);x1=min(960,bb[2]+2);y0=max(0,bb[1]-2);y1=min(720,bb[3]+2);patch=chroma[y0:y1,x0:x1];py,px=np.mgrid[y0:y1,x0:x1];mass=patch.sum();cx=float((px*patch).sum()/mass);cy=float((py*patch).sum()/mass);op=float(np.clip(mass/(255*2*42*sx*sy),0,1));carets.append({'frame':f,'x':(cx-sx-tx)/sx,'y':(cy-21*sy-ty)/sy,'opacity':op})
 else:carets.append({'frame':f,'x':303.,'y':339.,'opacity':0.})
 dark=(a.max(2)<150)&(a.max(2)-a.min(2)<18)&(u>295)&(u<678)&(w>335)&(w<390);_,xs=np.where(dark)
 if f<23 or len(xs)==0:width=0.
 else:
  right=(float(xs.max()+1)-tx)/sx-300;idx=int(np.argmin([abs(end-right)for start,end in runs]));end=runs[idx][1];width=(end+runs[idx+1][0])/2 if idx+1<len(runs)else 368.
 clips.append({'frame':f,'width':float(width)})
 region=src[f][330:394,682:773];blue=np.maximum(region[:,:,2]-region[:,:,0],0).sum();refblue=np.maximum(src[87][330:394,682:773,2]-src[87][330:394,682:773,0],0).sum();send.append({'frame':f,'opacity':float(np.clip(blue/refblue,0,1))if f>=23 else 0.})

def keys(rows,names):return{k:[{'t':r['frame']/30,'value':round(float(r[k]),6),'ease':'linear'}for r in rows]for k in names}
def localrows(rows):
 out=[]
 for r in rows:
  c=cams[r['frame']];out.append(dict(r,x=(r['x']-c['x'])/c['scaleX'],y=(r['y']-c['y'])/c['scaleY'],scaleX=r['scaleX']/c['scaleX'],scaleY=r['scaleY']/c['scaleY']))
 return out
oldbody=next(q for q in s['layers']if q['id']=='g-6');circle=copy.deepcopy(oldbody['children'][0]);rect=copy.deepcopy(oldbody['children'][1]);circle['id']='v19-plus-white-body';rect['id']='v19-input-white-body';body={'type':'group','id':'v19-composer-white-body','children':[circle,rect],'keyframes':keys(bodyrows+[{'frame':23,'x':0,'y':0,'scaleX':1,'scaleY':1,'opacity':1}],['x','y','scaleX','scaleY','opacity'])}
plusnode={'type':'group','id':'v19-composer-plus','children':[plus],'keyframes':keys(localrows(plusrows),['x','y','scaleX','scaleY','opacity'])}
micnode={'type':'group','id':'v19-composer-mic','end':23/30,'children':[mic],'keyframes':keys(microws,['x','y','scaleX','scaleY','opacity'])}
hnode={'type':'group','id':'v19-composer-placeholder','end':23/30,'children':[placeholder],'keyframes':keys(hrows,['x','y','scaleX','scaleY','opacity'])}
blue=copy.deepcopy(oldbody['children'][3]);blue['id']='v19-send-blue-body';blue['height']=56;sendnode={'type':'group','id':'v19-composer-send','start':23/30,'children':[blue,dict(arrow,x=706,y=339)],'keyframes':keys(send,['opacity'])}
textnode={'type':'group','id':'v19-composer-typing-viewport','x':300,'y':340,'start':23/30,'clip':{'x':0,'y':0,'width':368,'height':47},'children':[phrase],'keyframes':{'clipWidth':[{'t':0,'value':0}]}}
# Clip width is expressed as a native horizontal scale/reciprocal child pair.
# This avoids schema extensions and retains the unscaled original glyph shapes.
textnode.pop('keyframes');textnode['clip']['width']=368
cliprows=[dict(r,scaleX=max(r['width']/368,1e-6))for r in clips]
textnode['keyframes']=keys(cliprows,['scaleX']);textnode['children']=[{'type':'group','id':'v19-composer-typing-inverse','children':[phrase],'keyframes':{'scaleX':[{'t':r['frame']/30,'value':1/max(r['width']/368,1e-6),'ease':'linear'}for r in clips]}}]
caret={'type':'rect','id':'v19-composer-caret','width':2,'height':42,'fill':'#0088ff','keyframes':keys(carets,['x','y','opacity'])}
intro={'type':'group','id':'v19-intro-composer','start':0,'end':99/30,'children':[body,plusnode,micnode,hnode,sendnode,textnode,caret],'keyframes':{k:[{'t':f/30,'value':round(float(cams[f][k]),6),'ease':'linear'}for f in range(99)]for k in ['x','y','scaleX','scaleY']}}
oldroots=[q for q in s['layers']if q.get('end',999)<=99/30];ids=[q['id']for q in oldroots];first=min(s['layers'].index(q)for q in oldroots);s['layers']=[q for q in s['layers']if q['id']not in ids];s['layers'].insert(first,intro)
# Cash: replace only the guessed interpolation tail using its independent plus anchor.
cash=next(q for q in s['layers']if q['id']=='linq-measured-v6-group-36');composer=next(q for q in cash['children']if q['id']=='v10-cash-composer');panel=next(q for q in cash['children']if q['id']=='v10-cash-panel');im=composer['children'][0];ar=np.array(Image.open(im['src']).convert('RGB')).astype(float).mean(2);ink=255-ar
m=(ar<150);m[:,100:]=False;ys,xs=np.where(m);cy=(ys.min()+ys.max()+1)/2;cashrows=[]
for f in range(818,827):
 a=load(f).mean(2);py=next(z['value']for z in panel['keyframes']['y']if abs(z['t']*30-f)<1e-5);xx,yy=np.meshgrid(np.arange(185,255),np.arange(max(0,int(126+py)-8),min(720,int(230+py))));target=255-a[yy,xx]
 def residual(q):
  pred=map_coordinates(ink,[yy-126-q[0],xx-172],order=1,mode='constant',cval=0,prefilter=False);return(pred-target).ravel()/30
 fit=least_squares(residual,[py],bounds=([py-8],[py+8]),max_nfev=50,diff_step=[.001]);dy=round(float(fit.x[0]),6);old=next(z['value']for z in composer['keyframes']['y']if abs(z['t']*30-f)<1e-5)if any(abs(z['t']*30-f)<1e-5 for z in composer['keyframes']['y'])else None
 composer['keyframes']['y']=[z for z in composer['keyframes']['y']if abs(z['t']*30-f)>1e-5]+[{'t':f/30,'value':dy,'ease':'linear'}];cashrows.append({'frame':f,'y':dy,'panelPriorY':py,'oldExplicitKey':old})
composer['keyframes']['y'].sort(key=lambda z:z['t'])
out=D/'scene-composers-v19.json';out.write_text(json.dumps(s,indent=2)+'\n');(D/'measurements/composer-v19/measurements.json').write_text(json.dumps({'removedIntroRootIDs':ids,'closingCameras':cams,'plus':plusrows,'mic':microws,'placeholder':hrows,'body':bodyrows,'typingClips':clips,'carets':carets,'sendOpacity':send,'cash':cashrows,'traces':{'plus':pstats,'mic':mstats,'placeholder':hstats,'phrase':tstats,'arrow':astats},'notice':'All source images are analysis references only. Native paths are each traced once; numeric native poses, typing clip and control lifetimes carry motion.'},indent=2)+'\n');print('OUTPUT',out,'removed',ids,'cash',cashrows)
