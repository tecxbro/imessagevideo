"""Four static genuine-photo textures plus separately bounded original controls.
Combines a clean rest photo and one clean entrance observation to recover only
photo pixels exposed outside the independently fixed control. No frame playback.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
P=Path(__file__).resolve().parent
A=P/'assets/menu-thumbnail-entrance-v15';A.mkdir(exist_ok=True)
assets=json.loads((P/'menu-rows-v15/assets-split.json').read_text())['rows']
frames=json.loads((P/'menu-rows-v15/parts-measurements.json').read_text())['frames']
centers=[(554,142,22),(554,146,22),(554,146,22),(536,142,21.5)]
boxes=[[436.2,24.7,153.4,152.4],[436.2,28.6,153.3,152.4],[436.2,29.4,153.3,152.4],[423.3,29.1,146.9,146.9]]
records=[]
for index in range(4):
    asset=assets[index]
    width,height=asset['dimensions']
    yy,xx=np.mgrid[:height*2,:width*2].astype('float32')
    refx=(xx+.5)/2-.5
    refy=(yy+.5)/2-.5
    original=np.array(Image.open(P/'lunch-native'/f'{asset["source_frame"]-609:03}.png').convert('RGB'))
    left,top,right,bottom=asset['source_crop']
    base=original[top:bottom,left:right]
    rgb=cv2.resize(base,(width*2,height*2),interpolation=cv2.INTER_CUBIC).astype('float32')
    cx,cy,radius=centers[index]
    alpha=(((refx-cx)**2+(refy-cy)**2)>(radius+1.0)**2).astype('float32')
    entry=next(z for z in frames if any(r['row']==index for r in z['rows']))
    row=next(r for r in entry['rows'] if r['row']==index)
    photo=np.array(row['parts']['photo']['matrix'])
    copy=np.array(row['parts']['copy']['matrix'])
    sx=photo[0,0]*refx+photo[0,1]*refy+photo[0,2]
    sy=photo[1,0]*refx+photo[1,1]*refy+photo[1,2]
    source=np.array(Image.open(P/'lunch-native'/f'{entry["frame"]-609:03}.png').convert('RGB')).astype('float32')
    sampled=cv2.remap(source,sx.astype('float32'),sy.astype('float32'),cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(253,253,253))
    inverse_copy=np.linalg.inv(np.vstack([copy,[0,0,1]]))
    slotx=inverse_copy[0,0]*sx+inverse_copy[0,1]*sy+inverse_copy[0,2]
    sloty=inverse_copy[1,0]*sx+inverse_copy[1,1]*sy+inverse_copy[1,2]
    x,y,w,h=boxes[index]
    # Use safely interior photographic pixels only; the native slot owns edges.
    corner_radius=h*.285
    dx=np.maximum(abs(slotx-(x+w/2))-(w/2-corner_radius),0)
    dy=np.maximum(abs(sloty-(y+h/2))-(h/2-corner_radius),0)
    valid=(dx*dx+dy*dy<(corner_radius-3)**2)&(slotx>x+3)&(slotx<x+w-3)&(sloty>y+3)&(sloty<y+h-3)&(((slotx-cx)**2+(sloty-cy)**2)>(radius+1.5)**2)
    edge_distance=np.minimum.reduce([slotx-x,x+w-slotx,sloty-y,y+h-sloty])
    valid &= ~((edge_distance<25)&(np.min(sampled,axis=2)>243))
    opacity=row['parts']['photo']['opacity']
    sampled=np.clip(253+(sampled-253)/max(.1,opacity),0,255)
    rgb[valid]=sampled[valid]
    alpha[valid]=1
    # Crop atlas to the four bounded photographic domains, never the UI row.
    domain=(refx>x-2)&(refx<x+w+2)&(refy>y-2)&(refy<y+h+2)
    alpha*=domain
    texture=A/f'photo-{index}.png'
    Image.fromarray(np.dstack([np.uint8(np.clip(rgb,0,255)),np.uint8(alpha*255)])).save(texture)
    control_left=int(round(cx-radius));control_top=int(round(cy-radius));side=int(round(radius*2))
    control=base[control_top:control_top+side,control_left:control_left+side].copy()
    yy2,xx2=np.mgrid[:side,:side]
    control_alpha=np.uint8(np.clip(radius-np.sqrt((xx2+.5-side/2)**2+(yy2+.5-side/2)**2),0,1)*255)
    file=A/f'control-{index}.png'
    Image.fromarray(np.dstack([control,control_alpha])).save(file)
    records.append(dict(row=index,texture=str(texture),texture_sha256=hashlib.sha256(texture.read_bytes()).hexdigest(),control=str(file),control_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),control_geometry=dict(x=control_left,y=control_top,width=side,height=side),slot_box=boxes[index],provenance=dict(clean_rest_frame=asset['source_frame'],source_crop=asset['source_crop'],extra_genuine_photo_observation=entry['frame'],notice='The one entrance observation contributes only bounded genuine food pixels outside the independent native slot/control; rest crop fills other photo pixels. Transparent intersection remains under all independently positioned original control circles. Static photographic texture and bounded original plus glyph only; no complete source frame, video, or per-frame art sequence.')))
(P/'menu-rows-v15/thumbnail-entrance-art.json').write_text(json.dumps(dict(rows=records),indent=2))
print('built four static photographic textures and four bounded controls')
