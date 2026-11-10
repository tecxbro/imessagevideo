from pathlib import Path
import importlib.util,json,math
from PIL import Image
import numpy as np
from scipy.ndimage import label
R=Path(__file__).resolve().parent;S=R/'source-native';traceSpec=importlib.util.spec_from_file_location('trace',R.parent.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(traceSpec);traceSpec.loader.exec_module(trace)
def load(n):return np.asarray(Image.open(S/f'{n:06d}.png').convert('RGB')).astype(float)
def cleaned(mask,minsize=4):
 labs,num=label(mask);sizes=np.bincount(labs.ravel());keep=sizes>=minsize;keep[0]=False;return keep[labs]
def bbox(mask,x=0,y=0):
 yy,xx=np.nonzero(mask)
 return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+x+1),int(yy.max()+y+1)] if len(xx)>10 else None
def measure(a,roi,fill):
 l,t,r,b=map(int,roi);arr=a[t:b,l:r];v=255-np.array(fill);alpha=np.clip(np.sum((255-arr)*v,2)/np.sum(v*v),0,1);peak=float(np.quantile(alpha[alpha>.35*alpha.max()],.95)) if alpha.max()>.02 else 0
 if peak<.025:return None
 mask=cleaned(alpha>peak*.5);bb=bbox(mask,l,t)
 if bb is None:return None
 return dict(bbox=bb,opacity=peak)
def inkalpha(a,fill):
 v=255-np.array(fill);return np.clip(np.sum((255-a)*v,2)/np.sum(v*v),0,1)
canonical=load(346);colorROI=canonical[450:630,400:1048];gm=(colorROI[:,:,1]-colorROI[:,:,0]>55)&(colorROI[:,:,1]-colorROI[:,:,2]>15)&(colorROI[:,:,0]<70);colors,count=np.unique(colorROI[gm].astype(np.uint8),axis=0,return_counts=True);green=colors[np.argmax(count)].tolist();print('Source green mode',green,flush=True)
records=[];parts=['The','best contact','in your phone','with multiplayer mode'];fixedX=[(175,400),(400,1048),(1048,1750)]
for n in range(321,379):
 a=load(n);z=a[300:700,400:1048];strength=z[:,:,1]-z[:,:,0];peak=strength.max();g=(strength>max(5,peak*.45))&(z[:,:,1]-z[:,:,2]>max(3,peak*.18));bb=bbox(cleaned(g),400,300)
 if bb is None:raise RuntimeError('Missing real green title'+str(n))
 top=bb[1];row=dict(frame=n,phase='best contact',parts={});firstband=(max(0,top-8),min(1080,top+121))
 for j,name in enumerate(parts[:3]):
  l,r=fixedX[j];q=measure(a,[l,firstband[0],r,firstband[1]],green if j==1 else [0,0,0]);row['parts'][name]=q
 if n>=350:
  q=measure(a,[390,top+122,1530,780],[0,0,0])
  if q:row['parts'][parts[3]]=q
 records.append(row)
# Watches has actual separate text runs once the independent Messages icon enters.
for n in range(379,408):
 a=load(n);z=a[350:720,250:1700];neutral=z.max(2)-z.min(2)<16;alpha=(255-z.mean(2))/255;peak=float(np.quantile(alpha[neutral&(alpha>.35*alpha.max())],.97));mask=cleaned(neutral&(alpha>peak*.5));xs=np.where(mask.any(0))[0];groups=[]
 for x in xs:
  if not groups or x-groups[-1][-1]>20:groups.append([int(x)])
  else:groups[-1].append(int(x))
 boxes=[bbox(mask[:,gg[0]:gg[-1]+1],250+gg[0],350) for gg in groups];boxes=[q for q in boxes if q]
 if len(boxes)!=3:raise RuntimeError('Unexpected Watches word splits'+str((n,boxes)))
 first=[boxes[0][0],min(boxes[0][1],boxes[1][1]),boxes[1][2],max(boxes[0][3],boxes[1][3])];last=boxes[2];row=dict(frame=n,phase='Watches',parts={'Watches your':dict(bbox=first,opacity=peak),'inbox':dict(bbox=last,opacity=peak)})
 # Icon color signal is deliberately absolute/adaptive, not the old ratio-only detector.
 z=a[300:760,900:1410];st=z[:,:,1]-z[:,:,0];pk=float(st.max())
 if pk>10:
  mask=cleaned((st>max(5,pk*.45))&(z[:,:,1]-z[:,:,2]>max(3,pk*.2)));bb=bbox(mask,900,300)
  if bb:row['icon']=dict(colorBounds=bb,peakGreenRed=pk)
 records.append(row)
# Static semantic glyph shapes; no entire frame is stored as a runtime image.
native=[]
for name,frame,fill in [(p,346,green if p=='best contact' else [0,0,0]) for p in parts[:3]]+[('with multiplayer mode',367,[0,0,0]),('Watches your',403,[0,0,0]),('inbox',403,[0,0,0])]:
 row=next(q for q in records if q['frame']==frame);b=row['parts'][name]['bbox'];l,t,r,bot=b;pad=3;a=load(frame)[t-pad:bot+pad,l-pad:r+pad];alpha=inkalpha(a,fill);d,stats=trace.trace_alpha(alpha,-pad,-pad);native.append(dict(label=name,sourceFrame=frame,sourceBounds=b,width=r-l,height=bot-t,fill='#'+bytes(fill).hex(),path=d,traceStats=stats,notice='Bounded original semantic typography reconstructed as native vector contours; not live font copy.'))
(R/'measurements.json').write_text(json.dumps(records,indent=2));(R/'native-outlines.json').write_text(json.dumps(native,indent=2));print('Measured',len(records),'native poses; outlined',len(native),'semantic fragments',flush=True)
for q in records:
 if q['frame'] in [321,322,323,350,351,352,353,354,356,357,378,379,398,399,400,403,407]:print(q,flush=True)
