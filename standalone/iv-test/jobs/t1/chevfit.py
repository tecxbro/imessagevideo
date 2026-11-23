from PIL import Image, ImageDraw, ImageFont
import numpy as np

src = np.array(Image.open("frames/f02.png").convert("RGB")).astype(int)
sub = src[50:90, 30:65]
# blue mask
blue = (np.abs(sub - np.array([4,131,255])).sum(axis=2) < 200) & (sub[:,:,2]>150)
ys,xs=np.where(blue)
print("chevron ink rel:",xs.min(),ys.min(),xs.max(),ys.max())
# try text chevrons
res=[]
for ch in ['‹','❮','<','〈']:
    for size in range(24,44):
        f=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",size)
        img=Image.new("RGB",(sub.shape[1],sub.shape[0]),(253,253,253))
        d=ImageDraw.Draw(img)
        bb=d.textbbox((0,0),ch,font=f,anchor='la')
        for dy in range(-4,5):
            for dx in range(-4,5):
                i2=img.copy();d2=ImageDraw.Draw(i2)
                d2.text((xs.min()-bb[0]+dx,ys.min()-bb[1]+dy),ch,font=f,anchor='la',fill=(4,131,255))
                mae=float(np.abs(np.array(i2).astype(int)-sub).mean())
                res.append((round(mae,2),repr(ch),size,dx,dy))
res.sort()
for r in res[:8]: print(r)
# Sam fill check: darkest px median
sam = src[77:93,458:502]
dark = sam[np.all(sam<100,axis=2)]
print("sam dark px median:", np.median(dark,axis=0), "min:", dark.min(axis=0))
# chevron dominant color
ch = src[59:79,40:51]
cm = (np.abs(ch-np.array([4,131,255])).sum(axis=2)<150)&(ch[:,:,2]>150)
print("chev colors uniq:", np.unique(ch[cm].reshape(-1,3),axis=0)[:10])
