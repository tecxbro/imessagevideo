from PIL import Image, ImageDraw, ImageFont
import numpy as np

src = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)
REG = (115, 368, 250, 404)
sub = src[REG[1]:REG[3], REG[0]:REG[2]]
sdark = np.all(sub<150,axis=2)

# connected-letter column profile of source ink
colprof = sdark.sum(axis=0)
runs=[]; cur=None
for x,v in enumerate(colprof):
    if v>0 and cur is None: cur=x
    if v==0 and cur is not None: runs.append((cur,x-1)); cur=None
if cur is not None: runs.append((cur,len(colprof)-1))
print("src letter runs:", runs)

def runs_for(font, size, track=0.0):
    f=ImageFont.truetype(font,size)
    img=Image.new("L",(140,40),0); d=ImageDraw.Draw(img)
    bb=d.textbbox((0,0),"doors at 7",font=f,anchor='la')
    x=13-bb[0]-1
    if track:
        cx=0
        for ch in "doors at 7":
            d.text((x+cx,9-bb[1]),ch,font=f,anchor='la',fill=255)
            cx+=d.textlength(ch,font=f)+track
    else:
        d.text((x,9-bb[1]),"doors at 7",font=f,anchor='la',fill=255)
    a=np.array(img)>128
    cp=a.sum(axis=0); rr=[];cur=None
    for i,v in enumerate(cp):
        if v>0 and cur is None:cur=i
        if v==0 and cur is not None:rr.append((cur,i-1));cur=None
    if cur is not None:rr.append((cur,len(cp)-1))
    return rr, a

for nm,fp in [("Arial","/System/Library/Fonts/Supplemental/Arial.ttf"),("Helvetica","/System/Library/Fonts/Helvetica.ttc")]:
    rr,_=runs_for(fp,26)
    print(nm,"runs:",rr)

# per-letter MAE for Helvetica 26 dx-1
f=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",26)
img=Image.new("RGB",(sub.shape[1],sub.shape[0]),(231,231,233)); d=ImageDraw.Draw(img)
bb=d.textbbox((0,0),"doors at 7",font=f,anchor='la')
d.text((13-bb[0]-1,9-bb[1]),"doors at 7",font=f,anchor='la',fill=(0,0,0))
arr=np.array(img).astype(int)
diff=np.abs(arr-sub)
for i,(a,b) in enumerate(runs):
    seg=diff[:,a:b+1]
    print(f"src letter {i} cols {a}-{b}: segMAE={seg.mean():.2f}")
