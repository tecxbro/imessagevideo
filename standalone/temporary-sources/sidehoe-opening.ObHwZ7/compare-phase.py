from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import sys,json
p=Path(__file__).parent
prior=Path('/tmp/sidehoe-lens.scMdVq/clean-frames')
first=p/'probe-a'
ref=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
start,stop=int(sys.argv[1]),int(sys.argv[2])
test=p/sys.argv[3]
values={}
for f in range(start,stop+1):
 pictures=[np.array(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16) for base in (ref,prior,first,test)]
 vals=[round(float(np.abs(pictures[0]-a).mean()),5) for a in pictures[1:]]
 print(f,*vals)
 values[f]=vals
(p/(sys.argv[3]+'-metrics.json')).write_text(json.dumps(values,indent=2)+'\n')
frames=((0,2,5,9) if stop<20 else (319,322,325,328))
out=Image.new('RGB',(1080,813),'white');d=ImageDraw.Draw(out)
for i,f in enumerate(frames):
 for j,o in enumerate((ref,first,test)):
  im=Image.open(o/f'{f:06}.png').convert('RGB')
  im.thumbnail((265,245),Image.Resampling.LANCZOS)
  x=i*270;y=j*271
  out.paste(im,(x,y+18));d.text((x+4,y+1),f'{f} {("source","first probe","latest probe")[j]}',fill='black')
out.save(p/(sys.argv[3]+'.jpg'),quality=93)
