"""Refine component support and glyph lifecycles after native preview diagnosis."""
from pathlib import Path
import json,copy,importlib.util
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects,distance_transform_edt,map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'measurements/composer-v19/native';s=json.loads((D/'scene-composers-v19.json').read_text());data=json.loads((D/'measurements/composer-v19/measurements.json').read_text());intro=next(q for q in s['layers']if q['id']=='v19-intro-composer');by={q['id']:q for q in intro['children']}
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
def load(f):return np.array(Image.open(F/f'source-{f:06d}.png').convert('RGB')).astype(float)
# Restore the actual complete placeholder shape from the pre-caret reference.
a=load(12)[337:387,299:451];gray=a.mean(2);fg=float(np.percentile(gray[gray<220],5));alpha=np.clip((255-gray)/(255-fg),0,1);alpha[a[:,:,2]-a[:,:,0]>20]=0;hd,hs=trace.trace_alpha(alpha);hn=by['v19-composer-placeholder']['children'][0];hn['d']=hd;hn['fill']='#'+('%02x'%round(fg))*3;hi=alpha*(255-fg)
# High-pass component support prevents faint body shadows from pulling glyph geometry.
def fit(frame,ink,box,roi,exclude=False):
 a=load(frame);target=255-a.mean(2);target[a[:,:,2]-a[:,:,0]>20]=0;x0,y0,x1,y1=roi;xx,yy=np.meshgrid(np.arange(x0,x1),np.arange(y0,y1));keep=(xx>309)if exclude else np.ones(xx.shape,bool);xx=xx[keep];yy=yy[keep];raw=target[yy,xx];obs=np.maximum(raw-12,0);hp=np.maximum(ink-12,0);w=np.maximum(obs-4,0);total=w.sum()
 if total<20:return dict(x=box[0],y=box[1],scaleX=1.,scaleY=1.,opacity=0.)
 ry,rx=np.mgrid[:ink.shape[0],:ink.shape[1]];rw=np.maximum(hp-4,0);rn=rw.sum();rcx=(rx*rw).sum()/rn;rcy=(ry*rw).sum()/rn;cx=(xx*w).sum()/total;cy=(yy*w).sum()/total;sx=float(np.clip(np.sqrt((w*(xx-cx)**2).sum()/total/max((rw*(rx-rcx)**2).sum()/rn,1)),.65,1.3));sy=float(np.clip(np.sqrt((w*(yy-cy)**2).sum()/total/max((rw*(ry-rcy)**2).sum()/rn,1)),.45,1.5));x=float(cx-sx*rcx);y=float(cy-sy*rcy)
 def model(q,im):return map_coordinates(im,[(yy-q[1])/q[3],(xx-q[0])/q[2]],order=1,mode='constant',cval=0,prefilter=False)
 def residual(q):
  m=model(q,hp);op=float(np.clip(m@obs/max(m@m,1),0,1));return(m*op-obs)/30
 z=least_squares(residual,[x,y,sx,sy],bounds=([x-15,y-20,.4,.25],[x+15,y+20,1.6,1.8]),max_nfev=60,diff_step=[.0001,.0001,.0001,.0001]).x;m=model(z,ink);valid=m>15;op=float(np.clip(m[valid]@raw[valid]/max(m[valid]@m[valid],1),0,1))if valid.any()else 0.;return dict(zip(['x','y','scaleX','scaleY'],map(float,z)),opacity=op if op>.01 else 0.)
# Mic source remains the same genuine static graphic; fit its core rather than shadow.
a=load(21)[334:390,715:756];gray=a.mean(2);mfg=float(np.percentile(gray[gray<220],5));mi=np.clip((255-gray)/(255-mfg),0,1)*(255-mfg)
hr=[];mr=[]
for f in range(23):hr.append(dict(frame=f,**fit(f,hi,[299,337,451,387],[290,285,465,465],True)));mr.append(dict(frame=f,**fit(f,mi,[715,334,756,390],[695,285,780,465])))
def keys(rows):return{k:[{'t':r['frame']/30,'value':round(float(r[k]),6),'ease':'linear'}for r in rows]for k in ['x','y','scaleX','scaleY','opacity']}
by['v19-composer-placeholder']['keyframes']=keys(hr);by['v19-composer-mic']['keyframes']=keys(mr)
# Send remains opaque after its actual birth; a stationary sampling ROI is invalid after exit motion.
for k in by['v19-composer-send']['keyframes']['opacity']:
 if round(k['t']*30)>=27:k['value']=1.
