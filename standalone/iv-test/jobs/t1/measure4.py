from PIL import Image
import numpy as np

im = np.array(Image.open("frames/f02.png").convert("RGB")).astype(int)

def px(x,y): return tuple(im[y,x])

# sample specific points
print("bg:", px(30,400), px(500,400))
print("nav avatar center:", px(480,44), "edge:", px(460,44))
print("chevron:", px(44,64), px(42,66))
print("divider y126:", px(500,126), px(500,127), px(500,128), "above:", px(500,125), "below:", px(500,129))
print("sam text:", px(480,85))
print("grey bubble see-you:", px(100,300), px(185,300), px(60,300), px(310,300))
print("text inside grey:", )
# find dark text pixels inside grey bubble region y270-331 x60-311
sub = im[270:331, 60:311]
dark = np.all(sub < 150, axis=2)
ys,xs = np.where(dark)
if len(ys): print("  dark-in-grey1 bbox rel:", xs.min(), ys.min(), xs.max()+1, ys.max()+1, "abs x",60+xs.min(),60+xs.max()+1,"y",270+ys.min(),270+ys.max()+1, "color", tuple(sub[ys[0],xs[0]]))
# blue bubble region y180-260 x600-960
sub2 = im[150:260, 550:960]
blue = (np.abs(sub2 - np.array([8,131,252])).sum(axis=2) < 60)
ys,xs = np.where(blue)
print("blue bubble bbox:", 550+xs.min(), 150+ys.min(), 550+xs.max()+1, 150+ys.max()+1)
# white text inside blue
white = np.all(sub2 > 240, axis=2)
# within blue bbox only
bx0,by0,bx1,by1 = 550+xs.min(), 150+ys.min(), 550+xs.max()+1, 150+ys.max()+1
sub3 = im[by0:by1, bx0:bx1]
whitetxt = np.all(sub3 > 235, axis=2)
ys,xs = np.where(whitetxt)
print("  white text in blue rel:", xs.min(), ys.min(), xs.max()+1, ys.max()+1, "abs:", bx0+xs.min(), by0+ys.min(), bx0+xs.max()+1, by0+ys.max()+1)
print("blue color:", px(bx0+10, (by0+by1)//2))
# grey bubble exact
grey = (np.abs(im - np.array([231,231,233])).sum(axis=2) < 30)
sub4 = grey[270:331]
ys,xs = np.where(sub4)
print("grey1 bbox: x", xs.min(), xs.max()+1, "y 270-", 270+ys.max()+1)
# radius check: row widths at top of bubble
for dy in [0,1,2,3,5,8,12,16,20,30,60]:
    row = np.where(grey[270+dy, 40:400])[0]
    if len(row): print(f"  grey1 row y={270+dy}: x {40+row.min()}-{40+row.max()} w={40+row.max()-(40+row.min())+1}")
# vertical extent left edge
col = np.where(grey[270:340, 60])[0]
print("  grey1 col x=60: y", 270+col.min(), "-", 270+col.max())
