from pathlib import Path
from PIL import Image
from fontTools import subset
import json
p=Path(__file__).parent
scene=json.loads((p/'candidate-geometry-v4.scene.json').read_text())
camera=next(layer for layer in scene['layers'] if layer['id']=='p03-204')
# Corrected static artwork: one rich preview interior, one genuine isolated flying Memoji.
Image.open(p/'measured/20.png').crop((704,557,1227,834)).save(p/'assets/food-preview-original-art.png')
Image.open(p/'measured/21.5.png').crop((1315,540,1445,675)).save(p/'assets/laptop-person-menu.png')
known_bubbles=['Can someone order lunch for us?','Vegetarian for me.','Something light.',"Taking everyone’s preferences\ninto account, I found a few good\noptions."]
changes=[]
def visit(layer,in_menu=False):
    if layer['type']=='group':
        texts=[x.get('text') for x in layer.get('children',[]) if x['type']=='text']
        if 'Can someone order lunch for us?' in texts:
            layer.setdefault('keyframes',{})['y']=[{'t':15,'value':420},{'t':16.5,'value':420},{'t':17.3,'value':425,'ease':'linear'}]
        if 'Vegetarian for me.' in texts:
            layer.setdefault('keyframes',{})['y']=[{'t':15,'value':560},{'t':16.5,'value':560},{'t':17.3,'value':565,'ease':'linear'}]
        if any(value and value.startswith('Taking everyone') for value in texts):
            for key in layer['keyframes']['y']:
                key['value']-=7
        if 'Uber Eats' in texts and any(x.get('clip',{}).get('height')==278 for x in layer.get('children',[])):
            layer['x']=149
            layer['keyframes']['y']=[{'t':18.3,'value':1049.5},{'t':18.5,'value':1012.7,'ease':'easeOut'},{'t':18.7,'value':1019.5,'ease':'easeOut'}]
            layer['keyframes']['opacity']=[{'t':18.3,'value':0},{'t':18.5,'value':1,'ease':'easeOut'}]
            for child in layer['children']:
                if child['type']=='group' and child.get('clip',{}).get('height')==278:
                    child['clip']['radius']=0
                    child['children']=[{'id':'food-preview-original-interior-v4','type':'image','src':'assets/food-preview-original-art.png','x':0,'y':0,'width':520,'height':278}]
            changes.append(layer['id'])
        if layer.get('start')==20.6 and layer.get('end')==23.45:
            in_menu=True
    if layer['type']=='text':
        if layer.get('text') in known_bubbles:
            layer['fontFamily']='Recreation Text UI'
            layer['fontSize']=32.4
            layer['lineHeight']=39.2
            if layer['text']=='Something light.':
                layer['x']=30
            changes.append(layer['id'])
        if layer.get('text')=='Agent' and layer.get('y')==816:
            layer['y']=805
        if in_menu:
            layer['fontFamily']='Recreation Text UI'
            if layer.get('fontSize')==32:
                layer['fontSize']=33
                layer['lineHeight']=38.6
            changes.append(layer['id'])
    for child in layer.get('children',[]):
        visit(child,in_menu)
visit(camera)
for layer in scene['layers']:
    if layer['type']=='image' and layer.get('src')=='assets/laptop-person.png' and layer.get('start')==20.7:
        layer['src']='assets/laptop-person-menu.png'
        layer['width']=130
        layer['height']=135
        for key in layer['keyframes']['x']:
            key['value']-=15
        for key in layer['keyframes']['y']:
            key['value']-=50
        changes.append(layer['id'])
# Add true official SF Pro Text faces, subset only to the current scene characters.
characters=set(' ')
def gather(layer):
    if layer['type']=='text':
        characters.update(layer.get('text',''))
    for child in layer.get('children',[]):
        gather(child)
for layer in scene['layers']:
    gather(layer)
for style,weight in [('Regular',400),('Semibold',600),('Bold',700)]:
    original=Path('/workspace/imessage-recreations/shared/fonts')/('SF-Pro-Text-'+style+'.otf')
    output=p/'assets'/('SF-Pro-Text-'+style+'.scene.woff')
    options=subset.Options()
    font=subset.load_font(str(original),options)
    worker=subset.Subsetter(options=options)
    worker.populate(text=''.join(characters))
    worker.subset(font)
    font.flavor='woff'
    font.save(output)
    scene['fonts'].append({'family':'Recreation Text UI','src':str(output.relative_to(p)),'weight':weight})
scene['source']['notes']+=' V4 lunch patch: measured SF Pro Text glyph fit for main bubbles/menu, measured localstack spacing, original individual food-preview interior bitmapUI artwork, and original isolated flyinglaptopMemoji. Source0–15and26.7–42visuals unchanged from final-v3; changedrange15<=t<26.7.'
(p/'candidate-refined-v4.scene.json').write_text(json.dumps(scene,indent=2))
(p/'candidate-refined-v4-changes.json').write_text(json.dumps({'changed_layer_ids':changes,'changed_range_seconds':[15,26.7],'frame_range_inclusive':[450,800],'notes':'Rootfonts added but all earlier/later nodes retainoriginalfamily; no wholeframe/videoasset.'},indent=2))
print('candidate refined; changedlayers',len(changes))
