from PIL import Image, ImageDraw
import numpy as np
src=np.array(Image.open("frames/f01.png").convert("RGB")).astype(int)
sub=src[55:82,35:60]
res=[]
for w in (9,10,11,12):
  for h in (3,3.5,4):
    for rot in (49,50,51,52):
      for xy in ((43,67),(42.5,67),(43,66.75),(42,67)):
        img=Image.new("RGB",(25,27),(253,253,253))
        d=ImageDraw.Draw(img)
        for sgn in (-1,1):
            # rect at x,y with rotation about origin(0,h/2)
            x,y=xy;ox,oy=0,h/2
            a=np.radians(rot*sgn);c,s=np.cos(a),np.sin(a)
            # transform points: p -> (x+ox + c*(px-ox) - s*(py-oy), y+oy + s*(px-ox)+ c*(py-oy))
            def T(px,py): return (35+x+ox+c*(px-ox)-s*(py-oy)-35, 55+y+oy+s*(px-ox)+c*(py-oy)-55)
            # draw as polygon (PIL has no rotated rect) — approximate with 4 corners
            pts=[T(0,0),T(w,0),T(w,h),T(0,h)]
            d.polygon([(px-35,py-55) for px,py in pts],fill=(4,131,255))
            # round the tip and vertex with circles
            r=h/2
            for cx,cy in [T(0,h/2),T(w,h/2)]:
                d.ellipse((cx-35-r,cy-55-r,cx-35+r,cy-55+r),fill=(4,131,255))
        mae=float(np.abs(np.array(img).astype(int)-sub).mean())
        res.append((round(mae,2),w,h,rot,xy))
res.sort()
for r in res[:12]: print(r)
