from pathlib import Path
import sys,json
from PIL import Image
import numpy as np

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate

prev=Path('/tmp/sidehoe-pullback.nP3qTC')
status=json.loads((prev/'assistant-status-profiles.json').read_text())
measure=json.loads((prev/'assistant-landmarks.json').read_text())
sfile=root/'project/scene.json'
scene=json.loads(sfile.read_text())
tr=scene['tracks']
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
measurements={}

def region(q, box, threshold, minimum=2):
    l,t,r,b=map(round,box)
    sw=q[t:b,l:r]
    ink=(sw.max(2)<threshold)&(np.ptp(sw,axis=2)<26)
    ys=np.flatnonzero(ink.sum(1)>=minimum)
    xs=np.flatnonzero(ink.sum(0)>=minimum)
    if not ys.size or not xs.size:
        return None
    return [l+int(xs[0]),t+int(ys[0]),l+int(xs[-1])+1,t+int(ys[-1])+1]

fix_time={134:[158,356,235,389],135:[158,400,231,433],136:[156,431,232,459],137:[160,452,231,484]}
fix_cell={134:[668,359,714,389],135:[661,400,711,435]}
fix_wifi={134:[725,357,767,390],135:[724,401,767,434],136:[725,433,762,463]}
for f in range(134,162):
    x,y,w=interpolate(tr['assistantMeasuredPosition'],f)
    source=np.asarray(Image.open(src/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
    lens=scene['measuredRimDisplacement'].get(str(f))
    sc=w/900
    ease=interpolate(tr['assistantBodyFocus'],f)[0]
    def native(xp,yp):
        a=(xp-x)/sc
        b=yp-y
        if lens:
            px,py=zip((0,0),*lens,(900,0))
            displacement=-np.interp(a,px,py)*1.15
            b+=displacement*max(0,1-(b+28)/220)
        return a,b
    def fit(box,*,padding=0):
        x0,y0,x1,y1=box
        a,b=native(x0+padding,y0+padding)
        c,d=native(x1-padding,y1-padding)
        return [round(v,3) for v in (a,b,c-a,d-b)]
    reference=status.get(str(f),{}).get('source',{})
    if f==161:
        for key,box in status['160']['source'].items():
            if key != 'bevel_top' and box:
                reference[key]=[box[0],box[1]+30,box[2],box[3]+30]
    st={}
    for name,fix in [('time',fix_time),('cellular',fix_cell),('wifi',fix_wifi),('battery',{})]:
        box=fix.get(f,reference.get(name))
        if box is None or box[2]-box[0] < (40 if name in ('time','battery') else 17):
            continue
        if f>=159 and name=='wifi':
            # The fade can hide the thinner outer arcs in a thresholded region.
            box=[728,box[1]-4,769,box[3]+4]
        st[name]=fit(box,padding=max(0,ease*.09))
    if f>=135:
        heading=region(source,(399,y+176,599,y+278),162)
        if heading:
            st['heading']=fit(heading,padding=ease*.12)
    if f<=140:
        edit=region(source,(143,y+168,241,y+257),156,2)
        if edit and edit[2]-edit[0]>38:
            st['edit']=fit(edit,padding=ease*.13)
    if f<=144:
        right=measure[str(min(160,f))][0]['right_contact']
        left=measure[str(min(160,f))][0]['left_contact']
        if left and right:
            def disc(box):
                l,t,r,b=box
                cx,cy=native((l+r)/2,(t+b)/2)
                return [round(cx,3),round(cy,3),round(((r-l)/sc+b-t)/2,3)]
            st['pins']=list(map(disc,(left,right)))
    measurements[str(f)]=st
scene['assistantScreenRegistration']=measurements
sfile.write_text(json.dumps(scene,indent=2)+'\n')

p=root/'project/render.py'
s=p.read_text()
def edit(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)

look='''        ix,iy,iw,ih = self.track("assistantIslandBox",f)'''
edit(look,'''        screen = self.s.get("assistantScreenRegistration",{}).get(str(f),{})
'''+look)
before='''        text(d,103,86,self.c["status"],34,INK,630)
        for i, height in enumerate((7, 12, 17, 21)):
            d.rounded_rectangle((604+11*i,116-height,612+11*i,116),3,fill=INK)
        d.arc((667,90,707,118),208,332,fill=INK,width=5)
        d.arc((674,99,700,118),208,332,fill=INK,width=4)
        oval(d,687,114,4,4,INK)
        d.rounded_rectangle((727,93,774,115),6,fill=INK)
        d.rectangle((776,100,781,108),fill=INK)'''
after='''        if "time" in screen:
            fit_ink(beneath,self.c["status"],screen["time"],540,
                    family=messages_font,ink=(20,20,21),fractional=True)
        else:
            text(d,103,86,self.c["status"],34,INK,630)
        if "cellular" in screen:
            left,top,width,height = screen["cellular"]
            for i,part in enumerate((.43,.61,.79,1)):
                x=left+i*width*.268
                d.rounded_rectangle((x,top+height*(1-part),x+width*.19,top+height),
                                    width*.046,fill="#252527")
        else:
            for i,height in enumerate((7,12,17,21)):
                d.rounded_rectangle((604+11*i,116-height,612+11*i,116),3,fill=INK)
        if "wifi" in screen:
            left,top,width,height = screen["wifi"]
            center = left+width*.5
            for extent,lift,depth in ((1,0,1.49),(.69,.31,.89),(.36,.62,.40)):
                radius=width*extent*.61
                d.arc((center-radius,top+height*lift,center+radius,top+height*(lift+depth)),
                      218,322,fill="#202021",width=max(1,round(width*.128)))
            oval(d,center,top+height*.916,width*.097,height*.082,"#202021")
        else:
            d.arc((667,90,707,118),208,332,fill=INK,width=5)
            d.arc((674,99,700,118),208,332,fill=INK,width=4)
            oval(d,687,114,4,4,INK)
        if "battery" in screen:
            left,top,width,height = screen["battery"]
            d.rounded_rectangle((left,top,left+width*.885,top+height),
                                height*.24,fill="#262628")
            d.rounded_rectangle((left+width*.958,top+height*.32,left+width,top+height*.68),
                                width*.028,fill="#303031")
        else:
            d.rounded_rectangle((727,93,774,115),6,fill=INK)
            d.rectangle((776,100,781,108),fill=INK)'''
edit(before,after)
edit('''        text(d,143,208,self.c["edit"],33,INK,640,"center")
        if optics and "inbox" in optics:''','''        if "edit" in screen:
            fit_ink(beneath,self.c["edit"],screen["edit"],585,
                    family=messages_font,ink=(24,24,26),fractional=True)
        else:
            text(d,143,208,self.c["edit"],33,INK,640,"center")
        if optics and "inbox" in optics:''')
edit('''        else:
            text(d,450,207,self.c["inbox"],36,INK,650,"center")''','''        elif "heading" in screen:
            fit_ink(beneath,self.c["inbox"],screen["heading"],596,
                    family=messages_font,ink=(18,18,20),fractional=True)
        else:
            text(d,450,207,self.c["inbox"],36,INK,650,"center")''')
edit('''        for x,k,n in [(left,"marie","Marie"),(right,"darla","Darla")]:
            self.avatar(beneath,k,x,py+side_lift,side_diam,pin_alpha,lit=True)
            if f>=135:
                ld.text((x,name_y),n,font=messages_font(29,490),fill="#333333",anchor="mt")''','''        pins=screen.get("pins",[(left,py+side_lift,side_diam),(right,py+side_lift,side_diam)])
        for (x,cy,disk),k,n in zip(pins,("marie","darla"),("Marie","Darla"),strict=True):
            self.avatar(beneath,k,x,cy,disk,pin_alpha,lit=True)
            if f>=135:
                ld.text((x,name_y),n,font=messages_font(29,490),fill="#333333",anchor="mt")''')
p.write_text(s)
