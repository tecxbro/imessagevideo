from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,label,find_objects
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';A=D/'assets';s=json.loads((D/'scene-menu-middle-v11.json').read_text());g=next(q for q in s['layers'] if q['id']=='v11-menu-composer');poses=json.loads((D/'menu-composer-v11-poses.json').read_text());by={p['frame']:p for p in poses}
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
ref=load(99);rgbgray=ref.max(2)-ref.min(2);ink=(255-ref.mean(2))*(rgbgray<12);art=ink[556:610,304:721];pp=[];cp=[]
for f in range(99,110):
 a=load(f);chroma=a.max(2)-a.min(2);gray=a.mean(2);yy,xx=np.indices(gray.shape);color=(a[:,:,2]-a[:,:,0]>90)&(a[:,:,1]-a[:,:,0]>40)&(a[:,:,2]>175)&(xx>600)&(yy>500);ys,xs=np.where(color)
 if not len(ys):continue
 top=float(ys.min());mask=(gray<185)&(chroma<15)&(xx>120)&(xx<275)&(yy>top+9)
 lab,n=label(mask);stats=[]
 for i,sl in enumerate(find_objects(lab),1):
  if sl is not None:
   count=(lab[sl]==i).sum()
   if count>20:stats.append((count,sl))
 if stats:
  sl=max(stats,key=lambda z:z[0])[1];sc=(sl[0].stop-sl[0].start)/33;cx=(sl[1].start+sl[1].stop)/2;cy=(sl[0].start+sl[0].stop)/2
 else:sc=1.2;cx=194;cy=top+37
 pp.append(dict(frame=f,scale=sc,x=cx-211*sc,y=cy-579.5*sc,cx=cx,cy=cy))
 targetInk=(255-gray)*(chroma<15);wy,wx=np.mgrid[max(500,round(top)+8):720:2,280:950:2];target=targetInk[wy,wx];sc0=min(1.4,max(.95,sc));tx0=308-308*sc0;ty0=cy-583*sc0
 def residual(v):
  sc,x,y,alpha=v;coords=[(wy-y)/sc-556,(wx-x)/sc-304];pred=map_coordinates(art,coords,order=1,mode='constant',cval=0);return ((alpha*pred)-target).ravel()/255
 fit=least_squares(residual,[sc0,tx0,ty0,1],bounds=([.9,tx0-45,ty0-30,.2],[1.6,tx0+45,ty0+30,1.1]),max_nfev=70,diff_step=.005,ftol=.0005,xtol=.0005);sc,x,y,alpha=map(float,fit.x);cp.append(dict(frame=f,scale=sc,x=x,y=y,opacity=min(alpha,1)));print(f,'plus',pp[-1],'copy',cp[-1],flush=True)
# One declared static plus/control shell; each independently animated control
# keeps its original artwork, while the main inline sentence remains a path.
def asset(name,box,art):
 path=A/f'v11-composer-{name}.png';Image.fromarray(np.dstack([np.uint8(art),(art.min(2)<254).astype(np.uint8)*255])).save(path);return dict(type='image',id=f'v11-composer-{name}',src=str(path),x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1])
plusBox=[148,516,273,656];plus=asset('plus',plusBox,ref[516:656,148:273]);sendBox=[735,539,841,623];send=asset('send',sendBox,ref[539:623,735:841]);text=copy.deepcopy(g['children'][1])
# UI shell is one static component with no embedded copy or send button.
shellbox=[275,521,866,653];ar=ref[521:653,275:866].copy();ar[555-521:611-521,304-275:721-275]=255;ar[539-521:623-521,735-275:841-275]=255;shell=asset('input-shell',shellbox,ar)
def key(rows,k):return [dict(t=p['frame']/30,value=p[k],ease='linear') for p in rows]
plusg=dict(type='group',id='v11-composer-plus-camera',children=[plus],keyframes={k:key(pp,k) for k in ['x','y']});plusg['keyframes'].update(scaleX=key(pp,'scale'),scaleY=key(pp,'scale'))
textg=dict(type='group',id='v11-composer-copy-camera',children=[text],keyframes={k:key(cp,k) for k in ['x','y','opacity']});textg['keyframes'].update(scaleX=key(cp,'scale'),scaleY=key(cp,'scale'))
sendg=dict(type='group',id='v11-composer-send-camera',children=[send],keyframes={k:key(poses,k) for k in ['x','y','opacity']});sendg['keyframes'].update(scaleX=key(poses,'scale'),scaleY=key(poses,'scale'),blur=[dict(t=p['frame']/30,value=p['blurY']) for p in poses])
shellTracks={k:[] for k in ['x','y','scaleX','scaleY']}
for p in cp:
 f=p['frame'];sendp=by[f];left=275.;right=841*sendp['scale']+sendp['x']+22;scaleX=(right-left)/591;scaleY=p['scale'];top=p['y']+521*scaleY
 for k,v in [('x',left-275*scaleX),('y',top-521*scaleY),('scaleX',scaleX),('scaleY',scaleY)]:shellTracks[k].append(dict(t=f/30,value=v,ease='linear'))
shellg=dict(type='group',id='v11-composer-input-shell-camera',children=[shell],keyframes=shellTracks)
g['children']=[shellg,plusg,textg,sendg];g['keyframes']={}
(D/'composer-parts-v11-poses.json').write_text(json.dumps(dict(plus=pp,copy=cp),indent=2));(D/'scene-menu-middle-v11.json').write_text(json.dumps(s,indent=2)+'\n')
