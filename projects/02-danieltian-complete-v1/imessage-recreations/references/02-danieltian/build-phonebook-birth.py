"""Measure the five-frame phone-field birth as independently bounded text elements."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path('/workspace/imessage-recreations');REF=ROOT/'references/02-danieltian';P=ROOT/'verification/fidelity-review/02-birth';AS=REF/'assets/phonebook-birth';AS.mkdir(exist_ok=True)
seg=json.loads((P/'source-segmentation.json').read_text());plus={q['frame']:q for q in json.loads((P/'plus-segmentation.json').read_text())};layers=[];assets=[];counts={}
for q in seg:
 f=q['frame'];a=np.array(Image.open(P/f'source-{f}.png').convert('RGB'));g=a.mean(2);children=[]
 for ri,row in enumerate(q['rows']):
  y0,y1=row['y'];m=g[y0:y1]<(160 if f==415 else 245);prefixes=sorted(p[0] for p in plus[f]['rows'][ri]['pluses'])
  # This plus is connected to the preceding number during the squeezed launch.
  # Disjoint source-cell partitions preserve the overlap, without duplicating ink.
  if f==419 and ri==4:prefixes.append(962);prefixes.sort()
  xmin=int(np.where(m.any(0))[0][0]);boundaries=[0]
  for j,x in enumerate(prefixes):
   if j>0 or xmin<x-10:boundaries.append(max(0,x-3))
  boundaries.append(1920)
  for ci,(lo,hi) in enumerate(zip(boundaries,boundaries[1:])):
   xs=np.where(m[:,lo:hi].any(0))[0]+lo
   if not len(xs):continue
   # Isolate a newly born, almost invisible frontier fragment, rather than putting
   # hundreds of background pixels into a larger neighboring cell texture.
   cuts=[0]+[i+1 for i,v in enumerate(np.diff(xs)) if v>100]+[len(xs)]
   for fi,(ca,cb) in enumerate(zip(cuts,cuts[1:])):
    x0,x1=int(xs[ca]),int(xs[cb-1]+1);tight=m[:,x0:x1];yy=np.where(tight.any(1))[0];gy0,gy1=y0+int(yy.min()),y0+int(yy.max()+1);box=[max(0,x0-2),max(0,gy0-2),min(1920,x1+2),min(1080,gy1+2)];bx0,by0,bx1,by1=box
    # The transparent artwork contains glyph ink only; its small rectangle is not
    # an opaque source screenshot. Partition masks are disjoint at cell boundaries.
    ink=np.clip((253-g[by0:by1,bx0:bx1])/253,0,1);strong=(g[by0:by1,bx0:bx1]<(160 if f==415 else 245));mask=ndimage.binary_dilation(strong,iterations=2);xx=np.arange(bx0,bx1)[None,:];mask&=(xx>=max(lo,x0-2))&(xx<min(hi,x1+2));rgba=np.zeros((*ink.shape,4),np.uint8);rgba[:,:,3]=np.uint8(np.round(ink*mask*255))
    name=f'f{f}-r{ri}-c{ci}-p{fi}';path=AS/(name+'.png');Image.fromarray(rgba).save(path);assets.append(dict(file=str(path.relative_to(REF)),source_frame=f,source_bounds=box,source_cell_partition=[lo,y0,hi,y1],purpose='Bounded original phone glyph/cell pose for five-frame staggered birth; internal copy is bitmap, native placement/lifetime editable.',sha256=hashlib.sha256(path.read_bytes()).hexdigest()));children.append(dict(type='image',id='pb-birth-'+name,src=str(path.relative_to(REF)),x=bx0,y=by0,width=bx1-bx0,height=by1-by0))
 layers.append(dict(type='group',id=f'pb-birth-frame-{f}',start=f/30,end=(f+1)/30,children=children));counts[f]=len(children)
base=json.loads((REF/'scene-birth-base-v8.json').read_text());targets=[l['id'] for l in base['layers'] if l.get('type')=='image' and l['id'].startswith(('pb-early-','pb-number-')) and l.get('start',0)<14]
spec=dict(changed_frame_ranges=[[415,419]],gate_existing_ids=targets,gate_start=14,layers=layers,source_frame_element_counts=counts,assets=assets,notice='Five native launch frames only. Source-derived bounded text/cell pose artwork; no source-video or complete-frame runtime asset. The almost invisible frontier fragments and one overlapping plus are partitioned separately. Existing query/Uber/affine/glyph/endcard work is preserved.')
(REF/'phonebook-birth-elements.json').write_text(json.dumps(spec,indent=2));print(json.dumps(dict(target_count=len(targets),element_counts=counts,assets=len(assets)),indent=2))
