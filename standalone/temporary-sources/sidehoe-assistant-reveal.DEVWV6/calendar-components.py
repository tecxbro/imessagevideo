from pathlib import Path
from PIL import Image
import numpy as np,sys
p=Path(sys.argv[1]); d=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def runs(mask,min_width=3,offset=0):
    s=np.flatnonzero(mask)
    out=[]
    for a in np.split(s,np.flatnonzero(np.diff(s)>1)+1):
        if len(a)>=min_width:out.append((int(a[0])+offset,int(a[-1])+offset))
    return out
for f in range(473,479):
 print('\nframe',f)
 for loc in [d,p/'prior-full']:
  im=np.asarray(Image.open(loc/f'{f:06}.png').convert('RGB'),dtype=np.int16)
  red,green,blue=im.transpose(2,0,1)
  m1=(blue-green>19)&(blue-red>18)&(red>147)&(green<234)
  m2=(green-red>17)&(blue-red>26)&(red>154)&(green>206)
  print('source' if loc==d else 'candidate')
  for color,label in [(m1,'lavender'),(m2,'blue')]:
    rows=runs(color[260:650,150:950].sum(1)>45,4,260)
    print(label,'rows',rows)
    prev=[]
    for y in range(343,640,4):
       seg=runs(color[y,133:945],18,133)
       if seg!=prev and seg:
        print(y,seg)
       prev=seg
  gray=np.max(im,axis=2)-np.min(im,axis=2)<10
  levels=(red<246)&gray
  y,x=np.where((red[:290]>180)&(green[:290]<115)&(blue[:290]<160))
  print('marker',[(int(x.min()),int(y.min()),int(x.max()),int(y.max()))] if len(x) else [])
  for y0 in (265,368,470,572,674,776,879,981):
     if y0<1000:
        i=np.argmax(levels[max(0,y0-12):min(1000,y0+13),150:945].sum(axis=1))
        y=y0-12+i
        n=runs(levels[y,150:945],15,150)
        print('grid',y,n)
