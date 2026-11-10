from pathlib import Path
import sys,subprocess,time,json,hashlib
import numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations')
sys.path.insert(0,str(R/'engines'))
from run_alternative_batch import method_slot,active_any_worker
P=R/'outputs/alternative-methods/preflight/04-v19-sarah'
S=R/'outputs/04-poke/final-v19/scene.json'
frames=(142,165)
with method_slot('motion-canvas'):
 while active_any_worker('motion-canvas'):
  time.sleep(2)
 subprocess.run(['node','engines/fixtures/shadow-opacity/capture_probe.mjs','--scene',str(S),'--runtime','engines/motion-canvas-runtime.mjs','--frames',','.join(map(str,frames)),'--out-dir',str(P)],cwd=R,check=True)
with method_slot('pillow'):
 while active_any_worker('pillow'):
  time.sleep(2)
 for f in frames:
  subprocess.run(['engines/.venv/bin/python','engines/render_pillow.py','--scene',str(S),'--out',str(P/f'{f:06}-pillow.png'),'--frame',str(f)],cwd=R,check=True)
rows=[]
for f in frames:
 ref=R/'outputs/04-poke/qa-v19-prototype-02'/f'{f:06}.png'
 a=np.asarray(Image.open(ref).convert('RGB'),dtype=float)
 row={'frame':f,'sceneSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'acceptedControl':str(ref)}
 for method,path in [('motionCanvas',P/f'{f:06}.png'),('pillow',P/f'{f:06}-pillow.png')]:
  b=np.asarray(Image.open(path).convert('RGB'),dtype=float)
  row[method]={'mae':float(abs(a-b).mean()),'maxChannelDifference':float(abs(a-b).max())}
 rows.append(row)
(P/'report.json').write_text(json.dumps(rows,indent=2)+'\n')
print(rows,flush=True)
