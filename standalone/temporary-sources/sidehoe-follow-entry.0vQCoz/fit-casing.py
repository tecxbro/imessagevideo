from measure import *
from scipy.ndimage import map_coordinates, gaussian_filter
from scipy.optimize import minimize

def model_fit(f):
    src,old=[np.asarray(Image.open(d/f'{f:06d}.png').convert('RGB'),dtype=np.float32)
        for d in (SRC,ROOT/'probe')]
    x,y,s,asp,ky=camera(f)
    width,height=399*s,826*s*asp
    lo=max(1,int(x-10)); hi=min(999,round(x+width+11))
    t0=max(0,round(y-11)); t1=min(999,round(y+height+11))
    yy,xx = np.mgrid[t0:t1:3,lo:hi:3]
    # Sample the rails and the top/bottom belt. Exclude display ink and the cursor.
    weight = ((xx<x+22*s)|(xx>x+width-21*s)|(yy<y+16*s)|(yy>y+height-14*s))
    bx,by=xx[weight],yy[weight]
    measured=gaussian_filter(src.mean(2),.8)[by,bx]
    authored=gaussian_filter(old.mean(2),.8)
    cx,cy=x+width/2,y+height/2
    def loss(v):
        shift_x, shift_y, width_change, height_change=v
        coordinates=[(by-cy-shift_y)/(1+height_change/height)+cy,
                     (bx-cx-shift_x)/(1+width_change/width)+cx]
        v=map_coordinates(authored,coordinates,order=1)
        return (np.mean(np.square(v-measured))+np.mean(np.abs(v-measured))*5
                + np.dot([.35,.24,.18,.05], np.square([shift_x,shift_y,width_change,height_change])))
    start=np.zeros(4)
    limits=[(-4,4),(-9,9),(-7,7),(-19,19)]
    best=minimize(loss,start,method='Powell',bounds=limits,options={'maxiter':20,'ftol':1e-5})
    result=np.round(best.x,3)
    return [result.tolist(),round(loss(start),2),round(loss(result),2)]

rows={}
for f in range(636,660):
    rows[f]=model_fit(f)
    print(f,*rows[f],flush=True)
(ROOT/'casing-fit.json').write_text(json.dumps(rows,indent=2)+'\n')
