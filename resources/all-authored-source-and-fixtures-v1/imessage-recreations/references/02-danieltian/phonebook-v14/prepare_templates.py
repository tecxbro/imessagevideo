from pathlib import Path
import json,copy
R=Path(__file__).resolve().parent;P=R.parent.parent.parent/'outputs/02-danieltian/final-v13';s=json.loads((P/'scene.json').read_text());ids=['pb-capsule-lyft','pb-capsule-airbnb','pb-capsule-resy','pb-uber-eats'];layers=[]
def absolute(n):
 if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((P/n['src']).resolve())
 for c in n.get('children',[]):absolute(c)
for j,id in enumerate(ids):
 n=copy.deepcopy(next(q for q in s['layers'] if q['id']==id));absolute(n);n['keyframes']={};n.update(x=j*640+16,y=20,rotation=0,scaleX=1,scaleY=1,originX=0,originY=0,opacity=1,start=0,end=s['duration']);layers.append(n)
out=dict(width=2560,height=160,fps=30,duration=s['duration'],background='#FDFDFD',fonts=[],gradients=s.get('gradients',[]),layers=layers,source={'notes':'Measurement-only isolated original UI parts, local root cameras removed. Not a production recreation or a full source-frame asset.'});(R/'local-templates.scene.json').write_text(json.dumps(out,indent=2));(R/'template-order.json').write_text(json.dumps(ids));print('Prepared4 original UI local templates',flush=True)
