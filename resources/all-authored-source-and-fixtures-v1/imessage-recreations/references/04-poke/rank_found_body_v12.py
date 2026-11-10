"""Audit a large ink-width correction against both official optical families."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import shift
import numpy as np,json
p=Path(__file__).parent;fonts=p.parent.parent/'shared/fonts';text='found a few solid spots near you';a=np.array(Image.open(p/'measurements-v8/decoded/000674.png').convert('RGB')).mean(2)[459:512,215:1034];target=np.clip((236-a)/236,0,1);h,w=target.shape;out=[];threshold=(236-100)/236
for family in['Text','Display']:
 for style in['Regular','Medium','Semibold','Bold']:
  font=ImageFont.truetype(str(fonts/f'SF-Pro-{family}-{style}.otf'),256);b=font.getbbox(text);im=Image.new('L',(b[2]-b[0]+20,b[3]-b[1]+20));ImageDraw.Draw(im).text((10-b[0],10-b[1]),text,font=font,fill=255);v=np.array(im)/255;yy,xx=np.where(v>=threshold);v=v[yy.min():yy.max()+1,xx.min():xx.max()+1];shape=np.array(Image.fromarray((v*255).astype('uint8')).resize((w,h),Image.Resampling.LANCZOS))/255;best=(1e9,None)
  for dy in[-1,-.5,0,.5,1]:
   for dx in[-1,-.5,0,.5,1]:
    q=shift(shape,(dy,dx),order=1,mode='constant');mask=(q>.08)|(target>.08);error=float(abs(q[mask]-target[mask]).mean())
    if error<best[0]:best=(error,[dx,dy])
  out.append(dict(family=family,style=style,normalized_alpha_mae=best[0],phase=best[1]))
out.sort(key=lambda r:r['normalized_alpha_mae']);(p/'measurements-v8/found-body-font-rank-v12.json').write_text(json.dumps(dict(source_frame=674,text=text,ink_bbox=[215,459,1034,512],background=236,method='Official8faces,256pxPillow, original black-core threshold, exact provided ink normalization and bounded phase; rank is a shape hypothesis pending actual browser proof.',ranking=out),indent=2));print(json.dumps(out,indent=2))
