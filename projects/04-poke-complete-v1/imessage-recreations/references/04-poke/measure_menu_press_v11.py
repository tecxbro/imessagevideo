from pathlib import Path
from PIL import Image
import numpy as np,json,sys
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v10/scene.json').read_text());g=next(l for l in s['layers']if l['id']=='p0132');node=next(l for l in g['children']if l['id']=='p0125');rows=[]
for n in range(330,361):
 t=n/s['fps'];x,y,scale=[at(g,k,t)for k in['x','y','scaleX']];left=round(x+node['x']*scale-2);top=round(y+node['y']*scale);right=round(left+250*scale);bottom=round(top+75*scale)
 a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(float);c=a[max(0,top):min(1080,bottom),max(0,left):min(1440,right)];v=c[(c[:,:,2]-c[:,:,0]>20)&(c[:,:,1]-c[:,:,0]>10)];red=float(np.percentile(v[:,0],5))if len(v)else None;opacity=float(np.clip((236-red)/(236-25),0,1))if red is not None else None;rows.append(dict(frame=n,time=t,roi=[left,top,right,bottom],red_core5=red,opacity=opacity))
(p/'measurements-v8/menu-press-v11.json').write_text(json.dumps(dict(method='Source blue-text core5th-percentile red relative to authored native25/236blue/bodyred; emoji and glyph share a measured press fade.',measurements=rows),indent=2));print(json.dumps(rows,indent=2))
