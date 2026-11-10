from pathlib import Path
from PIL import Image
import json
r=Path('/workspace/imessage-recreations');d=r/'references/06-gallery';s=json.loads((d/'scene.json').read_text())
# Actual static soccerballtexture atsourceframe891; independenteditablemotion remains.
src=r/'verification/fidelity-review/06-gallery/final-v4/29.70-reference.png';im=Image.open(src).convert('RGBA').crop((765,535,921,691));im.save(d/'assets/soccer-word-frame891.png')
p=json.loads((d/'assets/asset-provenance.json').read_text());p.append({'path':'assets/soccer-word-frame891.png','source':'source.mp4','frame':891,'timestamp':29.7,'box':[765,535,921,691],'kind':'isolated static soccer-ball texture forwordphase, independentlyanimated'});(d/'assets/asset-provenance.json').write_text(json.dumps(p,indent=2))
for g in s['layers']:
 for tx in g.get('children',[]):
  if tx.get('type')=='text' and tx.get('text')=='you':tx['x']=968
 if g.get('start')==29.7 and any(x.get('text')=='ve' for x in g.get('children',[])):
  g['keyframes']['y']=[{'t':29.7,'value':0},{'t':29.7666667,'value':-42,'ease':'easeOut'}]
  for q in g['children']:
   if q.get('text')=='l':q.update(fontFamily='Rene Word Fit',fontSize=292,fontWeight=500,x=675.5,y=404,scaleX=.968,lineHeight=344.56)
   elif q.get('text')=='ve':q.update(fontFamily='Rene Word Fit',fontSize=292,fontWeight=500,x=940.1,y=405,scaleX=.966,lineHeight=344.56)
   elif q.get('type')=='image':
    q.update(src='assets/soccer-word-frame891.png',x=765,y=535,width=156,height=156)
    q['keyframes']={'x':[{'t':29.7,'value':765},{'t':29.7666667,'value':757,'ease':'easeOut'}],'y':[{'t':29.7,'value':535},{'t':29.7666667,'value':492,'ease':'easeOut'}]}
s['source']['notes']+=' Finalv6 refinesl/vewithmeasuredInterMediumperglyphbounds andisolatedframe891soccertexture/bounce; youx−3px. Onlyframes846–953differfromv4.'
(d/'scene.json').write_text(json.dumps(s,indent=2))
print('Measuredlovephase corrected')
