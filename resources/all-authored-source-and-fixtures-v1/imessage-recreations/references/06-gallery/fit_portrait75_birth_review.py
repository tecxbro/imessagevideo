"""Dense actual missing portrait75 birth; no canonical or final video writers."""
from pathlib import Path
import copy,json,sys,numpy as np
from PIL import Image
from scipy.optimize import minimize
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(P/'continuation-fit.scene.json'));rp.register_fonts(S,str(BASE));rows=[];W,H=480,270
for f in [618,617,616,619,620]:
 t=f/30;idx,g=next((i,copy.deepcopy(n))for i,n in enumerate(S['layers'])if n.get('semanticPhotoId')=='rene-final11-group-75'and n.get('start',0)<=t<n.get('end',99));w,h=g['children'][0]['width'],g['children'][0]['height'];g.pop('keyframes',None);g.update(start=0,end=99,opacity=1)
 def full(ls,bg):return np.array(rp.render({**S,'layers':ls,'background':bg},t,str(BASE)).resize((W,H),Image.Resampling.LANCZOS),dtype=float)/255
 below=full(S['layers'][:idx],S.get('background','#ffffff'));ab=full(S['layers'][idx+1:],'#000000');aw=full(S['layers'][idx+1:],'#ffffff');aa=np.clip(1-np.mean(aw-ab,axis=2,keepdims=True),0,1);ref=np.array(Image.open(P/'source'/f'{f:06}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS),dtype=float)/255;roi=np.zeros((H,W),bool);roi[105:185,100:220]=True;roi &= aa[:,:,0]<.8;hist=[]
 def fun(z):
  cx,cy,d,blur,op=map(float,z);q=copy.deepcopy(g);q.update(x=(cx-d/2)/4,y=(cy-d/2)/4,scaleX=d/w/4,scaleY=d/h/4,blur=blur/(d/w),opacity=op)
  def rgb(bg):return np.array(rp.render({**S,'width':W,'height':H,'layers':[q],'background':bg},t,str(BASE)),dtype=float)/255
  b=rgb('#000000');v=rgb('#ffffff');a=np.clip(1-np.mean(v-b,axis=2,keepdims=True),0,1);out=ab+(1-aa)*(b+(1-a)*below);delta=out-ref;r=dict(frame=f,cx=cx,cy=cy,diameter=d,blurWorld=blur,opacity=op,roiMAE=float(abs(delta[roi]).mean()*255),fullMAE=float(abs(delta).mean()*255));hist.append(r);return r['roiMAE']
 cx={616:555,617:595,618:630,619:668,620:703}[f];initial=[cx,585,180,2,1];bounds=[(cx-65,cx+65),(510,660),(100,280),(0,18),(0,1)];fun(initial);fit=minimize(fun,initial,method='Powell',bounds=bounds,options={'maxiter':5,'xtol':.05,'ftol':.0005});best=min(hist,key=lambda r:r['roiMAE']);rows.append(dict(frame=f,initial=hist[0],best=best,evaluations=len(hist)));print(rows[-1],flush=True);(P/'photo75-birth-fit.json').write_text(json.dumps(rows,indent=2));rp.LEAF_CACHE.clear();rp.GROUP_CACHE.clear();rp.FAST_CACHE.clear()
