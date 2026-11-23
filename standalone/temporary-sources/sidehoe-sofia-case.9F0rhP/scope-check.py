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
expected=[*range(319,343),504,505,506,514,515,516,521,522,523,524,525,526]
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

changed=[frame for frame in range(778) if
         digest(scratch/'base-frames'/f'{frame:06}.png')!=digest(scratch/'final-frames'/f'{frame:06}.png')]
assert changed==expected,changed
measurements=[]
for frame in sorted({*changed,192,318,343,479,503,513,520,527,557,675,694,706,777}):
    target,old,new=[np.asarray(Image.open(path/f'{frame:06}.png').convert('RGB'),np.int16)
                    for path in (source,scratch/'base-frames',scratch/'final-frames')]
    errors=[np.abs(target-current) for current in (old,new)]
    row=dict(frame=frame,previous=float(errors[0].mean()),revised=float(errors[1].mean()),
             different=frame in changed)
    if frame in range(319,343):
        y=scene['threadRegistration']['sofia'][str(frame)]['keys'][0]
        regions={'whole handset':(105,0,900,1000),'composer':(118,max(0,y-105),884,y)}
    elif frame in range(503,528):
        regions={'four tiles':(135,245,880,1000)}
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

def edit_upper_glass(s):
    s['sofiaClosedCasing']['330'][1][4]+=7

def edit_lower_metal(s):
    s['sofiaClosedCasing']['330'][0][6]+=8

def edit_volume(s):
    s['sofiaCaseButtons']['330'][0][1]+=8

def edit_placeholder(s):
    s['copy']['keyboardPrompt']='Message Sofia'

def edit_key(s):
    s['threadRegistration']['sofia']['340']['keyInkRegistration'][0][0][0]+=6

def edit_orbit(s):
    s['orbitActorFit']['522']['red'][0]+=10

check_edit(330,'top glass corner radius',(250,78,752,240),edit_upper_glass)
check_edit(330,'bottom metal corner radius',(249,839,754,1000),edit_lower_metal)
check_edit(330,'side control start',(270,264,291,323),edit_volume)
check_edit(330,'editable composer text',(365,626,460,669),edit_placeholder)
check_edit(340,'keyboard letter exposure x',(131,822,215,897),edit_key)
check_edit(522,'red tile period position',(169,346,847,883),edit_orbit)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
