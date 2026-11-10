"""Authentic static menu rows in an independently measured viewport/camera."""
from pathlib import Path
import json,copy
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,gaussian_filter,label,find_objects
from scipy.optimize import least_squares,minimize_scalar
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';A=D/'assets';M=D/'measurements/menu-v11';M.mkdir(exist_ok=True)
def load(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(np.float32)
imgs={f:load(f) for f in range(99,128)};ref=imgs[108];box=[194,518,509,614];art=ref[box[1]:box[3],box[0]:box[2]];poses=[]
# Full world image residual in a bounded ROI, not point matching which can
# suppress error by shrinking the actual app icon.
for f in range(101,128):
 a=imgs[f];r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];yy,xx=np.indices(r.shape);mask=(b-r>55)&(g-r>30)&(b>170)&(xx>80)&(xx<500)&(yy<620);lab,n=label(mask);stats=[]
 for i,sl in enumerate(find_objects(lab),1):
  if sl is not None:
   count=(lab[sl]==i).sum()
   if count>100:stats.append((count,sl))
 if stats:
  sl=max(stats,key=lambda q:q[0])[1];sx=(sl[1].stop-sl[1].start)/80.;cx=(sl[1].start+sl[1].stop)/2;cy=(sl[0].start+sl[0].stop)/2
 else:
  prev=poses[-1];sx=prev['scale'];cx=sx*240+prev['x'];cy=sx*565+prev['docY']-7
 sx=float(np.clip(sx,.15,1.2));tx=cx-sx*240;ty=cy-sx*565
 x0=max(0,int(tx+194*sx-22));x1=min(960,int(tx+509*sx+22));y0=max(0,int(ty+518*sx-35));y1=min(720,int(ty+614*sx+35));wy,wx=np.mgrid[y0:y1:2,x0:x1:2];target=a[y0:y1:2,x0:x1:2]
 # Row image only; blur is a source-derived rendering property of a static UI.
 def residual(v):
  sc,x,y,bx,by,alpha=v;blur=gaussian_filter(art,(by/max(sc,.1),bx/max(sc,.1),0),mode='constant',cval=255);coords=[(wy-y)/sc-box[1],(wx-x)/sc-box[0]];pred=np.stack([map_coordinates(blur[:,:,c],coords,order=1,mode='constant',cval=255) for c in range(3)],2);return ((255-alpha*(255-pred))-target).ravel()/255
 init=[sx,tx,ty,1,1,1];lo=[max(.12,sx-.16),tx-20,ty-28,0,0,.05];hi=[min(1.3,sx+.16),tx+20,ty+28,14,32,1.1]
 fit=least_squares(residual,init,bounds=(lo,hi),max_nfev=65,ftol=.0005,xtol=.0005,diff_step=.003);sc,x,y,bx,by,alpha=map(float,fit.x)
 # Static chrome-only ring follows the same optical scale and X, but the
 # menu document scrolls independently inside it.
 poses.append(dict(frame=f,scale=sc,x=x,docY=y,blurX=bx,blurY=by,opacity=min(1,alpha),cost=float(np.mean(fit.fun**2))))
 print(f,*(round(v,3) for v in [sc,x,y,bx,by,alpha]),flush=True)
# A single static chrome asset; its display interior is transparent.
cb=[99,15,815,698];chrome=Image.fromarray(np.uint8(ref[cb[1]:cb[3],cb[0]:cb[2]]));alpha=Image.new('L',chrome.size,255);draw=ImageDraw.Draw(alpha);draw.rounded_rectangle((153-cb[0],65-cb[1],756-cb[0],622-cb[1]),radius=56,fill=0);chrome.putalpha(alpha);cp=A/'v11-menu-chrome-static.png';chrome.save(cp)
ca=np.array(chrome);ay,ax=np.nonzero((ca[:,:,3]>0)&(ca[:,:,:3].mean(2)<254));vals=ca[ay,ax,:3].astype(float);# Restrict to actual border/shadow, never menu-row ink.
keep=(ax+cb[0]>740)|(ax+cb[0]<150)|(ay+cb[1]>635);ay,ax,vals=ay[keep],ax[keep],vals[keep]
for p in poses:
 a=imgs[p['frame']];sc=p['scale'];x=p['x'];mx=(ax+cb[0])*sc+x
 init=p['docY'] if p['frame']<=110 else (1-sc)*260
 def cost(y):
  my=(ay+cb[1])*sc+y;valid=(mx>=0)&(mx<959)&(my>=0)&(my<719);obs=np.stack([map_coordinates(a[:,:,c],[my[valid],mx[valid]],order=1) for c in range(3)],1);v=vals[valid];return float(np.mean((obs-(255-p['opacity']*(255-v)))**2))
 fit=minimize_scalar(cost,bounds=(init-30,init+30),method='bounded',options={'xatol':.05});p['cardY']=float(fit.x)
