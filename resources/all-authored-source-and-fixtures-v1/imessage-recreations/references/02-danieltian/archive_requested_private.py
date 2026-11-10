"""Root-approved single-writer reversible archival of seven superseded private scenes."""
from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,shutil,json,os
R=Path(__file__).resolve().parents[2];D=R/'outputs/02-danieltian/final-v19';ledger=D/'private-prototype-archives.json';preflight=json.loads((D/'private-prototype-archive-preflight.json').read_text());records=[]
def sha(file):
    digest=hashlib.sha256()
    with Path(file).open('rb')as incoming:
        for block in iter(lambda:incoming.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()
def save():
    data={'authorization':'Explicit root serialized archival handoff; current19/activepatchdata/assets/caches excluded.','records':records,'reclaimedBytes':sum(q['sourceBytes']-q['archiveBytes']for q in records if q['state']=='archived-raw-removed'),'completedFiles':sum(q['state']=='archived-raw-removed'for q in records),'totalFiles':len(preflight['approvedRelativePaths'])};temp=ledger.with_name(ledger.name+'.single-owner.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(ledger)
for name in preflight['approvedRelativePaths']:
    source=R/name;target=Path(str(source)+'.gz');temporary=Path(str(target)+'.single-owner.tmp');assert source.is_file()and not target.exists()and not temporary.exists();stat=source.stat();fact=(stat.st_ino,stat.st_size,stat.st_mtime_ns);sourceSHA=sha(source)
    with source.open('rb')as incoming,gzip.open(temporary,'wb',compresslevel=3)as outgoing:shutil.copyfileobj(incoming,outgoing,1024*1024)
    actual=hashlib.sha256()
    with gzip.open(temporary,'rb')as incoming:
        for block in iter(lambda:incoming.read(1024*1024),b''):actual.update(block)
    assert actual.hexdigest()==sourceSHA;stat=source.stat();assert fact==(stat.st_ino,stat.st_size,stat.st_mtime_ns)
    temporary.replace(target);record={'original':str(source),'archive':str(target),'sourceSHA256':sourceSHA,'decompressedSHA256':actual.hexdigest(),'archiveSHA256':sha(target),'sourceBytes':fact[1],'archiveBytes':target.stat().st_size,'sourceStatBefore':list(fact),'decompressedSHA256Verified':True,'state':'verified-raw-retained','verifiedAtUTC':datetime.now(timezone.utc).isoformat()};records.append(record);save();source.unlink();record['state']='archived-raw-removed';save();print(json.dumps(record),flush=True)
print('COMPLETE',ledger.read_text(),flush=True)
