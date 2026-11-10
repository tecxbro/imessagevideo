"""Extend the independently measured backplane through the five return frames."""
from pathlib import Path
import sys,json,subprocess,copy
import numpy as np
from scipy import ndimage
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
AS=REF/'assets/root-backplane-return';AS.mkdir(exist_ok=True);N=REF/'assets/root-backplane-measure';spec=copy.deepcopy(json.loads((REF/'root-backplane-patch.json').read_text()));spec['scope']=[[618,734]];spec['layers'][0]['end']=735/30
scene=json.loads((ROOT/'outputs/03-photon-mini/final-v13/scene.json').read_text());physical=next(l for l in scene['layers'] if l['id']=='measured-lunch-display-dim-v13');exclusions=json.loads((REF/'root-backplane-food-exclusions.json').read_text())
def value(ks,t):
 for a,b in zip(ks,ks[1:]):
  if a['t']<=t<=b['t']:
   p=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*p
 return ks[0]['value'] if t<ks[0]['t'] else ks[-1]['value']
proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',"select='between(n,730,734)'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
for n in range(730,735):
 raw=proc.stdout.read(1920*1080*3);a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3);Image.fromarray(a).save(N/f'frame-{n}.png');cam={k:value(v,n/30) for k,v in physical['keyframes'].items() if k in ('x','y','scaleX','scaleY')};s=cam['scaleX'];rx0=max(0,round(cam['x']+38*s));rx1=min(1920,round(cam['x']+762*s));roi=a[:,rx0:rx1].astype(float);g=roi.mean(2);neutral=(roi.max(2)-roi.min(2)<10)&(g>100)&(g<244);colors,c=np.unique(np.rint(g[neutral]).astype(int),return_counts=True);mode=int(colors[c.argmax()]);m=neutral&(abs(g-mode)<=3);lab,_=ndimage.label(m,np.ones((3,3)));labels=[]
 for i,sl in enumerate(ndimage.find_objects(lab)):
  if sl is not None:
   yy,xx=sl;area=int((lab[sl]==i+1).sum())
   if area>100 and xx.stop-xx.start>15:labels.append(i+1)
 core=np.isin(lab,labels);filled=np.zeros_like(core)
 for y in range(1080):
  xs=np.where(core[y])[0]
  if len(xs):filled[y,xs.min():xs.max()+1]=True
 canvas=np.zeros((1080,1920),bool);canvas[:,rx0:rx1]=filled;yy,xx=np.where(canvas);x0=max(0,int(xx.min())-3);x1=min(1920,int(xx.max())+4);y0=max(0,int(yy.min())-3);y1=min(1080,int(yy.max())+4);crop=canvas[y0:y1,x0:x1];d,_=trace_alpha(crop.astype(float));spec['layers'].append({'id':f'root-backplane-material-{n}','type':'path','d':d,'x':x0,'y':y0,'fill':'#'+f'{mode:02x}'*3,'start':n/30,'end':(n+1)/30,'semanticText':'Messages page returning behind collapsing lunch mini-app'})
 # The foreground white sheet remains a separate native element. Exclude its
 # entire connected interior, including its colored UI holes, from the ink layer.
 white=(g>245)&(roi.max(2)-roi.min(2)<8);wl,_=ndimage.label(white,np.ones((3,3)));opts=[]
 for i,sl in enumerate(ndimage.find_objects(wl)):
  if sl is not None:
   yy_,xx_=sl;area=int((wl[sl]==i+1).sum())
   if area>100 and xx_.stop-xx_.start>20:opts.append((area,i+1))
 front=np.zeros_like(white)
 if opts:
  _,label=max(opts);front=ndimage.binary_fill_holes(wl==label);front=ndimage.binary_dilation(front,iterations=3)
 fw=np.zeros_like(canvas);fw[:,rx0:rx1]=front;rgb=a[y0:y1,x0:x1];support=ndimage.binary_dilation(crop,iterations=2);ink=(np.max(abs(rgb.astype(float)-mode),axis=2)>3)&support&~fw[y0:y1,x0:x1];
 for bx0,by0,bx1,by1 in exclusions['bounds'].get(str(n),[]):
  margin=exclusions['margin'];xa=max(0,bx0-margin-x0);xb=min(x1-x0,bx1+margin-x0);ya=max(0,by0-margin-y0);yb=min(y1-y0,by1+margin-y0)
  if xb>xa and yb>ya:ink[ya:yb,xa:xb]=False
 rgba=np.dstack([rgb,np.uint8(ink)*255]);rgba[~ink,:3]=0;asset=AS/f'page-ui-ink-{n}.png';Image.fromarray(rgba).save(asset);spec['layers'].append({'id':f'root-backplane-ui-ink-{n}','type':'image','src':str(asset),'x':x0,'y':y0,'width':x1-x0,'height':y1-y0,'start':n/30,'end':(n+1)/30,'sourceFrame':n,'semanticText':'Visible Messages UI around the collapsing foreground sheet','editability':'Bounded original Messages UI/control ink only. Foreground white sheet is explicitly masked out; native page material and independent placements/lifetimes.'});spec['measurements'].append({'frame':n,'visibleBounds':[x0,y0,x1,y1],'pageGray':mode,'foregroundMaskPixels':int(front.sum()),'UIInkPixels':int(ink.sum())})
proc.stdout.close();assert proc.wait()==0
(REF/'root-backplane-patch-v3.json').write_text(json.dumps(spec,indent=2));print(spec['measurements'][-5:])
