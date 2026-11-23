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
perspective=[*range(352,360),671,672,694,695]
closing=list(range(709,715))+list(range(717,777))
expected=perspective+closing
def digest(f): return sha256(f.read_bytes()).hexdigest()
changed=[f for f in range(778) if digest(p/'prior-full'/f'{f:06}.png') != digest(p/'clean-frames'/f'{f:06}.png')]
assert changed==expected,changed
measurements=[]
for f in [*changed,192,351,360,670,673,674,675,693,696,706,708,715,716,777]:
    src,a,b=[np.asarray(Image.open(path/f'{f:06}.png').convert('RGB'),dtype=np.int16)
             for path in (source,p/'prior-full',p/'clean-frames')]
    row={'frame':f,'previous':float(np.abs(src-a).mean()),'revised':float(np.abs(src-b).mean()),
         'different':f in changed}
    if f in (352,765,767):
        row['components']={}
        areas = {
            352: {'suggestion_and_controls':(385,341,888,690),'casing_and_screen':(0,0,1000,1000)},
            765: {'first_line':(292,575,698,635),'second_line':(242,635,760,695)},
            767: {'pink_falloff':(0,730,1000,1000),'closing':(0,0,1000,1000)},
        }
        for name,(l,t,r,bot) in areas[f].items():
            row['components'][name]=[float(np.abs(src[t:bot,l:r]-v[t:bot,l:r]).mean()) for v in (a,b)]
    if f in changed:
        assert row['revised']<row['previous'],row
    measurements.append(row)
(review/'stage-metrics.json').write_text(json.dumps({'changed_frames':changed,'measurements':measurements},indent=2)+'\n')

scene=json.loads((p/'clean/scene.json').read_text())
old=json.loads((p/'prior/scene.json').read_text())
assert old['timeline']==scene['timeline']
edits=[]
def check_edit(frame,name,rect,apply):
    editable=deepcopy(scene)
    apply(editable)
    base=np.asarray(Image.open(p/'clean-frames'/f'{frame:06}.png').convert('RGB'),dtype=np.int16)
    delta=np.max(np.abs(np.asarray(Film(editable).frame(frame),dtype=np.int16)-base),axis=2)
    ys,xs=np.where(delta!=0)
    limits=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    l,t,r,b=limits
    assert delta.sum()>110 and rect[0]<=l and rect[1]<=t and r<=rect[2] and b<=rect[3],(name,limits)
    edits.append(dict(frame=frame,editable=name,pixel_count=int(len(xs)),bounds=limits))
def soften_suggestion(s): s['sofiaSuggestionRegistration']['352']['focus']+=1
def fresh_title(s): s['copy']['ending'][1][1]='companion'
def header(s): s['copy']['follow'][0]='Messages'
check_edit(352,'Sofia suggested reply',(395,470,900,620),lambda s:s['copy']['sofia'][6].__setitem__(0,'Or do you wanna go'))
check_edit(352,'Sofia suggestion focus',(390,335,906,681),soften_suggestion)
check_edit(695,'withdrawing handset label',(448,72,554,123),header)
check_edit(765,'closing second line',(465,634,681,705),fresh_title)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'improved before encode',778-len(changed),'matching baseline hashes')
print(edits)
