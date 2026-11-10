#!/usr/bin/env python3
"""One native worker per method, resolving frozen revision just before each job."""
import argparse,json,subprocess,time,os,hashlib,fcntl
from contextlib import contextmanager
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def active_worker(out,method):
 expected='render_pillow.py' if method=='pillow' else 'render_motion_canvas.mjs'
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   args=[a.decode(errors='replace') for a in (proc/'cmdline').read_bytes().split(b'\0') if a]
   if len(args)>1 and args[1].endswith(expected) and '--out' in args and Path(args[args.index('--out')+1]).resolve()==out:return int(proc.name)
  except (FileNotFoundError,PermissionError,ProcessLookupError,IndexError):pass
 return None
def active_any_worker(method):
 expected='render_pillow.py' if method=='pillow' else 'render_motion_canvas.mjs'
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   args=[a.decode(errors='replace') for a in (proc/'cmdline').read_bytes().split(b'\0') if a]
   if len(args)>1 and args[1].endswith(expected):return int(proc.name)
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 return None
def engine_hash(method):
 names=['render_pillow.py'] if method=='pillow' else ['render_motion_canvas.mjs','motion-canvas-runtime.mjs','common.mjs','scene-loader.mjs','runtime-scene.mjs']
 return hashlib.sha256(b''.join((ROOT/'engines'/name).read_bytes() for name in names)).hexdigest()
def current_engine(metadata,method):
 current=engine_hash(method)
 if metadata.get('engineSha256')==current:return True
 ledger=ROOT/'engines/native-engine-compatibility.json'
 if ledger.exists():
  for row in json.loads(ledger.read_text()).get('entries',[]):
   if row['method']==method and row['fromEngineSha256']==metadata.get('engineSha256') and row['toEngineSha256']==current and row['sceneSha256']==metadata.get('sceneSha256'):return True
 return False
@contextmanager
def method_slot(method,ready=None):
 lock=ROOT/'engines'/('.native-'+method+'.lock')
 with lock.open('a+') as handle:
  while True:
   fcntl.flock(handle,fcntl.LOCK_EX)
   if ready is None or ready():break
   # A new source gate can arrive while this job waits for another worker.
   # Release the slot before waiting, so held references do not block others.
   fcntl.flock(handle,fcntl.LOCK_UN)
   time.sleep(2)
  try:yield
  finally:fcntl.flock(handle,fcntl.LOCK_UN)
