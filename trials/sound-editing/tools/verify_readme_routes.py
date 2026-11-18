"""Execute reproduction shell blocks verbatim in a disposable, bootstrapped worktree."""
import argparse
from pathlib import Path
import re
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('readme',type=Path)
p.add_argument('--log',type=Path,required=True)
p.add_argument('--resume-at',help='Resume after a harness interruption, at this exact command substring')
p.add_argument('--block',type=int,action='append',help='Select shell blocks (zero-based), e.g. bootstrap only')
p.add_argument('--label',action='append',help='Instantiate the documented LABEL placeholder')
a=p.parse_args()
blocks=re.findall(r'```sh\n(.*?)```',a.readme.read_text(),re.S)
if a.block is not None:blocks=[blocks[i] for i in a.block]
if a.label:blocks=[expanded for block in blocks for expanded in ([block.replace('LABEL',label) for label in a.label] if 'LABEL' in block else [block])]
script='set -ex\n'
for block in blocks:
    commands=block.splitlines(keepends=True)
    joined=[];current=''
    for line in commands:
        current+=line
        if line.rstrip().endswith('\\'):continue
        # Damaged deliveries must fail review with exactly exit1, not crash.
        if 'check_cues.py' in current and '--json' in current and 'damaged' in current:
            current=current.rstrip()+' && exit 99 || test "$?" -eq 1\n'
        joined.append(current);current=''
    script+=''.join(joined)+current+'\n'
a.log.parent.mkdir(parents=True,exist_ok=True)
if a.resume_at:
    start=script.index(a.resume_at)
    variables='\n'.join(re.findall(r'^[A-Z]+=.*$',script[:start],re.M))
    script='set -ex\n'+variables+'\n'+script[start:]
script_path=a.log.with_suffix('.sh')
script_path.write_text(script)
with a.log.open('w') as log:
    result=subprocess.run(['bash',str(script_path)],stdin=subprocess.DEVNULL,text=True,stdout=log,stderr=subprocess.STDOUT)
print(f'{a.readme}: exit={result.returncode}; log={a.log}')
raise SystemExit(result.returncode)
