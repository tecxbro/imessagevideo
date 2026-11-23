"""Frame-indexed original vector stage. Render input is scene.json and its local font."""
import argparse
from bisect import bisect_right
from functools import lru_cache
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from artwork import app_icon, badge, composite, font, heart, oval, portrait
from artwork import rounded_gradient, sprite_portrait, stamp, text


SIZE = 1000
BASE = "#fdfdfd"
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
    if radius <= .25:
        return im
    return im.convert("RGBa").filter(ImageFilter.GaussianBlur(radius)).convert("RGBA")


@lru_cache(maxsize=84)
def wash(strength, variant="pink"):
    yy, xx = np.mgrid[0:1:240j, 0:1:240j]
    if variant == "apps":
        field = np.exp(-((xx-.47-.125*(yy-.50))/.269)**2-((yy-.50)/.25)**2)
        tint = field[:, :, None] * np.array([33.5, 57.7, .9])
    else:
        cx, cy, sx, sy, shear = (1.80, .97, 1.46, .455, 1.74) if variant == "closing" else (1.70, 1.03, 1.48, .42, 1.46)
        field = np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
        color = [28.7, 156.5, 18.2] if variant == "closing" else [20, 135, 10]
        tint = field[:, :, None] * np.array(color)
        if variant == "pink":
            edge = np.exp(-((xx-1.0)/.23)**2-((yy-.96)/.25)**2)
            tint += edge[:,:,None]*np.array([7,34,5])
    data = np.uint8(np.clip(253-tint*(strength/40), 0, 255))
    return Image.fromarray(data).resize((SIZE, SIZE), Image.Resampling.BICUBIC).convert("RGBA")


@lru_cache(maxsize=42)
def measured_wash(controls):
    """Evaluate two editable light fields over the original stage matte."""
    yy,xx = np.mgrid[0:1:240j,0:1:240j]
    tint = np.zeros((240,240,3),dtype=np.float32)
    for offset in (0,8):
        cx,cy,sx,sy,shear,r,g,b = controls[offset:offset+8]
        light = np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
        tint += light[:,:,None]*np.array([r,g,b])
    rgb = np.rint(np.clip(253-tint,0,255)).astype(np.uint8)
    return Image.fromarray(rgb).resize((SIZE,SIZE),Image.Resampling.BICUBIC).convert("RGBA")


def vertical_blur(image, length):
    if length < 2:
        return image
    image = image.convert("RGBa")
    mixed = image
    count = min(13, max(3, round(length/5)))
    for i, offset in enumerate(np.linspace(-length/2, length/2, count), 2):
        shifted = image.transform(image.size, Image.Transform.AFFINE, (1, 0, 0, 0, 1, offset),
                                  Image.Resampling.BILINEAR)
        mixed = Image.blend(mixed, shifted, 1/i)
    return mixed.convert("RGBA")


def apply_fringe(image, x_offset, y_offset):
    r, g, b, alpha = image.split()
    def shift(channel, dx, dy):
        return channel.transform(channel.size, Image.Transform.AFFINE, (1, 0, dx, 0, 1, dy),
                                 Image.Resampling.BICUBIC)
    return Image.merge("RGBA", (shift(r, -x_offset, y_offset), g, shift(b, x_offset, -y_offset), alpha))


def lens_ripple(image, displacement_samples):
    """Local top-edge refraction, tapering independently down the phone face."""
    w,h = image.size
    strip_height = 240
    samples=[(0,0),*displacement_samples,(w,0)]
    px,py=zip(*samples)
    def displacement(x):
        return np.interp(x,px,py)
    mesh = []
    for x in range(0,w,12):
        right = min(w,x+12)
        dy_left,dy_right = displacement(x),displacement(right)
        mesh.append(((x,0,right,strip_height),
                     (x,dy_left,x,strip_height,right,strip_height,right,dy_right)))
    mesh.append(((0,strip_height,w,h),(0,strip_height,0,h,w,h,w,strip_height)))
    return image.transform(image.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)


