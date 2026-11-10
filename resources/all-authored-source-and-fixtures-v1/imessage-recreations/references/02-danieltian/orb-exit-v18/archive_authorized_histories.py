"""Explicit root handoff: serialize17 + superseded private phonebook fixture."""
from pathlib import Path
import hashlib,gzip,shutil,json
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
entries=[(R/'outputs/02-danieltian/final-v17/scene.json','09df288bd09aee0ec33bca014dc4598f966ffa52b36cb3489c685fb21a43c74a'),(R/'references/02-danieltian/phonebook-v14/scene-preserved.json',None)]
records=[]
for source,expected in entries:
    target=Path(str(source)+'.gz');temporary=Path(str(target)+'.single-owner.tmp');assert not target.exists()and not temporary.exists()
    sourceSHA=hashlib.sha256(source.read_bytes()).hexdigest();before=source.stat().st_size
    if expected:assert sourceSHA==expected
    with source.open('rb')as incoming,gzip.open(temporary,'wb',compresslevel=3)as outgoing:shutil.copyfileobj(incoming,outgoing,1024*1024)
    actual=hashlib.sha256()
    with gzip.open(temporary,'rb')as incoming:
        for block in iter(lambda:incoming.read(1024*1024),b''):actual.update(block)
    assert actual.hexdigest()==sourceSHA
    temporary.replace(target)
    record={'source':str(source),'archive':str(target),'sourceSHA256':sourceSHA,'decompressedSHA256':actual.hexdigest(),'originalBytes':before,'archiveBytes':target.stat().st_size,'archiveSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'decompressedSHA256Verified':True,'authorization':'Explicit root single-writer handoff after all raw17 readers exited; superseded private phonebook fixture only. Current18, all assets/proofs/caches preserved.'}
    source.unlink();records.append(record);(D/'authorized-history-archives.json').write_text(json.dumps({'records':records,'reclaimedBytes':sum(q['originalBytes']-q['archiveBytes']for q in records)},indent=2));print(json.dumps(record),flush=True)
print('reclaimedBytes',sum(q['originalBytes']-q['archiveBytes']for q in records),flush=True)
