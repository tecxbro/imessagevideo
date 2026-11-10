from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
P=Path(__file__).parent;B=P/'early-v13-measure';a=np.asarray(Image.open(P/'assets/phone-hardware.png').convert('RGBA')).astype(float);gray=a[:,:,:3].mean(2);yy,xx=np.mgrid[:a.shape[0],:a.shape[1]];gy=np.abs(ndimage.sobel(gray,axis=0))/8;mask=(a[:,:,3]>245)&(gray<245)&((xx<14)|(xx>a.shape[1]-15))&(gy>12);y,x=np.where(mask);v=gray[mask];x=x*800/a.shape[1];y=y*1658/a.shape[0]
r=json.loads((B/'camera-fit-all.json').read_text());res=[]
for rec in r:
 f=rec['frame'];s=rec['scale'];tx=rec['x'];old=rec['old'][2]
 if f in [214,254,287] or 343<=f<=357:s=(rec['right']-rec['left'])/768;tx=rec['left']-16*s
 image=np.asarray(Image.open(B/'source'/f'{f-48:04d}.png').convert('RGB')).mean(2);ys=np.arange(old-220,old+221,2.);xp=np.broadcast_to((tx+s*x)[None,:]/2,(len(ys),len(x)));yp=(ys[:,None]+s*y[None,:])/2;inside=(xp>1)&(xp<959)&(yp>1)&(yp<539);sample=ndimage.map_coordinates(image,[yp,xp],order=1,mode='nearest');diff=np.minimum(abs(sample-v[None,:]),90);scores=(diff*inside).sum(1)/np.maximum(15,inside.sum(1));scores[inside.sum(1)<15]=100;index=int(scores.argmin());rec['hardwareY']=float(ys[index]);rec['hardwareCost']=float(scores[index]);rec['hardwareVisibleSamples']=int(inside[index].sum());res.append(rec)
 if f in [83,98,150,177,205,211,214,220,240,254,287,300,311,334,350,355,357,358,390]:print(f,'poseY',round(rec['y'],1),'hardwareY',round(rec['hardwareY'],1),'cost',round(rec['hardwareCost'],1),'samples',rec['hardwareVisibleSamples'],flush=True)
(B/'camera-fit-hardware-y.json').write_text(json.dumps(res,indent=2)+'\n')
