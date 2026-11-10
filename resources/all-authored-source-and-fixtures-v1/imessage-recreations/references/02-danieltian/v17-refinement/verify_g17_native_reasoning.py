from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[2];D=ROOT/'outputs/02-danieltian/frames-gsap';rows=[]
for f in range(271,376):
    p=D/f'{f:06d}.png';source=np.asarray(Image.open(R/'reasoning-source'/f'source-{f:04d}.png').convert('RGB')).astype('int16');baseline=np.asarray(Image.open(R/'reasoning-baseline'/f'{f:06d}.png').convert('RGB')).astype('int16');actual=np.asarray(Image.open(p).convert('RGB')).astype('int16');accepted=np.asarray(Image.open(R/'reasoning-dense-native'/f'{f/30:.3f}.png').convert('RGB')).astype('int16')
    rows.append({'frame':f,'before':float(abs(source-baseline).mean()),'actualAfter':float(abs(source-actual).mean()),'productionVsAcceptedMax':int(abs(actual-accepted).max()),'productionVsAcceptedMAE':float(abs(actual-accepted).mean()),'PNG_SHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'productionVsBaselineMax':int(abs(actual-baseline).max())})
changed=[r for r in rows if r['frame']not in[271,373,375]]
report={'sceneSHA256':'09df288bd09aee0ec33bca014dc4598f966ffa52b36cb3489c685fb21a43c74a','rows':rows,'all102Improve':all(r['actualAfter']<r['before']for r in changed),'regressions':[r for r in changed if r['actualAfter']>=r['before']],'controlsExact':all(r['productionVsBaselineMax']==0 for r in rows if r['frame']in[271,373,375]),'productionNativeMeanBefore':float(np.mean([r['before']for r in changed])),'productionNativeMeanAfter':float(np.mean([r['actualAfter']for r in changed])),'productionAllPixelIdenticalToAccepted':all(r['productionVsAcceptedMax']==0 for r in rows),'maxProductionVsAccepted':max(r['productionVsAcceptedMax']for r in rows)}
assert report['all102Improve']and report['controlsExact'];(R/'production-native-reasoning-v17.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='rows'},indent=2))
