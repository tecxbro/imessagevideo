"""One native frame validates UI-photo/avatars plus physical aperture/bottom anchors."""
from pathlib import Path
import copy,json,math
import numpy as np
from PIL import Image
from apply_blue_arrival_v14 import sample
from apply_menu_thumbnail_clips_v15 import affine_group
P=Path(__file__).resolve().parent
scene=json.loads((P/'final-v15.scene.json').read_text())
frame=738;time=frame/30
source=np.array(Image.open(P/'lunch-native/129.png').convert('RGB'))
candidate=np.array(Image.open(P.parent.parent/'outputs/03-photon-mini/frames-gsap/000738.png').convert('RGB'))
physical=next(n for n in scene['layers'] if n['id']=='measured-lunch-device-v13')
old={k:sample(physical['keyframes'][k],time) for k in ['x','y','scaleX','scaleY']}
center=old['x']+400*old['scaleX']

def runs(mask):
    points=np.where(mask)[0];out=[]
    for y in points:
        if out and y==out[-1][1]+1:out[-1][1]=int(y)
        else:out.append([int(y),int(y)])
    return out

def vertical_anchors(rgb):
    x0=int(center+20);x1=int(center+55)
    gray=rgb[:130,x0:x1].max(2)
    intervals=runs(np.mean(gray<30,axis=1)>.65)
    choices=[v for v in intervals if v[1]-v[0]+1>20]
    if len(choices)!=1:raise ValueError('Ambiguous physical aperture'+str(choices))
    pill=(choices[0][0]+choices[0][1]+1)/2
    gray=rgb[850:1080,int(center-40):int(center+40)].mean(2)
    intervals=runs(np.mean(gray<80,axis=1)>.8)
    if not intervals:raise ValueError('No observed physical bottom rim')
    bottom=intervals[-1][1]+851
    return dict(pill_center=pill,bottom=bottom,pill_runs=choices,bottom_runs=intervals)

native=vertical_anchors(candidate);actual=vertical_anchors(source)
canonical_pill=(native['pill_center']-old['y'])/old['scaleY']
canonical_bottom=(native['bottom']-old['y'])/old['scaleY']
sy=(actual['bottom']-actual['pill_center'])/(canonical_bottom-canonical_pill)
y=actual['pill_center']-sy*canonical_pill
sx=.623640625;x=709.54375
physical_matrix=np.array([[sx,0,x],[0,sy,y],[0,0,1]],float)
ui_data=json.loads((P/'return-camera-738-v16-attribution.json').read_text())
ui_matrix=np.array(ui_data['photo']['inferred_ui_matrix'])

def gate(node):
    old_opacity=node.get('opacity',1)
    if node.get('keyframes',{}).get('opacity'):raise ValueError('Unexpected animated root opacity')
    node.setdefault('keyframes',{})['opacity']=[dict(t=0,value=old_opacity,ease='hold'),dict(t=time,value=0,ease='hold'),dict(t=(frame+1)/30,value=old_opacity,ease='hold')]

def reid(node,prefix):
    node['id']=prefix+node['id']
    for child in node.get('children',[]):reid(child,prefix)

for identifier,M in [('measured-lunch-device-v13',physical_matrix),('measured-lunch-ui-v13',ui_matrix),('measured-lunch-bezel-overlay-v13',physical_matrix)]:
    original=next(n for n in scene['layers'] if n['id']==identifier)
    children=copy.deepcopy(original['children'])
    for child in children:reid(child,'return738-')
    if identifier=='measured-lunch-ui-v13':
        scrim=next(n for n in children if n['id'].endswith('celebration-phone-ui-scrim'))
        scrim['keyframes']['opacity']=[dict(t=0,value=1-249/253,ease='hold')]
    group=affine_group(M[:2],'return738-'+identifier,children)
    group.update(start=time,end=(frame+1)/30)
    gate(original)
    scene['layers'].insert(scene['layers'].index(original)+1,group)
scene['return738_measurement']=dict(native_anchors=native,source_anchors=actual,canonical_anchors=dict(pill=canonical_pill,bottom=canonical_bottom),physical_matrix=physical_matrix.tolist(),ui_matrix=ui_matrix.tolist(),notice='Independent UI photo+two avatar anchors validate the smaller/faster return. Physical Y/anisotropicheight use actual aperture and bottom rim, not the rejected photometric rimY. World food/Order roots and621–729/V5stencil are untouched.')
(P/'return-camera-738-v16-prototype.scene.json').write_text(json.dumps(scene,indent=2))
(P/'return-camera-738-v16-physical-anchors.json').write_text(json.dumps(scene['return738_measurement'],indent=2))
print(json.dumps(scene['return738_measurement'],indent=2))
