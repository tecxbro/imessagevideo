from pathlib import Path
import sys,subprocess,time,json,hashlib
import numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations')
sys.path.insert(0,str(R/'engines'))
from run_alternative_batch import method_slot,active_any_worker
P=R/'outputs/alternative-methods/preflight/04-v18-affine'
S=R/'outputs/04-poke/final-v18/scene.json'
with method_slot('motion-canvas'):
 while active_any_worker('motion-canvas'):
  time.sleep(2)
 subprocess.run(['node','engines/fixtures/shadow-opacity/capture_probe.mjs','--scene',str(S),'--runtime','engines/motion-canvas-runtime.mjs','--frames','108,557','--out-dir',str(P)],cwd=R,check=True)
rows=[]
for f in (108,557):
 ref=R/'outputs/04-poke/qa-v17-prototype-03'/f'{f:06}.png'
 native=P/f'{f:06}.png'
 pillow=P/f'{f:06}-pillow.png'
 subprocess.run(['engines/.venv/bin/python','engines/render_pillow.py','--scene',str(S),'--out',str(pillow),'--frame',str(f)],cwd=R,check=True)
 a=np.asarray(Image.open(ref).convert('RGB'),dtype=float)
 row={'frame':f,'sceneSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'acceptedControl':str(ref)}
 for method,path in [('motionCanvas',native),('pillow',pillow)]:
  b=np.asarray(Image.open(path).convert('RGB'),dtype=float)
  row[method]={'mae':float(abs(a-b).mean()),'maxChannelDifference':float(abs(a-b).max())}
 rows.append(row)
(P/'report.json').write_text(json.dumps(rows,indent=2)+'\n')
print(rows,flush=True)
