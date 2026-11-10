from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
scene=json.loads((ROOT/'outputs/02-danieltian/final-v15/scene.json').read_text())
rows=[]
def walk(node,parents):
    start=node.get('start',0);end=node.get('end',999)
    if 29.5<=start<=30.45 or ('love-it'in node['id']):
        rows.append({'id':node['id'],'type':node['type'],'start':start,'end':end,'parents':parents,'x':node.get('x'),'y':node.get('y'),'opacity':node.get('opacity'),'keyframes':{key:values[:3]if len(values)>6 else values for key,values in node.get('keyframes',{}).items()},'semanticText':node.get('semanticText'),'text':node.get('text')})
    for child in node.get('children',[]):walk(child,parents+[node['id']])
for node in scene['layers']:walk(node,[])
output=Path(__file__).resolve().parent/'pre912-node-audit.json';output.write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
