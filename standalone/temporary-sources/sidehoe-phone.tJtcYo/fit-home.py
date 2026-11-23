from pathlib import Path
from PIL import Image
from scipy.optimize import least_squares
from scipy.special import ndtr
import json,sys,numpy as np
p=Path(__file__).parent;sys.path.insert(0,str(p/'project'))
from render import interpolate
root=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
q=p/'project/scene.json';j=json.loads(q.read_text())
stage=j['tracks']['sofiaMeasuredCamera']
ys={313:484,314:605,315:663,316:713,317:756,318:788,319:812,320:832,321:851,322:867,323:882,324:895,325:907,326:919,327:930,328:942,329:954,330:967}
out=[]
for f,y in ys.items():
 ref=np.array(Image.open(root/f'{f:06}.png').convert('RGB'),dtype=float)
 x,_,s=interpolate(stage,f)
 c=round(x+200*s)
 right=int(min(1000,c+112))
 fmt=np.median(ref[:,c-42:c+43,:],axis=(1,2))
 before=np.concatenate([ref[:,c-111:c-98,:],ref[:,c+97:right,:]],axis=1).mean(axis=(1,2))
 shade=before-fmt
 past=[18,26,22,15,11,10,9,8,7,7,7,7,7,7,7,7,7,7][f-313]
 rng=np.arange(y-past,min(1000,y+past)+1)
 vals=shade[rng]
 def predict(v):
  m,h,sigma,depth=v
  return depth*(ndtr((rng+.5-m+h/2)/sigma)-ndtr((rng+.5-m-h/2)/sigma))
 def err(v):
  d=predict(v)-vals
  return np.r_[d,2*(v[1]-6.2),.03*(v[3]-179)]
 init=[y+.5,6.2,np.interp(f,[313,318,323],[19,6,1.2]),179]
 result=least_squares(err,init,bounds=([y-4,3,.4,110],[y+5,9,38,217]),loss='soft_l1',max_nfev=200)
 yy,h,gain,amplitude=result.x
 cx=c+.5
 w=134 if f<326 else 134+(f-326)*1.15
 out.append([f,cx,*np.round([yy,w,h,gain,amplitude],3).tolist()])
 print(f,out[-1],round(np.abs(predict(result.x)-vals).mean(),2))
j['tracks']['sofiaHomeIndicator']=out
q.write_text(json.dumps(j,indent=2)+'\n')
