"""Native editable Cash plus-control pulse with one authentic static plus detail."""
from pathlib import Path
import json
D = Path(__file__).resolve().parent

def find(layers, identity):
    for layer in layers:
        if layer['id'] == identity:
            return layer
        result = find(layer.get('children', []), identity)
        if result is not None:
            return result

def gray(value):
    return '#' + f'{max(0,min(255,round(value))):02x}'*3

def apply_cash_native(scene):
    panel = find(scene['layers'], 'v10-cash-panel')
    if any(child['id']=='root-cash-native-control-v19' for child in panel['children']):
        raise ValueError('Native Cash control already installed')
    data = json.loads((D/'root-cash-control-v19/native-measurements.json').read_text())
    poses = data['poses']
    def keys(function):
        return [{'t':pose['frame']/30,'value':function(pose),'ease':'linear'} for pose in poses]
    eraser = {'id':'root-cash-control-backing-v19','type':'circle','x':610,'y':345,'width':104,'height':110,'keyframes':{'fill':keys(lambda p:gray(p['background']))}}
    circle = {'id':'root-cash-control-disc-v19','type':'circle','keyframes':{
        'x':keys(lambda p:p['cx']-p['rx']),'y':keys(lambda p:p['cy']-p['ry']),
        'width':keys(lambda p:2*p['rx']),'height':keys(lambda p:2*p['ry']),
        'fill':keys(lambda p:gray(p['fill'])),'stroke':keys(lambda p:gray(p['stroke'])),
        'strokeWidth':keys(lambda p:p['strokeWidth']),
        'opacity':keys(lambda p:1 if p['glyphVisible'] else 0)}}
    reference = next(pose for pose in poses if pose['frame']==820)
    x0,y0,x1,y1=data['glyphImageBounds']
    core_x,core_y=reference['cx']-x0,reference['cy']-y0
    def sx(pose):return pose['glyphWidth']/data['glyphCoreWidth']
    def sy(pose):return pose['glyphHeight']/data['glyphCoreHeight']
    glyph = {'id':'root-cash-control-plus-v19','type':'image','src':str((D/'root-cash-control-v19/plus-static-820.png').resolve()),'width':40,'height':40,'sourceFrame':820,'semanticText':'+','editability':'One authentic static40×40 plus-alpha detail; native numeric position/size tracks, disc and material remain editable.', 'keyframes':{
        'x':keys(lambda p:p['cx']-core_x*sx(p)),'y':keys(lambda p:p['cy']-core_y*sy(p)),
        'width':keys(lambda p:40*sx(p)),'height':keys(lambda p:40*sy(p)),
        'opacity':keys(lambda p:1 if p['glyphVisible'] else 0)}}
    group = {'id':'root-cash-native-control-v19','type':'group','start':774/30,'end':832/30,'children':[eraser,circle,glyph],'semanticText':'Cash plus control pulse / hover','editability':'Native backing, circle, grayscale/radius/position/stroke tracks plus one authentic static plus-alpha detail. Original amount glyphs are painted above it; panel/input cameras unchanged.'}
    index = next(i for i,child in enumerate(panel['children']) if child['id']=='v10-cash-amount')
    panel['children'].insert(index,group)
    return scene