# Measured effective blue appearance also preserves the source's early tint.
send=by['v19-composer-send'];blue=send['children'][0];arrow=send['children'][1];newblue=[];ref=load(87);yy,xx=np.mgrid[330:394,682:773];mask=((xx-726.5)/32)**2+((yy-360)/22)**2<1;mask &= ref[330:394,682:773,0]<40
for f in [24,25,26,27]:
 color=np.median(load(f)[330:394,682:773][mask],axis=0).round().astype(int);node=copy.deepcopy(blue);node['id']=f'v19-send-color-{f}';node['fill']='#'+''.join(f'{v:02x}'for v in color);node['start']=f/30
 if f<27:node['end']=(f+1)/30
 newblue.append(node)
send['children']=newblue+[arrow];send['start']=24/30;send.pop('keyframes',None)
# Split original glyphs in2D. A1D column clip cannot separate kerned Y/o support.
a=load(87)[340:387,300:668];gray=a.mean(2);pfg=float(np.percentile(gray[gray<220],5));pa=np.clip((255-gray)/(255-pfg),0,1);pa[(a[:,:,2]-a[:,:,0]>40)&(a[:,:,2]>170)]=0;core=pa>.5;labs,n=label(core);components=[]
for k,sl in enumerate(find_objects(labs),1):
 if sl is None:continue
 y,x=sl;area=int((labs[sl]==k).sum())
 if area>=2:components.append({'labels':[k],'area':area,'cx':(x.start+x.stop)/2,'box':[x.start,y.start,x.stop,y.stop]})
small=[c for c in components if c['area']<=3];components=[c for c in components if c['area']>3]
for c in small:
 nearest=min(components,key=lambda z:abs(z['cx']-c['cx']));assert abs(nearest['cx']-c['cx'])<=6;nearest['labels']+=c['labels']
components.sort(key=lambda z:z['cx']);groups=[]
for c in components:
 if groups and abs(c['cx']-groups[-1]['cx'])<3.5:groups[-1]['labels']+=c['labels']
 else:groups.append(c)
chars=[c for c in "Yo i'm bored, chess battle?"if c!=' '];assert len(groups)==len(chars),(len(groups),len(chars),groups)
_,indices=distance_transform_edt(~core,return_indices=True);nearest=labs[tuple(indices)];pieces=[];paths=[]
for i,(group,ch)in enumerate(zip(groups,chars)):
 mask=np.isin(nearest,group['labels']);aa=pa*mask;pieces.append(aa*(255-pfg));d,stats=trace.trace_alpha(aa);paths.append({'type':'path','id':f'v19-type-glyph-{i}','d':d,'fill':'#'+('%02x'%round(pfg))*3,'semanticText':ch})
cumulative=np.concatenate([np.zeros((1,*pa.shape)),np.cumsum(np.stack(pieces),axis=0)],axis=0);yy,xx=np.mgrid[:pa.shape[0],:pa.shape[1]];counts=[];previous=0
for f in range(99):
 if f<23:count=0
 else:
  a=load(f);cam=data['closingCameras'][str(f)];gx=cam['x']+cam['scaleX']*(300+xx);gy=cam['y']+cam['scaleY']*(340+yy);ar=np.stack([map_coordinates(a[:,:,c],[gy,gx],order=1,mode='constant',cval=255,prefilter=False)for c in range(3)],axis=2);target=255-ar.mean(2);target[(ar[:,:,2]-ar[:,:,0]>40)&(ar[:,:,2]>170)]=0;err=np.mean((cumulative-target[None,:,:])**2,axis=(1,2));err[:previous]=np.inf;count=int(np.argmin(err));previous=count
 counts.append(count)
for i,p in enumerate(paths):p['start']=next(f/30 for f,k in enumerate(counts)if k>i)
new={'type':'group','id':'v19-composer-typed-glyphs','x':300,'y':340,'start':23/30,'semanticText':"Yo i'm bored, chess battle?",'children':paths};old=by['v19-composer-typing-viewport'];intro['children'][intro['children'].index(old)]=new
s['rebuildRevision']='v19-composers-preview';out=D/'scene-composers-v19-refined.json';out.write_text(json.dumps(s,indent=2)+'\n');(D/'measurements/composer-v19/refinement.json').write_text(json.dumps({'placeholder':hr,'mic':mr,'glyphCharacters':chars,'glyphCountByFrame':counts,'glyphStarts':[p['start']*30 for p in paths],'glyphGroups':groups,'notice':'One original native path per glyph; 2D separation preserves kerning without leaking the next character. Original caret and independent camera are measured. No source frame sequence renders.'},indent=2)+'\n');print('glyphs',len(paths),'starts',[round(p['start']*30)for p in paths]);print(out)
