from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
spec=json.loads((R/'elements-candidate.json').read_text())
proof=json.loads((R/'scope-proof-candidate.json').read_text())
rows=[]
for frame in proof['controls']:
    name=f'{frame/30:.3f}.png'
    source=np.asarray(Image.open(R/'source-native'/f'source-{frame:04d}.png').convert('RGB')).astype(float)
    before=np.asarray(Image.open(R/'native-baseline'/name).convert('RGB')).astype(float)
    after=np.asarray(Image.open(R/'native-candidate'/name).convert('RGB')).astype(float)
    rows.append({'frame':frame,'changed':frame in spec['changedFrames'],'before':float(abs(source-before).mean()),'after':float(abs(source-after).mean()),'baselineCandidateMax':float(abs(before-after).max())})
changed=[row for row in rows if row['changed']]
report={'rows':rows,'changedNativeCount':len(changed),'meanBefore':float(np.mean([q['before']for q in changed])),'meanAfter':float(np.mean([q['after']for q in changed])),'regressions':[q for q in changed if q['after']>q['before']],'outsideControlsPixelIdentical':all(q['baselineCandidateMax']==0 for q in rows if not q['changed']),'definition':'Full native1920×1080 source RGB versus independent same-adapter genuine GSAP candidate and baseline at every changed frame plus adjacent controls.','limitations':'Original native vectors preserve semantic shapes; outline AA and compressed source texture remain. Five brief rich-link textures are bounded original product artwork with bitmap internal UI, optical blur, and independent native pose. No whole-frame or video layer.'}
(R/'native-metrics-candidate.json').write_text(json.dumps(report,indent=2))
for label,frames,box in [('copy',[769,770,772,778,779,919,920,926,927],None),('provider',[810,811,813,817,820,821,823,824,867,868,869,870],(300,0,900,1080)),('photo',[839,840,841,842,843,844,845],(300,400,1324,1080))]:
    width,height=1500,260*len(frames)
    canvas=Image.new('RGB',(width,height),'white')
    draw=ImageDraw.Draw(canvas)
    for index,frame in enumerate(frames):
        if label=='copy':
            crop=(1050,650,1700,1000)if frame<800 else(1220,620,1550,900)
        else:
            crop=box
        for column,(folder,name,caption)in enumerate([('source-native',f'source-{frame:04d}.png','source'),('native-baseline',f'{frame/30:.3f}.png','before'),('native-candidate',f'{frame/30:.3f}.png','after')]):
            image=Image.open(R/folder/name).convert('RGB').crop(crop)
            image.thumbnail((500,250))
            canvas.paste(image,(column*500,index*260))
            draw.text((column*500+2,index*260+2),f'{frame} {caption}',fill='red')
    canvas.save(R/f'{label}-native-contact.jpg')
print(json.dumps({k:v for k,v in report.items()if k!='rows'},indent=2))
