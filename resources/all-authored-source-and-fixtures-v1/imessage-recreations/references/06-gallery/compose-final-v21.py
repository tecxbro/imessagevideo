"""Compose only accepted portrait03 into source06; retain all native20 evidence."""
from pathlib import Path
import json,hashlib,os,shutil,re,subprocess,time
R=Path('/workspace/imessage-recreations');REF=R/'references/06-gallery';OUT=R/'outputs/06-gallery';V20=OUT/'final-v20/scene.json';V21=OUT/'final-v21';Q=R/'verification/final/06-gallery/v21';Q.mkdir(parents=True,exist_ok=True)
expected='f540deb32ed3710e9de6f5d20c5ce7583a215283d77070428671e8e2800b220d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(V20)==expected
if (V21/'scene.json').exists():raise RuntimeError('Unique final-v21 already exists; do not overwrite')
backup=OUT/'iterations/final-v20-before-v21';backup.mkdir(parents=True,exist_ok=True);records=[]
for method in ['gsap','remotion','html','pillow','motion-canvas']:
 picture=OUT/f'{method}.mp4';sidecar=Path(str(picture)+'.render.json');meta=json.load(open(sidecar));assert meta.get('sceneSHA256',meta.get('sceneSha256'))==expected,(method,'not20');assert meta['frames']==1483
 cache=Path(meta['frameDirectory']);target=backup/'cache'/method;target.mkdir(parents=True,exist_ok=True);inventory=[];hashes={}
 for f in range(1483):
  file=cache/f'{f:06}.png';stat=file.stat();key=(stat.st_dev,stat.st_ino)
  if key not in hashes:hashes[key]=sha(file)
  dest=target/file.name
  if not dest.exists():os.link(file,dest)
  assert sha(dest)==hashes[key]
  inventory.append(dict(frame=f,sha256=hashes[key],bytes=stat.st_size))
 for file in [picture,sidecar]:
  dest=backup/file.name
  if not dest.exists():
   if file==picture:os.link(file,dest)
   else:shutil.copy2(file,dest)
  assert sha(dest)==sha(file)
 native_meta=cache/'native-cache.json'
 if native_meta.exists()and not(target/'native-cache.json').exists():shutil.copy2(native_meta,target/'native-cache.json')
 rec=dict(method=method,picture=str(picture),pictureSHA256=sha(picture),sidecarSHA256=sha(sidecar),frameDirectory=str(cache),backupCache=str(target),cacheFrames=inventory);records.append(rec)
(backup/'preservation.json').write_text(json.dumps(dict(sceneSHA256=expected,records=records),indent=2));(Q/'preserved-v20.json').write_text(json.dumps(dict(sceneSHA256=expected,backup=str(backup),methods=[{k:v for k,v in r.items()if k!='cacheFrames'}for r in records]),indent=2))
author=REF/'scene-final-v21-composed.json';subprocess.run(['python',str(REF/'apply-portrait614-review.py'),'--input',str(V20),'--elements',str(OUT/'portrait614-review-03/portrait614-review-elements.json'),'--output',str(author)],check=True,stdout=subprocess.DEVNULL)
s=json.load(open(author));pool=REF/'assets/final-v21-normalized';pool.mkdir(parents=True,exist_ok=True);assets={}
def normalize(src):
 if src.startswith('data:'):return src
 if src.startswith(('https:','http:')):raise ValueError('Remote dependency')
 file=Path(src);file=file if file.is_absolute()else author.parent/file;data=file.read_bytes();digest=hashlib.sha256(data).hexdigest();name=re.sub(r'^(?:[a-f0-9]{16}-)+','',file.name);dest=pool/digest/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():dest.write_bytes(data)
 assert sha(dest)==digest;assets[str(dest)]=dict(original=str(file),sha256=digest);return str(dest)
def walk(ls):
 for n in ls:
  if n.get('src'):n['src']=normalize(n['src'])
  assert not n.get('keyframes',{}).get('src'),'Unexpected animated src requires explicit immutable normalization'
  walk(n.get('children',[]))
walk(s['layers'])
for f in s.get('fonts',[]):f['src']=normalize(f['src'])
s['source']['notes']+=' Finalv21 applies the accepted independent portrait03 source correction at native frames613–621 only. All other20 source states retain identical evaluated graphics. Brief genuine photographed optical materials preserve separate native actors/cameras/clips; projected RGB/soft alpha/shadow is rasterized. Remaining material/optical/AA differences are disclosed; no100% match claim.'
author.write_text(json.dumps(s,indent=2)+'\n');(Q/'normalized-assets.json').write_text(json.dumps(assets,indent=2));subprocess.run(['python',str(R/'engines/snapshot_scene.py'),str(author),str(V21)],check=True);(Q/'composition.json').write_text(json.dumps(dict(baseSHA256=expected,portraitPayloadSHA256=sha(OUT/'portrait614-review-03/portrait614-review-elements.json'),authoring=str(author),scene=str(V21/'scene.json'),sceneSHA256=sha(V21/'scene.json'),sourceDelta=[[613,621]],normalizedAssets=len(assets)),indent=2));print(json.dumps(dict(scene=str(V21/'scene.json'),sceneSHA256=sha(V21/'scene.json'),normalizedAssets=len(assets),preservedBackup=str(backup))))
