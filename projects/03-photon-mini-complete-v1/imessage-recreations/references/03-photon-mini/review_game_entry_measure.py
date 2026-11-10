"""Source-only physical/view camera and presentation-dim measurement813–835."""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image
from scipy import ndimage,signal
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/03-game'
sys.path.insert(0,str(REF));from hardware_fit_v13 import fit_hardware
meta=json.load(open(REF/'montage-v13-changes.json'));poses=meta['poses'];sheets={q['frame']:q['panel_box'] for q in meta['game_measurements']}
template=Image.open(REF/'assets/peaks-review-chat/mini-review-chat-team-avatar.png').convert('RGB')
reference=json.load(open(R/'verification/fidelity-review/03-peaks/chat-measurements-initial.json'))
reference=next(r['hardware']for r in reference if r['frame']==804)

def zncc(image,guess,scale_hint):
    a=np.asarray(image).astype(float);best=None
    for scale in np.linspace(scale_hint*.80,scale_hint*1.08,25):
        w=round(template.width*scale);h=round(template.height*scale)
        c=np.asarray(template.resize((w,h),Image.Resampling.LANCZOS)).astype(float)
        gx,gy=guess;l=max(0,int(gx-30));t=max(0,int(gy-50));r=min(1920,int(gx+30+w+1));b=min(1080,int(gy+110+h+1))
        target=a[t:b,l:r];kernel=np.ones((h,w));count=h*w*3
        sums=sum(signal.fftconvolve(target[:,:,ch],kernel,mode='valid')for ch in range(3))
        energy=sum(signal.fftconvolve(target[:,:,ch]**2,kernel,mode='valid')for ch in range(3))-sums**2/count
        cc=c-c.mean();cov=sum(signal.fftconvolve(target[:,:,ch],cc[::-1,::-1,ch],mode='valid')for ch in range(3))
        score=cov/np.sqrt(np.maximum(1e-8,energy*(cc*cc).sum()))
        yy,xx=np.unravel_index(score.argmax(),score.shape);q=dict(x=l+int(xx),y=t+int(yy),scale=float(scale),ncc=float(score[yy,xx]))
        if best is None or q['ncc']>best['ncc']:best=q
    return best

records=[]
for f in range(813,836):
    image=Image.open(REF/'montage-native'/f'{f-794:03}.png').convert('RGB');a=np.asarray(image).astype(float);old=poses[str(f)]
    hardware=fit_hardware(image,old,y_radius=25,edge_bands=[(old['x']-35,old['x']+40),(old['x']+800*old['scaleX']-40,old['x']+800*old['scaleX']+35)])
    top=sheets[f][1];view=None;avatar=None
    if f<=823:
        ratio=hardware['scale']/reference['scale'];dx=hardware['x']-ratio*reference['x'];dy=hardware['y']-ratio*reference['y']
        avatar=zncc(image,(919*ratio+dx,75*ratio+dy),ratio)
        neutral=(a.max(2)-a.min(2)<6)&(a.mean(2)>70)&(a.mean(2)<253)
        region=np.zeros(neutral.shape,bool);region[max(0,round(hardware['y'])+5):min(1080,top),max(0,round(hardware['x'])):min(1920,round(hardware['x']+800*hardware['scale']))]=True
        labels,count=ndimage.label(neutral&region);sizes=np.bincount(labels.ravel());sizes[0]=0
        if len(sizes)>1 and sizes.max()>2000:
            index=sizes.argmax();mask=ndimage.binary_fill_holes(labels==index);yy,xx=np.where(mask);color=np.median(a[labels==index],axis=0)
            view=dict(box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],color=color.tolist(),opacity=float(np.mean(color)/253),area=int(mask.sum()))
    records.append(dict(frame=f,hardware=hardware,sheetTop=top,avatar=avatar,view=view))
    print(records[-1],flush=True)
(P/'presentation-measurements.json').write_text(json.dumps(records,indent=2))
