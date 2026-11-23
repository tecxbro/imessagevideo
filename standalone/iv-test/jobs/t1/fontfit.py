from PIL import Image, ImageDraw, ImageFont
import numpy as np

src = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)  # frame149 settled
# region around doors text: global x120-250 y370-400
REG = (115, 368, 250, 404)
sub = src[REG[1]:REG[3], REG[0]:REG[2]]

FONTS = {
 "Arial": "/System/Library/Fonts/Supplemental/Arial.ttf",
 "SFProText-Regular": "/Library/Fonts/SF-Pro-Text-Regular.otf",
 "SFProText-Medium": "/Library/Fonts/SF-Pro-Text-Medium.otf",
 "Helvetica": "/System/Library/Fonts/Helvetica.ttc",
}
import os
for name, fp in FONTS.items():
    if not os.path.exists(fp): print(name, "MISSING"); continue
    for size in (24,25,26,27):
        for fill in [(0,0,0),(17,17,17),(26,26,30),(32,32,37),(34,34,37)]:
            f = ImageFont.truetype(fp, size)
            img = Image.new("RGB",(sub.shape[1], sub.shape[0]), (231,231,233))
            d = ImageDraw.Draw(img)
            # ink target x68-182 rel bubble → global 128 → rel REG x = 13 ; ink y17 → global 377 → rel 9
            # draw text at anchor 'la' at layer pos: ink top = y + bbox.y0
            bb = d.textbbox((0,0), "doors at 7", font=f, anchor='la')
            # want ink x0=13, y0=9
            d.text((13-bb[0], 9-bb[1]), "doors at 7", font=f, anchor='la', fill=fill)
            arr = np.array(img).astype(int)
            mae = np.abs(arr - sub).mean()
            print(f"{name} s{size} fill{fill}: MAE={mae:.3f} inkbb={bb}")
