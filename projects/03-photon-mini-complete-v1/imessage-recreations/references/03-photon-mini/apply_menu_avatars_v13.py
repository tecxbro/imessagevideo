from pathlib import Path
import json,copy
p=Path(__file__).parent;s=json.loads((p/'menu-v13.scene.json').read_text());records=json.loads((p/'menu-avatar-v13-measurements.json').read_text());meta=[]
for name,data in records.items():
 c=next(x for x in s['layers'] if x['id']==data['id']);c['src']=data['src'];c['start']=data['birth']/30;c['end']=702/30;c['keyframes']={k:[] for k in ['x','y','width','height','opacity']};trail={'id':'menu13-motion-trail-'+name,'type':'circle','fill':{'alice':'#fae6d7','bob':'#deecfa','laptop':'#fae69b'}[name],'blur':11,'start':c['start'],'end':c['end'],'keyframes':{k:[] for k in ['x','y','width','height','opacity']}};prior=None
 for q in data['fits']:
  for k in c['keyframes']:c['keyframes'][k].append({'t':q['t'],'value':q[k],'ease':'linear'})
  vx=q['x']-prior['x'] if prior else 0;vy=q['y']-prior['y'] if prior else 0;speed=(vx*vx+vy*vy)**.5
  for k,v in [('x',q['x']-vx*1.2),('y',q['y']-vy*1.2),('width',q['width']),('height',q['height']),('opacity',min(.55,speed/40)*q['opacity'])]:trail['keyframes'][k].append({'t':q['t'],'value':v,'ease':'linear'})
  prior=q
 s['layers'].insert(s['layers'].index(c),trail);meta.append({'actor':name,'image':c['src'],'scope':[data['birth'],701],'fits':data['fits'],'limitation':'Memoji motion follows native template locations/scales. Per-frame soft trail is editable geometry and remains a motion-blur approximation.'})
s['source']['notes']+=' V13 flying menu Memoji: independently measured native-frame template positions/scales and lifetimes, clean laptopcore artwork, editable soft geometric motion trails.'
(p/'menu-v13.scene.json').write_text(json.dumps(s,indent=2));(p/'menu-avatar-v13-provenance.json').write_text(json.dumps(meta,indent=2));print('applied',len(meta))
