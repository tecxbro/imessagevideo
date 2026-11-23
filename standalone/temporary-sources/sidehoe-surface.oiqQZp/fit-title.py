from pathlib import Path
from PIL import Image,ImageFont,ImageDraw,ImageFilter
import json,sys,numpy as np
from functools import lru_cache
from scipy.optimize import minimize
from scipy.ndimage import gaussian_filter
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
j=json.loads((p/'project/scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
old=Path('/tmp/sidehoe-lens.I4y7rV/combined-frames')
F=Path('/System/Library/Fonts')
samplesH=[('SF'+str(o),F/'SFNS.ttf',0,o) for o in [17,24,28,36,48,66,96]]
samples=[*samplesH,('Inter',p/'project/assets/Inter.ttf',0,0),('Helvetica',F/'Helvetica.ttc',1,0),
 ('Helvetica Neue',F/'HelveticaNeue.ttc',1,0),('Helvetica Neue medium',F/'HelveticaNeue.ttc',10,0),
 ('Avenir Next',F/'Avenir Next.ttc',2,0),('Arial',F/'Supplemental/Arial Bold.ttf',0,0)]
bounds=[[(258,364),(364,410),(410,558),(558,751)],[(225,630),(630,783)]]
@lru_cache(maxsize=900)
def glyph(font_index,word,weight):
 name,path,index,opt=samples[font_index]
 face=ImageFont.truetype(path,190,index=index)
 if path.name=='SFNS.ttf': face.set_variation_by_axes([100,opt,400,weight])
 elif name=='Inter': face.set_variation_by_axes([32,weight])
 img=Image.new('L',(round(face.getlength(word))+25,245))
 ImageDraw.Draw(img).text((8,3),word,font=face,fill=255,anchor='lt')
 return img.crop(img.getbbox())
def measure(frame,line):
 source=np.asarray(Image.open(src/f'{frame:06}.png').convert('RGB'),dtype=float)
 away=np.asarray(Image.open(old/f'{frame:06}.png').convert('RGB'),dtype=float)
 x,y,w,h,opa,*_,r,g,b=interpolate(j['tracks']['personalLettering'][line],frame)
 raw=source[int(y)-5:int(y+h)+7]
 ref=away[int(y)-5:int(y+h)+7]
 ink=np.array([r,g,b]).mean()
 h_base=253-ink
 q=(253-raw.mean(axis=2))/h_base
 u=(253-ref.mean(axis=2))/h_base
 mask=(raw[:,:,0]-raw[:,:,1])<(35 if not line else max(30,r-g+13))
 # Where the other line extends into the crop, suppress its overlap.
 if line:
  mask[:5]=False
 else:
  d=round(interpolate(j['tracks']['personalLettering'][1],frame)[1])-int(y)+4
  mask[max(0,d):]=False
 return y,q,u,mask
def solve(frame,line, fonts):
 y,alpha,before,usable=measure(frame,line)
 words=j['copy']['personal'][line].split()
 results=[]
 for index,(x0,x1) in enumerate(bounds[line]):
  word=words[index]
  goal=alpha[:,x0:x1]; previous=before[:,x0:x1]; mask=usable[:,x0:x1]
  ij=np.array(np.where((goal>.49)&mask))
  if not ij.size: raise ValueError(frame,line,index)
  top,left=ij.min(axis=1)
  bot,right=ij.max(axis=1)+1
  # Mask the untouched neighboring words and the colors of the hearts.
  fits=[]
  for k in fonts:
   style=samples[k][0]
   weights=([560,600,640,680] if line==0 else [630,670,710,750]) if (style.startswith('SF') or style=='Inter') else [640]
   for weight in weights:
    shape=glyph(k,word,weight)
    gw,gh=shape.size
    def evaluation(params):
     left,top,w,h,blur,level=params
     predicted=shape.transform((x1-x0,goal.shape[0]),Image.Transform.AFFINE,(gw/w,0,-left*gw/w,0,gh/h,-top*gh/h),Image.Resampling.BICUBIC)
     pred=np.asarray(predicted,dtype=float)/255
     if blur>0.10:
      pred=gaussian_filter(pred,blur,mode='constant')
     return np.mean(np.abs(pred[mask]*level-goal[mask]))
    start=[left,top,right-left,bot-top,.52,1.]
    if line==0 and index==2:
     # The descender intersects the next line's optical envelope.
     start[3]+=max(1,round((bot-top)*.19))
    config=[(start[0]-3,start[0]+3),(start[1]-2,start[1]+2),(start[2]-6,start[2]+7),(start[3]-5,start[3]+8),(.2,1.5),(.84,1.08)]
    fit=minimize(evaluation,start,method='Powell',bounds=config,options={'xtol':.07,'ftol':.006,'maxiter':20})
    fits.append((fit.fun,k,weight,*fit.x))
  best=sorted(fits)
  results.append(best)
  d=np.mean(np.abs(previous[mask]-goal[mask]))
  print(frame,line,word,'current',round(d,4),'best',[(round(x[0],4),samples[x[1]][0],x[2],np.round(x[3:],1).tolist()) for x in best[:5]],flush=True)
 return results
for frame in [190]:
 for line in (0,1): solve(frame,line,range(len(samples)))
