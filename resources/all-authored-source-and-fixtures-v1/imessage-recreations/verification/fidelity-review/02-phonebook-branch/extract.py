from pathlib import Path
import subprocess, numpy as np,json
from PIL import Image,ImageDraw
from scipy import ndimage
root=Path('/workspace/imessage-recreations');ref=root/'references/02-danieltian';out=root/'verification/fidelity-review/02-phonebook-branch'
def extract(first,last,box,label):
 x,y,w,h=box
 cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(ref/'source.mp4'),'-vf',f'select=between(n\\,{first}\\,{last}),crop={w}:{h}:{x}:{y}','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-']
 data=subprocess.check_output(cmd);a=np.frombuffer(data,np.uint8).reshape(-1,h,w,3)
 print(label,len(a));np.save(out/(label+'.npy'),a)
 for i in range(len(a)):
  Image.fromarray(a[i]).save(out/f'{label}-{first+i}.png')
 return a
q=extract(390,418,[300,430,1300,230],'query')
u=extract(460,506,[1160,150,680,230],'uber')
ms=[]
for i,a in enumerate(q):
 g=a.mean(2); ink=253-g
 # glyphs have maximum contrast, inside central 100px band. threshold relative to each frame's peak.
 sub=ink[65:150];peak=np.percentile(sub[sub>3],98) if (sub>3).any() else 1
 m=np.zeros(g.shape,bool);m[65:150]=(sub>max(12,peak*.45));lab,n=ndimage.label(m);found=[]
 for sl in ndimage.find_objects(lab):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if h>9 and w>5:found.append((xx.start,yy.start,xx.stop,yy.stop))
 bb=[min(b[0] for b in found)+300,min(b[1] for b in found)+430,max(b[2] for b in found)+300,max(b[3] for b in found)+430] if found else None
 # Ring connected component; clip away icon/text darkness.
 lab,n=ndimage.label((g>180)&(g<252));rings=[]
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w>400 and 80<h<180:rings.append([xx.start+300,yy.start+430,w,h])
 ms.append(dict(frame=390+i,text_box=bb,peak=float(peak),rings=rings))
(out/'query-dense.json').write_text(json.dumps(ms,indent=2));print(json.dumps(ms,indent=1))
