from pathlib import Path
from base64 import b64decode
from hashlib import sha1
import concurrent.futures
import json
import os
import subprocess
import sys

repo, scratch = map(Path, sys.argv[1:])
prefix = 'review/imv-v3/motion'
env = {**os.environ, 'GIT_NO_LAZY_FETCH':'1', 'GIT_TERMINAL_PROMPT':'0'}
rows = subprocess.check_output(['git','ls-tree','-r','-z','HEAD',prefix],cwd=repo,env=env).rstrip(b'\0').split(b'\0')

def recover(record):
    header, path = record.split(b'\t')
    oid = header.split()[-1].decode()
    path = path.decode()
    local = subprocess.run(['git','cat-file','blob',oid],cwd=repo,env=env,capture_output=True)
    if local.returncode:
        raw = subprocess.check_output(['gh','api','repos/tecxbro/imessagevideo/git/blobs/'+oid],cwd=repo)
        result = json.loads(raw)
        binary = b64decode(result['content'])
        source = 'github-blob'
    else:
        binary = local.stdout
        source = 'local-git'
    assert oid==sha1(f'blob {len(binary)}\0'.encode()+binary).hexdigest(), path
    target = scratch/'snapshot'/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(binary)
    return [path, oid, len(binary), source]

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(recover,rows))
(scratch/'git-review-inventory.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'Recovered {len(results)} records; read {sum(r[3]=="github-blob" for r in results)} missing objects via GitHub blobs.')
