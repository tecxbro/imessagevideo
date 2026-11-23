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
expected=[*range(340,347),*range(483,622)]
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

changed=[frame for frame in range(778) if
         digest(scratch/'base-frames'/f'{frame:06}.png')!=digest(scratch/'final-frames'/f'{frame:06}.png')]
assert changed==expected,changed
measurements=[]
for frame in sorted({*changed,192,339,347,479,482,622,675,694,706,777}):
    target,old,new=[np.asarray(Image.open(path/f'{frame:06}.png').convert('RGB'),np.int16)
                    for path in (source,scratch/'base-frames',scratch/'final-frames')]
    errors=[np.abs(target-current) for current in (old,new)]
    row=dict(frame=frame,previous=float(errors[0].mean()),revised=float(errors[1].mean()),
             different=frame in changed)
    if frame in range(340,347):
        regions={'reply':(526,369,883,491),'suggestion and label':(399,464,884,614)}
    elif frame in range(483,622):
        regions={'four tile region':(135,245,880,1000)}
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

def move_ring(s):
    s['orbitActorFit']['557']['rings'][0]+=12

def edit_blue_height(s):
    s['orbitActorFit']['575']['blue'][3]*=1.11

def edit_dark_focus(s):
    s['orbitActorFit']['554']['dark'][4]*=1.5

def tilt_suggestion(s):
    s['sofiaSuggestionRegistration']['342']['messages'][1][0][-1]+=.024

def tilt_suggestion_ink(s):
    s['sofiaSuggestionRegistration']['342']['ink']['1']['slope']-=.024

def write_suggestion(s):
    s['copy']['sofia'][6][0]='Or would you like to'

check_edit(557,'ring tile horizontal position',(446,453,733,760),move_ring)
check_edit(575,'calendar tile face height',(540,408,762,684),edit_blue_height)
check_edit(554,'dark tile optical focus',(226,431,511,717),edit_dark_focus)
check_edit(342,'cyan bubble slope',(399,478,898,646),tilt_suggestion)
check_edit(342,'editable lettering slope',(452,506,830,570),tilt_suggestion_ink)
check_edit(342,'editable first suggestion line',(452,506,830,570),write_suggestion)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
