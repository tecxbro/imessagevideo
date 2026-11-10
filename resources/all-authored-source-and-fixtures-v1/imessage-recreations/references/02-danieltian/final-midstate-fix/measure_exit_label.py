from pathlib import Path
import json,sys,numpy as np
sys.path.insert(0,'/tmp/imessage-food-cv');import cv2
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
mapping=json.load(open(R/'birth-extra-source/mapping.json'))
source855=np.asarray(Image.open(R/'source-native/source-0855.png').convert('RGB'))
template=np.clip(253-source855[421:456,531:643].mean(2),0,253).astype('uint8')
rows=[];out=Image.new('RGB',(1400,125*12),'white');draw=ImageDraw.Draw(out)
for frame in range(947,959):
    source=np.asarray(Image.open(mapping[str(frame)]).convert('RGB'))
    native=np.asarray(Image.open(R.parents[2]/'outputs/02-danieltian/frames-gsap'/f'{frame:06d}.png').convert('RGB'))
    search=np.clip(253-source[:150,480:800].mean(2),0,253).astype('uint8')
    best=(-1,None)
    for scale in np.linspace(.86,.92,13):
        pattern=cv2.resize(template,None,fx=float(scale),fy=float(scale),interpolation=cv2.INTER_CUBIC)
        result=cv2.matchTemplate(search,pattern,cv2.TM_CCOEFF_NORMED)
        _,score,_,location=cv2.minMaxLoc(result)
        if score>best[0]:best=(score,[location[0]+480,location[1],scale])
    rows.append({'frame':frame,'sourceFullLabelCorrelation':float(best[0]),'matchedPositionAndScale':best[1]})
    for column,image in enumerate([source,native]):
        view=Image.fromarray(image).crop((480,0,1180,125));out.paste(view,(column*700,(frame-947)*125));draw.text((column*700,(frame-947)*125),str(frame),fill='red')
out.save(R/'provider-label-exit-contact.jpg');(R/'provider-label-exit-measurements.json').write_text(json.dumps(rows,indent=2));print(rows)
