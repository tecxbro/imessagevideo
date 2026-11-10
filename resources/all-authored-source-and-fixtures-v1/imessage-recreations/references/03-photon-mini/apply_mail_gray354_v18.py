"""Expose the native gray Messages material at exactly one observed return frame."""
from pathlib import Path
import copy,json,numpy as np
from apply_menu_thumbnail_clips_v15 import affine_group
from measure_lunch_refinement_v16 import matrix
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent

def apply_gray354(scene,spec=None):
 scene=copy.deepcopy(scene)
 spec=spec or json.loads((P/'mail-gray354-v18-elements.json').read_text())
 phone=next(n for n in scene['layers']if n['id']=='p03-86')
 def find(nodes,identifier):
  for n in nodes:
   if n['id']==identifier:return n
   result=find(n.get('children',[]),identifier)
   if result:return result
  return None
 backing=next(n for n in phone['children']if n['id']=='early-email-black-backplate-v13')
 shape=dict(id='mail-return-gray-page-material-v18',type='path',d=spec['path'],fill=spec['fill'],semanticText='Dimmed Messages page behind closing Mail editor',provenance=dict(kind='Native measured gray material geometry',source_frame=354,source_gray_component=spec['source_gray_component'],notice=spec['notice']))
 inv=np.linalg.inv(matrix(phone,354))
 group=affine_group(inv[:2],'mail-return-gray-page-local-v18',[shape])
 group.update(start=354/30,end=355/30)
 phone['children'].insert(phone['children'].index(backing)+1,group)
 backsheet=find(phone['children'],'p03-52')
 old=copy.deepcopy(backsheet.get('keyframes',{}).get('end',[dict(t=0,value=backsheet.get('end',42))]))
 backsheet.setdefault('keyframes',{})['end']=[k for k in old if k['t']<354/30]+[dict(t=354/30,value=354/30,ease='hold'),dict(t=355/30,value=sample(old,355/30),ease='hold')]+[k for k in old if k['t']>355/30]
 scene['mail_gray_return_v18']=dict(scope=[354,354],notice='One missingnative gray Messages material at first truefullbackplane frame. Graypill is suppressedonlyhere. Originalphysical/UI/papercamera,Mailpane/hardwareownership andallworldactorsremainunchanged. No new imageasset.')
 return scene
