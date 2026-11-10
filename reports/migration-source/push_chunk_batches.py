#!/usr/bin/env python3
"""Explicit migration helper: publish verified pieces in bounded Git pushes.

Only run on the named import branch in the explicitly selected repository.
This is migration history, not a normal Mac setup step.
"""
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
def out(args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def run(args):subprocess.run(['git',*args],cwd=ROOT,check=True)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--batch-size',type=int,default=8);a=p.parse_args()
if not a.run:raise SystemExit('Explicit --run is required')
assert out(['config','--get','remote.origin.url'])=='https://github.com/tecxbro/imessagevideo.git'
assert out(['branch','--show-current'])=='import/complete-library'
assert not out(['diff','--cached','--name-only']), 'Existing staged files must be reviewed first'
tracked=set(out(['ls-files','archives/resource-parts']).splitlines())
files=sorted(str(x.relative_to(ROOT)) for x in (ROOT/'archives/resource-parts').rglob('*') if x.is_file())
pending=[x for x in files if x not in tracked]
for n in range(0,len(pending),a.batch_size):
    batch=pending[n:n+a.batch_size]
    assert all((ROOT/x).stat().st_size<=25165824 for x in batch)
    print(json.dumps({'batch':n//a.batch_size+1,'files':len(batch),'bytes':sum((ROOT/x).stat().st_size for x in batch)}),flush=True)
    run(['add','--',*batch])
    run(['commit','-m',f'Preserve verified library pieces {n+1}-{n+len(batch)} of {len(pending)} remaining'])
    run(['-c','pack.compression=1','push','origin','import/complete-library'])
print(json.dumps({'original_parts_tracked':len(files),'head':out(['rev-parse','HEAD']),'all_batches_pushed':True}),flush=True)
