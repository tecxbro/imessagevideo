from pathlib import Path
import json
from fontTools import subset
p=Path(__file__).parent
scene=json.loads((p/'scene.json').read_text());chars=set(' ')
def visit(l):
 if l['type']=='text':chars.update(l.get('text',''))
 for child in l.get('children',[]):visit(child)
for l in scene['layers']:visit(l)
for f in scene['fonts']:
 original=p/f['src'];out=original.with_suffix('.scene.woff')
 font=subset.load_font(str(original),subset.Options())
 sub=subset.Subsetter(options=subset.Options());sub.populate(text=''.join(chars));sub.subset(font);font.flavor='woff';font.save(out);f['src']=str(out.relative_to(p))
scene['source']['notes'] += ' Official fonts subset to used scene characters for portable rendering.'
(p/'scene.json').write_text(json.dumps(scene,indent=2))
print('Subset',len(scene['fonts']),'fonts',sum((p/f['src']).stat().st_size for f in scene['fonts']),'bytes')
