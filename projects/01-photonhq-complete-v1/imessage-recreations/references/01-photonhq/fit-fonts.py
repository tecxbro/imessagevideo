from PIL import Image,ImageFont,ImageDraw
import numpy as np,glob,json
from pathlib import Path
im=Image.open('/workspace/imessage-recreations/references/01-photonhq/keyframes/00.50.png').convert('RGB');a=np.array(im);mask=(255-a[:,:,0])/255.;mask[:,970:]=0;mask[:,:490]=0;ys,xs=np.where(mask>.3);box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1);target=mask[box[1]:box[3],box[0]:box[2]]; best=[]
fonts=glob.glob('/usr/share/fonts/truetype/liberation/*Sans*ttf')+glob.glob('/usr/share/fonts/opentype/urw-base35/NimbusSans-*otf')+glob.glob('/usr/share/fonts/openai-sans/OpenAISans-*.woff2')+glob.glob('/workspace/imessage-recreations/shared/fonts/SF-Pro-Display-*.otf')+glob.glob('/workspace/imessage-recreations/references/01-photonhq/assets/Inter-*.ttf')
fonts=[p for p in fonts if not any(x in p for x in ['Italic','Oblique','variable'])]
for fp in fonts:
 for size in range(82,103):
  try:font=ImageFont.truetype(fp,size)
  except:continue
  bb=font.getbbox('Introducing');out=Image.new('L',(bb[2]-bb[0]+2,bb[3]-bb[1]+2));ImageDraw.Draw(out).text((-bb[0],-bb[1]),'Introducing',font=font,fill=255);aa=np.array(out);yy,xx=np.where(aa>64);out=out.crop((xx.min(),yy.min(),xx.max()+1,yy.max()+1));out=out.resize((target.shape[1],target.shape[0]),Image.Resampling.LANCZOS); b=np.array(out)/255.;best.append((float(np.mean((target-b)**2)),fp,size,bb))
best.sort();print(best[:20]);Path('/workspace/imessage-recreations/references/01-photonhq/font-fit-all.json').write_text(json.dumps({'target_bbox':list(map(int,box)),'results':best[:30]},indent=2))
