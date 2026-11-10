"""Use clean right app edge for the cropped933–946 exit camera."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';s=json.loads((D/'scene-chess-art-tap-v12.json').read_text());g=next(q for q in s['layers'] if q['id']=='broad-v5-group-41');by={round(k['t']*30):k for k in g['keyframes']['x']}
def edge(f,expect):
 a=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float);p=np.median(a[615:635,:,2],axis=0);der=np.maximum(np.gradient(gaussian_filter1d(p,1)),0);lo=max(1,round(expect)-22);hi=min(959,round(expect)+23);peak=lo+int(np.argmax(der[lo:hi]));lo=max(1,peak-9);hi=min(959,peak+10);w=der[lo:hi]**2;return float(np.dot(np.arange(lo,hi),w)/max(.001,w.sum()))
refX=by[898]['value'];refEdge=edge(898,refX+483);records=[]
for f in range(933,947):
 old=by[f]['value'];target=edge(f,old+483);x=refX+target-refEdge;by[f]['value']=x;records.append(dict(frame=f,previous=old,x=x,referenceEdge=refEdge,sourceEdge=target))
(D/'chess-exit-v13-measurements.json').write_text(json.dumps(records,indent=2));(D/'scene-chess-art-tap-v12.json').write_text(json.dumps(s,indent=2)+'\n');print(records)
