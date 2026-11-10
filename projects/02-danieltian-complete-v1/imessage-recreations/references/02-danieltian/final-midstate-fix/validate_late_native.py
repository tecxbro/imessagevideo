from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
extra=json.loads((R/'birth-extra-source/mapping.json').read_text())
spec=json.loads((R/'late-birth-elements-candidate.json').read_text())
rows=[]
for frame in range(900,959):
    if str(frame)in extra:path=Path(extra[str(frame)])
    else:path=R/'source-native'/f'source-{frame:04d}.png'
    source=np.asarray(Image.open(path).convert('RGB')).astype('int16')
    before=np.asarray(Image.open(R/'late-baseline-native'/f'{frame:06d}.png').convert('RGB')).astype('int16')
    after=np.asarray(Image.open(R/'late-native-candidate'/f'{frame/30:.3f}.png').convert('RGB')).astype('int16')
    rows.append({'frame':frame,'changed':frame in spec['changedFrames'],'before':float(abs(source-before).mean()),'after':float(abs(source-after).mean()),'baselineCandidateMaximum':int(abs(before-after).max())})
changed=[q for q in rows if q['changed']]
report={'nativeFramesChecked':len(rows),'changedNativeFramesChecked':len(changed),'meanBefore':float(np.mean([q['before']for q in changed])),'meanAfter':float(np.mean([q['after']for q in changed])),'regressions':[q for q in changed if q['after']>q['before']],'unchangedNativeControlsPixelIdentical':all(q['baselineCandidateMaximum']==0 for q in rows if not q['changed']),'rows':rows,'definition':'Actual immutable G15 lossless GSAP cache versus genuine GSAP candidate; every corrected native state901–957 and adjacent controls900/958. Native1920×1080 full-frame RGB; no proxy or decoded candidate video.','limitations':'Native silhouette/circles/gradient approximate source optical sampling/compression. Label retains existing source-derived vector glyph geometry with measured offscreen poses; source AA/font weight residuals remain. No whole source frame/video layer.'}
(R/'late-native-metrics-candidate.json').write_text(json.dumps(report,indent=2))
for label,frames,crop in [('birth',[900,901,902,903,905,907,909,911,912],(1240,650,1570,1000)),('clip',[904,905,910,914,915,919,930,947,951,954,955,957,958],(540,0,740,100))]:
    out=Image.new('RGB',(1200,len(frames)*200),'white')
    draw=ImageDraw.Draw(out)
    for index,frame in enumerate(frames):
        if str(frame)in extra:path=Path(extra[str(frame)])
        else:path=R/'source-native'/f'source-{frame:04d}.png'
        for column,(path,caption)in enumerate([(path,'source'),(R/'late-baseline-native'/f'{frame:06d}.png','before'),(R/'late-native-candidate'/f'{frame/30:.3f}.png','after')]):
            image=Image.open(path).convert('RGB').crop(crop)
            image.thumbnail((400,190))
            out.paste(image,(column*400,index*200))
            draw.text((column*400,index*200),f'{frame} {caption}',fill='red')
    out.save(R/f'late-{label}-native-contact.jpg')
print(json.dumps({k:v for k,v in report.items()if k not in['rows','definition','limitations']},indent=2))
