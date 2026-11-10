import subprocess,os,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[3]
# The production coordinator retains the normal one-method lock and final-source checks.
for name in ['06-gallery','04-poke','03-photon-mini']:
 path=root/'outputs/alternative-methods'/('text-refresh-'+name+'.log')
 with path.open('w') as log:
  started=time.monotonic();print(json.dumps({'event':'requesting-native-slot','reference':name}),flush=True)
  r=subprocess.run(['python3','engines/run_alternative_batch.py','--method','motion-canvas','--only',name],cwd=root,stdout=log,stderr=subprocess.STDOUT)
  print(json.dumps({'reference':name,'exitCode':r.returncode,'seconds':time.monotonic()-started,'log':str(path)}),flush=True)
  if r.returncode:raise SystemExit(r.returncode)
