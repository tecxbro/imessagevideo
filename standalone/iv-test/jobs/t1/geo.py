from PIL import Image
import numpy as np
im = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)  # f149
g = (np.abs(im - np.array([231,231,233])).sum(axis=2) < 60)
# doors bubble row widths near top/bottom
for dy in [0,1,2,3,5,8,12,20,30,60]:
    row = np.where(g[360+dy, 40:400])[0]
    if len(row): print(f"doors row y={360+dy}: x {40+row.min()}-{40+row.max()} w={row.max()-row.min()+1}")
for dy in [-1,-2,-3,-5]:
    row = np.where(g[420+dy+1, 40:400])[0]
    if len(row): print(f"doors row y={420+dy+1}: x {40+row.min()}-{40+row.max()} w={row.max()-row.min()+1}")
# divider rows
print("divider y126:", tuple(im[126,500]), "y125:", tuple(im[125,500]), "y129:", tuple(im[129,500]))
for y in [125,126,127,128,129]: print(y, tuple(im[y,480]))
# avatar edge profile: circle x456-504 y20-68. center?
a = (np.abs(im[0:130] - np.array([208,208,211])).sum(axis=2) < 40)
ys,xs=np.where(a)
print("avatar bbox:", xs.min(),ys.min(),xs.max()+1,ys.max()+1)
# sam: exact color profile
s = src_col = im[75:96,455:505]
uniq,cnt = np.unique(s.reshape(-1,3),axis=0,return_counts=True)
o=np.argsort(-cnt)[:8]
for i in o: print("sam color", tuple(uniq[i]), cnt[i])
