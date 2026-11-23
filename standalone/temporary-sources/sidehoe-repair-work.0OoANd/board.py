from pathlib import Path
from PIL import Image,ImageDraw
import sys
work=Path('/tmp/sidehoe-repair-work.0OoANd')
cache=work/sys.argv[1]
frames=[int(num) for num in sys.argv[3:]]
cols=3
size=230
im=Image.new('RGB',(cols*2*size,((len(frames)+cols-1)//cols)*(size+20)),'#efefef')
d=ImageDraw.Draw(im)
for i,f in enumerate(frames):
 x=(i%cols)*size*2;y=(i//cols)*(size+20)
 for j,folder in enumerate((Path('/tmp/sidehoe-fidelity.ESHOT4/source'),cache)):
  a=Image.open(folder/f'{f:06d}.png').convert('RGB').resize((size,size),Image.Resampling.LANCZOS)
  im.paste(a,(x+j*size,y+20))
  d.text((x+j*size+5,y+4),f"{f} {'original' if j==0 else 'candidate'}",fill='#151515')
im.save(work/sys.argv[2],quality=91)
