import json
from pathlib import Path
import numpy as np
from PIL import Image
from trace import trace

work=Path(__file__).parent
observations={row['frame']:row for row in json.loads((work/'analysis.json').read_text())}
out=work/'probe-native'
out.mkdir(exist_ok=True)
rows=[]
for f in range(673,697):
    old=Image.open(work.parent/'sidehoe-clean-frames'/f'{f:06d}.png').convert('RGB')
    evaluated=observations[f]
    replacement=None
    if 674<=f<=694:
        target=np.array(evaluated['source']['pointer'][1]['tip'])
        rendered=np.array(evaluated['pre2000']['pointer'][1]['tip'])
        before_pivot=np.array(evaluated['cursorPivot'])
        replacement=(before_pivot + target - rendered)/2
    im,unused=trace(f,replacement)
    before=np.asarray(old)
    after=np.asarray(im)
    changed=np.any(before!=after,2)
    pixels=int(changed.sum())
    if replacement is None:
        assert pixels==0,f
    elif pixels:
        ys,xs=np.where(changed)
        assert min(xs)>=420 and max(xs)<560 and min(ys)>=505 and max(ys)<660,f
        # Remove only the cursor and compare actual phone/other pixels to prove the edit's role.
        blank,_=trace(f,(10_000,10_000))
        clean=np.asarray(blank)
        assert not np.any(changed & np.all(before==clean,2) & np.all(after==clean,2))
    rows.append(dict(frame=f,changedNativePixels=pixels,sourceObservedAtLumaThreshold=110 if replacement is not None else None,candidatePivot=None if replacement is None else (replacement*2).tolist()))
    im.save(out/f'{f:06d}.png',compress_level=1)
(work/'probe-scope.json').write_text(json.dumps(rows,indent=2)+'\n')
