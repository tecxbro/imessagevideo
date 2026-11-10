from pathlib import Path
from PIL import Image
from scipy.ndimage import binary_erosion
import numpy as np,json,subprocess
R=Path('verification/encode-range');phases=json.loads((R/'inputs.json').read_text())['phases'];profiles=json.loads((R/'encode-results.json').read_text());patches=json.loads((R/'palette-patches.json').read_text());metrics=[];nativeReport=[]
def img(p):return np.asarray(Image.open(p).convert('RGB')).astype(np.int16)
for p in profiles:
 pp=[]
 for j,s in enumerate(phases):
  n=s['id'];a=img(R/'inputs'/f'{n}.png');b=img(R/'ffmpeg-decoded'/p['id']/f'{j+1:02d}.png');diff=b-a;absdiff=np.abs(diff);flat=np.all(a==253,2);fg=np.min(a,2)<246;color=(np.max(a,2)-np.min(a,2)>30);color=binary_erosion(color,iterations=2);q=dict(id=n,nativeMAE=float(absdiff.mean()),nativePSNR=float(20*np.log10(255/np.sqrt(np.mean(diff.astype(float)**2)))) if np.any(diff) else None,nativeForegroundMAE=float(absdiff[fg].mean()),nativeChromaticMAE=float(absdiff[color].mean()) if color.any() else None,nativeChromaticBiasRGB=np.mean(diff[color],0).tolist() if color.any() else None,nativeFlat253Pixels=int(flat.sum()),nativeFlat253DecodedMedianRGB=np.median(b[flat],0).tolist(),nativeFlat253MAE=float(absdiff[flat].mean()))
  if n!='palette':
   ref=img(R/'reference'/f'{n}.png');common=flat&np.all(ref==253,2);safe=binary_erosion(common,iterations=4);q.update(referenceMAE=float(np.abs(b-ref).mean()),rawNativeReferenceMAE=float(np.abs(a-ref).mean()),commonFlat253Pixels=int(common.sum()),commonFlat253MedianRGB=np.median(b[common],0).tolist(),commonFlat253MAE=float(absdiff[common].mean()),erodedCommonFlatPixels=int(safe.sum()),erodedCommonFlatMedianRGB=np.median(b[safe],0).tolist())
  else:
   values=[]
   for patch in patches:
    l,t,r,bot=patch['box'];pad=7 if patch['name'].startswith('gray') else 12;part=b[t+pad:bot-pad,l+pad:r-pad];target=np.array(patch['rgb']);values.append(dict(name=patch['name'],nativeRGB=patch['rgb'],medianRGB=np.median(part.reshape(-1,3),0).tolist(),mae=float(np.abs(part-target).mean()),meanBiasRGB=np.mean(part-target,axis=(0,1)).tolist()))
   q['patches']=values;q['grayPatchExactMedians']=sum(v['nativeRGB']==v['medianRGB'] for v in values[:256]);q['grayPatchMeanInteriorMAE']=float(np.mean([v['mae'] for v in values[:256]]));q['colorPatchMeanInteriorMAE']=float(np.mean([v['mae'] for v in values[256:]]))
  pp.append(q)
 # Decode unconverted original YUV plane samples, retaining yuvj420p for PC input.
 raw=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-filter_threads','1','-i',str(R/(p['id']+'.mp4')),'-vf','select=eq(n\\,2)','-frames:v','1','-f','rawvideo','-pix_fmt',p['ffprobe']['pix_fmt'],'-']);Y=np.frombuffer(raw,np.uint8,count=1920*1080).reshape(1080,1920);a=img(R/'inputs/535.png');flat=np.all(a==253,2);yValues,counts=np.unique(Y[flat],return_counts=True)
 metrics.append(dict(profile=p['id'],ffprobe=p['ffprobe'],filter=p['filter'],crf=p['crf'],bytes=p['bytes'],frames=pp,flat253EncodedYMedian=float(np.median(Y[flat])),flat253YHistogram=dict(zip(map(str,yValues.tolist()),counts.tolist()))))
(R/'ffmpeg-metrics.json').write_text(json.dumps(metrics,indent=2));print('profile 535native/535reference/flat253Median/grayExact/colorPatchMAE')
for p in metrics:
 x=p['frames'][0];pal=p['frames'][3];print(p['profile'],round(x['nativeMAE'],4),round(x['referenceMAE'],4),x['commonFlat253MedianRGB'],pal['grayPatchExactMedians'],round(pal['colorPatchMeanInteriorMAE'],4))
