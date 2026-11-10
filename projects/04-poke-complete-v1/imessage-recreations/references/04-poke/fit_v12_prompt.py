"""Clean late-conversation ink fit, with actual prompt medium font proof."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((p/'scene-v12-prompt-prototype-01.json').read_text());by={g['id']:g for g in s['layers']};fps=s['fps'];n=674;t=n/fps;out=[]
def ink(file,roi,gray):
 a=np.array(Image.open(file).convert('RGB')).astype(int);x,y,z,w=roi;c=a[y:w,x:z];mask=(c.min(2)>75)&(c.max(2)<215)&(c.max(2)-c.min(2)<12)if gray else c.max(2)<100;yy,xx=np.where(mask);return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+x+1),int(yy.max()+y+1)]
for groupid,nodeid,roi,gray in[('p0230','p0229',[180,430,1250,535],False),('p0259','p0258',[310,620,1100,700],True)]:
 g=by[groupid];node=next(c for c in g['children']if c['id']==nodeid);a=ink(p/f'measurements-v8/decoded/{n:06}.png',roi,gray);file=root/f'outputs/04-poke/v12-prompt-diagnostic-01/{n:06}.png';b=ink(file,roi,gray);gx,gy,sx,sy=[at(g,k,t)for k in['x','y','scaleX','scaleY']];nx=gx+at(node,'x',t)*sx;ny=gy+at(node,'y',t)*sy;rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);out.append(dict(id=nodeid,source_ink=a,candidate_ink=b,x=(a[0]-(b[0]-nx)*rx-gx)/sx,y=(a[1]-(b[1]-ny)*ry-gy)/sy,scaleX=at(node,'scaleX',t)*rx,scaleY=at(node,'scaleY',t)*ry))
(p/'measurements-v8/prompt-browser-fit-v12.json').write_text(json.dumps(dict(method='Original674after modal/scrim release; actual isolated native GSAP type proof. Found sentence stays TextRegular; independently ranked prompt is DisplayMedium.',measurements=out),indent=2));print(json.dumps(out,indent=2))
