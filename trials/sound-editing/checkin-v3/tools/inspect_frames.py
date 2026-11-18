"""Sequential native-frame evidence, before/at/after each supplied v3 action."""
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image,ImageDraw

BASE=Path(__file__).resolve().parents[1]


def main():
    supplied=json.loads((BASE/'director-events.json').read_text())
    events=sorted(map(int,supplied['events']))
    frames={f+d for f in events for d in [-1,0,1]}
    frames|={0,12,14,60,89,91,103,140,145,155,185,187,209,210,240,270,299,300,310,320,324,340,350,380,410,450,459,461,480,542,560,569,571,600,614,616,660,719}
    frames|=set(range(485,543))
    process=subprocess.Popen(['ffmpeg','-v','error','-i',str(BASE/'v3-final.mp4'),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    for f in range(720):
        raw=process.stdout.read(1920*1080*3)
        if len(raw)!=1920*1080*3:raise ValueError(f'Short decode at frame{f}')
        if f in frames:
            Image.fromarray(np.frombuffer(raw,np.uint8).reshape(1080,1920,3)).save(BASE/'evidence'/f'frame-{f:03}.png')
    if process.wait()!=0:raise RuntimeError('Frame decode failed')
    def sheet(name,rows,crop,size):
        w,h=size
        canvas=Image.new('RGB',(w*len(rows[0]),(h+22)*len(rows)),'#222222');draw=ImageDraw.Draw(canvas)
        for y,row in enumerate(rows):
            for x,f in enumerate(row):
                im=Image.open(BASE/'evidence'/f'frame-{f:03}.png')
                if crop:im=im.crop(crop)
                canvas.paste(im.resize(size),(x*w,y*(h+22)))
                draw.text((x*w+5,y*(h+22)+h+3),f'frame {f}',fill='white')
        canvas.save(BASE/'evidence'/name)
    sheet('opening-actions.png',[[f-1,f,f+1] for f in [13,90,132,186]],None,(480,270))
    sheet('typing.png',[[f-1,f,f+1] for f in events if 325<=f<=440],(650,760,1280,850),(600,90))
    sheet('backspaces.png',[[f-1,f,f+1] for f in events if 488<=f<=541],(650,760,1280,850),(600,90))
    sheet('late-actions.png',[[f-1,f,f+1] for f in [460,570,615]],None,(640,360))
    overview=[0,13,90,132,145,186,210,240,270,299,310,325,440,460,488,541,570,615,660,719]
    sheet('contact-sheet.png',[overview[i:i+4] for i in range(0,len(overview),4)],None,(480,270))
    print(f'Extracted {len(frames)} native frames and five evidence sheets')


if __name__=='__main__':main()
