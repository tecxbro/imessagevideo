"""Clip the early food-texture overshoot inside its fixed native thumbnail slot."""
from pathlib import Path
import copy,json,math
import numpy as np
P=Path(__file__).resolve().parent

def affine_group(matrix,identifier,children,clip=None):
    matrix=np.asarray(matrix,dtype=float)
    left,singular,right=np.linalg.svd(matrix[:,:2])
    if np.linalg.det(left)<0:
        left[:,1]*=-1
        singular[1]*=-1
    if np.linalg.det(right)<0:
        right[1,:]*=-1
        singular[1]*=-1
    inner=dict(id=identifier+'-inner',type='group',rotation=math.degrees(math.atan2(right[1,0],right[0,0])),children=children)
    if clip is not None:
        inner['clip']=clip
    return dict(id=identifier,type='group',x=float(matrix[0,2]),y=float(matrix[1,2]),rotation=math.degrees(math.atan2(left[1,0],left[0,0])),scaleX=float(singular[0]),scaleY=float(singular[1]),children=[inner])

def apply_thumbnail_clips(scene):
    scene=copy.deepcopy(scene)
    assets=json.loads((P/'menu-rows-v15/assets-split.json').read_text())['rows']
    art=json.loads((P/'menu-rows-v15/thumbnail-entrance-art.json').read_text())['rows']
    data=json.loads((P/'menu-rows-v15/parts-measurements.json').read_text())['frames']
    root=next(layer for layer in scene['layers'] if layer['id']=='measured-menu-photo-art-clip-v15')['children'][0]
    boxes=[[436.2,24.7,153.4,152.4],[436.2,28.6,153.3,152.4],[436.2,29.4,153.3,152.4],[423.3,29.1,146.9,146.9]]
    poses=[]
    for index,box in enumerate(boxes):
        photo=next(layer for layer in root['children'] if layer['id']==f'measured-menu-row-{index}-photo-v15')
        opacity=[]
        for frame in data:
            row=next((r for r in frame['rows'] if r['row']==index),None)
            if row is None:
                continue
            copy_matrix=np.array(row['parts']['copy']['matrix'])
            photo_matrix=np.array(row['parts']['photo']['matrix'])
            ratio=math.sqrt(np.linalg.det(photo_matrix[:,:2])/np.linalg.det(copy_matrix[:,:2]))
            clipped=frame['frame']<650 and ratio>1.015
            opacity.append(dict(t=frame['frame']/30,value=0 if clipped else 1,ease='hold'))
            if not clipped:
                continue
            copy3=np.vstack([copy_matrix,[0,0,1]])
            photo3=np.vstack([photo_matrix,[0,0,1]])
            relative=(np.linalg.inv(copy3)@photo3)[:2]
            asset=assets[index]
            image=dict(id=f'thumbnail-slot-{index}-{frame["frame"]}-art',type='image',src=art[index]['texture'],width=asset['dimensions'][0],height=asset['dimensions'][1],opacity=row['parts']['photo']['opacity'],semanticText=asset['name'],provenance=dict(kind='Single static bounded original thumbnail texture; independently measured content overshoot inside native slot',source_frame=asset['source_frame'],source_crop=asset['source_crop']))
            content=affine_group(relative,f'thumbnail-slot-{index}-{frame["frame"]}-content',[image])
            control=dict(id=f'thumbnail-slot-{index}-{frame["frame"]}-control',type='image',src=art[index]['control'],**art[index]['control_geometry'],semanticText='Add item',provenance=art[index]['provenance'])
            clip=dict(x=box[0],y=box[1],width=box[2],height=box[3],radius=box[3]*.285)
            slot=affine_group(copy_matrix,f'thumbnail-slot-{index}-{frame["frame"]}',[content,control],clip)
            slot.update(start=frame['frame']/30,end=(frame['frame']+1)/30)
            root['children'].append(slot)
            poses.append(dict(frame=frame['frame'],row=index,content_to_slot_scale=ratio,slot_reference_bbox=box))
        photo['keyframes']['opacity']=opacity
    scene['menu_thumbnail_entrance_v15']=dict(poses=poses,notice='Food texture overshoots the independently moving fixed native rounded slot during four thumbnail entrances. Selection shrink poses remain independent. Static original row texture is reused; no frame/video playback.')
    return scene

if __name__=='__main__':
    scene=json.loads((P/'menu-rows-split-v15.scene.json').read_text())
    scene=apply_thumbnail_clips(scene)
    (P/'menu-rows-clipped-v15.scene.json').write_text(json.dumps(scene,indent=2))
    print('clipped entrance poses',len(scene['menu_thumbnail_entrance_v15']['poses']))
