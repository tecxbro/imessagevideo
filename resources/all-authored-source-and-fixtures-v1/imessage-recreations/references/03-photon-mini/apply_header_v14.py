from pathlib import Path
from PIL import Image
import numpy as np,json,copy,importlib.util
from apply_blue_arrival_v14 import sample
P=Path(__file__).parent
sp=importlib.util.spec_from_file_location('outline',P.parent/'02-danieltian/trace_glyphs.py');tr=importlib.util.module_from_spec(sp);sp.loader.exec_module(tr)

def build():
 im=np.array(Image.open(P/'header-v14-measure/reference-551.png').convert('RGB'));refs={}
 for role,box,fg in [('word',[857,57,1051,87],0),('arrow',[1056,57,1079,89],153),('date',[886,130,1047,155],148)]:
  x,y,x2,y2=box;crop=im[y:y2,x-780:x2-780];a=np.clip((253-crop.mean(2))/(253-fg),0,1);d,meta=tr.trace_alpha(a,x0=x-(860 if role!='date' else 889),y0=y-(60 if role!='date' else 133),threshold=.5);refs[role]={'d':d,'metadata':meta,'source_frame':551,'source_box':box,'fg':fg}
 (P/'lunch-header-v14-outlines.json').write_text(json.dumps(refs,indent=2))

def apply_header(scene):
 s=copy.deepcopy(scene);root=next(x for x in s['layers'] if x['id']=='p03-204');data=json.loads((P/'lunch-header-v14-outlines.json').read_text());records=json.loads((P/'lunch-header-v14-measurements.json').read_text());new=[]
 for role,refw,refh in [('word',188,24),('date',155,19)]:
  keys={k:[] for k in ['x','y','scaleX','scaleY']};previous=None
  for rec in records:
   f=rec['frame'];t=f/30;q=rec[role];cam={k:sample(root['keyframes'][k],t) for k in ['x','y','scaleX','scaleY']}
   if q and not q['top_censored']:
    x,y,x2,y2=q['bbox'];world_scale=(x2-x)/refw;v={'x':(x-cam['x'])/cam['scaleX'],'y':(y-cam['y'])/cam['scaleY'],'scaleX':world_scale/cam['scaleX'],'scaleY':world_scale/cam['scaleY']};previous=v
   elif previous:v=previous
   else:continue
   for k in keys:keys[k].append({'t':t,'value':v[k],'ease':'linear'})
  if role=='word':
   children=[{'id':'header14-native-pill','type':'rect','x':-27,'y':-16,'width':254,'height':60,'radius':30,'fill':'#fdfdfd','shadow':{'x':0,'y':2,'blur':3,'color':'#00000025'}},{'id':'header14-word','type':'path','d':data['word']['d'],'fill':'#000000','semanticText':'Team Lunch','provenance':{'kind':'bounded original glyph outlines','source_frame':551,'source_box':data['word']['source_box'],'notice':'Editable semantic glyph outline rather than live font text.'}},{'id':'header14-chevron','type':'path','d':data['arrow']['d'],'fill':'#999999','semanticText':'Open conversation details'}]
  else:children=[{'id':'header14-date','type':'path','d':data['date']['d'],'fill':'#949494','semanticText':'Today 11:20 AM','provenance':{'kind':'bounded original glyph outlines','source_frame':551,'source_box':data['date']['source_box'],'notice':'Editable semantic glyph outline rather than live font text.'}}]
  new.append({'id':'measured-lunch-header-'+role+'-v14','type':'group','start':495/30,'end':618/30,'keyframes':keys,'children':children})
 index=next(i for i,x in enumerate(root['children']) if x['id']=='p03-103');root['children']=[x for x in root['children'] if x['id'] not in ['p03-103','p03-104','p03-105','p03-106']];root['children'][index:index]=new;s['lunch_header_v14']={'scope':[495,617],'notice':'Source held word/date glyphs are editable native outlines with semantic strings, independently measured native world tracks. Source551 wordbbox188x24 differs from substituteDisplay171x23; measured datebbox has7px right/5px lower anchor. Partial topcensored observations retain previous local pose and stageclip naturally. Tiny pixel AA differences are declared.'};return s
if __name__=='__main__':
 build();s=json.loads((P/'preview-arrival-v14.scene.json').read_text());s=apply_header(s);(P/'header-v14.scene.json').write_text(json.dumps(s,indent=2))
