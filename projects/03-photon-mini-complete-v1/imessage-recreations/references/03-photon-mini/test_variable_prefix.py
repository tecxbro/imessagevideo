from pathlib import Path
import json
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset
p=Path(__file__).parent;s=json.loads((p/'typography-v11-test.scene.json').read_text());g=next(x for x in s['layers'] if x['id']=='measured-prefix-reveal-v6');chars=''.join(c['text'] for c in g['children'])
f=TTFont('shared/fonts/native/Library/Fonts/SF-Pro.ttf');instantiateVariableFont(f,{'wght':450,'wdth':100,'opsz':28},inplace=True);sub=subset.Subsetter(options=subset.Options());sub.populate(text=chars);sub.subset(f);f.flavor='woff';f.save(p/'assets/SF-Pro-450.prefix.woff');s['fonts'].append({'family':'Recreation Prefix450 UI','src':'assets/SF-Pro-450.prefix.woff','weight':450})
for c in g['children']:c['fontFamily']='Recreation Prefix450 UI';c['fontWeight']=450
(p/'typography-v11-testC.scene.json').write_text(json.dumps(s,indent=2))
