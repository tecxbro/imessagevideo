from pathlib import Path
from copy import copy
from PIL import Image
from render import Film
import json
import numpy as np
import sys

p=Path(sys.argv[1])
s=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
d=copy(s)
out={}
for f in range(698,713):
    a=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    b=np.asarray(Film(s).frame(f),dtype=np.int16)
    default=float(np.abs(a-b).mean())
    options=[(default,256)]
    for size in (320,384,448,512):
        d['closingBadgeRasterWidth']={str(f):size}
        c=np.asarray(Film(d).frame(f),dtype=np.int16)
        options.append((float(np.abs(a-c).mean()),size))
    best=min(options)
    print(f,round(default,6),tuple(round(n,6) for n in best),flush=True)
    if best[1]!=256:
        out[str(f)]=best[1]
(p/'badge-raster-probe.json').write_text(json.dumps(out,indent=2)+'\n')
