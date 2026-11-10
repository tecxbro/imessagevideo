"""Local independent photographic actor fit. No source-frame assets or canonical mutation."""
from pathlib import Path
import json,sys,copy,numpy as np
from PIL import Image
from scipy.optimize import minimize
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(BASE/'scene.json'));rp.register_fonts(S,str(BASE));W,H=480,270;rows=[]
for f,ident,material in [(614,'79','source622'),(615,'79','source622'),(613,'79','source622'),(614,'71','original'),(615,'71','original'),(613,'71','original')]:
 t=f/30;idx,g=next((i,copy.deepcopy(n))for i,n in enumerate(S['layers'])if n.get('semanticPhotoId')=='rene-final11-group-'+ident and n.get('start',0)<=t<n.get('end',99));state=rp.state(g,t);child=g['children'][0];ow,oh=child['width'],child['height'];D=ow*state['scaleX'];cx=state['x']+D/2;cy=state['y']+oh*state['scaleY']/2;b=state['blur']*state['scaleX']
 if material=='source622':
  child.update(src=str(R/'references/06-gallery/giant-material-v21/portrait79-source622-material.png'),width=512,height=512)
  for k in ('x','y','blur'):g['shadow'][k]*=512/ow
 w,h=child['width'],child['height'];g.pop('keyframes',None);g.update(start=0,end=99,opacity=1)
 def full(ls,bg):return np.array(rp.render({**S,'layers':ls,'background':bg},t,str(BASE)).resize((W,H),Image.Resampling.LANCZOS),dtype=float)/255
 below=full(S['layers'][:idx],S.get('background','#ffffff'));ab=full(S['layers'][idx+1:],'#000000');aw=full(S['layers'][idx+1:],'#ffffff');aa=np.clip(1-np.mean(aw-ab,axis=2,keepdims=True),0,1);ref=np.array(Image.open(P/'source'/f'{f:06}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS),dtype=float)/255
 if ident=='79':
  bounds=[(cx-150,cx+150),(cy-250,cy+250),(D*.78,D*1.18),(D*.78,D*1.18),(max(0,b-50),b+50),(0,1.5)];initial=[cx,cy,D,D,b,1]
  if f==614:initial=[1350,1402,1600,1600,60,1]
  roi=np.zeros((H,W),bool);roi[140:,180:]=True
 else:
  bounds=[(cx-25,cx+25),(cy-90,cy+50),(D*.8,D*1.4),(D*.8,D*1.4),(0,25),(0,1.5)];initial=[cx,cy,D,D,min(b,20),1]
  if f==614:initial=[402,-21,340,340,12,1]
  roi=np.zeros((H,W),bool);roi[:max(1,min(H,round((cy+D*.7)/4))),max(0,round((cx-D*.7)/4)):min(W,round((cx+D*.7)/4))]=True
 history=[]
 def evaluate(z):
  xx,yy,dx,dy,blur,sh=map(float,z);q=copy.deepcopy(g);q.update(x=(xx-dx/2)/4,y=(yy-dy/2)/4,scaleX=dx/w/4,scaleY=dy/h/4,blur=blur/(dx/w));q['shadow']['color']='#000000'+format(round(34*sh),'02x')
  def rgb(bg):return np.array(rp.render({**S,'width':W,'height':H,'layers':[q],'background':bg},t,str(BASE)),dtype=float)/255
  black=rgb('#000000');white=rgb('#ffffff');alpha=np.clip(1-np.mean(white-black,axis=2,keepdims=True),0,1);out=ab+(1-aa)*(black+(1-alpha)*below);delta=out-ref;err=float(np.mean(abs(delta[roi]))*255);mse=float(np.mean(delta[roi]**2)*255**2);r=dict(frame=f,photo=ident,material=material,cx=xx,cy=yy,dx=dx,dy=dy,blur=blur,shadow=sh,roiMAE=err,roiMSE=mse,fullMAE=float(abs(delta).mean()*255));history.append(r)
  if len(history)%100==0:print('progress',f,ident,len(history),min(x['roiMAE']for x in history),flush=True)
  return err
 initial=np.clip(initial,np.array(bounds)[:,0],np.array(bounds)[:,1]);evaluate(initial);fit=minimize(evaluate,initial,method='Powell',bounds=bounds,options={'maxiter':4,'xtol':.05,'ftol':.0005});best=min(history,key=lambda r:r['roiMAE']);result=dict(frame=f,photo=ident,baseline=history[0],best=best,evaluations=len(history));rows.append(result);print('RESULT',result,flush=True);(P/'independent-fit.json').write_text(json.dumps(rows,indent=2));rp.LEAF_CACHE.clear();rp.GROUP_CACHE.clear();rp.FAST_CACHE.clear()
