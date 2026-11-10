#!/usr/bin/env python3
"""Read canonical scenes without retaining dense glyph-outline path strings."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SCENES={'01-photonhq':'outputs/01-photonhq/final-v10/scene.json','02-danieltian':'outputs/02-danieltian/final-v19/scene.json'}
def hash_file(path):
 digest=hashlib.sha256()
 with path.open('rb') as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):
   digest.update(block)
 return digest.hexdigest()

PATTERN=re.compile(r'cursor|pill|composer|send|typing|middle-message|middle-blue|budget-reply|love-it|caret|draft|_uiText',re.I)
for identifier,relative in SCENES.items():
 path=ROOT/relative
 parts=[]
 removed=0
 with path.open() as stream:
  for line in stream:
   if re.match(r'^\s*"d"\s*:',line):
    indent=line[:len(line)-len(line.lstrip())]
    parts.append(indent+'"d": "__geometry_omitted__"'+(',' if line.rstrip().endswith(',') else '')+'\n')
    removed+=len(line)
   else:
    parts.append(line)
 compact=''.join(parts)
 del parts
 scene=json.loads(compact)
 retained=len(compact.encode())
 del compact
 found=[]
 def walk(node,ancestors=(),parent_start=0,parent_end=None):
  if not isinstance(node,dict): return
  start=max(parent_start,float(node.get('start',parent_start)))
  end=min(parent_end if parent_end is not None else scene['duration'],float(node.get('end',parent_end if parent_end is not None else scene['duration'])))
  text=' '.join(str(node.get(k,'')) for k in ['id','text','semanticText','_uiText'])
  if PATTERN.search(text) or any(PATTERN.search(parent) for parent in ancestors):
   record={k:v for k,v in node.items() if k not in ['children','layers','d','src','keyframes']}
   record.update(ancestors=list(ancestors),effective_start=start,effective_end=end)
   if 'keyframes' in node:
    kf=node['keyframes']
    if len(json.dumps(kf))<35000: record['keyframes']=kf
    else: record['keyframe_summary']={key:{'count':len(value),'first':value[0] if value else None,'last':value[-1] if value else None} for key,value in kf.items()}
   found.append(record)
  for child in node.get('children',[]): walk(child,ancestors+(node.get('id','?'),),start,end)
 for root in scene['layers']:walk(root)
 result={'id':identifier,'canonical_scene':relative,'canonical_scene_sha256':hash_file(path),'fps':scene['fps'],'frames':round(scene['fps']*scene['duration']),'read_strategy':{'dense_path_bytes_discarded':removed,'stripped_json_bytes_retained':retained,'canonical_copied':False},'matches':found}
 (OUT/f'{identifier[:2]}-scene-ui-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'id':identifier,'matches':len(found),'stripped_bytes':retained,'root_ids':[x.get('id') for x in found if not x['ancestors']][:24]},separators=(',',':')))
 del scene,result,found
