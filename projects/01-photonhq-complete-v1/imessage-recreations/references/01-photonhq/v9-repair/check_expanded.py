from pathlib import Path
import json,sys,time,numpy as np
from PIL import Image,ImageDraw
root=Path('/workspace/imessage-recreations');sys.path.insert(0,str(root/'engines'));import render_pillow as rp
p=root/'references/01-photonhq/v9-repair';s=json.load(open(p/'candidate-expanded.scene.json'));rp.register_fonts(s,str(p));rows=[];frames=list(range(250,260))+[249,260];out=p/'expanded-native';out.mkdir(exist_ok=True)
for f in frames:
 started=time.monotonic();source=Image.open(root/'references/01-photonhq/early-walls-v7-measure'/f'frame-{f-(248 if f<282 else 263):03}.png').convert('RGB');old=Image.open(root/f'outputs/01-photonhq/cache/pillow/{f:06}.png').convert('RGB');new=rp.render(s,f/30,str(p));new.save(out/f'{f:04}.png');a=np.array(source,dtype=float);r={'frame':f,'old':float(np.abs(a-np.array(old,dtype=float)).mean()),'new':float(np.abs(a-np.array(new,dtype=float)).mean()),'oldNewMax':int(np.abs(np.array(old,dtype=int)-np.array(new,dtype=int)).max()),'seconds':time.monotonic()-started};rows.append(r);print(r,flush=True);(p/'expanded-metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
 if f in (250,253,256,257,259,297,299,300,301,307,310,314):
  sheet=Image.new('RGB',(1440,296),'#dddddd');d=ImageDraw.Draw(sheet)
  for col,(label,img) in enumerate([('source',source),('V8 native',old),('V9 candidate',new)]):sheet.paste(img.resize((480,270)),(480*col,26));d.text((480*col+8,6),f'{f} {label}',fill='black')
  sheet.save(out/f'{f:04}-contact.jpg')
