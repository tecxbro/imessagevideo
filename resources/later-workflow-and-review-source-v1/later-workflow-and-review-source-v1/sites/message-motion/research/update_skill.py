from pathlib import Path
import zipfile,json,hashlib,os
project=Path('/workspace/imessage-recreations');skill=project/'skill/imessage-motion-recreation'
source_zip=project/'imessage-motion-recreation-skill.zip';out=project/'imessage-motion-recreation-skill-public-update.zip';prefix='imessage-motion-recreation/'
with zipfile.ZipFile(source_zip) as src:files={n:src.read(n) for n in src.namelist() if not n.endswith('/') and n!=prefix+'checksums.json'}
for name in ['SKILL.md','references/execution-ledger.md','references/public-gallery-distribution.md']:files[prefix+name]=(skill/name).read_bytes()
script=Path('/workspace/sites/message-motion/verification/check_public.py').read_text().replace("root=Path('/workspace/sites/message-motion');base=sys.argv[1].rstrip('/');dist=root/'dist'","root=Path(sys.argv[2]) if len(sys.argv)>2 else Path.cwd();base=sys.argv[1].rstrip('/');dist=root/'dist'")
files[prefix+'scripts/check_public_review.py']=script.encode()
for dest,src in [('references/public-gallery/player-app.js',Path('/workspace/sites/message-motion/dist/app.js')),('references/public-gallery/reference-bridge.html',Path('/workspace/sites/message-motion-originals/dist/bridge.html')),('references/public-gallery/bridge.test.mjs',Path('/workspace/sites/message-motion-originals/tests/bridge.test.mjs')),('references/public-gallery/publication.audit.json',Path('/workspace/sites/message-motion/verification/publication.json')),('references/public-gallery/public-delivery.json',Path('/workspace/sites/message-motion/verification/public-delivery.json')),('references/public-gallery/public-assets.json',Path('/workspace/sites/message-motion/verification/public-assets.json'))]:
 files[prefix+dest]=src.read_bytes()
 for folder in [skill,Path('/workspace/.agents/skills/imessage-motion-recreation')]:
  path=folder/dest;path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_bytes(src.read_bytes());os.replace(tmp,path)
checks={n[len(prefix):]:hashlib.sha256(data).hexdigest() for n,data in sorted(files.items())}
files[prefix+'checksums.json']=(json.dumps(checks,indent=2)+'\n').encode()
tmp=out.with_suffix('.tmp')
with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,data in sorted(files.items()):z.writestr(name,data)
os.replace(tmp,out)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)
 for rel,sha in checks.items():assert hashlib.sha256(z.read(prefix+rel)).hexdigest()==sha
 for name in z.namelist():assert not name.lower().endswith(('.mp4','.mov','.woff','.woff2','.ttf','.otf'))
for folder in [skill,Path('/workspace/.agents/skills/imessage-motion-recreation')]:
 p=folder/'scripts/check_public_review.py';p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix('.tmp');t.write_text(script);os.replace(t,p)
 payloads={str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'checksums.json'}
 p=folder/'checksums.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(payloads,indent=2)+'\n');os.replace(t,p)
report={'path':str(out),'files':len(files),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'all_checksums_pass':True,'source_only':True,'original_frozen_skill_archive_unchanged':True}
Path('/workspace/sites/message-motion/verification/updated-skill.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
