"""Verify retained-cache scope against immutable pre-mapping native evidence."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parents[3];out=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in sys.argv[1:]:
 folder=root/'outputs'/name;meta=json.loads((folder/'motion-canvas.mp4.render.json').read_text());base=folder/'iterations/before-mc-rms-font';old=json.loads((base/'preservation.json').read_text());ranges=meta['capturedFrameRanges'];selected={f for a,b in ranges for f in range(a,b+1)};rows=[];outside=[]
 assert meta['engineSha256']=='7080c58ce151d1966b44671dc9db0801f81cb514200a3e8ed8a6cd1401777195'
 for row in old['frames']:
  f=row['frame'];p=folder/'cache/motion-canvas'/f'{f:06}.png';before=base/'frames-mc'/p.name;digest=sha(p);previous=sha(before)
  assert previous==row['sha256'],'Historical backup changed'
  if f not in selected:assert digest==previous and p.stat().st_ino==row['inode'],'Outside cache changed';outside.append(f)
  rows.append({'frame':f,'sha256':digest,'sameBytesAsBefore':digest==previous,'inode':p.stat().st_ino})
 assert len(rows)==meta['frames']
 result={'reference':name,'sceneSha256':meta['sceneSha256'],'engineSha256':meta['engineSha256'],'actualPreviousSceneSha256':old['sceneSha256'],'actualPreviousEngineSha256':old['engineSha256'],'captureRanges':ranges,'capturedFrames':len(selected),'uniqueFramesCaptured':meta['uniqueFramesCaptured'],'retainedPngCount':len(rows),'outsideFrames':len(outside),'outsideHashAndInodesIdentical':True,'historicalBackupsUnchanged':True,'actualChangedPngBytes':sum(not r['sameBytesAsBefore'] for r in rows),'nativePictureSHA256':sha(folder/'motion-canvas.mp4'),'metadata':str(folder/'motion-canvas.mp4.render.json'),'frames':rows}
 (out/(name+'-rms-cache-proof.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='frames'}),flush=True)
