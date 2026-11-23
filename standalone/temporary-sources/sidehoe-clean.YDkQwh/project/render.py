"""Frame-indexed original vector stage. Render input is scene.json and its local font."""
import argparse
from bisect import bisect_right
from functools import lru_cache
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from artwork import app_icon, badge, composite, font, heart, oval, portrait
from artwork import rounded_gradient, stamp, text


SIZE = 1000
BASE = "#fafafa"
INK = "#17171d"
MUTED = "#77747e"


def clamp(x, y=0, z=1):
    return min(z, max(x, y))


def up(f, a, b):
    return clamp((f-a)/(b-a))


def ease(p):
    return p*p*(3-2*p)


def tween(f,a,b):
    return ease(up(f,a,b))


def mix(a,b,p):
    return a+(b-a)*p


def interpolate(track, f):
    frames=[k[0] for k in track]
    at=bisect_right(frames,f)
    if at==0:
        return track[0][1:]
    if at==len(track):
        return track[-1][1:]
    a,b=track[at-1:at+1]
    return [mix(x,y,up(f,a[0],b[0])) for x,y in zip(a[1:],b[1:])]


def layer(w=SIZE,h=SIZE):
    return Image.new("RGBA",(w,h))


def blur(im,radius):
    return im.filter(ImageFilter.GaussianBlur(radius)) if radius > .25 else im


@lru_cache(maxsize=84)
def wash(strength, variant="pink"):
    yy,xx=np.mgrid[0:SIZE:240j,0:SIZE:240j] / SIZE
    if variant=="apps":
        a=np.exp(-((xx-.42)**2/.066+(yy-.43)**2/.09))
        b=np.exp(-((xx-.62)**2/.074+(yy-.59)**2/.07))
        t=np.stack([2*a+30*b,56*a+26*b,11*a],axis=-1)
        t=t*.58
    else:
        roll=np.clip((yy+.35*xx-.61)/.61,0,1)
        cloud=np.exp(-((xx-1.11)**2/.18+(yy-.96)**2/.24))
        t=roll[:,:,None]**1.75*np.array([1,72,6])+cloud[:,:,None]*np.array([34,66,18])
    data=np.uint8(np.clip(250-t*(strength/40),0,255))
    return Image.fromarray(data).resize((SIZE,SIZE),Image.Resampling.BICUBIC).convert("RGBA")


def gentle_characters(im, label, x, y, size, weight, f, onset, spacing, tinted=False):
    d=ImageDraw.Draw(im,"RGBA")
    face=font(size,weight)
    left=x-face.getlength(label)/2
    accents=[(211,128,222),(163,139,237),(104,207,217),(224,189,107)]
    for i,glyph in enumerate(label):
        a=up(f,onset+spacing*i,onset+spacing*i+4)
        after=up(f,onset+spacing*i+2,onset+spacing*i+7)
        if a:
            base=accents[i%len(accents)] if tinted else (143,141,151)
            color=tuple(round(mix(v,21,after)) for v in base)
            c=tuple(round(mix(250,v,a)) for v in color)
            text(d,left+face.getlength(label[:i]),y+(1-ease(a))*size*.19,glyph,size,c,weight)


def cursor(im,x,y,r=0, opacity=1, size=1):
    glyph=layer(68,72)
    d=ImageDraw.Draw(glyph)
    d.polygon([(11,9),(52,35),(34,38),(44,58),(34,63),(24,43),(13,55)],fill="#15141b",
              outline="#ffffff",width=3)
    if r:
        glyph=glyph.rotate(-r,resample=Image.Resampling.BICUBIC,center=(11,9))
    composite(im,glyph,x-11*size,y-9*size,opacity,size)


def phone_shell(im,w,h,radius):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,w-1,h-1),radius,fill="#666675")
    d.rounded_rectangle((2,2,w-3,h-3),radius-2,fill="#383846")
    d.rounded_rectangle((5,4,w-6,h-5),radius-5,fill="#171821",outline="#6d6b75",width=1)
    d.rounded_rectangle((9,8,w-10,h-9),radius-9,fill=BASE)
    d.line((1,h*.18,1,h*.26),fill="#2a2831",width=3)
    d.line((1,h*.30,1,h*.40),fill="#2a2831",width=3)
    d.line((w-2,h*.39,w-2,h*.46),fill="#2a2831",width=3)


