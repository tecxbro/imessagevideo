"""Bounded final genuine side-hardware material correction, native UI retained."""
from pathlib import Path
import json,copy
from v8_utils import track,amend
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v11/scene.json').read_text());by={l['id']:l for l in s['layers']};d=json.loads((p/'measurements-v8/rail-profiles-v12.json').read_text());g=by['p0109'];g.update(x=0,y=0,scaleX=1,scaleY=1);g['keyframes']={};g['children']=[]
for side in['left','right']:
    crop=d[side+'_crop'];image=dict(id='v12-'+side+'-rail-art',type='image',src=d[side+'_asset'],x=crop[0],y=0,width=crop[2]-crop[0],height=1080);group=dict(id='v12-'+side+'-rail-camera',type='group',children=[image]);rows=[]
    for r in d['measurements']:rows.append(dict(time=r['time'],x=r[side+'_x'],scaleX=r[side+'_scale'],opacity=r.get(side+'_opacity',1)))
    for prop in['x','scaleX','opacity']:track(group,prop,rows)
    g['children'].append(group)
# Independent original-ink spatial audit selects Text for inbox, and
# DisplaySemibold for feature titles. Literal scene copy is preserved.
inbox=by['v8-inbox-rows']
for node in inbox['children']:
    if node['type']=='text':node['fontFamily']='SF Pro Text'
for name in['p0430','p0436','p0442','p0448','p0454','p0460']:
    for node in by[name]['children']:
        if node['type']=='text'and node.get('fontWeight')==500:node['fontWeight']=600
# Prompt belongs to the conversation under the modal scrim; its independently
# ranked face is DisplayMedium. The clean674reference is after scrim release.
prompt=by['p0259'];s['layers'].remove(prompt);s['layers'].insert(s['layers'].index(by['p0231']),prompt)
for node in prompt['children']:
    if node['id']=='p0258':node.update(fontWeight=500,fill='#929292')
fitfile=p/'measurements-v8/type-browser-fit-v12.json'
if fitfile.exists():
    nodes={l['id']:l for g in s['layers']for l in g.get('children',[])}
    for r in json.loads(fitfile.read_text())['measurements']:
        for prop in['x','y','scaleX','scaleY']:nodes[r['id']][prop]=r[prop]
    nodes['v8-Angie'].update(scaleX=.934,scaleY=.9375)
promptfit=p/'measurements-v8/prompt-browser-fit-v12.json'
if promptfit.exists():
    nodes={l['id']:l for g in s['layers']for l in g.get('children',[])}
    for r in json.loads(promptfit.read_text())['measurements']:
        node=nodes[r['id']]
        if r['id']=='p0229':
            late=copy.deepcopy(node);late.update(id='v12-found-late',start=664/s['fps'],fontFamily='SF Pro Display');late.pop('keyframes',None)
            for prop in['x','y','scaleX','scaleY']:late[prop]=r[prop]
            node['end']=664/s['fps'];by['p0230']['children'].append(late)
        else:
            for prop in['x','y','scaleX','scaleY']:node[prop]=r[prop]
latefit=p/'measurements-v8/found-late-browser-fit-v12.json'
if latefit.exists():
    late=next(n for n in by['p0230']['children']if n['id']=='v12-found-late')
    for prop in['x','y','scaleX','scaleY']:late[prop]=json.loads(latefit.read_text())[prop]
s['title']='Poke Apple Messages launch — native recreation v12 measured hardware and typography'
s['source']['notes']+=' V12 uses two isolated genuine static side-hardware materials with independent measured native rail cameras; all screen UI remains native and editable. Original-ink shape audits select Text inbox, DisplaySemibold feature titles, and DisplayRegular/Medium late conversation type; browser ink fits preserve exact copy and independent cameras.'
(p/'scene-v12-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));print('Built v12 candidate')
diag=json.loads(json.dumps(s));ids=['v8-inbox-rows','p0430','p0436','p0442','p0448','p0454','p0460'];diag['layers']=[l for l in diag['layers']if l['id']in ids]
for g in diag['layers']:g['children']=[l for l in g['children']if l['type']=='text']
(p/'scene-v12-font-diagnostic.json').write_text(json.dumps(diag,indent=2,ensure_ascii=False))

promptdiag=json.loads(json.dumps(s));promptdiag['layers']=[g for g in promptdiag['layers']if g['id']in['p0230','p0259']]
for g in promptdiag['layers']:g['children']=[n for n in g['children']if n['type']=='text']
(p/'scene-v12-prompt-diagnostic.json').write_text(json.dumps(promptdiag,indent=2,ensure_ascii=False))
