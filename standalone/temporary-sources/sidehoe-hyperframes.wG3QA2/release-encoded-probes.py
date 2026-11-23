from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

scratch = Path('/tmp/sidehoe-hyperframes.wG3QA2')
repo = Path('sidehoe-skill-trial')
source = Path('/Users/darshan/Downloads/sidehoe.mp4')
before = repo/'finish'/'sidehoe.mp4'
after = repo/'hyperframes-review'/'candidate'/'sidehoe.mp4'
focus = [
    (22,(230,365,1710,1530),'inbox'), (53,(0,0,2000,2000),'inbox-scroll'), (355,(0,0,2000,2000),'sofia-handoff'), (357,(0,0,2000,2000),'sofia-release'),
    (106,(680,650,1320,1320),'profile'),
    (111,(680,650,1320,1320),'profile-settle'),
    (138,(0,0,2000,2000),'handset-entrance'),
    (150,(0,0,2000,2000),'handset-hold'),
    (158,(0,0,2000,2000),'handset-exit'),
    (184,(370,870,1630,1270),'heart-entrance'),
    (191,(365,790,1635,1180),'type-and-hearts'),
    (205,(355,650,1650,1060),'heart-exit'),
    (400,(250,1150,1690,2000),'calendar-before'),
    (401,(250,1090,1720,1850),'calendar-overlap'),
    (402,(250,960,1720,1710),'calendar-after'),
    (610,(738,1040,1250,1625),'tile-approach'),
    (612,(738,1090,1250,1655),'tile-face'),
    (616,(738,1245,1250,1830),'tile-start-exit'),
    (621,(738,1650,1250,2000),'tile-end-exit'),
    (622,(738,1650,1250,2000),'tile-control'),
    (670,(715,915,1335,1425),'cursor-approach'),
    (675,(710,880,1300,1400),'cursor-contact'),
    (686,(710,860,1290,1360),'cursor-hold'),
    (694,(720,875,1300,1345),'cursor-withdrawal'),
    (695,(720,875,1300,1345),'cursor-tail'),
]
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 17)
out = scratch/'release-encoded-probes'
out.mkdir(exist_ok=True)
frames = [f for f,_box,_label in focus]
selector = '+'.join(f'eq(n\\,{f})' for f in frames)
for idx,clip in enumerate((source,before,after)):
    target = out/str(idx)
    target.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-i',str(clip),
        '-vf',f'select={selector}', '-an','-fps_mode','passthrough',
        '-start_number','0',str(target/'%02d.png')],check=True)
results=[]
for k,(f,region,label) in enumerate(focus):
    views = [Image.open(out/str(j)/f'{k:02}.png').convert('RGB').crop(region) for j in range(3)]
    native = [np.asarray(im,dtype=np.int16) for im in views]
    old_abs = np.abs(native[0]-native[1])
    new_abs = np.abs(native[0]-native[2])
    results.append((f, label, round(float(old_abs.mean()),5), round(float(new_abs.mean()),5)))
    for im in views:
        im.thumbnail((480,600),Image.Resampling.LANCZOS)
    w,h=views[0].size
    board=Image.new('RGB',(w*3,h+33),'#13141a')
    d=ImageDraw.Draw(board)
    for j,(name,im) in enumerate(zip(('Source','Previous','Revised'),views)):
        board.paste(im,(j*w,33))
        d.text((j*w+10,7),f'{name}  ·  f{f}  /  {f/25:.2f} s',font=font,fill='white')
    board.save(out/f'f{f:03}-{label}.png')
print(*results, sep='\n')
