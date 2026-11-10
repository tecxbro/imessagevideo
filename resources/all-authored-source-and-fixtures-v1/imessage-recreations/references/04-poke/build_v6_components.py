"""Correct measured local components without changing the audio camera or its pacing."""
from pathlib import Path
import copy,hashlib,json
p=Path(__file__).parent;fps=30000/1001
parent=p/'scene-v5-artwork.json';s=json.loads(parent.read_text());m=json.loads((p/'component-fit-v5.json').read_text());changed=[]
byid={}
def index(nodes):
 for n in nodes:byid[n['id']]=n;index(n.get('children',[]))
index(s['layers'])
def replace_hold(layer,prop,value,lo=26.8,hi=29.2):
 ks=layer.setdefault('keyframes',{}).get(prop,[]);layer['keyframes'][prop]=sorted([k for k in ks if k['t']<lo or k['t']>hi]+[{'t':lo,'value':value,'ease':'easeInOut'},{'t':hi,'value':value,'ease':'hold'}],key=lambda k:k['t']);changed.append(layer['id'])
def inkfit(text,reference,candidate,old_parent,new_parent,scale):
 a,b=reference['bbox'],candidate['bbox'];rx=(a[2]-a[0]+1)/(b[2]-b[0]+1);ry=(a[3]-a[1]+1)/(b[3]-b[1]+1)
 text['x']=(a[0]-new_parent[0])/scale-((b[0]-old_parent[0])/scale-text['x'])*rx
 text['y']=(a[1]-new_parent[1])/scale-((b[1]-old_parent[1])/scale-text['y'])*ry
 text['scaleX']=text.get('scaleX',1)*rx;text['scaleY']=text.get('scaleY',1)*ry;changed.append(text['id'])
# Map footer: its corners and dismissing position were component-specific, not camera.
mapg=byid['p0300'];byid['p0299']['radius']=35;byid['p0302']['fontWeight']=600;byid['p0302']['text']="Zareen's"
anchors=m['anchors'];old=mapg['keyframes']['y'];lo,hi=anchors[0]['time'],anchors[-1]['time'];mapg['keyframes']['y']=sorted([k for k in old if k['t']<lo or k['t']>hi]+[{'t':r['time'],'value':r['map_footer_bbox'][3]+1-388*1.6,'ease':'easeInOut'}for r in anchors],key=lambda k:k['t']);changed+=['p0300','p0299','p0302']
# Distance bubble: source-derived native vector silhouette, with editable text inside.
dist=byid['p0307'];text=byid['p0306'];bbox=m['distance']['bbox'];inkfit(text,m['distance']['ink_source'],m['distance']['ink_candidate'],[241,213],bbox[:2],1.45);text['fontWeight']=600
text.update(json.loads((p/'distance-semibold-fit.json').read_text())['fit'])
dist['children']=[{'id':'p0307-measured-outline','type':'path','d':m['distance']['outline'],'fill':'#ececec'},text]
for prop,axis in [('x',0),('y',1)]:
 old=dist['keyframes'][prop];dist['keyframes'][prop]=sorted([k for k in old if k['t']<lo or k['t']>hi]+[{'t':r['time'],'value':r['distance_bbox'][axis],'ease':'easeInOut'}for r in anchors],key=lambda k:k['t'])
