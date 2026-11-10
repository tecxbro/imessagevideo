from pathlib import Path
from PIL import Image,ImageDraw
import json,copy
r=Path('/workspace/imessage-recreations');d=r/'references/06-gallery';s=json.loads((d/'scene.json').read_text())
# Exactstaticcropalphacleanups: keeprealpictorialpixels, remove rectangularbackground.
for name in ['birthday-gift-emoji.png','dan-memoji.png']:
 p=d/'assets'/name;im=Image.open(p).convert('RGBA')
 if name.startswith('dan'):
  mask=Image.new('L',im.size);ImageDraw.Draw(mask).ellipse((0,0,im.width-1,im.height-1),fill=255);im.putalpha(mask)
 else:
  pix=im.load()
  for yy in range(im.height):
   for xx in range(im.width):
    rr,gg,bb,aa=pix[xx,yy]
    if max(rr,gg,bb)-min(rr,gg,bb)<30 or rr<55:pix[xx,yy]=(rr,gg,bb,0)
 im.save(p)
# Smallsourceavatarpreservesoriginaltinylogostrokeatnativeview.
box=(605,942,651,990);im=Image.open(d/'keyframes/003.00.png').convert('RGBA').crop(box);im.save(d/'assets/intro-rene-avatar-source.png')
prov=json.loads((d/'assets/asset-provenance.json').read_text());prov.append({'path':'assets/intro-rene-avatar-source.png','timestamp':3,'box':box,'kind':'isolatedtinyRenemark'});(d/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2))
for g in s['layers']:
 if g.get('start')==1.1:
  for q in g['children']:
   if q.get('id')=='intro-rene-avatar-restored-v9':q.update(src='assets/intro-rene-avatar-source.png',x=57.66,y=718.29,width=37.89,height=39.54)
   if q.get('type')=='group':
    texts=[z.get('text','') for z in q.get('children',[]) if z.get('type')=='text'];tt=''.join(texts)
    if tt.startswith('We’ve'):q['y']+=2
    if tt.startswith('Someone'):q['y']+=.7
    for z in q.get('children',[]):
     if z.get('type')=='text':
      z['x']=22;z['fontSize']=26.5;z['lineHeight']=31.3;z['y']=14 if tt.startswith('Not me') else 12
 if g.get('start')==16.7:
  for q in g['children']:
   if q.get('type')!='group':continue
   tx=''.join(z.get('text','') for z in q.get('children',[]) if z.get('type')=='text')
   b=q['children'][0]
   if tx.startswith('Heads up'):q.update(x=43,y=334);b.update(width=480,height=137)
   elif tx.startswith('3 similar'):q.update(x=42,y=480);b.update(width=482,height=145)
   elif tx=='Yes plz':q.update(x=501,y=649);b.update(width=140,height=76)
   elif tx.startswith('It’s in your drafts'):q.update(x=43,y=737);b.update(width=480,height=109)
 if g.get('start')==18.5:
  for t in g.get('children',[]):
   if t.get('text')=='Remembers your people':t.update(x=958,y=455,fontWeight=500,fill='#000000',scaleX=.991)
  g.update(originX=960,originY=540)
  g['keyframes']['scaleX']=[{'t':18.5,'value':1},{'t':20.5,'value':1},{'t':21.5,'value':.5,'ease':'easeOut'}]
  g['keyframes']['scaleY']=[{'t':18.5,'value':1},{'t':20.5,'value':1},{'t':21.5,'value':.5,'ease':'easeOut'}]
# Blurduplicatednativeportraitnodesbehindglassycard; internalfaceassetsremainseparateeditablelayers.
faces=[copy.deepcopy(g) for g in s['layers'] if len(g.get('children',[]))==1 and 'portrait-' in g['children'][0].get('src','')]
def rename(q):
 q['id']+='-birthday-backdrop'
 for c in q.get('children',[]):rename(c)
for g in faces:rename(g)
for g in s['layers']:
 if g.get('start')==21.9:
  for q in g['children']:
   if q.get('text')=='Emma’s birthday is Saturday':q['fontSize']=52.5;q['y']=196
   if q.get('text')=='Rene':q['fontSize']=50;q['y']=124
   if q.get('src')=='assets/rene-mascot.png':q.update(x=439,y=142,width=94,height=105)
   if q.get('type')=='rect' and q.get('x')==356:q['opacity']=.85
  base={'id':'birthday-backdrop-base-v10','type':'rect','x':356,'y':62,'width':1208,'height':260,'radius':102,'fill':'#ffffff'}
  backdrop={'id':'birthday-blurred-portraits-v10','type':'group','clip':{'x':356,'y':62,'width':1208,'height':260,'radius':102},'blur':12,'children':faces}
  g['children']=[base,backdrop]+g['children']
s['source']['notes']+=' Finalv10fitsnativeintrotextpadding, exactsource18landlordbubblebounds, original19.5headlinebaseline/weightandsource21.5halfscalesettle, birthdayglassyblurredportraitbackdropandgiftalpha.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'revision-final-v10.json').write_text(json.dumps({'changes_vs_v4_output_ranges':[[1.1,3.6],[16.7,22.9],[28.2,31.8]],'changed_frame_ranges_inclusive':[[33,107],[501,686],[846,953]],'evidence_frames':[3,17,18,19.5,21.5,22.1,29.4,29.7]},indent=2));print('Measuredv10scene written')