def status(d,w,y,label,island=False):
    text(d,41,y,label,16 if island else 35,INK,630)
    size=1 if island else 2
    x=w-(94 if island else 202)
    for i,h in enumerate([4,7,10,13]):
        d.rounded_rectangle((x+i*5*size,y+(14-h)*size,x+(i*5+3)*size,y+14*size),2,fill=INK)
    x+=26*size
    d.arc((x-7*size,y+3*size,x+9*size,y+15*size),218,322,fill=INK,width=size*2)
    oval(d,x+size,y+12*size,size*1.4,size*1.4,INK)
    x+=17*size
    d.rounded_rectangle((x,y+4*size,x+22*size,y+14*size),2*size,outline=INK,width=size)
    d.rounded_rectangle((x+2*size,y+6*size,x+18*size,y+12*size),size,fill=INK)
    d.rectangle((x+23*size,y+7*size,x+24*size,y+11*size),fill=INK)
    if island:
        d.rounded_rectangle((w/2-55,y-19,w/2+55,y+15),22,fill="#202127")
        oval(d,w/2+40,y-2,4,4,"#4c485a")
        oval(d,w/2+40,y-2,1.8,1.8,"#767991")


class Film:
    def __init__(self, scene):
        self.s=scene
        self.c=scene["copy"]
        self.palette=scene["palette"]
        self.events={e["id"]:e["frame"] for e in scene["timeline"]["events"]}

    def at(self,event):
        return self.events[event]

    def track(self,key,f):
        return interpolate(self.s["tracks"][key], f)

    def avatar(self,im,key,x,y,diam,opacity=1,bg="",neutral=False):
        stamp(im,portrait(tuple(self.s["avatars"][key]),bg,neutral),x,y,diam,opacity)

    def inbox(self,im,f):
        i=layer(820,2500)
        d=ImageDraw.Draw(i)
        status(d,815,214,self.c["status"])
        d.rounded_rectangle((34,294,146,362),25,fill="#f0eff4")
        text(d,90,313,self.c["edit"],29,INK,600,"center")
        text(d,410,312,self.c["inbox"],33,INK,665,"center")
        oval(d,696,328,35,35,"#f0eff4")
        for width,y in [(38,318),(28,327),(16,336)]:
            d.rounded_rectangle((696-width/2,y,696+width/2,y+3),2,fill=INK)

        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):
            p=tween(f,0 if j==1 else 1,5 if j==1 else 8)
            self.avatar(i,key,x,482+68*(1-p),158*(.78+.22*p),.25+.75*p if j==1 else p)
            if p>.38:
                text(d,x,578,label,25,INK,530,"center")
        p=tween(f,4,11)
        if p>0:
            tag=layer(255,80)
            tagd=ImageDraw.Draw(tag)
            tagd.rounded_rectangle((3,4,252,70),24,fill="#fdfdff",outline="#eeedf4",width=2)
            tagd.polygon([(186,63),(211,63),(204,77)],fill="#fdfdff")
            text(tagd,124,22,self.c["pinNote"],25,INK,560,"center")
            composite(i,tag,285,373+(1-p)*22,p)

        rows=layer(820,2240)
        rd=ImageDraw.Draw(rows)
        for j,(name,quote,time,key) in enumerate(self.s["inboxRows"]):
            y=696+j*171
            oval(rd,80,y+56,8,8,"#19abdf")
            self.avatar(rows,key,140,y+55,69)
            text(rd,191,y+11,name,29,INK,630)
            text(rd,191,y+52,quote,26,MUTED)
            text(rd,690,y+14,time,23,"#98959f",400,"right")
            rd.line((717,y+16,726,y+25,717,y+34),fill="#bdbac5",width=2)
            rd.line((193,y+137,740,y+137),fill="#ecebf1",width=1)
        d.rounded_rectangle((231,2260,590,2270),6,fill="#777580")
        composite(i,rows,0,0,tween(f,2,10))
        y,=self.track("inboxY",f)
        scale,=self.track("inboxScale",f)
        amount=8*(1-up(f,0,6))+5*max(0,1-abs(f-57)/6)+2*up(f,98,101)
        composite(im,blur(i,amount),500-410*scale,y,1,scale)

    def identity(self,im,f):
        y,=self.track("identityY",f)
        s=mix(284,249,tween(f,103,114))
        a=tween(f,102,105)
        stamp(im,badge(round(mix(70,128,up(f,105,113))/4)*4),500,y,s,a)
        gentle_characters(im,self.c["brand"],500,y+s*.62,77,650,f,self.at("identity.name"),.75,True)

    def assistant(self,im,f):
        beneath=layer(900,830)
        phone_shell(beneath,900,830,153)
        d=ImageDraw.Draw(beneath)
        status(d,900,92,self.c["status"],True)
        d.rounded_rectangle((317,49,583,117),40,fill="#191a20")
        oval(d,553,83,12,12,"#353444")
        d.rounded_rectangle((83,90,125,114),7,fill=BASE)
        text(d,103,87,self.c["status"],33,INK,630)
        d.rounded_rectangle((759,83,886,112),10,fill=BASE)
        text(d,749,89,"▴  ◔  ▰",29,INK,600)
        d.rounded_rectangle((89,174,207,242),27,fill="#eeedf4")
        text(d,148,192,self.c["edit"],33,INK,615,"center")
        text(d,450,190,self.c["inbox"],35,INK,655,"center")
        for x,k,n in [(184,"marie","Marie"),(719,"darla","Darla")]:
            self.avatar(beneath,k,x,385,176,tween(f,134,138))
            text(d,x,491,n,29,INK,520,"center")
        stamp(beneath,badge(128),450,389,198)
        text(d,450,497,self.c["brand"]+"  ✓",29,INK,550,"center")
        y,=self.track("assistantY",f)
        composite(im,blur(beneath,3*(1-tween(f,134,139))+4*tween(f,158,161)),50,y)
        amount=round(34*tween(f,138,162))
        if amount:
            im.alpha_composite(Image.blend(im,wash(amount),.44))
        for j,line in enumerate(self.c["assistant"]):
            gentle_characters(im,line,500,215+j*64+max(0,y-441)*.65,57,640,f,135+j*3,.31)

    def personal(self,im,f):
        start=self.at("personal.line-one")
        im.alpha_composite(wash(round(36+4*tween(f,start,210))))
        y=455-530*tween(f,202,214)
        gentle_characters(im,self.c["personal"][0],500,y,56,630,f,start,.27)
        onset=self.at("personal.line-two")
        gentle_characters(im,self.c["personal"][1],500,y+60,77,760,f,onset,.48,True)
        d=ImageDraw.Draw(im)
        for i,(x,dy,s) in enumerate([(217,90,22),(243,122,16),(270,143,14),(722,117,16),(763,78,17),(771,124,23),(736,147,11)]):
            a=tween(f,onset+i*.7,onset+5+i*.7)*(1-tween(f,194+i*.5,211))
            if a>0:
                heart(d,x,y+dy-12*up(f,184,203),s*(.6+.4*a),(250,round(250-105*a),round(250-18*a)))

    def cluster(self,im,f):
        content=layer()
        d=ImageDraw.Draw(content)
        for k,x,y,r,on,col in self.s["cluster"]:
            a=tween(f,on,on+6)
            if a:
                cx=500+(x-500)*a
                cy=515+(y-515)*a+155*(1-a)
                oval(d,cx,cy,(r+27)*a,(r+27)*a,"#ece8f9")
        for k,x,y,r,on,col in self.s["cluster"]:
            a=tween(f,on,on+6)
            if a<=0:
                continue
            cx=500+(x-500)*a
            cy=515+(y-515)*a+155*(1-a)
            if k:
                self.avatar(content,k,cx,cy,2*r*a,a,col)
            else:
                oval(d,cx,cy,r*a,r*a,col)
        if f>=self.at("profiles.mosaic"):
            onset=self.at("profiles.mosaic")
            for j in range(6):
                p=up(f,onset+j*.33,onset+4+j*.33)
                w=p*1020
                d.rectangle((0 if j%2==0 else 1000-w,244+j*105,w if j%2==0 else 1000,
                             283+j*105+p*71),fill=BASE)
        grow=1+.12*tween(f,229,252)
        composite(im,blur(content,5*(1-tween(f,213,221))),500-500*grow,492-500*grow,1,grow)

    def profiles(self,im,f):
        xoff,yoff,zoom=self.track("profileCamera",f)
        for j,(name,key,tag,fill,ink) in enumerate(self.s["profiles"]):
            onset=self.at("profiles.directory")+j*2
            p=tween(f,onset,onset+8)
            opacity=p*(1-tween(f,287,302)*j*.48)
            if opacity<=0:
                continue
            tile=layer(300,370)
            d=ImageDraw.Draw(tile)
            self.avatar(tile,key,150,124,204,neutral=(f<self.at("profiles.lisa-focus") or f>=307))
            text(d,150,257,name,40,INK,630,"center")
            d.rounded_rectangle((40,309,260,357),24,fill=fill)
            text(d,150,319,tag,22,ink,590,"center")
            local=f-self.at("profiles.lisa-focus")
            if j==0 and local>=0 and local<15:
                for shift in (0,2):
                    d.arc((39+shift,308+shift,261-shift,358-shift), -140+local*12,
                          min(224,170+local*12),fill="#68d982" if shift==0 else "#c4f6cc",width=2)
            x=265+j*275
            x=500+(x-500)*zoom+xoff+85*(1-p)
            y=414+yoff-75*(1-p)
            composite(im,blur(tile,4*(1-p)+3*max(0,1-abs(f-287)/3)+5*tween(f,308,312)),
                      x-150*zoom,y-124*zoom,opacity,zoom)

    def bubble(self,im,x,y,w,h,lines,out=False,pale=False):
        d=ImageDraw.Draw(im)
        fill=self.palette["cyan"] if out else self.palette["incoming"]
        if pale:
            fill="#bcecf6"
        ink="#f4fdff" if out else self.palette["ink"]
        r=min(h*.43,18)
        d.rounded_rectangle((x,y,x+w,y+h),r,fill=fill)
        if out:
            d.polygon([(x+w-9,y+h-17),(x+w+1,y+h-6),(x+w+7,y+h),(x+w-10,y+h)],fill=fill)
        else:
            d.polygon([(x+9,y+h-15),(x-6,y+h),(x+12,y+h)],fill=fill)
        if isinstance(lines,str):
            lines=[lines]
        size=min(14.3,(w-18)/max(1,max(len(t) for t in lines)) * 1.92)
        font_h=size*1.26
        start=y+(h-font_h*len(lines))*.5+1
        for j,line in enumerate(lines):
            text(d,x+11,start+j*font_h,line,size,ink,480)

    def chip(self,im,x,y,w,h,label,active=False,scale=1, opacity=1,pressed=0):
        if opacity<=0:
            return
        a,b=self.palette["control_a"],self.palette["control_b"]
        if pressed:
            a="#e8ecf4"
            b="#f2e3f5"
        asset=rounded_gradient(w,h,a if active else self.palette["negative"],
                              b if active else "#d2d3db",round(h*.25),"x")
        d=ImageDraw.Draw(asset)
        text(d,w/2,round(h*.18),label,h*.60,INK,510,"center")
        composite(im,asset,x+(w*(1-scale))/2,y+h*(1-scale)/2,opacity,scale)

    def keyboard(self,im,y):
        d=ImageDraw.Draw(im)
        d.rectangle((10,y,389,817),fill="#d7d8e2")
        rows=[list("QWERTYUIOP"),list("ASDFGHJKL"),["↑",*list("ZXCVBNM"),"←"]]
        for j,letters in enumerate(rows):
            start=[13,32,18][j]
            step=[37.3,37.3,41.2][j]
            top=y+9+j*50
            for k,c in enumerate(letters):
                x=start+k*step
                fill="#fdfdff" if c not in {"↑","←"} else "#bbc0ce"
                d.rounded_rectangle((x,top+2,x+step-4,top+43),7,fill="#adafbb")
                d.rounded_rectangle((x,top,x+step-4,top+40),7,fill=fill)
                text(d,x+(step-4)/2,top+11,c,20,"#33323f",515,"center")
        top=y+158
        for a,b,n,col in [(15,92,"123","#bbc0ce"),(97,307,"space","#fcfcff"),(312,384,"Label","#bbc0ce")]:
            d.rounded_rectangle((a,top,b,top+38),7,fill=col)
            text(d,(a+b)/2,top+10,n,17,INK,520,"center")
        text(d,42,y+223,"☺",21,"#717684",490,"center")
        text(d,354,y+223,"◉",16,"#717684",490,"center")
        d.rounded_rectangle((137,807,263,813),3,fill="#34313d")

    def composer(self,im,y):
        d=ImageDraw.Draw(im)
        oval(d,44,y+15,15,15,"#eeedf2")
        text(d,44,y+5,"+",23,"#7c7985",540,"center")
        d.rounded_rectangle((70,y-1,373,y+32),17,outline="#d5d3dd",width=1)
        text(d,82,y+7,self.c["keyboardPrompt"],15,"#a6a2af")
        d.rounded_rectangle((352,y+7,358,y+18),3,fill="#8a8694")
        d.arc((349,y+11,361,y+23),0,180,fill="#8a8694",width=1)

    def thread_plate(self, which, f, keyboard_y):
        im=layer(400,827)
        phone_shell(im,400,827,65)
        # Header is inset within the shell, with an original tinted utility bar.
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((10,9,389,147),56,fill="#f3f1f6")
        d.rectangle((10,94,389,147),fill="#f3f1f6")
        d.line((10,147,389,147),fill="#e4e1ea",width=1)
        status(d,400,41,self.c["chatStatus"],True)
        d.line((45,100,35,111,45,122),fill="#6079ca",width=3)
        d.rounded_rectangle((351,104,365,117),3,outline="#6079ca",width=2)
        d.polygon([(365,110),(372,105),(372,117)],outline="#6079ca")
        if which=="sofia":
            c=self.c["sofia"]
            self.avatar(im,"danielle",200,100,44)
            text(d,200,126,c[0]+"  ›",11,INK,560,"center")
            self.bubble(im,141,183,219,35,c[1],True)
            self.bubble(im,39,250,171,32,c[2])
            self.bubble(im,39,286,269,32,c[3])
            text(d,200,341,self.c["today"],13,MUTED,500,"center")
        else:
            c=self.c["follow"]
            stamp(im,badge(85),200,100,38)
            text(d,200,126,c[0]+"  ›",11,INK,560,"center")
            self.bubble(im,140,173,222,48,c[1],True,True)
            self.bubble(im,42,232,260,48,c[2])
            text(d,200,307,self.c["today"],13,MUTED,500,"center")
            self.bubble(im,47,356,276,67,c[3])
        self.composer(im,keyboard_y-41)
        self.keyboard(im,keyboard_y)
        # The white screen and keyboard share the same curved bottom mask.
        mask=Image.new("L",im.size)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,399,826),65,fill=255)
        im.putalpha(mask)
        return im

    def suggestion_group(self,f):
        im=layer(410,545)
        c=self.c["sofia"]
        self.bubble(im,231,384,132,32,c[4],True)
        p=tween(f,self.at("sofia.suggestion"),340)
        if p>0:
            small=layer(213,74)
            text(ImageDraw.Draw(small),8,2,c[5],9.3,MUTED,520)
            self.bubble(small,1,13,185,50,c[6],True)
            composite(im,small,178+(1-p)*18,420+(1-p)*19,p,.88+.12*p)
        a=tween(f,self.at("sofia.no")-1,345)
        b=tween(f,self.at("sofia.send-control")-1,346)
        self.chip(im,252,485,43,24,c[7],False,.60+.40*a,a)
        self.chip(im,298,485,64,24,c[8],True,.62+.38*b,b)
        return im

    def sofia(self,im,f):
        y,s=self.track("sofiaCamera",f)
        x=500-200*s
        keyboard_y=round(mix(543,580,tween(f,335,347)))
        a=1-tween(f,352,360)
        g=self.suggestion_group(f)
        if a>0:
            plate=self.thread_plate("sofia",f,keyboard_y)
            entrance=6*(1-tween(f,313,320))
            push=2.3*max(0,1-abs(f-337)/5)+3*max(0,1-abs(f-354)/4)
            composite(im,blur(plate,entrance+push),x,y,a,s)
        if f<353:
            composite(im,blur(g,2.0*max(0,1-abs(f-337)/5)),x,y,1,s)
        else:
            dx,y,s=self.track("sendGroup",f)
            x=500-200*s+dx
            composite(im,blur(g,1.8*max(0,1-abs(f-355)/6)+3.3*tween(f,395,402)),
                      x,y,1-tween(f,398,403),s)
        if f>=381:
            x,y,r=self.track("sendCursor",f)
            cursor(im,x,y,r,1-tween(f,397,403),.89)

    def calendar(self,im,f):
        cal=layer()
        d=ImageDraw.Draw(cal)
        left,y0,h=self.track("calendarCamera",f)
        right=1000-left*.42
        first=left+20
        last=right-31
        for j,(dow,num) in enumerate(zip("SMTWTFS",[16,17,18,19,20,21,23])):
            x=mix(first,last,j/6)
            dark=INK if 0<j<6 else "#9894a5"
            if num==21:
                oval(d,x,y0-h*.60,h*.335,h*.335,"#ef3046")
                dark="#fff"
            text(d,x,y0-h*1.30,dow,h*.17,INK,635,"center")
            text(d,x,y0-h*.74,str(num),h*.33,dark,555,"center")
        for j in range(8):
            y=y0+h*j
            d.line((left,y,right,y),fill="#d5d2dc",width=2)
            text(d,left-8,y-8,f"{j or 12}AM",h*.195,"#8a8796",535,"right")
        appointments=(
            ("calendarLisa",self.c["calendar"][0],1.50,"#35b8e0","#8bd9f5","#246d87"),
            ("calendarMarie",self.c["calendar"][1],1.01,"#9a37df","#b68af1","#6826a3")
        )
        for track,name,dur,edge,fill,ink in appointments:
            top=y0+h*self.track(track,f)[0]
            bottom=top+h*dur
            bar=layer(round(right-left),max(1,round(bottom-top)))
            bd=ImageDraw.Draw(bar)
            from PIL import ImageColor
            rgb=ImageColor.getrgb(fill)
            bd.rounded_rectangle((0,0,bar.width-1,bar.height-1),8,fill=(*rgb,92))
            bd.rounded_rectangle((0,0,5,bar.height-1),3,fill=edge)
            composite(cal,bar,left,top)
            text(d,left+13,top+(h*.32 if track=="calendarMarie" else h*.10),name,h*.234,ink,620)
        x,y,r=self.track("calendarCursor",f)
        cursor(cal,x,y,r,tween(f,402,405),.88)
        if f>=self.at("calendar.mosaic"):
            p=up(f,self.at("calendar.mosaic"),479)
            for i in range(22):
                x=(169*i+378)%929
                y=(127*i+416)%819+72
                d.rectangle((x,y,x+(54+38*(i%4))*p,y+(87+22*(i%3))*p),fill=BASE)
        composite(im,blur(cal,4.5*(1-tween(f,398,410))+2*tween(f,472,479)),
                  0,0,tween(f,397,405)*(1-tween(f,476,480)))

    def apps(self,im,f):
        p=tween(f,478,487)*(1-tween(f,616,623))
        im.alpha_composite(wash(round(38*p),"apps"))
        phase,=self.track("orbitPhase",f)
        yoff,=self.track("orbitY",f)
        nodes=[]
        for name,k in [("red",0),("dark",.25),("rings",.50),("blue",.75)]:
            theta=(k-phase)*math.tau
            depth=math.cos(theta)
            s=mix(104,231,(depth+1)/2)*(.55+.45*p)
            x=500+186*math.sin(theta)*(.62+.38*p)
            y=495+110*depth+yoff
            nodes.append((depth,name,x,y,s))
        for depth,name,x,y,s in sorted(nodes):
            ox=blur(app_icon(name),4.5*(1-(depth+1)/2)+8*tween(f,615,622))
            stamp(im,ox,x,y,s,clamp(.50+2*p))

    def follow(self,im,f):
        y,s=self.track("followCamera",f)
        x=500-200*s
        contact=self.s["followContact"]
        y_shift,=interpolate(contact["phoneReframeY"],f)
        y+=y_shift
        plate=self.thread_plate("follow",f,543)
        a=tween(f,self.at("follow.no")-1,653)
        b=tween(f,self.at("follow.yes")-1,654)
        tapped=tween(f,self.at("follow.yes-feedback")-1,690)
        self.chip(plate,45,433,72,29,self.c["follow"][4],False,.58+.42*a,a)
        left,top,width,height=contact["yesRect"]
        self.chip(plate,left,top,width,height,self.c["follow"][5],True,.58+.42*b,b,tapped)
        composite(im,blur(plate,6*(1-tween(f,624,633))+2.5*max(0,1-abs(f-665)/7)+3*tween(f,690,696)),x,y,1,s)

        # Approach in stage space, then follow the live lower-right corner of Yes.
        cx,cy,r=self.track("followCursor",f)
        local=f-self.at("follow.yes-contact")
        attached=tween(local,-8,-2)
        if attached>0:
            dx,dy=interpolate(contact["tipFromLowerRight"],local)
            target_x=x+(left+width+dx)*s
            target_y=y+(top+height+dy)*s
            cx=mix(cx,target_x,attached)
            cy=mix(cy,target_y,attached)
        cursor(im,cx,cy,r,1,s*.59)

    def end(self,im,f):
        strength=round(48*tween(f,709,764))
        im.alpha_composite(wash(strength))
        y,=self.track("closingY",f)
        s,=self.track("closingSize",f)
        stamp(im,blur(badge(52),6*(1-tween(f,696,704))),500,y,s, .75+.25*tween(f,696,703))
        d=ImageDraw.Draw(im)
        words=self.c["ending"]
        onset=[
            [self.at("ending.the"),self.at("ending.most"),self.at("ending.personal")],
            [self.at("ending.imessage"),self.at("ending.assistant"),self.at("ending.yet")]
        ]
        for j,row in enumerate(words):
            size=47 if j==0 else 48
            weight=515 if j==0 else 690
            face=font(size,weight)
            x=500-face.getlength(" ".join(row))/2
            for k,word in enumerate(row):
                p=tween(f,onset[j][k]-1,onset[j][k]+6)
                if p:
                    tone=round(mix(248,20,p))
                    text(d,x,587+j*56+17*(1-p),word,size,(tone,tone,tone+min(6,255-tone)),weight)
                x+=face.getlength(word+" ")
        fade,=self.track("endingFade",f)
        if fade<1:
            return Image.blend(Image.new("RGBA",im.size,"black"),im,fade)
        return im

    def frame(self,f):
        im=Image.new("RGBA",(SIZE,SIZE),self.palette["paper"])
        if f<102:
            self.inbox(im,f)
        elif f<134:
            self.identity(im,f)
        elif f<162:
            self.assistant(im,f)
        elif f<213:
            self.personal(im,f)
        elif f<258:
            self.cluster(im,f)
        elif f<313:
            self.profiles(im,f)
        elif f<403:
            self.sofia(im,f)
        if 397<=f<480:
            self.calendar(im,f)
        if 478<=f<622:
            self.apps(im,f)
            if f<480:
                self.calendar(im,f)
        if 624<=f<696:
            self.follow(im,f)
        elif f>=696:
            im=self.end(im,f)
        return im.convert("RGB")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene",type=Path,default=Path(__file__).with_name("scene.json"))
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--frames",help="Inclusive frame span, e.g. 397:479. By default render all frames.")
    args=parser.parse_args()
    scene=json.loads(args.scene.read_text())
    count=scene["timeline"]["picture"]["frameCount"]
    start,end=(map(int,args.frames.split(":")) if args.frames else (0,count-1))
    if not 0<=start<=end<count:
        parser.error(f"frame span must be inside 0:{count-1}")
    film=Film(scene)
    args.cache.mkdir(exist_ok=True,parents=True)
    for f in range(start,end+1):
        film.frame(f).save(args.cache/f"{f:06d}.png",compress_level=1)
    print(f"Rendered {end-start+1} pictures from {start} to {end}")


if __name__=="__main__":
    main()
