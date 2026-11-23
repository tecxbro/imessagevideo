from pathlib import Path
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'project'))
from artwork import font, messages_font
config=json.loads((ROOT/'project/scene.json').read_text())
reference=lambda f:np.asarray(Image.open(ROOT/'source'/f'{f-133:03}.png')).astype('float32').mean(axis=2)

def template(value,family,weight,soft):
 face=family(160,weight)
 p=Image.new('L',(int(face.getlength(value))+18,182))
 ImageDraw.Draw(p).text((5,5),value,font=face,fill=255,anchor='lt')
 p=p.crop(p.getbbox()).resize((600,120),Image.Resampling.BICUBIC)
 return np.asarray(p.filter(__import__('PIL.ImageFilter',fromlist=['GaussianBlur']).GaussianBlur(soft))).astype('float32')/255

fonts=[messages_font,font]
result=[]
for n,key in enumerate(('assistantLine1','assistantLine2')):
 caption=config['copy']['assistant'][n]
 anchors=np.array(config['tracks'][key],float)
 is_first=(n==0)
 start=135 if is_first else 138
 early=[(128,63,.32,.26,9,4.6),(151,59,.55,.40,12,3.5),(168,57,.78,.52,14,2.8),(181,57,1,.61,13,2.2),(191,54,1,.64,10,1.9),(197,54,1,.68,8,1.7),(200,52,1,.72,6,1.5)] if is_first else [(273,46,.12,.08,7,3.4),(281,47,.47,.32,7,2.7),(285,46,.81,.39,7,2.3),(286,45,1,.41,6,1.8),(290,44,1,.48,5,1.6)]
 rows=[]
 for f in range(start,161):
  x0,y0,w0,h0=[np.interp(f,anchors[:,0],anchors[:,i]) for i in range(1,5)]
  w0=369 if is_first else 244
  if not is_first and f>=143:y0+=1
  if f-start<len(early):
   y0,h0,vis0,op0,slant0,soft=early[f-start]
  else:
   vis0,op0,slant0,soft = 1,min(1,.76+(f-142)*.027) if is_first else min(1,.5+(f-143)*.041),max(0,4-(f-142)*.69),max(.35,1.45-(f-142)*.16)
   if f>=157:soft += (f-157)*.52
  xx,yy=np.meshgrid(np.arange(int(x0)-16,int(x0+w0)+17,2),np.arange(max(0,int(y0)-14),int(y0+h0)+26,2))
  target=np.clip(252.6-reference(f)[yy,xx],0,255)/252.6
  mask=np.ones_like(target)
  # The second line can sit close to the descenders on its first frames.
  if n:mask[yy<y0-7]=.45
  temps=[template(caption,fam,weight,soft*2.0) for fam,weight in [(messages_font,615),(font,615)]]
  best=None
  for choice,src in enumerate(temps):
   def predict(pars):
    x,y,w,h,opacity,slant,reveal,feather=pars
    u=(xx-x)/w
    v=(yy-y-slant*u)/h
    image=map_coordinates(src,[v*119,u*599],order=1,mode='constant',cval=0,prefilter=False)
    fade=np.clip((reveal-u)/feather+.5,0,1)
    return image*opacity*fade*fade*(3-2*fade)
   lo=[x0-12,y0-12,w0*.93,h0*.71,.018,-8,.03,.02]
   hi=[x0+12,y0+17,w0*1.06,h0*1.21,1.005,27,1.14,.43]
   seed=[x0,y0,w0,h0,op0,slant0,vis0,.18 if f-start<=6 else .09]
   sol=least_squares(lambda p:((predict(p)-target)*mask).ravel(),seed,bounds=(lo,hi),diff_step=.002,max_nfev=34)
   mse=float(np.mean(sol.fun**2))
   if best is None or mse<best[0]*.98:best=(mse,choice,sol.x)
  mse,choice,v=best
  vals=[*v,soft,choice]
  print(n+1,f,round(mse,5),[round(float(z),3) for z in vals],flush=True)
  rows.append([f, *[round(float(z),5) for z in vals]])
 result.append(rows)
(ROOT/'title-fit.json').write_text(json.dumps(result,indent=2))
