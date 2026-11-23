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
expected=[*range(139,162),*range(691,696)]
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

changed=[frame for frame in range(778) if
         digest(scratch/'base-frames'/f'{frame:06}.png')!=digest(scratch/'final-frames'/f'{frame:06}.png')]
assert changed==expected,changed
measurements=[]
for frame in sorted({*changed,138,162,192,342,347,479,675,690,696,706,777}):
    target,old,new=[np.asarray(Image.open(path/f'{frame:06}.png').convert('RGB'),np.int16)
                    for path in (source,scratch/'base-frames',scratch/'final-frames')]
    errors=[np.abs(target-current) for current in (old,new)]
    row=dict(frame=frame,previous=float(errors[0].mean()),revised=float(errors[1].mean()),
             different=frame in changed)
    if frame in range(139,162):
        y=round(scene['assistantExitCasing'][str(frame)][0][1])
        regions={'glass near the camera':(205,y+23,796,y+70)}
    elif frame in range(691,696):
        y=scene['threadRegistration']['follow'][str(frame)]['keys'][0]
        regions={'keyboard':(127,y,883,1000),'middle key row':(175,y+91,841,min(1000,y+204))}
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

def adjust_clearance(s):
    s['assistantCasingGlass']['152'][0]+=.18

def move_letter(s):
    s['threadRegistration']['follow']['694']['keyInkRegistration'][0][0][0]+=5

def shear_letter(s):
    s['threadRegistration']['follow']['694']['keyInkRegistration'][0][0][4]+=.23

def extend_shutter(s):
    s['threadRegistration']['follow']['694']['keyInkRegistration'][0][0][7]+=6

def adjust_key_face(s):
    s['threadRegistration']['follow']['694']['keyPoses'][0][0][0][2]+=6

def move_last_letter(s):
    s['threadRegistration']['follow']['695']['keyInkRegistration'][1][2][1]+=5

check_edit(152,'central glass feather',(166,465,834,532),adjust_clearance)
check_edit(694,'Q letter x position',(193,700,260,779),move_letter)
check_edit(694,'Q letter shear',(193,700,260,779),shear_letter)
check_edit(694,'Q letter shutter',(191,696,263,785),extend_shutter)
check_edit(694,'Q key face width',(180,692,270,796),adjust_key_face)
check_edit(695,'D letter y position',(366,741,436,803),move_last_letter)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
