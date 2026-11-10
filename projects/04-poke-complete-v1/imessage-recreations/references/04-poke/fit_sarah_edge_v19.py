"""Independent native gray-edge camera/blur registration; text is excluded."""
from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
from scipy.optimize import least_squares
from scipy.special import erf
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v18/scene.json').read_text());g=next(x for x in s['layers']if x['id']=='p0066');raw=json.loads((p/'measurements-v8/sarah-entry-142-175-v19-parent.json').read_text());rows=[]
def edge(image,guess):
 low=max(0,int(guess)-25);high=min(1080,int(guess)+45);yy=np.arange(low,high,dtype=float);profile=np.median(image[low:high,500:900].mean(2),axis=1)
 def model(v):
  midpoint,sigma,bg,contrast,slope=v
  return bg+slope*(yy-guess)-contrast*(1+erf((yy-midpoint)/(2**.5*sigma)))/2
 initial=[guess+2,2,255,19,0];bounds=([guess-20,.2,225,8,-.3],[guess+25,16,260,35,.3]);fit=least_squares(lambda v:model(v)-profile,initial,bounds=bounds,loss='soft_l1',f_scale=.6,max_nfev=500)
 return dict(edge=float(fit.x[0]),sigma=float(fit.x[1]),background=float(fit.x[2]),contrast=float(fit.x[3]),slope=float(fit.x[4]),RMS=float(np.sqrt(np.mean((model(fit.x)-profile)**2))),sample_y=yy.tolist(),sample_gray=profile.tolist())
for n in range(142,176):
 t=n/s['fps'];r=next(r for r in raw['records']if r['frame']==n);obs=next(a for a in r['body_threshold_observations']if a['threshold']==243);source=np.array(Image.open(p/f'measurements-v8/native-v19/{n:06}.png').convert('RGB'));candidate=np.array(Image.open(root/f'outputs/retained-frames/measured-frames-jRBOzF/{n:06}.png').convert('RGB'));a=edge(source,obs['bounds'][1]);b=edge(candidate,at(g,'y',t));oldblur=at(g,'blur',t);scale=at(g,'scaleX',t);base=max(.2,np.sqrt(max(0,b['sigma']**2-(oldblur*scale)**2)));blur=float(np.sqrt(max(0,a['sigma']**2-base**2))/scale)
 rows.append(dict(frame=n,time=t,y=at(g,'y',t)+a['edge']-b['edge'],blur=blur,old_y=at(g,'y',t),old_blur=oldblur,source=a,candidate=b))
out=dict(method='Each exact native142–175 gray main-pill top edge is fitted independently on the median RGB profile x500:900, excluding text. Error-function step+local linear lighting solves continuous camera/blur; source vs actual candidate edge difference updates independent camera. Gaussian AA floor is removed before blur proposal. Source175onlyupperedge is used, not its contaminated fullcomponent; no new opacity is inferred. Native body/text/lifecycle proof is mandatory.',measurements=rows);(p/'measurements-v8/sarah-camera-edge-v19.json').write_text(json.dumps(out,indent=2));print([(r['frame'],round(r['y'],3),round(r['old_y'],3),round(r['blur'],3),round(r['old_blur'],3),round(r['source']['RMS'],3))for r in rows if r['frame']in [142,143,145,146,150,155,160,165,170,174,175]])
