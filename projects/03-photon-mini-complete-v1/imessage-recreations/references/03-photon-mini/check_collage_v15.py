from pathlib import Path
import sys,json,copy
import numpy as np
from PIL import Image,ImageDraw
p=Path(__file__).parent;sys.path.insert(0,str(p.parent.parent/'engines'));sys.path.insert(0,str(p))
import render_pillow as rp
from apply_collage_cameras_v15 import build_spec,apply_collage_cameras
out=p/'collage-v15-measure';src=(p.parent.parent/'outputs/03-photon-mini/final-v14/scene.json').resolve();s=json.load(open(src));rows=json.load(open(out/'source-feature-tracks.json'));spec=build_spec(s,rows);(out/'camera-spec-working.json').write_text(json.dumps(spec,indent=2));s=apply_collage_cameras(s,spec);rp.register_fonts(s,str(src.parent));metrics=[]
selected=range(903,975) if '--all' in sys.argv else [903,930,932,948]
(out/'native-combined-frames').mkdir(exist_ok=True)
for f in selected:
 a=np.array(Image.open(p/'collage-native'/f'{f-890:03}.png').convert('RGB'),dtype=float);image=rp.render(s,f/30,str(src.parent));image.save(out/'native-combined-frames'/f'{f:04}.png');b=np.array(image,dtype=float);old=np.array(Image.open(p.parent.parent/'outputs/03-photon-mini/frames-gsap'/f'{f:06}.png').convert('RGB'),dtype=float);r={'frame':f,'old':float(np.abs(a-old).mean()),'new':float(np.abs(a-b).mean())};metrics.append(r);print(r,flush=True)
 sheet=Image.new('RGB',(1440,296),'#dddddd');d=ImageDraw.Draw(sheet)
 for i,(name,im) in enumerate([('source',Image.fromarray(a.astype('uint8'))),('V14',Image.fromarray(old.astype('uint8'))),('native-cameras',image)]):sheet.paste(im.resize((480,270)),(i*480,26));d.text((i*480+8,6),f'{f} {name}',fill='black')
 sheet.save(out/f'combined-{f}-contact.jpg');(out/('all72-metrics.json' if '--all' in sys.argv else 'combined-peak-metrics.json')).write_text(json.dumps(metrics,indent=2))
