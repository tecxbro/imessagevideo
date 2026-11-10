"""Verify every retained lossless primary frame and the repaired R625 cache."""
from pathlib import Path
import json,hashlib,time
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];S=R/'outputs/05-linq/final-v19/scene.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();want=sha(S)
for method in ['gsap','remotion']:
 d=json.loads((R/f'outputs/05-linq/{method}.mp4.render.json').read_text());assert d['sceneSHA256']==want;assert d['frames']==1458;assert d['encoding']['profile']=='full-range-bt709-v1';assert d['encoding']['sceneSHA256']==want;assert d['encoding']['cacheUnchanged']
G=R/'outputs/05-linq/frames-gsap';M=R/'outputs/05-linq/frames-remotion';rows=[];byte_matches=0;t=time.monotonic()
for f in range(1458):
 g=G/f'{f:06d}.png';m=M/f'{f:06d}.png';gh=sha(g);mh=sha(m)
 if gh==mh:byte_matches+=1;mae=0.;maximum=0
 else:
  a=np.asarray(Image.open(g).convert('RGB')).astype(np.int16);b=np.asarray(Image.open(m).convert('RGB')).astype(np.int16);delta=np.abs(a-b);mae=float(delta.mean());maximum=int(delta.max())
 rows.append({'frame':f,'mae':mae,'maxChannelDelta':maximum,'byteIdentical':gh==mh})
fix=rows[625];assert fix['mae']<.02,('Material R625 defect persists',fix)
report={'scene':str(S.relative_to(R)),'sceneSHA256':want,'framesCompared':1458,'nativeDimensions':[960,720],'method':'Identical file SHA256 proves identical pixels; other PNGs are decoded to RGB and compared. Every frame is covered.','identicalByteCount':byte_matches,'identicalRGBCount':sum(r['maxChannelDelta']== 0 for r in rows),'meanFrameMAE':float(np.mean([r['mae']for r in rows])),'maxChannelDelta':max(r['maxChannelDelta']for r in rows),'changedFrames':[r for r in rows if r['maxChannelDelta']>0],'worstFrames':sorted(rows,key=lambda r:r['mae'],reverse=True)[:24],'cache625Repair':dict(fix,legacyEvidence='verification/05-raster-parity-625/legacy-remotion625.png',newRemotionSHA256=sha(M/'000625.png'),gsapSHA256=sha(G/'000625.png')),'seconds':time.monotonic()-t,'notice':'This is independent-renderer lossless parity, not source fidelity or a perfection percentage. The original legacy truncation cause remains unproven.'}
p=R/'verification/05-final-v19-primary-parity.json';p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['changedFrames','worstFrames']},indent=2));print(json.dumps(report['worstFrames'][:6],indent=2))
