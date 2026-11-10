from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy import ndimage
p=Path(__file__).parent

def fit(file,kind,side='right',stage=False):
    a=np.array(Image.open(file).convert('RGB')).astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    if kind=='blue':
        mask=(r<240)&(g>200)&(b>230)&((b-g)>3)&((b-r)>12)
        if stage:mask[:,1250:]=False
    elif kind=='yellow':
        mask=(r>230)&(g>180)&(b<185)
        if stage:
            mask[:,:1000]=False;mask[500:]=False
    elif kind=='mint':
        mask=(g>225)&(b>225)&(r<235)&((g-r)>12)&((b-g)<4)
        if stage:mask[:,:950]=False
    else:
        mask=(r>240)&(g>210)&(g<245)&(b>195)&(b<240)&((r-g)>10)&((g-b)>2)
        if stage:
            mask[:,:300]=False;mask[:700]=False
    points=[]
    for y in range(0,a.shape[0],3):
        xs=np.where(mask[y])[0]
        if len(xs)<5:continue
        x=float(xs.max())
        if side=='left':x=float(xs.min())
        if x<=1 or x>=a.shape[1]-2:continue
        if stage and kind=='blue' and x>=1249:continue
        if stage and kind=='yellow' and (x<=1001 or y>=498):continue
        if stage and kind=='mint' and x<=951:continue
        if stage and kind=='pink' and (x<=301 or y<=701):continue
        points.append((x,float(y)))
    if len(points)<12:return None
    xy=np.array(points);x=xy[:,0];y=xy[:,1]
    values=np.linalg.lstsq(np.column_stack([x,y,np.ones_like(x)]),-(x*x+y*y),rcond=None)[0]
    cx=-values[0]/2;cy=-values[1]/2;r2=cx*cx+cy*cy-values[2]
    if r2<=0:return None
    radius=np.sqrt(r2);errors=np.abs(np.sqrt((x-cx)**2+(y-cy)**2)-radius)
    return {'cx':float(cx),'cy':float(cy),'radius':float(radius),'residual':float(errors.mean()),'points':len(points)}

assets=[('bob','bob-large.png','blue','right',(0,0)),('laptop','laptop-person.png','yellow','right',(1166,0)),('robot','robot-large.png','mint','left',(1320,430)),('alice','alice-large.png','pink','left',(400,820))]
result={}
for name,file,kind,side,base in assets:
    world=fit(p/'assets'/file,kind,side)
    rows=[]
    for index in range(11,17):
        source=fit(p/'transition-14'/f'{index:02}.png',kind,side,True)
        if source is None or source['residual']>4:continue
        scale=source['radius']/world['radius']
        if not .5<scale<20:continue
        rows.append({'t':14+(index-1)/30,'scale':scale,'x':source['cx']-scale*world['cx'],'y':source['cy']-scale*world['cy'],'fit':source})
    result[name]={'world':world,'poses':rows,'base_xy':base,'asset':file}
(p/'transition-14/independent-avatar-poses.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
