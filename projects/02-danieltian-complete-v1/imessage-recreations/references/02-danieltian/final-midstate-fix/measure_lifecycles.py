from pathlib import Path
import sys,json,math,copy,re,time
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parent;ROOT=R.parents[2];cv2.setNumThreads(1);chat=json.loads((R/'chat-original.json').read_text());nodes={}
def walk(n):
 nodes[n['id']]=n
 for c in n.get('children',[]):walk(c)
walk(chat)
def sample(n,k,f):
 ks=n.get('keyframes',{}).get(k,[]);t=f/30;default=n.get(k,1 if k in['scaleX','scaleY','opacity']else 0)
 if not ks:return default
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:
   p=(t-a['t'])/(b['t']-a['t']);ease=b.get('ease','linear')
   if ease=='easeOut':p=1-(1-p)**3
   elif ease=='easeIn':p=p**3
   return a['value']+(b['value']-a['value'])*p
 return ks[-1]['value']
def source(f):return np.asarray(Image.open(R/'source-native'/f'source-{f:04d}.png').convert('RGB'))
def pink_bbox(a):
 crop=a[:,300:505];hsv=cv2.cvtColor(crop,cv2.COLOR_RGB2HSV);mask=(hsv[:,:,0]>158)&(hsv[:,:,0]<178)&(hsv[:,:,1]>105)&(hsv[:,:,2]>130);lab,count=ndimage.label(mask);comps=[]
 for k,bb in enumerate(ndimage.find_objects(lab),1):
  if bb is None:continue
  yy,xx=bb;ys,xs=np.nonzero(lab[bb]==k);area=len(xs);cx=(xx.start+xx.stop)/2+300
  if area>=3 and 320<cx<491:comps.append((area,k,np.array([cx,(yy.start+yy.stop)/2])))
 if not comps or max(c[0]for c in comps)<100:return None
 _,k,center=max(comps,key=lambda q:q[0]);keep=[v for area,v,c in comps if np.linalg.norm(c-center)<125];union=np.isin(lab,keep);yy,xx=np.nonzero(union);return[int(xx.min()+300),int(yy.min()),int(xx.max()+301),int(yy.max()+1)]
# Measure original logo intrinsic colored bounds, preserving original image pixels.
av=nodes['middle-avatar-how-about'];im=av['children'][0];asset=np.asarray(Image.open(im['src']).convert('RGBA'));hsv=cv2.cvtColor(asset[:,:,:3],cv2.COLOR_RGB2HSV);tm=(hsv[:,:,0]>158)&(hsv[:,:,0]<178)&(hsv[:,:,1]>105)&(hsv[:,:,2]>130)&(asset[:,:,3]>127);yy,xx=np.nonzero(tm);intrinsic=np.array([xx.min(),yy.min(),xx.max()+1,yy.max()+1],float)*[im['width']/asset.shape[1],im['height']/asset.shape[0],im['width']/asset.shape[1],im['height']/asset.shape[0]];avatars=[]
for f in range(802,871):
 a=source(f);b=np.asarray(Image.open(R/'baseline-v14-native'/f'{f:06d}.png').convert('RGB'));s=pink_bbox(a);c=pink_bbox(b);avatars.append({'frame':f,'sourceColorBounds':s,'nativeColorBounds':c,'oldLifeVisible':av.get('start',0)<=f/30<av.get('end',999),'boundsError':float(np.max(abs(np.array(s)-c)))if s and c else None})
