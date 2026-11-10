from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/02-capsule-collapse';cap=json.load(open(P/'check-v1/capture.json'));rows=[];panels=[]
for frame in cap['frameIndices']:
    source=Image.open(P/'source'/f'{frame-521:04d}.png').convert('RGB')
    before=Image.open(R/'outputs/02-danieltian/frames-gsap'/f'{frame:06d}.png').convert('RGB')
    after=Image.open(P/'check-v1'/f'{frame/30:.3f}.png').convert('RGB')
    s=np.array(source).astype(float);b=np.array(before).astype(float);a=np.array(after).astype(float)
    row=dict(frame=frame,before_mae=float(abs(s-b).mean()),after_mae=float(abs(s-a).mean()),baseline_candidate_pixels_identical=np.array_equal(b,a))
    for name,box in [('search',[400,240,1560,410]),('capsules',[650,410,1290,920])]:
        x0,y0,x1,y1=box
        row[name+'_before_mae']=float(abs(s[y0:y1,x0:x1]-b[y0:y1,x0:x1]).mean())
        row[name+'_after_mae']=float(abs(s[y0:y1,x0:x1]-a[y0:y1,x0:x1]).mean())
    rows.append(row)
    panel=Image.new('RGB',(1920,384),'white');drawing=ImageDraw.Draw(panel)
    for index,picture in enumerate([source,before,after]):
        picture.thumbnail((640,360));panel.paste(picture,(index*640,24));drawing.text((index*640+3,3),str(frame)+' '+['Source','Nativev12','Correctionv1'][index],fill='red')
    panels.append(panel)
sheet=Image.new('RGB',(1920,len(panels)*384),'white')
for index,panel in enumerate(panels):sheet.paste(panel,(0,index*384))
sheet.save(P/'comparison-v1.jpg',quality=95);(P/'native-metrics-v1.json').write_text(json.dumps(rows,indent=2));print(rows)
