from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys

import numpy as np
from PIL import Image

p,review=map(Path,sys.argv[1:])
sys.path.insert(0,str(p/'clean'))
from render import Film
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
expected=[*range(42,60),*range(134,152),*range(473,478)]
def digest(x): return sha256(x.read_bytes()).hexdigest()
changed=[f for f in range(778) if digest(p/'prior-full'/f'{f:06}.png')!=digest(p/'clean-frames'/f'{f:06}.png')]
assert changed==expected,changed
metrics=[]
for f in [*changed,41,60,133,152,192,472,478,706,777]:
    target,old,new=[np.asarray(Image.open(path/f'{f:06}.png').convert('RGB'),np.int16)
                    for path in (source,p/'prior-full',p/'clean-frames')]
    a,b=np.abs(target-old),np.abs(target-new)
    row=dict(frame=f,previous=float(a.mean()),revised=float(b.mean()),different=f in changed)
    regions={
        47: {'chrome':(140,90,862,568),'scrolling_rows':(160,555,865,1000)},
        135: {'camera_and_glass':(318,307,661,500)},
        141: {'personal_title':(303,188,689,340),'pins':(118,696,864,920)},
        476: {'calendar_appointments':(135,350,952,637),'lower_grid':(130,635,950,996)},
    }
    if f in regions:
        row['components']={k:[float(p[t:bot,l:r].mean()) for p in (a,b)]
                           for k,(l,t,r,bot) in regions[f].items()}
    assert f not in changed or row['revised']<row['previous'],row
    metrics.append(row)
(review/'stage-metrics.json').write_text(json.dumps(dict(changed_frames=changed,measurements=metrics),indent=2)+'\n')
scene=json.loads((p/'clean/scene.json').read_text())
prior=json.loads((p/'prior/scene.json').read_text())
assert scene['timeline']==prior['timeline']

edits=[]
def check_edit(frame,name,rect,apply):
    editable=deepcopy(scene)
    apply(editable)
    previous=np.asarray(Image.open(p/'clean-frames'/f'{frame:06}.png').convert('RGB'),np.int16)
    revised=np.asarray(Film(editable).frame(frame),np.int16)
    delta=np.max(np.abs(previous-revised),axis=2)
    ys,xs=np.where(delta!=0)
    bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    l,t,r,b=bounds
    assert delta.sum()>200 and rect[0]<=l and rect[1]<=t and r<=rect[2] and b<=rect[3],(name,bounds)
    edits.append(dict(frame=frame,editable=name,pixel_count=int(len(xs)),bounds=bounds))

def shift_rows(s): s['inboxScrollRegistration']['47']['rowExposure'][3]+=6
def slide_island(s): s['assistantIslandRegistration']['135']['opening'][0]+=7
def edit_disk(s): s['assistantScreenRegistration']['141']['pinDiskLighting'][0][0]='#dbb187'
def edit_wipe(s): s['calendarDeparture']['476']['removed'][5][0]+=15
check_edit(47,'inbox message rows', (140,546,869,1000),shift_rows)
check_edit(135,'camera opening', (341,342,670,488),slide_island)
check_edit(141,'assistant lower title', (355,254,649,349),lambda s:s['copy']['assistant'].__setitem__(1,'companion'))
check_edit(141,'Marie disk lighting',(116,693,339,934),edit_disk)
check_edit(476,'calendar wipe cell',(468,460,505,585),edit_wipe)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
print(edits)
