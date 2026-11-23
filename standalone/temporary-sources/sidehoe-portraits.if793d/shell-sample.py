from pathlib import Path
from PIL import Image
from scipy.ndimage import label,binary_closing,binary_fill_holes,distance_transform_edt
import numpy as np,sys,json
p=Path(__file__).parent;src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
state=json.loads((p/'project/scene.json').read_text())
def contour(q):
 rgb=np.array(q,dtype=np.int16)
 R,G,B=np.moveaxis(rgb,2,0)
 purple=(G<247)&(R<249)&(B>237)&(B>G+6)
 vivid=np.max(253-rgb,axis=2)>23
 hull=binary_closing(purple|vivid,iterations=4)
 names,n=label(hull)
 counts=np.bincount(names.ravel())
 components=np.argsort(counts[1:])[::-1]+1
 return [binary_fill_holes(names==k) for k in components if counts[k]>900]
for f in (218,219,221,226,227,235,246,253):
 a=np.asarray(Image.open(src/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 R,G,B=np.moveaxis(a,2,0)
 parts=contour(a); print(f,'components',list(map(np.sum,parts)))
 field=np.maximum.reduce([distance_transform_edt(m) for m in parts])
 slot=(field>0)&(R>=233)&(G>=221)&(B>=244)&(B>=G)
 for r in ((0,3),(3,8),(8,14),(14,22),(22,33),(33,47),(47,70),(70,95),(95,150),(150,250)):
  n=slot&(field>r[0])&(field<=r[1])
  print(r,np.median(a[n],axis=0).astype(int).tolist() if n.sum() else [],n.sum(),end=' ')
 print()
