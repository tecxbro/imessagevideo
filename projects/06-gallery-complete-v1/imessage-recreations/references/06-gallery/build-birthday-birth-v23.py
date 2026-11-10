"""Measured five independent UI entrances; preserve parent camera and settled UI."""
from pathlib import Path
import json,copy,sys
R=Path('/workspace/imessage-recreations');B=R/'outputs/06-gallery/final-v22/scene.json';D=R/'verification/final/06-gallery/v23';s=json.load(open(B));sys.path.insert(0,str(R/'engines'));import render_pillow as rp
nodes={}
def walk(ns):
 for n in ns:
  nodes[n['id']]=n;walk(n.get('children',[]))
walk(s['layers']);before=copy.deepcopy(nodes);fits=json.load(open(D/'birth-fits.json'));by={(q['name'],q['frame']):q for q in fits}
def put(ident,prop,values):
 n=nodes[ident];lo,hi=min(values),max(values);a,b=lo/30,hi/30;old=n.setdefault('keyframes',{}).get(prop,[]);keys=[k for k in old if not(a-1e-7<=k['t']<=b+1e-7)]
 for f,v in values.items():keys.append({'t':f/30,'value':v,'ease':'linear'})
 for f in [lo-1,hi+1]:
  t=f/30;v=rp.state(before[ident],t).get(prop,1 if prop=='opacity' else 0);keys=[k for k in keys if k['t']!=t];keys.append({'t':t,'value':v,'ease':'linear'})
 n['keyframes'][prop]=sorted(keys,key=lambda k:k['t'])
records=[]
for name,birth in [('Fuji',714),('Wait',734),('Order',745),('Done',770),('Remember',781)]:
 ident='phone-v17-message-'+name;n=nodes[ident];baseY=n['y'];curve={}
 for age in range(14):
  f=birth+age;q=by.get((name,f));fallback=[28,19,13.5,10.25,7.75,5.75,4.25,3.25,2.5,1.75,1.25,.75,.5,.25][age]
  dy=q['dy'] if q and q['correlation']>.8 else fallback
  # Fit plateau alpha is biased by subpixel glyph registration. Source half/full
  # exposure ratio is consistent across all five actors, including blue masks.
  curve[f]=baseY+dy
 put(ident,'y',curve);put(ident,'opacity',{birth:.5,birth+1:1});n['start']=birth/30
 records.append({'id':ident,'sourceBirth':birth,'oldStart':before[ident]['start'],'halfThenFullNativeOpacity':[.5,1],'nativeYOffsets':{f:round(v-baseY,5) for f,v in curve.items()},'material':'same genuine bounded UI asset, independent native pose/opacity; parent camera unchanged'})
updates={}
for ident,n in nodes.items():
 dd={k:copy.deepcopy(v) for k,v in n.items() if k!='children' and v!=before[ident].get(k)}
 if dd:updates[ident]=dd
payload={'definition':'Five independently native birthday UI entrances fitted to actual source onset/exposure/bounce; same genuine UI internals and parent camera, no frame playback. Source-only117 diagnostic frames680–796 establish Fuji714,Wait734,Order745,Done770,Remember781 half-opacity first picture then full next picture.','baseSceneSHA256':__import__('hashlib').sha256(B.read_bytes()).hexdigest(),'node_updates':updates,'insertions':[],'records':records}
(R/'references/06-gallery/birthday-birth-v23-elements.json').write_text(json.dumps(payload,indent=2));
def norm(ns):
 for n in ns:
  if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((B.parent/n['src']).resolve())
  norm(n.get('children',[]))
norm(s['layers'])
for f in s.get('fonts',[]):
 if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((B.parent/f['src']).resolve())
s['source']['notes']+=' '+payload['definition'];(R/'references/06-gallery/scene-birthday-birth-v23.json').write_text(json.dumps(s,indent=2));(D/'birth-model.json').write_text(json.dumps(records,indent=2));print('five scoped UI IDs; source-only model ready')
