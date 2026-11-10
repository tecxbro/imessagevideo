"""Root-authorized disjoint native output lanes; runtime remains frozen."""
import argparse,fcntl,json,os,subprocess,sys,time,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'engines'))
from run_alternative_batch import active_worker,engine_hash
p=argparse.ArgumentParser();p.add_argument('references',nargs='+');p.add_argument('--wait-for');a=p.parse_args()
outdir=Path(__file__).parent;expected='7080c58ce151d1966b44671dc9db0801f81cb514200a3e8ed8a6cd1401777195'
assert engine_hash('motion-canvas')==expected
if a.wait_for:
 while active_worker(root/'outputs'/a.wait_for/'motion-canvas.mp4','motion-canvas'):time.sleep(2)
for name in a.references:
 output=root/'outputs'/name;picture=output/'motion-canvas.mp4'
 with (output/'.motion-canvas-output.lock').open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  while active_worker(picture,'motion-canvas'):time.sleep(2)
  revision=dict(json.loads((root/'engines/native-queue.json').read_text()))[name]
  scene=output/revision/'scene.json';target=hashlib.sha256(scene.read_bytes()).hexdigest()
  patch=json.loads((root/'engines/native-patches.json').read_text())[name]
  assert patch['revision']==revision
  cli=patch.get('methodRanges',{}).get('motion-canvas',patch.get('ranges'))
  selected={f for text in cli.split(',') for f in range(int(text.split(':')[0]),int(text.split(':')[1])+1)}
  old=json.loads(Path(str(picture)+'.render.json').read_text())
  if old['sceneSha256']==target and old['engineSha256']==expected:
   print(json.dumps({'event':'already-complete','reference':name}),flush=True);continue
  for c in json.loads((root/'engines/native-engine-corrections.json').read_text())['entries']:
   if c['method']=='motion-canvas' and c['fromEngineSha256']==old['engineSha256'] and c['toEngineSha256']==expected and c['sceneSha256']==old['sceneSha256']:
    selected.update(f for first,last in c['ranges'] for f in range(first,last+1))
  merged=[]
  for f in sorted(selected):
   if merged and merged[-1][1]==f-1:merged[-1][1]=f
   else:merged.append([f,f])
  cli=','.join(f'{first}:{last}' for first,last in merged)
  if name=='05-linq':
   for frame in [820,828]:
    log=outdir/f'05-preflight-{frame}.log';candidate=root/f'outputs/alternative-methods/05-final20-motion-canvas-{frame}.png'
    with log.open('w') as handle:subprocess.run(['node',str(root/'engines/render_motion_canvas.mjs'),'--scene',str(scene),'--out',str(candidate),'--frame',str(frame)],cwd=root,stdout=handle,stderr=subprocess.STDOUT,check=True)
  log=outdir/(name+'-rms-capture.log');started=time.monotonic()
  print(json.dumps({'event':'starting-disjoint-native-output','reference':name,'frames':len(selected),'ranges':merged,'engineSha256':expected}),flush=True)
  with log.open('w') as handle:
   subprocess.run(['node',str(root/'engines/render_motion_canvas.mjs'),'--scene',str(scene),'--out',str(picture),'--frames-dir',str(output/'cache/motion-canvas'),'--ranges',cli],cwd=root,stdout=handle,stderr=subprocess.STDOUT,check=True)
  meta=json.loads(Path(str(picture)+'.render.json').read_text());assert meta['engineSha256']==expected and meta['sceneSha256']==target
  record={'reference':name,'sceneSha256':target,'engineSha256':expected,'capturedFrames':len(selected),'ranges':merged,'seconds':time.monotonic()-started,'metadata':str(picture)+'.render.json','log':str(log),'status':'capture/renderer encode complete; final PC/parity/audio remain assigned separately'}
  (outdir/(name+'-rms-completion.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
