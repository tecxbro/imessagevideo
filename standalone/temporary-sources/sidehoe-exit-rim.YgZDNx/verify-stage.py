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
expected=[*range(153,162),*range(701,712)]
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

changed=[frame for frame in range(778) if
         digest(scratch/'base-full'/f'{frame:06}.png')!=digest(scratch/'clean-frames'/f'{frame:06}.png')]
assert changed==expected,changed
measurements=[]
for frame in sorted({*changed,152,162,192,347,479,675,700,712,777}):
    target,old,new=[np.asarray(Image.open(path/f'{frame:06}.png').convert('RGB'),np.int16)
                    for path in (source,scratch/'base-full',scratch/'clean-frames')]
    errors=[np.abs(target-current) for current in (old,new)]
    row=dict(frame=frame,previous=float(errors[0].mean()),revised=float(errors[1].mean()),
             different=frame in changed)
    if frame in range(153,162):
        regions={'top reflection':(135,440,870,605),'left shoulder':(35,447,237,770),
                 'right shoulder':(770,447,970,770),'screen controls':(112,500,868,837)}
    elif frame in range(701,712):
        regions={'badge':(360,350,640,640)}
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
    base=np.asarray(Image.open(scratch/'clean-frames'/f'{frame:06}.png').convert('RGB'),np.int16)
    test=np.asarray(Film(editable).frame(frame),np.int16)
    delta=np.max(np.abs(base-test),axis=2)
    ys,xs=np.where(delta!=0)
    bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    l,t,r,b=bounds
    print(name,bounds,delta.sum(),flush=True)
    assert delta.sum()>200 and rect[0]<=l and rect[1]<=t and r<=rect[2] and b<=rect[3],(name,bounds)
    edits.append(dict(frame=frame,editable=name,pixel_count=int(len(xs)),bounds=bounds))

def edit_outer(s):
    s['assistantExitCasing']['160'][0][3]+=15

def edit_glass(s):
    s['assistantExitCasing']['160'][1][4]+=15

def edit_bevel_light(s):
    s['assistantExitCasing']['160'][4][5][11]=[147,109,122]

def edit_clock(s):
    sh=s['assistantScreenRefraction']['160']['time'][1]
    sh[-2]+=6
    sh[-1]=.85

def edit_badge(s):
    s['closingBadgeOutline']['706'][4]+=9

check_edit(160,'outer shoulder radius',(0,500,1000,816),edit_outer)
check_edit(160,'glass opening radius',(0,500,1000,816),edit_glass)
check_edit(160,'upper bevel light ramp',(340,510,790,788),edit_bevel_light)
check_edit(160,'clock glyph shutter',tuple(scene['assistantScreenRefraction']['160']['time'][0]),edit_clock)
check_edit(706,'badge shoulder radius',(372,371,629,627),edit_badge)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
