from pathlib import Path
import json,gzip,hashlib,os,time
base=Path('/workspace/imessage-recreations/outputs'); records=[]
paths=[]
for folder in ['03-photon-mini','06-gallery']:
 for p in (base/folder).glob('*.json'):
  if ('candidate' in p.name or 'accepted' in p.name) and p.stat().st_size>5_000_000 and p.stat().st_nlink==1: paths.append(p)
for p in paths:
 q=p.with_suffix(p.suffix+'.gz')
 if q.exists(): continue
 before=hashlib.sha256(p.read_bytes()).hexdigest(); size=p.stat().st_size
 t=q.with_suffix('.gz.tmp')
 with p.open('rb') as src,t.open('wb') as out:
  with gzip.GzipFile(fileobj=out,mode='wb',compresslevel=6,mtime=0) as dst:
   while chunk:=src.read(1024*1024): dst.write(chunk)
 with gzip.open(t,'rb') as check:
  h=hashlib.file_digest(check,'sha256').hexdigest()
 if h!=before: raise RuntimeError(str(p))
 os.replace(t,q); p.unlink(); records.append({'path':str(p),'archive':str(q),'raw_bytes':size,'gzip_bytes':q.stat().st_size,'raw_sha256':before})
log={'reason':'Lossless archival of obsolete private candidate JSONs to make space for the public video site. Current scenes, media, caches, delivery archive and staged project untouched. Restore using gzip -dc and validate raw_sha256.','records':records,'saved_bytes':sum(x['raw_bytes']-x['gzip_bytes'] for x in records)}
Path('/workspace/sites/message-motion/research/historical-archives.json').write_text(json.dumps(log,indent=2)+'\n')
print(json.dumps({'files':len(records),'saved_bytes':log['saved_bytes']}))
