import numpy as np,json
from PIL import Image
from pathlib import Path
d=Path(__file__).parent
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
p=d/'project/scene.json'
j=json.loads(p.read_text())
m=json.loads((d/'measurements.json').read_text())
new=json.loads((d/'inside-staging.json').read_text())['sofia']
for f,row in new.items():
    q=np.asarray(Image.open(source/f'{int(f):06}.png').convert('RGB'))
    src,old=m[f]
    shades=np.median(q[200:610],axis=(0,2))
    ramps=[]
    l,r=row['rails']
    lane_bounds=[(max(0,l-28),l+8),(r-8,min(999,r+28))]
    for left,right in lane_bounds:
        ramps.append([left,right,np.rint(np.interp(np.linspace(left,right,15),np.arange(1000),shades)).astype(int).tolist()])
    row['edgeRamps']=ramps
    row['corners']=[round(.43*(r[0][3]-r[0][1]),1) for r in row['items']]
    if row['today'] is None:
        row['today']=[449,267,83,30]
    j['threadRegistration']['sofia'][f]=row
p.write_text(json.dumps(j,indent=2)+'\n')
p=d/'project/render.py'
s=p.read_text().replace('softness=1.14+.29*min(1,abs(frame-348)/5)',
'''softness=1.14+.29*min(1,abs(frame-348)/5)
            if frame>=352:
                softness = 1.25+1.1*(frame-352)
                if frame==355:
                    surface=vertical_blur(surface,22,horizontal=29)''')
p.write_text(s)
