from pathlib import Path
import json,importlib.util
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';A=D/'assets';s=json.loads((D/'scene-menu-middle-v11.json').read_text())
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
ref=load(99);bb=[735,539,841,623];art=ref[bb[1]:bb[3],bb[0]:bb[2]];poses=[]
for f in range(99,110):
 a=load(f);wy,wx=np.mgrid[500:720:2,600:960:2];target=a[500:720:2,600:960:2]
 def residual(v):
  sc,x,y,bx,by,alpha=v;blur=gaussian_filter(art,(by/sc,bx/sc,0),mode='constant',cval=255);coords=[(wy-y)/sc-bb[1],(wx-x)/sc-bb[0]];pred=np.stack([map_coordinates(blur[:,:,c],coords,order=1,mode='constant',cval=255) for c in range(3)],2);return ((255-alpha*(255-pred))-target).ravel()/255
 if f==99:init=[1,0,0,.2,.2,1]
 else:
  prev=poses[-1];init=[prev['scale'],prev['x']+20,prev['y']+18,8,3,1]
 fit=least_squares(residual,init,bounds=([.7,-300,-300,0,0,.1],[1.9,300,300,30,20,1.1]),max_nfev=70,diff_step=.005,ftol=.0005,xtol=.0005);sc,x,y,bx,by,alpha=map(float,fit.x);poses.append(dict(frame=f,scale=sc,x=x,y=y,blurX=bx,blurY=by,opacity=min(alpha,1)));print(f,fit.x,flush=True)
# Static real composer shell is isolated from its outlined, editable main copy.
box=[147,516,866,656];ar=ref[box[1]:box[3],box[0]:box[2]].copy();ar[555-box[1]:611-box[1],304-box[0]:721-box[0]]=255;path=A/'v11-menu-composer-shell.png';rgba=np.dstack([np.uint8(ar),(ar.min(2)<254).astype(np.uint8)*255]);Image.fromarray(rgba).save(path)
roi=ref[556:610,304:721].mean(2);d,stats=trace.trace_alpha(1-roi/255,304,556)
children=[dict(type='image',id='v11-menu-composer-shell',src=str(path),x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1]),dict(type='path',id='v11-menu-composer-copy',d=d,fill='#000000',semanticText="Yo i'm bored, chess battle?")]
def key(k):return [dict(t=p['frame']/30,value=p[k],ease='linear') for p in poses]
g=dict(type='group',id='v11-menu-composer',start=99/30,end=110/30,children=children,keyframes={'scaleX':key('scale'),'scaleY':key('scale'),'x':key('x'),'y':key('y'),'blur':[dict(t=p['frame']/30,value=(p['blurX']+p['blurY'])/2) for p in poses],'opacity':key('opacity')})
for q in s['layers']:
 if q['id'] in ['g-6','g-90']:q['end']=99/30
 q2=q
 if q['id']=='g-119':
  for z in q['children']:
   if z['id']=='v11-menu-chrome':
    for k in z['keyframes']['y']:k['value']+=15
s['layers'].insert(next(i for i,q in enumerate(s['layers']) if q['id']=='g-119'),g)
(D/'menu-composer-v11-poses.json').write_text(json.dumps(poses,indent=2));(D/'scene-menu-middle-v11.json').write_text(json.dumps(s,indent=2)+'\n')
