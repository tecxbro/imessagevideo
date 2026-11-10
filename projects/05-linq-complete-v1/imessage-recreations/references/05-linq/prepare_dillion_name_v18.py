"""One original outlined UI word; independent measured camera, no source frames."""
from pathlib import Path
import json,copy,importlib.util
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;R=D.parent.parent;s=json.loads((D/'scene-foodash-camera-v18-final.json').read_text());g=next(q for q in s['layers']if q['id']=='rich-group-12');art=np.array(Image.open(g['children'][0]['src']).convert('RGB')).astype(float);word=art[464:492,38:122].mean(2);ink=255-word;ys,xs=np.where(word<100);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace);black=float(np.percentile(word[word<100],10));alpha=np.clip(ink/(255-black),0,1);path,stats=trace.trace_alpha(alpha)
def val(k,f):
 a=g['keyframes'][k];return next(e['value']for e in a if abs(e['t']*30-f)<1e-5)
rows=[]
for f in range(998,1036):
 src=np.array(Image.open(D/'measurements/native-transition'/f'{f:06d}.png').convert('RGB')).astype(float).mean(2);px,py,psx,psy=[val(k,f)for k in ['x','y','scaleX','scaleY']];x0=max(0,int(px+psx*20));x1=min(960,int(px+psx*175));y0=max(0,int(py+psy*445));y1=min(720,int(py+psy*504));c=src[y0:y1,x0:x1];by,bx=np.where(c<100)
 if len(by)<5:raise ValueError(('Name not identified',f))
 bbox=[int(bx.min()+x0),int(by.min()+y0),int(bx.max()+x0+1),int(by.max()+y0+1)];sx=(bbox[2]-bbox[0])/(box[2]-box[0]);sy=(bbox[3]-bbox[1])/(box[3]-box[1]);gx=bbox[0]-sx*box[0];gy=bbox[1]-sy*box[1];xx,yy=np.meshgrid(np.arange(max(0,bbox[0]-5),min(960,bbox[2]+5)),np.arange(max(0,bbox[1]-5),min(720,bbox[3]+5)));target=src[yy,xx]
 def residual(v):
  x,y,sx,sy=v;pred=255-map_coordinates(ink,[(yy-y)/sy,(xx-x)/sx],order=1,mode='constant',cval=0,prefilter=False);return(pred-target).ravel()/30
 fit=least_squares(residual,[gx,gy,sx,sy],bounds=([gx-3,gy-3,psx*.83,psy*.83],[gx+3,gy+3,psx*1.2,psy*1.2]),max_nfev=80,diff_step=[.001,.001,.0001,.0001]);gx,gy,sx,sy=fit.x
 rows.append({'frame':f,'sourceBlackBBox':bbox,'sourceDarkestLuma':float(c.min()),'fitRMSE':float(np.sqrt(np.mean(residual(fit.x)**2))),'x':round(float((gx-px)/psx),6),'y':round(float((gy-py)/psy),6),'scaleX':round(float(sx/psx),6),'scaleY':round(float(sy/psy),6),'opacity':1,'globalPose':list(map(float,fit.x))})
patch={'type':'rect','id':'v18-dillion-paper-mask','x':25,'y':450,'width':155,'height':51,'fill':'#ffffff','start':998/30,'end':1036/30}
name={'type':'group','id':'v18-dillion-independent-name','start':998/30,'end':1036/30,'children':[{'type':'path','id':'v18-dillion-original-glyphs','d':path,'fill':'#'+('%02x'%round(black))*3,'semanticText':'Dillion'}],'keyframes':{k:[{'t':r['frame']/30,'value':r[k],'ease':'linear'}for r in rows]for k in ['x','y','scaleX','scaleY']}}
g['children'] += [patch,name]
(D/'scene-foodash-name-native-v18.json').write_text(json.dumps(s,indent=2)+'\n');(D/'dillion-name-v18-measurements.json').write_text(json.dumps({'staticWordSource':'Original accepted static Foodash document upper1032/name row1038','canonicalCrop':[38,464,122,492],'blackRGB':black,'trace':stats,'rows':rows,'opacityModel':'Solid word throughout; geometric pose measured independently. No opacity compensation for geometry/font mismatch.','unchanged':'Original product/status/price/subtotal assets, content, state, lifetimes and opacity tracks remain unchanged.'},indent=2)+'\n');print('word',box,'black',black,'frames',len(rows));print(rows[22:35])
