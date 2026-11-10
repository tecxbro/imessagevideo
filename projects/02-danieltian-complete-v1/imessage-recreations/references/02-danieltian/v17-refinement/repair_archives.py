"""One writer, atomic archive publish, SHA verification before source unlink."""
from pathlib import Path
import gzip,hashlib,shutil,json
R=Path(__file__).resolve().parent
source=R/'reasoning-neutral-house-probe.json';dest=Path(str(source)+'.gz');temp=Path(str(dest)+'.serial-verified.tmp')
original=hashlib.sha256(source.read_bytes()).hexdigest();before=source.stat().st_size
with source.open('rb')as incoming,gzip.open(temp,'wb',compresslevel=3)as outgoing:shutil.copyfileobj(incoming,outgoing,1024*1024)
h=hashlib.sha256()
with gzip.open(temp,'rb')as incoming:
 for block in iter(lambda:incoming.read(1024*1024),b''):h.update(block)
assert h.hexdigest()==original
temp.replace(dest);source.unlink()
records=[{'file':str(source),'archive':str(dest),'sourceSHA256':original,'decompressedSHA256':h.hexdigest(),'verified':True,'before':before,'after':dest.stat().st_size}]
other=R/'reasoning-neutral-candidate.json.gz';h=hashlib.sha256();length=0
with gzip.open(other,'rb')as incoming:
 for block in iter(lambda:incoming.read(1024*1024),b''):h.update(block);length+=len(block)
records.append({'file':str(other)[:-3],'archive':str(other),'decompressedSHA256':h.hexdigest(),'verified':True,'before':length,'after':other.stat().st_size,'priorProducer':"Original simplify_neutral verified original/decompressed SHA then unlinked this file before its separate house archive failed. This independent read reconfirms stream integrity."})
for q in records:q['archiveSHA256']=hashlib.sha256(Path(q['archive']).read_bytes()).hexdigest()
(R/'neutral-private-archives.json').write_text(json.dumps(records,indent=2))
print(json.dumps({'reclaimedBytes':sum(x['before']-x['after']for x in records),'records':records}),flush=True)
