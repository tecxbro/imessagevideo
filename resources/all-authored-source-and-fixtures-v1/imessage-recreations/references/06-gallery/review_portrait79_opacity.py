from pathlib import Path
import json,copy,sys,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20'
sys.path.insert(0,str(R/'engines'));import render_pillow as rp
s=json.load(open(BASE/'scene.json'));rp.register_fonts(s,str(BASE));n=next(n for n in s['layers']if n['id']=='rene-portrait-v18-614-71');w=n['children'][0]['width'];h=n['children'][0]['height'];v=dict(x=232,y=-191,scaleX=340/w,scaleY=340/h,blur=12/(340/w));n['keyframes'].update({k:[dict(t=614/30,value=x)]for k,x in v.items()});s['layers']=[n for n in s['layers']if n['id']!='rene-portrait-v18-614-79'];base_image=rp.render(s,614/30,str(BASE));base_image.save(P/'without-actor79.png');B=np.asarray(base_image).astype(float);S=np.asarray(Image.open(P/'source/000614.png').convert('RGB')).astype(float);C=np.asarray(Image.open(P/'combined-candidate-1.png').convert('RGB')).astype(float);D=C-B;T=S-B;mask=(np.max(abs(D),axis=2)>15);mask[:400]=False;mask[:,:450]=False;alpha=float(np.clip((T[mask]*D[mask]).sum()/max(1,(D[mask]**2).sum()),0,1));rows=[]
for a in [alpha,.7,.8,.9,1]:
    out=B+a*D;mae=float(abs(S-out).mean());rows.append(dict(opacity=a,fullMAE=mae));print(rows[-1],flush=True);Image.fromarray(np.clip(out,0,255).round().astype('uint8')).save(P/f'actor79-opacity-{a:.4f}.png')
(P/'actor79-opacity-fit.json').write_text(json.dumps(rows,indent=2))
