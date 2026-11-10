"""Compose approved scoped helpers and freeze a portable content-addressed scene."""
from pathlib import Path
import json,hashlib,importlib.util,shutil,mimetypes
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent;BASE=ROOT/'outputs/02-danieltian/final-v13/scene.json';DEST=ROOT/'outputs/02-danieltian/final-v14';AUTHOR=REF/'scene-merged-v14.json'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
assert sha(BASE)=='a896028ccd61f354f4177d231d4e790eee16107c48ab6243c0394133edf98796'
if DEST.exists():raise FileExistsError('Unique immutable snapshot already exists: '+str(DEST))
scene=json.loads(BASE.read_text())
def absolute(n):
 if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((BASE.parent/n['src']).resolve())
 for c in n.get('children',[]):absolute(c)
for n in scene['layers']+scene.get('fonts',[]):absolute(n)
functions=[('apply-phonebook-grid-review.py','apply_phonebook'),('apply-root-send-flight.py','apply_send'),('apply-root-orbit.py','apply_orbit'),('apply-root-header-birth-v3.py','apply_birth')];helpers=[]
for i,(file,function)in enumerate(functions):
 path=REF/file;before=sha(path);s=importlib.util.spec_from_file_location('approved_v14_'+str(i),path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);scene=getattr(m,function)(scene);assert sha(path)==before;helpers.append({'file':str(path),'function':function,'sha256':before});print('applied',function,flush=True)
assert len(scene['layers'])==len({n['id']for n in scene['layers']});assert scene['width']==1920 and scene['height']==1080 and scene['fps']==30 and round(scene['duration']*scene['fps'])==1360
with AUTHOR.open('w')as f:json.dump(scene,f,separators=(',',':'))
DEST.mkdir();(DEST/'assets').mkdir();cache={};assets=[];counts={}
def copy_asset(src):
 if src.startswith('data:'):return src
 if src.startswith(('http:','https:')):raise ValueError('Unfrozen remote asset '+src)
 source=Path(src)
 if not source.is_absolute():raise ValueError('New helper asset path is not absolute: '+src)
 source=source.resolve()
 if source in cache:
  counts[str(source)]+=1;return cache[source]
 digest=sha(source);suffix=source.suffix.lower()or'.bin';rel=Path('assets')/(digest+suffix);target=DEST/rel
 if not target.exists():shutil.copyfile(source,target)
 assert sha(target)==digest
 cache[source]=str(rel);counts[str(source)]=1;assets.append({'original':str(source),'snapshot':str(rel),'sha256':digest,'bytes':source.stat().st_size});return str(rel)
def freeze(n):
 if n.get('src'):n['src']=copy_asset(n['src'])
 for c in n.get('children',[]):freeze(c)
for n in scene['layers']+scene.get('fonts',[]):freeze(n)
with(DEST/'scene.json').open('w')as f:json.dump(scene,f,indent=2);f.write('\n')
for a in assets:a['references']=counts[a['original']]
manifest={'original':str(AUTHOR),'original_sha256':sha(AUTHOR),'snapshot_sha256':sha(DEST/'scene.json'),'base':str(BASE),'base_sha256':sha(BASE),'ordered_helpers':helpers,'assets':assets,'assetNaming':'FullSHA256 plus original media suffix; avoids nested snapshot basename growth while preserving every asset byte.','conservativeCaptureRanges':[[175,179],[436,524],[548,597]],'conservativeCaptureFrameCount':144};(DEST/'snapshot.json').write_text(json.dumps(manifest,indent=2)+'\n');assert all(sha(DEST/a['snapshot'])==a['sha256']for a in assets);(DEST/'asset-proof.json').write_text(json.dumps({'allAssetsVerified':True,'uniqueSourceAssetPaths':len(assets),'uniqueSnapshotAssets':len(set(a['snapshot']for a in assets)),'totalReferences':sum(counts.values()),'missingAssets':[],'sceneSHA256':manifest['snapshot_sha256'],'helpersStableDuringComposition':True},indent=2)+'\n');print(json.dumps({'scene':str(DEST/'scene.json'),'SHA256':manifest['snapshot_sha256'],'assets':len(assets),'frames':1360,'scope':manifest['conservativeCaptureRanges']}),flush=True)
