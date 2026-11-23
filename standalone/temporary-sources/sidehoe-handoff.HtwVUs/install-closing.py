from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import interpolate

p=Path(sys.argv[1])
scene_path=p/'project/scene.json'
scene=json.loads(scene_path.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
wash=scene['tracks']['closingWashFields']
fits=json.loads((p/'wash-fit.json').read_text())
fitted={f:data for f,data,a,b in fits if b<a-.07}
scene['tracks']['closingWashFields']=[
    [f,*fitted.get(f,interpolate(wash,f))]
    for f in sorted({r[0] for r in wash}|set(range(711,777)))
]
styles=json.loads((p/'closing-ink-fit.json').read_text())
assert all(s.pop('family')=='messages' for s in styles.values())
scene['closingInkAppearance']=styles
for pair in scene['tracks']['endingFade']:
    f,val=pair
    if not 766<=f<=776:
        continue
    rgb=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'))
    flat=float(np.median(rgb[40:200,200:760]))
    assert flat>0 and flat<253
    raw=int(val*253)
    if abs(flat-raw)>.1:
        pair[1]=round((flat+.38)/253,7)
scene_path.write_text(json.dumps(scene,indent=2,ensure_ascii=False)+'\n')
print('active wash fits',len(fitted))
print('fade',scene['tracks']['endingFade'])
