from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from PIL import Image
import json
import sys
import numpy as np

scratch,review=map(Path,sys.argv[1:])
sys.path.insert(0,str(scratch/'clean'))
from render import Film

source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
scene=json.loads((scratch/'clean/scene.json').read_text())
expected=sorted({*range(139,162),*range(690,696),*map(int,scene['closingBadgeArtwork'])})
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

changed=[frame for frame in range(778) if
         digest(scratch/'base-frames'/f'{frame:06}.png')!=digest(scratch/'final-frames'/f'{frame:06}.png')]
assert changed==expected,changed
measurements=[]
for frame in sorted({*changed,138,162,192,347,479,675,689,696,700,775,777}):
    target,old,new=[np.asarray(Image.open(path/f'{frame:06}.png').convert('RGB'),np.int16)
                    for path in (source,scratch/'base-frames',scratch/'final-frames')]
    errors=[np.abs(target-current) for current in (old,new)]
    row=dict(frame=frame,previous=float(errors[0].mean()),revised=float(errors[1].mean()),
             different=frame in changed)
    if frame in range(139,162):
        l,t,r,b=scene['assistantSpeakerSlot'][str(frame)][0]
        regions={'casing':(32,max(0,t-15),970,min(1000,t+165)),'speaker':(l,t,r,b)}
    elif frame in range(690,696):
        regions={'keyboard':(100,652,900,1000),'contact controls':(130,500,690,655)}
    elif frame in range(701,777):
        regions={'badge and artwork':(340,330,660,640)}
    else:
        regions={}
    row['components']={name:[float(error[top:bottom,left:right].mean()) for error in errors]
                       for name,(left,top,right,bottom) in regions.items()}
    assert frame not in changed or row['revised']<row['previous'],row
    measurements.append(row)
(review/'stage-metrics.json').write_text(json.dumps(dict(changed_frames=changed,measurements=measurements),indent=2)+'\n')
scene=json.loads((scratch/'clean/scene.json').read_text())
prior=json.loads((scratch/'base/scene.json').read_text())
assert scene['timeline']==prior['timeline']

edits=[]
def check_edit(frame,name,rect,apply):
    editable=deepcopy(scene)
    apply(editable)
    base=np.asarray(Image.open(scratch/'final-frames'/f'{frame:06}.png').convert('RGB'),np.int16)
    test=np.asarray(Film(editable).frame(frame),np.int16)
    delta=np.max(np.abs(base-test),axis=2)
    ys,xs=np.where(delta!=0)
    bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    l,t,r,b=bounds
    print(name,bounds,delta.sum(),flush=True)
    assert delta.sum()>200 and rect[0]<=l and rect[1]<=t and r<=rect[2] and b<=rect[3],(name,bounds)
    edits.append(dict(frame=frame,editable=name,pixel_count=int(len(xs)),bounds=bounds))

def edit_slot(s):
    s['assistantSpeakerSlot']['152'][1][0]+=18

def edit_key(s):
    s['threadRegistration']['follow']['691']['keyPoses'][0][0][1][0]+=8

def edit_lip(s):
    s['assistantSpeakerSlot']['152'][2][1]=[51,40,49]

def edit_card(s):
    s['closingBadgeArtwork']['706'][2][0]+=12

def edit_heart(s):
    s['closingBadgeArtwork']['706'][3][1]+=12

def edit_outline(s):
    s['closingBadgeOutline']['732'][4]+=9

slot_bounds=tuple(scene['assistantSpeakerSlot']['152'][0])
check_edit(152,'speaker position',slot_bounds,edit_slot)
check_edit(152,'speaker lip highlight',slot_bounds,edit_lip)
check_edit(691,'keyboard glyph',(148,740,238,808),edit_key)
check_edit(706,'center card position',(439,430,560,541),edit_card)
check_edit(706,'badge heart position',(457,505,549,587),edit_heart)
check_edit(732,'badge corner radius',(391,328,611,553),edit_outline)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
