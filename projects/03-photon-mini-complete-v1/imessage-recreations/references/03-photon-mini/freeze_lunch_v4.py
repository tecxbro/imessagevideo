from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(__file__).parent
scene=json.loads((p/'candidate-refined-v4.scene.json').read_text())
camera=next(layer for layer in scene['layers'] if layer['id']=='p03-204')
Image.open(p/'measured/22.5.png').crop((1097,789,1248,940)).save(p/'assets/food-wrap.png')
def visit(layer,in_menu=False):
    if layer['type']=='group':
        texts=[x.get('text') for x in layer.get('children',[]) if x['type']=='text']
        if any(value and value.startswith('Taking everyone') for value in texts):
            layer['children']=[child for child in layer['children'] if child['type']!='path']
        if 'Uber Eats' in texts and any(x.get('clip',{}).get('height')==278 for x in layer.get('children',[])):
            layer['scaleX']=523/(520*1.02)
            layer['scaleY']=373/(370*1.02)
            for child in layer['children']:
                if child['type']=='group' and child.get('clip',{}).get('height')==278:
                    targetheight=277/(1.02*layer['scaleY'])
                    child['clip']['height']=targetheight
                    for image in child['children']:
                        image['height']=targetheight
                if child['type']=='text' and child.get('text')=='Uber Eats':
                    child['fontFamily']='Recreation Text UI'
                    child['fontSize']=28.8
                    child['lineHeight']=33.7
                if child['type']=='text' and child.get('text')=='Lanespan Pizza & Pub (Emeryville)':
                    child['fontFamily']='Recreation Text UI'
                    child['fontSize']=21.8
                    child['lineHeight']=25.5
                    child['y']=327
        if layer.get('start')==20.6 and layer.get('end')==23.45:
            in_menu=True
        if in_menu and any(child.get('text')=='Grilled Chicken Rice Bowl' for child in layer.get('children',[])):
            layer['x']=4.5
            for child in layer['children']:
                if child['type']=='image' and child.get('y')==1056:
                    child['src']='assets/food-wrap.png'
    for child in layer.get('children',[]):
        visit(child,in_menu)
visit(camera)
scene['source']['notes']+=' Final-v4 measured refinements: food preview nativewidth523px/height373px at20s and exact277pxinteriorheight; SFTextfooteradvancesfitted139px/361px; no tail on prior paragraph in same incomingchain; authentic turkeywrapphoto. Remaining unverifiedphases and photos are notcertifiedone-to-one.'
file=p/'final-v4.scene.json'
file.write_text(json.dumps(scene,indent=2))
checksum=hashlib.sha256(file.read_bytes()).hexdigest()
(p/'final-v4-changes.json').write_text(json.dumps({'sha256':checksum,'baseline':'final-v3.scene.json','changed_range_seconds':[15,26.7],'frame_range_inclusive':[450,800],'native_dimensions':[1920,1080],'fps':30,'frame_count':1260,'notes':['Camera measured from9bluebubbleanchors17.3–20.5; endpullback21.1','OfficialSFProText32.4 mainbubblecopy fitsnativeglyphwidths; rowText33 fits362pxsource title','One originalrichpreviewinteriorartasset withbitmapcopy; nativeouterbubble/footer/text/cameraremaineditable','AuthenicisolatedrightMemojiandturkeywrapphoto','No visualchangesoutside15<=t<26.7; Figma/exportavailabilityseparate','Existingrefined-v4PNGs predatelastanalyticfoodwidth/footer/rowpaddingrefinements; must samplepatchedcachebeforefinalsignoff']},indent=2))
print(checksum)
