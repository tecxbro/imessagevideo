"""Close only final Mail copy335–344; all original camera tracks are preserved."""
from pathlib import Path
import json,copy,re
import numpy as np
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent

def apply_return_copy(scene,spec=None):
 scene=copy.deepcopy(scene)
 spec=spec or json.loads((P/'mail-return-copy-v17-elements.json').read_text())
 phone=next(n for n in scene['layers']if n['id']=='p03-86')
 def find(nodes,identifier):
  for n in nodes:
   if n['id']==identifier:
    return n
   result=find(n.get('children',[]),identifier)
   if result:
    return result
  return None
 for identifier in spec['old_ids']:
  n=find(phone['children'],identifier)
  old=n.get('keyframes',{}).get('opacity',[dict(t=0,value=n.get('opacity',1),ease='hold')])
  n.setdefault('keyframes',{})['opacity']=[key for key in old if key['t']<342/30]+[dict(t=342/30,value=0,ease='hold'),dict(t=345/30,value=sample(old,345/30),ease='hold')]+[key for key in old if key['t']>345/30]
 pane=find(phone['children'],'p03-77')
 new_copy=copy.deepcopy(spec['body'])
 new_copy['start']=342/30
 pane['children'].append(new_copy)
 original_leaf=find(phone['children'],'p03-71-original-outline-v13')
 clean_leaf=copy.deepcopy(original_leaf)
 parts=[]
 removed_carets=0
 removed_edge_fragments=0
 for part in re.findall(r'M[^M]*',original_leaf['d']):
  points=np.array([float(v)for v in re.findall(r'-?\d+(?:\.\d+)?',part)]).reshape(-1,2)
  x,y=points.min(0)
  x2,y2=points.max(0)
  if x>1165 and x2<1171 and y>693 and y2<721 and y2-y>20:
   removed_carets+=1
   continue
  if y>770:
   removed_edge_fragments+=1
   continue
  parts.append(part)
 if removed_carets!=1:
  raise ValueError('Expected exactly one original baked caret')
 clean_leaf.update(id='mail-return-clean-original-body-v17',d=' '.join(parts),start=335/30,end=342/30,provenance=dict(kind='Original native glyphs with the unrelated bakedcaret/edgefragments removed',source_frame=300,removed_carets=removed_carets,removed_edge_fragments=removed_edge_fragments,notice='Existing335–341copy layout alreadyfits; blanket latecopy plane regressed, so onlysemantic caret/period cleanup is accepted here.'))
 old_opacity=original_leaf.get('keyframes',{}).get('opacity',[dict(t=0,value=original_leaf.get('opacity',1),ease='hold')])
 original_leaf.setdefault('keyframes',{})['opacity']=[key for key in old_opacity if key['t']<335/30]+[dict(t=335/30,value=0,ease='hold'),dict(t=342/30,value=sample(old_opacity,342/30),ease='hold')]+[key for key in old_opacity if key['t']>342/30]
 body=find(phone['children'],'p03-71')
 body['children'].append(clean_leaf)
 body['children'].append(copy.deepcopy(spec['period_group']))
 scene['mail_return_copy_v17']=dict(scope=[335,344],full_copy_scope=[342,344],semantic_cleanup_scope=[335,341],notice='Native observed semanticcopy plus fieldseparators. Sourcefinalperiod andabsenceofcaret are restored after specialcloseup. Physical/UI/papercamera,310–334fade and345+boundedpaneexit are unchanged.')
 return scene
