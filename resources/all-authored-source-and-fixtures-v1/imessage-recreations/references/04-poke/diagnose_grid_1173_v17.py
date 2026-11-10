"""Read-only original/candidate tile registration at the held-grid residual peak."""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v17/scene.json').read_text());frame=1173;t=frame/s['fps'];source=np.array(Image.open(p/f'measurements-v8/decoded/{frame:06}.png').convert('RGB'));control=np.array(Image.open(root/f'outputs/retained-frames/measured-frames-jRBOzF/{frame:06}.png').convert('RGB'));sift=cv2.SIFT_create();matcher=cv2.BFMatcher();rows=[]
for g in s['layers']:
 if not (g.get('start')==39.005633333333336 and g.get('children')):continue
 n=g['children'][0]
 if n['type']!='image':continue
 gx,gy,scale=[at(g,k,t)for k in ['x','y','scaleX']];w=at(n,'width',t)*scale;h=at(n,'height',t)*scale
 if gx<0 or gy<0 or gx+w>1440 or gy+h>1080:continue
 template=Image.open(p/n['src']).convert('RGBA');im=Image.new('RGBA',template.size,'white');im.alpha_composite(template);gray=cv2.cvtColor(np.array(im.convert('RGB')),cv2.COLOR_RGB2GRAY);key,desc=sift.detectAndCompute(gray,None);x0=max(0,int(gx)-25);y0=max(0,int(gy)-25);x1=min(1440,int(gx+w)+26);y1=min(1080,int(gy+h)+26);r=dict(id=g['id'],asset=n['src'],declared=[gx,gy,scale],measurements={})
 for name,image in [('source',source),('candidate',control)]:
  crop=image[y0:y1,x0:x1];k,d=sift.detectAndCompute(cv2.cvtColor(crop,cv2.COLOR_RGB2GRAY),None)
  if desc is None or d is None:continue
  good=[m for m,n2 in matcher.knnMatch(desc,d,k=2)if m.distance<.72*n2.distance]
  if len(good)<8:continue
  aa=np.float32([key[m.queryIdx].pt for m in good]);bb=np.float32([k[m.trainIdx].pt for m in good]);matrix,inliers=cv2.estimateAffinePartial2D(aa,bb,method=cv2.RANSAC,ransacReprojThreshold=1,maxIters=2000)
  if matrix is None or inliers.sum()<6:continue
  matrix[0,2]+=x0;matrix[1,2]+=y0;mask=inliers[:,0].astype(bool);projected=aa@matrix[:,:2].T+matrix[:,2];target=bb+[x0,y0];rms=float(np.sqrt(((projected[mask]-target[mask])**2).sum(1).mean()));r['measurements'][name]=dict(matrix=matrix.tolist(),inliers=int(inliers.sum()),rms=rms,x=matrix[0,2],y=matrix[1,2],scale=float(np.hypot(matrix[0,0],matrix[1,0])))
 rows.append(r)
out=p/'measurements-v8/grid-1173-v17-diagnosis.json';out.write_text(json.dumps(dict(frame=frame,method='Read-only bounded genuine individual tile-art SIFT ratio.72, source vs candidate controls, RANSAC1px; geometry is diagnostic until source-art/rasterization and actual controls verified.',records=rows),indent=2));print([(r['id'],{name:[round(v['x']-r['declared'][0],2),round(v['y']-r['declared'][1],2),round(v['scale']-r['declared'][2],5),v['inliers']]for name,v in r['measurements'].items()})for r in rows])
