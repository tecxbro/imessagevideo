"""Reconstruct two bounded static app documents, then measure independent cameras.
No reference frame sequence is used as animation artwork.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';O=D/'measurements/long-panels-v10';O.mkdir(exist_ok=True);A=D/'assets'
def load(f):return np.asarray(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float)
def save(name,a):
 p=A/(name+'.png');Image.fromarray(np.uint8(np.clip(a,0,255))).save(p);return str(p)
feat={x['frame']:x for x in json.loads((D/'measurements/transition-features.json').read_text())}

# Foodash uses a single tall document. Its upper and lower static sections overlap
# around Priya; match the Dillion name to recover the exact document displacement.
ref=load(1056);tpl=(255-ref[51:81,225:350]);food=[]
for f in range(1032,1064):
 a=load(f);candidates=[]
 for y in range(0,641):
  v=255-a[y:y+30,225:350];candidates.append(np.mean((v-tpl)**2))
 yy=int(np.argmin(candidates));food.append({'frame':f,'x':188.,'y':float(yy-51-412),'scale':1.,'matchMSE':float(min(candidates))})
# Source 1032 has the Veggie Shack line mid-crossfade. Use its unchanged upper
# document, the settled row from 1038, then the settled lower document from1056.
canvas=np.full((1132,584,3),255.)
canvas[:720]=load(1032)[:,188:772]
canvas[440:550]=load(1038)[416:526,188:772]
canvas[550:]=ref[138:720,188:772]
foodpath=save('v10-foodash-tall-final',canvas)
# Initial Dillion row is a bounded state asset normalized from the last near1x
# source view before the row changes, not a whole app frame.
pose1026={'x':230-40*(74/76),'y':44-34*(74/76),'scale':74/76}
src=Image.fromarray(np.uint8(load(1026)))
initial=np.asarray(src.transform((584,110),Image.Transform.AFFINE,(pose1026['scale'],0,pose1026['x'],0,pose1026['scale'],pose1026['y']+440*pose1026['scale']),Image.Resampling.BICUBIC))
initialpath=save('v10-foodash-initial-dillion-row',initial)
# Every early frame has a clear near-square green icon. It establishes translation
# and scale independently of the changing chat/order text.
logo=json.loads((D/'measurements/foodash-logo-poses.json').read_text())
if isinstance(logo,dict):logo=logo.get('poses',logo.get('frames',[]))
early=[]
for row in logo:
 f=row['frame'];b=row.get('logo',row.get('box',row.get('bbox',row.get('bounds'))))
 if b is None or f>1031:continue
 scale=(b[3]-b[1])/76
 early.append({'frame':f,'x':b[0]-40*scale,'y':b[1]-34*scale,'scale':scale})
food=early+food
subtotalpath=save('v10-foodash-initial-subtotal-row',load(1050)[578:668,188:772])
(O/'foodash.json').write_text(json.dumps({'path':foodpath,'width':584,'height':1132,'initialRow':initialpath,'initialSubtotal':subtotalpath,'poses':food},indent=2))

# Native restaurant camera from a stable independent button silhouette.
rest=[]
for f in range(1058,1145):
 a=load(f);m=(a.max(2)<200)&(a.max(2)-a.min(2)<15);m[:,:190]=0;m[:,558:]=0;labs,n=label(m);buttons=[]
 for sl in find_objects(labs):
  if sl is None:continue
  y,x=sl;w,h=x.stop-x.start,y.stop-y.start
  if 330<w<380 and 40<h<85:buttons.append([x.start,y.start,x.stop,y.stop])
 if not buttons:
  hm=(a.min(2)>130)&(a.max(2)<230)&(a.max(2)-a.min(2)<8);hm[:,:440]=0;hm[:,525:]=0;ll,nn=label(hm);handles=[]
  for sl in find_objects(ll):
   if sl is None:continue
   yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
   if 40<w<70 and 4<h<12:handles.append([xx.start,yy.start,xx.stop,yy.stop])
  if handles:
   b=handles[0];rest.append({'frame':f,'y':b[1]+20,'alpha':1.,'buttonRGB':18.})
  continue
 b=max(buttons,key=lambda b:(b[2]-b[0])*(b[3]-b[1]));rest.append({'frame':f,'y':b[1]-123,'alpha':1.,'buttonRGB':float(np.median(a[b[1]+30:b[1]+37,230:280]))})

# Five original photos, each independently editable and moving on one clipped rail.
# The full-size source photos have widths386,268,504,334,444 with24px gutters.
photos=[]
for name,f,box,x in [('facade',1068,[195,362,612,696],-1060),('table',1098,[339,303,607,637],-619),('bowl',1104,[232,302,736,636],-327),('octopus',1110,[201,302,535,636],201),('interior',1134,[319,303,763,637],559)]:
 ar=load(f)[box[1]:box[3],box[0]:box[2]];p=save('v10-restaurant-'+name,ar);photos.append({'name':name,'path':p,'x':x,'width':ar.shape[1],'height':334,'source_frame':f,'source_box':box})
# The static UI document is stitched through the lower details; its photo band is
# deliberately empty, since each original photograph lives on the independent rail.
base=np.full((860,586,3),255.);base[:721]=np.vstack([np.full((1,586,3),255),load(1110)[:,188:774]])
base[650:840]=load(1143)[530:720,188:774];base[303:637]=255
uipath=save('v10-restaurant-document',base)
# Build a horizontal image profile only for pose measurement. It never enters scene.
strip=np.full((334,2063,3),255.)
for p in photos:strip[:,p['x']+1060:p['x']+1060+p['width']]=np.asarray(Image.open(p['path']))
profile=strip[100:250].mean(0);qs=np.arange(-260,1301);world=np.arange(188,774)[None,:];ix=world-qs[:,None]+1060;valid=(ix>=0)&(ix<2063);models=255-profile[np.clip(ix,0,2062)];models*=valid[:,:,None];models=models.reshape(len(qs),-1);den=np.sum(models*models,1)
camera={x['frame']:x for x in rest};last=1255
for f in range(1058,1145):
 row=camera.get(f)
 if row is None:continue
 if f<1068:row['q']=1255.;continue
 a=load(f);y=round(303+row['y']);p=255-a[y+100:y+250,188:774].mean(0);dot=models@p.ravel();alpha=dot/den;err=np.maximum(0,np.sum(p*p)-dot*dot/den)/den;at=int(np.argmin(err));q=float(qs[at]);
 if 0<at<len(qs)-1:
  dd=err[at-1]-2*err[at]+err[at+1]
  if dd>0:q+=float(np.clip(.5*(err[at-1]-err[at+1])/dd,-.5,.5))
 row['q']=q;row['photoProfileMSE']=float(err[at]);last=q
# Once the button clips above the viewport, fit the settled interior photograph
# independently for vertical translation and fade amplitude through the exit.
photo=np.asarray(Image.open(photos[-1]['path'])).astype(float);p0=(255-photo).mean(1);yg=np.arange(-330,400);world=np.arange(720)[None,:];idx=world-yg[:,None];valid=(idx>=0)&(idx<334);models=p0[np.clip(idx,0,333)]*valid[:,:,None];models=models.reshape(len(yg),-1);den=np.sum(models*models,1)
for f in range(1144,1150):
 a=load(f);p=(255-a[:,319:763]).mean(1);dot=models@p.ravel();alpha=dot/den;energy=valid@np.sum(p*p,1);err=np.maximum(0,energy-dot*dot/den)/np.maximum(energy,1);err[(alpha<.01)|(alpha>1.2)]=1e6;at=int(np.argmin(err));y=float(yg[at]);sub=0
 if 0<at<len(err)-1:
  dd=err[at-1]-2*err[at]+err[at+1]
  if dd>0:sub=float(np.clip(.5*(err[at-1]-err[at+1])/dd,-.5,.5))
 row=dict(frame=f,y=y+sub-303,alpha=float(np.clip(alpha[at],0,1)),q=-240.,fit=float(err[at]),buttonRGB=0.)
 rest=[r for r in rest if r['frame']!=f]+[row]
rest.sort(key=lambda x:x['frame']);rest.append(dict(frame=1150,y=rest[-1]['y']-20,alpha=0.,q=-240.,buttonRGB=0.))
(O/'restaurant.json').write_text(json.dumps({'path':uipath,'width':586,'height':860,'photos':photos,'poses':rest},indent=2));print('Food',food[:2],food[-1]);print('Restaurant',rest[:2],rest[-8:])

# Fare cards keep moving left as the seat grid is revealed above them. Track the
# large Economy white-card silhouette, then fit seat-grid reveal coefficient only
# on original white body pixels, excluding bitmap letterforms.
fare=load(399);grid=load(426);cardmask=(fare[:,:,0]>210)&(fare[:,:,1]>220)&(fare[:,:,2]>230);cardmask[:,:188]=0;cardmask[:,770:]=0
labs,n=label(cardmask);keep=np.zeros(cardmask.shape,bool)
from scipy.ndimage import binary_fill_holes,binary_dilation
for sl in find_objects(labs):
 if sl is None:continue
 yy,xx=sl
 if xx.stop-xx.start>150 and yy.stop-yy.start>50:keep[sl]|=binary_fill_holes(cardmask[sl])
keep=binary_dilation(keep,iterations=1)
rgba=np.dstack([np.uint8(fare[:,188:770]),np.uint8(keep[:,188:770])*255]);farepath=save('v10-flight-independent-fare-cards',rgba)
gridpath=save('v10-flight-unselected-grid',grid[:,188:770]);seats=[]
for f in range(412,423):
 a=load(f);m=(a[:,:,0]>210)&(a[:,:,1]>220)&(a[:,:,2]>230);m[:,:188]=0;m[:,770:]=0;labs,n=label(m);cc=[]
 for sl in find_objects(labs):
  if sl is None:continue
  yy,xx=sl
  if xx.stop-xx.start>80 and yy.stop-yy.start>300:cc.append([xx.start,yy.start,xx.stop,yy.stop])
 if f<=416:dx=(max(cc,key=lambda b:b[2])[2]-747) if cc else 0
 elif cc:dx=max(b[2] for b in cc)-747
 else:dx=-600
 shifted=np.full_like(fare,255);mask=np.zeros((720,960),bool)
 if dx>=-580:
  lo=max(188,188+dx);hi=min(770,770+dx)
  if hi>lo:shifted[:,lo:hi]=fare[:,lo-dx:hi-dx];mask[:,lo:hi]=keep[:,lo-dx:hi-dx]
 mask&=(shifted.min(2)>235);mask[:120]=False;mask[690:]=False
 diff=(grid-shifted)[mask];obs=(a-shifted)[mask];beta=float(np.clip(np.sum(diff*obs)/max(1,np.sum(diff*diff)),0,1)) if len(diff) else 1.
 seats.append({'frame':f,'x':dx,'gridAlpha':beta})
summary=[]
for f in range(428,469):
 a=load(f);m=(a.min(2)>230)&(a.max(2)-a.min(2)<12);m[:,:205]=0;m[:,755:]=0;labs,n=label(m)
 for sl in find_objects(labs):
  if sl is None:continue
  yy,xx=sl
  if xx.stop-xx.start>450 and yy.start>400:summary.append({'frame':f,'y':yy.start});break
summarypath=save('v10-flight-summary-card',load(450)[512:720,208:752])
(O/'flight-seats.json').write_text(json.dumps({'farePath':farepath,'gridPath':gridpath,'poses':seats,'summaryPath':summarypath,'summaryPoses':summary},indent=2))

# Check-in is another independent rising message, then remains behind the pass.
source=load(1179);m=(source.max(2)-source.min(2)<6)&(source.mean(2)>210)&(source.mean(2)<242);labs,n=label(m);bb=[]
for sl in find_objects(labs):
 if sl is None:continue
 yy,xx=sl
 if xx.stop-xx.start>500 and yy.stop-yy.start>100:bb.append([xx.start-2,yy.start-2,xx.stop+2,yy.stop+2])
box=max(bb,key=lambda b:(b[2]-b[0])*(b[3]-b[1]));art=source[box[1]:box[3],box[0]:box[2]];h,w=art.shape[:2];p0=(255-art).mean(1);yg=np.arange(-h+10,715);world=np.arange(720)[None,:];idx=world-yg[:,None];valid=(idx>=0)&(idx<h);models=(p0[np.clip(idx,0,h-1)]*valid[:,:,None]).reshape(len(yg),-1);den=np.sum(models*models,1);poses=[]
for f in range(1149,1182):
 a=load(f);p=(255-a[:,box[0]:box[2]]).mean(1);dot=models@p.ravel();alpha=dot/np.maximum(den,1);energy=valid@np.sum(p*p,1);err=np.maximum(0,energy-dot*dot/np.maximum(den,1))/np.maximum(energy,1);err[(alpha<.04)|(alpha>1.4)]=1e6;at=int(np.argmin(err))
 if err[at]>.15:continue
 y=float(yg[at]);sub=0
 if 0<at<len(err)-1:
  dd=err[at-1]-2*err[at]+err[at+1]
  if dd>0:sub=float(np.clip(.5*(err[at-1]-err[at+1])/dd,-.5,.5))
 poses.append({'frame':f,'y':y+sub,'alpha':float(np.clip(alpha[at],0,1))})
path=save('v10-checkin-art-measurement',art)
(O/'checkin.json').write_text(json.dumps({'box':box,'path':path,'poses':poses},indent=2));print('Check-in',box,poses[:2],poses[-1:])
