"""Fit a finite native near-plane anchor against screen pixels, not hidden samples."""
from pathlib import Path
import copy,json,sys,itertools
import numpy as np
from PIL import Image
from scipy.optimize import minimize
P=Path(__file__).parent;B=P/'portrait-helper-v18';sys.path.insert(0,str(P.parents[1]/'engines'));import render_pillow
S=json.load(open(B/'combined-validation.scene.json'));data=json.load(open(B/'camera-fit-frozen-v18.json'));frame=613;t=frame/30;id='79';groups=[g for g in S['layers']if g.get('semanticPhotoId')=='rene-final11-group-'+id and g.get('start',0)<=t<g.get('end',S['duration'])];assert len(groups)==1;g=copy.deepcopy(groups[0]);w,h=g['children'][0]['width'],g['children'][0]['height'];g['keyframes']={};g['opacity']=1.;W,H=480,270
base=copy.deepcopy(S);base['layers']=[x for x in base['layers']if x['id']!=g['id']];background=np.asarray(render_pillow.render(base,t,str(P)).resize((W,H),Image.Resampling.LANCZOS),dtype=np.float32)/255;ref=np.asarray(Image.open(P/f'native-transition-v18/{frame:06d}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS),dtype=np.float32)/255
history=[]
def evaluate(z,detail=False):
 u,top,D,bf=map(float,z);cx=960+u*D;cy=top+D/2;g.update(x=cx-D/2,y=cy-D/2,scaleX=D/w,scaleY=D/h,blur=bf*w)
 def rgb(bg):
  q=copy.deepcopy(g);q.update(x=q['x']/4,y=q['y']/4,scaleX=q['scaleX']/4,scaleY=q['scaleY']/4);s={**S,'layers':[q],'background':bg,'width':W,'height':H};return np.asarray(render_pillow.render(s,t,str(P)),dtype=np.float32)/255
 black=rgb('#000000');white=rgb('#ffffff');alpha=np.clip(1-np.mean(white-black,axis=2,keepdims=True),0,1);diff=black-alpha*background;den=float(np.sum(diff*diff));opacity=float(np.clip(np.sum(diff*(ref-background))/max(1e-6,den),0,1));F=background+opacity*diff;loss=float(np.mean((F-ref)**2)*255**2);mae=float(np.mean(abs(F-ref))*255);rec={'u':u,'top':top,'diameter':D,'blurFraction':bf,'cx':cx,'cy':cy,'opacity':opacity,'mse':loss,'mae':mae};history.append(rec)
 if detail:return rec
 return loss+.03*((D-3155)/3155)**2
best=json.load(open(B/'bounded-entry-v19-coarse-checkpoint.json'))
evaluate([best[k]for k in ['u','top','diameter','blurFraction']],True)
z=[best[k]for k in ['u','top','diameter','blurFraction']];result=minimize(evaluate,z,method='Powell',bounds=[(.15,.85),(650,2200),(1800,8000),(.015,.28)],options={'maxiter':5,'xtol':.08,'ftol':.0003});final=evaluate(result.x,True);allbest=min(history,key=lambda r:r['mse']);report={'frame':frame,'photo':id,'baseline_mae':float(np.mean(abs(background-ref))*255),'best':allbest,'last':final,'evaluations':len(history),'constraint':'Finite native disc; body leading edge650–2200, diameter1800–8000. Opacity is derived from actual native RGB matte energy. No source pixels are an output asset.'};(B/'bounded-entry-v19.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT',report,flush=True)
