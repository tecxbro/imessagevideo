"""Fit native label ink using explicit versioned inputs, without overwriting by default."""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image
p=Path(__file__).parent;root=p.parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--scene',type=Path,required=True)
parser.add_argument('--source-png',type=Path,required=True)
parser.add_argument('--candidate-png',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--overwrite',action='store_true')
args=parser.parse_args()
if args.out.exists() and not args.overwrite:parser.error('Output exists; choose a versioned filename or use --overwrite')
source=Image.open(args.source_png).convert('RGB')
candidate=Image.open(args.candidate_png).convert('RGB')
s=json.loads(args.scene.read_text());g=next(l for l in s['layers'] if l.get('start')==10.15 and any(c.get('text')=='Mexican' for c in l.get('children',[])));labels=[l for l in g['children'] if l.get('type')=='text'];rows=[]
def box(im,region):
 crop=im.crop(region);pts=[]
 for y in range(crop.height):
  for x in range(crop.width):
   r,gg,b=crop.getpixel((x,y))
   if b>r+80 and gg>r+40:pts.append((x+region[0],y+region[1]))
 if not pts:raise ValueError('No blue label ink')
 return [min(v[0] for v in pts),min(v[1] for v in pts),max(v[0] for v in pts),max(v[1] for v in pts)]
for i,label in enumerate(labels):
 region=(340,130+i*108,820,240+i*108)
 ref=box(source,region);can=box(candidate,region);sx=(ref[2]-ref[0]+1)/(can[2]-can[0]+1);sy=(ref[3]-ref[1]+1)/(can[3]-can[1]+1)
 x=ref[0]-227-(can[0]-227-label['x'])*sx;y=ref[1]-105-(can[1]-105-label['y'])*sy
 rows.append({'label':label['text'],'id':label['id'],'source_ink_bbox':ref,'candidate_ink_bbox':can,'fit':{'x':x,'y':y,'scaleX':label.get('scaleX',1)*sx,'scaleY':label.get('scaleY',1)*sy}})
report={'source_frame':360,'source_time':360*1001/30000,'inputs':{name:{'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}for name,path in [('scene',args.scene),('source',args.source_png),('candidate',args.candidate_png)]},'method':'Identical blue-ink threshold b>r+80,g>r+40; independent per-label geometry. Parent at12s isx227,y105,scale1. Existing scale transforms retained. No font-advance substitution.','labels':rows};args.out.write_text(json.dumps(report,indent=2));print(str(args.out))
