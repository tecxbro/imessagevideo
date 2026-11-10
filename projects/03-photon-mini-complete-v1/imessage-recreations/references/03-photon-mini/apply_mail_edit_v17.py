"""Replace only observed early Mail editing states and verified physical occlusion."""
from pathlib import Path
import copy,json
from apply_early_bezel_overlay_v17 import apply_bezel
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent

def apply_mail_edit(scene,spec=None):
 scene=copy.deepcopy(scene)
 spec=spec or json.loads((P/'mail-edit-v17-elements.json').read_text())
 phone=next(node for node in scene['layers'] if node['id']=='p03-86')
 def find(nodes,identifier):
  for node in nodes:
   if node['id']==identifier:
    return node
   result=find(node.get('children',[]),identifier)
   if result:
    return result
  return None
 for identifier in ['p03-70','p03-71','p03-75','p03-76']:
  node=find(phone['children'],identifier)
  if node.get('keyframes',{}).get('opacity'):
   raise ValueError('Unexpected original edit opacity track:'+identifier)
  original=node.get('opacity',1)
  node.setdefault('keyframes',{})['opacity']=[dict(t=0,value=original,ease='hold'),dict(t=230/30,value=0,ease='hold'),dict(t=310/30,value=original,ease='hold')]
 pane=find(phone['children'],'p03-77')
 pane['children'].append(copy.deepcopy(spec['body']))
 back=find(pane['children'],'p03-52')
 observations=json.loads((P/'mail-backsheet-v17-measurements.json').read_text())['frames']
 end_keys=copy.deepcopy(back.get('keyframes',{}).get('end',[dict(t=0,value=back.get('end',42))]))
 back.setdefault('keyframes',{})['end']=[key for key in end_keys if key['t']<230/30]+[dict(t=230/30,value=230/30,ease='hold'),dict(t=310/30,value=sample(end_keys,310/30),ease='hold')]+[key for key in end_keys if key['t']>310/30]
 native_back={key:copy.deepcopy(value) for key,value in back.items()if key not in ['id','keyframes','start','end']}
 native_back.update(id='mail-gray-backsheet-measured-v17',start=230/30,end=310/30,keyframes=dict(y=[dict(t=row['frame']/30,value=row['corrected_logical_y'],ease='hold')for row in observations],fill=[dict(t=row['frame']/30,value=row['corrected_fill'],ease='hold')for row in observations]),semanticText='Gray view behind Mail editor',provenance=dict(kind='Native measured backsheet material',notice='Actual exposed center top is~20px below the prior surface, while foregroundpaper top alreadymatches. Only native backsheetY/fill230–309 are corrected; no physical/UI/papercamera change. Cropped nativecalibration uses oneuncensored275pose rather than inventing an offstage edge.'))
 pane['children'].insert(pane['children'].index(back)+1,native_back)
 scene=apply_bezel(scene,start_frame=230,end_frame=344,identifier='mail-only-top-bezel-v17')
 scene['mail_edit_v17']=dict(copy_scope=[230,309],bezel_scope=[[230,309],[335,344]],notice='The generic genuine bezel already has opacity0 through310–334, preserving special measuredhardware/fade. No camera value or world actor changes. Source-observed native copy selection242–267,deletion268–269,typed270–308 andonecaret replace the skippedA→Bstate andbakedduplicatecaret. Frame309 hasnoobservedcaret. No new runtime raster asset.')
 return scene

if __name__=='__main__':
 base=json.loads((P/'final-v16.scene.json').read_text())
 (P/'mail-edit-v17-prototype.scene.json').write_text(json.dumps(apply_mail_edit(base),indent=2))
 print('Built bounded native Mail edit/occlusion prototype')
