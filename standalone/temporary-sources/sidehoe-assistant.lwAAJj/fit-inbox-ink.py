from pathlib import Path
import json,sys
from PIL import Image
import numpy as np
root=Path(__file__).parent
proj=root/'inbox-project'
sys.path.insert(0,str(proj))
from render import interpolate
p=proj/'scene.json'
s=json.loads(p.read_text())
local=s['inboxHeldRegistration']
observed=json.loads((root/'inbox-landmarks.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
def bounds(q,target,threshold):
    l,t,r,b=map(round,target)
    body=q[t:b,l:r]
    ink=(body.max(2)<threshold)&(np.ptp(body,axis=2)<20)
    yy=np.where(ink.sum(1)>1)[0]
    xx=np.where(ink.sum(0)>1)[0]
    return None if not (yy.size and xx.size) else [l+int(xx[0]),t+int(yy[0]),l+int(xx[-1])+1,t+int(yy[-1])+1]
for f in range(10,42):
    row=local[str(f)]
    head=observed[str(f)][0]['head']
    cy=head[1]
    clock_y=cy-114
    q=np.asarray(Image.open(source/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
    head_ink=bounds(q,(365,cy-42,627,cy+38),171)
    clock_ink=bounds(q,(145,clock_y-24,282,clock_y+25),171)
    y,=interpolate(s['tracks']['inboxY'],f)
    scale,=interpolate(s['tracks']['inboxScale'],f)
    x=500-410*scale
    def project(role, box, width, height):
        if not box:
            return
        l,t,r,b=box
        if (r-l)<width or (b-t)<height or b-t>48:
            return
        row[role]=[round(z,4) for z in ((l-x)/scale,(t-y)/scale-row['chromeY'],(r-l)/scale,(b-t)/scale)]
    project('clockInk',clock_ink,55,16)
    project('headingInk',head_ink,132,20)
p.write_text(json.dumps(s,indent=2)+'\n')

p=proj/'render.py'
c=p.read_text()
def edit(a,b):
    global c
    assert c.count(a)==1,a
    c=c.replace(a,b)
edit('''def status(d,w,y,label,island=False,*,island_bounds=None):
    text(d,41 if island else 92,y if island else y-18,label,16 if island else 35,INK,630)''','''def status(d,w,y,label,island=False,*,island_bounds=None):
    if label:
        text(d,41 if island else 92,y if island else y-18,label,16 if island else 35,INK,630)''')
edit('''        status(d,815,214,self.c["status"])
        floating_control(chrome, 77, 292, 109, 68, 30)''','''        clock = held.get("clockInk") if held else None
        status(d,815,214,None if clock else self.c["status"])
        if clock:
            fit_ink(chrome,self.c["status"],clock,555,.99,.18,
                    family=messages_font,ink=(12,12,13),fractional=True)
        floating_control(chrome, 77, 292, 109, 68, 30)''')
edit('''        d.text((410,306),self.c["inbox"],font=messages_font(35,620),fill="#090909",anchor="mt")''','''        heading=held.get("headingInk") if held else None
        if heading:
            fit_ink(chrome,self.c["inbox"],heading,630,.98,.16,
                    family=messages_font,ink=(13,13,14),fractional=True)
        else:
            d.text((410,306),self.c["inbox"],font=messages_font(35,620),fill="#090909",anchor="mt")''')
p.write_text(c)
