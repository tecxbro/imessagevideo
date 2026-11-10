from pathlib import Path
import gzip,hashlib,shutil,json
R=Path(__file__).resolve().parent
records=[]
for name in ['reasoning-neutral-compact.json','reasoning-combined-candidate.json','reasoning-combined-probe.scene.json']:
    source=R/name;destination=Path(str(source)+'.gz');temporary=Path(str(destination)+'.single-writer.tmp')
    before=source.stat().st_size;h=hashlib.sha256(source.read_bytes()).hexdigest()
    with source.open('rb')as incoming,gzip.open(temporary,'wb',compresslevel=3)as outgoing:shutil.copyfileobj(incoming,outgoing,1024*1024)
    actual=hashlib.sha256()
    with gzip.open(temporary,'rb')as incoming:
        for block in iter(lambda:incoming.read(1024*1024),b''):actual.update(block)
    assert actual.hexdigest()==h
    temporary.replace(destination);source.unlink()
    records.append({'original':str(source),'archive':str(destination),'originalSHA256':h,'decompressedSHA256':actual.hexdigest(),'originalBytes':before,'archiveBytes':destination.stat().st_size,'archiveSHA256':hashlib.sha256(destination.read_bytes()).hexdigest(),'verified':True})
    print('archived',name,before-destination.stat().st_size,flush=True)
(R/'final-private-archives.json').write_text(json.dumps({'records':records,'reclaimedBytes':sum(r['originalBytes']-r['archiveBytes']for r in records)},indent=2))
