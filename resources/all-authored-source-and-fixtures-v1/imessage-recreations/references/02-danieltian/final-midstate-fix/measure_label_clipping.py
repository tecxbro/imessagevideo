from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
ROOT=R.parents[2]
extra=json.loads((R/'birth-extra-source/mapping.json').read_text())
rows=[]
for frame in range(894,958):
    if str(frame)in extra:path=Path(extra[str(frame)])
    else:path=R/'source-native'/f'source-{frame:04d}.png'
    source=np.asarray(Image.open(path).convert('RGB'))
    native=np.asarray(Image.open(ROOT/'outputs/02-danieltian/frames-gsap'/f'{frame:06d}.png').convert('RGB'))
    first_photo=np.nonzero(source[:180,700:800].mean((1,2))<240)[0]
    photo_top=int(first_photo[0])if len(first_photo)else 180
    height=max(0,min(150,photo_top))
    s_ink=source[:height,550:710].mean(2)<128
    n_ink=native[:height,550:710].mean(2)<128
    sy,sx=np.nonzero(s_ink)
    ny,nx=np.nonzero(n_ink)
    source_bounds=[int(sx.min()+550),int(sy.min()),int(sx.max()+551),int(sy.max()+1)]if len(sx)else None
    native_bounds=[int(nx.min()+550),int(ny.min()),int(nx.max()+551),int(ny.max()+1)]if len(nx)else None
    row={'frame':frame,'photoTop':photo_top,'sourceInkBounds':source_bounds,'nativeInkBounds':native_bounds}
    if source_bounds and source_bounds[1]==0 and source_bounds[3]<22:
        baseline_bottom=native_bounds[3]if photo_top>=25 else 24
        row['nativeYCorrection']=source_bounds[3]-baseline_bottom
        row['clippedSource']=True
    if not source_bounds and frame>=955:row['hideOriginalLabel']=True
    rows.append(row)
(R/'label-clipping-measurements.json').write_text(json.dumps(rows,indent=2))
print(json.dumps([q for q in rows if q.get('clippedSource')or q.get('hideOriginalLabel')],indent=2))
