"""Replace measured menu copy with bounded semantic native glyph outlines."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
p=Path(__file__).parent;sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'menu-v13.scene.json').read_text());clip=next(x for x in s['layers'] if x['id']=='measured-menu-clip-v13');menu=clip['children'][0];body=next(c for c in menu['children'] if c['id']=='menu13-p03-202');records={r['frame']:r for r in json.loads((p/'menu-world-v13-measurements.json').read_text())};meta=[]
for i,row in enumerate(body['children']):
 f=651 if i<3 else 666 if i==3 else 729;r=records[f];q=r['matches'][i]
 if i==5:q={'x':r['matches'][4]['x'],'y':r['matches'][4]['y']+236*r.get('body_scale',r['scale'])}
 scale=r.get('body_scale',r['scale']);im=Image.open(p/'lunch-native'/f'{f-609:03}.png').convert('RGB');old=row['children'];copytext='; '.join(c.get('text','') for c in old[:3]);paths=[]
 for name,dy,height,gray,fill in [('title-price',-4,92,0,'#000000'),('description',90,108,180,'#b4b4b4')]:
  box=(round(q['x']-489*scale),round(q['y']+dy*scale),round(q['x']-14*scale),round(q['y']+(dy+height)*scale));crop=np.array(im.crop(box),dtype=float);alpha=np.clip((253-crop.mean(2))/(253-gray),0,1);d,stats=trace_alpha(alpha);paths.append({'id':f'menu13-copy-{i}-{name}','type':'path','d':d,'x':553+(box[0]-q['x'])/scale,'y':348+236*i+(box[1]-q['y'])/scale,'scaleX':1/scale,'scaleY':1/scale,'fill':fill,'semanticText':copytext,'provenance':{'source_frame':f,'source_box':list(box),'kind':'bounded original glyph outlines, editable vector path'}});meta.append({'row':i,'name':name,'source_frame':f,'source_box':list(box),'stats':stats})
 row['children']=paths+old[3:]
s['source']['notes']+=' Static menu body copy is original bounded glyph outlines, retaining semantic text and independent perrow native transforms; photos remain separate declared artwork.'
(p/'menu-v13.scene.json').write_text(json.dumps(s,indent=2));(p/'menu-copy-v13-provenance.json').write_text(json.dumps(meta,indent=2));print('outlined',len(meta))
