"""Correct the one-frame early Four in a Row frontier; retain later accepted poses."""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();src=a.input.resolve();scene=json.loads(src.read_text())
def absolute(l):
 if l.get('src') and not l['src'].startswith(('data:','http:','https:')):l['src']=str((src.parent/l['src']).resolve())
 for c in l.get('children',[]):absolute(c)
for l in scene['layers']:
 absolute(l)
 if l['id']=='rich-group-10':
  l['start']=940/30;l['keyframes']['x']=[{'t':940/30,'value':914.0}]+[r for r in l['keyframes']['x'] if r['t']>940/30]
for f in scene.get('fonts',[]):
 if not f['src'].startswith(('data:','http:','https:')):f['src']=str((src.parent/f['src']).resolve())
scene['root_four_handoff']={'scope':[[940,940]],'cause':'The source already shows46pixels of Four in a Row at frame940; old start941 omitted that entire entering frontier. Later accepted poses and native counters remain unchanged.'};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(scene,indent=2));print(a.output)
