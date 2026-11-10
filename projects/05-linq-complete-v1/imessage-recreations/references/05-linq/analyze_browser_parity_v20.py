"""Classify measured HTML/GSAP differences without claiming pixel identity."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path.cwd()
ranges=json.load(open('verification/05-v20-method-deltas.json'))['methods']['html']['ranges']
fresh={f for a,b in ranges for f in range(a,b+1)}
rows=[]
def rgb(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
for f in range(1458):
    g=R/f'outputs/05-linq/frames-gsap/{f:06}.png'
    h=R/f'outputs/05-linq/frames-html/{f:06}.png'
    if hashlib.sha256(g.read_bytes()).digest()==hashlib.sha256(h.read_bytes()).digest():
        continue
    a,b=rgb(g),rgb(h)
    error=np.abs(a-b)
    if not error.max():
        continue
    c=rgb(R/f'outputs/05-linq/frames-remotion/{f:06}.png')
    rh=np.abs(c-b)
    rows.append({'frame':f,'htmlVsGsapMAE':float(error.mean()),'htmlVsGsapMax':int(error.max()),'htmlVsRemotionMAE':float(rh.mean()),'htmlVsRemotionMax':int(rh.max()),'freshlyRefreshedHTML':f in fresh})
report={'framesCompared':1458,'htmlRefreshedFrames':len(fresh),'differingFrames':rows,'htmlDifferencesInRefreshedRange':[r for r in rows if r['freshlyRefreshedHTML']],'htmlDifferencesMatchingRemotionExactly':sum(r['htmlVsRemotionMax']==0 for r in rows),'largeMaterialDifferenceCandidates':[r for r in rows if r['htmlVsGsapMAE']>.25 or r['htmlVsGsapMax']>64],'notice':'All differences are reported. The former strict zero-pixel expectation failed; this analysis distinguishes retained small samples from a material blank frame. It does not silently assert pixel identity or replace the source fidelity gate.'}
Path('verification/05-final-v20-html-parity-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='differingFrames'},indent=2))
