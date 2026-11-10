from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json
r=Path('/workspace/imessage-recreations');d=r/'references/05-linq'
items=[('008.20',(549,425,643,519),'white-pawn-transparent',(23,18,73,82)),('008.20',(472,265,566,365),'black-pawn-transparent',(23,7,74,79)),('029.00',(455,128,527,202),'black-queen-transparent',(7,5,66,70))]
for t,b,name,roi in items:
 im=Image.open(d/f'keyframes/{t}.png').convert('RGBA').crop(b);m=Image.new('L',im.size);p=im.load();q=m.load()
 for y in range(im.height):
  for x in range(im.width):
   rr,gg,bb,_=p[x,y];q[x,y]=255 if roi[0]<=x<roi[2] and roi[1]<=y<roi[3] and min(rr,gg,bb)>170 and max(rr,gg,bb)-min(rr,gg,bb)<55 else 0
 m=m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3));ImageDraw.floodfill(m,(0,0),128,thresh=0);q=m.load()
 for y in range(im.height):
  for x in range(im.width):q[x,y]=0 if q[x,y]==128 else 255
 im.putalpha(m.filter(ImageFilter.GaussianBlur(.2)));im.save(d/f'assets/{name}.png')
s=json.loads((d/'scene.json').read_text());s['source']['notes']+=' Finalv8 restricts sprite extraction to bright neutral outlines inside measured piece ROIs, removing neutral wood false positives.';(d/'scene.json').write_text(json.dumps(s,indent=2))
