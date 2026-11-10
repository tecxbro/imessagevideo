from pathlib import Path
from PIL import Image
import json,shutil,hashlib,os,subprocess
R=Path('verification/encode-range');inputs={'535':Path('verification/fidelity-review/02-capsule-collapse/check-v2-gsap/17.833.png'),'126':Path('outputs/02-danieltian/root-copy-check-v3/4.200.png'),'885':Path('outputs/02-danieltian/frames-gsap/000885.png')};records=[]
for name,p in inputs.items():
 target=R/'inputs'/f'{name}.png';shutil.copyfile(p,target);records.append(dict(id=name,source=str(p.resolve()),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
im=Image.new('RGB',(1920,1080));patches=[]
for v in range(256):
 x=(v%16)*120;y=(v//16)*32;im.paste((v,v,v),(x,y,x+120,y+32));patches.append(dict(name=f'gray-{v}',rgb=[v]*3,box=[x,y,x+120,y+32]))
colors=['000000','010101','080808','101010','202020','404040','808080','c0c0c0','ececec','f0f0f0','f8f8f8','fcfcfc','fdfdfd','fefefe','ffffff','3ca4f9','1688ff','0084ff','55c2f3','007aff','32c859','00c853','00ff00','ff0000','0000ff','ffff00','ff00ff','00ffff','ff9500','af52de','ff2d55','8e8e93']
for i,c in enumerate(colors):
 x=i%8*240;y=512+i//8*142;rgb=tuple(bytes.fromhex(c));im.paste(rgb,(x,y,x+240,y+142));patches.append(dict(name=f'color-{c}',rgb=list(rgb),box=[x,y,x+240,y+142]))
im.save(R/'inputs/palette.png');(R/'palette-patches.json').write_text(json.dumps(patches,indent=2));records.append(dict(id='palette',source='Synthetic native gray256-level/color32-patch PNG',sha256=hashlib.sha256((R/'inputs/palette.png').read_bytes()).hexdigest()))
for j,name in enumerate(['535','126','885','palette']):
 for k in range(6):
  p=R/'sequence'/f'{j*6+k:06d}.png'
  if p.exists():p.unlink()
  os.link(R/'inputs'/f'{name}.png',p)
(R/'inputs.json').write_text(json.dumps(dict(cadence=30,frames=24,duration=.8,phases=[dict(id=n,frames=[j*6,j*6+5],sampleFrame=j*6+2,sampleTime=(j*6+2)/30) for j,n in enumerate(['535','126','885','palette'])],inputs=records),indent=2))
for n in [126,535,885]:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-i','references/02-danieltian/source.mp4','-vf',f'select=eq(n\\,{n})','-frames:v','1',str(R/'reference'/f'{n}.png')],check=True)
print('Prepared immutable4-phase24-frame30fps codec experiment inputs',flush=True)
