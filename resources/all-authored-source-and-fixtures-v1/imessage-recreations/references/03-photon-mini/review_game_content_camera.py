"""Register actual visible poster independently of the presenting header camera."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import signal
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/03-game'
spec=json.load(open(REF/'game-entry-review-elements.json'));out=[]
poster=Image.open(REF/'assets/peaks-review-chat/mini-review-jump-card.png').convert('RGB')
for f in range(813,818):
    root=next(n for n in spec['insert_before']['p03-371']if n['id']==f'game-review-frame-{f}')
    group=next(n for n in root['children']if n['id']==f'game-review-whole-view-dim-{f}')['children'][1]
    jump=next(n for n in group['children']if 'mini-review-chat-jump-812'in n['id'])
    guess=(group['x']+group['scaleX']*jump['x'],group['y']+group['scaleY']*jump['y']);hint=group['scaleX']*jump['scaleX']
    height=200
    if f==816:height=160
    if f==817:height=60
    template=poster.crop((0,0,poster.width,height));a=np.asarray(Image.open(REF/'montage-native'/f'{f-794:03}.png').convert('RGB')).astype(float);best=None
    for scale in np.linspace(hint*.97,hint*1.02,21):
        w=round(template.width*scale);h=round(template.height*scale);c=np.asarray(template.resize((w,h),Image.Resampling.LANCZOS)).astype(float);l=round(guess[0]-12);t=round(guess[1]-16);target=a[t:round(guess[1]+16+h+1),l:round(guess[0]+12+w+1)];count=h*w*3;kernel=np.ones((h,w));sums=sum(signal.fftconvolve(target[:,:,ch],kernel,mode='valid')for ch in range(3));energy=sum(signal.fftconvolve(target[:,:,ch]**2,kernel,mode='valid')for ch in range(3))-sums*sums/count;cc=c-c.mean();cov=sum(signal.fftconvolve(target[:,:,ch],cc[::-1,::-1,ch],mode='valid')for ch in range(3));score=cov/np.sqrt(np.maximum(1e-8,energy*(cc*cc).sum()));yy,xx=np.unravel_index(score.argmax(),score.shape);q=dict(frame=f,x=l+int(xx),y=t+int(yy),scale=float(scale),ncc=float(score[yy,xx]),templateHeight=height)
        if best is None or q['ncc']>best['ncc']:best=q
    q=best['scale']/jump['scaleX'];best['camera']=dict(scale=q,x=best['x']-q*jump['x'],y=best['y']-q*jump['y']);out.append(best);print(best,flush=True)
(P/'content-camera.json').write_text(json.dumps(out,indent=2))
