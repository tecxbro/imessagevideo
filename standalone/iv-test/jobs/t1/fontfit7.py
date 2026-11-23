from PIL import Image, ImageDraw, ImageFont
import numpy as np

src = np.array(Image.open("frames/f02.png").convert("RGB")).astype(int)

def fit(reg, text, sizes, bg, fill, fonts):
    sub = src[reg[1]:reg[3], reg[0]:reg[2]]
    # find ink bbox in source
    if fill == 'white':
        ink = np.all(sub>240,axis=2)
    else:
        ink = np.all(sub<150,axis=2)
    if not ink.any(): print("no ink", text); return
    ys,xs=np.where(ink); print(f"=== {text} ink rel x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}")
    res=[]
    for fname,fp in fonts.items():
        for size in sizes:
            f=ImageFont.truetype(fp,size)
            scr=ImageDraw.Draw(Image.new("L",(1,1)))
            bb=scr.textbbox((0,0),text,font=f,anchor='la')
            for dy in range(-3,4):
                for dx in range(-3,4):
                    img=Image.new("RGB",(sub.shape[1],sub.shape[0]),bg)
                    d=ImageDraw.Draw(img)
                    fc = (255,255,255) if fill=='white' else (0,0,0)
                    d.text((xs.min()-bb[0]+dx, ys.min()-bb[1]+dy), text, font=f, anchor='la', fill=fc)
                    mae=float(np.abs(np.array(img).astype(int)-sub).mean())
                    res.append((round(mae,2),fname,size,dx,dy))
    res.sort()
    for r in res[:6]: print("   ",r)

F={"Helv":"/System/Library/Fonts/Helvetica.ttc","Arial":"/System/Library/Fonts/Supplemental/Arial.ttf"}
fit((440,68,520,100), "Sam", range(14,24), (253,253,253), 'dark', F)
fit((620,188,840,230), "train gets in at 6", (24,25,26,27), (8,131,252), 'white', F)
fit((70,278,360,320), "see you there", (24,25,26,27), (231,231,233), 'dark', F)
