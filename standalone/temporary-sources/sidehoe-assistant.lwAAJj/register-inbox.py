from pathlib import Path
import json
import sys
import numpy as np

root=Path(__file__).parent
project=root/'inbox-project'
sys.path.insert(0,str(project))
from render import interpolate
p=project/'scene.json'
s=json.loads(p.read_text())
samples=json.loads((root/'inbox-landmarks.json').read_text())
data={}
for f in range(10,42):
    a,b=samples[str(f)]
    old_y,=interpolate(s['tracks']['inboxY'],f)
    old_scale,=interpolate(s['tracks']['inboxScale'],f)
    a0,a1=a['unread'][:2]
    b0,b1=b['unread'][:2]
    assert a1[1]-a0[1]>140
    scale=(a1[1]-a0[1])/171
    x=(a0[0]+a1[0])*.5-80*scale
    y=(a0[1]+a1[1])*.5-(696+56+171*.5)*scale
    body=[]
    for n in ('marie','darla'):
        d,e=a[n],b[n]
        dw=d[3][2]-d[3][0]; ew=e[3][2]-e[3][0]
        body.append([*np.round(((d[0]-e[0])/old_scale,(d[1]-e[1])/old_scale,
                                 np.clip(dw/ew,.935,1.08)),4)])
    ink=(a['head'][1]-b['head'][1])/old_scale
    b_avg=np.array(body).mean(0)
    data[str(f)]=dict(rows=[round(q,4) for q in (x,y,scale)],chromeY=round(ink,4),
                       pins=[body[0],np.round(b_avg,4).tolist(),body[-1]])
s['inboxHeldRegistration']=data
p.write_text(json.dumps(s,indent=2)+'\n')

p=project/'render.py'
code=p.read_text()
def replace(a,b):
    global code
    assert code.count(a)==1,a
    code=code.replace(a,b)

replace('''    def inbox(self,im,f):
        i=layer(820,2500)''','''    def inbox(self,im,f):
        held = self.s.get("inboxHeldRegistration",{}).get(str(f))
        i=layer(820,2500)''')
replace('''        else:
            composite(i,chrome,0,0)
        d=ImageDraw.Draw(i)''','''        else:
            composite(i,chrome,0,held["chromeY"] if held else 0)
        d=ImageDraw.Draw(i)''')
replace('''            p=tween(f,0 if j==1 else 1,5 if j==1 else 8)
            self.avatar(i,key,x,473+68*(1-p),162*(.78+.22*p),
                        (.58+.42*p if f<10 else .25+.75*p) if j==1 else p,lit=True)
            if p>.38:
                text(d,x,571,label,26,"#353535",510,"center")''','''            p=tween(f,0 if j==1 else 1,5 if j==1 else 8)
            dx,dy,size = held["pins"][j] if held else (0,0,1)
            self.avatar(i,key,x+dx,473+68*(1-p)+dy,162*(.78+.22*p)*size,
                        (.58+.42*p if f<10 else .25+.75*p) if j==1 else p,lit=True)
            if p>.38:
                text(d,x+dx,571+dy,label,26,"#353535",510,"center")''')
replace('''            if f>=10:
                composite(i,tag,285,359+(1-p)*22,p)''','''            if f>=10:
                dx,dy,_ = held["pins"][1] if held else (0,0,1)
                composite(i,tag,285+dx,359+(1-p)*22+dy*.67,p)''')
replace('''        else:
            d.rounded_rectangle((231,2260,590,2270),6,fill="#777580")
            composite(i,rows,0,0,tween(f,-.5,9) if f<10 else 1)
            composite(im,blur(i,amount),500-410*scale,y,1,scale)
        if f<10:''','''        elif held:
            composite(im,blur(i,amount),500-410*scale,y,1,scale)
            row_left,row_top,row_scale = held["rows"]
            composite(im,rows,row_left,row_top,1,row_scale)
        else:
            d.rounded_rectangle((231,2260,590,2270),6,fill="#777580")
            composite(i,rows,0,0,tween(f,-.5,9) if f<10 else 1)
            composite(im,blur(i,amount),500-410*scale,y,1,scale)
        if f<10:''')
p.write_text(code)
