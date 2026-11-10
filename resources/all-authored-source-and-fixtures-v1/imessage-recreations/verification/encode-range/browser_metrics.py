from pathlib import Path
from PIL import Image
from scipy.ndimage import binary_erosion
import numpy as np,json
R=Path('verification/encode-range');phases=json.loads((R/'inputs.json').read_text())['phases'];patches=json.loads((R/'palette-patches.json').read_text());cache={}
def image(p):return np.asarray(Image.open(p).convert('RGB')).astype(np.int16)
def medianRGB(x):return [float(np.median(x[:,k])) for k in range(3)]
for phase in phases:
 n=phase['id'];a=image(R/'inputs'/f'{n}.png');ref=image(R/'reference'/f'{n}.png') if n!='palette' else None;flat=np.all(a==253,2);common=flat&np.all(ref==253,2) if ref is not None else flat;color=binary_erosion(a.max(2)-a.min(2)>30,iterations=2);cache[n]=(a,ref,flat,common,color)
reports=[]
for row in json.loads((R/'browser-final-results.json').read_text()):
 out=dict(profile=row['profile'],flags=row['flagSet'],browser=row.get('browserVersion'),error=row.get('error'),frames=[],playback=row.get('playback'),metadata=row.get('metadata'))
 for sample in row.get('samples',[]):
  n=sample['id'];a,ref,flat,common,color=cache[n];b=image(R/'browser-final-decoded'/row['flagSet']/row['profile']/f'{n}.png');diff=b-a;q=dict(id=n,nativeMAE=float(np.abs(diff).mean()),nativeChromaticMAE=float(np.abs(diff[color]).mean()) if color.any() else None,nativeFlat253MedianRGB=medianRGB(b[flat]),commonFlat253MedianRGB=medianRGB(b[common]),commonFlat253Pixels=int(common.sum()),browserMediaTime=sample['mediaTime'],targetNativeFrame=sample['wantedNativeFrame'])
  if ref is not None:q.update(referenceMAE=float(np.abs(b-ref).mean()),nativeRawReferenceMAE=float(np.abs(a-ref).mean()))
  else:
   vals=[]
   for patch in patches:
    l,t,r,bot=patch['box'];pad=7 if patch['name'].startswith('gray') else 12;part=b[t+pad:bot-pad,l+pad:r-pad].reshape(-1,3);target=np.array(patch['rgb']);vals.append(dict(name=patch['name'],nativeRGB=patch['rgb'],medianRGB=medianRGB(part),mae=float(np.abs(part-target).mean())))
   q.update(patches=vals,grayPatchExactMedians=sum(p['nativeRGB']==p['medianRGB'] for p in vals[:256]),grayPatchMeanInteriorMAE=float(np.mean([p['mae'] for p in vals[:256]])),colorPatchMeanInteriorMAE=float(np.mean([p['mae'] for p in vals[256:]])))
  out['frames'].append(q)
 reports.append(out)
(R/'browser-final-metrics.json').write_text(json.dumps(reports,indent=2));print('flag profile native535MAE native535median grayExact colorPatchMAE playbackDrops')
for p in reports:
 x=p['frames'][0];pal=next((q for q in p['frames'] if q['id']=='palette'),{});play=p.get('playback') or{};print(p['flags'],p['profile'],round(x['nativeMAE'],4),x['commonFlat253MedianRGB'],pal.get('grayPatchExactMedians'),round(pal.get('colorPatchMeanInteriorMAE',0),4),play.get('playbackDroppedDelta'))
