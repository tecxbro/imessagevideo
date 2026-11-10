from pathlib import Path
import sys,subprocess,time,json,hashlib
import numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');sys.path.insert(0,str(R/'engines'));from run_alternative_batch import method_slot,active_any_worker
P=R/'outputs/alternative-methods/preflight/05-boarding-v18';S=P/'snapshot.scene.json'
with method_slot('motion-canvas'):
 while active_any_worker('motion-canvas'):time.sleep(2)
 subprocess.run(['node','engines/fixtures/shadow-opacity/capture_probe.mjs','--scene',str(S),'--runtime','engines/motion-canvas-runtime.mjs','--frames','1204,1210','--out-dir',str(P)],cwd=R,check=True)
rows=[]
for f in (1204,1210):
 ref=R/'outputs/05-linq/root-boarding-overlay-v18-check'/f'{f/30:.3f}.png';new=P/f'{f:06}.png';a=np.array(Image.open(ref).convert('RGB'),dtype=float);b=np.array(Image.open(new).convert('RGB'),dtype=float);rows.append({'frame':f,'nativeMcVsAcceptedGsapMae':float(abs(a-b).mean()),'maxChannelDifference':float(abs(a-b).max()),'candidateSceneSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'acceptedControl':str(ref)})
(P/'report.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows,flush=True)
