"""Interpolate the four artwork registrations and check every affected stage frame."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from render import Film

w=Path(sys.argv[1])
path=w/'project/scene.json'
s=json.loads(path.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
base=w/'base-frames'
anchors=json.loads((w/'badge-part-anchors.json').read_text())
frames=sorted(map(int,anchors))
values=np.array([anchors[str(f)] for f in frames]).reshape(-1,16)
s['closingBadgeArtwork']={}
art=s['closingBadgeArtwork']
outline=s['closingBadgeOutline']
notes=[]
for f in range(frames[0],777):
    k=str(f)
    poses=np.array([np.interp(f,frames,axis) for axis in values.T]).reshape(4,4)
    target=np.asarray(Image.open(source/f'{f:06d}.png').convert('RGB'),np.int16)
    before=np.asarray(Image.open(base/f'{f:06d}.png').convert('RGB'),np.int16)
    def cost():
        a=np.asarray(Film(s).frame(f),np.int16)
        return float(np.abs(target-a).mean())
    prior=float(np.abs(target-before).mean())
    if f>765 and '765' in outline:
        outline[k]=outline['765']
    case=cost()
    art[k]=poses.round(5).tolist()
    revised=cost()
    if revised>=case:
        # Try a smaller adjustment before leaving the artwork in its prior pose.
        neutral=np.tile((0.,0.,1.,1.),(4,1))
        art[k]=(neutral+(poses-neutral)*.55).round(5).tolist()
        revised=cost()
    if revised>=case:
        art.pop(k)
        revised=case
    if revised>=prior and f>765:
        outline.pop(k,None)
        if cost()>=prior:
            art.pop(k,None)
        revised=cost()
    if f in (701,706,711,712,716,732,765,766,771,776):
        print(f,round(prior,6),round(case,6),round(revised,6),k in art,flush=True)
    notes.append([f,prior,case,revised])
assert all(v[3]<=v[1] for v in notes)
path.write_text(json.dumps(s,indent=2)+'\n')
(w/'closing-stage-fit.json').write_text(json.dumps(notes,indent=2)+'\n')
print('artwork',len(art),'outline',len(outline),'improved',sum(v[3]<v[1] for v in notes))
