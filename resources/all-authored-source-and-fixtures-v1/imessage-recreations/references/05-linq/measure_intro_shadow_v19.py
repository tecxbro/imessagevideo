"""Read-only fit of the native composer's exterior shadow profiles."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.special import erf
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent
im=np.asarray(Image.open(D/'measurements/composer-v19/native/source-000087.png').convert('RGB')).astype(float)
obs=255-im[260:462,470:610].mean((1,2))
y=np.arange(260,462)+.5
keep=(y<320)|(y>402)
def model(z):
    alpha,offset,sigma=z
    return 255*alpha*.5*(erf((y-320-offset)/(2**.5*sigma))-erf((y-402-offset)/(2**.5*sigma)))
fit=least_squares(lambda z:(model(z)-obs)[keep],[.12,4,10],bounds=([.001,-10,1],[.8,20,40]),max_nfev=100)
z=fit.x
r={'inputExterior':dict(zip(['alpha','offsetY','sigma'],map(float,z))),'profileMAE':float(abs(model(z)[keep]-obs[keep]).mean()),'oldProfileMAE':float(abs(model([12/255,4,14])[keep]-obs[keep]).mean()),'sourceFrame':87,'method':'Only exterior of the held composer, straight top/bottom edge atx470–610; no source pixels copied to a rendered asset.'}
(D/'measurements/composer-v19/shadow-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
from scipy.ndimage import gaussian_filter,map_coordinates
xx,yy=np.meshgrid(np.arange(140,275)+.5,np.arange(270,450)+.5)
body=((xx-219)**2+(yy-360)**2<=39**2).astype(float)
target=255-im[270:450,140:275].mean(2)
keep=(body==0)&(xx<240)
def circle_model(q):
    alpha,dy,sigma=q
    sh=gaussian_filter(body,sigma=sigma,mode='constant')
    sh=map_coordinates(sh,[(yy-.5-270-dy),(xx-.5-140)],order=1,mode='constant',cval=0,prefilter=False)
    return 255*alpha*sh
z=least_squares(lambda q:(circle_model(q)-target)[keep],[.08,3,8],bounds=([.001,-10,1],[.8,20,35]),max_nfev=60).x
r['plusExterior']=dict(zip(['alpha','offsetY','sigma'],map(float,z)))
r['circleProfileMAE']=float(abs(circle_model(z)[keep]-target[keep]).mean())
r['circleOldProfileMAE']=float(abs(circle_model([11/255,3,8])[keep]-target[keep]).mean())
(D/'measurements/composer-v19/shadow-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
s=json.loads((D/'scene-v19-composed.json').read_text())
i=next(q for q in s['layers']if q['id']=='v19-intro-composer')
b=next(q for q in i['children']if q['id']=='v19-composer-white-body')
for node,name in zip(b['children'],['plusExterior','inputExterior']):
    q=r[name]
    node['shadow']={'x':0,'y':q['offsetY'],'blur':q['sigma'],'color':f"#000000{round(q['alpha']*255):02x}"}
(D/'scene-composers-shadow-v19.json').write_text(json.dumps(s,indent=2)+'\n')
