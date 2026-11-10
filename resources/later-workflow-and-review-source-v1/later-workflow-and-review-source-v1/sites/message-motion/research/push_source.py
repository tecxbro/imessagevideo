import os,sys,json,subprocess
from pathlib import Path
print('Ready for credential JSON on stdin (input is hidden).',flush=True)
if sys.stdin.isatty():
 import termios
 attrs=termios.tcgetattr(sys.stdin.fileno());hidden=attrs.copy();hidden[3]&=~termios.ECHO;termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,hidden)
try: credential=json.loads(sys.stdin.readline())
finally:
 if sys.stdin.isatty():termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,attrs)
root=Path('/workspace/sites/message-motion');env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
if credential.get('auth_mode')!='work_proxy':
 env['GIT_CONFIG_COUNT']='1';env['GIT_CONFIG_KEY_0']='http.extraHeader';env['GIT_CONFIG_VALUE_0']='Authorization: Bearer '+credential['token']
run=lambda args:subprocess.run(args,cwd=root,env=env,text=True,capture_output=True)
r=run(['git','remote','get-url','origin'])
if r.returncode:subprocess.run(['git','remote','add','origin',credential['remote_url']],cwd=root,check=True,capture_output=True)
elif r.stdout.strip()!=credential['remote_url']:raise RuntimeError('Remote mismatch')
plan=json.loads((root/'verification/bounded-source-upload.json').read_text())['batches']
remote=run(['git','ls-remote','origin','refs/heads/'+credential['branch']])
if remote.returncode:raise RuntimeError('Could not read remote state')
current=remote.stdout.split()[0] if remote.stdout.strip() else None
shas=[b['commit_sha'] for b in plan]
if current and current not in shas:raise RuntimeError('Unexpected remote state; no force push permitted')
start=shas.index(current)+1 if current else 0
for index,batch in enumerate(plan[start:],start):
 r=run(['git','push','origin',batch['commit_sha']+':refs/heads/'+credential['branch']])
 if r.returncode:
  output=(r.stderr or r.stdout).replace(credential.get('token','NO_TOKEN'),'<redacted>')
  print(json.dumps({'status':'failed','batch':index+1,'error':output}));sys.exit(r.returncode)
 print(json.dumps({'status':'batch_pushed','batch':index+1,'total':len(plan),'raw_new_bytes':batch['new_bytes']}),flush=True)
sha=run(['git','rev-parse','HEAD']).stdout.strip()
remote=run(['git','ls-remote','origin','refs/heads/'+credential['branch']])
if remote.returncode or remote.stdout.split()[0]!=sha:raise RuntimeError('Remote HEAD did not match local commit')
print(json.dumps({'status':'pushed','commit_sha':sha,'verified_remote_head':True}))
