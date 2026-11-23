import os, subprocess
from PIL import Image, ImageDraw
from pathlib import Path
dest=Path('sidehoe-recreation/evidence')
windows={
'01-opening':(0,12,(175,225,1450,1580)), '02-scroll':(43,69,(200,0,1450,1960)),
'03-identity':(98,118,(560,550,940,1000)), '04-assistant':(130,165,(105,300,1790,1700)),
'05-title':(174,187,(390,680,1250,620)), '06-cluster':(210,226,(90,330,1820,1400)),
'07-mosaic':(251,273,(110,375,1760,1200)), '08-lisa':(282,313,(120,565,1640,1110)),
'09-phone':(313,342,(0,0,2000,2000)), '10-suggestion':(334,360,(0,300,2000,1700)),
'11-send':(382,406,(580,500,1250,1480)), '12-cal-in':(400,423,(110,320,1810,1090)),
'13-cal-maria':(427,443,(225,660,1550,550)), '14-cal-lisa':(447,462,(225,660,1550,700)),
'15-cal-out':(470,487,(100,380,1810,1250)), '16-orbits':(529,590,(360,460,1270,1060)),
'17-second-phone':(613,634,(320,0,1550,2000)), '18-options':(644,659,(647,950,620,520)),
'19-yes':(659,689,(275,520,1440,985)), '20-close':(690,713,(200,214,1600,1590)),
'21-end-label':(716,757,(360,700,1280,690)), '22-ending':(755,777,(0,0,2000,2000)),
}
sel={f for a,b,_ in windows.values() for f in range(a,b+1)}
cache={}
ref='/Users/darshan/Downloads/sidehoe.mp4'
w=800
p=subprocess.Popen(['ffmpeg','-v','error','-i',ref,'-vf',f'scale={w}:{w}', '-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
for f in range(778):
    b=p.stdout.read(w*w*3)
    if f in sel: cache[f]=b
p.wait()
for name,(a,b,rect) in windows.items():
    x,y,rw,rh=rect
    box=tuple(round(v*w/2000) for v in (x,y,x+rw,y+rh))
    size=(180,min(147,round(rh*180/rw)))
    cols=8
    sheet=Image.new('RGB',(size[0]*cols,((b-a)//cols+1)*(size[1]+19)),'#e5e5e5')
    draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(range(a,b+1)):
        p=Image.frombytes('RGB',(w,w),cache[f]).crop(box)
        p.thumbnail(size)
        xx,yy=i%cols*size[0],i//cols*(size[1]+19)
        sheet.paste(p,(xx,yy))
        draw.text((xx+4,yy+size[1]+2),f'{f:03} / {f/25:.2f}',fill='black')
    sheet.save(dest/f'source-{name}.jpg',quality=92)
