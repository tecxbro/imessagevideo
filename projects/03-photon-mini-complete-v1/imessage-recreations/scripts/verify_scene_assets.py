#!/usr/bin/env python3
"""Decode the assets actually referenced by scenes; reject invisible image mistakes."""
from pathlib import Path
import argparse,json,hashlib,io,base64
from PIL import Image
from fontTools.ttLib import TTFont

def main():
 p=argparse.ArgumentParser();p.add_argument('scenes',nargs='+',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();records={};errors=[];warnings=[]
 def check(src,base,node,kind,allow_empty=False):
  if src.startswith(('https://','http://')):errors.append({'node':node,'error':'Remote dependency is not a reproducible local asset','src':src});return
  if src.startswith('data:'):
   header,value=src.split(',',1);raw=base64.b64decode(value);name='embedded:'+hashlib.sha256(raw).hexdigest()
  else:
   path=(base/src).resolve();name=str(path)
   try:raw=path.read_bytes()
   except Exception as e:errors.append({'node':node,'error':str(e),'src':name});return
  if name in records:records[name]['nodes'].append(node);return
  rec={'kind':kind,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'nodes':[node]};records[name]=rec
  try:
   if kind=='font':
    f=TTFont(io.BytesIO(raw),lazy=True);rec.update(family=f['name'].getDebugName(1),style=f['name'].getDebugName(2));f.close()
   else:
    im=Image.open(io.BytesIO(raw));im.load();rec.update(size=list(im.size),mode=im.mode)
    if 'A' in im.getbands():
     alpha=im.getchannel('A');rec['alpha_extrema']=list(alpha.getextrema());rec['visible_bbox']=alpha.getbbox()
     if rec['visible_bbox'] is None and not allow_empty:errors.append({'node':node,'error':'Fully transparent image: no visible component','src':name})
    channels=im.convert('RGB').getextrema();rec['rgb_extrema']=channels
    alpha_varies='alpha_extrema' in rec and rec['alpha_extrema'][0]!=rec['alpha_extrema'][1]
    if not alpha_varies and all(hi-lo<=1 for lo,hi in channels):warnings.append({'node':node,'warning':'Uniform image; verify that this is intentional artwork/background','src':name})
  except Exception as e:errors.append({'node':node,'error':'Asset decode failed: '+str(e),'src':name})
 def walk(layers,base,scene):
  for l in layers:
   if l.get('type')=='image':check(l['src'],base,scene+':'+l['id'],'image',l.get('allowEmptyImage',False))
   for k in l.get('keyframes',{}).get('src',[]):check(k['value'],base,scene+':'+l['id']+'@'+str(k['t']),'image')
   walk(l.get('children',[]),base,scene)
 for path in a.scenes:
  s=json.loads(path.read_text());walk(s['layers'],path.resolve().parent,str(path))
  for f in s.get('fonts',[]):check(f['src'],path.resolve().parent,str(path)+':font:'+f['family'],'font')
 result={'scenes':list(map(str,a.scenes)),'assets_checked':len(records),'errors':errors,'warnings':warnings,'assets':records};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2));print(json.dumps({'assets_checked':len(records),'errors':errors,'warning_count':len(warnings),'report':str(a.out)},indent=2));return bool(errors)
if __name__=='__main__':raise SystemExit(main())
