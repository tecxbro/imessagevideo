from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from fontTools import subset
import json,hashlib
root=Path('/workspace/imessage-recreations');d=root/'references/06-gallery';s=json.loads((d/'scene.json').read_text())
# Source textmask fitting ranks InterMedium above SF variants for the isolated wordyou.
font=root/'references/01-photonhq/assets/Inter-500.ttf';dest=d/'assets/inter-word-fit-500.ttf'
o=subset.Options();o.layout_features=['*'];ft=subset.load_font(str(font),o);sub=subset.Subsetter(options=o);sub.populate(text='you lve');sub.subset(ft);subset.save_font(ft,str(dest),o)
s['fonts'].append({'family':'Rene Word Fit','src':'assets/inter-word-fit-500.ttf','weight':500})
changed=[]
for g in s['layers']:
 children=g.get('children',[])
 for tx in children:
  if tx.get('type')=='text' and tx.get('text')=='you':
   tx.update(fontFamily='Rene Word Fit',fontSize=292,fontWeight=500,x=971,y=362,scaleX=.958,lineHeight=344.56)
   tx['keyframes']={'y':[{'t':28.2,'value':362},{'t':29.5,'value':362},{'t':29.6,'value':351},{'t':29.6666667,'value':333}]};changed.append(tx['id'])
 if g.get('start')==29.7 and any(x.get('text')=='ve' for x in children):
  g['keyframes']['opacity']=[{'t':29.7,'value':1}]
  g['keyframes']['y']=[{'t':29.7,'value':42},{'t':29.7666667,'value':0,'ease':'easeOut'}]
  # Keepmeasured reststategeometry; onlyentrytimeandbouncechange.
  changed.append(g['id'])
s['source']['notes']+=' Finalv5 fixes exactframe891 love opacity and measured verticalbounce; isolated you is fitted with InterMedium based on native textmask error, distinct from SFUI. Changed native phase28.2–31.8s only.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'word-phase-v5.json').write_text(json.dumps({'changed_ids':changed,'changed_output_range':[28.2,31.8],'changed_frame_range_inclusive':[846,953],'font_source':str(font),'font_source_sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'subset_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'fit_evidence':'font-fit-you.json'},indent=2))
print(changed)
