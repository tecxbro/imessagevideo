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
expected=[*range(134,138),*range(343,352)]
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

changed=[frame for frame in range(778) if
         digest(scratch/'prior-full'/f'{frame:06}.png')!=digest(scratch/'clean-frames'/f'{frame:06}.png')]
assert changed==expected,changed
measurements=[]
for frame in sorted({*changed,133,138,192,342,352,479,658,675,706,777}):
    target,old,new=[np.asarray(Image.open(path/f'{frame:06}.png').convert('RGB'),np.int16)
                    for path in (source,scratch/'prior-full',scratch/'clean-frames')]
    errors=[np.abs(target-current) for current in (old,new)]
    row=dict(frame=frame,previous=float(errors[0].mean()),revised=float(errors[1].mean()),
             different=frame in changed)
    if frame in range(134,138):
        regions={'controls':(142,373,854,600),'badge':(341,595,558,836),'bottom light':(104,891,873,1000)}
    elif frame in range(343,352):
        regions={'left rail':(0,0,120,967),'right rail':(870,0,1000,967),
                 'composer and keyboard':(65,700,950,999)}
    else:
        regions={}
    row['components']={name:[float(error[top:bottom,left:right].mean()) for error in errors]
                       for name,(left,top,right,bottom) in regions.items()}
    assert frame not in changed or row['revised']<row['previous'],row
    measurements.append(row)
(review/'stage-metrics.json').write_text(json.dumps(dict(changed_frames=changed,measurements=measurements),indent=2)+'\n')
scene=json.loads((scratch/'clean/scene.json').read_text())
prior=json.loads((scratch/'prior/scene.json').read_text())
assert scene['timeline']==prior['timeline']

edits=[]
def check_edit(frame,name,rect,apply):
    editable=deepcopy(scene)
    apply(editable)
    base=np.asarray(Image.open(scratch/'clean-frames'/f'{frame:06}.png').convert('RGB'),np.int16)
    test=np.asarray(Film(editable).frame(frame),np.int16)
    delta=np.max(np.abs(base-test),axis=2)
    ys,xs=np.where(delta!=0)
    bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    l,t,r,b=bounds
    print(name,bounds,delta.sum(),flush=True)
    assert delta.sum()>200 and rect[0]<=l and rect[1]<=t and r<=rect[2] and b<=rect[3],(name,bounds)
    edits.append(dict(frame=frame,editable=name,pixel_count=int(len(xs)),bounds=bounds))

def edit_status(s):
    s['assistantScreenRefraction']['135']['time'][1][0]+=9

def edit_badge(s):
    s['assistantScreenRegistration']['135']['badgeCalibration'][1]*=.8

def edit_caustic(s):
    s['assistantControlCaustics']['135'][0][2][0]=[30,-45,-55]

def edit_composer(s):
    s['threadRegistration']['sofia']['347']['composer']['plus'][0]+=12

def edit_key(s):
    s['threadRegistration']['sofia']['347']['keyPoses'][0][0][1][0]+=13

def edit_title(s):
    s['copy']['assistant'][0]='A different title'

check_edit(135,'generated title',(250,95,750,320),edit_title)
check_edit(135,'clock glyph refraction',(135,383,248,462),edit_status)
check_edit(135,'badge motif scale',(330,599,581,823),edit_badge)
caustic_bounds=tuple(scene['assistantControlCaustics']['135'][0][0])
check_edit(135,'local chromatic lobe',caustic_bounds,edit_caustic)
check_edit(347,'composer attachment position',(75,715,205,847),edit_composer)
check_edit(347,'keyboard glyph position',(82,867,160,930),edit_key)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
