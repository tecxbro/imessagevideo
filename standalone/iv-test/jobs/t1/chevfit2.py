from PIL import Image, ImageDraw, ImageFont
import numpy as np
src=np.array(Image.open("frames/f01.png").convert("RGB")).astype(int)
sub=src[50:90,30:65]
res=[]
for ch in ['‹','❮']:
  for fp in ["/System/Library/Fonts/Helvetica.ttc","/System/Library/Fonts/HelveticaNeue.ttc"]:
    for size in range(30,60):
        f=ImageFont.truetype(fp,size)
        img=Image.new("RGB",(sub.shape[1],sub.shape[0]),(253,253,253))
        d=ImageDraw.Draw(img);bb=d.textbbox((0,0),ch,font=f,anchor='la')
        # source ink at (42,60)-(50,78) global → rel (12,10)-(20,28)
        d.text((12-bb[0],10-bb[1]),ch,font=f,anchor='la',fill=(4,131,255))
        mae=float(np.abs(np.array(img).astype(int)-sub).mean())
        res.append((round(mae,2),fp.split('/')[-1],repr(ch),size))
res.sort()
for r in res[:10]: print(r)
