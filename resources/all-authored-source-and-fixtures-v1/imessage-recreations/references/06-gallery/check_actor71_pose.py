from pathlib import Path
import sys,copy,json,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20'
sys.path.insert(0,str(R/'engines'));import render_pillow as rp
s=json.load(open(BASE/'scene.json'));rp.register_fonts(s,str(BASE));a=np.asarray(Image.open(P/'source/000614.png').convert('RGB')).astype(float);rows=[]
for D,cx,cy,b in [(340,402,-21,12),(330,402,-16,12),(340,402,-20,8),(350,402,-25,12)]:
    q=copy.deepcopy(s);n=next(n for n in q['layers']if n['id']=='rene-portrait-v18-614-71');w=n['children'][0]['width'];h=n['children'][0]['height'];values=dict(x=cx-D/2,y=cy-D/2,scaleX=D/w,scaleY=D/h,blur=b/(D/w))
    n['keyframes'].update({k:[dict(t=614/30,value=v)]for k,v in values.items()});im=rp.render(q,614/30,str(BASE));im.save(P/f'actor71-pose-{D}-{b}.png');c=np.asarray(im).astype(float);r=dict(diameter=D,cx=cx,cy=cy,blur=b,fullMAE=float(abs(a-c).mean()),roiMAE=float(abs(a[:300,150:720]-c[:300,150:720]).mean()));rows.append(r);print(r,flush=True)
(P/'actor71-pose-check.json').write_text(json.dumps(rows,indent=2))
