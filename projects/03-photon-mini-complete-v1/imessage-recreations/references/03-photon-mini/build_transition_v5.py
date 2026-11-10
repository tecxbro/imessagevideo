from pathlib import Path
from PIL import Image
import copy,json,hashlib
p=Path(__file__).parent
scene=json.loads((p/'final-v4.scene.json').read_text())
phone=next(layer for layer in scene['layers'] if layer.get('start')==1.65 and layer.get('end')==13.8)
lunch=next(layer for layer in scene['layers'] if layer['id']=='p03-204')
late=copy.deepcopy(phone)

def reid(layer,prefix):
    layer['id']=prefix+layer['id']
    for child in layer.get('children',[]):
        reid(child,prefix)
reid(late,'late-mail-')
late['start']=13.8
late['end']=430/30
measurements=json.loads((p/'transition-14/blue-card-camera-refined.json').read_text())
for field in ['x','y','scaleX','scaleY']:
    initial=phone['keyframes'][field][-1]['value']
    keys=[{'t':13.8,'value':initial}]
    for row in measurements:
        value=row['scale']
        if field=='x':value=row['camera_x']
        if field=='y':value=row['camera_y']
        keys.append({'t':row['t'],'value':value,'ease':'linear'})
    final=.001
    if field=='x':final=959.6
    if field=='y':final=539.171
    keys.append({'t':14.3,'value':final,'ease':'linear'})
    late['keyframes'][field]=keys

def refine(layer):
    if layer.get('end')==13.8:
        layer['end']=430/30
    if layer['type']=='group':
        texts=[child.get('text') for child in layer.get('children',[]) if child['type']=='text']
        if any(value and value.startswith('Draft an email') for value in texts):
            layer['end']=430/30
            for key in layer.get('keyframes',{}).get('y',[]):key['value']+=30
        if 'Working on it.' in texts:
            layer['end']=430/30
            for key in layer.get('keyframes',{}).get('y',[]):key['value']+=30
            layer['children']=[child for child in layer['children'] if child['type']!='path']
        if 'Sent.' in texts:
            layer['children']=[child for child in layer['children'] if child['type']!='path']
        if "I'll let you know when she replies." in texts:
            for key in layer.get('keyframes',{}).get('y',[]):key['value']-=24
            for child in layer['children']:
                if child['type']=='rect':
                    child.update(width=575,height=74,radius=37)
                if child['type']=='path':
                    child['d']='M25 52 Q27 78 13 86 Q48 77 55 54 Z'
        if 'Mail' in texts:
            for child in layer['children']:
                if child['type']=='group' and child.get('clip',{}).get('height')==274:
                    child['clip']['radius']=0
                    child['children']=[{'id':'late-mail-card-original-interior','type':'image','src':'assets/mail-preview-original-art.png','x':0,'y':0,'width':517,'height':274}]
                if child['type']=='text' and child.get('text')=='Mail':
                    child.update(fontFamily='Recreation Text UI',fontSize=29.5,lineHeight=34.5)
                if child['type']=='text' and child.get('text')=='To: Alice':
                    child.update(fontFamily='Recreation Text UI',fontSize=21.5,lineHeight=25)
    if layer['type']=='text':
        value=layer.get('text','')
        if value.startswith('Draft an email') or value in ['Working on it.','Sent.',"I'll let you know when she replies."]:
            layer.update(fontFamily='Recreation Text UI',fontSize=32.4,lineHeight=39.2)
            if value.startswith('Draft an email'):layer['x']=30
    for child in layer.get('children',[]):refine(child)
refine(late)
# Keep hardware opaque while measured UI brightness fades toward the white screen.
hardware=late['children'][:6]
ui=late['children'][6:]
ui_opacity=[{'t':13.8,'value':1}]
first_red=75
for index,row in enumerate(measurements):
    image=Image.open(p/'transition-14'/f'{index+1:02}.png').convert('RGB')
    x=round(row['blue_art']['x']+100*row['scale']);y=round(row['blue_art']['y']+50*row['scale'])
    red=image.getpixel((x,y))[0]
    ui_opacity.append({'t':row['t'],'value':max(0,min(1,(253-red)/(253-first_red))),'ease':'linear'})
