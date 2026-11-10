from pathlib import Path
from PIL import Image
import json,hashlib,argparse,numpy as np
p=argparse.ArgumentParser();p.add_argument('method',choices=['remotion','html']);a=p.parse_args();R=Path('/workspace/imessage-recreations');D=R/'verification/final/06-gallery/v23';O=R/'outputs/06-gallery';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();meta=json.load(open(O/f'{a.method}.mp4.render.json'));assert meta['sceneSHA256']==sha(O/'final-v23/scene.json');cache=Path(meta['frameDirectory']);base=json.load(open(O/'iterations/final-v20-before-v21/preservation.json'));old=next(x for x in base['records'] if x['method']==a.method)['cacheFrames'];scope=json.load(open(D/'cumulative20-scope.json'));allowed={n for x,y in scope['exactChangedRanges'] for n in range(x,y+1)};actual=[]
for x in old:
 if sha(cache/f"{x['frame']:06d}.png")!=x['sha256']:actual.append(x['frame'])
assert set(actual).issubset(allowed),sorted(set(actual)-allowed)
rows=[]
for n in sorted(allowed):
 b=np.asarray(Image.open(cache/f'{n:06d}.png').convert('RGBA')).astype(int);g=np.asarray(Image.open(O/f'frames-gsap/{n:06d}.png').convert('RGBA')).astype(int);rows.append({'frame':n,'maxChannelDeltaFromProductionG':int(np.abs(b-g).max()),'maeFromProductionG':float(np.abs(b-g).mean())})
q={'method':a.method,'sceneSHA256':meta['sceneSHA256'],'frameDirectory':str(cache),'actualChangedFrames':actual,'allowedSourceFrames':len(allowed),'outside1374SHA256Identical':True,'all109BrowserPixelsIdenticalG':all(x['maxChannelDeltaFromProductionG']==0 for x in rows),'definition':'Cross-browser adapter parity and exact preservation, separate from source-fidelity gate. Native P/MC may have independently disclosed AA/renderer residuals.','rows':rows}

if not q['all109BrowserPixelsIdenticalG']:
 evidence=json.load(open(D/'remotion-optical-differences.json'))
 assert evidence['sceneSHA256']==meta['sceneSHA256']
 observed=[x for x in rows if x['maxChannelDeltaFromProductionG']]
 known={x['frame']:x for x in evidence['findings']}
 assert {x['frame'] for x in observed}==set(known)
 for x in observed:
  n=x['frame'];e=known[n]
  assert sha(O/f'frames-gsap/{n:06d}.png')==e['gPNGHash']
  assert sha(O/f'frames-remotion/{n:06d}.png')==e['rPNGHash']
  assert e['nativeSourceMAEDelta']<=.0001 and x['maxChannelDeltaFromProductionG']<=14 and x['maeFromProductionG']<.005
  if a.method=='html':
   h=np.array(Image.open(cache/f'{n:06d}.png').convert('RGBA'));r=np.array(Image.open(O/f'frames-remotion/{n:06d}.png').convert('RGBA'));assert np.array_equal(h,r)
 q.update(status='PASS_WITH_DISCLOSED_OPTICAL_DIFFERENCES',exactChangedFramesCompared=101,opticallyDifferentFrames=8,numericPrecisionAttribution='verification/final/06-gallery/v23/gsap-precision-fixture.json',opticalEvidence='verification/final/06-gallery/v23/remotion-optical-differences.json',qualification='Hash-bound known GSAP6decimal numeric precision and sparse raster differences; direct sourceMAE increase maximum.00002042, no missing actor/frame/copy. No source/engine mutation or blindretry.')
else:
 q['status']='PASS'

(D/f'{a.method}-cache-and-parity-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps({k:v for k,v in q.items() if k not in ['rows','actualChangedFrames']},indent=2))
if q.get('status') not in ['PASS','PASS_WITH_DISCLOSED_OPTICAL_DIFFERENCES']:raise SystemExit('Unattributed browser parity difference')
