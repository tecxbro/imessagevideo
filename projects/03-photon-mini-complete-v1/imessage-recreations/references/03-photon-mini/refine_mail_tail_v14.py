"""Measure the six unobserved native mail-exit frames before the v5 anchors."""
from pathlib import Path
from PIL import Image
import numpy as np,json,copy,sys
p=Path(__file__).parent;sys.path.insert(0,str(p.parents[1]/'engines'));from render_pillow import state
from hardware_fit_v13 import fit_hardware
s=json.loads((p/'tail-camera-v14.scene.json').read_text());mail=next(x for x in s['layers'] if x['id']=='late-mail-native-state-v5');baseline=copy.deepcopy(mail);ui=next(x for x in mail['children'] if x['id']=='late-mail-ui-fade');proof=[]
def put(node,key,t,value):
 tr=node.setdefault('keyframes',{}).setdefault(key,[]);q=next((q for q in tr if abs(q['t']-t)<1e-8),None)
 if q:q['value']=value;q['ease']='linear'
 else:tr.append({'t':t,'value':value,'ease':'linear'});tr.sort(key=lambda q:q['t'])
def find_art(node,t,parent=(0,0,1,1)):
 q=state(node,t);px,py,psx,psy=parent;cur=(px+q.get('x',0)*psx,py+q.get('y',0)*psy,psx*q.get('scaleX',1),psy*q.get('scaleY',1))
 if node.get('id')=='late-mail-card-original-interior':return cur,node
 for c in node.get('children',[]):
  found=find_art(c,t,cur)
  if found:return found
 return None
for f in range(414,426):
 t=f/30;im=Image.open(p/'mail-tail-native-v14'/f'{f-413:03}.png').convert('RGB');q=state(baseline,t);fit=fit_hardware(im,{'scale':q['scaleX'],'x':q['x'],'y':q['y']},y_radius=130,edge_bands=[(q['x']-35,q['x']+85*q['scaleX']),(q['x']+715*q['scaleX'],q['x']+825*q['scaleX'])]);values={'x':fit['x'],'y':fit['y'],'scaleX':fit['scale'],'scaleY':fit['scale']}
 for key,value in values.items():put(mail,key,t,value)
 (x,y,sx,sy),art=find_art(mail,t);template=Image.open(p/art['src']).convert('RGB');w=round(art['width']*sx);h=round(art['height']*sy);rr=np.array(template.resize((w,h),Image.Resampling.BILINEAR),dtype=float);xx=round(x);yy=round(y);x0=max(0,xx);x1=min(1920,xx+w);y0=max(0,yy);y1=min(1080,yy+h);rr=rr[y0-yy:y1-yy,x0-xx:x1-xx];ss=np.array(im,dtype=float)[y0:y1,x0:x1];m=(rr[:,:,2]-rr[:,:,0]>20)&(rr[:,:,0]<200);d=253-rr;v=253-ss;alpha=float(np.clip(np.sum(d[m]*v[m])/max(np.sum(d[m]*d[m]),1),0,1));put(ui,'opacity',t,alpha);proof.append({'frame':f,'physical_fit':fit,'art_box':[x,y,w,h],'ui_opacity':alpha})
s['source']['notes']+=' V14 mail exit414–419: actual physical side/rim fit and independently sampled blue mini-app brightness fill the old13.8→14.0 camera/opacity gap. Existing measured420–429 anchors retained. No sourceframe or sourcevideo raster layer.'
(p/'mail-tail-v14.scene.json').write_text(json.dumps(s,indent=2));(p/'mail-tail-v14-changes.json').write_text(json.dumps({'scope':[414,425],'measurements':proof},indent=2));print([(q['frame'],round(q['physical_fit']['hardware_cost'],2),round(q['physical_fit']['scale'],3),round(q['ui_opacity'],3)) for q in proof])
