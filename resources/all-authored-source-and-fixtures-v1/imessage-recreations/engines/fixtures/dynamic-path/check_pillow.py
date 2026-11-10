from pathlib import Path
import sys,json
p=Path(__file__).resolve().parent;sys.path.insert(0,str(p.parents[1]))
import render_pillow as rp
from PIL import Image
s=json.load(open(p/'scene.json'));rp.register_fonts(s,str(p))
for f in (0,5,6,7,12,13):rp.render(s,f/s['fps'],str(p)).save(p/f'pillow-{f}.png')