changed.append(dist['id'])
# Audio: all silhouette, text, player and waveform layers remain independent vectors.
audio=byid['p0310'];caption=byid['p0314'];inkfit(caption,m['audio']['caption_source'],m['audio']['caption_candidate'],[452,379],[452,379],1)
keep=[c for c in audio['children'] if c['type']!='rect' and c['id']!='p0309']
audio['children']=[{'id':'p0310-measured-outline','type':'path','d':m['audio']['outline'],'fill':'#9ea3ae'}]+keep
for i,bar in enumerate(m['audio']['waveform_bars']):audio['children'].append({'id':f'p0310-wave-{i:02}','type':'rect',**bar,'fill':'#ffffff'})
changed.append(audio['id'])
# Composer stays vertically fixed while the conversation above it scrolls. The prior
# camera amendment incorrectly moved it18px up at28s.
composer=byid['p0372'];replace_hold(composer,'y',735)
inkfit(byid['p0367'],m['composer']['source_ink'],m['composer']['candidate_ink'],[228,717],[228,735],.84)
for id in ['p0365','p0366']:
 c=byid[id];c['x']=38+(c['x']-38)*.9;c['y']=32.15+(c['y']-26)*.9;c['width']*=.9;c['height']*=.9;c['radius']*=.9;changed.append(id)
byid['p0363']['opacity']=.25
# Keyboard: actual white key bounds are90px wide at108px pitch, at y1007. Correct
# the static key grid instead of offsetting the whole camera.
keyboard=byid['p0427'];replace_hold(keyboard,'y',872)
for k in keyboard['keyframes']['x']:
 if k['t']>=26.8:k['value']+=4
for c in keyboard['children']:
 if c['id']=='p0373':c['width']=1258;continue
 if c['type'] in ['rect','text']:
  c['x']=(c['x']-10)*(108/110)+10+12/.88
  c['y']-=22/.88
  if c['type']=='rect':c['width']*=108/110
  elif c['fontSize']==98:c['fontSize']=74
s.setdefault('gradients',[]).append({'id':'keyboard-native-gradient','type':'linear','x1':'0%','y1':'0%','x2':'0%','y2':'100%','stops':[{'offset':'0%','color':'#d5d5da'},{'offset':'18%','color':'#e1e2e7'},{'offset':'100%','color':'#e1e2e7'}]});byid['p0373']['fill']='url(#keyboard-native-gradient)';changed.append(keyboard['id'])
# Replace only genuine phone side hardware in the stable late shot. Screen/UI
# remains transparent and independently recreated; no full source frame is embedded.
hardware=next(l for l in s['layers'] if l.get('start')==23.4 and l.get('end')==29.6);hardware['end']=810/fps
strips=[]
for asset in json.loads((p/'hardware-native28.json').read_text())['assets']:
 x,y,x2,y2=asset['source_crop'];strips.append({'id':'native28-'+Path(asset['src']).stem,'type':'image','src':asset['src'],'x':x,'y':y,'width':x2-x,'height':y2-y})
new={'id':'native28-hardware','type':'group','children':strips,'start':810/fps,'end':29.6,'x':0,'y':0,'keyframes':{'x':[{'t':810/fps,'value':46},{'t':840/fps,'value':0,'ease':'easeInOut'},{'t':870/fps,'value':-2,'ease':'easeInOut'}],'opacity':[{'t':810/fps,'value':1},{'t':29.2,'value':1},{'t':29.6,'value':0,'ease':'easeInOut'}]}}
# Original hardware is behind the native UI, so keep the same stacking position.
s['layers'].insert(s['layers'].index(hardware)+1,new);changed+=['native28-hardware',hardware['id']]
s['source']['notes']+=' V6 local components measured from native840: keyboard keys/pitch/glyphs and gradient, fixed-height composer, map-footer radius/heading/dismissal, native vector distance/audio silhouettes, exact editable waveform bars and caption ink. Genuine narrow native28 side-hardware crops have transparent screens; measured horizontal anchors810/840/870 only. Main audio camera is unchanged.'
out=p/'scene-v6-components.json';out.write_text(json.dumps(s,indent=2))
report={'scene':out.name,'scene_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':parent.name,'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'delta_from_v5_inclusive':[[710,887]],'cli_ranges_from_v5':'710:887','changed_frames':178,'measurements':'component-fit-v5.json','modified_ids':changed,'status':'Measured local component candidate. Native source comparison required before acceptance; not1:1 certified.'};(p/'final-v6-scene.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
