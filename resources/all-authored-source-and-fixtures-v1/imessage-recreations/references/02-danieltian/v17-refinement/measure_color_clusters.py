from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
R=Path(__file__).resolve().parent
rows=[]
for frame in range(272,375):
    image=np.asarray(Image.open(R/'reasoning-source'/f'source-{frame:04d}.png').convert('RGB')).astype(float)
    color=(image.max(2)-image.min(2)>12)&(image.min(2)<235)
    grown=ndimage.binary_dilation(color,iterations=6)
    labels,count=ndimage.label(grown)
    clusters=[]
    for label,box in enumerate(ndimage.find_objects(labels),1):
        if box is None:continue
        yy,xx=box
        mask=(labels[box]==label)&color[box]
        y,x=np.nonzero(mask)
        if len(x)<8:continue
        bounds=[int(x.min()+xx.start),int(y.min()+yy.start),int(x.max()+xx.start+1),int(y.max()+yy.start+1)]
        clusters.append({'bounds':bounds,'pixels':len(x),'center':[(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2]})
    rows.append({'frame':frame,'clusters':clusters})
(R/'reasoning-color-clusters.json').write_text(json.dumps(rows,indent=2))
anchors=[272,273,275,280,287,289,290,293,296,300,310,320,330,350,360]
for row in rows:
    if row['frame']in anchors:print(row)
