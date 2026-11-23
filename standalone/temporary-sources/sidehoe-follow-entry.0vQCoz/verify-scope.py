import hashlib
import os
from pathlib import Path
import sys
import numpy as np
from PIL import Image

old=Path('/tmp/sidehoe-phone.tJtcYo/final-frames')
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
new=Path(sys.argv[1])
paths=[f'{n:06}.png' for n in range(778)]
assert all(sorted(p.name for p in folder.glob('*.png'))==paths for folder in (old,new))
def digest(path):
    return hashlib.sha256(path.read_bytes()).digest()
changed=[i for i,n in enumerate(paths) if digest(old/n)!=digest(new/n)]
assert changed==list(range(631,660)), changed
print('All 749 authored control frames are byte-identical.')
for f in changed:
    name=paths[f]
    a,b,c=[np.asarray(Image.open(r/name),dtype=np.int16) for r in (source,old,new)]
    before,after=[float(np.abs(a-k).mean()) for k in (b,c)]
    assert after<before, (f,before,after)
print('All 29 edited frames improve lossless stage RGB error.')
pointer=[]
for f in range(646,660):
    name=paths[f]
    a,b,c=[np.asarray(Image.open(r/name).crop((847,315,945,515)),dtype=np.int16)
           for r in (source,old,new)]
    before,after=[float(np.abs(a-k).mean()) for k in (b,c)]
    pointer.append((f,round(before,5),round(after,5)))
print('Lossless isolated pointer MAE by frame',pointer)
