from pathlib import Path
from PIL import Image
import numpy as np
from scipy.optimize import least_squares
from scipy.ndimage import map_coordinates
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-portraits.if793d/full-frames')
for frame in range(640,660):
    a,b=[np.asarray(Image.open(d/f'{frame:06}.png').convert('RGB'),dtype='float32') for d in (src,prior)]
    loc=[]
    for im in (a,b):
        section=(im[185:805,:,:3].mean(2)<60)
        y,x=np.where(section)
        loc.append((x.min(),x.max(),y.min()+185,y.max()+185))
    x0,x1,y0,y1=loc[0]
    l,r,t,d=loc[1]
    avg=((x0+x1)/2,(y0+y1)/2)
    # Align high-contrast rails using border windows and keep composer pixels out of the geometry fit.
    yy,xx=np.mgrid[max(0,y0-15):min(1000,y1+16):3,max(0,x0-14):min(1000,x1+16):3]
    on_rail = (xx<x0+32)|(xx>x1-32)|(yy<y0+22)|(yy>y1-24)
    x,y=xx[on_rail],yy[on_rail]
    ga=a[y,x,:3].mean(1); gb=b[:,:,:3].mean(2)
    def fit(v):
        dx,dy,sx,sy=v
        sample=map_coordinates(gb,[(y-avg[1]-dy)/sy+avg[1],(x-avg[0]-dx)/sx+avg[0]],order=1)
        return (sample-ga).astype(np.float64)
    opt=least_squares(fit,[(x0+x1-l-r)/2,(y0+y1-t-d)/2,(x1-x0+1)/(r-l+1),(y1-y0+1)/(d-t+1)],loss='soft_l1',f_scale=20,diff_step=1e-3,x_scale=(7,7,.02,.02),max_nfev=19)
    dx,dy,sx,sy=opt.x
    ys,xs=np.mgrid[y0:y1+1:3,x0:x1+1:3]
    z=np.stack([map_coordinates(b[:,:,j],[(ys-avg[1]-dy)/sy+avg[1],(xs-avg[0]-dx)/sx+avg[0]],order=1) for j in range(3)],axis=-1)
    aa=a[ys,xs]
    err0=np.mean(abs(aa-b[ys,xs]))
    err1=np.mean(abs(aa-z))
    print(frame,loc,np.round(opt.x,3),np.round([err0,err1],2),flush=True)
