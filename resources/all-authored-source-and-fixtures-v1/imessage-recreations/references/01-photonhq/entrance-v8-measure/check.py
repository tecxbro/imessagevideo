from pathlib import Path
import json,sys,numpy as np
from PIL import Image,ImageDraw
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));import render_pillow as rp
p=root/'references/01-photonhq/entrance-v8-measure';s=json.load(open(p/'candidate.scene.json'));rp.register_fonts(s,str(p));rows=[]
for f in (336,337,338):
 image=rp.render(s,f/30,str(p));image.save(p/f'{f}-candidate.png');src=Image.open(root/'references/01-photonhq/wall-v6-measure/wall'/f'{f-335:03}.png').convert('RGB');old=Image.open(root/'outputs/01-photonhq/cache/motion-canvas'/f'{f:06}.png').convert('RGB');a=np.array(src,dtype=float);r={'frame':f,'old':float(np.abs(a-np.array(old,dtype=float)).mean()),'new':float(np.abs(a-np.array(image,dtype=float)).mean())};print(r,flush=True);rows.append(r);sheet=Image.new('RGB',(1440,296),'#dddddd');d=ImageDraw.Draw(sheet)
 for col,(name,img) in enumerate([('source',src),('V7',old),('candidate',image)]):sheet.paste(img.resize((480,270)),(480*col,26));d.text((480*col+8,6),f'{f} {name}',fill='black')
 sheet.save(p/f'{f}-contact.jpg');(p/'native-metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
