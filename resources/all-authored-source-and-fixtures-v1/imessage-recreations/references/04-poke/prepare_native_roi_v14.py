"""Native source/candidate detail pairs; exact original frame IDs, no downscale."""
from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
p=Path(__file__).parent;root=p.parent.parent;out=root/'outputs/04-poke/qa-v14-native-regions';out.mkdir(exist_ok=True);rows=[]
regions=[('phone-header-758',758,[400,0,1100,400]),('audio-keyboard-834',834,[250,300,1150,1080]),('date-title-214',214,[230,530,760,625]),('grid-1173',1173,[650,250,1440,550]),('logo-55',55,[430,160,1010,720]),('restaurant-575',575,[570,570,1180,1080]),('intro-sydney-108',108,[1080,180,1440,760]),('intro-braden-108',108,[0,200,370,760])]
for name,n,box in regions:
 source=p/f'measurements-v8/decoded/{n:06}.png';candidate=root/f'outputs/retained-frames/measured-frames-jRBOzF/{n:06}.png'
 if not source.exists():raise ValueError('Missing exact source PNG '+str(source))
 a=Image.open(source).convert('RGB').crop(box);b=Image.open(candidate).convert('RGB').crop(box);d=abs(np.array(a).astype(np.int16)-np.array(b).astype(np.int16));sheet=Image.new('RGB',(a.width*2,a.height+22),'white');sheet.paste(a,(0,22));sheet.paste(b,(a.width,22));ImageDraw.Draw(sheet).text((3,3),f'{name}: original | native V14 candidate. Native crop; MAE {d.mean():.5f}',fill='black');sheet.save(out/(name+'.png'));rows.append(dict(name=name,source_frame=n,box=box,native_roi_mae=float(d.mean()),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),candidate_png_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),candidate_scene_sha256='7764ad5269f142c6ccd4275751d491ec117f8f350ffc613bef252c0ad02612bd'))
(out/'regions.json').write_text(json.dumps(rows,indent=2));print([(r['name'],r['native_roi_mae'])for r in rows])
