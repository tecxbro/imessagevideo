"""Losslessly archive only five superseded private scene experiments."""
from pathlib import Path
import gzip,hashlib,json,os,shutil,time
R=Path(__file__).resolve().parent;ROOT=R.parents[2];canonical=ROOT/'outputs/02-danieltian/final-v14';assert json.loads((canonical/'asset-proof.json').read_text())['allAssetsVerified'];names=['frame486-layered-prototype.scene.json','scene-candidate.json','helper-candidate.scene.json','scene-refined.json','scene-query-final.json'];manifest=R/'superseded-scene-archives.json';data=json.loads(manifest.read_text())if manifest.exists()else{'notice':'Lossless archival only: current inputs/release candidate, all canonical snapshots/assets/caches are excluded. Original JSON can be recovered exactly with gzip.','diskFreeBefore':shutil.disk_usage(ROOT).free,'files':[]}
def sha_stream(f):
 h=hashlib.sha256()
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
for name in names:
 p=R/name
 if not p.exists():
  assert any(q['original']==str(p)for q in data['files']);continue
 before=p.stat()
 with p.open('rb')as f:digest=sha_stream(f)
 target=p.with_suffix(p.suffix+'.gz');temp=target.with_suffix(target.suffix+'.tmp-'+str(os.getpid()))
 with p.open('rb')as src,gzip.open(temp,'wb',compresslevel=6)as out:shutil.copyfileobj(src,out,length=1024*1024)
 with gzip.open(temp,'rb')as f:verified=sha_stream(f)
 assert verified==digest
 after=p.stat();assert(before.st_size,before.st_mtime_ns,before.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino)
 with p.open('rb')as f:assert sha_stream(f)==digest
 os.replace(temp,target)
 with target.open('rb')as f:archive_sha=sha_stream(f)
 row={'original':str(p),'originalBytes':before.st_size,'originalSHA256':digest,'archive':str(target),'archiveBytes':target.stat().st_size,'archiveSHA256':archive_sha,'decompressedSHA256':verified,'verifiedBeforeOriginalUnlink':True};p.unlink();data['files'].append(row);data['savedBytes']=sum(q['originalBytes']-q['archiveBytes']for q in data['files']);data['diskFreeAfter']=shutil.disk_usage(ROOT).free;manifest.write_text(json.dumps(data,indent=2)+'\n');print(name,'saved',row['originalBytes']-row['archiveBytes'],'free',data['diskFreeAfter'],flush=True)
print(json.dumps({'files':len(data['files']),'savedBytes':data['savedBytes'],'diskFreeAfter':data['diskFreeAfter']}),flush=True)
