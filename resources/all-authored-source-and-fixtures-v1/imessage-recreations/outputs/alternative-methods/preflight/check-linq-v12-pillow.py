from pathlib import Path
import json,sys
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));import render_pillow as rp
p=root/'outputs/05-linq/final-v12/scene.json';s=json.load(open(p));rp.register_fonts(s,str(p.parent))
for f in (105,111,933):
 rp.render(s,f/30,str(p.parent)).save(root/'outputs/alternative-methods/preflight'/f'05-v12-pillow-{f}.png');print(f,flush=True)
