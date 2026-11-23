from measure import *
from render import cursor
from scipy.optimize import minimize

rows={}
for f in range(646,660):
    image=Image.open(SRC/f'{f:06d}.png').convert('RGB')
    old=Image.open(PRE/f'{f:06d}.png').convert('RGB')
    x,y,a,s,bx,by,al=interpolate(S['tracks']['followLeadIn'],f)
    bx0,by0=round(x)-44,round(y)-62
    box=(bx0,by0,bx0+106,by0+117)
    # Fit within a window that isolates the moving pointer on the paper.
    r=np.asarray(image.crop(box),dtype=float)
    g=np.asarray(old.crop(box),dtype=float)
    background=tuple(int(z) for z in np.median(r,axis=(0,1)))
    initial=[x-bx0,y-by0,a,s,bx,by,al]
    def loss(v):
        target=Image.new('RGBA',(106,117),background)
        cursor(target,*v[:3],v[6],v[3],tuple(v[4:6]))
        delta=np.asarray(target.convert('RGB'),dtype=float)-r
        return float(np.mean(delta*delta))
    bounds=[(initial[0]-4,initial[0]+4),(initial[1]-4,initial[1]+4),(a-12,a+12),
            (s*.74,s*1.18),(max(.08,bx-.8),bx+2),(max(.08,by-.8),by+2),(.78,1)]
    steps=np.array([1.4,1.5,4,.05,.60,.70,-.04])
    simplex=np.vstack((initial,np.array(initial)+np.diag(steps)))
    opt=minimize(loss, initial, bounds=bounds, method='Nelder-Mead',
                 options={'maxiter':260,'initial_simplex':simplex,'xatol':.005,'fatol':.006})
    v=opt.x.copy()
    best=v if loss(v)<loss(initial) else np.array(initial)
    bx1=best.copy()
    bx1[:2]+=[bx0,by0]
    rows[f]=[round(float(v),4) for v in bx1]
    print(f, round(float(np.mean((g-r)**2)),3), round(loss(initial),3), round(loss(best),3), rows[f],flush=True)
(ROOT/'pointer-fit-simplex.json').write_text(json.dumps(rows,indent=2)+'\n')
