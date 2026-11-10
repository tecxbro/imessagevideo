"""Trace bounded actual email-field glyphs into native local pane coordinates."""
from pathlib import Path
import json,sys,copy
import numpy as np
from PIL import Image
P=Path(__file__).parent;B=P/'early-v13-measure';sys.path.insert(0,str(P.parents[1]/'engines'));from render_pillow import state
sys.path.insert(0,str(P.parent/'02-danieltian'));from trace_glyphs import trace_alpha
s=json.loads((P/'early-v13.scene.json').read_text());phone=next(l for l in s['layers'] if l['id']=='p03-86');pane=next(l for l in phone['children'] if l['id']=='p03-77');original_scene=json.loads((P/'final-v12.scene.json').read_text());original_phone=next(l for l in original_scene['layers'] if l['id']=='p03-86');original_pane=next(l for l in original_phone['children'] if l['id']=='p03-77');by={l['id']:l for l in original_pane['children']};replacements={};records=[]
rois={'p03-60':(595,310,1180,410),'p03-61':(600,448,655,500),'p03-62':(655,448,760,500),'p03-64':(600,530,1320,590),'p03-66':(600,620,720,680),'p03-67':(720,620,1180,680),'p03-69':(600,730,840,795),'p03-70':(600,800,1355,930),'p03-72':(600,930,1300,995),'p03-73':(600,995,800,1065)}
for identifier in ['p03-60','p03-61','p03-62','p03-64','p03-66','p03-67','p03-69','p03-70','p03-71','p03-72','p03-73','p03-74']:
 original=by[identifier];f=300 if identifier in ['p03-71','p03-74'] else 220;ps=state(phone,f/30);es=state(pane,f/30);scale=ps['scaleX'];ox=ps['x']+scale*es['x'];oy=ps['y']+scale*es['y'];im=Image.open(B/'source-full-0300.png' if f==300 else B/'validation-source/012.png').convert('RGB')
 if identifier in rois:box=rois[identifier]
 else:
  x=ox+original['x']*scale;y=oy+original['y']*scale;box=(round(x-10),round(y-18),round(x+(680 if identifier=='p03-71' else 140)*scale),min(1080,round(y+(125 if identifier=='p03-71' else 45)*scale)))
 a=np.asarray(im.crop(box)).astype(float);lum=a.mean(2);ink=lum<245
 if not ink.any():raise ValueError('No ink in '+identifier)
 core=lum<=np.percentile(lum[ink],8);color=np.median(a[core],axis=0);alpha=np.clip((252-lum)/max(1,252-color.mean()),0,1);d,stats=trace_alpha(alpha,box[0],box[1]);fill='#'+''.join(f'{int(np.clip(round(c),0,255)):02x}'for c in color);path={'id':identifier+'-original-outline-v13','type':'path','d':d,'fill':fill,'x':-ox/scale,'y':-oy/scale,'scaleX':1/scale,'scaleY':1/scale,'semanticText':original['text'],'editableAs':'native original glyph outlines'}
 replacement={k:v for k,v in original.items() if k in ['id','start','end','keyframes']};replacement.update(type='group',children=[path],semanticText=original['text'],end=min(original.get('end',345/30),345/30));replacements[identifier]=replacement;records.append({'id':identifier,'source_frame':f,'bounds':list(box),'semantic_text':original['text'],'inverse_pane_projection':{'x':-ox/scale,'y':-oy/scale,'scale':1/scale},'fill':fill,**stats})
# Original white send-arrow outline; its circle and press scale stay native.
im=Image.open(B/'validation-source/012.png').convert('RGB');box=(1227,205,1314,290);a=np.asarray(im.crop(box)).astype(float);yy,xx=np.mgrid[:a.shape[0],:a.shape[1]];alpha=np.clip(a[:,:,0]/255,0,1);alpha[((xx+box[0]-1270)**2+(yy+box[1]-247)**2)>(34**2)]=0;d,stats=trace_alpha(alpha,box[0],box[1]);ps=state(phone,220/30);es=state(pane,220/30);scale=ps['scaleX'];ox=ps['x']+scale*(es['x']+658);oy=ps['y']+scale*(es['y']+232);replacements['p03-58']={'id':'p03-58','type':'path','d':d,'fill':'#ffffff','x':-ox/scale,'y':-oy/scale,'scaleX':1/scale,'scaleY':1/scale,'semanticText':'Send arrow','editableAs':'native original glyph outline'};records.append({'id':'p03-58','source_frame':220,'bounds':list(box),'semantic_text':'Send arrow',**stats})
(B/'pane-outline-replacements.json').write_text(json.dumps(replacements)+'\n');(B/'pane-outline-provenance.json').write_text(json.dumps({'records':records,'scope':'Twelve independently bounded static email text fields. No full pane/frame traced. Native controls/backgrounds/rules and all motion remain separate.'},indent=2)+'\n');print('nativepane textfields',len(replacements))
