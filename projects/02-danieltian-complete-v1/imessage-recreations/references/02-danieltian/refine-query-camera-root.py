"""Fit the actual optical fade of one accepted static search UI component."""
from pathlib import Path
import numpy as np,json,subprocess
from PIL import Image
from scipy import ndimage,optimize
REF=Path(__file__).resolve().parent
scene=json.load(open(REF.parents[1]/'outputs/02-danieltian/final-v12/scene.json'));base=REF.parents[1]/'outputs/02-danieltian/final-v12';group=next(l for l in scene['layers'] if l['id']=='pb-result-search');layer=next(c for c in group['children'] if c['id']=='middle-query-after-18');image=np.array(Image.open(base/layer['src']).convert('RGB')).astype(float)
model=np.zeros((195,1190));x,y=405-385,248-225;model[y:y+148,x:x+1110]=np.clip((253-image.mean(2))/253,0,1)
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',"select='between(n,540,571)'",'-fps_mode','passthrough','-pix_fmt','rgb24','-threads','1','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE);rows=[]
for n in range(540,572):
 raw=p.stdout.read(1920*1080*3);assert len(raw)==1920*1080*3;rgb=np.frombuffer(raw,np.uint8).reshape(1080,1920,3)[225:420,385:1575].astype(float);target=np.clip((253-rgb.mean(2))/253,0,1)
 colored=rgb.max(2)-rgb.min(2)>18;labels,_=ndimage.label(colored,np.ones((3,3)));excluded=np.zeros(target.shape,bool)
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is not None and (labels[sl]==i+1).sum()>40:excluded|=ndimage.binary_fill_holes(labels==i+1)
 keep=~ndimage.binary_dilation(excluded,iterations=6)
 def fit(sigma,details=False):
  a=ndimage.gaussian_filter(model,sigma,mode='constant') if sigma>0 else model;v=a[keep];b=target[keep];opacity=float(np.clip((v*b).sum()/max((v*v).sum(),1e-9),0,1));error=float(np.mean((v*opacity-b)**2));return (error,opacity) if details else error
 opt=optimize.minimize_scalar(fit,bounds=(0,55),method='bounded') if n>550 else None;options=[(0,fit(0))]+([(float(opt.x),float(opt.fun))] if opt is not None else []);sigma,error=min(options,key=lambda r:r[1]);_,opacity=fit(sigma,True);rows.append(dict(frame=n,blur=sigma,opacity=opacity,neutralRMSE=253*error**.5))
p.stdout.close();assert p.wait()==0
(REF/'root-query-camera-patch.json').write_text(json.dumps(dict(scope=[[540,571]],rows=rows,notice='One accepted static original search UI component with independently measured native Gaussian blur and opacity tracks. The previous early fade/blur schedule was wrong; source remains sharp through550. Bitmap internal caption/magnifier/border are explicit, camera/lifetime/filter remain editable. No per-frame UI screenshot sequence.'),indent=2));print(rows)
