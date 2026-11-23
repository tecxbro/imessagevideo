from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

src = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)
REG = (115, 368, 250, 404)
sub = src[REG[1]:REG[3], REG[0]:REG[2]]

FONTS = {
 "Arial": "/System/Library/Fonts/Supplemental/Arial.ttf",
 "Helvetica": "/System/Library/Fonts/Helvetica.ttc",
 "HelveticaNeue": "/System/Library/Fonts/HelveticaNeue.ttc",
 "SFCompactText": "/Library/Fonts/SF-Compact-Text-Regular.otf",
 "SFCompact": "/System/Library/Fonts/SFCompact.ttf",
 "Avenir": "/System/Library/Fonts/Avenir.ttc",
 "Geneva": "/System/Library/Fonts/Geneva.ttf",
}
res=[]
for name, fp in FONTS.items():
    if not os.path.exists(fp): continue
    for size in (24,25,26,27):
        try: f = ImageFont.truetype(fp, size)
        except Exception as e: continue
        scr = ImageDraw.Draw(Image.new("L",(1,1)))
        bb = scr.textbbox((0,0), "doors at 7", font=f, anchor='la')
        for dy in range(-2,3):
            for dx in range(-3,4):
                img = Image.new("RGB",(sub.shape[1], sub.shape[0]), (231,231,233))
                d = ImageDraw.Draw(img)
                d.text((13-bb[0]+dx, 9-bb[1]+dy), "doors at 7", font=f, anchor='la', fill=(0,0,0))
                mae = float(np.abs(np.array(img).astype(int) - sub).mean())
                res.append((round(mae,3), name, size, dx, dy))
res.sort()
for r in res[:14]: print(r)
