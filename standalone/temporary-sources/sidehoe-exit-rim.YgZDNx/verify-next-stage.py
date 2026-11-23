"""Keep only stage improvements when extending the next candidate's support."""
from pathlib import Path
import copy
import json
import sys
import numpy as np
from PIL import Image
from render import Film

p=Path(sys.argv[1])
target=p/'follow-next/scene.json'
s=json.loads(target.read_text())
base=Film(json.loads((p/'clean-final/scene.json').read_text()))
rs=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
load=lambda name:json.loads((p/name).read_text())
casing=load('settled-casing-fit.json')
badge=load('hold-outline-fit.json')
s['assistantExitCasing'].update(casing)
s['closingBadgeOutline'].update(badge)
stage=Film(s)
result={}
for group,frames,original in (
    ('casing',range(139,153),s['assistantExitCasing']),
    ('follow',range(690,696),s['threadRegistration']['follow']),
    ('badge',range(712,766),s['closingBadgeOutline']),
):
    rows=[]
    for frame in frames:
        ref=np.asarray(Image.open(rs/f'{frame:06d}.png').convert('RGB'),np.int16)
        old,new=[float(np.abs(ref-np.asarray(film.frame(frame),np.int16)).mean()) for film in (base,stage)]
        rows.append([frame,old,new])
        if new>=old and group!='follow':
            original.pop(str(frame),None)
        elif new>=old and group=='follow':
            original[str(frame)]=copy.deepcopy(base.s['threadRegistration']['follow'][str(frame)])
    result[group]=rows
    print(group,sum(new<old for f,old,new in rows),'of',len(rows),flush=True)
(p/'next-stage-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
target.write_text(json.dumps(s,indent=2)+'\n')
