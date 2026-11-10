from pathlib import Path
from PIL import Image
import json,numpy as np
R=Path(__file__).resolve().parent
mapping=json.loads((R/'birth-extra-source/mapping.json').read_text())
rows=[]
for frame in range(930,958):
    if str(frame)in mapping:
        path=Path(mapping[str(frame)])
    else:
        path=R/'source-native'/f'source-{frame:04d}.png'
    image=np.asarray(Image.open(path).convert('RGB'))
    photo=np.nonzero(image[:150,700:800].mean((1,2))<240)[0]
    photo_top=int(photo[0])if len(photo)else 150
    height=max(0,min(100,photo_top-3))
    ink=image[:height,570:690].mean(2)<128
    yy,xx=np.nonzero(ink)
    bounds=None
    if len(xx):bounds=[int(xx.min()+570),int(yy.min()),int(xx.max()+571),int(yy.max()+1)]
    rows.append({'frame':frame,'photoTop':photo_top,'sourceInkBounds':bounds})
(R/'label-exit-ink-measurements.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
