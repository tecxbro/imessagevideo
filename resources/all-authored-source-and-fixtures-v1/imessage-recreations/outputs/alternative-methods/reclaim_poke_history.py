"""Authorized deletion of superseded numbered frame histories V10–V16 only."""
from pathlib import Path
import json,hashlib,re,os,time
from collections import defaultdict
ROOT=Path('/workspace/imessage-recreations');base=ROOT/'outputs/04-poke/cache-history';out=ROOT/'outputs/alternative-methods/04-history-cleanup-ledger.json';versions=[f'v{n}'for n in range(10,17)]
# CurrentnativeV9 bytes are protected regardless of unrelated browser histories.
def native_stats():
 rows=[]
 for method in ('pillow','motion-canvas'):
  folder=ROOT/'outputs/04-poke/cache'/method
  for p in sorted(folder.glob('*.png')):
   st=p.stat();rows.append([str(p.relative_to(ROOT)),st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns])
 return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
protected_before=native_stats();records=[];inodes=defaultdict(list);folder_meta=[];started=time.monotonic()
for version in versions:
 folder=base/version
 if not folder.exists():continue
 assert folder.resolve().parent==base.resolve(),'Unexpected history symlink'
 canonical=ROOT/'outputs/04-poke'/('final-'+version)/'scene.json'
 folder_meta.append({'folder':str(folder.relative_to(ROOT)),'canonicalScene':str(canonical.relative_to(ROOT))if canonical.exists()else None,'canonicalSceneSha256':hashlib.sha256(canonical.read_bytes()).hexdigest()if canonical.exists()else None})
 for p in sorted(folder.rglob('*.png')):
  if p.is_symlink()or not re.fullmatch(r'\d{6}\.png',p.name):continue
  assert p.resolve().is_relative_to(folder.resolve())
  st=p.stat();rec={'path':str(p.relative_to(ROOT)),'bytes':st.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'device':st.st_dev,'inode':st.st_ino,'linksBefore':st.st_nlink,'allocatedBytes':st.st_blocks*512};records.append(rec);inodes[(st.st_dev,st.st_ino)].append(rec)
expected=sum(rs[0]['allocatedBytes']for rs in inodes.values()if rs[0]['linksBefore']==len(rs));metadata=[]
for p in (ROOT/'outputs/04-poke').rglob('*.render.json'):
 try:m=json.load(open(p))
 except (ValueError,OSError):continue
 version=Path(m.get('scene','')).parent.name
 if version in ['final-'+v for v in versions]:metadata.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scene':m.get('scene'),'sceneSha256':m.get('sceneSha256',m.get('sceneSHA256')),'method':m.get('method'),'frameDirectory':m.get('frameDirectory'),'capturedFrameRanges':m.get('capturedFrameRanges')})
report={'authorization':'Root delegated deletion only of regenerable old PNG histories; owner confirmedV10–V16unused andV17mustbe preserved.','versions':versions,'folders':folder_meta,'metadata':metadata,'frames':records,'frameFiles':len(records),'uniqueInodes':len(inodes),'expectedReclaimedBytes':expected,'protectedNativeStatSHA256Before':protected_before,'protected':['outputs/04-poke/cache/pillow','outputs/04-poke/cache/motion-canvas','outputs/04-poke/cache-history/v17','allcurrentlosslesscaches','sourcevideos','canonicalscenes','finalmasters','diagnosticandnonnumericPNGs','allJSONmetadata'],'status':'Hashes recorded before deletion','freeBytesBefore':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize}
def save():
 tmp=out.with_suffix('.json.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(out)
save();print('Ledgerdurable',len(records),'frames,expectedreclaim',expected,flush=True)
for rec in records:
 p=ROOT/rec['path'];st=p.stat();assert(st.st_dev,st.st_ino,st.st_size)==(rec['device'],rec['inode'],rec['bytes']);p.unlink()
report['protectedNativeStatSHA256After']=native_stats();assert report['protectedNativeStatSHA256After']==protected_before,'Protectednativecachechanged';report.update(status='Removed only recorded numberedPNG directoryentries',freeBytesAfter=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize,seconds=time.monotonic()-started);save();print({k:report[k]for k in('frameFiles','expectedReclaimedBytes','freeBytesBefore','freeBytesAfter','seconds')},flush=True)
