from pathlib import Path
import argparse,copy,json
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elements',type=Path,default=Path(__file__).with_name('boarding-exposure-review-elements.json'));a=p.parse_args();s=json.loads(a.input.read_text());sp=json.loads(a.elements.read_text());n=0

def absolute(layer):
    if layer.get('src') and not layer['src'].startswith(('/','data:','http:','https:')):layer['src']=str((a.input.parent/layer['src']).resolve())
    for child in layer.get('children',[]):absolute(child)
for layer in s['layers']:
    absolute(layer)
    if layer['id']==sp['root_id']:
        children=[c for c in layer['children'] if c['id']==sp['content_id']]
        if len(children)!=1:raise ValueError('Expected unique native boarding content')
        children[0].setdefault('keyframes',{})['opacity']=copy.deepcopy(sp['content_opacity']);layer['children']+=copy.deepcopy(sp['append_children']);n+=1
if n!=1:raise ValueError('Expected unique g942')
for font in s.get('fonts',[]):
    if not font['src'].startswith(('/','data:','http:','https:')):font['src']=str((a.input.parent/font['src']).resolve())
s['source']['notes']+=' Bounded boarding exposure review1185–1189/1191–1194/1196–1199: inferred native camera exposures and local linear-light color masks; original color fields/check-in and1190/1195 controls preserved.';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(s,indent=2));print(json.dumps(dict(root=n,ranges=sp['changed_frame_ranges'],output=str(a.output))))
