from pathlib import Path
from fontTools import subset
import json,hashlib
root=Path('/workspace/imessage-recreations')
for directory in ['05-linq','06-gallery']:
 d=root/'references'/directory
 scene=json.loads((d/'scene.json').read_text())
 chars=set()
 def walk(ls):
  for l in ls:
   chars.update(l.get('text',''));walk(l.get('children',[]))
 walk(scene['layers']);chars.update(' ')
 rows=[]
 for style,weight in [('Regular',400),('Medium',500),('Semibold',600),('Bold',700)]:
  source=root/f'shared/fonts/SF-Pro-Display-{style}.otf';dest=d/f'assets/sf-pro-display-used-{style.lower()}.otf'
  options=subset.Options();options.layout_features=['*'];options.name_IDs=['*'];options.name_legacy=True
  font=subset.load_font(str(source),options);sub=subset.Subsetter(options=options);sub.populate(text=''.join(sorted(chars)));sub.subset(font);subset.save_font(font,str(dest),options)
  rows.append({'family':'SF Pro Display','weight':weight,'source':str(source),'subset':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size,'characters':len(chars)})
 (d/'assets/font-subsets.json').write_text(json.dumps(rows,indent=2));print(directory,[(x['weight'],x['bytes']) for x in rows])
