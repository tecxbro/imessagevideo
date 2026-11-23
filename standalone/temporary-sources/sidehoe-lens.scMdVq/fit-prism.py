from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import numpy as np,json,sys
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import Film
scene=json.loads((p/'project/scene.json').read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
base=p/'lens-probe-a'

def fit(f):
 cfg=deepcopy(scene)
 a=cfg['assistantEntranceOptics'][str(f)]
 prism=deepcopy(scene.get('assistantPrism',{}).get(str(f)))
 flare=deepcopy(a.get('flare'))
 lens=deepcopy(scene['measuredRimDisplacement'].get(str(f)))
 pin=deepcopy(a.get('pin'))
 shift,breadth={134:(0,0),135:(4.3,.20),136:(4.9,.40),137:(1.8,.39)}[f]
 ref=np.array(Image.open(src/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 prior=np.array(Image.open(base/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 def rate(img):
    diff=np.abs(img-ref)
    base=float(diff.mean())
    if f in (135,136,137):
     base+=.06*float(diff[890:].mean())
    return base
 baseline=rate(prior)
 result=baseline
 defaults=[shift,breadth,1,0,0,1,0,0,1,0,0,1,12,0,0,0,0]
 best=defaults[:]
 def update(v):
    shift,breadth,rip_gain,rip_dx,prism_y,prism_gain,lx,ly,lg,rx,ry,rg,stretch,px,py,pd,pbend=v
    if f==134:
     a['exposure']=stretch
     a['pin']=[pin[0]+px,pin[1]+py,pin[2]+pd,pin[3]+pbend]
    else:
     a['lensFringe']=[shift,breadth]
     cfg['measuredRimDisplacement'][str(f)]=[[x+rip_dx,y*rip_gain] for x,y in lens]
    if prism:
     cfg['assistantPrism'][str(f)]=[[x,y+prism_y,*[q*prism_gain for q in colors]] for x,y,*colors in prism]
    if flare:
     a['flare']=[[x+(lx if x<500 else rx),y+(ly if x<500 else ry),w,h,angle,
                 *[q*(lg if x<500 else rg) for q in (r,g,b)]]
                 for x,y,w,h,angle,r,g,b in flare]
 def score(v):
    update(v)
    return rate(np.asarray(Film(cfg).frame(f),dtype=np.int16))
 moves=[
 (-1.5,-.75,0,.75,1.5),(-.11,-.06,0,.06,.11),(-.22,-.12,0,.12,.22),(-6,-3,0,3,6),
 (-6,-3,0,3,6),(-.45,-.2,0,.14,.3),(-7,-4,0,4,7),(-11,-5,0,5,11),(-.40,-.23,0,.22,.4),
 (-7,-4,0,4,7),(-11,-5,0,5,11),(-.40,-.23,0,.22,.4),
 (-6,-3,0,3,6),(-6,-3,0,3,6),(-6,-3,0,3,6),(-10,-5,0,5,10),(-2.2,-1,0,1.5,3)
 ]
 dims=range(12,17) if f==134 else [0,1,2,3,*([4,5] if prism else []),*(range(6,12) if flare else [])]
 for _ in range(2):
    for k in dims:
     for d in moves[k]:
      v=best[:]
      v[k]=defaults[k]+d
      if k in (0,1) and v[k]<.05:
       continue
      q=score(v)
      if q<result:
       result=q;best=v
 update(best)
 return f,baseline,result,a,cfg.get('assistantPrism',{}).get(str(f)),cfg['measuredRimDisplacement'].get(str(f))
records=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 for f,b,r,a,pin,lens in pool.map(fit,range(134,138)):
  print(f,b,r,flush=True)
  records.append([f,b,r,a,pin,lens])
(p/'prism-fit.json').write_text(json.dumps(records,indent=2)+'\n')
