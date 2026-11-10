from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import signal
P=Path(__file__).parent;B=P/'early-v13-measure';R=Image.open(P/'assets/robot.png').convert('L');rec={r['frame']:r for r in json.loads((B/'camera-fit-hardware-y.json').read_text())};out=[]
for f in range(210,225):
 r=rec[f];s=(r['right']-r['left'])/768;tx=r['left']-16*s;ty=r['hardwareY'];I=np.array(Image.open(B/'source'/f'{f-48:04d}.png').convert('L'),dtype=float)[:150,410:550];best=None
 for ui in np.arange(.76,1.061,.02):
  w=round(110*s*ui/2);T=np.asarray(R.resize((w,w)),dtype=float);T=T-T.mean();ones=np.ones(T.shape);num=signal.fftconvolve(I,T[::-1,::-1],mode='valid');su=signal.fftconvolve(I,ones,mode='valid');sq=signal.fftconvolve(I*I,ones,mode='valid');den=np.sqrt(np.maximum(1e-8,(sq-su*su/T.size)*np.sum(T*T)));corr=num/den;y,x=np.unravel_index(np.argmax(corr),corr.shape);score=float(corr[y,x]);v={'frame':f,'uiScale':float(ui),'x':float((2*(410+x)-tx)/s-346*ui),'y':float((2*y-ty)/s-160*ui),'correlation':score,'sourceRobotTop':[int((410+x)*2),int(y*2)],'cameraY':ty}
  if best is None or score>best['correlation']:best=v
 out.append(best);print(best,flush=True)
(B/'header-ui-measurements.json').write_text(json.dumps(out,indent=2)+'\n')
