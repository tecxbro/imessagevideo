"""Batch measured ink/short-camera corrections. Immutable parent remains untouched."""
from pathlib import Path
import json,copy,math,hashlib
import numpy as np
from PIL import Image
p=Path(__file__).parent;root=p.parent.parent;fps=30000/1001
old=json.loads((p/'scene-v3-typography.json').read_text());s=copy.deepcopy(old);changed=set();notes=[]
def flatten(layers):
 out=[]
 for l in layers:out.append(l);out+=flatten(l.get('children',[]))
 return out
def sample(keys,t):
 keys=sorted(keys,key=lambda k:k['t'])
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t<=b['t']:
   z=(t-a['t'])/(b['t']-a['t']);e=b.get('ease','linear')
   if e=='hold':return b['value'] if z>=1 else a['value']
   if e=='easeInOut':z=4*z**3 if z<.5 else 1-(-2*z+2)**3/2
   if e=='easeIn':z=z**3
   if e=='easeOut':z=1-(1-z)**3
   if isinstance(a['value'],(int,float)) and isinstance(b['value'],(int,float)):return a['value']+(b['value']-a['value'])*z
   return b['value'] if z>=1 else a['value']
 return keys[-1]['value']
def at(l,key,t):
 if key in l.get('keyframes',{}):return sample(l['keyframes'][key],t)
 return l.get(key,1 if key in ['scaleX','scaleY','opacity'] else 0)
def set_track(l,key,keys):l.setdefault('keyframes',{})[key]=sorted(keys,key=lambda k:k['t']);changed.add(l['id'])
def amend(l,key,values,lo,hi):
 oldkeys=l.get('keyframes',{}).get(key,[]);set_track(l,key,[k for k in oldkeys if k['t']<lo or k['t']>hi]+values)
def has(l,text):return any(text in c.get('text','') for c in l.get('children',[]))
# Six complete actual ink boxes, including line-position/height differences.
byid={l['id']:l for l in flatten(s['layers'])}
for row in json.loads((p/'label-ink-fit-v3.json').read_text())['labels']:
 l=byid[row['id']];l.update(row['fit']);changed.add(l['id'])
notes.append('Six option labels fitted individually to actual native blue-ink bounds, not font advances.')
# Native short fast dismissal; reject blurred template matches with high error.
restaurant=next(l for l in s['layers'] if l.get('start')==19.3 and has(l,'Anything catching your eye?'))
rows=[r for r in json.loads((p/'restaurant-motion-measurements.json').read_text())['measurements'] if r['color_profile_mse']<1000]
lo,hi=rows[0]['time'],rows[-1]['time'];keys=[{'t':21.3,'value':-405,'ease':'hold'}]
for i,r in enumerate(rows):keys.append({'t':r['time'],'value':r['sheet_y'],'ease':'easeIn' if i==0 else'linear'})
amend(restaurant,'y',keys,21.3,hi)
# Continue the dismissal rapidly after the last reliable unblurred frame.
for k in restaurant['keyframes']['y']:
 if k['t']==22.4:k['ease']='easeOut'
