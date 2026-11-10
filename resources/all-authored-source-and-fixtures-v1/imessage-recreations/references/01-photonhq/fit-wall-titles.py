from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset
import numpy as np,json,shutil
R=Path('/workspace/imessage-recreations/references/01-photonhq');candidates=[]
for wt in [400,500,600,700]:candidates.append(dict(name=f'Inter{wt}',path=str(R/'assets'/f'Inter-{wt}.ttf')))
for wt in [400,450,500,550,600]:candidates.append(dict(name=f'Geist{wt}',path=str(R/'assets'/'Geist-variable.ttf'),variation=wt))
for sty in ['Regular','Medium','Semibold','Bold']:candidates.append(dict(name='SFDisplay'+sty,path=f'/workspace/imessage-recreations/shared/fonts/SF-Pro-Display-{sty}.otf'))
for sty in ['Regular','Bold']:candidates.append(dict(name='NimbusSans'+sty,path=f'/usr/share/fonts/opentype/urw-base35/NimbusSans-{sty}.otf'))
for sty in ['Regular','Medium','Semibold','Bold']:candidates.append(dict(name='OpenAISans'+sty,path=f'/usr/share/fonts/openai-sans/OpenAISans-{sty}.woff2'))
phases=[('sms',270,'10,000+ SMS'),('calls',336,'8000+ voice minutes'),('imessage',372,'Unlimited iMessage'),('whatsapp',408,'Unlimited WhatsApp'),('telegram',444,'Unlimited Telegram')]
results={}
for name,n,copy in phases:
 a=np.array(Image.open(R/f'assets/wall-art/measure/{n:04d}.png').convert('RGB'));alpha=(255-a[:,:,0])/255;roi=alpha[470:620,200:1720];yy,xx=np.where(roi>.5);box=[int(xx.min()+200),int(yy.min()+470),int(xx.max()+201),int(yy.max()+471)];target=alpha[box[1]:box[3],box[0]:box[2]];scores=[]
 for cand in candidates:
  for sz in [88,92,96,100]:
   f=ImageFont.truetype(cand['path'],sz)
   if 'variation' in cand:f.set_variation_by_axes([cand['variation']])
   bb=f.getbbox(copy);im=Image.new('L',(bb[2]-bb[0]+4,bb[3]-bb[1]+4));ImageDraw.Draw(im).text((-bb[0]+2,-bb[1]+2),copy,font=f,fill=255);ar=np.array(im);y,x=np.where(ar>128);im=im.crop((int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)));im=im.resize((target.shape[1],target.shape[0]),Image.Resampling.LANCZOS);score=float(np.mean((np.array(im)/255-target)**2));scores.append(dict(mse=score,size=sz,**cand))
 scores.sort(key=lambda d:d['mse']);best=scores[0];src=Path(best['path']);dest=R/'assets'/f'wall-title-{name}{src.suffix if src.suffix!=".woff2" else ".woff2"}'
 if src.suffix=='.woff2':shutil.copyfile(src,dest)
 else:
  font=TTFont(src)
  if 'variation' in best:instantiateVariableFont(font,{'wght':best['variation']},inplace=True)
  opts=subset.Options();sub=subset.Subsetter(options=opts);sub.populate(text=copy);sub.subset(font);font.save(dest)
 results[name]=dict(copy=copy,source_frame=n,source_bbox=box,font_asset=str(dest.relative_to(R)),family='Photon Wall '+name,selected=best,top_candidates=scores[:12])
 print(name,'bbox',box,'best',best['name'],best['size'],round(best['mse'],5),flush=True)
(R/'wall-title-fit.json').write_text(json.dumps(results,indent=2))
