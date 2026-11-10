from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys
from scipy import ndimage
from v8_utils import at
from v10_shape_trace import vector_outline
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v15/scene.json').read_text());g=next(x for x in s['layers'] if x['id']=='p0255');rows=[]
for n in [575,576,583,590,600,629,659,664,667,670,671]:
 f=p/f'measurements-v8/native-v16/{n:06}.png';a=np.array(Image.open(f).convert('RGB'));y=at(g,'y',n/s['fps']);y0=max(0,round(y)+60);y1=min(1080,round(y)+160);m=a[y0:y1,300:1150].max(2)<80;yy,xx=np.where(m);row=dict(frame=n,root_y=y,bounds=None)
 if len(xx) and y+60>=0:row['bounds']=[int(xx.min()+300),int(yy.min()+y0),int(xx.max()+301),int(yy.max()+y0+1)]
 row['surface']={str(dy):a[round(y)+dy,600].tolist() for dy in [0,1,10,20,30,40,50,60] if round(y)+dy in range(1080)};rows.append(row)
# Source540 has the fully visible isolated static body/footer silhouette.
a=np.array(Image.open(p/'measurements-v8/native-v16/000540.png').convert('RGB'));crop=a[274:1005,604:1170];m=(crop.max(2)<248)&((crop.max(2).astype(int)-crop.min(2))<18);rounded=Image.new('L',(554,731));ImageDraw.Draw(rounded).rounded_rectangle((0,0,553,699),radius=52,fill=255);m[:560,:554]=np.array(rounded)[:560]>0;m[:560,554:]=False;m=ndimage.binary_fill_holes(m);lab,_=ndimage.label(m);idx=lab[560,200];m=lab==idx;d=vector_outline(m,(0,0,0,0),(0,0),1)
shape=dict(source_frame=540,source_origin=[604,274],method='Native original gray body/footer component threshold below248, lowchroma18, holes filled; top map interior closed; traced one independently editable silhouette. No source UI bitmap.',d=d)
(p/'measurements-v8/shared-location-body-v16.json').write_text(json.dumps(shape,indent=2));a=np.array(Image.open(p/'measurements-v8/native-v16/000575.png').convert('RGB')).mean(2);gy=at(g,'y',575/s['fps']);vertical=[]
for dy in range(-600,1,10):
 y=round(gy+dy);v=float(np.median(a[max(0,y-2):y+3,400:581]));vertical.append(dict(dy=dy,opacity=max(0,(255-v)/255)))
y=round(gy)-51;horizontal=[]
for x in range(150,1291,20):
 v=float(np.median(a[y-2:y+3,x-2:x+3]));horizontal.append(dict(x=x-250,gain=max(0,min(1,(255-v)/16))))
report=dict(method='Original native575 independent flat background shadow. Vertical samples avoid text/map atx400:580; horizontal samples atsheetTop−51 avoid the map. Opaque canvas255 converts deficit to alpha. Shadow represented by measured editable native strips/one horizontal gradient, moved with independent sheet camera; not a screenshot asset.',title_measurements=rows,shadow_vertical=vertical,shadow_horizontal=horizontal)
(p/'measurements-v8/sheet-ui-v16-source.json').write_text(json.dumps(report,indent=2));print([(r['frame'],r['bounds'])for r in rows]);print('Native body path',len(d))
