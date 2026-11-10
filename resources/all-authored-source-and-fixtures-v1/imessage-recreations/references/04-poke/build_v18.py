"""Apply only native source-supported held-grid camera/aspect correction."""
from pathlib import Path
import json
from v8_utils import at,track
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v17/scene.json').read_text());fps=s['fps'];fit=json.loads((p/'measurements-v8/grid-camera-v18.json').read_text())['measurements'];accepted=json.loads((p/'measurements-v8/grid-native-acceptance-v18.json').read_text())['accepted_ranges_inclusive'];fit=[r for r in fit if any(lo<=r['frame']<=hi for lo,hi in accepted)];parents=[]
for g in s['layers']:
 if g.get('start')!=39.005633333333336 or not g.get('children'):continue
 if g['children'][0]['type']!='image':continue
 parents.append(g['id']);rows=[]
 for r in fit:
  t=r['time'];x,y,sx,sy=[at(g,k,t)for k in ['x','y','scaleX','scaleY']];rows.append(dict(time=t,x=r['ax']*x+r['bx'],y=r['ay']*y+r['by'],scaleX=r['ax']*sx,scaleY=r['ay']*sy))
 for prop in ['x','y','scaleX','scaleY']:track(g,prop,rows)
s['title']='Poke Apple Messages launch — native recreation v18 measured held-grid camera'
s['source']['notes']+=' V18 retains all genuine tile art, fonts and materials. Original1169–1214six-tile native SIFT registrations plus actual candidate controls fit a coherent camera/aspect independently for each native frame; source residuals change sign through the interval, so no constant/global guessed offset is used. Bias-corrected four-corner/center correspondences and uncertainty are frozen in grid-camera-v18.json; sub.1px correction snaps to identity. After full native interval validation, only1170–1210is accepted on24existing held-grid image roots; the unproved1211–1214global extension is rejected and original poses retained, with actual1169entry/1215exit preserved. No genuine branding artwork changes.'
(p/'scene-v18-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));(p/'v18-changed-parents.json').write_text(json.dumps(parents,indent=2));print('V18 native candidate',len(parents),'held image roots')