full=[q for q in avatars if q['sourceColorBounds']and q['sourceColorBounds'][3]<1078 and q['sourceColorBounds'][2]-q['sourceColorBounds'][0]>60];f0=full[0]['frame'];fitrows=[q for q in full if q['frame']<f0+8];fw=np.polyfit([q['frame']-f0 for q in fitrows],[q['sourceColorBounds'][2]-q['sourceColorBounds'][0]for q in fitrows],1);fh=np.polyfit([q['frame']-f0 for q in fitrows],[q['sourceColorBounds'][3]-q['sourceColorBounds'][1]for q in fitrows],1)
for q in avatars:
 if not q['sourceColorBounds']:continue
 l,t,r,b=q['sourceColorBounds'];W=r-l;H=b-t
 if b>=1078:
  W=float(np.polyval(fw,q['frame']-f0));H=float(np.polyval(fh,q['frame']-f0));cx=(l+r)/2;l=cx-W/2
 sx=W/(intrinsic[2]-intrinsic[0]);sy=H/(intrinsic[3]-intrinsic[1]);q['measuredPose']={'x':float(l-intrinsic[0]*sx),'y':float(t-intrinsic[1]*sy),'scaleX':float(sx),'scaleY':float(sy)};q['needsCorrection']=not q['oldLifeVisible']or q['nativeColorBounds']is None or(q['boundsError']or 0)>2
(R/'avatar-measurements.json').write_text(json.dumps({'intrinsicLogicalColorBounds':intrinsic.tolist(),'firstFullSourceFrame':f0,'rows':avatars},indent=2));print('avatar corrections',[q['frame']for q in avatars if q.get('needsCorrection')],flush=True)
# Locate the existing native Airbnb glyph shape by matching the true source855 word.
label=nodes['middle-airbnb-card-sender-label'];raw=[float(x)for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)',label['d'])];bb=np.array([min(raw[::2]),min(raw[1::2]),max(raw[::2]),max(raw[1::2])]);crop=np.array([math.floor(bb[0])-4,math.floor(bb[1])-4,math.ceil(bb[2])+4,math.ceil(bb[3])+4]);s855=source(855);template=np.clip(253-s855[crop[1]:crop[3],crop[0]:crop[2]].mean(2),0,253).astype('uint8');labels=[]
for f in range(802,871):
 a=source(f);search=np.clip(253-a[:,470:760].mean(2),0,253).astype('uint8');oldscale=sample(label,'scaleX',f);best=None
 for sc in np.linspace(oldscale-.035,oldscale+.035,15):
  temp=cv2.resize(template,None,fx=float(sc),fy=float(sc),interpolation=cv2.INTER_CUBIC);m=cv2.matchTemplate(search,temp,cv2.TM_CCOEFF_NORMED);_,score,_,loc=cv2.minMaxLoc(m)
  if best is None or score>best[0]:best=(score,sc,loc)
 score,sc,(x,y)=best;pose={'x':float(x+470-crop[0]*sc),'y':float(y-crop[1]*sc),'scaleX':float(sc),'scaleY':float(sc)};old=np.array([sample(label,'x',f)+sample(label,'scaleX',f)*bb[0],sample(label,'y',f)+sample(label,'scaleY',f)*bb[1],sample(label,'x',f)+sample(label,'scaleX',f)*bb[2],sample(label,'y',f)+sample(label,'scaleY',f)*bb[3]]);new=np.array([pose['x']+sc*bb[0],pose['y']+sc*bb[1],pose['x']+sc*bb[2],pose['y']+sc*bb[3]]);visible=label.get('start',0)<=f/30<label.get('end',999);labels.append({'frame':f,'score':float(score),'measuredPose':pose,'matchedGlyphBounds':new.tolist(),'oldGlyphBounds':old.tolist(),'oldVisible':visible,'boundsError':float(np.max(abs(old-new))),'needsCorrection':bool(score>.83 and(not visible or np.max(abs(old-new))>2))})
