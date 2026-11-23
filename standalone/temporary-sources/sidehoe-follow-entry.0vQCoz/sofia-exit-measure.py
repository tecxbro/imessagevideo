import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label, find_objects
root=Path(__file__).parent
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
prior=Path('/tmp/sidehoe-phone.tJtcYo/final-frames')
results={}
for f in range(351,360):
    records=[]
    for folder in (source,prior):
        q=np.asarray(Image.open(folder/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
        Q=q[0:313,27:818]
        y,x=np.mgrid[0:313,27:818]
        gray=(np.ptp(Q,axis=2)<9)
        paper=np.median(q[255:725,50:115],axis=(0,1))
        out=[]
        for low,hi in ((0,180),(180,235),(235,244),(244,250),(250,253)):
            bands=gray & (Q[:,:,0]>=low)&(Q[:,:,0]<hi)
            comps,nn=label(bands)
            areas=[]
            for i, (yy,xx) in enumerate(find_objects(comps),1):
                n=(comps[yy,xx]==i).sum()
                if n<40 or xx.stop-xx.start<18:
                    continue
                areas.append([int(n),[xx.start+27,yy.start,xx.stop+27,yy.stop]])
            out.append(sorted(areas,reverse=True)[:4])
        dark=q[250:600,925:]
        edge=np.median(dark,axis=(0,2)).astype(float)
        dark_cols=np.flatnonzero(edge<85)
        rail=None if not dark_cols.size else [int(dark_cols[0])+925,int(dark_cols[-1])+925,float(edge.min())]
        neutral=q[724:900,100:800]
        rowtones=np.median(neutral,axis=(1,2))
        tray=np.flatnonzero(rowtones<246)
        records.append(dict(gray=out,rail=rail,trayTop=int(tray[0])+724 if len(tray) else None,paper=paper.tolist()))
    results[f]=records
    if f in (353,354,355,356,357):
        print(f,*records,sep='\n')
(root/'sofia-exit-measurements.json').write_text(json.dumps(results,indent=2)+'\n')
