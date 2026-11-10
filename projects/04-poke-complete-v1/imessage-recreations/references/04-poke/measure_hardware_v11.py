"""Recover the isolated physical rail's horizontal camera from genuine material."""
from pathlib import Path
import json,numpy as np,hashlib
from PIL import Image
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d
p=Path(__file__).parent;src=p/'measurements-v8/decoded';ref=np.array(Image.open(src/'000340.png').convert('RGB')).astype(float);xs=np.arange(170);profile=np.concatenate([ref[20:100,:170],ref[950:1050,:170]],axis=0).mean(0);records=[]
for n in range(261,361):
 a=np.array(Image.open(src/f'{n:06}.png').convert('RGB')).astype(float);target=np.concatenate([a[20:100,:170],a[950:1050,:170]],axis=0).mean(0)
 def residual(q):
  tx,s,blur=q;sample=(xs-tx)/s;filtered=gaussian_filter1d(profile,max(.01,blur/s),axis=0);pred=np.stack([np.interp(sample,xs,filtered[:,ch],left=255,right=255)for ch in range(3)],axis=1);return(pred-target).ravel()
 fit=least_squares(residual,[0,1,.1],bounds=([-15,.72,0],[25,1.08,15]),max_nfev=100,loss='soft_l1',f_scale=8);records.append(dict(frame=n,time=n*1001/30000,x=float(fit.x[0]),scaleX=float(fit.x[1]),blur=float(fit.x[2]),profile_MAE=float(abs(residual(fit.x)).mean())))
# This is a single static hardware-only asset; source screen and UI are excluded.
a=ref[:,30:126].astype(np.uint8);alpha=np.ones(a.shape[:2],np.uint8)*255;alpha[(a.min(2)>250)]=0;rgba=np.dstack([a,alpha]);out=p/'assets/early-left-hardware-v11.png';Image.fromarray(rgba).save(out)
provenance=dict(source_frame=340,crop=[30,0,126,1080],output='assets/'+out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),mask='Only isolated side-hardware strip. White background pixels transparent; source screen and all UI lie outside this96px-wide crop. No complete source frame.',camera='Horizontal source-material profile fitting, no UI registration. Static artwork; independent editable transforms.');(p/'assets/early-left-hardware-v11-provenance.json').write_text(json.dumps(provenance,indent=2));(p/'measurements-v8/hardware-camera-v11.json').write_text(json.dumps(dict(method='Robust three-channel1Dhorizontal source-material registration using two button-free vertical spans. Camera maps static native340hardware world coordinates to each frame; no screen pixels in template.',measurements=records),indent=2));print(json.dumps(records[::10],indent=2))
