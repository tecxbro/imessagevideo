#!/usr/bin/env python3
"""Make a content-addressed immutable render input snapshot and provenance ledger."""
import argparse,hashlib,json,shutil,gzip
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('scene');p.add_argument('destination');a=p.parse_args();source=Path(a.scene).resolve();raw=gzip.decompress(source.read_bytes()) if source.suffix=='.gz' else source.read_bytes();scene=json.loads(raw);dest=Path(a.destination).resolve();dest.mkdir(parents=True,exist_ok=True);assets=[]
 def copy_asset(src):
  if src.startswith('data:'):return src
  if src.startswith(('http://','https://')):raise ValueError('Remote asset cannot form reproducible snapshot: '+src)
  path=(source.parent/src).resolve();data=path.read_bytes();digest=hashlib.sha256(data).hexdigest();name=path.name if path.name.startswith(digest[:16]+'-') else digest[:16]+'-'+path.name;relative=Path('assets')/name;target=dest/relative;target.parent.mkdir(exist_ok=True);target.write_bytes(data);assets.append({'original':str(path),'snapshot':str(relative),'sha256':digest,'bytes':len(data)});return str(relative)
 def walk(layers):
  for layer in layers:
   if layer.get('src'):layer['src']=copy_asset(layer['src'])
   walk(layer.get('children',[]))
 walk(scene['layers'])
 for font in scene.get('fonts',[]):font['src']=copy_asset(font['src'])
 manifest=json.dumps(scene,indent=2)+'\n';(dest/'scene.json').write_text(manifest);(dest/'snapshot.json').write_text(json.dumps({'original':str(source),'original_sha256':hashlib.sha256(raw).hexdigest(),'snapshot_sha256':hashlib.sha256(manifest.encode()).hexdigest(),'assets':assets},indent=2)+'\n');print(dest/'scene.json')
if __name__=='__main__':main()
