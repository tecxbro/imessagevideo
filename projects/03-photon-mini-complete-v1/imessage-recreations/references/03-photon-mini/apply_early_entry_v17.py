"""Independent original message poses plus native receding-page/unread control."""
from pathlib import Path
import copy,json
import numpy as np
from apply_blue_arrival_v14 import sample
from apply_menu_thumbnail_clips_v15 import affine_group
from apply_early_page_material_v17 import apply_page_material
from apply_early_bezel_overlay_v17 import apply_bezel
P=Path(__file__).resolve().parent

def matrix(node,frame):
    values={key:sample(node.get('keyframes',{}).get(key,[dict(t=0,value=node.get(key,default))]),frame/30) for key,default in [('x',0),('y',0),('scaleX',1),('scaleY',1)]}
    return np.array([[values['scaleX'],0,values['x']],[0,values['scaleY'],values['y']],[0,0,1]],float)

def gate(node,hidden):
    old=copy.deepcopy(node.get('keyframes',{}).get('opacity',[dict(t=0,value=node.get('opacity',1))]))
    keys=[k for k in old if k['t']<211/30]
    for frame in range(211,230):
        keys.append(dict(t=frame/30,value=0 if frame in hidden else sample(old,frame/30),ease='hold'))
    keys.append(dict(t=230/30,value=sample(old,230/30),ease='hold'))
    keys.extend(k for k in old if k['t']>230/30)
    node.setdefault('keyframes',{})['opacity']=keys

