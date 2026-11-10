from pathlib import Path
import json
from fontTools import subset
p=Path(__file__).parent;s=json.loads((p/'final-v10.scene.json').read_text());g=next(x for x in s['layers'] if x['id']=='measured-prefix-reveal-v6');chars=''.join(c['text'] for c in g['children'])
font=subset.load_font('shared/fonts/SF-Pro-Display-Medium.otf',subset.Options());sub=subset.Subsetter(options=subset.Options());sub.populate(text=chars);sub.subset(font);font.flavor='woff';font.save(p/'assets/SF-Pro-Display-Medium.prefix.woff')
s['fonts'].append({'family':'Recreation Prefix UI','src':'assets/SF-Pro-Display-Medium.prefix.woff','weight':500})
for c in g['children']:c['fontFamily']='Recreation Prefix UI';c['fontWeight']=500
for k in g['keyframes']['y']:k['value']-=10 if k['t']<=32.8 else 8
for k in g['keyframes']['x']:k['value']+=1
cta=next(x for x in s['layers'] if x['id']=='p03-699')
for c in cta['children']:c['fontWeight']=600
(p/'typography-v11-test.scene.json').write_text(json.dumps(s,indent=2))
