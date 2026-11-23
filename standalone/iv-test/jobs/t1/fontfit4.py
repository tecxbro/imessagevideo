from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

src = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)
REG = (115, 368, 250, 404)
sub = src[REG[1]:REG[3], REG[0]:REG[2]]
fp = "/System/Library/Fonts/Helvetica.ttc"
f = ImageFont.truetype(fp, 26)
scr = ImageDraw.Draw(Image.new("L",(1,1)))
bb = scr.textbbox((0,0), "doors at 7", font=f, anchor='la')
for fill in [(0,0,0),(8,8,10),(16,16,16),(20,20,24),(32,32,32),(34,34,37),(48,48,50)]:
    img = Image.new("RGB",(sub.shape[1], sub.shape[0]), (231,231,233))
    d = ImageDraw.Draw(img)
    d.text((13-bb[0]-1, 9-bb[1]), "doors at 7", font=f, anchor='la', fill=fill)
    arr=np.array(img).astype(int)
    diff=np.abs(arr-sub)
    mae=float(diff.mean())
    # count pixels >30
    big=(diff.max(axis=2)>30).sum()
    print("fill",fill,"MAE",round(mae,3),"big-diff-px",big)
# show diff map for fill 0
img = Image.new("RGB",(sub.shape[1], sub.shape[0]), (231,231,233))
d = ImageDraw.Draw(img)
d.text((13-bb[0]-1, 9-bb[1]), "doors at 7", font=f, anchor='la', fill=(0,0,0))
arr=np.array(img).astype(int)
diff=np.abs(arr-sub).max(axis=2)
ys,xs=np.where(diff>40)
print("diff>40 bbox:", xs.min(),ys.min(),xs.max(),ys.max(),"n",len(ys))
# where is ink in source vs render (col profile of dark px)
sdark = np.all(sub<120,axis=2); rdark=np.all(arr<120,axis=2)
print("src ink cols:", np.where(sdark.any(axis=0))[0][[0,-1]], "rows:", np.where(sdark.any(axis=1))[0][[0,-1]])
print("rnd ink cols:", np.where(rdark.any(axis=0))[0][[0,-1]], "rows:", np.where(rdark.any(axis=1))[0][[0,-1]])
# per-column dark count compare for first glyph
for x in range(10,30):
    print(x, int(sdark[:,x].sum()), int(rdark[:,x].sum()), int(diff[:,x].max()))
