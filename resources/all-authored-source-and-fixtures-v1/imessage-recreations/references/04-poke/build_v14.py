"""Bounded native correction of first dismissal pose and calendar optical type."""
from pathlib import Path
import json,copy
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v13/scene.json').read_text());g=next(l for l in s['layers']if l['id']=='p0230');t=664/s['fps']
# The prior interpolation is invisible: original actor opacity is0 until664.
# Keep that original visibility track untouched; only its664camera endpoint changes.
for prop in['scaleX','scaleY']:
    key=next(k for k in g['keyframes'][prop]if abs(k['t']-t)<1e-8);key['value']=.9989417989417989
# The late incoming body differs from the generic early rect/tail geometry.
# Preserve early UI and use one independently editable measured static vector.
outline=json.loads((p/'measurements-v8/found-body-outline-v14.json').read_text())
for node in g['children']:
    if node['id']in['p0227','p0228']:node['end']=664/s['fps']
g['children'].insert(0,dict(id='v14-found-body-outline',type='path',d=outline['d'],fill='#ececec',start=664/s['fps']))
calendar=next(l for l in s['layers']if l['id']=='p0100')
for node in calendar['children']:
    if node['id']in['p0074','p0085','p0094']:node['fontFamily']='SF Pro Text'
fit=p/'measurements-v8/calendar-date-ink-v14.json'
if fit.exists():
    by={n['id']:n for n in calendar['children']}
    for row in json.loads(fit.read_text())['measurements']:
        for prop in['x','y','scaleX','scaleY']:by[row['id']][prop]=row[prop]
# Checkbox capsule and prompt spring independently of the conversation camera.
from v8_utils import at,track
prompt=next(n for n in s['layers']if n['id']=='p0259');text=next(n for n in prompt['children']if n['id']=='p0258');fitfile=p/'measurements-v8/prompt-spring-ink-v14.json'
if fitfile.exists():
    rows=json.loads(fitfile.read_text())['measurements'];last=rows[-1]['frame'];capsules=[n for n in prompt['children']if n['id']in['p0256','p0257']];capsuleposes=[]
    for row in rows:
        if len(row['source_badge_removed'])!=1 or len(row['candidate_badge_removed'])!=1:raise ValueError('Uncertain capsule component')
        a,b=row['source_badge_removed'][0],row['candidate_badge_removed'][0];gx,gy,sx,sy=[at(prompt,k,row['time'])for k in['x','y','scaleX','scaleY']];rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);capsuleposes.append(dict(time=row['time'],x=(a[0]-(b[0]-gx)*rx-gx)/sx,y=(a[1]-(b[1]-gy)*ry-gy)/sy,scaleX=rx,scaleY=ry))
    for prop in['x','y','scaleX','scaleY']:
        first=dict(time=663/s['fps'],**{prop:at(text,prop,663/s['fps'])});after=dict(time=(last+1)/s['fps'],**{prop:at(text,prop,(last+1)/s['fps'])});track(text,prop,[first,*rows,after])
        for capsule in capsules:
            first=dict(time=663/s['fps'],**{prop:at(capsule,prop,663/s['fps'])});after=dict(time=(last+1)/s['fps'],**{prop:at(capsule,prop,(last+1)/s['fps'])});poses=[]
            for pose in capsuleposes:
                original=at(capsule,prop,pose['time']);axis='scaleX'if prop=='x'else'scaleY';value=pose[prop]+original*pose[axis]if prop in['x','y']else pose[prop]*original;poses.append(dict(time=pose['time'],**{prop:value}))
            track(capsule,prop,[first,*poses,after])
s['title']='Poke Apple Messages launch — native recreation v14 exact first dismissal camera and calendar optical type'
s['source']['notes']+=' V14 corrects native664 found-message camera (original819px sentence versus prior799px censored body fit), preserving original visibility. The late incoming bubble silhouette is an editable measured static vector rather than the generic early rectangle/tail. Independent font ranking identifies SF Pro TextSemibold for the three calendar date headings; actual native browser ink is fitted separately from their unchanged parent camera. Original native checkbox capsule and prompt spring are fitted independently through709, with the original710hardzoom restored. Restaurant title and blue time faces were proven correct and retained.'
(p/'scene-v14-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False))
diag=copy.deepcopy(s);diag['layers']=[copy.deepcopy(calendar)];diag['layers'][0]['children']=[n for n in calendar['children']if n['id']in['p0074','p0085','p0094']];(p/'scene-v14-date-diagnostic.json').write_text(json.dumps(diag,indent=2,ensure_ascii=False))
