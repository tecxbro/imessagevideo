from pathlib import Path
import sys,json,copy,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20'
sys.path.insert(0,str(R/'engines'));import render_pillow as rp
s=json.load(open(BASE/'scene.json'));rp.register_fonts(s,str(BASE));a=np.asarray(Image.open(P/'source/000614.png').convert('RGB')).astype(float);rows=[]
cases=[('original',1600,1358,1420,60),('source622',1600,1350,1402,60),('source622',1500,1352,1358,60),('source622',1700,1348,1446,60),('source622',1600,1352,1390,80),('source622',1702.5381495797046,1354.5383570615295,1458.6903499392429,59.35123220801482)]
for index,(material,D,cx,cy,blur)in enumerate(cases):
    q=copy.deepcopy(s);n=next(n for n in q['layers']if n['id']=='rene-portrait-v18-614-71');w=n['children'][0]['width'];h=n['children'][0]['height'];values=dict(x=402-170,y=-21-170,scaleX=340/w,scaleY=340/h,blur=12/(340/w));n['keyframes'].update({k:[dict(t=614/30,value=v)]for k,v in values.items()})
    n=next(n for n in q['layers']if n['id']=='rene-portrait-v18-614-79');child=n['children'][0];oldw=child['width']
    if material=='source622':
        child.update(src=str(REF/'giant-material-v21/portrait79-source622-material.png'),width=512,height=512)
        for k in ['x','y','blur']:n['shadow'][k]*=512/oldw
    w=child['width'];h=child['height'];values=dict(x=cx-D/2,y=cy-D/2,scaleX=D/w,scaleY=D/h,blur=blur/(D/w));n['keyframes'].update({k:[dict(t=614/30,value=v)]for k,v in values.items()});im=rp.render(q,614/30,str(BASE));im.save(P/f'combined-candidate-{index}.png');c=np.asarray(im).astype(float);r=dict(index=index,material=material,D=D,cx=cx,cy=cy,blur=blur,fullMAE=float(abs(a-c).mean()),heroROI=float(abs(a[450:,450:]-c[450:,450:]).mean()));rows.append(r);print(r,flush=True)
(P/'combined-candidate-metrics.json').write_text(json.dumps(rows,indent=2))
