from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
ROOT=R.parents[2]
scene=ROOT/'outputs/02-danieltian/final-v15/scene.json'
sha=hashlib.sha256(scene.read_bytes()).hexdigest()
assert sha=='ff896ac0fe8ab53b2301d7f55349438cc2efe1d2c2d088730c36a02588302a25'
proof=json.loads((R/'scope-proof-candidate.json').read_text())
rows=[]
for frame in proof['controls']:
    actual=ROOT/'outputs/02-danieltian/frames-gsap'/f'{frame:06d}.png'
    expected=R/'native-candidate'/f'{frame/30:.3f}.png'
    a=np.asarray(Image.open(actual).convert('RGB')).astype('int16')
    b=np.asarray(Image.open(expected).convert('RGB')).astype('int16')
    delta=abs(a-b)
    rows.append({'frame':frame,'pixelIdentical':bool(not delta.any()),'mae':float(delta.mean()),'maximumChannelDifference':int(delta.max()),'productionPNG_SHA256':hashlib.sha256(actual.read_bytes()).hexdigest(),'acceptedNativePNG_SHA256':hashlib.sha256(expected.read_bytes()).hexdigest()})
report={'sceneSHA256':sha,'nativeFramesChecked':len(rows),'allPixelIdentical':all(q['pixelIdentical']for q in rows),'rows':rows,'definition':'Actual complete retained GSAP production PNGs versus accepted native checkpoint PNGs at every corrected state and all controls. No decoded-video approximation involved.'}
(R/'production-native-parity-v15.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items()if k!='rows'}))
