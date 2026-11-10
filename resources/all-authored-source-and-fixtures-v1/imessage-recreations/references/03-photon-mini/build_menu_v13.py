"""Native popup, staggered list, independent physical-phone branch."""
from pathlib import Path
import copy,json,hashlib
p=Path(__file__).parent;s=json.loads((p/'montage-v13.scene.json').read_text());phone=next(x for x in s['layers'] if x['id']=='p03-204');phone['end']=618/30;old=next(x for x in phone['children'] if x['id']=='p03-203');records=json.loads((p/'menu-world-v13-measurements.json').read_text());hardware=json.loads((p/'late-hardware-v13-measurements.json').read_text());hardware={q['frame']:q for q in hardware}
def old_sample(track,t):
 if t<=track[0]['t']:return track[0]['value']
 for a,b in zip(track,track[1:]):
  if t<=b['t']:
   u=(t-a['t'])/(b['t']-a['t']);return a['value']*(1-u)+b['value']*u
 return track[-1]['value']
# Preserve the already verified anisotropic physical camera from v10 for the
# late menu/celebration. A uniform new fit would regress its height/width ratio.
for f,q in hardware.items():
 if 702<=f<800:
  for key in ['x','y']:q[key]=old_sample(phone['keyframes'][key],f/30)
  q['scale']=old_sample(phone['keyframes']['scaleX'],f/30);q['scaleY']=old_sample(phone['keyframes']['scaleY'],f/30)
def reid(x,prefix):
 x['id']=prefix+x['id']
 for c in x.get('children',[]):reid(c,prefix)
ui=copy.deepcopy(phone);reid(ui,'lunch13-');ui['id']='measured-lunch-ui-v13';ui['start']=618/30;ui['end']=800/30;ui['children']=[x for x in ui['children'][6:] if x['id']!='lunch13-p03-203'];ui['clip']={'x':28,'y':30,'width':744,'height':1600,'radius':120}
physical={'id':'measured-lunch-device-v13','type':'group','start':618/30,'end':800/30,'children':copy.deepcopy(phone['children'][:6]),'keyframes':{k:[] for k in ['x','y','scaleX','scaleY']}}
for c in physical['children']:reid(c,'device13-')
for f in range(618,800):
 q=hardware[f]
 for k,v in [('x',q['x']),('y',q['y']),('scaleX',q['scale']),('scaleY',q.get('scaleY',q['scale']))]:physical['keyframes'][k].append({'t':f/30,'value':v,'ease':'linear'})
# Background dim and black display are independent of the rising popup.
dim=copy.deepcopy(physical);dim['id']='measured-lunch-display-dim-v13';dim['children']=[{'id':'lunch13-dim','type':'rect','x':28,'y':30,'width':744,'height':1600,'radius':120,'fill':'#000000','keyframes':{'opacity':[{'t':618/30,'value':0},{'t':619/30,'value':.047},{'t':624/30,'value':.16},{'t':626/30,'value':1},{'t':729/30,'value':1},{'t':730/30,'value':0},{'t':735/30,'value':0}]}}];dim['end']=735/30
menu=copy.deepcopy(old);reid(menu,'menu13-');menu['id']='measured-menu-v13';menu['start']=618/30;menu['end']=735/30;menu['originX']=0;menu['originY']=0;menu['keyframes']={k:[] for k in ['x','y','scaleX','scaleY','opacity']};menu['children']=[c for c in menu['children'] if c['id']!='menu13-p03-150'];back=next(c for c in menu['children'] if c['id']=='menu13-p03-151');back['keyframes']={'opacity':[{'t':618/30,'value':0},{'t':625/30,'value':0},{'t':626/30,'value':1}]};white=next(c for c in menu['children'] if c['id']=='menu13-p03-152');white['fill']='#fdfdfd';blue=next(c for c in menu['children'] if c['id']=='menu13-p03-158')['children'][0];blue['fill']='#3abaf3'
body=next(c for c in menu['children'] if c['id']=='menu13-p03-202');body['keyframes']={};original=body['children'];body['children']=[]
for i in range(6):
 child={'id':f'menu13-row-{i}','type':'group','children':original[i*7:(i+1)*7],'keyframes':{'opacity':[{'t':r['t'],'value':r['row_presence'][i],'ease':'hold'} for r in records],'x':[],'y':[],'scaleX':[],'scaleY':[]}}
 for r in records:
  good=[(j,q) for j,q in enumerate(r['matches']) if q and q['cosine']>.86 and q['opacity']>.7]
  q=r['matches'][i]
  if q and q['cosine']>.86 and q['opacity']>.7:dx=q['x']-(r['x']+553*r.get('body_scale',r['scale']));dy=q['y']-(r['y']+(348+236*i)*r.get('body_scale',r['scale']))
  elif good:
   j,q=min(good,key=lambda z:abs(z[0]-i));dx=q['x']-(r['x']+553*r.get('body_scale',r['scale']));dy=q['y']-(r['y']+(348+236*j)*r.get('body_scale',r['scale']))
  else:dx=dy=0
  child['keyframes']['scaleX'].append({'t':r['t'],'value':r.get('body_scale',r['scale'])/r['scale'],'ease':'linear'});child['keyframes']['scaleY'].append({'t':r['t'],'value':r.get('body_scale',r['scale'])/r['scale'],'ease':'linear'});child['keyframes']['x'].append({'t':r['t'],'value':dx/r['scale'],'ease':'linear'});child['keyframes']['y'].append({'t':r['t'],'value':dy/r['scale'],'ease':'linear'})
 body['children'].append(child)
