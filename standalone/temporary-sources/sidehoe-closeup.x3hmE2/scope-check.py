from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(sys.argv[1])/'clean'))
from render import Film

p=Path(sys.argv[1])
review=Path(sys.argv[2])
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
expected=[*range(319,330),*range(650,660),*range(673,694)]
measurements=[]
def digest(f): return sha256(f.read_bytes()).hexdigest()
changed=[f for f in range(778) if digest(p/'prior-full'/f'{f:06}.png')!=digest(p/'clean-frames'/f'{f:06}.png')]
assert changed==expected,changed
controls=[318,330,649,660,672,694,777]
for f in [*changed,*controls]:
    src,a,b=[np.array(Image.open(root/f'{f:06}.png').convert('RGB'),dtype=np.int16)
             for root in (source,p/'prior-full',p/'clean-frames')]
    row={'frame':f,'previous':float(abs(src-a).mean()),'revised':float(abs(src-b).mean()),
         'different':f in changed}
    if f==681:
        row['components']={}
        for name,(l,t,r,bot) in {
            'left_rail':(75,0,133,470),'right_rail':(865,0,927,470),
            'blue_message':(390,0,842,72),'incoming_reply':(205,365,727,470),
            'reply_controls_and_cursor':(172,500,532,625),'composer':(138,626,861,726),
            'keys':(125,732,873,1000)
        }.items():
            row['components'][name]=[float(abs(src[t:bot,l:r]-v[t:bot,l:r]).mean()) for v in (a,b)]
    measurements.append(row)
    if f in changed:
        assert row['revised']<row['previous'],row
(review/'stage-metrics.json').write_text(json.dumps({'changed_frames':changed,'measurements':measurements},indent=2)+'\n')
scene=json.loads((p/'clean/scene.json').read_text())
old=json.loads((p/'prior/scene.json').read_text())
assert scene['timeline']==old['timeline']
base=Image.open(p/'clean-frames/000681.png').convert('RGB')
edits=[]
def check_edit(name,rect,edit):
    editable=deepcopy(scene)
    edit(editable)
    change=np.max(abs(np.asarray(Film(editable).frame(681),dtype=np.int16)-np.asarray(base,dtype=np.int16)),axis=2)
    ys,xs=np.where(change!=0)
    delta=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    assert change.sum()>200 and rect[0]<=delta[0] and rect[1]<=delta[1] and rect[2]>=delta[2] and rect[3]>=delta[3],(name,delta)
    edits.append({'frame':681,'editable':name,'pixel_count':int(len(xs)),'bounds':delta})
at=lambda s:s['threadRegistration']['follow']['681']
def move_case(s):
    at(s)['railHardware'][0][1][0]+=9
def move_composer(s):
    at(s)['composer']['plus'][0]+=5
def move_cursor(s):
    s['followPointerOptics']['681'][0]+=9
check_edit('middle handset side button',(70,103,120,255),move_case)
check_edit('composer plus',(130,636,237,724),move_composer)
check_edit('outgoing message',(377,0,858,78),lambda s:s['copy']['follow'][1].__setitem__(1,'in a date with Maria?'))
check_edit('Yes label',(343,510,500,568),lambda s:s['copy']['follow'].__setitem__(5,'Go {tongue}'))
check_edit('cursor during hold',(440,534,524,630),move_cursor)
(review/'editability.json').write_text(json.dumps(edits,indent=2)+'\n')
print(len(changed),'modified stages all improved, 736 stages stayed byte-identical')
print(edits)
