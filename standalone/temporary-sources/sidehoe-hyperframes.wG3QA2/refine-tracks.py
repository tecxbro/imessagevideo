import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import label, find_objects

scratch = Path('/tmp/sidehoe-hyperframes.wG3QA2')
path = Path('sidehoe-skill-trial/hyperframes-review/project/scene.json')
scene = json.loads(path.read_text())
tracks = scene['tracks']
tracks['followPointerStage'] = [row[0] for row in json.loads((scratch/'fitted-cursor.json').read_text())]
tones=[]
for f, _, phone_y, _ in tracks['assistantMeasuredPosition']:
    if f<141 or f>160:
        continue
    a=np.array(Image.open(scratch/'source-stage'/f'{f:06}.png').convert('RGB'))
    ink=(a[130:phone_y-45,290:710].max(axis=2)<170)
    rows=np.where(ink.sum(axis=1)>3)[0]
    split=np.split(rows,np.flatnonzero(np.diff(rows)>3)+1)
    regions=[]
    for section in split:
        if len(section)<10:
            continue
        y0,y1=int(section[0]),int(section[-1])
        _, x=np.where(ink[y0:y1+1])
        regions.append([f,int(x.min())+290,y0+130,int(x.max()-x.min()+1),y1-y0+1])
    if len(regions)==2 and regions[0][3]>330 and regions[1][3]>190:
        tones.append(regions)

for j, track in enumerate(('assistantLine1','assistantLine2')):
    picked = {row[j][0]:row[j] for row in tones}
    tracks[track] = [picked.get(row[0],row) for row in tracks[track]]
density = {397:97,398:90,399:77,400:83,401:76,402:58,403:41,404:27,405:23,408:0}
tracks['calendarArrivalSmear'] = [[f,x] for f,x in density.items()]
for row in tracks['calendarCamera']:
    if 398 <= row[0] <= 406:
        row[2] += {398:-5,399:-3,400:-3,401:-1,402:5,403:-3,404:0,405:-3,406:-1}[row[0]]
for row in tracks['calendarArrivalOpacity']:
    if 397<=row[0]<=401:
        row[1] += .025 if row[0]>=400 else .03

# Keep the plate and black motif centered during the badge landing.
for row in tracks['identityMeasuredBox']:
    f=row[0]
    if not 105<=f<=132:
        continue
    a=np.array(Image.open(scratch/'source-stage'/f'{f:06}.png').convert('RGB'))
    mask=(a[320:725,320:680].max(axis=2)<146)
    lbl,_=label(mask)
    parts=find_objects(lbl)
    if not parts:
        continue
    yy,xx=max(parts,key=lambda v:(v[1].stop-v[1].start)*(v[0].stop-v[0].start))
    w=xx.stop-xx.start
    h=yy.stop-yy.start
    if w<210 or h<210:
        continue
    row[1:]=[320+(xx.start+xx.stop)/2,320+(yy.start+yy.stop)/2,w,h]

path.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
print('Assistant text poses',tones[:4], 'and', tones[-2:])
