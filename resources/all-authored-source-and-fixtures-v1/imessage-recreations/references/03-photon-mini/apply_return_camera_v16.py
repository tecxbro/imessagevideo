"""Independent source-measured physical/UI camera for the ten-frame return settle."""
from pathlib import Path
import copy,json
from apply_menu_thumbnail_clips_v15 import affine_group
P=Path(__file__).resolve().parent

def apply_return(scene,spec=None):
 scene=copy.deepcopy(scene);spec=spec or json.loads((P/'return-camera-v16-dense-measurements.json').read_text())
 all_rows=[r for r in spec['frames'] if 735<=r['frame']<=799]
 if len(all_rows)!=65:raise ValueError('Expected65 observed native UI return poses')
 def reid(n):
  n['id']='return-settle-v16-'+n['id']
  for c in n.get('children',[]):reid(c)
 for identifier,field in [('measured-lunch-device-v13','physical_matrix'),('measured-lunch-ui-v13','ui_matrix'),('measured-lunch-bezel-overlay-v13','physical_matrix')]:
  rows=all_rows if field=='ui_matrix' else [r for r in all_rows if r['frame']<=744]
  end=800 if field=='ui_matrix' else 745
  original=next(n for n in scene['layers'] if n['id']==identifier)
  if original.get('keyframes',{}).get('opacity'):raise ValueError('Unexpected root opacity animation')
  children=copy.deepcopy(original['children'])
  for c in children:reid(c)
  if field=='ui_matrix':
   scrim=next(n for n in children if n['id'].endswith('celebration-phone-ui-scrim'))
   scrim['keyframes']['opacity']=[dict(t=r['frame']/30,value=r['scrim_alpha'],ease='hold') for r in rows]
  group=affine_group(rows[0][field][:2],'return-settle-v16-'+identifier,children,original.get('clip'))
  group.update(start=735/30,end=end/30)
  group['keyframes']={k:[] for k in ['x','y','scaleX','scaleY','rotation']}
  group['children'][0]['keyframes']={'rotation':[]}
  for r in rows:
   pose=affine_group(r[field][:2],'unused',[])
   for k in group['keyframes']:group['keyframes'][k].append(dict(t=r['frame']/30,value=pose[k],ease='hold'))
   group['children'][0]['keyframes']['rotation'].append(dict(t=r['frame']/30,value=pose['children'][0]['rotation'],ease='hold'))
  group['provenance']=dict(kind='Independent native UI/physical return camera',scope=[735,end-1],notice='Photo features and two separate avatar anchors validate UI plane; hardware width plus physical aperture/bottom validate body. Top-censored aperture centres use observed bottom and calibrated height. Original world food and Order actors are untouched.')
  opacity=original.get('opacity',1)
  original.setdefault('keyframes',{})['opacity']=[dict(t=0,value=opacity,ease='hold'),dict(t=735/30,value=0,ease='hold'),dict(t=end/30,value=opacity,ease='hold')]
  scene['layers'].insert(scene['layers'].index(original)+1,group)
 scene['return_settle_v16']=dict(ui_scope=[735,799],physical_scope=[735,744],measurements=all_rows,notice='Only original device/UI/bezel groups are replaced in this bounded interval.621–729 menu and V5stencil, and independent food/Order actors remain unchanged.')
 return scene

if __name__=='__main__':
 scene=json.loads((P/'final-v15.scene.json').read_text());scene=apply_return(scene)
 (P/'return-camera-v16-prototype.scene.json').write_text(json.dumps(scene,indent=2))
 print('Built65UI/10physical return-camera prototype')
