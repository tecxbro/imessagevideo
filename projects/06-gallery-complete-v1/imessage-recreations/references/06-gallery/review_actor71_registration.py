"""Read-only partial portrait registration from its fully visible lower half."""
from pathlib import Path
import sys,json,copy,numpy as np
from PIL import Image
from scipy import signal
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20'
sys.path.insert(0,str(R/'engines'));import render_pillow as rp
s=json.load(open(BASE/'scene.json'));old=next(n for n in s['layers']if n['id']=='rene-portrait-v18-614-71');st=rp.state(old,614/30);w=old['children'][0]['width'];h=old['children'][0]['height'];source=np.asarray(Image.open(P/'source/000614.png').convert('RGB')).astype(float);target=source[:350,100:750];rows=[]
for diameter in range(220,381,10):
    for blur in [0,4,8,12,20]:
        actor=copy.deepcopy(old);actor.pop('keyframes',None);actor.update(x=100,y=100,scaleX=diameter/w,scaleY=diameter/h,start=0,end=1,blur=blur/(diameter/w));scene=dict(width=diameter+200,height=diameter+300,duration=1,fps=30,background='#fdfdfd',layers=[actor],gradients=[])
        image=rp.render(scene,0,str(BASE));crop_top=round(100+diameter*.75);anchor=crop_top-100-diameter/2;template=np.asarray(image.crop((0,crop_top,diameter+200,100+diameter+80))).astype(float);hh,ww=template.shape[:2];count=hh*ww*3;kernel=np.ones((hh,ww));sums=sum(signal.fftconvolve(target[:,:,ch],kernel,mode='valid')for ch in range(3));energy=sum(signal.fftconvolve(target[:,:,ch]**2,kernel,mode='valid')for ch in range(3))-sums*sums/count;cc=template-template.mean();cov=sum(signal.fftconvolve(target[:,:,ch],cc[::-1,::-1,ch],mode='valid')for ch in range(3));score=cov/np.sqrt(np.maximum(1e-8,energy*(cc*cc).sum()));yy,xx=np.mgrid[:score.shape[0],:score.shape[1]];cx=100+xx+ww/2;cy=yy-anchor;valid=(cx>=350)&(cx<=450)&(cy>=-80)&(cy<=80);score[~valid]=-1;j,i=np.unravel_index(score.argmax(),score.shape);row=dict(diameter=diameter,blurWorld=blur,cx=float(100+i+ww/2),cy=float(j-anchor),ncc=float(score[j,i]));rows.append(row)
    print('diameter',diameter,'best',max(rows[-5:],key=lambda q:q['ncc']),flush=True)
rows.sort(key=lambda q:q['ncc'],reverse=True);(P/'actor71-registration-quarter.json').write_text(json.dumps(rows,indent=2));print(rows[:8],flush=True)
