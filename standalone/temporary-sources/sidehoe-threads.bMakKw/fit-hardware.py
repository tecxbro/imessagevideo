from pathlib import Path
from PIL import Image
import numpy as np,json,sys
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
d=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
p=root/'project/scene.json'
scene=json.loads(p.read_text());s=scene['threadRegistration']
m=json.loads((root/'measurements.json').read_text())
for name,reg in s.items():
 for f,row in list(reg.items()):
  n=int(f)
  if n==694:
   del reg[f]
   continue
  q=np.asarray(Image.open(d/f'{n:06}.png').convert('RGB'))
  src,old=m[f]
  strip=np.median(q[200:610],axis=(0,2))
  lanes=[]
  for axis in (0,1):
   pos=src['rails'][axis][0]
   if len(pos)!=2:continue
   old_start,old_end=old['rails'][axis][0] or pos
   start=min(pos[0]-4,old_start-1)
   end=max(pos[1]+3,old_end+1)
   if not 0<=start<end<1000:continue
   x=np.linspace(start,end,15)
   gray=np.interp(x,np.arange(1000),strip)
   physical=np.rint(gray).astype(int).tolist()
   lanes.append([start,end,physical])
  row['edgeRamps']=lanes
  if name=='sofia':
   r,g,b=np.moveaxis(q[:78].astype('int16'),2,0)
   k=(r<138)&(g>143)&(b>207)
   k[:,:max(0,row['rails'][0]+12)]=False
   k[:,row['rails'][1]-6:]=False
   points=np.argwhere(k)
   if len(points)>100:
    top,lo=points.min(axis=0)
    bottom,hi=points.max(axis=0)+1
    if top==0:
     top=round(bottom-src['est'][2]*34.2)
    row['blue']=[int(lo),int(top),int(hi),int(bottom)]
  elif row['no']:
   lx,ty,rx,by=row['no']
   nominal=round(src['est'][2]*29.1)
   row['no']=[lx,ty,min(rx,lx+round(src['est'][2]*73)),ty+max(nominal-2,min(nominal+1,by-ty))]
p.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
