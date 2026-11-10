from pathlib import Path
import ast,json
import numpy as np
from scipy import ndimage
from scipy.spatial import ConvexHull
from PIL import Image
p=Path(__file__).parent
# Reuse pure measurement functions without rerunning their acquisition loop.
module=ast.parse((p/'measure_entrance_v13.py').read_text());nodes=[n for n in module.body if isinstance(n,ast.FunctionDef)];env={'np':np,'ndimage':ndimage,'ConvexHull':ConvexHull};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<measurement-functions>','exec'),env)
rows=json.loads((p/'entrance-v13-measurements.json').read_text())
for index,row in enumerate(rows):
 a=np.array(Image.open(p/'entrance-native'/f'{index+1:03}.png').convert('RGB'),dtype='int16')
 if row['t']>=14.6333333333 and 'alice' in row['avatars']:
  prior=row['avatars']['alice'];choices=[]
  for mask,box in env['components'](env['color_mask'](a,'alice')):
   fit=env['circle'](mask)
   if fit and fit['residual']<4 and prior['radius']*.6<fit['radius']<prior['radius']*1.4:
    distance=np.hypot(fit['cx']-prior['cx'],fit['cy']-prior['cy']);choices.append((distance,fit))
  if choices:row['avatars']['alice']=min(choices,key=lambda q:q[0])[1]
 actors=list(row['avatars'].values())
 if not actors:continue
 radius=max(v['radius'] for v in actors);xs=[v['cx']-v['radius'] for v in actors]+[v['cx']+v['radius'] for v in actors];ys=[v['cy']-v['radius'] for v in actors]+[v['cy']+v['radius'] for v in actors];span=max(max(xs)-min(xs),max(ys)-min(ys));margin=span*.22
 x0=max(0,int(min(xs)-margin));x1=min(1920,int(max(xs)+margin));y0=max(0,int(min(ys)-margin));y1=min(1080,int(max(ys)+margin))
 if 'first_T' in row:y1=min(y1,row['first_T']['y']-8)
 gray=(a.max(2)-a.min(2)<4)&(a.mean(2)>231)&(a.mean(2)<252.5);gray[:,:x0]=False;gray[:,x1:]=False;gray[:y0]=False;gray[y1:]=False
 # Use the union of the plate's visible disconnected pieces. Memoji can touch
 # its rim and split its background into multiple connected components.
 labeled,n=ndimage.label(gray);counts=np.bincount(labeled.ravel());valid=counts>=30;valid[0]=False;gray=valid[labeled];fit=env['circle'](gray)
 row.pop('gray_circle',None)
 target=np.mean([[v['cx'],v['cy']] for v in actors],0)
 if fit and fit['residual']<4 and radius*1.2<fit['radius']<radius*3.3 and np.hypot(fit['cx']-target[0],fit['cy']-target[1])<radius:
  fit['gray']=float(np.median(a[gray].mean(1)));row['gray_circle']=fit
(p/'entrance-v13-measurements.json').write_text(json.dumps(rows,indent=2));print('gray',sum('gray_circle'in r for r in rows));print(json.dumps([r for r in rows if r['frame'] in [439,457,472,495]],indent=2))
