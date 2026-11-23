from PIL import Image
import numpy as np
im = np.array(Image.open("frames/f02.png").convert("RGB")).astype(int)
im149 = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)

# text inside blue: white pixels strictly inside interior region x570-890 y190-230
interior = im[195:228, 575:885]
white = np.all(interior > 235, axis=2)
ys,xs = np.where(white)
print("white text blue interior abs:", 575+xs.min(), 195+ys.min(), 575+xs.max()+1, 195+ys.max()+1)
# row profile of text
for y in range(195,228):
    n = white[y-195].sum()
    if n: print("   y",y,"x",575+np.where(white[y-195])[0].min(),"-",575+np.where(white[y-195])[0].max(),"n",n)
