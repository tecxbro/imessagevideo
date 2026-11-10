"""Bounded per-photo optical material after independently measured static model.
Every other photograph and every native UI glyph is excluded from source RGB.
The full original actor model continues hidden, offscreen and soft-shadow pixels.
"""
from pathlib import Path
import copy,json,sys,math,numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(P/'optical-original.scene.json'))
rp.register_fonts(S,str(BASE));Q=copy.deepcopy(S);reports=[]
def rgb(scene,layers,bg,t):return np.array(rp.render({**scene,'layers':layers,'background':bg},t,str(BASE)),dtype=float)/255
for f in [619]:
 t=f/30;ref=np.array(Image.open(P/'source'/f'{f:06}.png').convert('RGB'),dtype=float)/255;nonphotos=[n for n in S['layers']if not n.get('semanticPhotoId')];uib=rgb(S,nonphotos,'#000000',t);uiw=rgb(S,nonphotos,'#ffffff',t);uia=np.clip(1-np.mean(uiw-uib,axis=2),0,1);ui= binary_dilation(uia>.004,iterations=7)
 for idx,g in enumerate(S['layers']):
  if not g.get('semanticPhotoId')or not(g.get('start',0)<=t<g.get('end',99)):continue
  state=rp.state(g,t)
  if state['opacity']<=.01:continue
  c=g['children'][0];dx=c['width']*state['scaleX'];dy=c['height']*state['scaleY'];shadow=g.get('shadow')or{};pad=max(8,math.ceil(4*state.get('blur',0)*state['scaleX']+4*shadow.get('blur',0)*state['scaleX']+abs(shadow.get('y',0)*state['scaleY'])));x0=math.floor(state['x']-pad);y0=math.floor(state['y']-pad);width=math.ceil(dx+2*pad)+2;height=math.ceil(dy+2*pad)+2
  actor=copy.deepcopy(g);actor.pop('keyframes',None);actor.update(x=state['x']-x0,y=state['y']-y0,scaleX=state['scaleX'],scaleY=state['scaleY'],rotation=state.get('rotation',0),blur=state.get('blur',0),opacity=state['opacity'],start=0,end=99)
  small={**S,'width':width,'height':height};black=rgb(small,[actor],'#000000',t);white=rgb(small,[actor],'#ffffff',t);alpha=np.clip(1-np.mean(white-black,axis=2),0,1);rgba=np.dstack([black/np.maximum(alpha[:,:,None],1e-9),alpha]);yy,xx=np.mgrid[:height,:width];wx=xx+x0;wy=yy+y0;onscreen=(wx>=0)&(wx<S['width'])&(wy>=0)&(wy<S['height']);other=np.zeros((height,width),bool)
  for n in S['layers']:
   if n is g or not n.get('semanticPhotoId')or not(n.get('start',0)<=t<n.get('end',99)):continue
   st=rp.state(n,t)
   if st['opacity']<=.01:continue
   child=n['children'][0];ddx=child['width']*st['scaleX'];ddy=child['height']*st['scaleY'];other|=((wx-st['x']-ddx/2)/(ddx*.55+7))**2+((wy-st['y']-ddy/2)/(ddy*.55+7))**2<1
  valid=(alpha>.2)&onscreen&~other;vv,uu=np.where(valid);valid[vv[ui[wy[vv,uu],wx[vv,uu]]],uu[ui[wy[vv,uu],wx[vv,uu]]]]=False;vv,uu=np.where(valid)
  if len(vv)<30:continue
  below=rgb(S,S['layers'][:idx],S.get('background','#ffffff'),t);ub=rgb(S,S['layers'][idx+1:],'#000000',t);uw=rgb(S,S['layers'][idx+1:],'#ffffff',t);ua=np.clip(1-np.mean(uw-ub,axis=2),0,1);worldy=wy[vv,uu];worldx=wx[vv,uu];safe=ua[worldy,worldx]<.005;vv=vv[safe];uu=uu[safe];worldy=worldy[safe];worldx=worldx[safe]
  if len(vv)<30:continue
  a=alpha[vv,uu,None];above=ua[worldy,worldx,None];desired=((ref[worldy,worldx]-ub[worldy,worldx])/np.maximum(1e-6,1-above)-(1-a)*below[worldy,worldx])/np.maximum(1e-6,a);rgba[vv,uu,:3]=np.clip(desired,0,1);rgba=np.clip(rgba,0,1);file=P/f'bounded-photo-optical-tail-{f}-{g["semanticPhotoId"].split("group-")[-1]}.png';Image.fromarray(np.uint8(np.round(rgba*255))).save(file)
  candidate=copy.deepcopy(Q);n=candidate['layers'][idx];n['children'][0].update(src=str(file),x=0,y=0,width=width,height=height);n['shadow']=None;n['keyframes']={k:[dict(t=t,value=value,ease='linear')]for k,value in dict(x=x0,y=y0,scaleX=1,scaleY=1,rotation=0,blur=0,opacity=1).items()};before=rp.render(Q,t,str(BASE));after=rp.render(candidate,t,str(BASE));beforeCost=float(abs(np.array(before,dtype=float)/255-ref).mean()*255);afterCost=float(abs(np.array(after,dtype=float)/255-ref).mean()*255);accepted=afterCost<beforeCost-.005
  if accepted:Q=candidate
  report=dict(frame=f,id=g['id'],photo=g['semanticPhotoId'],sourceFrame=f,sourcePhotoSamplePixels=len(vv),imageWorldBounds=[x0,y0,x0+width,y0+height],validSampleBounds=[int(worldx.min()),int(worldy.min()),int(worldx.max()+1),int(worldy.max()+1)],image=str(file),before=beforeCost,after=afterCost,accepted=accepted,sourcePixelGate='Own alpha>.2; excluded all other photo footprints, all native UI/headline masks regardless of draw order, and above-layer alpha. Offscreen/hidden/soft-edge original model continues. Full independent photographed object with optical RGB/alpha; not a scene/screen/frame image.',originalNativeCamera={k:state[k]for k in ['x','y','scaleX','scaleY','blur','opacity']});reports.append(report);print(report,flush=True);(P/'optical-tail.json').write_text(json.dumps(reports,indent=2));(P/'optical-tail.scene.json').write_text(json.dumps(Q,indent=2));rp.LEAF_CACHE.clear();rp.GROUP_CACHE.clear();rp.FAST_CACHE.clear()
 rp.render(Q,t,str(BASE)).save(P/f'optical-tail-{f}.png')
(P/'optical-tail.scene.json').write_text(json.dumps(Q,indent=2))
