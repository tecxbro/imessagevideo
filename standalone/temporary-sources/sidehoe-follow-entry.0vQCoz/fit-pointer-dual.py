from measure import *
from render import cursor
from scipy.optimize import minimize

rows={}
initial_mse=json.loads((ROOT/"pointer-fit-simplex.json").read_text())
S=json.loads((ROOT.parent/"sidehoe-phone.tJtcYo/project/scene.json").read_text())
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
    def delta(v):
        target=Image.new('RGBA',(106,117),background)
        cursor(target,*v[:3],v[6],v[3],tuple(v[4:6]))
        return np.asarray(target.convert('RGB'),dtype=float)-r
    def costs(v):
        residual=delta(v)
        return float(np.mean(np.abs(residual))),float(np.mean(residual**2))
    def loss(v):
        mae,mse=costs(v)
        return mae+mse/390
    bounds=[(initial[0]-4,initial[0]+4),(initial[1]-4,initial[1]+4),(a-12,a+12),
            (s*.74,s*1.18),(max(.08,bx-.8),bx+2),(max(.08,by-.8),by+2),(.78,1)]
    points=np.array(initial_mse[str(f)])
    points[:2]-=[bx0,by0]
    steps=np.array([.87,.85,3.6,.055,.45,.38,-.075])
    options={'maxiter':240,'xatol':.005,'fatol':.0001}
    candidates=[np.asarray(initial),points]
    for seed in (np.asarray(initial),points):
        simplex=np.vstack((seed,seed+np.diag(steps)))
        res=minimize(loss,seed,bounds=bounds,method='Nelder-Mead',
                     options=dict(options,initial_simplex=simplex))
        candidates.append(res.x.copy())
    threshold=costs(initial)
    dual=[v for v in candidates if all(j<=k for j,k in zip(costs(v),threshold))]
    best=min(dual,key=loss)
    bx1=best.copy()
    bx1[:2]+=[bx0,by0]
    rows[f]=[round(float(v),4) for v in bx1]
    print(f,[tuple(round(x,4) for x in costs(v)) for v in (initial,best)],rows[f],flush=True)

(ROOT/'pointer-fit-dual.json').write_text(json.dumps(rows,indent=2)+'\n')
