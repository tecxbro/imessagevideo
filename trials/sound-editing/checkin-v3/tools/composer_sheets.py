"""Regenerate composer crops from retained native PNGs, without decoding again."""
import json
from pathlib import Path
from PIL import Image,ImageDraw

BASE=Path(__file__).resolve().parents[1]
events=sorted(map(int,json.loads((BASE/'director-events.json').read_text())['events']))
for name,frames in [('typing.png',[f for f in events if 325<=f<=440]),('backspaces.png',[f for f in events if 488<=f<=541])]:
    canvas=Image.new('RGB',(1800,len(frames)*112),'#222222');draw=ImageDraw.Draw(canvas)
    for row,f in enumerate(frames):
        for col,n in enumerate([f-1,f,f+1]):
            im=Image.open(BASE/'evidence'/f'frame-{n:03}.png').crop((650,760,1280,850)).resize((600,90))
            canvas.paste(im,(col*600,row*112));draw.text((col*600+5,row*112+93),f'frame {n}',fill='white')
    canvas.save(BASE/'evidence'/name)
print('Corrected two composer sheets: crop follows centered v3 phone, not old right-phone layout')