def panel_wipe(im, masks, frame):
    d = ImageDraw.Draw(im)
    for onset, x, y, width, height in masks:
        if frame >= onset:
            d.rectangle((x, y, x+width, y+height), fill=(0, 0, 0, 0))


def gentle_characters(im, label, x, y, size, weight, f, onset, spacing, tinted=False):
    d=ImageDraw.Draw(im,"RGBA")
    if f >= onset+spacing*(len(label)-1)+7:
        text(d,x,y,label,size,(21,21,21),weight,"center")
        return
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


def fitted_badge(im, box, corner, radius=0, opacity=1, shine=0):
    x,y,w,h=box
    mark=badge(corner)
    if shine:
        highlight=Image.new("RGBA",mark.size,(175,165,252,round(shine)))
        mixed=Image.alpha_composite(mark,highlight)
        mixed.putalpha(mark.getchannel("A"))
        mark=mixed
    mark=mark.resize((max(1,round(w)),max(1,round(h))),Image.Resampling.LANCZOS)
    composite(im,blur(mark,radius),x-w/2,y-h/2,opacity)


def fit_ink(im, caption, bbox, weight, opacity=1, blur_radius=0):
    x,y,w,h=bbox
    if opacity<=0 or w<=0 or h<=0:
        return
    plane=layer(1050,140)
    text(ImageDraw.Draw(plane),10,12,caption,80,(20,20,20,255),weight)
    box=plane.getbbox()
    if box is None:
        return
    ink=plane.crop(box).resize((max(1,round(w)),max(1,round(h))),Image.Resampling.BICUBIC)
    patch=layer(ink.width+16,ink.height+16)
    patch.alpha_composite(ink,(8,8))
    composite(im,blur(patch,blur_radius),x-8,y-8,opacity)


def cursor(im,x,y,r=0, opacity=1, size=1):
    glyph=layer(68,72)
    d=ImageDraw.Draw(glyph)
    d.polygon([(11,9),(51,43),(31,42),(43,65),(34,70),(22,48),(12,59)],fill="#15141b",
              outline="#ffffff",width=3)
    if r:
        glyph=glyph.rotate(-r,resample=Image.Resampling.BICUBIC,center=(11,9))
    composite(im,glyph,x-11*size,y-9*size,opacity,size)


@lru_cache(maxsize=8)
def shell_material(w, h, radius):
    yy, xx = np.mgrid[:h, :w]
    edge_x = np.abs(xx-(w-1)/2)-(w/2-radius-1)
    edge_y = np.abs(yy-(h-1)/2)-(h/2-radius-1)
    distance = np.hypot(np.maximum(edge_x,0), np.maximum(edge_y,0))
    distance += np.minimum(np.maximum(edge_x,edge_y),0)-radius
    bevel = max(10, round(w*.032))
    inset = -distance
    peak = np.exp(-((inset-bevel*.23)/max(1.3,bevel*.16))**2)
    light = (23 + peak*(32+73*np.exp(-yy/(h*.21)))
             + 33*np.exp(-((xx-w*.15)/(w*.12))**2)*np.exp(-yy/(h*.17)))
    glass = np.clip((inset-bevel+.5)*1.1,0,1)
    rgb = light*(1-glass)+253*glass
    alpha = np.clip(inset+.5,0,1)*255
    pixels = np.stack((rgb,rgb,np.minimum(rgb+2,253),alpha),axis=2).astype(np.uint8)
    return Image.fromarray(pixels)


def phone_shell(im, w, h, radius):
    im.alpha_composite(shell_material(w, h, radius))


