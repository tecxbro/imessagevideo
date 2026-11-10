"""Read-only registration of opaque visible hair/forehead, independent of disc71."""
from pathlib import Path
import sys,json,copy,numpy as np
from PIL import Image
from scipy import signal
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20'
sys.path.insert(0,str(R/'engines'));import render_pillow as rp
s=json.load(open(BASE/'scene.json'));old=next(n for n in s['layers']if n['id']=='rene-portrait-v18-614-79');source=np.asarray(Image.open(P/'source/000614.png').convert('RGB')).astype(float);target=source[450:1080,650:1920];u0,u1,v0,v1=.30,.70,.07,.23;rows=[]
for material in ['original','source622']:
    for D in range(1500,2101,100):
        for blur in [20,40,60,80]:
            actor=copy.deepcopy(old);actor.pop('keyframes',None);child=actor['children'][0];ow=child['width'];oh=child['height']
            if material=='source622':
                child.update(src=str(REF/'giant-material-v21/portrait79-source622-material.png'),width=512,height=512)
                for key in ['x','y','blur']:actor['shadow'][key]*=512/ow
            w=child['width'];h=child['height'];actor.update(x=-u0*D,y=-v0*D,scaleX=D/w,scaleY=D/h,start=0,end=1,blur=blur/(D/w));scene=dict(width=round((u1-u0)*D),height=round((v1-v0)*D),duration=1,fps=30,background='#ffffff',layers=[actor],gradients=[])
            template=np.asarray(rp.render(scene,0,str(BASE))).astype(float);hh,ww=template.shape[:2];count=hh*ww*3;kernel=np.ones((hh,ww));sums=sum(signal.fftconvolve(target[:,:,ch],kernel,mode='valid')for ch in range(3));energy=sum(signal.fftconvolve(target[:,:,ch]**2,kernel,mode='valid')for ch in range(3))-sums*sums/count;cc=template-template.mean();cov=sum(signal.fftconvolve(target[:,:,ch],cc[::-1,::-1,ch],mode='valid')for ch in range(3));score=cov/np.sqrt(np.maximum(1e-8,energy*(cc*cc).sum()));yy,xx=np.mgrid[:score.shape[0],:score.shape[1]];cx=650+xx-u0*D+D/2;cy=450+yy-v0*D+D/2;valid=(cx>=1150)&(cx<=1550)&(cy>=1250)&(cy<=1650);score[~valid]=-1;j,i=np.unravel_index(score.argmax(),score.shape);row=dict(material=material,diameter=D,blurWorld=blur,cx=float(650+i-u0*D+D/2),cy=float(450+j-v0*D+D/2),ncc=float(score[j,i]));rows.append(row)
        print(material,D,max(rows[-4:],key=lambda q:q['ncc']),flush=True)
rows.sort(key=lambda q:q['ncc'],reverse=True);(P/'actor79-registration-grid.json').write_text(json.dumps(rows,indent=2));print(rows[:8],flush=True)
