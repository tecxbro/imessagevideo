"""Native static UI camera calibration; excludes independently changing rows."""
from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;R=D.parent.parent;B=R/'outputs/05-linq/final-v17';s=json.loads((B/'scene.json').read_text());g=next(q for q in s['layers']if q['id']=='rich-group-12');im=g['children'][0];ar=np.array(Image.open(B/im['src']).convert('RGB')).astype(float).mean(2)
def value(k,f):
 t=f/30;a=g.get('keyframes',{}).get(k,[])
 if not a:return g.get(k,1 if k in ['scaleX','scaleY','opacity']else 0)
 if t<=a[0]['t']:return a[0]['value']
 for p,q in zip(a,a[1:]):
  if t<=q['t']:
   w=(t-p['t'])/(q['t']-p['t']);return p['value']+(q['value']-p['value'])*w
 return a[-1]['value']
rows=[]
for f in range(998,1074):
 p=D/'measurements/native-transition'/f'{f:06d}.png'
 if not p.exists():continue
 src=np.array(Image.open(p).convert('RGB')).astype(float).mean(2);x,y,sx,sy=[value(k,f)for k in ['x','y','scaleX','scaleY']];opacity=value('opacity',f)
 xx,yy=np.meshgrid(np.arange(max(0,int(x)+5),min(960,int(x+sx*584)-5),2),np.arange(0,720,2));u=(xx-x)/sx;v=(yy-y)/sy
 keep=(u>=5)&(u<579)&(v>=5)&(v<1130)&~((v>425)&(v<565))&~((v>905)&(v<1020))
 tx=xx[keep].astype(float);ty=yy[keep].astype(float);target=src[yy[keep],xx[keep]]
 def residual(q):
  nx,ny,nsx,nsy=q;model=map_coordinates(ar,[(ty-ny)/nsy,(tx-nx)/nsx],order=1,mode='constant',cval=255,prefilter=False);model=255-(255-model)*opacity
  return(model-target)/30
 initial=np.array([x,y,sx,sy]);fit=least_squares(residual,initial,bounds=(initial+[-6,-6,-.025,-.045],initial+[6,6,.025,.045]),max_nfev=75,diff_step=[.001,.001,.0001,.0001]);out=fit.x
 rows.append({'frame':f,'before':dict(zip(['x','y','scaleX','scaleY'],map(float,initial))),'candidate':dict(zip(['x','y','scaleX','scaleY'],map(float,out))),'beforeFitRMSE':float(np.sqrt(np.mean(residual(initial)**2))),'afterFitRMSE':float(np.sqrt(np.mean(residual(out)**2))),'fitPoints':len(tx)})
 if f%10==0 or f==1031:print(rows[-1],flush=True)
(D/'foodash-camera-v18-diagnostic.json').write_text(json.dumps({'scope':[998,1073],'excludedCanonicalRows':[[425,565],[905,1020]],'rows':rows,'notice':'Numeric diagnostic camera fit against one genuine static UI document. No source-frame playback or warped candidate frame is an authored asset.'},indent=2)+'\n')
