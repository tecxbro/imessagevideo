"""Read-only actor71 blur attribution against actual frame614; canonical untouched."""
from pathlib import Path
import json,sys,copy,numpy as np
from PIL import Image,ImageDraw
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20'
sys.path.insert(0,str(R/'engines'));import render_pillow as rp
scene=json.load(open(BASE/'scene.json'));rp.register_fonts(scene,str(BASE))
f=614;t=f/30;source=np.asarray(Image.open(P/'source'/f'{f:06}.png').convert('RGB')).astype(float)
actor=next(n for n in scene['layers']if n['id']=='rene-portrait-v18-614-71');original=rp.state(actor,t);scale=original['scaleX']
rows=[];panels=[]
for blur in [53.30653124543678,0,2,4,8,12,20,30]:
    trial=copy.deepcopy(scene);node=next(n for n in trial['layers']if n['id']==actor['id']);node['keyframes']['blur']=[dict(t=t,value=blur/scale,ease='hold')]
    image=rp.render(trial,t,str(BASE));candidate=np.asarray(image).astype(float);roi=(slice(0,300),slice(150,720))
    q=dict(blurWorld=blur,fullMAE=float(abs(source-candidate).mean()),actor71ROI=float(abs(source[roi]-candidate[roi]).mean()),actor71ROIContribution=float(abs(source[roi]-candidate[roi]).sum()/(1920*1080*3)))
    rows.append(q);image.save(P/f'actor71-blur-{blur:.2f}.png');panels.append((blur,image.crop((150,0,720,300))))
    print(q,flush=True)
(P/'actor71-blur-grid.json').write_text(json.dumps(rows,indent=2))
sheet=Image.new('RGB',(1140,len(panels)//2*330),'white');draw=ImageDraw.Draw(sheet)
for i,(blur,image)in enumerate(panels):sheet.paste(image,((i%2)*570,(i//2)*330+25));draw.text(((i%2)*570,(i//2)*330+4),f'World blur {blur:.2f}',fill='black')
sheet.save(P/'actor71-blur-grid.jpg',quality=93)
