"""Prepare a separately reviewable timing/camera candidate; canonical scene remains frozen."""
from pathlib import Path
import json,copy,math,hashlib
p=Path(__file__).parent;original=json.loads((p/'scene.json').read_text());fit=copy.deepcopy(original);fps=30000/1001
exact=json.loads((p/'feature-track-measurements.json').read_text()) if (p/'feature-track-measurements.json').exists() else {}
if exact.get('measurements') and exact.get('frame_selection'):
 rows=exact['measurements'];method='exact original frame indices';datafile='feature-track-measurements.json'
else:
 ledger=json.loads((p/'feature-track-measurements-v1-fps-filter.json').read_text());rows=copy.deepcopy(ledger['measurements']);method='first-pass fps-filter data; source index inferred as floor((nominal+.05)*fps), pending exact-ledger confirmation';datafile='feature-track-measurements-v1-fps-filter.json'
 for r in rows:
  r['frame_index']=math.floor((r['time']+.05)*fps-1e-8);r['time']=r['frame_index']/fps
changed=[]
# Native closeup is horizontally larger until camera pullback at12.75s.
edge=next(l for l in fit['layers'] if l.get('start')==8.78 and l.get('end')==15.65 and any(c.get('x')==38 and c.get('width')==30 for c in l.get('children',[])))
edge['keyframes']={'x':[{'t':8.78,'value':9},{'t':12.05,'value':9},{'t':12.75,'value':0,'ease':'easeInOut'}],'scaleX':[{'t':8.78,'value':1.25},{'t':11.02,'value':1.25},{'t':11.6,'value':1.05,'ease':'easeInOut'},{'t':12.05,'value':1.05},{'t':12.75,'value':1,'ease':'easeInOut'}]};changed.append(edge['id'])
# Native modal entrance is lighter and all background-message content pans upward.
intro=next(l for l in fit['layers'] if l.get('start')==4.45 and l.get('end')==8.78 and any(c.get('text')=='sarah wants to grab dinner tmrw' for c in l.get('children',[])))
intro['keyframes']['y'] += [{'t':5.4,'value':485},{'t':6.006,'value':430,'ease':'easeInOut'},{'t':7.1,'value':430}]
intro['keyframes']['opacity']=[{'t':4.45,'value':1},{'t':7.1,'value':1},{'t':7.75,'value':0,'ease':'easeInOut'}];changed.append(intro['id'])
scrim=next(l for l in fit['layers'] if l.get('start')==5.65 and l.get('type')=='rect')
scrim['keyframes']['opacity']=[{'t':5.65,'value':0},{'t':6.006,'value':37/255,'ease':'easeInOut'},{'t':6.7,'value':.25,'ease':'easeInOut'},{'t':8.55,'value':.25},{'t':8.78,'value':0,'ease':'easeInOut'}];changed.append(scrim['id'])
sheet=next(l for l in fit['layers'] if l.get('start')==5.68 and any(c.get('text')=='Dinner with Sarah' for c in l.get('children',[])))
sheet['keyframes']['y']=[k for k in sheet['keyframes']['y'] if k['t']!=6.1]+[{'t':6.006,'value':531,'ease':'easeInOut'}];changed.append(sheet['id'])
menu=next(l for l in fit['layers'] if l.get('start')==10.15 and any(c.get('text')=='Mexican' for c in l.get('children',[])))
menu['keyframes']['x']=[{'t':10.15,'value':260},{'t':11.02,'value':260},{'t':11.6,'value':227,'ease':'easeInOut'}]
menu['keyframes']['y']=[{'t':10.15,'value':700},{'t':10.65,'value':255,'ease':'easeInOut'},{'t':11.011,'value':181,'ease':'easeInOut'},{'t':11.6,'value':105,'ease':'easeInOut'},{'t':12.05,'value':105},{'t':12.45,'value':-700,'ease':'easeInOut'}]
for prop in ['scaleX','scaleY']:menu['keyframes'][prop]=[{'t':10.15,'value':1.245},{'t':11.02,'value':1.245},{'t':11.6,'value':1,'ease':'easeInOut'},{'t':12.05,'value':1},{'t':12.45,'value':.8,'ease':'easeInOut'}]
changed.append(menu['id'])
for name in sorted(set(r['feature'] for r in rows)):
 g=next(l for l in fit['layers'] if any(c.get('text')==name for c in l.get('children',[])))
 data=sorted([r for r in rows if r['feature']==name],key=lambda r:r['time']);start,end=data[0]['time'],data[-1]['time']
 for prop,col,mul in [('x','x',1),('y','y',1),('scaleX','width',1/1040),('scaleY','width',1/1040)]:
  old=g['keyframes'][prop];g['keyframes'][prop]=sorted([k for k in old if k['t']<start or k['t']>end]+[{'t':r['time'],'value':r[col]*mul,'ease':'linear'} for r in data],key=lambda k:k['t'])
 changed.append(g['id'])
fit['source']['notes'] += ' Experimental fitted candidate: horizontally measured native closeup edge and densely measured feature-card poses. Canonical source scene remains separate. '+method+'.'
(p/'scene-feature-fit.json').write_text(json.dumps(fit,indent=2))
def sample(track,t):
 if not track:return None
 ks=sorted(track,key=lambda z:z['t'])
 if t<=ks[0]['t']:return ks[0]['value']
 for a,b in zip(ks,ks[1:]):
  if t<=b['t']:
   z=(t-a['t'])/(b['t']-a['t']);e=b.get('ease','linear')
   if e=='easeInOut':z=4*z**3 if z<.5 else 1-(-2*z+2)**3/2
   elif e=='easeOut':z=1-(1-z)**3
   elif e=='easeIn':z=z**3
   return a['value']+(b['value']-a['value'])*z
 return ks[-1]['value']
a={l['id']:l for l in original['layers']};b={l['id']:l for l in fit['layers']};frames=[]
for i in range(round(original['duration']*fps)):
 t=i/fps
 for id in changed:
  oa,nb=a[id],b[id]
  if not oa.get('start',0)<=t<oa.get('end',original['duration']):continue
  dif=False
  for prop in ['x','y','scaleX','scaleY','opacity']:
   va=sample(oa.get('keyframes',{}).get(prop),t);vb=sample(nb.get('keyframes',{}).get(prop),t)
   if va is None:va=oa.get(prop,1 if prop.startswith('scale') or prop=='opacity' else 0)
   if vb is None:vb=nb.get(prop,1 if prop.startswith('scale') or prop=='opacity' else 0)
   if abs(va-vb)>1e-8:dif=True;break
  if dif:frames.append(i);break
ranges=[]
for frame in frames:
 if ranges and frame==ranges[-1][1]+1:ranges[-1][1]=frame
 else:ranges.append([frame,frame])
report={'canonical_scene_sha256':hashlib.sha256((p/'scene.json').read_bytes()).hexdigest(),'candidate_scene_sha256':hashlib.sha256((p/'scene-feature-fit.json').read_bytes()).hexdigest(),'candidate':'scene-feature-fit.json','measurement_file':datafile,'measurement_method':method,'modified_layer_ids':changed,'changed_frame_ranges_inclusive':ranges,'cli_ranges':','.join(f'{a}:{b}' for a,b in ranges),'status':'Prepared reviewable candidate; not rendered, not canonical and not certified1:1. Exact-index ledger is paused under resource coordination.'}
(p/'feature-fit-candidate.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
