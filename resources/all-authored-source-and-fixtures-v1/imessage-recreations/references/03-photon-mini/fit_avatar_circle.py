from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy import ndimage
p=Path(__file__).parent

def fit(file):
    a=np.array(Image.open(file).convert('RGB')).astype('float64')
    mask=(a[:,:,0]<240)&(a[:,:,1]>200)&(a[:,:,2]>230)&((a[:,:,2]-a[:,:,1])>3)&((a[:,:,2]-a[:,:,0])>12)
    labeled,number=ndimage.label(mask)
    candidates=[]
    for label,box in enumerate(ndimage.find_objects(labeled),1):
        if box is not None and box[1].start<100 and box[1].stop-box[1].start>200:
            candidates.append((int((labeled[box]==label).sum()),label))
    if candidates:
        selected=max(candidates)[1]
        mask=labeled==selected
    points=[]
    for y in range(0,a.shape[0],4):
        xs=np.where(mask[y])[0]
        if len(xs)>20 and xs.max()<a.shape[1]-2:
            points.append([float(xs.max()),float(y)])
    xy=np.array(points)
    if len(xy)<15:
        return None
    x=xy[:,0];y=xy[:,1]
    coefficients=np.linalg.lstsq(np.column_stack([x,y,np.ones_like(x)]),-(x*x+y*y),rcond=None)[0]
    cx=-coefficients[0]/2;cy=-coefficients[1]/2;r=np.sqrt(cx*cx+cy*cy-coefficients[2])
    residual=np.abs(np.sqrt((x-cx)**2+(y-cy)**2)-r)
    return {'cx':float(cx),'cy':float(cy),'radius':float(r),'mean_residual':float(residual.mean()),'points':len(points)}
world=fit(p/'assets/bob-large.png');rows=[]
for index in range(11,17):
    file=p/'transition-14'/f'{index:02}.png'
    if not file.exists():continue
    circle=fit(file)
    if circle is None:continue
    scale=circle['radius']/world['radius'];x=circle['cx']-scale*world['cx'];y=circle['cy']-scale*world['cy']
    rows.append({'time':14+(index-1)/30,'scale':float(scale),'x':float(x),'y':float(y),'circle':circle})
(p/'transition-14/avatar-circle-camera.json').write_text(json.dumps({'world_circle':world,'poses':rows},indent=2))
print(json.dumps({'world_circle':world,'poses':rows},indent=2))
# Diagnostic avatar-only world composition from separate declared original assets.
margin=600
worldimage=Image.new('RGBA',(3120,2280),(253,253,253,255))
draw_world=ImageDraw.Draw(worldimage)
r=world['radius'];cx=world['cx']+margin;cy=world['cy']+margin
color=Image.open(p/'assets/bob-large.png').convert('RGB').getpixel((100,200))
draw_world.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*color,255))
for name,x,y,w,h in [('bob-large.png',0,0,1110,830),('laptop-person.png',1140,0,640,416),('robot-large.png',1320,430,600,650),('alice-large.png',400,820,720,260)]:
    asset=Image.open(p/'assets'/name).convert('RGBA').resize((w,h),Image.Resampling.BICUBIC);worldimage.alpha_composite(asset,(x+margin,y+margin))
sheet=Image.new('RGB',(960,len(rows)*294),'#dddddd');draw=ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
    scale=row['scale'];matrix=(1/scale,0,margin-row['x']/scale,0,1/scale,margin-row['y']/scale)
    candidate=worldimage.transform((1920,1080),Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC,fillcolor=(253,253,253,255)).convert('RGB')
    source=Image.open(p/'transition-14'/f'{11+i:02}.png').convert('RGB')
    sheet.paste(source.resize((480,270)),(0,i*294+24));sheet.paste(candidate.resize((480,270)),(480,i*294+24));draw.text((8,i*294+4),f"{row['time']:.5f}s source / fitted native avatar assets",fill='black')
sheet.save(p/'transition-14/avatar-fit-contact.jpg')
