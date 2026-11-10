"""Native bounded original glyph poses and two independently bounded icon components."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).parent;B=P/'early-v13-measure';D=P/'assets/early-intro-v13';D.mkdir(exist_ok=True);sys.path.insert(0,str(P.parent/'02-danieltian'));from trace_glyphs import trace_alpha
boxes=[('Introducing',(530,400,1048,533)),('API',(1048,400,1188,533)),('for',(1188,400,1340,533)),('Mini',(515,535,699,670)),('Apps',(699,535,933,670)),('in',(933,535,1014,670)),('iMessage / Agent transition',(1106,535,1540,670)),('Agent transition',(1014,535,1106,670))]
icons=[('App Store',(365,535,515,670)),('Messages',(1014,535,1106,670))];layers=[];records=[]
for f in range(59):
 im=Image.open(B/'intro-full'/f'{f+1:03d}.png').convert('RGB');a=np.asarray(im).astype(float)
 for i,(semantic,box) in enumerate(boxes):
  x1,y1,x2,y2=box;rgb=a[y1:y2,x1:x2];alpha=np.clip((253-rgb.mean(2))/253,0,1);alpha[np.ptp(rgb,axis=2)>15]=0;ink=alpha[alpha>.07]
  if len(ink)<5:continue
  op=float(np.percentile(ink,95));d,stats=trace_alpha(np.clip(alpha/max(.001,op),0,1),x1,y1)
  if not d:continue
  layers.append({'id':f'early-intro-glyph-v13-{f}-{i}','type':'path','d':d,'fill':'#000000','opacity':op,'start':f/30,'end':(f+1)/30,'semanticText':semantic,'editableAs':'native original glyph outlines, measured per-frame pose'})
  records.append({'id':layers[-1]['id'],'source_frame':f,'bounds':list(box),'semantic_text':semantic,'opacity':op,**stats})
 for i,(semantic,box) in enumerate(icons):
  x1,y1,x2,y2=box;roi=a[y1:y2,x1:x2];mask=np.ptp(roi,axis=2)>18;ys,xs=np.where(mask)
  if len(xs)<5:continue
  bounds=(max(x1,x1+int(xs.min())-2),max(y1,y1+int(ys.min())-2),min(x2,x1+int(xs.max())+3),min(y2,y1+int(ys.max())+3));asset=D/f'icon-{i}-frame-{f:03d}.png';im.crop(bounds).save(asset)
  layers.append({'id':f'early-intro-icon-v13-{f}-{i}','type':'image','src':str(asset.relative_to(P)),'x':bounds[0],'y':bounds[1],'width':bounds[2]-bounds[0],'height':bounds[3]-bounds[1],'start':f/30,'end':(f+1)/30,'semanticText':semantic,'editableAs':'bounded original icon component; independent pose/lifetime'})
  records.append({'id':layers[-1]['id'],'source_frame':f,'bounds':list(bounds),'semantic_text':semantic,'asset':str(asset.relative_to(P)),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'limitation':'Icon internal shading/lettering is bitmap; no neighboring copy or device pixels included.'})
(B/'intro-native-layers.json').write_text(json.dumps(layers)+'\n');(B/'intro-outline-provenance.json').write_text(json.dumps({'source_sha256':hashlib.sha256((P/'source.mp4').read_bytes()).hexdigest(),'records':records,'diagnosis':'Sourceframe0 is a complete title poster,1–3 are blank, words/icons reveal separately4–18, and50–58 exit into a header morph. Original broad text-layer lifetimes showed future copy prematurely. Every text component remains native outlines; only the two colored icon components are bounded image artwork.'},indent=2)+'\n');print('nativeintro layers',len(layers))
