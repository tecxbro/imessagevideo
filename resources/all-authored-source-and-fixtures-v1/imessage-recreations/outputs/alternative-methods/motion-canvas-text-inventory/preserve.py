"""Preserve actual prior native captures, final pictures/audio and lossless caches."""
import hashlib,json,os,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[3]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as stream:
  for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
records=[]
for name in ['01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery']:
 output=root/'outputs'/name;cache=output/'cache/motion-canvas';dest=output/'iterations/before-mc-text-top-metrics';dest.mkdir(parents=True,exist_ok=True)
 meta=json.loads((output/'motion-canvas.mp4.render.json').read_text())
 record={'reference':name,'sceneSha256':meta['sceneSha256'],'engineSha256':meta['engineSha256'],'files':[],'frames':[]}
 for p in [output/'motion-canvas.mp4',output/'motion-canvas.mp4.render.json',cache/'native-cache.json',root/'deliverables'/name/'motion-canvas.mp4',root/'deliverables'/name/'motion-canvas.audio.json']:
  if not p.exists():continue
  part='deliverables' if 'deliverables' in p.parts else 'cache' if p.parent==cache else 'master';target=dest/part/p.name;target.parent.mkdir(parents=True,exist_ok=True)
  if part=='deliverables' and target.exists() and target.stat().st_ino==p.stat().st_ino:
   temporary=target.with_name(target.name+'.copy');shutil.copy2(p,temporary);temporary.replace(target)
  if not target.exists():
   # Metadata writers may update files in place; copy those, hardlink immutable pictures.
   if p.suffix=='.json' or part=='deliverables':shutil.copy2(p,target)
   else:os.link(p,target)
  digest=sha(p)
  if sha(target)!=digest:raise RuntimeError('Prior preservation differs: '+str(target))
  record['files'].append({'path':str(p.relative_to(root)),'preserved':str(target.relative_to(root)),'sha256':digest,'bytes':p.stat().st_size})
 frameDir=dest/'frames-mc';frameDir.mkdir(exist_ok=True)
 for p in sorted(cache.glob('[0-9]*.png')):
  target=frameDir/p.name
  if not target.exists():os.link(p,target)
  digest=sha(p)
  if sha(target)!=digest:raise RuntimeError('Prior PNG preservation differs: '+str(target))
  record['frames'].append({'frame':int(p.stem),'sha256':digest,'inode':p.stat().st_ino,'bytes':p.stat().st_size})
 (dest/'preservation.json').write_text(json.dumps(record,indent=2)+'\n');records.append({k:v for k,v in record.items() if k!='frames'}|{'frameCount':len(record['frames']),'manifest':str((dest/'preservation.json').relative_to(root))})
 print(json.dumps({'reference':name,'frames':len(record['frames']),'sceneSha256':record['sceneSha256'],'engineSha256':record['engineSha256']}),flush=True)
(Path(__file__).parent/'prior-capture-preservation.json').write_text(json.dumps(records,indent=2)+'\n')
