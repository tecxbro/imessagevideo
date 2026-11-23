from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np

p,review=map(Path,sys.argv[1:])
sys.path.insert(0,str(p/'clean'))
from render import Film
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
expected=[*range(478,483),*range(630,671)]
def digest(x): return sha256(x.read_bytes()).hexdigest()
changed=[f for f in range(778) if digest(p/'prior-full'/f'{f:06}.png')!=digest(p/'clean-frames'/f'{f:06}.png')]
assert changed==expected,changed
metrics=[]
for f in [*changed,192,477,483,629,671,674,675,706,777]:
    target,old,new=[np.asarray(Image.open(path/f'{f:06}.png').convert('RGB'),np.int16)
                    for path in (source,p/'prior-full',p/'clean-frames')]
    a,b=np.abs(target-old),np.abs(target-new)
    row=dict(frame=f,previous=float(a.mean()),revised=float(b.mean()),different=f in changed)
    regions={
        478: {'calendar_and_ring':(297,355,841,628)},
        648: {'no_appearance':(338,478,412,522)},
        658: {'left_bevel':(249,180,291,891),'right_bevel':(709,180,752,891),
              'upper_bevel':(353,0,645,28),'keyboard':(277,633,726,966),
              'no_and_yes':(305,495,515,552),'message_ink':(309,180,719,487)},
        667: {'camera_push':(113,0,886,998)},
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
    base=np.asarray(Image.open(p/'clean-frames'/f'{frame:06}.png').convert('RGB'),np.int16)
    new=np.asarray(Film(editable).frame(frame),np.int16)
    delta=np.max(np.abs(base-new),axis=2)
    ys,xs=np.where(delta!=0)
    bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    l,t,r,b=bounds
    assert delta.sum()>200 and rect[0]<=l and rect[1]<=t and r<=rect[2] and b<=rect[3],(name,bounds)
    edits.append(dict(frame=frame,editable=name,pixel_count=int(len(xs)),bounds=bounds))
def ring(s): s['orbitArrivalExposure']['478']['rings'][0]+=6
def edit_no(s): s['copy']['follow'][4]='Go {cry}'
def edit_reply(s): s['copy']['follow'][3][0]='It has been 6 months since you spoke'
def edit_bevel(s): s['followSettledRegistration']['658']['bevelLighting'][0][3][11]=[137,130,128]
def edit_key_face(s):
    first=next(key for key in s['followSettledRegistration']['658']['keyboardAppearance']['rows'][0] if key)
    first[1][0]+=4
def edit_push(s): s['followCameraWarp']['667'][2][9][5][0]+=5
check_edit(478,'ring tile position',(365,367,646,641),ring)
check_edit(648,'negative response label',(349,487,399,515),edit_no)
check_edit(658,'incoming reply text',(311,414,631,451),edit_reply)
check_edit(658,'left bevel lighting',(250,65,282,934),edit_bevel)
check_edit(658,'keyboard character pose',(275,630,729,704),edit_key_face)
check_edit(667,'handset lens warp',(270,679,643,986),edit_push)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
print(edits)
