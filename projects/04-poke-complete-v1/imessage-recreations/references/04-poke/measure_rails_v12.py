"""Measure isolated genuine side-hardware profiles independently of screen UI."""
from pathlib import Path
from PIL import Image
import json,numpy as np,hashlib
from scipy.optimize import minimize_scalar
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v11/scene.json').read_text());g=next(l for l in s['layers']if l['id']=='p0109');fps=s['fps'];d=p/'measurements-v8/decoded'
def load(n):return np.array(Image.open(d/f'{n:06}.png').convert('RGB')).astype(np.float32)
def profile(a):return np.concatenate([a[20:100],a[950:1050]],axis=0).mean(0)
def runs(values):
    out=[]
    for x in values:
        if out and x==out[-1][-1]+1:out[-1].append(int(x))
        else:out.append([int(x)])
    return out
leftref=profile(load(340));rightimage=load(397);rightref=profile(rightimage);refhi=min(r[0]for r in runs(np.where(rightimage[500].max(1)<80)[0])if r[0]>1250 and len(r)>4);crop=[refhi,0,min(1440,refhi+80),1080];rgb=rightimage[:,crop[0]:crop[2]].astype(np.uint8);alpha=np.ones(rgb.shape[:2],np.uint8)*255;alpha[rgb.min(2)>250]=0;asset=p/'assets/early-right-hardware-v12.png';Image.fromarray(np.dstack([rgb,alpha])).save(asset);rows=[];lastleft=.75;lastright=1.0;xs=np.arange(1440)
for n in range(361,480):
    a=load(n);target=profile(a);rr=runs(np.where(a[500].max(1)<80)[0]);left=[v for v in rr if v[0]<110];right=[v for v in rr if v[0]>1250 and len(v)>0];hi=min((v[0]for v in right),default=None);t=n/fps;expected=at(g,'x',t)+92*at(g,'scaleX',t);chosen=min(left,key=lambda r:abs(r[-1]+1-expected))if left else None;lo=chosen[-1]+1 if chosen and abs(chosen[-1]+1-expected)<12 else None;row=dict(frame=n,time=t)
    if lo is None:lo=2*716.5-hi if hi is not None else at(g,'x',t)+92*at(g,'scaleX',t)
    def fit(ref,anchor,target_anchor,indices,bounds):
        def loss(scale):
            tx=target_anchor-anchor*scale;q=(indices-tx)/scale;prediction=np.stack([np.interp(q,xs,ref[:,ch],left=255,right=255)for ch in range(3)],1);error=np.minimum(abs(prediction-target[indices]),60);return float((error*error).mean())
        r=minimize_scalar(loss,bounds=bounds,method='bounded',options={'xatol':.0001});return float(r.x),float(r.fun)
    if lo>=30:
        indices=np.arange(min(180,max(1,int(lo+6))))
        lastleft,loss=fit(leftref,124,lo,indices,(.45,1.3))
    else:loss=None
    row.update(left_x=lo-124*lastleft,left_scale=lastleft,left_loss=loss,source_left_inner=lo)
    if hi is not None:
        if 1440-hi>=60:lastright,rloss=fit(rightref,refhi,hi,np.arange(max(0,hi-3),1440),(.55,1.6))
        else:rloss=None
        row.update(right_x=hi-refhi*lastright,right_scale=lastright,right_opacity=1,right_loss=rloss,source_right_inner=hi)
    else:row.update(right_x=1440-refhi*lastright,right_scale=lastright,right_opacity=0)
    rows.append(row)
(p/'measurements-v8/rail-profiles-v12.json').write_text(json.dumps(dict(method='Independent isolated physical side material. Source row500 inner edges anchor the observed boundary; bounded native RGB profiles on two button-free spans fit rail thickness. Once clipped to an information-poor strip, retain its last observed scale and measured surviving edge. No screen/text pixels in artwork.',left_asset='assets/early-left-hardware-v11.png',left_crop=[30,0,126,1080],right_asset='assets/'+asset.name,right_crop=crop,measurements=rows),indent=2));(p/'assets/early-right-hardware-v12-provenance.json').write_text(json.dumps(dict(source_frame=397,crop=crop,asset='assets/'+asset.name,sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),screen='All source screen pixels left of the inner black edge are excluded. White background pixels are transparent. One static genuine hardware-only strip.'),indent=2));print('Measured',len(rows),'native rail poses',crop)
