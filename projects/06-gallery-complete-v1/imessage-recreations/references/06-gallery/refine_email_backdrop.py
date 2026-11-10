from pathlib import Path
from PIL import Image
import json
r=Path('/workspace/imessage-recreations');d=r/'references/06-gallery';s=json.loads((d/'scene.json').read_text());p=json.loads((d/'assets/asset-provenance.json').read_text())
# Real bounded email-application panels. The foreground phone is excluded entirely.
source=Image.open(d/'keyframes/018.00.png').convert('RGBA');assets=[]
for name,b in [('email-list-left',(0,0,622,1080)),('email-list-right',(1248,0,1920,1080))]:
 path=f'assets/{name}.png';source.crop(b).save(d/path);p.append({'path':path,'timestamp':18,'box':b,'kind':'bounded email application background pane; foreground phone excluded; internal email text bitmap'});assets.append({'id':name+'-source-art','type':'image','src':path,'x':b[0],'y':b[1],'width':b[2]-b[0],'height':b[3]-b[1]})
plate={'id':'measured-email-panes-v13','type':'group','children':assets,'start':17.3,'end':18.5,'keyframes':{'opacity':[{'t':17.3,'value':0},{'t':18,'value':1},{'t':18.2,'value':1},{'t':18.5,'value':0}],'y':[{'t':17.3,'value':20},{'t':18,'value':0},{'t':18.2,'value':0},{'t':18.5,'value':-30}]}}
idx=next(i for i,g in enumerate(s['layers']) if g.get('start')==16.7);s['layers'].insert(idx,plate)
for g in s['layers']:
 if g.get('start')==16.7:
  for q in g['children']:
   if q.get('type')=='image' and 'phone-hardware-ring' in q.get('src',''):
    q['keyframes']={'scaleX':[{'t':16.7,'value':1},{'t':17.2,'value':1},{'t':18,'value':1.01}],'x':[{'t':16.7,'value':0},{'t':17.2,'value':0},{'t':18,'value':-2.2}],'y':[{'t':16.7,'value':0},{'t':17.2,'value':0},{'t':18,'value':-2.2}]}
s['source']['notes']+=' Finalv13 replaces approximate outer email rows with declared bounded actual email-application panes, with the foreground phone excluded; native phone, messages and camera stay separate. Only source17.2–18.5 differs fromv12.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(p,indent=2))
