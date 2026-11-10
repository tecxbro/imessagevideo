"""Bounded proof: material clip coordinates and adjacent-logo false match."""
from pathlib import Path
import json,copy
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v12/scene.json').read_text());count=0
for group in s['layers']:
    if group['id'].startswith('v10-logo-morph-'):
        children=[]
        for node in group['children']:
            if node['type']=='image'and'clip'in node:
                image=copy.deepcopy(node);clip=image.pop('clip');children.append(dict(id=node['id']+'-clip-parent',type='group',clip=clip,children=[image]));count+=1
            else:children.append(node)
        group['children']=children
    if group['id']=='v8-entry-p0510':group['start']=1160/s['fps']
# Material identity switches at72; old linear72–79 crossfade was unsupported.
blend={r['frame']:r for r in json.loads((p/'measurements-v8/logo-material-blend-v13.json').read_text())['measurements']}
for g in s['layers']:
    if not g['id'].startswith('v10-logo-morph-'):continue
    row=blend[int(g['id'].rsplit('-',1)[1])]
    if row['fitted_mae']<row['old_mae']-.5:
        node=next(v['children'][0]for v in g['children']if v.get('type')=='group'and'square'in v['id']);node['opacity']=row['blend']
# The verified badge has an independently bouncing entrance at native72.
# The old ease began at75 and stayed32px too far right.
from v8_utils import track
badge=next(n for n in s['layers']if n['id']=='p0016');early=copy.deepcopy(badge);early.update(id='v13-verified-badge-entry',start=72/s['fps'],end=109/s['fps']);early['keyframes']={};poses=[]
for row in json.loads((p/'measurements-v8/verified-badge-v13.json').read_text())['measurements']:
    if not row['observed']:continue
    x,y,z,w=row['observed']['bbox'];poses.append(dict(time=row['time'],x=x,y=y,scaleX=(z-x)/56,scaleY=(w-y)/57,opacity=1))
for prop in['x','y','scaleX','scaleY','opacity']:track(early,prop,poses)
badge['start']=109/s['fps'];s['layers'].insert(s['layers'].index(badge),early)
# Caption row recenters as the badge appears; fit actual glyph bounds separately.
from v8_utils import at
caption=next(n for n in s['layers']if n['id']=='p0015');poses=json.loads((p/'measurements-v8/poke-caption-ink-v13.json').read_text())['measurements']
for prop in['x','y','scaleX','scaleY']:
    saved=[dict(time=n/s['fps'],**{prop:at(caption,prop,n/s['fps'])})for n in[63,109]]
    track(caption,prop,[saved[0],*poses,saved[1]])
caption.setdefault('keyframes',{})['fill']=[dict(t=0,value='#858585'),dict(t=64/s['fps'],value='#818181',ease='hold'),dict(t=109/s['fps'],value='#858585',ease='hold')]
s['title']='Poke Apple Messages launch — native recreation v13 corrected logo material clips'
s['source']['notes']+=' V13 moves logo material clipping from image-local to logo-parent coordinates, preserving native editable palm silhouettes and two static authentic blue textures. Measured square material already dominates from72 instead of an invented slow crossfade. Verification badge has its own measured opaque native72–108 entrance camera. Right-edge Sonos entry is gated at first confirmed1160 after the older NCC detector falsely matched the adjacent Oura tile in1152–1157.'
(p/'scene-v13-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));print('Wrapped clips',count)
