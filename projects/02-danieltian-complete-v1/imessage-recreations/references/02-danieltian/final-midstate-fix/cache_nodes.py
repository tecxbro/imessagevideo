from pathlib import Path
import json,copy,re
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parent;BASE=ROOT/'outputs/02-danieltian/final-v14/scene.json';s=json.loads(BASE.read_text());g=copy.deepcopy(next(n for n in s['layers']if n['id']=='group-1118'))
def absolute(n):
 if n.get('src')and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((BASE.parent/n['src']).resolve())
 for c in n.get('children',[]):absolute(c)
absolute(g);(R/'chat-original.json').write_text(json.dumps(g,separators=(',',':')));nodes={};parents={}
def walk(n,p=''):
 nodes[n['id']]=n;parents[n['id']]=p
 for c in n.get('children',[]):walk(c,n['id'])
walk(g);atlas=[];meta=[]
for id,y in[('middle-glyphs-budget-reply',0),('middle-glyphs-love-it',200)]:
 n=copy.deepcopy(nodes[id]);n.pop('keyframes',None);n['opacity']=1;n['y']=n.get('y',0)+y;atlas.append(n);meta.append({'id':id,'atlasY':y,'nativeFill':nodes[id].get('fill'),'pathBytes':len(n['d']),'parent':parents[id]})
labels=[]
for id,n in nodes.items():
 if n.get('semanticText')=='Airbnb' or id.startswith('middle-agent-label'):
  labels.append({k:n[k]for k in['id','type','start','end','semanticText','sourceFrame','x','y','opacity']if k in n}|{'parent':parents[id],'parentStart':nodes[parents[id]].get('start'),'parentEnd':nodes[parents[id]].get('end')})
(R/'agent-label-node-audit.json').write_text(json.dumps(labels,indent=2));(R/'glyph-atlas.scene.json').write_text(json.dumps({'id':'white-glyph-component-measurement','width':600,'height':400,'fps':30,'duration':1,'background':'#000000','layers':atlas},separators=(',',':')));(R/'glyph-atlas-meta.json').write_text(json.dumps(meta,indent=2));print('cached source chat subtree',len(nodes),'nodes; glyph masks',meta);print('agentlabels',labels)