for r in records:
 for k,v in [('x',r['x']),('y',r['y']),('scaleX',r['scale']),('scaleY',r['scale']),('opacity',1 if r['frame']<733 else 0)]:menu['keyframes'][k].append({'t':r['t'],'value':v,'ease':'linear'})
# Actual app menu is clipped to its physical phone display, independent of its
# scroll/timing camera. World clip coordinates are measured per native frame.
clip={'id':'measured-menu-clip-v13','type':'group','start':618/30,'end':735/30,'children':[menu],'clip':{'x':28,'y':30,'width':744,'height':1600,'radius':120},'keyframes':{k:[] for k in ['x','y','scaleX','scaleY']}}
# A transformed clip wrapper would also transform its child; normalize each
# world menu pose into the perframe physical interior instead.
for r in records:
 q=hardware[r['frame']];left=q['x'];top=q['y'];w=q['scale'];h=q.get('scaleY',q['scale']);
 for k,v in [('x',left),('y',top),('scaleX',w),('scaleY',h)]:clip['keyframes'][k].append({'t':r['t'],'value':v,'ease':'linear'})
 for k,base in [('x',left),('y',top)]:next(x for x in menu['keyframes'][k] if x['t']==r['t'])['value']=(r[k]-base)/(w if k=='x' else h)
 next(x for x in menu['keyframes']['scaleX'] if x['t']==r['t'])['value']=r['scale']/w;next(x for x in menu['keyframes']['scaleY'] if x['t']==r['t'])['value']=r['scale']/h
# The sheet surface belongs to the physical display; its contents have a
# separate camera. A smaller content scale must not reveal black side bands.
surface=copy.deepcopy(physical);surface['id']='measured-menu-surface-v13';surface['end']=730/30;surface['children']=[{'id':'menu13-full-sheet-surface','type':'rect','x':28,'width':744,'fill':'#fdfdfd','radius':78,'keyframes':{'y':[],'height':[],'opacity':[]}}]
for r in records:
 q=hardware[r['frame']];sy=q.get('scaleY',q['scale']);top=(r['y']+170*r['scale']-q['y'])/sy
 for key,value in [('y',top),('height',1630-top),('opacity',1 if r['frame']>=630 else 0)]:surface['children'][0]['keyframes'][key].append({'t':r['t'],'value':value,'ease':'linear'})
overlay=copy.deepcopy(physical);overlay['id']='measured-lunch-bezel-overlay-v13';overlay['children']=[copy.deepcopy(phone['children'][2])];reid(overlay['children'][0],'overlay13-')
index=s['layers'].index(phone);s['layers'][index+1:index+1]=[physical,ui,dim,surface,clip,overlay];s['source']['notes']+=' V13 lunch/menu: physical hardware fitted independently618–799; rising sheet from measured cyan control and static food photo anchors, source row births and native containers; physical display clip prevents sheet pixels outside phone.'
f=p/'menu-v13.scene.json';f.write_text(json.dumps(s,indent=2));(p/'menu-v13-changes.json').write_text(json.dumps({'baseline':'montage-v13.scene.json','delta':[618,799],'hardware_review_required':[r['frame'] for r in hardware.values() if r['review_required']],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()},indent=2));print('built menu')
