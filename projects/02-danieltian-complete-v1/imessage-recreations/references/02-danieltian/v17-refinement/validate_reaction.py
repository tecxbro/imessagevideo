from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
ROOT=R.parents[2]
rows=[];contact=Image.new('RGB',(1200,200*8),'white');draw=ImageDraw.Draw(contact)
for index,frame in enumerate(range(815,823)):
    paths=[ROOT/'references/02-danieltian/final-midstate-fix/source-native'/f'source-{frame:04d}.png',ROOT/'outputs/02-danieltian/frames-gsap'/f'{frame:06d}.png',R/'reaction-native'/f'{frame/30:.3f}.png']
    images=[Image.open(path).convert('RGB')for path in paths]
    source,before,after=[np.asarray(image).astype('int16')for image in images]
    rows.append({'frame':frame,'before':float(abs(source-before).mean()),'after':float(abs(source-after).mean()),'baselineCandidateMax':int(abs(before-after).max())})
    for column,image in enumerate(images):
        view=image.crop((1240,0,1480,160)).resize((300,200));contact.paste(view,(column*400,index*200));draw.text((column*400,index*200),f'{frame} '+['source','before','after'][column],fill='red')
changed=[q for q in rows if 816<=q['frame']<=821]
report={'rows':rows,'meanBefore':float(np.mean([q['before']for q in changed])),'meanAfter':float(np.mean([q['after']for q in changed])),'regressions':[q for q in changed if q['after']>q['before']],'controlsPixelIdentical':all(q['baselineCandidateMax']==0 for q in rows if q['frame']in[815,822])}
(R/'reaction-native-metrics.json').write_text(json.dumps(report,indent=2));contact.save(R/'reaction-native-contact.jpg');print(json.dumps(report,indent=2))
