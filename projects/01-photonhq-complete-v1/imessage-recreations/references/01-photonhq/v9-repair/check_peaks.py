from pathlib import Path
import json,sys,numpy as np
from PIL import Image,ImageDraw
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));import render_pillow as rp
p=root/'references/01-photonhq/v9-repair';s=json.load(open(p/'candidate.scene.json'));rp.register_fonts(s,str(p));rows=[]
for f in (250,256,257,260,300,307):
 source=Image.open(root/'references/01-photonhq/early-walls-v7-measure'/f'frame-{f-(248 if f<282 else 263):03}.png').convert('RGB');old=Image.open(root/f'outputs/01-photonhq/cache/pillow/{f:06}.png').convert('RGB');new=rp.render(s,f/30,str(p));new.save(p/f'{f}-candidate.png');a=np.array(source,dtype=float);r={'frame':f,'old':float(np.abs(a-np.array(old,dtype=float)).mean()),'new':float(np.abs(a-np.array(new,dtype=float)).mean()),'oldNewMax':int(np.abs(np.array(old,dtype=int)-np.array(new,dtype=int)).max())};rows.append(r);print(r,flush=True);(p/'peak-metrics.json').write_text(json.dumps(rows,indent=2)+'\n');sheet=Image.new('RGB',(1440,296),'#dddddd');d=ImageDraw.Draw(sheet)
 for col,(label,img) in enumerate([('source',source),('V8 native',old),('V9 candidate',new)]):sheet.paste(img.resize((480,270)),(480*col,26));d.text((480*col+8,6),f'{f} {label}',fill='black')
 sheet.save(p/f'{f}-contact.jpg')
