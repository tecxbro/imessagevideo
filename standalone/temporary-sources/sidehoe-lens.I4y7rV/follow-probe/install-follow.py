from pathlib import Path
from PIL import Image
import numpy as np,json
root=Path(__file__).parent
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
p=root/'project/scene.json'
scene=json.loads(p.read_text())
measurements=json.loads((root/'measurements.json').read_text())
readings=json.loads((root/'inside-staging.json').read_text())['follow']
for f,row in readings.items():
    if int(f)>671: continue
    q=np.asarray(Image.open(source/f'{int(f):06}.png').convert('RGB'))
    src,old=measurements[f]
    shade=np.median(q[200:610],axis=(0,2))
    ramps=[]
    for side in (0,1):
        x1,x2=src['rails'][side][0]
        px1,px2=old['rails'][side][0]
        left=min(x1-4,px1-1)
        right=max(x2+3,px2+1)
        ramps.append([left,right,np.rint(np.interp(np.linspace(left,right,15),np.arange(1000),shade)).astype(int).tolist()])
    row['edgeRamps']=ramps
    row['corners']=[round(.32*(r[0][3]-r[0][1]),1) for r in row['items']]
    if row['today'] is None:
        row['today']=[472,266+(669-int(f))*5,57,16]
    scene['threadRegistration']['follow'][f]=row
p.write_text(json.dumps(scene,indent=2)+'\n')
p=root/'project/render.py'
s=p.read_text().replace('softness=.78+1.7*tween(frame,688,694)',
'softness=.78+1.7*tween(frame,688,694)+max(0, (672-frame)*.48)')
p.write_text(s)
