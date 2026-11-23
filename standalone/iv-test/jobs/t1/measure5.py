from PIL import Image
import numpy as np

im = np.array(Image.open("frames/f02.png").convert("RGB")).astype(int)
im149 = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)

# white text inside blue bubble: restrict to pixels whose neighborhood is blue
blue_mask = (np.abs(im - np.array([8,131,252])).sum(axis=2) < 90)
sub3 = im[180:240, 560:900]
white = np.all(sub3 > 200, axis=2)
ys,xs = np.where(white)
print("white text in blue abs:", 560+xs.min(), 180+ys.min(), 560+xs.max()+1, 180+ys.max()+1)

# dark text in grey bubble1
sub = im[270:331, 60:371]
dark = np.all(sub < 150, axis=2)
ys,xs = np.where(dark)
print("dark text grey1 abs:", 60+xs.min(), 270+ys.min(), 60+xs.max()+1, 270+ys.max()+1)

# doors at 7 settled bubble (frame 149): y360-421 x60-311
sub2 = im149[360:421, 60:311]
dark2 = np.all(sub2 < 150, axis=2)
ys,xs = np.where(dark2)
print("dark text doors abs:", 60+xs.min(), 360+ys.min(), 60+xs.max()+1, 360+ys.max()+1)

# sam text color & bbox
sub5 = im[76:94, 455:505]
darkish = np.all(sub5 < 200, axis=2)
ys,xs = np.where(darkish)
print("sam text abs:", 455+xs.min(), 76+ys.min(), 455+xs.max()+1, 76+ys.max()+1, "color:", tuple(sub5[ys[len(ys)//2], xs[len(xs)//2]]))

# chevron: blue pixels in nav zone x0-100 y40-100
chev = (np.abs(im[40:110,0:120] - np.array([8,131,252])).sum(axis=2) < 200)
ys,xs = np.where(chev)
print("chevron abs:", xs.min(), 40+ys.min(), xs.max()+1, 40+ys.max()+1, "colors:", [tuple(im[40+y,x]) for x,y in list(zip(xs,ys))[:5]])

# blue bubble corner profile
bm = blue_mask[180:240, 560:900]
for dy in [0,1,2,4,6,9,14,20,30,59]:
    row = np.where(bm[dy])[0]
    if len(row): print(f"  blue row y={180+dy}: x {560+row.min()}-{560+row.max()} w={row.max()-row.min()+1}")
col = np.where(blue_mask[180:250, 560])[0]
print("  blue col x=560: y", 180+col.min(), 180+col.max())
col2 = np.where(blue_mask[180:250, 899])[0]
print("  blue col x=899: y", 180+col2.min(), 180+col2.max())
# tail? iMessage outgoing bubble has tail bottom-right. Check below y240 near x850-900
tail = blue_mask[240:260, 800:960]
ys,xs=np.where(tail)
print("below-bubble blue:", (800+xs.min(),240+ys.min(),800+xs.max()+1,240+ys.max()+1) if len(ys) else None)
# also check grey bubble tail below y331
gmask = (np.abs(im - np.array([231,231,233])).sum(axis=2) < 60)
t2 = gmask[331:360, 40:400]
ys,xs=np.where(t2)
print("below grey1:", (40+xs.min(),331+ys.min(),40+xs.max()+1,331+ys.max()+1) if len(ys) else None)
t3 = gmask[421:450, 40:340]
ys,xs=np.where(t3)
print("below doors(settled f149):", (40+xs.min(),421+ys.min(),40+xs.max()+1,340 and 40+xs.max()+1,421+ys.max()+1) if len(ys) else None)