(R/'label-measurements.json').write_text(json.dumps({'glyphLocalBounds':bb.tolist(),'templateSourceCrop':crop.tolist(),'rows':labels},indent=2));print('label matches/corrections',[(q['frame'],round(q['score'],3),round(q['boundsError'],1))for q in labels if q['needsCorrection']],flush=True)
# White paths contain exterior paper corners; isolate the real lettering in a native interior clip.
atlas=np.asarray(Image.open(R/'glyph-atlas/0.000.png').convert('RGB'))[:,:,0].astype('float32')/255;records={}
for role,first,last,offset,W,H in[('budget-reply',748,790,0,466,124),('love-it',904,940,200,180,92)]:
 mask=atlas[offset:offset+200].copy();keep=np.zeros_like(mask);keep[20:H-20,20:W-20]=1;mask*=keep;g=nodes['middle-message-'+role];glyph=nodes['middle-glyphs-'+role];out=[]
 for f in range(first,last+1):
  a=source(f).astype(float);blue=(a[:,:,2]-a[:,:,0]>80)&(a[:,:,1]-a[:,:,0]>35)&(a[:,:,0]<120);blue[:,:950]=False;lab,count=ndimage.label(blue);sizes=np.bincount(lab.ravel());sizes[0]=0;k=int(sizes.argmax());ys,xs=np.nonzero(lab==k)
  if sizes[k]<500 or len(xs)==0:out.append({'frame':f,'copyPresent':False,'reason':'no visible outgoing body'});continue
  body=ndimage.binary_fill_holes(lab==k);inside=ndimage.binary_erosion(body,iterations=4);l=max(0,int(xs.min())-12);t=max(0,int(ys.min())-12);r=min(1920,int(xs.max())+13);b=min(1080,int(ys.max())+13);roi=a[t:b,l:r];bm=blue[t:b,l:r];bg=[]
  for j in range(b-t):bg.append(float(np.median(roi[j,:,0][bm[j]]))if bm[j].any()else 40.)
  bg=np.array(bg)[:,None];observed=(np.clip((roi[:,:,0]-bg)/(255-bg),0,1)*inside[t:b,l:r]).astype('float32');M=np.float32([[sample(g,'scaleX',f),0,sample(g,'x',f)-l],[0,sample(g,'scaleY',f),sample(g,'y',f)-t]]);pred=cv2.warpAffine(mask,M,(r-l,b-t),flags=cv2.INTER_LINEAR);alpha=pred.sum();frac=float((pred*inside[t:b,l:r]).sum()/max(1e-6,alpha));py,px=np.nonzero(pred>.02)
  if not len(px)or frac<.88:out.append({'frame':f,'copyPresent':False,'reason':'typing body narrower than full copy','fractionInside':frac});continue
  x0,x1=max(0,px.min()-5),min(r-l,px.max()+6);y0,y1=max(0,py.min()-5),min(b-t,py.max()+6);p=pred[y0:y1,x0:x1];o=observed[y0:y1,x0:x1];# Same-size normalized correlation plus a small actual source translation search.
  best=(-2,0.,0,0)
  for dy in range(-3,4):
   for dx in range(-3,4):
    pp=cv2.warpAffine(p,np.float32([[1,0,dx],[0,1,dy]]),(p.shape[1],p.shape[0]));corr=float(cv2.matchTemplate(o,pp,cv2.TM_CCOEFF_NORMED)[0,0]);kfit=float(np.sum(pp*o)/max(1e-6,np.sum(pp*pp)))
    if corr>best[0]:best=(corr,kfit,dx,dy)
  corr,kfit,dx,dy=best;out.append({'frame':f,'copyPresent':bool(corr>.52 and kfit>.025),'correlation':corr,'opacityFit':kfit,'fitShift':[dx,dy],'fractionInside':frac,'oldOpacity':sample(glyph,'opacity',f),'blueBounds':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]})
 hold=[q['opacityFit']for q in out if q.get('copyPresent')and q['frame']>=last-5];normal=float(np.median(hold))
 for q in out:q['normalizedOpacity']=float(np.clip(q.get('opacityFit',0)/normal,0,1))if q.get('copyPresent')else 0.
 records[role]={'heldNormalization':normal,'rows':out};print(role,'measured',[(q['frame'],round(q.get('correlation',0),3),round(q['normalizedOpacity'],3),q.get('oldOpacity'))for q in out if q.get('copyPresent')],flush=True)
(R/'white-copy-measurements.json').write_text(json.dumps(records,indent=2));print('DONE',flush=True)
