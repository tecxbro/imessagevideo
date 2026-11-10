"""Replace two frames of individually clipped call-edge material only."""
from pathlib import Path
import copy,json
p=Path(__file__).parent

def apply_call_entrance(scene,spec=None):
 scene=copy.deepcopy(scene);spec=spec or json.load(open(p/'entrance-v8-measure/edge-poses-frozen-v8.json'));updated=[]
 for layer in scene['layers']:
  if layer['id'] not in spec['gates']:continue
  keys=layer['keyframes']['opacity'];keys.append({'t':337/30,'value':0,'ease':'hold'});keys.sort(key=lambda k:k['t']);updated.append(layer['id'])
 scene['layers'].extend(copy.deepcopy(spec['nodes']));scene['source']['notes']+=' V8 source337–338 call-edge repair: separately bounded original clipped controls and thin strip material replace false inherited fractional fades/wrong visible edge identity for two frames. Main call bodies, caption, all earlier local3D poses and every339+ state remain unchanged. Bitmap material internals are explicitly declared; no complete scene frame/video is an output layer.'
 return scene,{'scope':[337,338],'updatedEdgeGroups':updated,'newAssets':len(spec['nodes'])}

if __name__=='__main__':
 import sys
 src=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();scene,report=apply_call_entrance(json.load(open(src)))
 def normalize(n):
  if n.get('src') and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((src.parent/n['src']).resolve())
  for c in n.get('children',[]):normalize(c)
 for n in scene['layers']:normalize(n)
 out.write_text(json.dumps(scene,indent=2));(out.parent/'handoff-spec.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
