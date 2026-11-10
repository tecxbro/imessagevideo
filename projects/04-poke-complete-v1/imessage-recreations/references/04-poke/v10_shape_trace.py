"""Native contour tracing reused from verified v6 component measurement."""
import numpy as np

def simplify(points,tolerance):
 if len(points)<3:return points
 a,b=points[0],points[-1];d=b-a;length=float(np.dot(d,d))
 if length:dist=np.abs(d[0]*(points[:,1]-a[1])-d[1]*(points[:,0]-a[0]))/length**.5
 else:dist=np.linalg.norm(points-a,axis=1)
 i=int(dist.argmax())
 if dist[i]>tolerance:return np.vstack([simplify(points[:i+1],tolerance)[:-1],simplify(points[i:],tolerance)])
 return points[[0,-1]]

def vector_outline(mask,roi,origin,scale=1):
 # Directed exposed pixel edges form an editable closed contour. Simplify below one
 # native pixel, then use quadratic corner controls to remove pixel stair steps.
 ys,xs=np.where(mask);edges={}
 for x,y in zip(xs,ys):
  if y==0 or not mask[y-1,x]:edges[(int(x),int(y))]=(int(x+1),int(y))
  if x==mask.shape[1]-1 or not mask[y,x+1]:edges[(int(x+1),int(y))]=(int(x+1),int(y+1))
  if y==mask.shape[0]-1 or not mask[y+1,x]:edges[(int(x+1),int(y+1))]=(int(x),int(y+1))
  if x==0 or not mask[y,x-1]:edges[(int(x),int(y+1))]=(int(x),int(y))
 start=min(edges,key=lambda q:(q[1],q[0]));points=[start];v=edges[start]
 while v!=start:
  points.append(v);v=edges[v]
  if len(points)>20000:raise ValueError('Contour did not close')
 points=np.asarray(points,dtype=float);cut=len(points)//2
 pts=np.vstack([simplify(points[:cut+1],.8)[:-1],simplify(np.vstack([points[cut:],points[:1]]),.8)[:-1]])
 pts=(pts+np.array(roi[:2])-np.array(origin))/scale
 mids=(pts+np.roll(pts,-1,axis=0))/2
 d=f'M {mids[-1,0]:.4f} {mids[-1,1]:.4f} '
 for q,m in zip(pts,mids):d+=f'Q {q[0]:.4f} {q[1]:.4f} {m[0]:.4f} {m[1]:.4f} '
 return d+'Z'
