from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label, find_objects, binary_closing
D=Path('/tmp/sidehoe-optical.0heyYI')
dirs=[Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage'),D/'confirmed-frames']
def comp(ar,mask,box,sz):
 x0,y0,x1,y1=box
 m=mask(*np.moveaxis(ar[y0:y1,x0:x1].astype('int16'),2,0))
 labels,n=label(binary_closing(m,iterations=1))
 out=[]
 for q,(yy,xx) in enumerate(find_objects(labels),1):
  w,h=xx.stop-xx.start,yy.stop-yy.start
  if w<sz[0] or h<sz[1]:continue
  area=np.count_nonzero(labels[yy,xx]==q)
  selection=ar[y0+yy.start:y0+yy.stop,x0+xx.start:x0+xx.stop][labels[yy,xx]==q]
  out.append((area,(x0+xx.start,y0+yy.start,x0+xx.stop,y0+yy.stop),[int(t) for t in np.median(selection,axis=0)]))
 return [(x,y) for _,x,y in sorted(out,key=lambda a:-a[0])]
gray=lambda r,g,b:(r>208)&(r<241)&(np.abs(b-r)<12)&(np.abs(g-r)<7)
cyan=lambda r,g,b:(r<95)&(g>155)&(b>209)
dark=lambda r,g,b:(r<168)&(g<170)&(b<180)
neg=lambda r,g,b:(r>168)&(r<217)&(np.abs(r-g)<9)&(np.abs(r-b)<15)
active=lambda r,g,b:((r-g)>10)&((b-g)>20)&(b>225)
for f in [340,342,344,346,348,350,352,354,356,358]:
 print('FRAME',f)
 for j,d in enumerate(dirs):
  a=np.asarray(Image.open(d/f'{f:06}.png').convert('RGB'))
  gr=comp(a,gray,(60,35,800,365),(95,29)); cy=comp(a,cyan,(375,280,950,660),(145,28))
  lab=comp(a,dark,(390,440,830,495),(12,6))
  control=comp(a,neg,(590,600,785,695),(48,19))
  send=comp(a,active,(700,597,885,685),(35,14))
  print(j, 'gray',gr,'cyan',cy,'label',lab,'neg',control,'send',send)
