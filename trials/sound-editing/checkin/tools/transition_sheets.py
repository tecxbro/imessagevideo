from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]/'evidence'


def grid(frames, crop, name, width=320, height=220):
    sheet=Image.new('RGB',(width*6,((len(frames)+5)//6)*(height+25)),'#222222')
    draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(frames):
        x,y=(i%6)*width,(i//6)*(height+25)
        im=Image.open(BASE/f'frame-{f:03}.png').crop(crop).resize((width,height))
        sheet.paste(im,(x,y));draw.text((x+4,y+height+4),f'frame {f}',fill='white')
    sheet.save(BASE/name)


grid(list(range(0,36)),(500,100,1400,800),'receive-onset.png')
grid(list(range(134,166)),(560,480,1320,865),'draft-onset.png')
grid(list(range(420,461)),(1280,200,1920,810),'second-phone-onset.png')
grid(list(range(180,211)),(560,480,1320,865),'send-onset.png')
grid(list(range(85,101)),(500,570,1400,1080),'plus-onset.png')
grid([444,445,446,450,451,452,456,457,458,462,463,464,468,469,470,473,474,475,479,480,481,485,486,487,491,492,493],(1100,650,1920,850),'typing-wide.png',320,100)
grid(list(range(500,513)),(1060,360,1200,520),'arrival-map.png',240,240)
grid(list(range(90,111)),(500,0,1400,1080),'plus-full.png',320,384)
