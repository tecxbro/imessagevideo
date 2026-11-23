from PIL import Image, ImageDraw, ImageFont
import numpy as np

f26 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
scr = ImageDraw.Draw(Image.new("L",(1,1)))
for s in ["train gets in at 6","see you there","Sam"]:
    bb = scr.textbbox((0,0), s, font=f26, anchor='la')
    print("Helv26", s, "bb", bb, "w", bb[2]-bb[0], "h", bb[3]-bb[1], "len", scr.textlength(s,font=f26))
# targets: train w181 h22 ; see w156 h24 ; Sam w44 h16 (x458-502 y77-93)
for size in (14,15,16,17,18,19,20):
    f=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",size)
    bb=scr.textbbox((0,0),"Sam",font=f,anchor='la')
    print("Sam size",size,"bb",bb,"w",bb[2]-bb[0],"h",bb[3]-bb[1],"len",round(scr.textlength("Sam",font=f),1))
