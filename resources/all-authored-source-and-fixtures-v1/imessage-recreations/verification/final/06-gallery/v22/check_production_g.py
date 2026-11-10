from pathlib import Path
from PIL import Image
import json, hashlib, numpy as np
R=Path('/workspace/imessage-recreations')
D=R/'verification/final/06-gallery/v22'
O=R/'outputs/06-gallery'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
meta=json.load(open(O/'gsap.mp4.render.json'))
assert meta['sceneSHA256']==sha(O/'final-v22/scene.json')
cache=Path(meta['frameDirectory'])
old=json.load(open(O/'iterations/final-v21-before-v22/preservation.json'))['frames']
scope=json.load(open(D/'scope-exact-boundary.json'))
changed={n for a,b in scope['exactChangedRanges'] for n in range(a,b+1)}
actual=[]
for row in old:
    if sha(cache/f"{row['frame']:06d}.png")!=row['sha256']:
        actual.append(row['frame'])
assert actual==sorted(changed),(actual,sorted(changed))
rows=[]
for n in sorted(changed):
    a=np.asarray(Image.open(cache/f'{n:06d}.png'))
    b=np.asarray(Image.open(D/f'check-exact/{n/30:.3f}.png'))
    err=int(np.abs(a.astype(int)-b.astype(int)).max())
    rows.append({'frame':n,'maxChannelDeltaFromNativeReviewed':err})
assert all(r['maxChannelDeltaFromNativeReviewed']==0 for r in rows)
(D/'gsap-cache-and-review-proof.json').write_text(json.dumps({'sceneSHA256':meta['sceneSHA256'],'actualChangedFrames':actual,'outside1451SHA256Identical':True,'all32ReviewedNativePixelIdentical':True,'reviewDefinition':'Production candidate versus native-reviewed candidate, not a claim of source identity','rows':rows},indent=2))
print('production G32 exact reviewed pixels; outside1451byte-identical')
