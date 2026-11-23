from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

src = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)
REG = (115, 368, 250, 404)
sub = src[REG[1]:REG[3], REG[0]:REG[2]]

FONTS = {
 "Arial": "/System/Library/Fonts/Supplemental/Arial.ttf",
 "Helvetica": "/System/Library/Fonts/Helvetica.ttc",
 "SFProText": "/Library/Fonts/SF-Pro-Text-Regular.otf",
}
best = []
for name, fp in FONTS.items():
    if not os.path.exists(fp): continue
    for size in (25,26):
        f = ImageFont.truetype(fp, size)
        scr = ImageDraw.Draw(Image.new("L",(1,1)))
        bb = scr.textbbox((0,0), "doors at 7", font=f, anchor='la')
        for dy in range(-3,4):
            for dx in range(-3,4):
                img = Image.new("RGB",(sub.shape[1], sub.shape[0]), (231,231,233))
                d = ImageDraw.Draw(img)
                d.text((13-bb[0]+dx, 9-bb[1]+dy), "doors at 7", font=f, anchor='la', fill=(0,0,0))
                mae = np.abs(np.array(img).astype(int) - sub).mean()
                best.append((mae, name, size, dx, dy))
best.sort()
for b in best[:10]: print(b)
