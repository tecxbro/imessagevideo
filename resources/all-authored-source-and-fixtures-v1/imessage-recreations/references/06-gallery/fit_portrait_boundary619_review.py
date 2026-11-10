"""Independently fit genuine static photo cameras in only native613–615."""
from pathlib import Path
import copy,json,sys,numpy as np
from PIL import Image
from scipy.optimize import minimize
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(R/'outputs/06-gallery/portrait614-review-01/scene.json'))
def absolute(ls):
 for n in ls:
  if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((R/'outputs/06-gallery/portrait614-review-01'/n['src']).resolve())
  absolute(n.get('children',[]))
absolute(S['layers'])
for font in S.get('fonts',[]):
 if not font['src'].startswith(('/','data:','http:','https:')):font['src']=str((R/'outputs/06-gallery/portrait614-review-01'/font['src']).resolve())
rp.register_fonts(S,str(BASE));W,H=480,270;reports=[];N=512
seed=json.load(open(P/'independent-fit.json')) if (P/'independent-fit.json').exists() else []
def apply(g,r):
 child=g['children'][0];ow,oh=child['width'],child['height']
 if r.get('material')=='source622' and ow!=N:
  child.update(src=str(R/'references/06-gallery/giant-material-v21/portrait79-source622-material.png'),width=N,height=N)
  for k in ('x','y','blur'):g['shadow'][k]*=N/ow
 w,h=child['width'],child['height'];dx,dy=r['dx'],r['dy'];v=dict(x=r['cx']-dx/2,y=r['cy']-dy/2,scaleX=dx/w,scaleY=dy/h,blur=r['blur']/(dx/w));g['keyframes'].update({k:[dict(t=r['frame']/30,value=float(x),ease='linear')] for k,x in v.items()});g['shadow']['color']='#000000'+format(round(34*r.get('shadow',1)),'02x')
for f in [619]:
 t=f/30
 # Seed the two proven partial-circle/material registrations; final combined state still validated independently.
 for q in seed:
  if q['frame']==f and not (f==613 and q['photo']=='71'):
   g=next(n for n in S['layers']if n.get('semanticPhotoId')=='rene-final11-group-'+q['photo']and n.get('start',0)<=t<n.get('end',99));apply(g,q['best'])
 for idx in range(len(S['layers'])):
  original=S['layers'][idx]
  if not original.get('semanticPhotoId') or not (original.get('start',0)<=t<original.get('end',99)):continue
  state=rp.state(original,t)
  if state['opacity']<=.01 or original.get('semanticPhotoId')not in ['rene-final11-group-77','rene-final11-group-79']:continue
  if original['semanticPhotoId']=='rene-final11-group-79':
   child=original['children'][0];ow,oh=child['width'],child['height'];child.update(src=str(R/'references/06-gallery/giant-material-v21/portrait79-source622-material.png'),width=N,height=N)
   for k in ('x','y','blur'):original['shadow'][k]*=N/ow
   original['keyframes']['scaleX']=[{**k,'value':k['value']*ow/N}for k in original['keyframes']['scaleX']]
   original['keyframes']['scaleY']=[{**k,'value':k['value']*oh/N}for k in original['keyframes']['scaleY']]
   original['keyframes']['blur']=[{**k,'value':k['value']*N/ow}for k in original['keyframes']['blur']]
   state=rp.state(original,t)
  ident=original['semanticPhotoId'];g=copy.deepcopy(original);child=g['children'][0];w,h=child['width'],child['height'];dx=w*state['scaleX'];dy=h*state['scaleY'];cx=state['x']+dx/2;cy=state['y']+dy/2;b=state['blur']*state['scaleX'];material='source622'if w==512 else'original';shadow=int(g.get('shadow',{}).get('color','#00000022')[-2:],16)/34
  def full(ls,bg):return np.array(rp.render({**S,'layers':ls,'background':bg},t,str(BASE)).resize((W,H),Image.Resampling.LANCZOS),dtype=float)/255
  below=full(S['layers'][:idx],S.get('background','#ffffff'));ab=full(S['layers'][idx+1:],'#000000');aw=full(S['layers'][idx+1:],'#ffffff');aa=np.clip(1-np.mean(aw-ab,axis=2,keepdims=True),0,1);ref=np.array(Image.open(P/'source'/f'{f:06}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS),dtype=float)/255
  roi=np.zeros((H,W),bool);x0=max(0,int((cx-dx*.78)/4));x1=min(W,int((cx+dx*.78)/4)+1);y0=max(0,int((cy-dy*.78)/4));y1=min(H,int((cy+dy*.78)/4)+1);roi[y0:y1,x0:x1]=True;roi &= aa[:,:,0]<.7
  # The black headline is independently native; exclude its occupied band from photo fitting.
  roi[120:148,110:370]=False
  if roi.sum()<40:continue
  g.pop('keyframes',None);g.update(start=0,end=99,opacity=state['opacity']);history=[]
  def evaluate(z):
   xx,yy,ddx,ddy,blur,sh=map(float,z);q=copy.deepcopy(g);q.update(x=(xx-ddx/2)/4,y=(yy-ddy/2)/4,scaleX=ddx/w/4,scaleY=ddy/h/4,blur=blur/(ddx/w));q['shadow']['color']='#000000'+format(round(34*sh),'02x')
   def rgb(bg):return np.array(rp.render({**S,'width':W,'height':H,'layers':[q],'background':bg},t,str(BASE)),dtype=float)/255
   black=rgb('#000000');white=rgb('#ffffff');alpha=np.clip(1-np.mean(white-black,axis=2,keepdims=True),0,1);out=ab+(1-aa)*(black+(1-alpha)*below);delta=out-ref;err=float(np.mean(abs(delta[roi]))*255);r=dict(frame=f,photo=ident,material=material,cx=xx,cy=yy,dx=ddx,dy=ddy,blur=blur,shadow=sh,roiMAE=err,fullMAE=float(abs(delta).mean()*255));history.append(r);return err
  radius=max(15,dx*.22);initial=[cx,cy,dx,dy,b,shadow];bounds=[(cx-radius,cx+radius),(cy-radius,cy+radius),(dx*.75,dx*1.3),(dy*.75,dy*1.3),(0,max(12,b*1.7)),(0,1.5)]
  evaluate(initial);fit=minimize(evaluate,initial,method='Powell',bounds=bounds,options={'maxiter':2,'xtol':.1,'ftol':.001});best=min(history,key=lambda q:q['roiMAE']);accepted=best['fullMAE']<history[0]['fullMAE']-.002
  if accepted:apply(S['layers'][idx],best)
  rec=dict(frame=f,photo=ident,before=history[0],best=best,accepted=accepted,evaluations=len(history));reports.append(rec);print('RESULT',json.dumps(rec),flush=True);(P/'boundary619-fit.json').write_text(json.dumps(reports,indent=2));(P/'boundary619-fit.scene.json').write_text(json.dumps(S,indent=2));rp.LEAF_CACHE.clear();rp.GROUP_CACHE.clear();rp.FAST_CACHE.clear()
 for prefix,scene in [('boundary619-fit',S)]:
  im=rp.render(scene,t,str(BASE));im.save(P/f'{prefix}-{f}.png');print('FRAME',f,float(abs(np.array(im,dtype=float)-np.array(Image.open(P/'source'/f'{f:06}.png'),dtype=float)).mean()),flush=True)
(P/'boundary619-fit.scene.json').write_text(json.dumps(S,indent=2))
