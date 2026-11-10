"""Compare actual native checkpoint PNGs against immutable source and v10cache."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,argparse,hashlib
parser=argparse.ArgumentParser();parser.add_argument('directory');parser.add_argument('--sheet',default='');args=parser.parse_args();root=Path(__file__).parent.parent.parent;out=Path(args.directory);out=out if out.is_absolute()else root/out;rows=[];pairs=[];selected=set(int(v)for v in args.sheet.split(',')if v)
for q in sorted(out.glob('*.png')):
    source=root/'references/04-poke/measurements-v8/decoded'/q.name
    if not source.exists():continue
    reference=root/'outputs/retained-frames/measured-frames-jRBOzF'/q.name
    a=np.array(Image.open(source).convert('RGB')).astype(np.int16);b=np.array(Image.open(reference).convert('RGB')).astype(np.int16);c=np.array(Image.open(q).convert('RGB')).astype(np.int16)
    row=dict(frame=int(q.stem),v10=float(abs(a-b).mean()),candidate=float(abs(a-c).mean()),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(q.read_bytes()).hexdigest());rows.append(row)
    if int(q.stem)in selected:
        im=Image.new('RGB',(1440,380),'white');ImageDraw.Draw(im).text((2,2),str({k:row[k]for k in['frame','v10','candidate']}),fill='black')
        for i,v in enumerate([a,b,c]):im.paste(Image.fromarray(v.astype('uint8')).resize((480,360)),(480*i,20))
        pairs.append(im)
(out/'metrics.json').write_text(json.dumps(rows,indent=2))
if pairs:
    im=Image.new('RGB',(1440,380*len(pairs)),'white')
    for i,v in enumerate(pairs):im.paste(v,(0,380*i))
    im.save(out/'review.jpg')
print(json.dumps([{k:r[k]for k in['frame','v10','candidate']}for r in rows],indent=2))
