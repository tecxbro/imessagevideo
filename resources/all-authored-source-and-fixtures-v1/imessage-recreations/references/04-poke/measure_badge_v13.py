"""Source-only coherent verification badge component positions, native72–108."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;rows=[]
for n in range(66,109):
    a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'));roi=a[500:850,750:940];m=(roi.max(2)<190)&(roi.min(2)>60)&(roi.max(2)-roi.min(2)<12);labels,_=ndimage.label(m);found=[]
    for i,sl in enumerate(ndimage.find_objects(labels),1):
        if sl is None:continue
        yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
        if 43<w<90 and 43<h<90:found.append(dict(bbox=[xx.start+750,yy.start+500,xx.stop+750,yy.stop+500],gray=int(np.median(roi[labels==i]))))
    if len(found)>1:raise ValueError((n,found))
    rows.append(dict(frame=n,time=n*1001/30000,observed=found[0]if found else None))
report=dict(method='Coherent original gray badge component, distinct compact star outline; search x750:940,y500:850, achromatic60..190, width/height44..89. Missing detection retained separately, first visually coherent72. Component bounds are ink, not image advance.',measurements=rows)
(p/'measurements-v8/verified-badge-v13.json').write_text(json.dumps(report,indent=2));print([(r['frame'],r['observed'])for r in rows])
