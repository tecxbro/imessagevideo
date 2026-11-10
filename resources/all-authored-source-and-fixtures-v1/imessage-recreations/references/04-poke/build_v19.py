"""Full incoming-message lifecycle camera/blur from original gray-edge fits."""
from pathlib import Path
import json,copy
from v8_utils import at,track
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v18/scene.json').read_text());fps=s['fps'];original=next(g for g in s['layers']if g['id']=='p0066');g=copy.deepcopy(original);g['id']='v19-Sarah-incoming';g['start']=142/fps;g['end']=original['end']
for n in g['children']:n['id']='v19-'+n['id']
rows=json.loads((p/'measurements-v8/sarah-camera-edge-v19.json').read_text())['measurements'];camera=[]
for r in rows:
 camera.append(dict(time=r['time'],y=r['y'],blur=r['blur'] if r['frame']<=174 else 0))
raw=json.loads((p/'measurements-v8/sarah-entry-142-175-v19-parent.json').read_text())
for key in ['late_topcap_observations_176_180','late_topcap_observations_181_190']:
 for r in raw[key]:camera.append(dict(time=r['frame']/fps,y=r['edge_half_cross']+.5,blur=0))
for r in raw['late_topcap_lifecycle_191_233']:
 if r['frame']>198:continue
 profile=r['profile'];origin=r['profile_y0'];bg=sum(profile[425-origin:430-origin])/5;inside=sum(profile[435-origin:438-origin])/3;half=(bg+inside)/2
 for y in range(430,437):
  a,b=profile[y-origin],profile[y+1-origin]
  if a>=half>b:
   cross=y+(a-half)/(a-b);camera.append(dict(time=r['frame']/fps,y=cross+.5,blur=0));break
camera.sort(key=lambda r:r['time'])
# Hold the measured settled pose behind the independently moving calendar;
# preserve original opacity/fade/cut, and verify the remaining full native interval.
camera.append(dict(time=g['end'],y=camera[-1]['y'],blur=0))
for prop in ['y','blur']:track(g,prop,camera)
# Existing source-confirmed TextRegular, matched-threshold native ink fit.
style=json.loads((p/'measurements-v8/sarah-ink-v19.json').read_text())['measurements'];style=[r for r in style if r['frame']<=174];text=next(n for n in g['children']if n['id']=='v19-p0065')
for prop in ['x','y','scaleX','scaleY']:text.setdefault('keyframes',{})[prop]=[dict(t=r['time'],value=r[prop],ease='linear')for r in style]
outline=json.loads((p/'measurements-v8/sarah-outline-v19.json').read_text());g['children']=[n for n in g['children']if n['id']not in ['v19-p0063','v19-p0064']];g['children'].insert(0,dict(id='v19-Sarah-native-silhouette',type='path',d=outline['d'],fill='#ececec'))
bar=next(n for n in g['children']if n['id']=='v19-p0067');bar.update(x=740,y=120.8,width=396,height=5,fill='#b7b7b7')
s['layers'][s['layers'].index(original)]=g
s['title']='Poke Apple Messages launch — native recreation v19 measured Sarah lifecycle'
s['source']['notes']+=' V19 source-only full142–175main-pill gray-edge registration exposes the delayed post150settle and first-entry camera/blur approximation. Continuous error-function edge profiles, actual candidate controls and local lighting fit camera/blur independently of glyphs, not from blurred247thresholdbounds. Current officialTextRegular wins independent eight-face source165shape audit and is retained. A separately measured native actor preserves the original142–261lifecycle, opacity/fade/cut. Dense source topcap proof continues through198, with opaque calendar centercoverage199; no total side-arc occlusion is inferred. The measured settled pose is retained behind the calendar and the remaining fade/side-arc interval is natively checked. One static original165silhouette is a native path; source-confirmed TextRegular ink fits use160for faint142–149because100censorsglyphs, then100for settledfont. Underline remains a separate native rectangle with measured lighter material/thickness. No bitmap UI. Neighbor/lifecycle native proof is required before freeze; no copied UI bitmap or branding changes.'
(p/'scene-v19-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));print('V19 native incoming lifecycle candidate ready')
