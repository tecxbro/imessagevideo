from pathlib import Path
from PIL import Image,ImageDraw
import json
r=Path('/workspace/imessage-recreations');d=r/'references/06-gallery';s=json.loads((d/'scene.json').read_text());prov=json.loads((d/'assets/asset-provenance.json').read_text())
for name,box in [('dan-memoji',(596,776,659,841)),('camp-emoji',(1013,383,1051,421))]:
 im=Image.open(d/'keyframes/003.00.png').convert('RGBA').crop(box);im.save(d/f'assets/{name}.png');prov.append({'path':f'assets/{name}.png','timestamp':3,'box':box,'kind':'isolated sourceMemoji/emoji texture'})
for g in s['layers']:
 if g.get('start')!=1.1:continue
 out=[]
 for q in g['children']:
  # Converse positions were72px low atcamera settle; native camera scale1.214means−60local.
  if q.get('text')=='👨' or (q.get('type')=='circle' and q.get('fill')=='#e4d6ff'):continue
  if q.get('y',0)>=300 and q.get('src')!='assets/phone-hardware-ring.png':q['y']-=60;q['x']=q.get('x',0)+4.1
  if q.get('src')=='assets/phone-hardware-ring.png':q['scaleX']=1.027
  if q.get('type')=='rect' and q.get('x')==27 and q.get('y')==24:q['width']=652
  if q.get('type')=='rect' and q.get('x')==242 and q.get('y')==48:q['x']=251;q['width']=201.5
  if q.get('text')=='12:02':q['x']+=6.5
  if q.get('type')=='circle' and q.get('x')==405:q['x']=414
  if q.get('type')=='circle' and q.get('x')==543 and q.get('y')==136:q['x']+=20
  if q.get('type')=='rect' and q.get('x')==563 and q.get('y')==157:q['x']+=20
  if q.get('d','').startswith('M 594 165'):q['x']=20
  if q.get('text')=='Cabin trip 🏕️':q.update(text='Cabin trip',x=254.5,fontSize=30,textAnchor='start')
  out.append(q)
 out +=[{'id':'intro-camp-emoji-v9','type':'image','src':'assets/camp-emoji.png','x':393.7,'y':257.8,'width':31.3,'height':31.3},{'id':'intro-dan-memoji-v9','type':'image','src':'assets/dan-memoji.png','x':50.3,'y':581.5,'width':52,'height':53.5},{'id':'intro-rene-avatar-restored-v9','type':'image','src':'assets/rene-mascot.png','x':60.1,'y':720,'width':36,'height':42}]
 g['children']=out
s['source']['notes']+=' Finalv9native3sframeauditcorrectsintroconversation−72px, physicalphonewidthandstatus/camerafit, andoriginalDan/campemojiassets; v8birthday/inbox/camerafixesretained.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2))
print('Intro actual3sgeometry corrected')
