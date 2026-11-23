from PIL import Image
import numpy as np
im = np.array(Image.open("frames/f02.png").convert("RGB")).astype(int)
# grey bubble left edge at y=300: x56-66
for x in range(56,67): print("x",x, tuple(im[300,x]))
print("top edge y=270..278 at x=200:")
for y in range(268,279): print("y",y, tuple(im[y,200]))
print("blue bubble left edge y=210 x556-566:")
for x in range(556,567): print("x",x, tuple(im[210,x]))
print("text edge: doors 'd' left x~128 y~382 (f29)")
im2 = np.array(Image.open("frames/f29.png").convert("RGB")).astype(int)
for x in range(124,134): print("x",x, tuple(im2[382,x]))
