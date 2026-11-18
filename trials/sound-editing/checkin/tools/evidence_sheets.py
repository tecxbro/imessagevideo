from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]/'evidence'


def sheet(events, crop, name, size):
    width,height=size
    canvas=Image.new('RGB',(width*3,(height+24)*len(events)),'#222222')
    draw=ImageDraw.Draw(canvas)
    for row,frame in enumerate(events):
        for col,f in enumerate([frame-1,frame,frame+1]):
            im=Image.open(BASE/f'frame-{f:03}.png').crop(crop).resize(size)
            x,y=col*width,row*(height+24)
            canvas.paste(im,(x,y));draw.text((x+5,y+height+4),f'frame {f}',fill='white')
    canvas.save(BASE/name)


sheet([445,451,457,463,469,474,480,486,492],(1250,735,1600,805),'typing-pairs.png',(420,84))
sheet([522,525,529,532,535,538,542,545,548],(1250,735,1600,805),'deletion-pairs.png',(420,84))
sheet([12,90,132,140,186],(500,0,1400,930),'early-action-pairs.png',(450,465))
sheet([432,505,510,575,590],(0,120,1680,820),'late-action-pairs.png',(672,280))
