from PIL import Image,ImageFont,ImageDraw
import numpy as np,json
from pathlib import Path
im=Image.open('/workspace/imessage-recreations/references/01-photonhq/keyframes/00.50.png').convert('RGB'); a=np.array(im);mask=(255-a[:,:,0])/255.;mask[:,970:]=0;mask[:,:490]=0
ys,xs=np.where(mask>.3);box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1);target=mask[box[1]:box[3],box[0]:box[2]]; best=[]
for sty in ['Regular','Medium','Semibold','Bold']:
 for size in range(80,111):
  font=ImageFont.truetype('/workspace/imessage-recreations/shared/fonts/SF-Pro-Display-'+sty+'.otf',size); bb=font.getbbox('Introducing'); out=Image.new('L',(bb[2]-bb[0],bb[3]-bb[1]));ImageDraw.Draw(out).text((-bb[0],-bb[1]),'Introducing',font=font,fill=255)
  out=out.resize((target.shape[1],target.shape[0]),Image.Resampling.LANCZOS); b=np.array(out)/255.;err=np.mean((target-b)**2);best.append((err,sty,size,bb))
best.sort();print('target',box,'best',best[:15])
Path('/workspace/imessage-recreations/references/01-photonhq/font-fit.json').write_text(json.dumps({'target_bbox':box,'results':best[:15]},indent=2,default=int))
