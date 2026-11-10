"""Scoped source01 free-zoom/wall trajectory corrections from immutablev5."""
from pathlib import Path
import copy,json,re,hashlib
import numpy as np
P=Path(__file__).parent;B=P/'wall-v6-measure';ROOT=P.parents[1]
def scaled_path(d,scale):return re.sub(r'-?\d+(?:\.\d+)?',lambda m:f'{float(m.group())*scale:.5f}',d)
def contour_groups(d):
 contours=[]
 for part in re.split(r'(?=M)',d):
  if not part.strip():continue
  xy=np.array([float(v)for v in re.findall(r'-?\d+(?:\.\d+)?',part)]).reshape(-1,2);contours.append({'d':part,'box':[float(xy[:,0].min()),float(xy[:,1].min()),float(xy[:,0].max()),float(xy[:,1].max())]})
 groups=[]
 for c in sorted(contours,key=lambda c:c['box'][0]):
  if groups and c['box'][0]<=groups[-1]['box'][2]+1:
   g=groups[-1];g['d']+=' '+c['d'];g['box']=[min(g['box'][0],c['box'][0]),min(g['box'][1],c['box'][1]),max(g['box'][2],c['box'][2]),max(g['box'][3],c['box'][3])]
  else:groups.append(copy.deepcopy(c))
 return groups

def apply_free(scene):
 s=copy.deepcopy(scene);g=next(l for l in s['layers'] if l['id']=='group-27');original=next(l for l in g['children'] if l['type']=='path');fits=json.loads((B/'free-camera-fit.json').read_text())['measurements'];blue=json.loads((B/'free-blue-vector.json').read_text());unit=16;children=[]
 for i,c in enumerate(contour_groups(original['d'])):
  tracks={k:[]for k in ['x','y','scaleX','scaleY','opacity']}
  for q in fits:
   x1,y1,x2,y2=c['box'];visible=q['x']+x2*q['scaleX']>-64 and q['x']+x1*q['scaleX']<1984 and q['y']+y2*q['scaleY']>-64 and q['y']+y1*q['scaleY']<1144
   for k in tracks:tracks[k].append({'t':q['frame']/30,'value':int(visible) if k=='opacity' else q[k]/unit if k.startswith('scale') else q[k],'ease':'hold' if k=='opacity' else 'linear'})
  children.append({'id':f'free-black-glyph-v6-{i}','type':'path','d':scaled_path(c['d'],unit),'fill':'#000000','keyframes':tracks,'semanticText':'Original black title glyph group','authoringUnitsPerCanvasUnit':unit})
 tracks={k:[{'t':q['frame']/30,'value':q[k]/unit if k.startswith('scale') else q[k],'ease':'linear'}for q in blue['measurements']]for k in ['x','y','scaleX','scaleY']}
 children.append({'id':'free-blue-native-outline-v6','type':'path','d':scaled_path(blue['d'],unit),'fill':'url(#measured-free-gradient-v6)','keyframes':tracks,'semanticText':'free','authoringUnitsPerCanvasUnit':unit,'editability':'Native original glyph outlines and sampled native gradient; fine source grain is approximated.'})
 g.update(x=0,y=0,originX=0,originY=0,start=240/30,end=249/30,opacity=1,keyframes={},children=children)
 s.setdefault('gradients',[]).append(blue['gradient']);s['source']['notes']+=' V6 free zoom uses actual per-frame native glyph projection (final16.34x, not10x extrapolation), native blue outlines/gradient and independent black glyphs. Fine original grain is approximated by native gradient. Sourceframes240–248 only.'
 return s

def apply_walls(scene):
 s=copy.deepcopy(scene);layers=json.loads((B/'wall-native-layers.json').read_text());caption_fits=json.loads((B/'caption-projection-fits.json').read_text());gates=[];caption_layers=[]
 for layer in s['layers']:
  if layer['id'].startswith(('ocr-wall-', 'edge-restore-')):
   keys=layer.setdefault('keyframes',{}).setdefault('opacity',[])
   # The settled source336–338 native body already fits. Preserve it; replace
   # actual card-state exits from339, then restore baseline at465.
   keys[:]=[k for k in keys if k['t']<339/30 or k['t']>465/30]
   keys.extend([{'t':339/30,'value':0,'ease':'hold'},{'t':465/30,'value':1,'ease':'hold'}]);keys.sort(key=lambda k:k['t']);gates.append(layer['id'])
  if layer['id'].startswith('source-heading-word-'):
   phase=next((p for p in ['calls','imessage','whatsapp','telegram'] if layer['id'].startswith('source-heading-word-'+p+'-')),None)
   if phase:
    start,end={'calls':(336,355),'imessage':(355,390),'whatsapp':(390,425),'telegram':(425,465)}[phase]
    fitted=copy.deepcopy(layer) if phase=='calls' else layer
    if phase=='calls':
     # Isolate this interval so new first fit cannot change interpolation in335.
     layer['end']=336/30;fitted['id']+='-measured-v6';caption_layers.append(fitted)
    fitted['start']=start/30;fitted['end']=end/30;fitted['opacity']=1;fitted['keyframes']=copy.deepcopy(caption_fits[layer['id']]);fitted['editability']='Native original semantic word outline with measured per-frame transform and hard lifecycle cut.'
 layers=[l for l in layers if l['end']>339/30]
 for l in layers:l['start']=max(l['start'],339/30)
 s['layers'].extend(layers+caption_layers)
 s['source']['notes']+=' V6 source339–464 wall cards use independent bounded original artwork, per-frame editable native transforms and exact opaque lifetimes. Previous OCR loss was incorrectly rendered as opacity/vertical collapse. Material masks exclude neighboring components; bitmap internal copy is explicitly declared. Native caption projections336–464 include exact hard edits355,390,425 and the late upward exit.'
 return s,{'scope':[[339,464]],'caption_scope':[[336,464]],'legacy_gates':gates,'cards':len(layers),'caption_hard_edits':[355,390,425]}

def absolute_assets(s,base):
 def walk(ls):
  for l in ls:
   if l.get('src') and not l['src'].startswith('data:'):l['src']=str((base/l['src']).resolve())
   walk(l.get('children',[]))
 walk(s['layers'])
 for f in s.get('fonts',[]):
  if not f['src'].startswith('data:'):f['src']=str((base/f['src']).resolve())
 return s
if __name__=='__main__':
 base=ROOT/'outputs/01-photonhq/final-v5/scene.json';scene=absolute_assets(json.loads(base.read_text()),base.parent);scene=apply_free(scene);scene,proof=apply_walls(scene);(B/'scope.json').write_text(json.dumps(proof,indent=2)+'\n');out=P/'wall-v6.scene.json';out.write_text(json.dumps(scene,indent=2)+'\n');print(out)
