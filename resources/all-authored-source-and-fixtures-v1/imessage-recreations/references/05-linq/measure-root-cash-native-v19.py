"""Measure native circle/pulse tracks from diagnostic original UI crops."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
D = Path(__file__).resolve().parent
OUT = D / 'root-cash-control-v19'
rows = []
yy, xx = np.mgrid[345:455,610:714]
previous = None
for frame in range(774,832):
    rgba = np.asarray(Image.open(OUT/f'control-{frame:06}.png').convert('RGBA'))
    image = rgba[:,:,:3].mean(2).astype(float)
    py = next(row['panelY'] for row in json.loads((OUT/'asset-provenance.json').read_text()) if row['frame']==frame)
    valid = (rgba[:,:,3]>0)&(yy+py>=0)&(yy+py<720)&(xx>=620)
    white = valid&(image>205)&(xx>=635)&(xx<680)&(yy>=375)&(yy<426)
    wy, wx = np.where(white)
    if len(wx)>25:
        x1,x2 = int(xx[wy,wx].min()),int(xx[wy,wx].max()+1)
        y1,y2 = int(yy[wy,wx].min()),int(yy[wy,wx].max()+1)
        cx,cy = (x1+x2)/2,(y1+y2)/2
        gw,gh = x2-x1,y2-y1
    else:
        cx,cy,gw,gh = 656.,400.,28.,28.
    radius = np.hypot(xx-cx,yy-cy)
    fitmask = valid&(radius>21)&(radius<55)
    x = xx[fitmask]-cx
    y = yy[fitmask]-cy
    observed = image[fitmask]
    start = [35.,35.,32.,50.,1.,15.]
    if previous is not None:
        start = [previous[k] for k in ['rx','ry','fill','stroke','strokeWidth','background']]
    def residual(p):
        rx,ry,fill,stroke,width,bg = p
        distance = (1-np.sqrt((x/rx)**2+(y/ry)**2))*(rx+ry)/2
        outer = np.clip(.5+distance+width/2,0,1)
        inner = np.clip(.5+distance-width/2,0,1)
        return bg+(stroke-bg)*outer+(fill-stroke)*inner-observed
    if len(observed)>300 and frame>=775:
        fit=least_squares(residual,start,bounds=([29,29,15,20,.5,8],[48,48,180,200,2.5,40]),loss='soft_l1',f_scale=2,max_nfev=60)
        p=fit.x
    else:
        p=np.asarray(start)
    row=dict(frame=frame,cx=cx,cy=cy,glyphWidth=gw,glyphHeight=gh,rx=float(p[0]),ry=float(p[1]),fill=float(p[2]),stroke=float(p[3]),strokeWidth=float(p[4]),background=float(p[5]),glyphVisible=frame>=775,fitMAE=float(np.abs(residual(p)).mean()) if len(observed) else None)
    rows.append(row);previous=row
    if frame in [774,775,777,786,792,797,810,820,831]:print(json.dumps(row),flush=True)
# One authentic alpha detail from the held dark control, replacing per-frame UI pixels.
reference=np.asarray(Image.open(OUT/'control-000820.png').convert('RGBA'))[:,:,:3].mean(2).astype(float)
base=next(row for row in rows if row['frame']==820)
x0,y0=round(base['cx'])-20,round(base['cy'])-20
patch=reference[y0-345:y0-345+40,x0-610:x0-610+40]
a=np.clip((patch-base['fill'])/(255-base['fill']),0,1)
a[np.abs(np.mgrid[:40,:40][1]-20)>18]=0
a[np.abs(np.mgrid[:40,:40][0]-20)>18]=0
rgba=np.zeros((40,40,4),dtype=np.uint8);rgba[:,:,:3]=255;rgba[:,:,3]=np.uint8(np.rint(a*255))
Image.fromarray(rgba).save(OUT/'plus-static-820.png')
(OUT/'native-measurements.json').write_text(json.dumps({'glyphReferenceFrame':820,'glyphImageBounds':[x0,y0,x0+40,y0+40],'glyphCoreWidth':base['glyphWidth'],'glyphCoreHeight':base['glyphHeight'],'poses':rows},indent=2)+'\n')
