"""Split copy/photo motion and assign foreground occlusion ownership explicitly."""
from pathlib import Path
import copy
import json
import math
import numpy as np
from apply_blue_arrival_v14 import sample
P = Path(__file__).resolve().parent

def affine_tracks(observations,role):
    keys = {key:[] for key in ['x','y','rotation','scaleX','scaleY']}
    inner = []
    opacity = []
    proof = []
    for frame,part in observations:
        matrix = np.array(part['matrix'],dtype='float64')
        left,singular,right = np.linalg.svd(matrix[:,:2])
        if np.linalg.det(left)<0:
            left[:,1] *= -1
            singular[1] *= -1
        if np.linalg.det(right)<0:
            right[1,:] *= -1
            singular[1] *= -1
        angle_left = math.degrees(math.atan2(left[1,0],left[0,0]))
        angle_right = math.degrees(math.atan2(right[1,0],right[0,0]))
        values = dict(x=matrix[0,2],y=matrix[1,2],rotation=angle_left,scaleX=singular[0],scaleY=singular[1])
        for key,value in values.items():
            keys[key].append(dict(t=frame/30,value=float(value),ease='hold'))
        inner.append(dict(t=frame/30,value=angle_right,ease='hold'))
        opacity.append(dict(t=frame/30,value=part['opacity'],ease='hold'))
        proof.append(dict(frame=frame,part=role,recomposition_error=float(np.max(abs(left@np.diag(singular)@right-matrix[:,:2]))),measurement_status=part['status']))
    return keys,inner,opacity,proof

def camera_clip(original,identifier,children):
    outer = {key:copy.deepcopy(value) for key,value in original.items() if key not in ['id','children','start','end']}
    outer.update(id=identifier,start=618/30,end=730/30)
    inverse = {key:[] for key in ['x','y','scaleX','scaleY']}
    for frame in range(618,730):
        time = frame/30
        values = {key:sample(original['keyframes'][key],time) for key in inverse}
        inverse_values = dict(x=-values['x']/values['scaleX'],y=-values['y']/values['scaleY'],scaleX=1/values['scaleX'],scaleY=1/values['scaleY'])
        for key,value in inverse_values.items():
            inverse[key].append(dict(t=time,value=value,ease='hold'))
    outer['children'] = [dict(id=identifier+'-world',type='group',keyframes=inverse,children=children)]
    return outer

def apply_rows(scene):
    scene = copy.deepcopy(scene)
    assets = json.loads((P/'menu-rows-v15/assets-split.json').read_text())['rows']
    frames = json.loads((P/'menu-rows-v15/parts-measurements.json').read_text())['frames']
    clip = next(layer for layer in scene['layers'] if layer['id']=='measured-menu-clip-v13')
    menu = clip['children'][0]
    body = next(layer for layer in menu['children'] if layer['id']=='menu13-p03-202')
    copies = []
    photos = []
    proof = []
    for index,asset in enumerate(assets):
        found = []
        for frame in frames:
            record = next((row for row in frame['rows'] if row['row']==index),None)
            if record:
                found.append((frame['frame'],record))
        first = found[0][0]
        native = body['children'][index]
        original_opacity = copy.deepcopy(native.get('keyframes',{}).get('opacity',[dict(t=0,value=native.get('opacity',1))]))
        native_opacity = [key for key in original_opacity if key['t']<first/30]
        native_opacity.append(dict(t=first/30,value=0,ease='hold'))
        native_opacity.append(dict(t=730/30,value=sample(original_opacity,730/30),ease='hold'))
        native_opacity.extend(key for key in original_opacity if key['t']>730/30)
        native.setdefault('keyframes',{})['opacity'] = native_opacity
        width,height = asset['dimensions']
        split = asset['copy_photo_split_x']
        separator_height = asset['separator_height']
        for role in ['copy','photo','separator']:
            measurement_role = role
            if role=='separator':
                measurement_role = 'copy'
            observations = [(frame,row['parts'][measurement_role]) for frame,row in found]
            tracks,rotation,opacity,checks = affine_tracks(observations,role)
            proof.extend(dict(row=index,**check) for check in checks)
            rectangle = dict(x=0,y=0,width=split,height=height-separator_height)
            if role=='photo':
                rectangle = dict(x=split,y=0,width=width-split,height=height-separator_height)
            if role=='separator':
                rectangle = dict(x=0,y=height-separator_height,width=width,height=separator_height)
            image = dict(id=f'menu-row-{index}-{role}-art-v15',type='image',src=asset['asset'],width=width,height=height,keyframes=dict(opacity=opacity),semanticText=asset['name'],provenance=dict(kind='Separately clipped static rich-app UI row artwork',source_frame=asset['source_frame'],source_crop=asset['source_crop'],notice=asset['editability']))
            children = [image]
            if role=='photo':
                children.insert(0,dict(id=f'menu-row-{index}-photo-white-support-v15',type='path',d=asset['photo_support_path'],fill='#fdfdfd',start=679/30,end=730/30,semanticText='Native white material supplies correct photo fade destination and opaque white highlights'))
            inner = dict(id=f'menu-row-{index}-{role}-inner-v15',type='group',keyframes=dict(rotation=rotation),clip=rectangle,children=children)
            group = dict(id=f'measured-menu-row-{index}-{role}-v15',type='group',start=first/30,end=730/30,keyframes=tracks,children=[inner])
            if role=='photo':
                photos.append(group)
            else:
                copies.append(group)
    copy_root = camera_clip(clip,'measured-menu-copy-art-clip-v15',copies)
    photo_root = camera_clip(clip,'measured-menu-photo-art-clip-v15',photos)
    forbidden = {'measured-menu-copy-art-clip-v15','measured-menu-photo-art-clip-v15'}
    scene['layers'] = [layer for layer in scene['layers'] if layer['id'] not in forbidden]
    before = next((i for i,layer in enumerate(scene['layers']) if layer['id'].startswith('root-backplane-stencil-')),next(i for i,layer in enumerate(scene['layers']) if layer['id']=='measured-lunch-bezel-overlay-v13'))
    scene['layers'].insert(before,copy_root)
    before_bezel = next(i for i,layer in enumerate(scene['layers']) if layer['id']=='measured-lunch-bezel-overlay-v13')
    scene['layers'].insert(before_bezel,photo_root)
    scene['menu_row_foreground_v15'] = dict(scope=[618,729],static_assets=6,notice='Six static separately bounded row UI assets are reused through copy/photo/separator clips. Copy and thumbnail load/selection motion are independently source-measured. Internal labels/prices/descriptions/photos/originalplus controls are bitmap; native panel/header/camera/hardware/cart/selection actors remain separate. Copy/separators stay under the exposed-page stencil; independent photo foreground paints above it and belowhardware with native white support only during the active679–729 stencil interval. Earlier thumbnail fades retain the actual background. Original editable native vector rows remain gated fallbacks and restore exactly at730. No full-frame or source-video runtime layer.',affine_proof=proof)
    return scene

if __name__=='__main__':
    scene = json.loads((P/'final-v14.scene.json').read_text())
    scene = apply_rows(scene)
    (P/'menu-rows-split-v15.scene.json').write_text(json.dumps(scene,indent=2))
    print('built split row scene')