notes.append('Restaurant frames655–663 use exact original timestamps and measured photo translation; blurred664–665 excluded.')
# Map is at−72 once its560px image ends488 in native19/20s.
mapc=next(l for l in s['layers'] if l.get('start')==17.65 and any(c.get('src','').endswith('location-map.png') for c in l.get('children',[])))
set_track(mapc,'y',[{'t':17.65,'value':1200},{'t':18,'value':274,'ease':'easeInOut'},{'t':18.7,'value':-72,'ease':'easeInOut'},{'t':20.6,'value':-72}]);mapc['children'][0]['radius']=52;changed.add(mapc['children'][0]['id'])
# Earlier found-message view has a smaller native bubble; restore old geometry while invisible.
found=next(l for l in s['layers'] if l.get('start')==18.25 and has(l,'found a few solid spots near you'))
parent_old=next(l for l in old['layers'] if l['id']==found['id']);native_t=570/fps
set_track(found,'x',[{'t':18.25,'value':235},{'t':19.3,'value':235},{'t':22.2,'value':153,'ease':'easeInOut'},{'t':23.3,'value':153},{'t':24,'value':445,'ease':'easeInOut'}])
amend(found,'y',[{'t':18.25,'value':1200},{'t':18.85,'value':700,'ease':'easeInOut'},{'t':19.3,'value':700}],18.25,19.3)
for prop in ['scaleX','scaleY']:amend(found,prop,[{'t':18.25,'value':.8},{'t':19.3,'value':.8}],18.25,19.3)
rect=found['children'][0]
for prop,early,late in [('width',916.25,945),('height',125,140),('radius',62.5,70)]:set_track(rect,prop,[{'t':18.25,'value':early},{'t':19.3,'value':early},{'t':22.2,'value':late,'ease':'linear'}])
path=next(c for c in found['children'] if c['type']=='path');early=copy.deepcopy(path);early.update(id=path['id']+'-early',start=18.25,end=19.3,d='M 28 80 Q 75 120 35 149 Q 88 149 118 112 Z');path['start']=22.2;found['children'].insert(1,early);changed.add(path['id']);changed.add(early['id'])
# Actual black-ink fit for that earlier message, restored before its later native view.
def black_box(file):
 roi=(150,700,1100,830);a=np.asarray(Image.open(file).convert('RGB').crop(roi));yy,xx=np.where(a.max(2)<80);return [int(xx.min()+roi[0]),int(yy.min()+roi[1]),int(xx.max()+roi[0]),int(yy.max()+roi[1])]
frozen_found=json.loads((p/'found-ink-fit-v3.json').read_text());ref=frozen_found['source_ink_bbox'];can=frozen_found['candidate_v3_ink_bbox'];txt=next(c for c in found['children'] if c['type']=='text');osx,osy=at(parent_old,'scaleX',native_t),at(parent_old,'scaleY',native_t);ox,oy=at(parent_old,'x',native_t),at(parent_old,'y',native_t)
nsx=(ref[2]-ref[0]+1)/(can[2]-can[0]+1)*osx/.8;nsy=(ref[3]-ref[1]+1)/(can[3]-can[1]+1)*osy/.8
nx=(ref[0]-235)/.8-((can[0]-ox)/osx-txt['x'])*nsx;ny=(ref[1]-700)/.8-((can[1]-oy)/osy-txt['y'])*nsy
for prop,v in [('x',nx),('y',ny),('scaleX',nsx),('scaleY',nsy)]:set_track(txt,prop,[{'t':18.25,'value':v},{'t':19.3,'value':v},{'t':22.2,'value':txt.get(prop,1 if prop.startswith('scale') else 0),'ease':'linear'}])
notes.append(f'Native19s found-message ink/source boxes{ref}/{can}; gray body733×100 at235,700 restored to original later view while hidden.')
# Camera drift across the audio shot, fitted from existing native27/28/29 images.
d=json.loads((p/'audio-grid-measurements-v3.json').read_text());times=[810/fps,840/fps,870/fps]
old_audio=next(l for l in old['layers'] if l.get('start')==26.4 and has(l,'Please remind me'))
deltas=[]
for n in [810,840,870]:
 a,b=d[f'audio_source_{n}']['bbox'],d[f'audio_candidate_{n}']['bbox'];deltas.append((a[0]-b[0],a[1]-b[1]))
ids=[]
for l in s['layers']:
 if l.get('start') in [24.45,25.2,26.4,28.45,23.7] and l.get('end') in [29.4,29.5,29.6]:ids.append(l['id'])
for l in s['layers']:
 if l['id'] not in ids:continue
 old_l=next(x for x in old['layers'] if x['id']==l['id'])
 for prop,idx in [('x',0),('y',1)]:
  values=[{'t':t,'value':at(old_l,prop,t)+delta[idx],'ease':'easeInOut'} for t,delta in zip(times,deltas)];amend(l,prop,values,times[0],times[-1])
# Hardware silhouette uses both measured bezel edges, rather than only one translation.
hardware=next(l for l in s['layers'] if l.get('start')==23.4 and l.get('end')==29.6);old_hw=next(l for l in old['layers'] if l['id']==hardware['id']);xs=[];scales=[]
for t,n in zip(times,[810,840,870]):
 a,b=d[f'hardware_source_{n}'],d[f'hardware_candidate_{n}'];al,ar=a['black_run_at_y900'][1],a['right_black_run_at_y900'][0];bl,br=b['black_run_at_y900'][1],b['right_black_run_at_y900'][0];ratio=(ar-al)/(br-bl);x=al-(bl-at(old_hw,'x',t))*ratio;xs.append({'t':t,'value':x,'ease':'easeInOut'});scales.append({'t':t,'value':at(old_hw,'scaleX',t)*ratio,'ease':'easeInOut'})