def apply_entry(scene):
    scene=apply_page_material(scene)
    data=json.loads((P/'early-entry-v17-measurements.json').read_text())
    root=next(n for n in scene['layers'] if n['id']=='p03-86')
    ui=next(n for n in root['children'] if n['id']=='early-messages-ui-v13')
    if any(n['id'].startswith('early-entry-measured-') for n in ui['children']):
        raise ValueError('Entry helper was already applied')
    new={};hidden={};proof=[]
    originals={node['id']:copy.deepcopy(node) for node in ui['children']}
    for row in data['messages']:
        if row['status']!='measured':
            continue
        frame=row['frame'];identifier=row['group_id']
        world=np.vstack([np.array(row['matrix']),[0,0,1]])
        parent=matrix(root,frame)@matrix(ui,frame)
        original=originals[identifier]
        reference_image=next(child for child in original['children'] if child['id']==row['image_id'])
        pixel=np.array([[reference_image['width']/row['intrinsic'][0],0,reference_image.get('x',0)],[0,reference_image['height']/row['intrinsic'][1],reference_image.get('y',0)],[0,0,1]],float)
        group_world=world@np.linalg.inv(pixel)
        local=(np.linalg.inv(parent)@group_world)[:2]
        items=copy.deepcopy(original['children'])
        def rename(item):
            item['id']=f'early-entry-{identifier}-{frame}-'+item['id']
            for child in item.get('children',[]):rename(child)
        for item in items:rename(item)
        if identifier=='p03-35':
            native=data['native_working_reference']
            refrow=next(record for record in data['messages'] if record['frame']==215 and record['group_id']=='p03-35')
            pixel=np.vstack([np.array(refrow['matrix']),[0,0,1]])
            group_world=world@np.linalg.inv(pixel)
            local=(np.linalg.inv(parent)@group_world)[:2]
            x,y,x2,y2=native['bbox']
            fill='#'+''.join(f'{value:02x}' for value in native['native_background_rgb'])
            ink='#'+format(native['native_foreground'],'02x')*3
            items=[
                dict(id=f'early-entry-native-working-{frame}-body',type='rect',
                     x=x,y=y,width=x2-x,height=y2-y,radius=(y2-y)/2,
                     fill=fill,semanticText='Grouped incoming status pill without a tail'),
                dict(id=f'early-entry-native-working-{frame}-copy',type='path',
                     d=native['path'],fill=ink,semanticText='Working on it.',
                     provenance=dict(kind='Native semantic original glyph outlines',
                         source_frame=215,
                         notice='Clean native body/copy remove the obsolete tail and captured motion blur from the former bitmap skin.'))
            ]
        # Keep the original pre/pressed skin stack and each child opacity. The
        # pressed state is fading over the pre state at211; one opaque sprite
        # cannot reproduce that already authorized component's material.
        group=affine_group(local,f'early-entry-measured-{identifier}-{frame}',items)
        group['provenance']=dict(kind='Existing bounded message child stack; independent native affine camera',measurement_file='early-entry-v17-measurements.json',inliers=row['inliers'],rms=row['rms'],notice='Natural-pixel correspondence converted back into original logical image canvas. Child lifetime, blending and pressed-state opacity are preserved. No new source-image sequence.')
        group.update(start=frame/30,end=(frame+1)/30)
        new.setdefault(identifier,[]).append(group);hidden.setdefault(identifier,set()).add(frame)
        proof.append(dict(frame=frame,group=identifier,recomposition_world_error=float(np.max(abs(parent@np.vstack([local,[0,0,1]])@pixel-world)))))
    children=[]
    for node in ui['children']:
        if node['id'] in hidden:
            gate(node,hidden[node['id']]);children.extend(new[node['id']])
        if node['id'] in ['p03-14','p03-15']:
            gate(node,set(range(211,230)))
        children.append(node)
    ui['children']=children
    reference=data['control_reference'];badge=reference['badge'];cx,cy=badge['center']
    radius=reference['draw_radius'];left,top,right,bottom=reference['pill_bbox']
    ref_parent=matrix(root,215)@matrix(ui,215)
    control_elements=[dict(id='pill',type='rect',x=left,y=top,width=right-left,height=bottom-top,radius=(bottom-top)/2,fill='#fdfdfd',shadow=dict(x=0,y=2,blur=3,color='#00000025'),semanticText='Back control'),dict(id='chevron',type='path',d=reference['chevron_path'],fill='#'+f'{reference["chevron_fill"]:02x}'*3,semanticText='Back'),dict(id='badge',type='circle',x=cx-radius,y=cy-radius,width=radius*2,height=radius*2,fill='#'+f'{reference["badge_fill"]:02x}'*3,semanticText='Unread count background'),dict(id='count',type='path',d=reference['count_path'],fill='#fdfdfd',semanticText='2 unread messages',provenance=dict(kind='Original source glyph outline',source_frame=215,notice='Native semantic white count glyph, not a control screenshot.'))]
    controls=[]
    for row in data['controls']:
        frame=row['frame'];parent=matrix(root,frame)@matrix(ui,frame)
        if len(row['proposals'])==1:
            observed=row['proposals'][0];scale=observed['radius']/badge['radius']
            world=np.array([[scale,0,observed['center'][0]-scale*cx],[0,scale,observed['center'][1]-scale*cy],[0,0,1]],float)
            status='observed_original_circle_arc'
        else:
            world=parent@np.linalg.inv(ref_parent)
            status='cropped_or_occluded_existing_UI_camera'
        local=(np.linalg.inv(parent)@world)[:2]
        items=copy.deepcopy(control_elements)
        for item in items:item['id']=f'early-entry-control-{frame}-'+item['id']
        group=affine_group(local,f'early-entry-measured-control-{frame}',items)
        group.update(start=frame/30,end=(frame+1)/30,measurementStatus=status)
        controls.append(group)
    ui['children'][1:1]=controls
    scene['early_entry_v17']=dict(scope=[211,229],accepted_message_poses=len(proof),affine_proof=proof,notice='Native black display and receding white-page material, independently measured existing static message skins, native unread2pill/circle/glyphs. False matches after actual foreground occlusion are rejected; source camera is retained for cropped/unobserved control poses. Existing hardware, Mail panel, later310+projection, menu and collage remain untouched. No complete source frame or source video playback.')
    return apply_bezel(scene,211,229,'early-entry-top-bezel-v17')

if __name__=='__main__':
    scene=json.loads((P/'final-v15.scene.json').read_text())
    result=apply_entry(scene)
    (P/'early-entry-v17-native-working-prototype.scene.json').write_text(json.dumps(result,indent=2))
    print('built',result['early_entry_v17']['accepted_message_poses'],'native message poses and native unread control')
