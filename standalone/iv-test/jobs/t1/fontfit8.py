from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

src = np.array(Image.open("all/135.png").convert("RGB")).astype(int)
sub = src[360:421,60:311]

CANDS = []
def add(name, fp, index=0, style=None):
    CANDS.append((name,fp,index))
for i in range(6): add(f"Helv[{i}]","/System/Library/Fonts/Helvetica.ttc",i)
for i in range(8): add(f"HelvNeue[{i}]","/System/Library/Fonts/HelveticaNeue.ttc",i)
add("Arial","/System/Library/Fonts/Supplemental/Arial.ttf")
add("ArialBold","/System/Library/Fonts/Supplemental/Arial Bold.ttf")
add("SFText","/Library/Fonts/SF-Pro-Text-Regular.otf")
add("SFTextMed","/Library/Fonts/SF-Pro-Text-Medium.otf")
add("SFCompText","/Library/Fonts/SF-Compact-Text-Regular.otf")
add("SFCompTextMed","/Library/Fonts/SF-Compact-Text-Medium.otf")
add("Lucida","/System/Library/Fonts/LucidaGrande.ttc")

res=[]
for name,fp,idx in CANDS:
    if not os.path.exists(fp): continue
    for size in (25,26,27):
        try: f=ImageFont.truetype(fp,size,index=idx)
        except Exception: continue
        scr=ImageDraw.Draw(Image.new("L",(1,1)))
        bb=scr.textbbox((0,0),"doors at 7",font=f,anchor='la')
        for dy in range(-2,3):
            for dx in range(-3,4):
                img=Image.new("RGB",(sub.shape[1],sub.shape[0]),(231,231,233))
                d=ImageDraw.Draw(img)
                d.text((68-bb[0]+dx,17-bb[1]+dy),"doors at 7",font=f,anchor='la',fill=(0,0,0))
                mae=float(np.abs(np.array(img).astype(int)-sub).mean())
                res.append((round(mae,2),name,size,dx,dy))
res.sort()
for r in res[:15]: print(r)
