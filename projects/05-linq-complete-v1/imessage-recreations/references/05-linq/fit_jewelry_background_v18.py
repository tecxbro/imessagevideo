"""Reproduce the native-template background blur/white-wash calibration.

First render scene-jewelry-bgfit-v18.json frame587 to
verification/05-jewelry-v18/bgfit/19.567.png. This template contains only
independently authored native thread components on white, never source playback.
The source ROI supplies scalar numeric fit parameters only.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.optimize import minimize_scalar
D=Path(__file__).resolve().parent;R=D.parent.parent;F=D/'measurements/native-transition'
s=json.loads((D/'scene-jewelry-v18.json').read_text())
template=255-np.array(Image.open(R/'verification/05-jewelry-v18/bgfit/19.567.png').convert('RGB')).astype(float).mean(2)
roi=(slice(150,470),slice(75,180));sigmas=np.arange(2,20.001,.25)
models=np.stack([gaussian_filter(template,z,mode='constant')[roi].ravel()for z in sigmas]);den=np.sum(models*models,axis=1);rows=[]
for f in range(578,651):
 a=255-np.array(Image.open(F/f'{f:06d}.png').convert('RGB')).astype(float).mean(2);target=a[roi].ravel();dots=models@target;alphas=np.clip(dots/den,0,1);errors=np.sum((models*alphas[:,None]-target)**2,axis=1);i=int(np.argmin(errors))
 def fit(z):
  m=gaussian_filter(template,float(z),mode='constant')[roi].ravel();alpha=float(np.clip(m@target/(m@m),0,1));return float(np.mean((m*alpha-target)**2)),alpha
 z=minimize_scalar(lambda z:fit(z)[0],bounds=(max(2,sigmas[i]-.25),min(20,sigmas[i]+.25)),method='bounded',options={'xatol':1e-5}).x;err,alpha=fit(z)
 rows.append({'frame':f,'blur':round(float(z),6),'opacity':round(alpha,6),'ROI_RMSE':err**.5})
bg=next(q for q in s['layers']if q['id']=='broad-v5-group-59');bg['start']=578/30
for i,c in enumerate(bg['children']):c['y']=[183.43459463119507,290.7995471060276][i];c['opacity']=1;c.pop('keyframes',None)
bg['keyframes']={k:[{'t':r['frame']/30,'value':r[k],'ease':'linear'}for r in rows]for k in ['blur','opacity']}
next(q for q in s['layers']if q['id']=='g-580')['end']=578/30
(D/'scene-jewelry-v18b.json').write_text(json.dumps(s,indent=2)+'\n')
(D/'jewelry-background-v18-measurements.json').write_text(json.dumps({'ROI':[75,150,180,470],'template':'verification/05-jewelry-v18/bgfit/19.567.png','nativeGeometryY':[183.43459463119507,290.7995471060276],'rows':rows,'model':'Gaussian convolution of independently native-rendered fixed UI components over white plus scalar opacity; source only calibrates numeric blur/opacity, never supplies a background frame layer.'},indent=2)+'\n')
print('fit',len(rows),'native scalar poses')
