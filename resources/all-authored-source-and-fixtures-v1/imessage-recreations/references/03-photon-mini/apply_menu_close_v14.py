"""Native closing-widget poses from measured body bounds and exposed UI gray."""
from pathlib import Path
from PIL import Image
from scipy.signal import fftconvolve
import numpy as np,json,sys
p=Path(__file__).parent;sys.path.insert(0,str(p.parents[1]/'engines'));from render_pillow import state
s=json.loads((p/'combined-v14.scene.json').read_text());clip=next(x for x in s['layers'] if x['id']=='measured-menu-clip-v13');menu=clip['children'][0];body=next(x for x in menu['children'] if x['id']=='menu13-p03-202');dim=next(x for x in s['layers'] if x['id']=='measured-lunch-display-dim-v13')['children'][0];records=json.loads((p/'menu-close-v14-measurements.json').read_text());proof=[]
def put(node,key,t,value):
 track=node.setdefault('keyframes',{}).setdefault(key,[]);q=next((q for q in track if abs(q['t']-t)<1e-8),None)
 if q:q['value']=float(value);q['ease']='linear'
 else:track.append({'t':t,'value':float(value),'ease':'linear'});track.sort(key=lambda q:q['t'])
def match(a,template,x,y,sx,sy):
 w=max(4,round(176*sx/2));h=max(4,round(176*sy/2));r=np.array(template.resize((w,h),Image.Resampling.BILINEAR),dtype=float);d=(253-r)/255;mask=(r.max(2)-r.min(2)>20)|(r.mean(2)<140);d*=mask[:,:,None];den=(d*d).sum();xx=round(x/2);yy=round(y/2);x0=max(0,xx-14);x1=min(960,xx+w+15);y0=max(0,yy-24);y1=min(540,yy+h+25)
 if x1-x0<w or y1-y0<h:return None
 reg=(253-a[y0:y1,x0:x1])/255;dot=sum(fftconvolve(reg[:,:,c],d[::-1,::-1,c],mode='valid') for c in range(3));energy=sum(fftconvolve(reg[:,:,c]**2,mask[::-1,::-1].astype(float),mode='valid') for c in range(3));cos=dot/np.sqrt(np.maximum(energy*den,1e-9));iy,ix=np.unravel_index(cos.argmax(),cos.shape);return {'x':float((x0+ix)*2),'y':float((y0+iy)*2),'cosine':float(cos[iy,ix]),'opacity':float(np.clip(dot[iy,ix]/max(den,1e-9),0,1))}
for rec in records:
 f=rec['frame'];t=f/30;put(dim,'opacity',t,rec['extra_dim'])
 if rec['scale'] is None:put(menu,'opacity',t,0);continue
 sx=rec['scale'];sy=rec['scaleY'];x=rec['x'];y=rec['y'];q=state(clip,t)
 for key,value in [('x',(x-q['x'])/q['scaleX']),('y',(y-q['y'])/q['scaleY']),('scaleX',sx/q['scaleX']),('scaleY',sy/q['scaleY']),('opacity',1)]:put(menu,key,t,value)
 a=np.array(Image.open(p/'lunch-native'/f'{f-609:03}.png').resize((960,540),Image.Resampling.LANCZOS),dtype=float);matches=[]
 for i,row in enumerate(body['children']):
  image=next(n for n in row['children'] if n['type']=='image');im=Image.open(p/image['src']).convert('RGB');matches.append(match(a,im,x+553*sx,y+(348+236*i)*sy,sx,sy))
 good=[(i,z) for i,z in enumerate(matches) if z and z['cosine']>.87 and z['opacity']>.7]
 for i,row in enumerate(body['children']):
  z=matches[i]
  if z and z['cosine']>.87 and z['opacity']>.7:ref=i
  elif good:ref,z=min(good,key=lambda zz:abs(zz[0]-i))
  else:ref=z=None
  dx=z['x']-(x+553*sx) if z else 0;dy=z['y']-(y+(348+236*ref)*sy) if z else 0
  for key,value in [('x',dx/sx),('y',dy/sy),('scaleX',1),('scaleY',1)]:put(row,key,t,value)
  for node in row['children']:
   if node['type']=='circle' or node['type']=='text' and node.get('text')=='+':
    put(node,'opacity',729/30,1);put(node,'opacity',t,0);put(node,'opacity',735/30,1)
 proof.append({**rec,'photo_matches':matches})
s['source']['notes']+=' V14 closing sheet730–734: actual bright body span(nativey310..1630) defines independent x/y widget projection; offscreen/fading cyan-control diameter was invalid. Exposed source-gray margin197→237 fits separate native backdrop dim. Native body text/photos/controls stay independently editable; no panel screenshot used.'
(p/'closed-menu-v14.scene.json').write_text(json.dumps(s,indent=2));(p/'menu-close-v14-changes.json').write_text(json.dumps({'baseline':'combined-v14.scene.json','scope':[730,734],'measurements':proof,'native_geometry':True},indent=2));print('closedmenu',len(proof))
