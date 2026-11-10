"""Measure every exposed display/page region, including the offstage sheet's bottom."""
from pathlib import Path
import sys,json,copy,subprocess
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
AS=REF/'assets/root-backplane-stencil-v5';AS.mkdir(exist_ok=True);spec=copy.deepcopy(json.loads((REF/'root-backplane-patch-v4.json').read_text()));spec['layers']=[l for l in spec['layers'] if not l['id'].startswith(('root-backplane-material-','root-backplane-ui-ink-')) or int(l['id'].split('-')[-1])<679];spec['measurements']=[r for r in spec['measurements'] if r['frame']<679];spec['stencilLayers']=[];ex=json.loads((REF/'root-backplane-food-exclusions-v4.json').read_text());scene=json.loads((ROOT/'outputs/03-photon-mini/final-v13/scene.json').read_text());physical=next(l for l in scene['layers'] if l['id']=='measured-lunch-display-dim-v13')
def value(ks,t):
 for a,b in zip(ks,ks[1:]):
  if a['t']<=t<=b['t']:
   p=(t-a['t'])/(b['t']-a['t']);return a['value']+(b['value']-a['value'])*p
 return ks[0]['value'] if t<ks[0]['t'] else ks[-1]['value']
def spans(mask):
 filled=np.zeros_like(mask)
 for y in range(mask.shape[0]):
  xs=np.where(mask[y])[0]
  if len(xs):filled[y,xs.min():xs.max()+1]=True
 return filled
proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',"select='between(n,679,734)'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
for n in range(679,735):
 raw=proc.stdout.read(1920*1080*3)
 if len(raw)!=1920*1080*3:raise ValueError('Incomplete source')
 a=np.frombuffer(raw,np.uint8).reshape(1080,1920,3);cam={k:value(v,n/30) for k,v in physical['keyframes'].items() if k in ('x','y','scaleX','scaleY')};sx,sy=cam['scaleX'],cam['scaleY'];left=cam['x']+28*sx;right=cam['x']+772*sx;top=cam['y']+30*sy;bottom=cam['y']+1630*sy
 domain_image=Image.new('L',(1920,1080));ImageDraw.Draw(domain_image).rounded_rectangle((left,top,right,bottom),radius=120*min(sx,sy),fill=255);domain=np.array(domain_image)>0;yy,xx=np.where(domain);x0=max(0,int(xx.min())-2);x1=min(1920,int(xx.max())+3);y0=max(0,int(yy.min())-2);y1=min(1080,int(yy.max())+3);rgb=a[y0:y1,x0:x1].astype(float);g=rgb.mean(2);dm=domain[y0:y1,x0:x1];neutral=rgb.max(2)-rgb.min(2)<10
 white=(g>245)&neutral&dm;lab,_=ndimage.label(white,np.ones((3,3)));opts=[]
 for i,sl in enumerate(ndimage.find_objects(lab)):
  if sl is not None:
   yy_,xx_=sl;area=int((lab[sl]==i+1).sum())
   if area>100 and xx_.stop-xx_.start>15:opts.append((area,i+1))
 front=spans(lab==max(opts)[1])&dm if opts else np.zeros_like(dm)
 exposed=dm&~front;valid=neutral&(g>100)&(g<252)&exposed;hist=np.bincount(np.rint(g[valid]).astype(np.uint8),minlength=256);mode=int(hist.argmax()) if hist.any() else 128;core=valid&(abs(g-mode)<=3);glab,_=ndimage.label(core,np.ones((3,3)));chosen=[]
 for i,sl in enumerate(ndimage.find_objects(glab)):
  if sl is not None:
   yy_,xx_=sl;area=int((glab[sl]==i+1).sum())
   if area>20 and (yy_.stop-yy_.start>10 or xx_.stop-xx_.start>10):chosen.append(i+1)
 gray=spans(np.isin(glab,chosen))&dm;visible_gray=gray&exposed;children=[]
 for kind,mask,fill in [('black',exposed,'#000000'),('gray',visible_gray,'#'+f'{mode:02x}'*3)]:
  d,_=trace_alpha(mask.astype(float))
  if d:children.append({'id':f'root-backplane-stencil-{kind}-{n}','type':'path','d':d,'fill':fill,'semanticText':'Native exposed display/page occlusion stencil'})
 support=(ndimage.binary_dilation(gray,iterations=2)|ndimage.binary_dilation(front,iterations=3))&exposed&dm;base=np.where(gray,mode,0);ink=(np.max(abs(rgb-base[:,:,None]),axis=2)>2)&support
 for bx0,by0,bx1,by1 in ex['bounds'].get(str(n),[]):
  m=ex['margin'];xa=max(0,bx0-m-x0);xb=min(x1-x0,bx1+m-x0);ya=max(0,by0-m-y0);yb=min(y1-y0,by1+m-y0)
  if xb>xa and yb>ya:ink[ya:yb,xa:xb]=False
 for rule in ex.get('shapeMasks',[]):
  if rule['frame']!=n:continue
  mx0,my0,mx1,my1=rule['bounds'];mask=np.array(Image.open(rule['file']).convert('L'))>0;xa=max(x0,mx0);xb=min(x1,mx1);ya=max(y0,my0);yb=min(y1,my1)
  if xb>xa and yb>ya:ink[ya-y0:yb-y0,xa-x0:xb-x0]&=~mask[ya-my0:yb-my0,xa-mx0:xb-mx0]
 rgba=np.dstack([rgb.astype(np.uint8),np.uint8(ink)*255]);rgba[~ink,:3]=0;asset=AS/f'visible-ui-ink-{n}.png';Image.fromarray(rgba).save(asset);children.append({'id':f'root-backplane-stencil-ink-{n}','type':'image','src':str(asset),'width':x1-x0,'height':y1-y0,'sourceFrame':n,'semanticText':'Only actually exposed Messages UI and optical edge ink','editability':'Bounded transparent original UI/edge ink outside the actual foreground white-body silhouette. No foreground row/artwork, food/order actor, hardware or whole-frame playback.'});spec['stencilLayers'].append({'id':f'root-backplane-stencil-{n}','type':'group','x':x0,'y':y0,'start':n/30,'end':(n+1)/30,'children':children});spec['measurements'].append({'frame':n,'stencil':True,'bounds':[x0,y0,x1,y1],'pageGray':mode,'foregroundPixels':int(front.sum()),'exposedGrayPixels':int(visible_gray.sum()),'inkPixels':int(ink.sum())})
proc.stdout.close();assert proc.wait()==0
spec['notice']='Independent exposed-page/display native stencil after foreground and before hardware for679–734. Actual white-body row-span silhouette excludes all foreground content; bounded exposed UI/edge ink is separate.618–678 preserved fromV4, all food/order exclusions retained.';(REF/'root-backplane-patch-v5.json').write_text(json.dumps(spec,indent=2));print(spec['measurements'][-6:])
