"""One bounded genuine-photograph optical pose after static model limits.
Source RGB only where this independent photo is dominant, excluding every other
photo and native headline; original model continues all hidden/soft-edge pixels.
"""
from pathlib import Path
import json,copy,sys,numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(P/'continuation-fit.scene.json'));rp.register_fonts(S,str(BASE));f=616;t=f/30;ident='rene-final11-group-79';idx,g=next((i,n)for i,n in enumerate(S['layers'])if n.get('semanticPhotoId')==ident and n.get('start',0)<=t<n.get('end',99))
def rgb(ls,bg):return np.array(rp.render({**S,'layers':ls,'background':bg},t,str(BASE)),dtype=float)/255
black=rgb([g],'#000000');white=rgb([g],'#ffffff');alpha=np.clip(1-np.mean(white-black,axis=2),0,1);rgba=np.dstack([black/np.maximum(alpha[:,:,None],1e-9),alpha]);below=rgb(S['layers'][:idx],S.get('background','#ffffff'));ub=rgb(S['layers'][idx+1:],'#000000');uw=rgb(S['layers'][idx+1:],'#ffffff');ua=np.clip(1-np.mean(uw-ub,axis=2),0,1);ref=np.array(Image.open(P/'source'/f'{f:06}.png').convert('RGB'),dtype=float)/255
other=np.zeros(alpha.shape,bool)
for n in S['layers']:
 if n is g or not n.get('semanticPhotoId')or not(n.get('start',0)<=t<n.get('end',99)):continue
 st=rp.state(n,t)
 if st['opacity']<=.01:continue
 c=n['children'][0];dx=c['width']*st['scaleX'];dy=c['height']*st['scaleY'];yy,xx=np.mgrid[:alpha.shape[0],:alpha.shape[1]];other|=((xx-st['x']-dx/2)/(dx*.54+5))**2+((yy-st['y']-dy/2)/(dy*.54+5))**2<1
valid=(alpha>.7)&~other&~binary_dilation(ua>.005,iterations=5);desired=((ref-ub)/np.maximum(1e-6,1-ua[:,:,None])-(1-alpha[:,:,None])*below)/np.maximum(1e-6,alpha[:,:,None]);rgba[:,:,:3][valid]=np.clip(desired[valid],0,1);rgba=np.clip(rgba,0,1);yy,xx=np.where(alpha>.002);x0,x1=max(0,int(xx.min())-2),min(S['width'],int(xx.max())+3);y0,y1=max(0,int(yy.min())-2),min(S['height'],int(yy.max())+3);file=P/'optical-photo616-79.png';Image.fromarray(np.uint8(np.round(rgba[y0:y1,x0:x1]*255))).save(file);Q=copy.deepcopy(S);n=Q['layers'][idx];child=n['children'][0];child.update(src=str(file),x=0,y=0,width=x1-x0,height=y1-y0);n['shadow']=None;n['keyframes']={k:[dict(t=t,value=v,ease='linear')]for k,v in dict(x=x0,y=y0,scaleX=1,scaleY=1,rotation=0,blur=0,opacity=1).items()};before=rp.render(S,t,str(BASE));after=rp.render(Q,t,str(BASE));before.save(P/'optical616-before.png');after.save(P/'optical616-after.png');report=dict(frame=f,photo=ident,sourcePhotoSamplePixels=int(valid.sum()),imageBounds=[x0,y0,x1,y1],ownAlphaSupportPixels=int((alpha>.002).sum()),sourcePixelGate='Only own alpha>.7, excluding all other native photo footprints and dilated upper content. Hidden and edge pixels retain the independent static photo model; no foreign content or source background field sampled.',before=float(abs(np.array(before,dtype=float)/255-ref).mean()*255),after=float(abs(np.array(after,dtype=float)/255-ref).mean()*255));(P/'optical616-trial.json').write_text(json.dumps(report,indent=2));(P/'optical616-trial.scene.json').write_text(json.dumps(Q,indent=2));print(report)