# Seven independent static row artworks. Lower3 are registered from123 into
# the original108 document, using the measured shared Store pose.
p123=next(p for p in poses if p['frame']==123);rows=[];provenance=[]
for name,f,bb in [('Photos',108,[198,85,590,160]),('AppleCash',108,[194,221,628,313]),('Polls',108,[194,370,520,461]),('Store',108,[194,518,509,614]),('GamePigeon',123,[178,325,750,422]),('Threadsby',123,[212,488,747,552]),('StarFlights',123,[181,625,753,701])]:
 ar=imgs[f][bb[1]:bb[3],bb[0]:bb[2]];path=A/f'v11-menu-row-{name}.png';alpha=(ar.min(2)<254).astype(np.uint8)*255;rgba=np.dstack([np.uint8(ar),alpha]);Image.fromarray(rgba).save(path)
 if f==108:x,y,w,h=bb[0],bb[1],bb[2]-bb[0],bb[3]-bb[1]
 else:x=(bb[0]-p123['x'])/p123['scale'];y=(bb[1]-p123['docY'])/p123['scale'];w=(bb[2]-bb[0])/p123['scale'];h=(bb[3]-bb[1])/p123['scale']
 rows.append(dict(type='image',id=f'v11-menu-row-{name}',src=str(path),x=x,y=y,width=w,height=h));provenance.append(dict(path=str(path),source_frame=f,box=bb,kind='bounded static original app-menu row UI; internal text bitmap; native independent viewport/document motion'))
s=json.loads((D/'scene-middle-v11.json').read_text());old=next(q for q in s['layers'] if q['id']=='g-119');old.update(start=101/30,end=127/30,x=0,y=0)
def key(k):return [dict(t=p['frame']/30,value=p[k],ease='linear') for p in poses if p['frame']<=126]
# Each row is rendered separately and clipped by a native rounded viewport.
# Use isotropic blur approximation for viewport/camera; directional blur remains
# explicitly measured in data and can be exported through richer adapters.
old['children']=[dict(type='image',id='v11-menu-chrome',src=str(cp),x=cb[0],y=cb[1],width=cb[2]-cb[0],height=cb[3]-cb[1],keyframes={'y':[dict(t=p['frame']/30,value=p['cardY']/p['scale']) for p in poses if p['frame']<=126]}),dict(type='group',id='v11-menu-document-viewport',clip={'x':126,'y':38,'width':658,'height':612,'radius':83},children=[dict(type='group',id='v11-menu-document',children=rows,keyframes={'y':[dict(t=p['frame']/30,value=(p['docY']-p['cardY'])/p['scale']) for p in poses if p['frame']<=126]})],keyframes={'y':[dict(t=p['frame']/30,value=p['cardY']/p['scale']) for p in poses if p['frame']<=126]})]
old['keyframes']={'scaleX':key('scale'),'scaleY':key('scale'),'x':key('x'),'opacity':key('opacity'),'blur':[dict(t=p['frame']/30,value=min(12,(p['blurX']+p['blurY'])/2)) for p in poses if p['frame']<=126]}
# Correct the bounded chrome origin: cardY is world translation, so all cameraY
# resides on child nodes and does not affect document independently.
(D/'menu-v11-poses.json').write_text(json.dumps(poses,indent=2));(A/'menu-v11-provenance.json').write_text(json.dumps(provenance+[dict(path=str(cp),source_frame=108,box=cb,kind='static app-menu chrome only; transparent interior')],indent=2));(D/'scene-menu-middle-v11.json').write_text(json.dumps(s,indent=2)+'\n')
