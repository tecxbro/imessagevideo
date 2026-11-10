"""Bounded correction of three measured text regressions in frozenv8."""
from pathlib import Path
import json,sys,copy
from v8_utils import at,amend
p=Path(__file__).parent;root=p.parent.parent;source=root/'outputs/04-poke/final-v8/scene.json';s=json.loads(source.read_text());by={l['id']:l for l in s['layers']};fps=s['fps'];records=[]
# Repair the confirmed held camera boundary before fitting its text component.
for prop,value in [('x',126),('y',485),('scaleX',1),('scaleY',1)]:
    amend(by['p0066'],prop,[dict(t=150/fps,value=value)],150/fps,150/fps)
for identifier,frame,target,candidate in[
 ('p0066',150,[179,539,1263,606],[180,536,1271,603]),
 ('p0113',300,[307,166,735,234],[305,162,732,228]),
 ('p0117',300,[305,386,1101,440],[298,375,1138,429])]:
    group=by[identifier];node=next(l for l in group['children']if l['type']=='text');node['fontFamily']='SF Pro Text'
    time=frame/fps;gx,gy,gsx,gsy=[at(group,k,time)for k in['x','y','scaleX','scaleY']]
    sx=(target[2]-target[0])/(candidate[2]-candidate[0]);sy=(target[3]-target[1])/(candidate[3]-candidate[1])
    nx=gx+node['x']*gsx;ny=gy+node['y']*gsy
    node['x']=(target[0]-(candidate[0]-nx)*sx-gx)/gsx
    node['y']=(target[1]-(candidate[1]-ny)*sy-gy)/gsy
    node['scaleX']=sx;node['scaleY']=sy
    records.append(dict(id=node['id'],frame=frame,source_ink_bbox=target,actual_Text_candidate_bbox=candidate,properties={k:node[k]for k in['fontFamily','x','y','scaleX','scaleY']}))
s['title']='Poke Apple Messages launch — native recreation v9 measured complete timeline'
s['source']['notes']+=' V9 bounded held-frame audit restores the verified Text Regular family for three early conversation text nodes, fits their actual native glyph ink bounds and fixes the exact150held Sarah camera anchor. All other v8 scene states, assets and cameras are unchanged.'
(p/'scene-v9-final-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));(p/'measurements-v8/v9-three-bubble-fit.json').write_text(json.dumps({'method':'Exact source150/300 and actual production GSAP Text candidate glyph bounds; fit after confirming the150held camera, not before.','changed_ranges_inclusive':[[142,360]],'measurements':records},indent=2));print(records)