ui_opacity.append({'t':14.3,'value':0,'ease':'linear'})
composer=next((child for child in lunch['children'] if child['type']=='group' and child.get('start')==23.7),None)
if composer:
    composer=copy.deepcopy(composer);reid(composer,'late-composer-');composer.update(start=13.8,end=430/30,y=53);ui.append(composer)
late['children']=hardware+[{'id':'late-mail-ui-fade','type':'group','children':ui,'keyframes':{'opacity':ui_opacity}}]
# Reconstruct independent avatar motion from the actual colored-circle contours.
fits=json.loads((p/'transition-14/independent-avatar-poses.json').read_text())
old_avatars=[layer for layer in scene['layers'] if layer['type']=='image' and layer.get('start')==13.8 and layer.get('end')==15.25]
by_asset={Path(layer['src']).name:layer for layer in old_avatars}
points={'bob':(100,200),'laptop':(30,200),'robot':(50,400),'alice':(300,70)}
carriers=[]
for name,info in fits.items():
    original=by_asset[info['asset']]
    artwork=copy.deepcopy(original)
    for field in ['keyframes','start','end','scaleX','scaleY','rotation','originX','originY']:
        artwork.pop(field,None)
    artwork.update(id='avatar-art-'+name,x=0,y=0)
    asset_image=Image.open(p/'assets'/info['asset']).convert('RGB')
    artwork['width'],artwork['height']=asset_image.size
    color=asset_image.getpixel(points[name]);fill='#' + ''.join(f'{value:02x}' for value in color)
    world=info['world'];radius=world['radius']
    circle={'id':'avatar-background-extension-'+name,'type':'circle','x':world['cx']-radius,'y':world['cy']-radius,'width':radius*2,'height':radius*2,'fill':fill}
    poses=copy.deepcopy(info['poses'])
    # The exact source crop is the final 14.5s pose; do not let fitting noise alter it.
    poses=[row for row in poses if row['t']<14.5]
    poses.append({'t':14.5,'scale':1,'x':info['base_xy'][0],'y':info['base_xy'][1]})
    tracks={}
    for field in ['x','y','scaleX','scaleY']:
        key='scale'
        if field in ['x','y']:key=field
        tracks[field]=[{'t':row['t'],'value':row[key],'ease':'linear'} for row in poses]
        tracks[field].append(copy.deepcopy(original['keyframes'][field][-1]))
    carrier={'id':'avatar-carrier-'+name,'type':'group','children':[circle,artwork],'start':poses[0]['t'],'end':15.25,'keyframes':tracks}
    carriers.append(carrier)
cluster={'id':'measured-avatar-transition-v5','type':'group','children':carriers,'start':430/30,'end':15.25}
# Replace only the previously premature transition; everything else remains frozen v4.
replacement=[]
for layer in scene['layers']:
    if layer in old_avatars:
        if not any(item['id']=='late-mail-native-state-v5' for item in replacement):
            late['id']='late-mail-native-state-v5';replacement.extend([late,cluster])
    else:replacement.append(layer)
scene['layers']=replacement
scene['source']['notes']+=' V5 transition correction: native mail phone remains until14.300s and avatars begin atframe430/30; individual original avatar crops and editable background circles follow contour-fitted independent tracks. Relativev4 changesonly13.8<=t<15.25 (frames414–457). No whole source frame or source video layer.'
file=p/'final-v5.scene.json';file.write_text(json.dumps(scene,indent=2));checksum=hashlib.sha256(file.read_bytes()).hexdigest()
(p/'final-v5-changes.json').write_text(json.dumps({'sha256':checksum,'baseline':'final-v4.scene.json','inclusive_changed_frames_from_v4':[414,457],'inclusive_changed_frames_from_v3':[414,800],'phone_transition_source_frames':[420,429],'first_avatar_source_frame':430,'source_measurements':['transition-14/blue-card-camera-refined.json','transition-14/independent-avatar-poses.json'],'limitations':'Contour fits validate camera/background boundaries, not all character texture pixels. Native transition preview and patched-cache QA still required.'},indent=2))
print(checksum)
