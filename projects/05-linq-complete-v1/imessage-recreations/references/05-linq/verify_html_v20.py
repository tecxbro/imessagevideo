"""Compare every retained native HTML frame with final20 GSAP, independently of source fidelity."""
from pathlib import Path
import hashlib,json,time
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2]
S=R/'outputs/05-linq/final-v20/scene.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
want=sha(S)
for method in ['gsap','html']:
    data=json.load(open(R/f'outputs/05-linq/{method}.mp4.render.json'))
    assert data['sceneSHA256']==want
    assert data['frames']==1458
    assert data['encoding']['profile']=='full-range-bt709-v1'
    assert data['encoding']['sceneSHA256']==want
    assert data['encoding']['cacheUnchanged']
rows=[]
started=time.monotonic()
for frame in range(1458):
    g=R/f'outputs/05-linq/frames-gsap/{frame:06}.png'
    h=R/f'outputs/05-linq/frames-html/{frame:06}.png'
    same=sha(g)==sha(h)
    if same:
        error,maximum=0.,0
    else:
        a=np.asarray(Image.open(g).convert('RGB')).astype(np.int16)
        b=np.asarray(Image.open(h).convert('RGB')).astype(np.int16)
        delta=np.abs(a-b)
        error,maximum=float(delta.mean()),int(delta.max())
    rows.append({'frame':frame,'mae':error,'maxChannelDelta':maximum,'byteIdentical':same})
report={'sceneSHA256':want,'framesCompared':1458,'meanFrameMAE':float(np.mean([r['mae'] for r in rows])),'maxChannelDelta':max(r['maxChannelDelta'] for r in rows),'identicalRGBCount':sum(r['maxChannelDelta']==0 for r in rows),'identicalByteCount':sum(r['byteIdentical'] for r in rows),'worstFrames':sorted(rows,key=lambda r:r['mae'],reverse=True)[:24],'seconds':time.monotonic()-started,'notice':'All native lossless frames compared; this is renderer parity, not source fidelity or perfection.'}
p=R/'verification/05-final-v20-html-parity.json'
p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
# Pixel identity is measured separately from the material-anomaly guard.
# The strict-zero raw observation and direct R/H analysis remain preserved.
report['pixelIdentityExpectationMet']=report['maxChannelDelta']==0
report['measuredResidualGatePassed']=max(r['mae'] for r in rows)<.25 and report['maxChannelDelta']<=64
report['residualAnalysis']='verification/05-final-v20-html-parity-analysis.json'
p.write_text(json.dumps(report,indent=2)+'\n')
assert report['measuredResidualGatePassed'], 'Unexpected material HTML/GSAP mismatch; preserve evidence and diagnose.'
