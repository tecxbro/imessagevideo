"""Bounded native scene registration of giant615/614 photograph nodes.
Each evaluation changes one editable photo camera; other graphics stay native.
"""
from pathlib import Path
import copy,json,sys,math
import numpy as np
from PIL import Image
from scipy.optimize import minimize
P=Path(__file__).parent;B=P/'portrait-helper-v18';sys.path.insert(0,str(P.parents[1]/'engines'));import render_pillow
S=json.load(open(B/'combined-validation.scene.json'));W,H=480,270;updates=[];reports=[]
def active_group(scene,frame,id):
 t=frame/30;ls=[(i,g)for i,g in enumerate(scene['layers'])if g.get('semanticPhotoId')=='rene-final11-group-'+id and g.get('start',0)<=t<g.get('end',scene['duration'])];assert len(ls)==1,(frame,id);return ls[0]
def update(scene,frame,id,rec):
 _,g=active_group(scene,frame,id);w,h=g['children'][0]['width'],g['children'][0]['height'];values={'x':rec['cx']-rec['diameter']/2,'y':rec['cy']-rec['diameter']/2,'scaleX':rec['diameter']/w,'scaleY':rec['diameter']/h,'blur':rec['blurFraction']*w,'opacity':rec['opacity']}
 for key,value in values.items():
  keys=g['keyframes'][key];keys[:]=[q for q in keys if abs(q['t']-frame/30)>1e-9];keys.append({'t':frame/30,'value':float(value),'ease':'linear'});keys.sort(key=lambda q:q['t'])
 return g
# The already measured offscreen613 anchor is part of the same tiny release.
r=json.load(open(B/'bounded-entry-v19.json'))['best'];update(S,613,'79',r);updates.append({'frame':613,'photo':'79',**r})
for frame,id in [(614,'79'),(614,'77'),(615,'79'),(615,'77')]:
 index,original=active_group(S,frame,id);g=copy.deepcopy(original);state=render_pillow.state(g,frame/30);w,h=g['children'][0]['width'],g['children'][0]['height'];D=(state['scaleX']*w+state['scaleY']*h)/2;initial=np.array([state['x']+D/2,state['y']+D/2,D,state['blur']/w]);g['keyframes']={};g['opacity']=1.
 def full_rgb(ls,bg):
  s={**S,'layers':ls,'background':bg};return np.asarray(render_pillow.render(s,frame/30,str(P)).resize((W,H),Image.Resampling.LANCZOS),dtype=np.float32)/255
 below=full_rgb(S['layers'][:index],S.get('background','#ffffff'));above_black=full_rgb(S['layers'][index+1:],'#000000');above_white=full_rgb(S['layers'][index+1:],'#ffffff');above_alpha=np.clip(1-np.mean(above_white-above_black,axis=2,keepdims=True),0,1);ref=np.asarray(Image.open(P/f'native-transition-v18/{frame:06d}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS),dtype=np.float32)/255;history=[]
 def evaluate(z,detail=False):
  cx,cy,d,bf=map(float,z);q=copy.deepcopy(g);q.update(x=(cx-d/2)/4,y=(cy-d/2)/4,scaleX=d/w/4,scaleY=d/h/4,blur=bf*w)
  def rgb(bg):
   s={**S,'width':W,'height':H,'layers':[q],'background':bg};return np.asarray(render_pillow.render(s,frame/30,str(P)),dtype=np.float32)/255
  black=rgb('#000000');white=rgb('#ffffff');alpha=np.clip(1-np.mean(white-black,axis=2,keepdims=True),0,1);base=above_black+(1-above_alpha)*below;diff=(1-above_alpha)*(black-alpha*below);den=float(np.sum(diff*diff));opacity=float(np.clip(np.sum(diff*(ref-base))/max(1e-6,den),.2 if frame==614 else .7,1));F=base+opacity*diff;mse=float(np.mean((F-ref)**2)*255**2);mae=float(np.mean(abs(F-ref))*255);rec={'cx':cx,'cy':cy,'diameter':d,'blurFraction':bf,'opacity':opacity,'mse':mse,'mae':mae};history.append(rec)
  if detail:return rec
  return mse+.05*math.log(d/D)**2
 before=evaluate(initial,True);dx=D*(.16 if frame==614 else .10);bounds=[(initial[0]-dx,initial[0]+dx),(initial[1]-dx,initial[1]+dx),(D*.82,D*1.18),(.001,.14)];print('begin',frame,id,'baseline',before,flush=True)
 fit=minimize(evaluate,initial,method='Powell',bounds=bounds,options={'maxiter':5,'xtol':.05,'ftol':.0002});evaluate(fit.x,True);best=min(history,key=lambda r:r['mse']);accepted=best['mse']<before['mse']-.1
 if accepted:update(S,frame,id,best);updates.append({'frame':frame,'photo':id,**best})
 report={'frame':frame,'photo':id,'before':before,'best':best,'accepted':accepted,'evaluations':len(history)};reports.append(report);print('RESULT',report,flush=True);(B/'native-giant-v19-progress.json').write_text(json.dumps({'updates':updates,'reports':reports},indent=2)+'\n')
(B/'native-giant-v19-updates.json').write_text(json.dumps({'updates':updates,'reports':reports},indent=2)+'\n');(B/'native-giant-v19-validation.scene.json').write_text(json.dumps(S,indent=2)+'\n')
