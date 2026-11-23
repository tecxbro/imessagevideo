from pathlib import Path
import hashlib,json,subprocess,io
from PIL import Image,ImageDraw
import numpy as np
p=Path('/tmp/imv-motion-audit.Zz5HS0')
frames=[0,21,23,24,26,98,110,111,113,127,128,129,227,228,234,235,607,827,828,832,940,941,1091,1100,1111,1143,1144,1145,1148,1149,1204,1206,1218,1267,1271,1338,1339,1373,1457]
files={'source':Path('source.mp4'),'GSAP':Path('../../deliverables/05-linq/gsap.mp4'),'Pillow':Path('../../deliverables/05-linq/pillow.mp4')}
w,h=960,720; size=w*h*3
sets={}
for name,file in files.items():
    filters='select='+ '+'.join(f'eq(n\\,{f})' for f in frames)
    cmd=['ffmpeg','-nostdin','-v','error','-xerror','-threads','1','-i',str(file),'-map','0:v:0','-an','-vf',filters,'-fps_mode','passthrough','-pix_fmt','rgb24','-threads','1','-f','rawvideo','-']
    raw=subprocess.check_output(cmd)
    assert len(raw)==len(frames)*size
    with file.open('rb') as media:
        digest=hashlib.file_digest(media,'sha256').hexdigest()
    sets[name]=(digest,np.frombuffer(raw,dtype=np.uint8).reshape(-1,h,w,3))
proof={'files':{name:pair[0] for name,pair in sets.items()},'selection':'zero-based consecutive FFmpeg decode with passthrough output, RGB24','samples':[]}
ref=sets['source'][1]
for i,f in enumerate(frames):
    row={'frame':f}
    for name in ('GSAP','Pillow'):
        delta=np.abs(ref[i].astype(np.int16)-sets[name][1][i].astype(np.int16))
        row[name]={'sourceMAE':float(delta.mean()),'max':int(delta.max())}
    proof['samples'].append(row)
for n,picked in enumerate(([0,21,23,24,26,111,127,128,129,607],[228,234,828,940,1100,1144,1145,1148,1149],[1204,1206,1218,1267,1338,1339,1373,1457]),1):
    sheet=Image.new('RGB',(778,len(picked)*215),'white')
    draw=ImageDraw.Draw(sheet)
    for row,f in enumerate(picked):
        i=frames.index(f)
        for col,(name,(_,a)) in enumerate(sets.items()):
            x=col*259
            im=Image.fromarray(a[i]).resize((256,192),Image.Resampling.LANCZOS)
            sheet.paste(im,(x,row*215+19))
            draw.text((x+2,row*215+2),f'{name} / native frame {f}',fill='#202030')
    sheet.save(p/f'linq-proof-{n}.jpg',quality=84)
(p/'linq-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(f'{len(frames)} native source and archived master samples from each of three files')
