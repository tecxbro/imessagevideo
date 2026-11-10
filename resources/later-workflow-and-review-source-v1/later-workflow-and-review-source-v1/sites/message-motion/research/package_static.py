from pathlib import Path
import sys,subprocess,json,tarfile,hashlib,os
root=Path(sys.argv[1]);name=sys.argv[2];sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
if subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip():raise RuntimeError('Dirty source')
paths=['.openai/hosting.json']+[str(p.relative_to(root)) for p in sorted((root/'dist').rglob('*')) if p.is_file()]
for path in paths:
 if (root/path).read_bytes()!=subprocess.check_output(['git','show',sha+':'+path],cwd=root):raise RuntimeError('Uncommitted static file '+path)
out=root/name;temp=out.with_suffix(out.suffix+'.tmp')
with tarfile.open(temp,'w:gz',compresslevel=6) as z:
 for path in paths:z.add(root/path,arcname=path,recursive=False)
os.replace(temp,out)
if out.stat().st_size>=256*1024*1024:raise RuntimeError('Input archive exceeds documented limit')
with tarfile.open(out,'r:gz') as z:
 assert z.getnames()==paths
 for m in z:
  assert m.isfile()
  if hashlib.sha256(z.extractfile(m).read()).digest()!=hashlib.sha256((root/m.name).read_bytes()).digest():raise RuntimeError('Archive hash mismatch '+m.name)
report={'project_id':json.loads((root/'.openai/hosting.json').read_text())['project_id'],'commit_sha':sha,'archive':str(out),'archive_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'files':len(paths),'all_committed_payloads_verified':True}
(root/'verification/source-package.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
