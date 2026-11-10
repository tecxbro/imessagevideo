#!/usr/bin/env python3
"""Bound private Drive parts to 24MiB so future agents can materialize each."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/dev/shm/imessage-complete-library/parts');OUT.mkdir(exist_ok=True)
size=24*1024*1024
def digest(path):return hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
p=ROOT/'complete-library/packs.json';records=json.loads(p.read_text())['archives'];result=[]
for record in records:
    source=Path(record['path']);folder=OUT/record['id'];folder.mkdir(exist_ok=True);pieces=[]
    with source.open('rb') as stream:
        number=0
        while data:=stream.read(size):
            number+=1;name=f"{record['id']}.zip.part{number:03}";path=folder/name;h=hashlib.sha256(data).hexdigest()
            if not path.is_file() or path.stat().st_size!=len(data) or digest(path)!=h:
                temp=path.with_suffix(path.suffix+'.tmp');temp.write_bytes(data);os.replace(temp,path)
            pieces.append({'number':number,'file_name':name,'path':str(path),'bytes':len(data),'sha256':h})
    assert sum(v['bytes'] for v in pieces)==record['bytes']
    full=hashlib.sha256()
    for part in pieces:
        with Path(part['path']).open('rb') as stream:
            while data:=stream.read(1024*1024):full.update(data)
    assert full.hexdigest()==record['sha256']
    result.append({**record,'parts':pieces})
out=ROOT/'complete-library/upload-plan.json';temp=out.with_suffix('.tmp');temp.write_text(json.dumps({'part_limit_bytes':size,'archives':result},indent=2)+'\n');os.replace(temp,out)
print(json.dumps({'archives':len(result),'parts':sum(len(v['parts']) for v in result),'bytes':sum(v['bytes'] for v in result)}))
