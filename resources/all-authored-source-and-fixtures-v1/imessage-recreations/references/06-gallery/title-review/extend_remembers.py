from pathlib import Path
from PIL import Image
from scipy.ndimage import label
import numpy as np,json
R=Path(__file__).resolve().parent;rows=json.loads((R/'remembers-measurements.json').read_text());art={q['label']:q for q in json.loads((R/'remembers-outlines.json').read_text())};cuts=[(340,968),(968,1213),(1213,1580)]
for record,(left,right) in zip(rows,cuts):
 a=art[record['label']];record['poses']=[p for p in record['poses'] if p['frame']<=580]
 for n in range(581,597):
  rgb=np.asarray(Image.open(R/'remembers-native'/f'{n:06d}.png').convert('RGB')).astype(float);target=(255-rgb[450:650,left:right].mean(2))/255;peak=float(np.quantile(target[target>.35*target.max()],.96));labs,num=label(target>peak*.5);sz=np.bincount(labs.ravel());keep=sz>=4;keep[0]=False;yy,xx=np.nonzero(keep[labs]);b=[int(xx.min()+left),int(yy.min()+450),int(xx.max()+left+1),int(yy.max()+451)];record['poses'].append(dict(frame=n,x=b[0],y=b[1],scaleX=(b[2]-b[0])/a['width'],scaleY=(b[3]-b[1])/a['height'],opacity=peak,blur=0,sourceInkBounds=b,method='Native per-word held-caption bounds; source-derived geometry, no source frame layer.'))
(R/'remembers-final-measurements.json').write_text(json.dumps(rows,indent=2));print('Extended held semantic word poses581–596, preserve597+',flush=True)
