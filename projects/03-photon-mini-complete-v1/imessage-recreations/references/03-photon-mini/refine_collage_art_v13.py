"""Preserve measured partial-card sampling and native semantic footer outlines."""
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
p=Path(__file__).parent;sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'late-v13.scene.json').read_text());old=next(x for x in s['layers'] if x['id']=='p03-650');new=next(x for x in s['layers'] if x['id']=='measured-collage-v13');source=Image.open(p/'measured/31.png').convert('RGB');meta=[]
for i,box,H in [(0,(0,0,308,135),206),(1,(382,0,770,104),208),(2,(844,0,1236,76),206),(3,(1308,0,1688,60),209),(4,(1756,0,1920,29),206)]:
 c=old['children'][i];sx=next(q['value'] for q in c['keyframes']['scaleX'] if q['t']==31.35);art=new['children'][i]['children'][1];image=[q for q in art['children'] if q['type']=='image'][-1];canvas=Image.open(p/image['src']).convert('RGBA').resize((390,H),Image.Resampling.BILINEAR);crop=source.crop(box).convert('RGBA');crop=crop.resize((round(crop.width/sx),crop.height),Image.Resampling.LANCZOS);left=round((box[0]-c['x'])/sx);top=round(box[1]-c['y']);canvas.paste(crop,(left,top));file=f'assets/card-art/{i:02d}-measured-v13.png';canvas.save(p/file);image.update(src=file,height=H);art['clip']['height']=H;meta.append({'index':i,'file':file,'source_frame':930,'source_box':list(box),'native_paste':[left,top],'diagnosis':'The old bottom-mode crop stretched a partial source area across the entire card. Preserve its actual native offset and pixel scale; unknown upper art retains declared prior artwork.'})
for i,(o,c) in enumerate(zip(old['children'],new['children'])):
 sx=next(q['value'] for q in o['keyframes']['scaleX'] if q['t']==31.35);x=o['x'];y=o['y'];children=c['children'];semantics=[children[2].get('text',''),children[3].get('text','')]
 # Clipped left/bottom copy retains live text, since a partial source span cannot
 # establish missing letter geometry when it later enters the stage.
 if x<0 or x+390*sx>1920 or y+274>1080:continue
 paths=[]
 for j,(dy,h,gray,fill) in enumerate([(210,36,0,'#000000'),(247,26,170,'#aaaaaa')]):
  box=(round(x+12*sx),round(y+dy),round(x+382*sx),round(y+dy+h));im=np.array(source.crop(box),dtype=float);alpha=np.clip((231-im.mean(2))/(231-gray),0,1);d,stats=trace_alpha(alpha);paths.append({'id':f'collage13-footer-copy-{i}-{j}','type':'path','d':d,'x':(box[0]-x)/sx,'y':box[1]-y,'scaleX':1/sx,'fill':fill,'semanticText':semantics[j],'provenance':{'source_frame':930,'source_box':list(box),'native_outlines':True}});meta.append({'index':i,'kind':'footer-copy','semanticText':semantics[j],'source_box':list(box),'stats':stats})
 c['children']=children[:2]+paths+children[4:]
s['source']['notes']+=' V13 collage artwork refinement: partial original artworks retain their measured native offset instead of stretching to fill cards; full visible footer copy is bounded native semantic glyph outlines.'
(p/'late-v13.scene.json').write_text(json.dumps(s,indent=2));(p/'collage-art-v13-provenance.json').write_text(json.dumps(meta,indent=2));print('refined',len(meta))
