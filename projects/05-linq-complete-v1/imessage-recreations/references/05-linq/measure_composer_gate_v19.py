"""Compare every authored intro/Cash native frame and immutable-cache boundary."""
from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;R=D.parent.parent;N=D/'measurements/composer-v19/native';intro=R/'verification/05-composers-v19-dense';cash=R/'verification/05-cash-caret-v19-detail';rows=[]
for f in list(range(99))+list(range(768,827)):
 folder=intro if f<99 else cash;a=np.asarray(Image.open(N/f'source-{f:06}.png').convert('RGB')).astype(np.int16);b=np.asarray(Image.open(folder/f'{f/30:.3f}.png').convert('RGB')).astype(np.int16);c=np.asarray(Image.open(R/f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB')).astype(np.int16);rows.append({'frame':f,'oldMAE':float(np.abs(a-c).mean()),'newMAE':float(np.abs(a-b).mean()),'delta':float(np.abs(a-b).mean()-np.abs(a-c).mean())})
controls=[]
for f,folder in [(99,intro),(767,cash),(827,cash)]:
 a=np.asarray(Image.open(folder/f'{f/30:.3f}.png').convert('RGB')).astype(np.int16);b=np.asarray(Image.open(R/f'outputs/05-linq/frames-gsap/{f:06}.png').convert('RGB')).astype(np.int16);controls.append({'frame':f,'maxDelta':int(np.abs(a-b).max())})
report={'frames':len(rows),'rows':rows,'oldMean':float(np.mean([r['oldMAE']for r in rows])),'newMean':float(np.mean([r['newMAE']for r in rows])),'regressions':[r for r in rows if r['delta']>1e-10],'controls':controls,'note':'These are local unencoded native comparisons. Source fidelity is measured independently after final PC709 encode; no ratio is a perfection percentage.'};out=R/'verification/05-v19-composer-native-gate.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='rows'},indent=2));assert all(r['maxDelta']==0 for r in controls)
