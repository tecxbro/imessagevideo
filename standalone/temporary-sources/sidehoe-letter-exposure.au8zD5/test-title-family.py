from functools import lru_cache
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageFont
import render
from artwork import font, messages_font

p=Path(sys.argv[1])
scene=json.loads((p/'base/scene.json').read_text())
reference=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
system=Path('/System/Library/Fonts')
@lru_cache(maxsize=200)
def helvetica(size,weight):
    return ImageFont.truetype(system/'HelveticaNeue.ttc',round(size),index=1 if weight>=670 else 0)
@lru_cache(maxsize=200)
def helvetica_classic(size,weight):
    return ImageFont.truetype(system/'Helvetica.ttc',round(size),index=1 if weight>=670 else 0)
@lru_cache(maxsize=200)
def arial(size,weight):
    return ImageFont.truetype(system/'Supplemental'/('Arial Bold.ttf' if weight>=670 else 'Arial.ttf'),round(size))
def inter(size,weight):
    return font(size,weight)
for frame in range(187,198):
    target=np.asarray(Image.open(reference/f'{frame:06d}.png').convert('RGB'),np.int16)
    result=[]
    for family in (messages_font,inter,helvetica,helvetica_classic,arial):
        render.messages_font=family
        try:
            art=np.asarray(render.Film(scene).frame(frame),np.int16)
        except OSError:
            continue
        loss=np.abs(art-target)
        result.append([family.__name__,round(float(loss[410:495,234:758].mean()),4),
                       round(float(loss[486:577,216:778].mean()),4)])
    print(frame,result,flush=True)
