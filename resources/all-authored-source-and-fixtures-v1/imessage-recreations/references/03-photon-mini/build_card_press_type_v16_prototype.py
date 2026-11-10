from pathlib import Path
import copy,json
P=Path(__file__).resolve().parent
scene=json.loads((P/'final-v15.scene.json').read_text())
root=next(n for n in scene['layers'] if n['id']=='p03-204')

def find(nodes,identifier):
    for node in nodes:
        if node['id']==identifier:return node
        result=find(node.get('children',[]),identifier)
        if result:return result
    return None

def one_frame(node,key,value):
    old=node.get(key)
    node.setdefault('keyframes',{})[key]=[dict(t=0,value=old,ease='hold'),dict(t=605/30,value=value,ease='hold'),dict(t=606/30,value=old,ease='hold')]

paragraph=find(root['children'],'p03-132')
one_frame(paragraph,'fontSize',33)
one_frame(paragraph,'y',16)
body=find(root['children'],'p03-135');tail=find(root['children'],'p03-134')
one_frame(body,'fill','#e8e8e8');one_frame(tail,'fill','#e8e8e8')
black_tail={key:copy.deepcopy(value) for key,value in tail.items() if key not in ['id','keyframes']}
black_tail.update(id='press-prototype-tail-v16',fill='#000000')
black_body={key:copy.deepcopy(value) for key,value in body.items() if key not in ['id','keyframes']}
black_body.update(id='press-prototype-body-v16',fill='#000000')
inner=find(root['children'],'measured-preview-inner-affine-v14')
inner['children'].append(dict(id='measured-card-press-material-prototype-v16',type='group',start=605/30,end=606/30,opacity=.14,children=[black_tail,black_body],semanticText='Pressed rich-app card material',provenance=dict(kind='Native black press material over the union of existing rounded card and tail',notice='Group opacity applies once across overlapping body/tail. No viewport dim, no new artwork.')))
(P/'card-press-type-v16-prototype.scene.json').write_text(json.dumps(scene,indent=2))
print('built isolated605press/type prototype')
