#!/usr/bin/env python3
"""Report text characters absent from a scene's chosen declared primary font."""
from pathlib import Path
import json,argparse,collections
from fontTools.ttLib import TTFont
p=argparse.ArgumentParser();p.add_argument('scenes',nargs='+',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();reports=[]
for source in a.scenes:
 scene=json.loads(source.read_text());fonts=collections.defaultdict(list)
 for spec in scene.get('fonts',[]):
  path=(source.parent/spec['src']).resolve();font=TTFont(path,lazy=True);cmap=set(font.getBestCmap());font.close();weight=spec.get('weight',400);weight=400 if weight=='normal' else 700 if weight=='bold' else int(weight);fonts[spec['family'].strip("'\"")].append((weight,cmap,str(path)))
 def walk(ls):
  for l in ls:
   if l.get('type')=='text':
    family=l.get('fontFamily','').split(',')[0].strip().strip("'\"");choices=fonts.get(family,[])
    if choices:
     weight=l.get('fontWeight',400);weight=400 if weight=='normal' else 700 if weight=='bold' else int(weight);chosen=min(choices,key=lambda r:(abs(r[0]-weight),-r[0]));missing=sorted(c for c in set(l.get('text',''))-set('\n\r\t ') if ord(c) not in chosen[1])
     if missing:reports.append({'scene':str(source),'layer':l['id'],'text':l.get('text'),'family':family,'weight':chosen[0],'font':chosen[2],'missing':[{'character':c,'unicode':f'U+{ord(c):04X}'} for c in missing]})
   walk(l.get('children',[]))
 walk(scene['layers'])
result={'notice':'Primary-font coverage diagnostic. A declared CSS fallback may render these characters; inspect native glyph appearance before changing a font. This is not a universal rendering failure.','issues':reports};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2));print(json.dumps({'textLayersWithPrimaryFontGaps':len(reports),'report':str(a.out)}))
