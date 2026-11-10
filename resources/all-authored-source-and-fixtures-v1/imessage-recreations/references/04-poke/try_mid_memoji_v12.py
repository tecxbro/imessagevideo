"""Bounded identity-material test; existing measured favorite cameras retained."""
from pathlib import Path
from PIL import Image
import numpy as np,json,copy
from v8_utils import at
p=Path(__file__).parent;s=json.loads((p/'scene-v12-candidate.json').read_text());by={l['id']:l for l in s['layers']};fps=s['fps']
def bounds(src):
    a=np.array(Image.open(p/src).convert('RGBA'));m=(a[:,:,:3].max(2)-a[:,:,:3].min(2)>10)&(a[:,:,:3].min(2)<245)&(a[:,:,3]>100);yy,xx=np.where(m);return a.shape[1],a.shape[0],[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
for id in['p0007','p0010']:
    original=by[id];g=copy.deepcopy(original);original['end']=98/fps;g['start']=98/fps;g['end']=109/fps
    def rename(n):
        n['id']='v12-mid-'+n['id']
        for c in n.get('children',[]):rename(c)
    rename(g);image=g['children'][0];oldsize=bounds(image['src']);newsrc=by['v11-late-'+id]['children'][0]['src'];newsize=bounds(newsrc);oldx,oldy,oldw,oldh=[at(image,k,98/fps)for k in['x','y','width','height']];ow,oh,ob=oldsize;nw,nh,nb=newsize;w=oldw*((ob[2]-ob[0])/ow)/((nb[2]-nb[0])/nw);h=oldh*((ob[3]-ob[1])/oh)/((nb[3]-nb[1])/nh);x=oldx+ob[0]/ow*oldw-nb[0]/nw*w;y=oldy+ob[1]/oh*oldh-nb[1]/nh*h;image.update(src=newsrc,x=x,y=y,width=w,height=h);image['keyframes']={};s['layers'].insert(s['layers'].index(original)+1,g)
(p/'scene-v12-mid-memoji-proof.json').write_text(json.dumps(s,indent=2,ensure_ascii=False))
