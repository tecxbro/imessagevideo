from PIL import Image, ImageDraw, ImageFont
import numpy as np
src = np.array(Image.open("all/135.png").convert("RGB")).astype(int)
sub = src[360:421,60:311]

def probe(fp, idx_max=8):
    out=[]
    for i in range(idx_max):
        try:
            f=ImageFont.truetype(fp,26,index=i)
            out.append((i, f.getname()))
        except Exception as e:
            break
    return out
for fp in ["/System/Library/Fonts/Helvetica.ttc","/System/Library/Fonts/HelveticaNeue.ttc","/System/Library/Fonts/ArialHB.ttc"]:
    print(fp, probe(fp))
