"""Native original/candidate sentence ink and static editable incoming silhouette."""
from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy import ndimage
from v8_utils import at
from v10_shape_trace import vector_outline
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((p/'scene-v19-prototype-01.json').read_text());g=next(x for x in s['layers']if x['id']=='v19-Sarah-incoming');node=next(x for x in g['children']if x['id']=='v19-p0065');raw=json.loads((p/'measurements-v8/sarah-entry-142-175-v19-parent.json').read_text());rows=[]
for n in range(142,176):
 t=n/s['fps'];r=next(r for r in raw['records']if r['frame']==n);observed=r['bounded_text_band']['observations'];preferred=160 if n<=149 else 100;entry=next(a for a in observed if a['threshold']==preferred);a=entry['bounds'];threshold=entry['threshold'];image=np.array(Image.open(root/f'outputs/04-poke/qa-v19-prototype-01/{n:06}.png').convert('RGB'));gx,gy,sx,sy=[at(g,k,t)for k in ['x','y','scaleX','scaleY']];y0=max(0,int(gy+15*sy));y1=min(1080,int(gy+145*sy));crop=image[y0:y1,150:1290];mask=crop.max(2)<threshold;yy,xx=np.where(mask);b=[int(xx.min()+150),int(yy.min()+y0),int(xx.max()+151),int(yy.max()+y0+1)];rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);nx=gx+at(node,'x',t)*sx;ny=gy+at(node,'y',t)*sy
 rows.append(dict(frame=n,time=t,threshold=threshold,source_ink=a,candidate_ink=b,x=(a[0]-(b[0]-nx)*rx-gx)/sx,y=(a[1]-(b[1]-ny)*ry-gy)/sy,scaleX=at(node,'scaleX',t)*rx,scaleY=at(node,'scaleY',t)*ry))
(p/'measurements-v8/sarah-ink-v19.json').write_text(json.dumps(dict(method='Matched native source/candidate glyph threshold100 when coherent,160for faint142/143; each original sentence band excludes underline and later calendar. Parent camera/blur are held independent. Current source-confirmed TextRegular retained; fit actual browser ink, not advances.',measurements=rows),indent=2))
a=np.array(Image.open(p/'measurements-v8/native-v19/000165.png').convert('RGB'));crop=a[420:650,100:1340];mask=crop.max(2)<247;mask=ndimage.binary_fill_holes(mask);labels,_=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0;mask=labels==sizes.argmax();gx=at(g,'x',165/s['fps']);gy=436.;d=vector_outline(mask,(100,420,0,0),(gx,gy),1)
(p/'measurements-v8/sarah-outline-v19.json').write_text(json.dumps(dict(source_frame=165,origin=[gx,gy],source_threshold=247,d=d,method='Single static original neutral gray main-pill/tail contour, text holes filled, traced as editable native vector. No source UI bitmap. Independent camera/blur reuses this shape across source-confirmed lifecycle.'),indent=2))
print([(r['frame'],r['threshold'],r['source_ink'],r['candidate_ink'],round(r['y'],3))for r in rows if r['frame']in [142,145,150,165,174,175]])
