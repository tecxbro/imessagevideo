"""Replace held-copy substitutes with bounded original native glyph outlines.
Each word remains an independent editable path with semantic metadata.
"""
from pathlib import Path
import json,hashlib,copy,sys
import numpy as np
from PIL import Image
p=Path(__file__).parent
sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'final-v10.scene.json').read_text());records=[]
def word_layer(image,box,origin,semantic,identifier,start,end):
 crop=np.array(image.crop(box).convert('RGB'),dtype='float64');alpha=np.clip((253-crop.mean(2))/253,0,1)
 d,stats=trace_alpha(alpha,box[0]-origin[0],box[1]-origin[1])
 records.append({'id':identifier,'semantic_text':semantic,'box':list(box),'origin':list(origin),'source_time':33.5 if semantic in ['Now','your','agent','can','send'] else 37.5,**stats})
 return {'id':identifier,'type':'path','d':d,'fill':'#000000','start':start,'end':end,'semanticText':semantic,'editableAs':'native glyph outlines'}
# The existing motion was measured against this exact rest pose. Replacing
# font metrics with original outlines recovers the intended positions directly.
prefix=next(x for x in s['layers'] if x['id']=='measured-prefix-reveal-v6');im=Image.open(p/'measured/33.5.png')
words=[('Now',(274,500,429,582),32.6),('your',(441,500,598,582),32.6666666667),('agent',(612,500,813,582),32.7333333333),('can',(829,500,956,582),33.0666666667),('send',(973,500,1140,582),33.1666666667)]
prefix['children']=[word_layer(im,box,(270,493),word,'prefix-outline-'+word,start,36.5) for word,box,start in words]
for k in prefix['keyframes']['y']:
 if k['t']<=32.8:k['value']=488.5
 if k['t']==33:k['value']=493.5
prefix['keyframes']['y'].append({'t':33.1,'value':493,'ease':'linear'})
prefix['keyframes']['scaleX']=[{'t':32.6,'value':1.0847},{'t':32.8,'value':1.0847,'ease':'linear'},{'t':33,'value':1.0094,'ease':'linear'},{'t':33.1,'value':.9985,'ease':'linear'},{'t':33.2,'value':857/859,'ease':'linear'},{'t':33.3,'value':858/859,'ease':'linear'},{'t':33.4,'value':1,'ease':'linear'}]
prefix['keyframes']['scaleY']=[{'t':32.6,'value':1.158},{'t':32.8,'value':1.158,'ease':'linear'},{'t':33,'value':1.0145,'ease':'linear'},{'t':33.1,'value':1,'ease':'linear'}]
cta=next(x for x in s['layers'] if x['id']=='p03-699');url=next(x for x in cta['children'] if x['id']=='p03-698');im=Image.open(p/'measured/37.5.png')
words=[('Available',(433,500,746,590),36.5),('today',(757,500,962,590),36.6666666667),('at',(971,500,1046,590),36.9666666667)]
cta['children']=[word_layer(im,box,(437,495),word,'cta-outline-'+word,start,39.6) for word,box,start in words]
# Keep the bounded colored URL as one declared independently transformed asset.
box=(1065,500,1493,590);asset='assets/closing-url-original.png';im.crop(box).save(p/asset)
url_image={'id':'closing-url-original-v11','type':'image','src':asset,'x':box[0]-437,'y':box[1]-495,'width':box[2]-box[0],'height':box[3]-box[1],'start':url['start'],'end':url['end'],'semanticText':'tryphoton.ai','keyframes':copy.deepcopy(url['keyframes'])}
base=url_image['x']
for k in url_image['keyframes']['x']:k['value']=base+(k['value']-633)
cta['children'].append(url_image)
for k in cta['keyframes']['x']:
 if k['t']==37.5:k['value']=437
# Small observed CTA spring in the source rest width/height.
cta['originY']=17
cta['keyframes']['scaleX']=[{'t':36.5,'value':.99},{'t':37,'value':599/605,'ease':'linear'},{'t':37.5,'value':1,'ease':'linear'}]
cta['keyframes']['scaleY']=[{'t':36.5,'value':67/68},{'t':37,'value':67/68,'ease':'linear'},{'t':37.5,'value':1,'ease':'linear'}]
s['source']['notes']+=' V11: bounded closing black-copy glyphs traced as native editable perword paths with semantic metadata from clean33.5/37.5 restposes. Original wordlifetimes/motion retained. ColoredURL is a bounded separate source asset with independent transform/opacity. No fullframe/sourcevideo substitution.'
f=p/'final-v11.scene.json';f.write_text(json.dumps(s,indent=2));sha=hashlib.sha256(f.read_bytes()).hexdigest()
(p/'final-v11-changes.json').write_text(json.dumps({'sha256':sha,'baseline':'final-v10.scene.json','delta_frames_inclusive':[[978,1187]],'glyph_outlines':records,'url_asset':{'file':asset,'semantic_text':'tryphoton.ai','source_time':37.5,'box':list(box),'limitation':'ColoredURLcopy is bitmap; independently editable transform/opacity remain.'},'diagnosis':'Regular/Medium font fitting traded width and weight. Original bounded glyph outlines remove that substitution while preserving native editability of path geometry, word timing and camera.'},indent=2));print(sha)
