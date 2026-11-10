import os,sys,json,subprocess
from pathlib import Path
root=Path(sys.argv[1]);print('Ready for credential JSON on stdin (input is hidden).',flush=True)
if sys.stdin.isatty():
 import termios
 attrs=termios.tcgetattr(sys.stdin.fileno());hidden=attrs.copy();hidden[3]&=~termios.ECHO;termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,hidden)
try:c=json.loads(sys.stdin.readline())
finally:
 if sys.stdin.isatty():termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,attrs)
env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
if c.get('auth_mode')!='work_proxy':env.update({'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'http.extraHeader','GIT_CONFIG_VALUE_0':'Authorization: Bearer '+c['token']})
def git(*args):return subprocess.run(['git',*args],cwd=root,env=env,capture_output=True,text=True)
r=git('remote','get-url','origin')
if r.returncode:git('remote','add','origin',c['remote_url'])
elif r.stdout.strip()!=c['remote_url']:raise RuntimeError('Remote mismatch')
r=git('push','origin','HEAD:refs/heads/'+c['branch'])
if r.returncode:print(json.dumps({'status':'failed','error':r.stderr.replace(c.get('token','UNUSED'),'<redacted>')}));sys.exit(r.returncode)
sha=git('rev-parse','HEAD').stdout.strip();r=git('ls-remote','origin','refs/heads/'+c['branch'])
if r.returncode or r.stdout.split()[0]!=sha:raise RuntimeError('Remote HEAD mismatch')
print(json.dumps({'status':'pushed','commit_sha':sha,'remote_verified':True}))
