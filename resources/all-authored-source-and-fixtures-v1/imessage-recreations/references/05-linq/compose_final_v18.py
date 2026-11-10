"""Compose four immutable, ID-scoped V18 releases from immutable V17."""
from pathlib import Path
import hashlib,json,importlib.util
D=Path(__file__).resolve().parent;R=D.parent.parent;B=R/'outputs/05-linq/final-v17';base=B/'scene.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins={base:'08693593be02034862ffeb2e487ab10ae2f81fc374b33a6493c3d859456cf996',D/'jewelry-v18-frozen-elements.json':'44c8c1c8c30dd509bcc4eef00119ebb533a44a2d732c1b1fbf98df23b325eafc',D/'foodash-v18-frozen-elements.json':'4fcc3d6ad86f995cf97d84ba37c7fa1a761298100156f0b697106f395c50ad4c',D/'games-pop-v18-measure/spec-frozen-v18.json':'dfb3ed92e21716a0a5379ca17e332da997d0653a0427c772bced02ff66f37892',D/'root-boarding-overlay-v18-frozen.json':'0763dfaef3d33b26e0c8e08186f7b95ed1cefffefe9d3024d3ead61fa3b515cc'}
for p,want in pins.items():assert sha(p)==want,(p,sha(p),want)
s=json.loads(base.read_text())
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src'and isinstance(v,str)and not v.startswith(('data:','http:','https:','/')):o[k]=str((B/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
s=module('jewelry',D/'apply-jewelry-v18.py').apply_jewelry(s)
s=module('foodash',D/'apply-foodash-v18.py').apply_foodash(s)
s=module('games',D/'apply_games_pop_v18.py').apply_games_pop(s)
s=module('boarding',D/'apply-root-boarding-overlay-v18.py').apply_boarding(s)
s['rebuildRevision']='final-v18'
s['source']['notes']+=' Final V18 merges four independently validated scopes: Games130–145 restores bounded lower tile materials and label poses while retaining its camera; Jewelry578–650 restores one static upper UI document, measured native entrance, and valid native thread background; Foodash998–1055 corrects measured camera quantization and the independently posed solid original Dillion vector word while preserving product/price/subtotal artwork and state; boarding1200–1219 adds four masked original UI ink/panel-edge materials above the unchanged phone/gallery base and camera. Native full-scope comparisons improve every affected frame. Original rich UI internal text remains bitmap except outlined copy, and exact original curves/materials have not been recovered. No whole-source-frame or source-video layer is introduced.'
ids=[]
def collect(o):
 if isinstance(o,dict):
  if 'id'in o:ids.append(o['id'])
  for v in o.values():collect(v)
 elif isinstance(o,list):
  for q in o:collect(q)
collect(s);assert len(ids)==len(set(ids)),[q for q in ids if ids.count(q)>1]
out=D/'scene-v18-merged.json';out.write_text(json.dumps(s,indent=2)+'\n')
fontEvidence=[]
for old,new in zip(json.loads(base.read_text()).get('fonts',[]),s.get('fonts',[])):
 assert {k:v for k,v in old.items()if k!='src'}=={k:v for k,v in new.items()if k!='src'}
 assert sha(B/old['src'])==sha(new['src']);fontEvidence.append({'family':new.get('family'),'weight':new.get('weight'),'sha256':sha(new['src'])})
(R/'verification/05-v18-composition.json').write_text(json.dumps({'base':str(base),'pins':{str(p):v for p,v in pins.items()},'candidate':str(out),'candidateSHA256':sha(out),'ranges':[[130,145],[578,650],[998,1055],[1200,1219]],'changedFrames':167,'uniqueIDs':len(ids),'fontPropertiesAndBytesPreserved':fontEvidence},indent=2)+'\n')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'uniqueIDs':len(ids),'changedFrames':167}))
