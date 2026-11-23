from PIL import Image, ImageDraw, ImageFont
import numpy as np
FP = "/System/Library/Fonts/Supplemental/Arial.ttf"
for size in range(20, 34):
    f = ImageFont.truetype(FP, size)
    scr = ImageDraw.Draw(Image.new("L",(1,1)))
    w = scr.textlength("doors at 7", font=f)
    bb = scr.textbbox((0,0), "doors at 7", font=f, anchor='la')
    w2 = scr.textlength("see you there", font=f)
    bb2 = scr.textbbox((0,0), "see you there", font=f, anchor='la')
    w3 = scr.textlength("train gets in at 6", font=f)
    bb3 = scr.textbbox((0,0), "train gets in at 6", font=f, anchor='la')
    print(f"size={size} doors: textlen={w:.1f} bbox={bb} w={bb[2]-bb[0]} h={bb[3]-bb[1]} | see: len={w2:.1f} bboxh={bb2[3]-bb2[1]} | train: len={w3:.1f} h={bb3[3]-bb3[1]}")
print("targets: doors bbox w114 h19 | see w156 h24 | train w181 h22")
