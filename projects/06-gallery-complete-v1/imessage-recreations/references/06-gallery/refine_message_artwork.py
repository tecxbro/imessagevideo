from pathlib import Path
from PIL import Image
import json
r=Path('/workspace/imessage-recreations');d=r/'references/06-gallery';s=json.loads((d/'scene.json').read_text());p=json.loads((d/'assets/asset-provenance.json').read_text())
items=[('Dan','004.00',(550,98,1206,275),(550,98)),('Oct17','004.00',(550,339,1206,494),(550,339)),('Want','004.00',(550,502,1206,798),(550,502)),('Priya','006.50',(550,393,1131,524),(550,863)),('Book','006.50',(1046,563,1479,695),(1046,1033)),('Done','007.50',(542,535,1202,656),(548,1235))]
assets={}
for name,t,b,pos in items:
 path=f'assets/intro-message-{name.lower()}.png';Image.open(d/f'keyframes/{t}.png').convert('RGBA').crop(b).save(d/path);p.append({'path':path,'timestamp':float(t),'box':b,'kind':'bounded static message component artwork; internal text bitmap; independent scroll/arrival native'});assets[name]={'id':'source-message-art-'+name,'type':'image','src':path,'x':pos[0],'y':pos[1],'width':b[2]-b[0],'height':b[3]-b[1]}
def replacement(q):
 if q.get('type')!='group':return q
 text=''.join(z.get('text','') for z in q.get('children',[]) if z.get('type')=='text')
 for prefix,name in [('Not me','Dan'),('Oct 17','Oct17'),('Want me','Want'),('Ok we gotta commit','Priya'),('Let’s go!','Book'),('Done. In your calendars','Done')]:
  if text.startswith(prefix):return dict(assets[name])
 q['children']=[replacement(z) for z in q.get('children',[]) if 'booking-eyes' not in z.get('src','') and 'calendar-camp-emoji' not in z.get('src','')]
 if q.get('start')==6.8:
  for z in q['children']:
   if z.get('type') in ['text','image'] and z.get('id')!='source-message-art-Done':z['x']=z.get('x',0)+6
 return q
for g in s['layers']:
 if g.get('start')==3.7:g['children']=[replacement(q) for q in g['children']]
s['source']['notes']+=' Finalv15 uses actual bounded static message-component artwork for the six intro messages after a regional audit isolated font/tail/grouping differences. Arrival, scroll, camera, controls and sender context stay independently native; message-body text is bitmap.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(p,indent=2))