@lru_cache(maxsize=4)
def rim_only(w,h,radius):
    outer = shell_material(w,h,radius).copy()
    alpha = outer.getchannel("A")
    bevel = max(10, round(w*.032))
    ImageDraw.Draw(alpha).rounded_rectangle((bevel,bevel,w-bevel-1,h-bevel-1),radius-bevel,fill=0)
    outer.putalpha(alpha)
    return outer


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
        spec = self.s["avatars"][key]
        asset = (sprite_portrait(key,spec[0],bg,not neutral) if self.s.get("portraitSprites")
                 else portrait(tuple(spec),bg,neutral))
        stamp(im,asset,x,y,diam,opacity)

    def inbox(self,im,f):
        i=layer(820,2500)
        chrome=layer(820,630)
        d=ImageDraw.Draw(chrome)
        status(d,815,214,self.c["status"])
        d.rounded_rectangle((34,294,146,362),25,fill="#f0eff4")
        text(d,90,313,self.c["edit"],29,INK,600,"center")
        text(d,410,312,self.c["inbox"],33,INK,665,"center")
        oval(d,696,328,35,35,"#f0eff4")
        for width,y in [(38,318),(28,327),(16,336)]:
            d.rounded_rectangle((696-width/2,y,696+width/2,y+3),2,fill=INK)

        if f<10:
            alpha,softness,rise=self.track("inboxIntroHeader",f)
            composite(i,vertical_blur(blur(chrome,softness),softness*1.8),0,rise,alpha)
        else:
            composite(i,chrome,0,0)
        d=ImageDraw.Draw(i)
        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):
            p=tween(f,0 if j==1 else 1,5 if j==1 else 8)
            self.avatar(i,key,x,482+68*(1-p),158*(.78+.22*p),
                        (.58+.42*p if f<10 else .25+.75*p) if j==1 else p)
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
        amount=3*(1-up(f,0,6))+1.3*up(f,98,101)
        scroll_streak=0
        if f>=42:
            measured,=self.track("inboxMeasuredScroll",f)
            y=mix(y,measured,tween(f,42,47)*.86)
            scroll_streak,=self.track("inboxScrollSmear",f)
        composite(im,vertical_blur(blur(i,amount),scroll_streak),500-410*scale,y,1,scale)

    def identity(self,im,f):
        cx,cy,w,h=self.track("identityMeasuredBox",f)
        a=tween(f,102,105)
        amount=6*tween(f,129,133)
        corner=round(mix(87,128,up(f,105,113))/4)*4
        fitted_badge(im,(cx,cy,w,h),corner,amount,a)
        text_plate=layer()
        gentle_characters(text_plate,self.c["brand"],cx,cy+h*.64,77,650,f,
                          self.at("identity.name")-1,.68,True)
        exposure=max(amount,5*(1-tween(f,106,110)))
        composite(im,vertical_blur(blur(text_plate,exposure),exposure),0,0)

    def assistant(self,im,f):
        beneath=layer(900,830)
        phone_shell(beneath,900,830,153)
        d=ImageDraw.Draw(beneath)
        d.rounded_rectangle((316,58,586,131),45,fill="#0c0d10")
        d.rounded_rectangle((329,68,466,120),23,fill="#151518")
        oval(d,548,94,16,16,"#161720")
        oval(d,548,94,7,7,"#252b42")
        text(d,103,86,self.c["status"],34,INK,630)
        for i, height in enumerate((7, 12, 17, 21)):
            d.rounded_rectangle((604+11*i,116-height,612+11*i,116),3,fill=INK)
        d.arc((667,90,707,118),208,332,fill=INK,width=5)
        d.arc((674,99,700,118),208,332,fill=INK,width=4)
        oval(d,687,114,4,4,INK)
        d.rounded_rectangle((727,93,774,115),6,fill=INK)
        d.rectangle((776,100,781,108),fill=INK)
        d.rounded_rectangle((85,181,198,252),35,fill="#f7f6f8")
        d.rounded_rectangle((720,181,790,251),33,fill="#f8f7f9")
        for half,y_line in ((19,208),(14,218),(8,228)):
            d.rounded_rectangle((755-half,y_line,755+half,y_line+4),2,fill="#535258")
        text(d,143,208,self.c["edit"],33,INK,640,"center")
        text(d,450,207,self.c["inbox"],36,INK,650,"center")
        for x,k,n in [(184,"marie","Marie"),(719,"darla","Darla")]:
            self.avatar(beneath,k,x,396,178,tween(f,134,138))
            text(d,x,501,n,29,INK,520,"center")
        stamp(beneath,badge(128),450,396,201)
        text(d,450,501,self.c["brand"]+"  ✓",29,INK,550,"center")
        x,y,width=self.track("assistantMeasuredPosition",f)
        # Add the first inbox row inside the handset's measured bottom crop.
        self.avatar(beneath,"danielle",126,567,64,tween(f,136,141))
        text(d,179,534,"Natalie",32,INK,620)
        text(d,179,581,"See you soon!",25,MUTED)
        text(d,814,535,"1:50 AM",22,MUTED,500,"right")
        body = blur(beneath,3.8*(1-tween(f,134,139))+4*tween(f,158,161))
        if 135 <= f <= 137:
            shift = {135: 4, 136: 5, 137: 2}[f]
            curved=lens_ripple(body,self.s["measuredRimDisplacement"][str(f)])
            body=apply_fringe(curved,shift*.80,shift*.48)
        composite(im,body.resize((round(width),body.height),Image.Resampling.BICUBIC),x,y)
        tint, = self.track("assistantWash", f)
        amount = round(42*tint)
        if amount:
            overlay = wash(amount).convert("RGB")
            im.paste(ImageChops.multiply(im.convert("RGB"), overlay))
        title_y, = self.track("assistantTitleY", f)
        title = layer()
        for j, line in enumerate(self.c["assistant"]):
            gentle_characters(title,line,500,title_y+j*75,60,640,f,134+j*4,.20)
        composite(im,title,0,0,1-tween(f,157,161))

    def personal(self,im,f):
        start=self.at("personal.line-one")
        fields = tuple(self.track("titleWashFields", f))
        im.alpha_composite(measured_wash(fields))
        y, = self.track("personalTitleY", f)
        title = layer()
        if f<168:
            gentle_characters(title,self.c["personal"][0],500,y,65,660,f,start-1,.30)
        else:
            fit_ink(title,self.c["personal"][0],self.track("personalLine1",f),660,
                    mix(.72,1,tween(f,168,174)))
        onset=self.at("personal.line-two")
        if f>=188:
            fit_ink(title,self.c["personal"][1],self.track("personalLine2",f),765)
        elif f>=onset:
            line=self.c["personal"][1]
            face=font(89,765)
            left=500-face.getlength(line)/2
            hints=(179,178,178,182,183,177,181,183,180,182,181,177)
            for j,char in enumerate(line):
                ink=(72,35,76,round(255*tween(f,hints[min(j,len(hints)-1)],188)))
                text(ImageDraw.Draw(title),left+face.getlength(line[:j]),y+56,char,89,ink,765)
        d=ImageDraw.Draw(title)
        for i,(x,dy,s) in enumerate([(238,96,24),(253,118,29),(223,78,19),(746,100,22),(767,75,19),(767,124,24),(743,138,19)]):
            a=tween(f,onset+i*.7,onset+5+i*.7)*(1-tween(f,194+i*.5,208))
            if a>0:
                heart(d,x,y+dy-12*up(f,184,203),s*(.6+.4*a),(250,round(250-105*a),round(250-18*a)))

        composite(im,vertical_blur(title,23*tween(f,205,212)),0,0)
        if f==212:
            self.cluster_entrance(im,f)

    def cluster_entrance(self,im,f):
        layer_image=layer()
        d=ImageDraw.Draw(layer_image)
        samples=[]
        for entry, keys in zip(self.s["cluster"],self.s["tracks"]["clusterEntrance"]):
            if f<keys[0][0]:
                continue
            actor,_,_,_,_,color=entry
            x,y,size,opacity=interpolate(keys,f)
            samples.append((actor,x,y,size,opacity,color))
        if f>=214:
            for _,x,y,size,opacity,_ in samples:
                oval(d,x,y,size*.61,size*.61,(236,232,251,round(opacity*232)))
        for actor,x,y,size,opacity,color in samples:
            if actor:
                self.avatar(layer_image,actor,x,y,size,opacity,color)
            else:
                from PIL import ImageColor
                oval(d,x,y,size/2,size/2,(*ImageColor.getrgb(color),round(opacity*255)))
        softness,=self.track("clusterEarlyBlur",f)
        smear,=self.track("clusterEarlySmear",f)
        composite(im,vertical_blur(blur(layer_image,softness),smear),0,0)

    def cluster(self,im,f):
        if f<=226:
            self.cluster_entrance(im,f)
            return
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
        x,y,grow = self.track("clusterPose", f)
        if f >= self.at("profiles.mosaic"):
            stage = layer()
            composite(stage,content,500-500*grow+x,492-500*grow+y,1,grow)
            panel_wipe(stage,self.s["clusterWipe"],f)
            trail = f-254
            if trail>=2:
                stage=stage.transpose(Image.Transpose.ROTATE_90)
                stage=vertical_blur(stage,(trail-1)*22).transpose(Image.Transpose.ROTATE_270)
            composite(im,blur(stage,.6+trail*.75),0,0,max(0,1-.17*trail))
        else:
            composite(im,blur(content,11*(1-tween(f,213,222))),500-500*grow+x,492-500*grow+y,1,grow)

    def profile_arrival(self,im,f):
        for j,(name,key,tag,fill,ink) in enumerate(self.s["profiles"]):
            track_name = f"profileArrival{name}"
            start = self.s["tracks"][track_name][0][0]
            if f < start:
                continue
            x,y,radius,blur_radius = self.track(track_name, f)
            portrait_layer = layer(360,320)
            self.avatar(portrait_layer,key,180,160,2*radius,neutral=False)
            sprite = blur(portrait_layer,blur_radius*.51)
            if f == 258:
                sprite = sprite.transpose(Image.Transpose.ROTATE_90)
                sprite = vertical_blur(sprite,140).transpose(Image.Transpose.ROTATE_270)
            composite(im,sprite,x-180,y-160)
            label_y = mix(563, 561, tween(f,263,271))
            label_alpha = tween(f,start+1,start+7)
            labels = layer(300,155)
            d = ImageDraw.Draw(labels)
            prefix = name[:max(1,round(len(name)*label_alpha))]
            text(d,150,5,prefix,40,INK,630,"center")
            chip_w = 220*(.40+.60*label_alpha)
            d.rounded_rectangle((150-chip_w/2,58,150+chip_w/2,106),24,fill=fill)
            text(d,150,68,tag,22,ink,590,"center")
            composite(im,blur(labels,blur_radius*.23),x-150,label_y,label_alpha)

    def profiles(self,im,f):
        if f < 271:
            self.profile_arrival(im,f)
            return
        xoff,yoff,zoom=self.track("profileCamera",f)
        for j,(name,key,tag,fill,ink) in enumerate(self.s["profiles"]):
            onset=self.s["profileStartingFrames"][j]
            p=tween(f,onset,onset+4)
            opacity=p*(1-tween(f,287,300)*j*.70)
            if opacity<=0:
                continue
            tile=layer(300,370)
            d=ImageDraw.Draw(tile)
            if j==0:
                expression,=self.track("lisaExpression",f)
                self.avatar(tile,key,150,124,204,neutral=True)
                self.avatar(tile,key,150,124,204,expression,neutral=False)
            else:
                self.avatar(tile,key,150,124,204,neutral=True)
            labels = layer(300,370)
            label_draw = ImageDraw.Draw(labels)
            text(label_draw,150,257,name,40,INK,630,"center")
            label_draw.rounded_rectangle((40,309,260,357),24,fill=fill)
            text(label_draw,150,319,tag,22,ink,590,"center")
            composite(tile,labels,0,0,tween(f,onset+3,onset+8))
            local=f-self.at("profiles.lisa-focus")
            if j==0 and local>=0 and local<15:
                for shift in (0,2):
                    d.arc((39+shift,308+shift,261-shift,358-shift), -140+local*12,
                          min(224,170+local*12),fill="#68d982" if shift==0 else "#c4f6cc",width=2)
            if j==1 and f>=287:
                veil,=self.track("ellaRevealVeil",f)
                field=np.clip(np.linspace(.45,1.8,300)*veil,0,.98)
                mask=Image.fromarray(np.tile(np.uint8((1-field)*255),(370,1)))
                tile.putalpha(ImageChops.multiply(tile.getchannel("A"),mask))
                opacity=max(opacity,.91)
            x=265+j*275
            x=500+(x-500)*zoom+xoff+126*(1-p)
            y=414+yoff-90*(1-p)
            composite(im,blur(tile,9*(1-p)+6*max(0,1-abs(f-287)/3)+5*tween(f,308,312)),
                      x-150*zoom,y-124*zoom,opacity,zoom)

    def bubble(self,im,x,y,w,h,lines,out=False,pale=False,text_size=14.3):
        d=ImageDraw.Draw(im)
        fill=self.palette["cyan"] if out else self.palette["incoming"]
        if pale:
            fill="#bcecf6"
        ink="#f4fdff" if out else self.palette["ink"]
        r=min(h*.43, text_size*1.24)
        d.rounded_rectangle((x,y,x+w,y+h),r,fill=fill)
        if out:
            d.polygon([(x+w-9,y+h-17),(x+w+1,y+h-6),(x+w+7,y+h),(x+w-10,y+h)],fill=fill)
        else:
            d.polygon([(x+9,y+h-15),(x-6,y+h),(x+12,y+h)],fill=fill)
        if isinstance(lines,str):
            lines=[lines]
        size=min(text_size,(w-18)/max(1,max(len(t) for t in lines)) * 1.92)
        font_h=size*1.22
        start=y+(h-font_h*len(lines))*.5+1
        for j,line in enumerate(lines):
            text(d,x+max(11,size*.33),start+j*font_h,line,size,ink,480)

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
        im.alpha_composite(rim_only(400,827,65))
        return im

    def expose_phone(self, im, plate, x, y, scale, smear, radius, alpha=1):
        if smear > 1:
            pad = math.ceil(smear/2)+4
            padded = layer(plate.width, plate.height+2*pad)
            padded.alpha_composite(plate,(0,pad))
            plate = vertical_blur(padded,smear)
            y -= pad*scale
        composite(im,blur(plate,radius),x,y,alpha,scale)

    def suggestion_group(self,f):
        im=layer(410,545)
        c=self.c["sofia"]
        self.bubble(im,231,384,132,32,c[4],True)
        onset=self.at("sofia.suggestion")
        p=tween(f,onset-3,340) if f>=onset else 0
        if p>0:
            small=layer(213,74)
            text(ImageDraw.Draw(small),8,2,c[5],9.3,MUTED,520)
            self.bubble(small,1,13,185,50,c[6],True)
            landing_y = mix(375,420,tween(f,onset,340))
            composite(im,small,178+(1-p)*18,landing_y+(1-p)*19,p,.88+.12*p)
        a=tween(f,self.at("sofia.no")-1,345)
        b=tween(f,self.at("sofia.send-control")-1,346)
        self.chip(im,252,485,43,24,c[7],False,.60+.40*a,a)
        self.chip(im,298,485,64,24,c[8],True,.62+.38*b,b)
        return im

    def sofia(self,im,f):
        x,y,s=self.track("sofiaMeasuredCamera",f)
        keyboard_y=round(mix(543,580,tween(f,335,347)))
        a=1-tween(f,352,360)
        g=self.suggestion_group(f)
        if a>0:
            plate=self.thread_plate("sofia",f,keyboard_y)
            entrance=6*(1-tween(f,313,320))
            push=2.3*max(0,1-abs(f-337)/5)+3*max(0,1-abs(f-354)/4)
            trail, = self.track("sofiaExposure",f)
            self.expose_phone(im,plate,x,y,s,trail,entrance+push,a)
        if f < 353:
            trail = 85*(1-tween(f,313,319))
            composite(im,vertical_blur(blur(g,2.0*max(0,1-abs(f-337)/6)),trail),x,y,1,s)
        elif f < 360:
            dx,y,s=self.track("sendGroup",f)
            x=500-200*s+dx
            composite(im,blur(g,1.8*max(0,1-abs(f-355)/6)),x,y,1,s)
        else:
            detached = layer()
            c = self.c["sofia"]
            left, top, right, bottom = self.track("sendReplyBox", f)
            self.bubble(detached,left,top,right-left-8,bottom-top,c[4],True,text_size=54)
            left, top, right, bottom = self.track("sendSuggestionBox", f)
            text(ImageDraw.Draw(detached),left+12,top-28,c[5],27,MUTED,520)
            self.bubble(detached,left,top,right-left-8,bottom-top,c[6],True,text_size=46)
            self.chip(detached, right-318, bottom+5, 123, 64, c[7])
            self.chip(detached, right-177, bottom+5, 160, 66, c[8], True)
            composite(im,blur(detached,4*tween(f,396,403)),0,0,1-tween(f,399,403))
        if f>=381:
            x,y,r=self.track("sendCursor",f)
            cursor(im,x,y,r,1-tween(f,397,403),1.53)

    def calendar(self,im,f):
        cal=layer()
        d=ImageDraw.Draw(cal)
        left,y0,h=self.track("calendarCamera",f)
        right, = self.track("calendarRight", f)
        day_x, day_y = self.track("calendarDay", f)
        step = (right-left)/6.3
        first = day_x-5*step
        for j,(dow,num) in enumerate(zip("SMTWTFS",[16,17,18,19,20,21,23])):
            x=first+j*step
            dark=INK if 0<j<6 else "#9894a5"
            if num==21:
                oval(d,day_x,day_y,h*.335,h*.335,"#ef3046")
                dark="#fff"
            text(d,x,y0-h*1.30,dow,h*.17,INK,635,"center")
            text(d,x,(day_y-h*.15) if num==21 else y0-h*.74,str(num),h*.33,dark,555,"center")
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
        cursor(cal,x,y,r,tween(f,398,405),.98)
        if f>=self.at("calendar.mosaic"):
            panel_wipe(cal,self.s["calendarWipe"],f)
        a, = self.track("calendarArrivalOpacity",f)
        smear, = self.track("calendarArrivalSmear",f)
        if smear:
            cal = vertical_blur(cal,smear)
        composite(im,blur(cal,4.5*(1-tween(f,398,410))+2*tween(f,472,479)),
                  0,0,a*(1-tween(f,477,482)))

    def apps(self,im,f):
        phase,=self.track("orbitPhase",f)
        fade=1-tween(f,619,623)
        nodes=[]
        entrances={"rings":478,"red":479,"blue":479,"dark":481}
        lead = ("rings" if f<=478 else "red" if f<=533 else "dark" if f<=555
                else "rings" if f<=575 else "blue")
        for name,k in (("red",0),("dark",.25),("rings",.50),("blue",.75)):
            onset=entrances[name]
            if f<onset:
                continue
            depth=math.cos((k-phase)*math.tau)
            path=f"{name}Orbit" if name in ("red","blue") else f"{name}MeasuredOrbit"
            x,y,size=self.track(path,f)
            alpha=mix(.68,1,tween(f,onset,onset+2))*fade
            nodes.append((name==lead,depth,name,x,y,size,alpha))
        for _,depth,name,x,y,size,alpha in sorted(nodes):
            ox=app_icon(name)
            softness=(1-depth)*1.4+4*(1-tween(f,478,483))
            ox=blur(ox,softness)
            if f>=617:
                pad=64
                exposed=layer(ox.width,ox.height+2*pad)
                exposed.alpha_composite(ox,(0,pad))
                ox=vertical_blur(exposed,125*tween(f,616,621))
                frame_scale=size/ox.width
                composite(im,ox,x-size/2,y-(128+pad)*frame_scale,alpha,frame_scale)
            else:
                stamp(im,ox,x,y,size,alpha)

    def follow(self,im,f):
        x,y,s=self.track("followMeasuredCamera",f)
        contact=self.s["followContact"]
        plate=self.thread_plate("follow",f,543)
        no_frame=self.at("follow.no")
        yes_frame=self.at("follow.yes")
        a=mix(.79,1,tween(f,no_frame,653)) if f>=no_frame else 0
        b=mix(.72,1,tween(f,yes_frame,654)) if f>=yes_frame else 0
        tapped=tween(f,self.at("follow.yes-feedback")-1,690)
        self.chip(plate,45,433,72,29,self.c["follow"][4],False,.58+.42*a,a)
        left,top,width,height=contact["yesRect"]
        self.chip(plate,left,top,width,height,self.c["follow"][5],True,.58+.42*b,b,tapped)
        trail, = self.track("followExposure",f)
        softness=5*(1-tween(f,624,633))+2.2*max(0,1-abs(f-665)/7)+3*tween(f,690,696)
        self.expose_phone(im,plate,x,y,s,trail,softness)

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
        fields = tuple(self.track("closingWashFields", f))
        im.alpha_composite(measured_wash(fields))
        if f<766:
            shine,=self.track("badgeClosingHighlights",f)
            fitted_badge(im,self.track("closingMeasuredBox",f),52,5*(1-tween(f,696,704)),1,shine)
        else:
            y,=self.track("closingY",f)
            s,=self.track("closingSize",f)
            stamp(im,badge(52),500,y,s)
        d=ImageDraw.Draw(im)
        words=self.c["ending"]
        onset=[
            [self.at("ending.the"),self.at("ending.most"),self.at("ending.personal")],
            [self.at("ending.imessage"),self.at("ending.assistant"),self.at("ending.yet")]
        ]
        for j,row in enumerate(words):
            size=47 if j==0 else 48
            weight=515 if j==0 else 690
            if f<766:
                bounds=self.track(f"closingLine{j+1}",f)
                face=font(80,weight)
                width=face.getlength(" ".join(row))
                x,y,w,h=bounds
                for k,word in enumerate(row):
                    at=onset[j][k]
                    a=tween(f,at-1,at+5)
                    prefix=" ".join(row[:k])+(" " if k else "")
                    xi=x+w*face.getlength(prefix)/width
                    word_w=w*face.getlength(word)/width
                    fit_ink(im,word,(xi,y+12*(1-a),word_w,h),weight,a,4*(1-a))
                continue
            face=font(size,weight)
            x=500-face.getlength(" ".join(row))/2
            for k,word in enumerate(row):
                p=tween(f,onset[j][k]-1,onset[j][k]+6)
                if p:
                    tone=round(mix(248,20,p))
                    text(d,x,590+j*57+17*(1-p),word,size,(tone,tone,tone+min(6,255-tone)),weight)
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
        elif f<313:
            if f < 259:
                self.cluster(im,f)
            if f >= 258:
                self.profiles(im,f)
        elif f<403:
            self.sofia(im,f)
        if 478<=f<622:
            im.alpha_composite(measured_wash(tuple(self.track("measuredOrbitGlow",f))))
        if 397<=f<482:
            self.calendar(im,f)
        if 478<=f<622:
            self.apps(im,f)
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
