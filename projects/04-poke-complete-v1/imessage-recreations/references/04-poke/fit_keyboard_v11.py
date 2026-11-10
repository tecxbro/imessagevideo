"""Fit editable early keyboard key/glyph ink to one uncensored native state."""
from pathlib import Path
from PIL import Image
import numpy as np,json,shutil,hashlib
from scipy import ndimage
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v10/scene.json').read_text());g=next(l for l in s['layers']if l['id']=='p0220');fps=s['fps'];time=480/fps;gx,gy,sx,sy=[at(g,k,time)for k in['x','y','scaleX','scaleY']];source=np.array(Image.open(p/'measurements-v8/decoded/000480.png').convert('RGB'));candidatepath=p/'measurements-v8/v10-candidate-000480.png'
if not candidatepath.exists():shutil.copy2(root/'outputs/retained-frames/measured-frames-jRBOzF/000480.png',candidatepath)
candidate=np.array(Image.open(candidatepath).convert('RGB'));rows=[]
def ink(a,roi):
    x0,y0,x1,y1=roi;c=a[y0:y1,x0:x1];mask=c.max(2)<170;yy,xx=np.where(mask)
    if not len(xx):return None
    return [int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+1+x0),int(yy.max()+1+y0)]
for i,node in enumerate(g['children']):
    if node['type']!='text'or len(node.get('text',''))!=1:continue
    rect=g['children'][i-1]
    if rect['type']!='rect':continue
    x0=round(gx+rect['x']*sx);y0=round(gy+rect['y']*sy);x1=round(x0+rect['width']*sx);y1=round(y0+rect['height']*sy)
    if not(4<x0<x1<1436 and 0<y0<y1<1080):continue
    roi=[x0+5,y0+5,x1-5,y1-5];a=ink(source,roi);b=ink(candidate,roi)
    if a is None or b is None:raise ValueError(node['id'])
    rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);nx=gx+node['x']*sx;ny=gy+node['y']*sy;x=(a[0]-(b[0]-nx)*rx-gx)/sx;y=(a[1]-(b[1]-ny)*ry-gy)/sy
    rows.append(dict(id=node['id'],text=node['text'],source_ink=a,candidate_ink=b,x=x,y=y,scaleX=node.get('scaleX',1)*rx,scaleY=node.get('scaleY',1)*ry))
(p/'measurements-v8/early-keyboard-ink-v11.json').write_text(json.dumps(dict(method='Original source480and actual canonicalv10PNG480, individual fully visible native keycell ink. Editable TextRegular glyphs; source/candidate positions/scales fitted per actual ink, not advancewidth. Screen UI is never rasterized.',candidate_sha256=hashlib.sha256(candidatepath.read_bytes()).hexdigest(),reference_frame=480,measurements=rows),indent=2));print(json.dumps(rows,indent=2))