amend(hardware,'x',xs,times[0],times[-1]);amend(hardware,'scaleX',scales,times[0],times[-1])
notes.append(f'Audio shot native840 offset{deltas[1]}; per-layer camera and both hardware bezel edges fitted at810/840/870.')
# Service grid zoom is a single camera about stage center, preserving authentic tile artwork.
t39,t40=1169/fps,1199/fps;zoom=240/224;rate=(zoom-1)/(t40-t39);endzoom=1+rate*(40.6-t39);xs=[-78,201,472,744,1015,1287];ys=[22,293,565,837]
grid=[l for l in s['layers'] if l.get('start')==37.8 and l.get('end')==40.6]
for i,l in enumerate(grid):
 row,col=divmod(i,6);bx,by=xs[col],ys[row]
 for prop,base,center in [('x',bx,720),('y',by,540)]:
  oldkeys=[k for k in l['keyframes'][prop] if k['t']<=38.45];set_track(l,prop,oldkeys+[{'t':t39,'value':base,'ease':'easeInOut'},{'t':t40,'value':center+(base-center)*zoom,'ease':'linear'},{'t':40.6,'value':center+(base-center)*endzoom,'ease':'linear'}])
 for prop in ['scaleX','scaleY']:
  oldkeys=[k for k in l['keyframes'][prop] if k['t']<=38.45];set_track(l,prop,oldkeys+[{'t':t39,'value':1,'ease':'linear'},{'t':t40,'value':zoom,'ease':'linear'},{'t':40.6,'value':endzoom,'ease':'linear'}])
notes.append('Service grid actual39s column positions and1.07143global40s zoom about720,540; both banana andWebflow widths agree.')
s['source']['notes']+=' V4 measured refinements: '+' '.join(notes)
out=p/'scene-v4-refined.json';out.write_text(json.dumps(s,indent=2))
# Conservative exact frame-difference intervals, including nested opacity visibility.
a={l['id']:l for l in flatten(old['layers'])};b={l['id']:l for l in flatten(s['layers'])};parents={}
def parent_map(layers,parent=None):
 for l in layers:parents[l['id']]=parent;parent_map(l.get('children',[]),l['id'])
parent_map(s['layers'])
def active(l,t,table):
 if not l.get('start',0)<=t<l.get('end',s['duration']) or at(l,'opacity',t)<=0:return False
 par=parents.get(l['id'])
 return not par or active(table[par],t,table)
frames=[];props=['x','y','scaleX','scaleY','opacity','width','height','radius','d']
for n in range(round(s['duration']*fps)):
 t=n/fps
 for id in changed:
  la,lb=a.get(id),b.get(id);vis_a=la is not None and active(la,t,a);vis_b=lb is not None and active(lb,t,b)
  if not vis_a and not vis_b:continue
  if vis_a!=vis_b:frames.append(n);break
  difference=False
  for prop in props:
   va,vb=at(la,prop,t),at(lb,prop,t)
   if isinstance(va,(int,float)) and isinstance(vb,(int,float)):different=abs(va-vb)>1e-8
   else:different=va!=vb
   if different:difference=True;break
  if difference:frames.append(n);break
ranges=[]
for n in frames:
 if ranges and n==ranges[-1][1]+1:ranges[-1][1]=n
 else:ranges.append([n,n])
report={'scene':out.name,'scene_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':'scene-v3-typography.json','parent_sha256':hashlib.sha256((p/'scene-v3-typography.json').read_bytes()).hexdigest(),'changed_ranges_from_v3_inclusive':ranges,'cli_ranges_from_v3':','.join(f'{a}:{b}' for a,b in ranges),'changed_frames':len(frames),'corrections':notes,'modified_ids':sorted(changed),'status':'Prepared immutable v4 for cache patch; no1:1 certification.'};(p/'final-v4-scene.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
