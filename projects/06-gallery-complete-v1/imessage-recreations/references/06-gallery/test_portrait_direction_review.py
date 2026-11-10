"""Test source-camera shutter anisotropy on a genuine independent portrait material."""
from pathlib import Path
import json,sys,copy,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
s=json.load(open(P/'local-fit.scene.json'));rp.register_fonts(s,str(BASE));f=614;g=next(n for n in s['layers']if n.get('semanticPhotoId')=='rene-final11-group-93'and n.get('start',0)<=f/30<n.get('end',99));state=rp.state(g,f/30);child=g['children'][0];ow,oh=child['width'],child['height'];dx=ow*state['scaleX'];dy=oh*state['scaleY'];N=256;pad=150;p=Path(child['src']);p=p if p.is_absolute()else BASE/p;im=Image.open(p).convert('RGBA').resize((N,N),Image.Resampling.LANCZOS);a=np.array(im,dtype=float)/255;a[:,:,:3]*=a[:,:,3,None];a=np.pad(a,((pad,pad),(pad,pad),(0,0)));fft=np.fft.rfft2(a,axes=(0,1));yy=np.fft.fftfreq(a.shape[0])[:,None];xx=np.fft.rfftfreq(a.shape[1])[None,:];ref=np.array(Image.open(P/'source/000614.png'),dtype=float);rows=[]
for angle in [-15,0,15]:
 for major in [20,35,50]:
  for minor in [5,15]:
   theta=np.deg2rad(angle);c=np.cos(theta);sn=np.sin(theta);u=xx*c+yy*sn;v=-xx*sn+yy*c;filt=np.exp(-2*np.pi**2*((major*N/dx)**2*u*u+(minor*N/dy)**2*v*v));arr=np.fft.irfft2(fft*filt[:,:,None],s=a.shape[:2],axes=(0,1));arr=np.clip(arr,0,1);arr[:,:,:3]/=np.maximum(1e-9,arr[:,:,3,None]);arr=np.clip(arr,0,1);file=P/f'shutter93-{angle}-{major}-{minor}.png';Image.fromarray(np.uint8(np.round(arr*255))).save(file)
   q=copy.deepcopy(s);n=next(z for z in q['layers']if z['id']==g['id']);n['children'][0].update(src=str(file),x=-pad,y=-pad,width=N+pad*2,height=N+pad*2);n['keyframes'].update({key:[dict(t=f/30,value=value)]for key,value in dict(scaleX=dx/N,scaleY=dy/N,blur=0).items()})
   for key in ('x','y','blur'):n['shadow'][key]*=N/ow
   out=rp.render(q,f/30,str(BASE));cost=float(abs(np.array(out,dtype=float)-ref).mean());r=dict(angle=angle,major=major,minor=minor,fullMAE=cost,file=str(file));rows.append(r);print(r,flush=True)
   if cost==min(x['fullMAE']for x in rows):out.save(P/'direction93-best.png');(P/'direction93-best.scene.json').write_text(json.dumps(q,indent=2))
(P/'direction93-tests.json').write_text(json.dumps(sorted(rows,key=lambda r:r['fullMAE']),indent=2))
