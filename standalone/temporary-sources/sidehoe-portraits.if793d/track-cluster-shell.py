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
 hull=binary_closing(np.pad(purple|vivid,5,mode="edge"),iterations=4)[5:-5,5:-5]
 names,n=label(hull)
 counts=np.bincount(names.ravel())
 components=np.argsort(counts[1:])[::-1]+1
 return [binary_fill_holes(names==k) for k in components if counts[k]>900]

def trace(mask):
 above=np.zeros_like(mask);above[1:]=mask[:-1]
 below=np.zeros_like(mask);below[:-1]=mask[1:]
 left=np.zeros_like(mask);left[:,1:]=mask[:,:-1]
 right=np.zeros_like(mask);right[:,:-1]=mask[:,1:]
 corridors={}
 for near, a,b in ((above,(0,0),(1,0)),(right,(1,0),(1,1)),(below,(1,1),(0,1)),(left,(0,1),(0,0))):
   for y,x in np.argwhere(mask&~near):
      start,end=(int(x+a[0]),int(y+a[1])),(int(x+b[0]),int(y+b[1]))
      corridors.setdefault(start,[]).append(end)
 sequences=[]
 while corridors:
   origin=next(iter(corridors))
   point=origin
   walk=[]
   while point in corridors:
      walk.append(point)
      next_point=corridors[point].pop()
      if not corridors[point]:del corridors[point]
      point=next_point
      if point==origin:break
   if len(walk)>12:sequences.append(walk)
 return max(sequences,key=len)

def simplify(points,maximum_error=1.4):
 start,end=points[0],points[-1]
 line=end-start
 size=np.dot(line,line)
 if size==0:
    error=np.linalg.norm(points-start,axis=1)
 else:
    along=np.clip(np.einsum('ij,j->i',points-start,line)/size,0,1)
    error=np.linalg.norm(points-(start+along[:,None]*line),axis=1)
 peak=error.argmax()
 if error[peak]<maximum_error:return points[0],points[-1]
 a=simplify(points[:peak+1],maximum_error)
 b=simplify(points[peak:],maximum_error)
 return [*a[:-1],*b]

out={}
for f in range(218,254):
 a=np.asarray(Image.open(src/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 parts=contour(a)
 used=np.zeros(a.shape[:2],dtype=bool); res=[]
 for mask in parts:
    if ((mask&used).sum()/mask.sum())>.25:continue
    polygon=np.asarray(trace(mask),dtype=int)
    far_idx=np.linalg.norm(polygon-polygon[0],axis=1).argmax()
    left=simplify(polygon[:far_idx+1])
    right=simplify(np.r_[polygon[far_idx:],polygon[:1]])
    vertices=np.array([*left[:-1],*right[:-1]])
    res.append(vertices.tolist())
    used |= mask
 out[str(f)]=res
 if f in (218,219,223,226,241,253):print(f,*[len(pts) for pts in res])
cfg=p/'project/scene.json'
state=json.loads(cfg.read_text())
del state['tracks']['clusterHaloRegistration']
state['clusterShellContours']=out
cfg.write_text(json.dumps(state,indent=2)+'\n')
