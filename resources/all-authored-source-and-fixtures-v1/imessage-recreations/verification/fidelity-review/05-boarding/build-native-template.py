from pathlib import Path
import copy, json
R=Path('/workspace/imessage-recreations'); P=R/'verification/fidelity-review/05-boarding'
scene=json.load(open(R/'outputs/05-linq/final-v11/scene.json'))
group=next(layer for layer in scene['layers'] if layer['id']=='g-942')
content=next(layer for layer in group['children'] if layer['id']=='root-boarding-native-content')
def clone(prefix,x):
    layer=copy.deepcopy(content)
    def rename(node):
        node['id']=prefix+node['id']
        for child in node.get('children',[]):rename(child)
    rename(layer)
    layer.pop('keyframes',None)
    layer.update(x=x,y=200)
    return layer
canonical=dict(width=1920,height=1400,fps=30,duration=1/30,background='#000000',layers=[dict(id='white-background',type='rect',x=960,y=0,width=960,height=1400,fill='#ffffff'),clone('black-',0),clone('white-',960)],source={'notes':'Analysis-only native vector alpha template; not a runtime screenshot or source-frame layer.'})
(P/'canonical-native.scene.json').write_text(json.dumps(canonical,indent=2))
