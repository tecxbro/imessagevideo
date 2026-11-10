from pathlib import Path
import json
R=Path(__file__).resolve().parent
ROOT=R.parents[2]
BASE=ROOT/'outputs/02-danieltian/final-v16/scene.json'
scene=json.loads(BASE.read_text())
ids=['reason-v5-measured-camera','group-1077','group-1118']
selected={node['id']:node for node in scene['layers']if node['id']in ids}
assert set(selected)==set(ids)
def absolute(node):
    if node.get('src')and not node['src'].startswith(('/','data:','http:','https:')):node['src']=str((BASE.parent/node['src']).resolve())
    for child in node.get('children',[]):absolute(child)
for node in selected.values():absolute(node)
for identity,node in selected.items():(R/(identity+'.json')).write_text(json.dumps(node,separators=(',',':')))
records=[]
def walk(node,parents):
    record={key:value for key,value in node.items()if key not in['d','src','keyframes','children']}
    record['parents']=parents
    record['pathLength']=len(node.get('d',''))
    if node.get('src'):record['src']=node['src']
    if node.get('keyframes'):record['keyframes']={key:values if len(values)<=8 else[values[0],values[-1]]for key,values in node['keyframes'].items()}
    records.append(record)
    for child in node.get('children',[]):walk(child,parents+[node['id']])
walk(selected['reason-v5-measured-camera'],[])
walk(selected['group-1077'],[])
reaction=next(n for n in selected['group-1118']['children']if n['id']=='middle-reaction-command-like')
walk(reaction,[])
(R/'component-audit.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
