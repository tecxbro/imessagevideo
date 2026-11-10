"""Use absolute opaque grayscale bands, not below-1/255 stacked alphas."""
from pathlib import Path
import json,importlib.util,time
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;spec=json.loads((R/'elements-refined.json').read_text());data=json.loads((R/'dense-measurements.json').read_text());s=importlib.util.spec_from_file_location('trace',R.parent/'trace_glyphs.py');trace=importlib.util.module_from_spec(s);s.loader.exec_module(trace);ledger=[];start=time.monotonic()
for n in spec['layers']:
 if not n['id'].startswith('pb14-query-'):continue
 f=round(n['start']*30);src=np.asarray(Image.open(R/'source-native'/f'{f:06d}.png').convert('RGB')).astype(float);L,T,RR,B=350,230,1550,470;ar=src[T:B,L:RR];a=np.clip((253-ar.mean(2))/253,0,1)*(ar.max(2)-ar.min(2)<12);Y,X=np.indices(a.shape);X=X+L;Y=Y+T
 for q in data[str(f)]['caps']:
  l,t,r,b=q['bbox'];cx=(l+r)/2;cy=(t+b)/2;rad=(b-t)/2;halfStraight=(r-l)/2-rad;distance=np.sqrt(np.maximum(abs(X-cx)-halfStraight,0)**2+(Y-cy)**2);a[distance<=rad+4]=0
 peak=float(a.max());out=[];previous=253
 for j in range(48):
  shade=int(round(253*(1-peak*(j+1)/48)))
  if shade==previous:continue
  threshold=((253-previous)+(253-shade))/(2*253);d,stats=trace.trace_alpha(a,L,T,threshold=threshold);previous=shade
  if d:out.append(dict(id=n['id']+'-opaque-ink-'+str(j),type='path',d=d,fill='#'+format(shade,'02x')*3))
 n['children']=out;n['provenance']['bounds']=[L,T,RR,B];n['provenance']['material']='native opaque grayscale contour bands of source query optical reveal; actual rounded card footprints excluded, no sub-1/255 layer alphas';ledger.append(dict(frame=f,peak=peak,absoluteGrayRange=[253,int(round(253*(1-peak)))],paths=len(out),bounds=[L,T,RR,B]));print(f,'native shades',len(out),'min',previous,'seconds',round(time.monotonic()-start,1),flush=True)
spec['notes']+=' Faint query reveal uses absolute opaque grayscale contour bands because very small per-layer opacity is quantized away by8-bit compositing. Expanded source query bounds preserve the optical halo around independently occluding rounded cards.';(R/'elements-query-final.json').write_text(json.dumps(spec,separators=(',',':')));(R/'query-precision-ledger.json').write_text(json.dumps(ledger,indent=2));print('DONE',time.monotonic()-start,flush=True)
