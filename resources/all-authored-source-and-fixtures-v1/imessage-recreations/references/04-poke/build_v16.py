"""Measured editable SharedLocation typography/silhouette and modal surface."""
from pathlib import Path
import json,copy
import numpy as np
from v8_utils import at,track
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v15/scene.json').read_text());fps=s['fps'];g=next(x for x in s['layers'] if x['id']=='p0223');by={n['id']:n for n in g['children']}
shape=json.loads((p/'measurements-v8/shared-location-body-v16.json').read_text());by['p0221'].update(type='path',d=shape['d']);by['p0221'].pop('width');by['p0221'].pop('height');by['p0221'].pop('radius');by['p0222']['opacity']=0
# Actual production browser diagnostic at575, source same-frame ink bounds.
fit=[]
for id,source,browser in [('p0225',[638,521,906,549],[638,521,914,550]),('p0226',[639,568,822,596],[639,571,842,602])]:
 n=by[id];sx=(source[2]-source[0])/(browser[2]-browser[0]);sy=(source[3]-source[1])/(browser[3]-browser[1]);gx=604.0105;gy=-70.9767;nx=source[0]-gx-(browser[0]-gx-n['x'])*sx;ny=source[1]-gy-(browser[1]-gy-n['y'])*sy;n.update(x=nx,y=ny,scaleX=sx,scaleY=sy)
 if id=='p0225':n.update(fontFamily='SF Pro Display',fontWeight=500)
 fit.append(dict(id=id,source_ink=source,browser_ink=browser,x=nx,y=ny,scaleX=sx,scaleY=sy))
(p/'measurements-v8/shared-location-ink-v16.json').write_text(json.dumps(dict(method='Native575 actual production browser diagnostic, confirmed source DisplayMedium title, unchanged subtitle TextRegular; original ink-bound affine fit, later moving within independent map camera.',measurements=fit),indent=2))
# SourceSIFT updates only560..590; explicit559/591controls prevent interpolation leaks.
ledger=json.loads((p/'measurements-v8/shared-location-560-590-v16-parent.json').read_text());rows=[]
for r in ledger['records']:
 m=r['matrix'];rows.append(dict(time=r['frame']/fps,x=m[0][2],y=m[1][2],scaleX=m[0][0],scaleY=m[1][1]))
for prop in ['x','y','scaleX','scaleY']:
 controls=[dict(time=559/fps,**{prop:at(g,prop,559/fps)}),*rows,dict(time=591/fps,**{prop:at(g,prop,591/fps)})];track(g,prop,controls)
# Actual sheet first entry has a shallow tinted top surface and a thin outline.
g=next(x for x in s['layers'] if x['id']=='p0255');by={n['id']:n for n in g['children']};by['p0232'].update(fill='url(#v16-sheet-surface)',stroke='#bdbdbd',strokeWidth=1)
s['gradients'].append(dict(id='v16-sheet-surface',type='linear',stops=[dict(offset='0%',color='#f4f3f6'),dict(offset=f'{42/1900*100}%',color='#f4f3f6'),dict(offset=f'{49/1900*100}%',color='#ffffff'),dict(offset='100%',color='#ffffff')]))
# The independently verified DisplayBold face is retained; its source ink is narrower.
n=by['p0234'];a=[315,739,968,785];b=[315,740,995,789];rx=(a[2]-a[0])/(b[2]-b[0]);ry=(a[3]-a[1])/(b[3]-b[1]);gx=250;gy=at(g,'y',575/fps);n.update(x=a[0]-gx-(b[0]-gx-n['x'])*rx,y=a[1]-gy-(b[1]-gy-n['y'])*ry,scaleX=rx,scaleY=ry)
# Native gradient strips represent the measured separable shadow field. No UI bitmap.
ledger=json.loads((p/'measurements-v8/sheet-ui-v16-source.json').read_text());horizontal=ledger['shadow_horizontal'];s['gradients'].append(dict(id='v16-sheet-shadow-horizontal',type='linear',x1='0%',x2='100%',y1='0%',y2='0%',stops=[dict(offset=f'{(r["x"]+100)/1140*100}%',color='#000000',opacity=r['gain'])for r in horizontal]));vertical=ledger['shadow_vertical'];yy=[r['dy']for r in vertical];aa=[r['opacity']for r in vertical];strips=[]
for y in range(-600,151,10):
 opacity=float(np.interp(y+5,yy,aa));strips.append(dict(id=f'v16-sheet-shadow-{y+600}',type='rect',x=-100,y=y,width=1140,height=10,fill='url(#v16-sheet-shadow-horizontal)',opacity=opacity))
g['children']=[*strips,*g['children']]
s['title']='Poke Apple Messages launch — native recreation v16 measured location and modal UI'
s['source']['notes']+=' V16 repairs independently measured source575 graphic UI: SharedLocation title matches DisplayMedium rather than TextRegular; native browser ink fitting restores both caption widths/heights/positions, unchanged subtitle family. One static native gray-body outline captures the original540footer/tail. Source560–590 mapSIFT refines only its~1px late camera offset, with original559/591guards. Restaurant sheet retains verified DisplayBold but fits original ink size, and restores its separate shallow tinted top material, thin outline and measured native gradient shadow. No full source frame or UI bitmap is output artwork.'
(p/'scene-v16-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));print('V16 candidate ready')
