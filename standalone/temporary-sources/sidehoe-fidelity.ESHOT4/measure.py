from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).parent
def load(k,f): return np.asarray(Image.open(p/k/f'{f:06d}.png')).astype('int16')
def rgb(a,x,y): return tuple(int(i) for i in np.median(a[y-3:y+4,x-3:x+4].reshape(-1,3),axis=0))
def bounds(mask):
 y,x=np.where(mask)
 return (int(x.min())*4,int(y.min())*4,int(x.max())*4,int(y.max())*4) if len(x)>4 else None
for f in (133,134,135,136,137,138,140,145,154,159,161,168,183,187,196,201,205,209,714,724,732,752,765):
 result=[]
 for k in ('source','baseline'):
  a=load(k,f)
  # use 500-wide source raster. Print dark ink bands above/below the center.
  mask=a.max(2)<145
  bands=[(40,170),(170,215),(215,257),(257,302),(302,353),(353,420)]
  result.append(([(m[0],m[1]+4*y,m[2],m[3]+4*y) if (m:=bounds(mask[y:z])) else None for y,z in bands],
     [rgb(a,x,y) for x,y in [(20,20),(470,150),(460,320),(200,440),(470,470),(380,425)]]))
 print(f,*result)
print('CAL')
for f in (403,405,408,410,412,415,420,427,431,435,442,452,460,470,473):
 a=load('source',f)
 r,g,b=a.transpose(2,0,1)
 day=(r>165)&(r-g>85)&(r-b>65)
 day[:,0:300]=False; day[225:]=False
 y,x=np.nonzero(day)
 row_extent=[]
 for row in range(145,470):
  m=(r[row]<249)&(r[row]>160)&(abs(r[row]-g[row])<10)&(abs(r[row]-b[row])<15)
  m[:75]=False
  cols=np.flatnonzero(m)
  if len(cols)>220:
   row_extent.append((row*4,cols[0]*4,cols[-1]*4))
 print(f,(float(np.median(x)*4),float(np.median(y)*4)) if len(x) else None,row_extent)