def main():
 p=argparse.ArgumentParser();p.add_argument('--method',choices=['pillow','motion-canvas'],required=True);p.add_argument('--only');a=p.parse_args();results=[];queue=ROOT/'engines/native-queue.json';names=[row[0] for row in json.loads(queue.read_text())]
 for name in names:
  if a.only and a.only!=name:continue
  paused=ROOT/'engines/native-paused.json';announced=False
  method_paused=ROOT/'engines/native-method-paused.json'
  def is_paused():
   return (paused.exists() and name in json.loads(paused.read_text())) or (method_paused.exists() and name in json.loads(method_paused.read_text()).get(a.method,[]))
  while is_paused():
   if not announced:print(json.dumps({'event':'waiting-final-frozen-input','reference':name,'method':a.method}),flush=True);announced=True
   time.sleep(2)
  revision=dict(json.loads(queue.read_text()))[name];scene=ROOT/'outputs'/name/revision/'scene.json';out=ROOT/'outputs'/name/(a.method+'.mp4');waiting=False
  while pid:=active_worker(out,a.method):
   if not waiting:print(json.dumps({'event':'waiting-existing-native-worker','pid':pid,'reference':name,'method':a.method}),flush=True);waiting=True
   time.sleep(2)
  revision=dict(json.loads(queue.read_text()))[name];scene=ROOT/'outputs'/name/revision/'scene.json';meta=Path(str(out)+'.render.json')
  if meta.exists() and out.exists():
   m=json.loads(meta.read_text())
   if Path(m.get('scene','')).resolve()==scene.resolve() and current_engine(m,a.method):print(json.dumps({'event':'already-complete','reference':name,'method':a.method,'revision':revision}),flush=True);continue
  if not scene.exists():raise FileNotFoundError('Frozen queue input not ready: '+str(scene))
  with method_slot(a.method,lambda:not is_paused()):
   revision=dict(json.loads(queue.read_text()))[name];scene=ROOT/'outputs'/name/revision/'scene.json'
   if meta.exists() and out.exists():
    completed=json.loads(meta.read_text())
    if Path(completed.get('scene','')).resolve()==scene.resolve() and current_engine(completed,a.method):
     print(json.dumps({'event':'already-complete-after-native-slot','reference':name,'method':a.method,'revision':revision}),flush=True);continue
   announced=False
   while pid:=active_any_worker(a.method):
    if not announced:print(json.dumps({'event':'waiting-native-method-capacity','pid':pid,'reference':name,'method':a.method}),flush=True);announced=True
    time.sleep(2)
   revision=dict(json.loads(queue.read_text()))[name];scene=ROOT/'outputs'/name/revision/'scene.json'
   cmd=[str(ROOT/'engines/.venv/bin/python'),str(ROOT/'engines/render_pillow.py'),'--scene',str(scene),'--out',str(out),'--aa','1'] if a.method=='pillow' else ['node',str(ROOT/'engines/render_motion_canvas.mjs'),'--scene',str(scene),'--out',str(out)]
   cmd+=['--frames-dir',str(ROOT/'outputs'/name/'cache'/a.method)]
   ranges=None
   patches=ROOT/'engines/native-patches.json'
   if patches.exists():
    patch=json.loads(patches.read_text()).get(name)
    if patch and patch.get('revision')==revision:
     ranges=patch.get('methodRanges',{}).get(a.method,patch.get('ranges'))
     if a.method=='pillow' and 'antialias' in patch:
      antialias=patch['antialias']
      if not isinstance(antialias,int) or antialias<1:raise ValueError('Invalid native Pillow antialias setting')
      cmd[cmd.index('--aa')+1]=str(antialias)
     if meta.exists():
      base=Path(json.loads(meta.read_text()).get('scene','')).parent.name
      ranges=patch.get('baseRanges',{}).get(a.method,{}).get(base,ranges)
   # A source patch must also repair any known renderer-only differences in its
   # retained baseline. These tuples pin the actual old scene and engine hashes.
   corrections=ROOT/'engines/native-engine-corrections.json'
   if ranges and meta.exists() and corrections.exists():
    previous=json.loads(meta.read_text());extra=[]
    for correction in json.loads(corrections.read_text()).get('entries',[]):
     if correction['method']==a.method and correction['fromEngineSha256']==previous.get('engineSha256') and correction['toEngineSha256']==engine_hash(a.method) and correction['sceneSha256']==previous.get('sceneSha256'):extra.extend(correction['ranges'])
    if extra:
     selected={f for r in ranges.split(',') for f in range(int(r.split(':')[0]),int(r.split(':')[1])+1)}
     selected.update(f for first,last in extra for f in range(first,last+1));merged=[]
     for f in sorted(selected):
      if merged and merged[-1][1]==f-1:merged[-1][1]=f
      else:merged.append([f,f])
     ranges=','.join(f'{first}:{last}' for first,last in merged)
     print(json.dumps({'event':'including-native-engine-corrections','reference':name,'method':a.method,'extra_ranges':extra}),flush=True)
   if ranges:cmd+=['--ranges',ranges]
   print(json.dumps({'event':'starting','method':a.method,'reference':name,'revision':revision}),flush=True);started=time.monotonic();result=subprocess.run(cmd,cwd=ROOT);record={'reference':name,'revision':revision,'method':a.method,'exit_code':result.returncode,'seconds':time.monotonic()-started,'output':str(out)};results.append(record);(ROOT/'outputs/alternative-methods'/('batch-'+a.method+'.json')).write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(record),flush=True)
   if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
