from pathlib import Path
import json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
root=P.parent.parent

def read(path):
 return np.asarray(Image.open(path).convert('RGB'))
def mae(a,b):
 return float(np.abs(np.subtract(a,b,dtype=np.int16)).mean())
frames=list(range(230,310))+list(range(335,345))
records=[]
for frame in frames:
 name=str(frame//30)if frame%30==0 else str(frame/30)
 source=read(P/f'mail-edit-v17-source/{frame:04}.png')
 old=read(root/f'outputs/03-photon-mini/frames-gsap/{frame:06}.png')
 new=read(P/f'mail-edit-v17-final-dense/{name}.png')
 before=mae(source,old)
 after=mae(source,new)
 records.append(dict(frame=frame,before=before,after=after,delta=after-before))
controls=[]
for frame in [229,310,334,345,354,355]:
 name=str(frame//30)if frame%30==0 else str(frame/30)
 old=read(root/f'outputs/03-photon-mini/frames-gsap/{frame:06}.png')
 new=read(P/f'mail-edit-v17-final-dense/{name}.png')
 controls.append(dict(frame=frame,pixel_mae=mae(old,new),maximum_channel_delta=int(np.abs(np.subtract(old,new,dtype=np.int16)).max())))
summary=dict(frames=len(records),scope=[[230,309],[335,344]],mean_before=float(np.mean([r['before']for r in records])),mean_after=float(np.mean([r['after']for r in records])),max_after=max(records,key=lambda r:r['after']),regressions=[r for r in records if r['delta']>1e-5],controls=controls,records=records)
(P/'mail-edit-v17-native-metrics.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items()if k!='records'},indent=2))
