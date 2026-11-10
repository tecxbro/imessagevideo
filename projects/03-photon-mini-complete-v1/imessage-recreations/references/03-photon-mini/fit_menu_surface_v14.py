from pathlib import Path
from PIL import Image
from scipy import ndimage,optimize
import numpy as np,json,copy
P=Path(__file__).parent;s=json.loads((P/'joint-v14-provisional.scene.json').read_text());base=next(x for x in s['layers'] if x['id']=='measured-menu-clip-v13');surface=next(x for x in s['layers'] if x['id']=='measured-menu-surface-v13');frames=[];proof=[]
for f in range(618,730):
 a=np.array(Image.open(P/'lunch-native'/f'{f-609:03}.png').convert('RGB'));m=a.min(2)>246;lab,n=ndimage.label(m);cs=[]
 for i,b in enumerate(ndimage.find_objects(lab),1):
  if b is None:continue
  y,x=b;w=x.stop-x.start;h=y.stop-y.start
  if not (150<w<900 and h>80 and abs((x.start+x.stop)/2-960)<220):continue
  area=int((lab[b]==i).sum())
  if area>8000:cs.append((area,i,b))
 if not cs:continue
 _,i,b=max(cs);yy,xx=b;L,T,R,B=xx.start,yy.start,xx.stop,yy.stop;W=R-L;profiles=[]
 # Native header fill is separated from body by its full-width gray divider.
 for j,c in enumerate(ndimage.find_objects(lab),1):
  if c is None:continue
  y,x=c
  if y.stop<=T+2 and y.stop>T-220 and x.stop-x.start>.85*W and x.start>=L-10 and x.stop<=R+10:T=min(T,y.start)
 body=(lab[b]==i)
 if B<1079:
  for y in range(max(0,body.shape[0]-250),body.shape[0]-2):
   xs=np.where(body[y])[0]
   if len(xs) and xs.min()<W*.42:profiles.append((y+yy.start,float(xs.min()+L)))
  def fun(v):
   rad=v[0];z=[]
   for y,x in profiles:
    pred=L if y<=B-rad else L+rad-np.sqrt(max(0,rad*rad-(y-(B-rad))**2));z.append(pred-x)
   return z
  fit=optimize.least_squares(fun,[min(120,W/4)],bounds=([10],[W/2]),loss='soft_l1',f_scale=2);rad=float(fit.x[0]);fitcost=float(np.mean(np.abs(fun([rad]))))
 else:B=2000;rad=70;fitcost=None
 if T==0:T=-1000
 clone=copy.deepcopy(base);clone.pop('start',None);clone.pop('end',None)
 def rename(node):
  node['id']=f'surface14-{f}-'+node['id']
  for c in node.get('children',[]):rename(c)
 rename(clone)
 # Clip is in stage coordinates. The child retains independent measured camera/rows.
 root={'id':f'measured-surface-frame-{f}-v14','type':'group','start':f/30,'end':(f+1)/30,'clip':{'x':L,'y':T,'width':W,'height':B-T,'radius':rad},'children':[{'id':f'surface14-{f}-white','type':'rect','x':L,'y':T,'width':W,'height':B-T,'radius':rad,'fill':'#fdfdfd'},clone]};frames.append(root);proof.append({'frame':f,'pane':[L,T,R,B],'radius':rad,'radius_fit_mean_abs_px':fitcost})
s['layers']=[x for x in s['layers'] if x['id'] not in ['measured-menu-clip-v13','measured-menu-surface-v13']];base=copy.deepcopy(base);base['start']=730/30;s['layers'].append(base);ix=next(i for i,x in enumerate(s['layers']) if x['id']=='measured-lunch-bezel-overlay-v13');s['layers'][ix:ix]=[{'id':'measured-menu-native-surface-v14','type':'group','start':618/30,'end':730/30,'children':frames}]
(P/'joint-fitted-surface-v14.scene.json').write_text(json.dumps(s,indent=2));(P/'menu-surface-v14-measurements.json').write_text(json.dumps(proof,indent=2));print('built',len(frames))
