"""Original editable vector artwork drawn with Pillow."""
from functools import lru_cache
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np


@lru_cache(maxsize=180)
def font(size, weight=400):
    face = ImageFont.truetype(Path(__file__).parent / "assets/Inter.ttf", max(1, round(size)))
    face.set_variation_by_axes([min(32, max(14, size)), weight])
    return face


def oval(d, x, y, rx, ry, fill, **kw):
    d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=fill, **kw)


def heart(d, x, y, size, color):
    oval(d, x - size * .21, y - size * .15, size * .28, size * .26, color)
    oval(d, x + size * .21, y - size * .15, size * .28, size * .26, color)
    d.polygon([(x - size * .46, y - size * .035), (x, y + size * .48),
               (x + size * .46, y - size * .035)], fill=color)


def pictogram(d, name, x, y, s):
    if name in {"heart", "broken"}:
        heart(d, x, y, s, "#b51827" if name == "broken" else "#ec518a")
        if name == "broken":
            heart(d,x,y-.037*s,s*.88,"#e32f42")
            oval(d,x-.23*s,y-.23*s,.14*s,.075*s,"#ff8b91")
            oval(d,x+.20*s,y-.23*s,.14*s,.075*s,"#ff7983")
            d.line([(x+.07*s,y-.33*s),(x-.10*s,y-.04*s),(x+.03*s,y+.09*s),
                    (x-.065*s,y+.24*s),(x+.015*s,y+.46*s)],
                   fill="#fff3f2",width=max(1,round(.065*s)))
    elif name == "tongue":
        oval(d,x,y,.48*s,.46*s,"#eab223")
        oval(d,x,y-.08*s,.43*s,.36*s,"#ffd854")
        oval(d,x+.185*s,y-.085*s,.16*s,.18*s,"#fffcf1")
        oval(d,x+.23*s,y-.07*s,.066*s,.079*s,"#4c433d")
        d.arc((x-.33*s,y-.15*s,x-.08*s,y+.06*s),205,340,fill="#70472e",
              width=max(1,round(.07*s)))
        d.pieslice((x-.27*s,y-.04*s,x+.29*s,y+.40*s),0,180,fill="#70412d")
        oval(d,x+.044*s,y+.36*s,.13*s,.13*s,"#f4779b")
    elif name in {"cry", "wink", "cat"}:
        oval(d, x, y, .47*s, .46*s, "#ffd15a")
        if name == "cat":
            d.polygon([(x-.46*s,y-.21*s),(x-.40*s,y-.59*s),(x-.13*s,y-.35*s),
                       (x+.18*s,y-.36*s),(x+.40*s,y-.59*s),(x+.46*s,y-.21*s)],fill="#ffd15a")
        oval(d,x-.16*s,y-.07*s,.047*s,.065*s,"#44332d")
        if name == "wink":
            d.line((x+.10*s,y-.055*s,x+.23*s,y-.11*s),fill="#44332d",width=max(1,round(.07*s)))
        else:
            oval(d,x+.16*s,y-.07*s,.047*s,.065*s,"#44332d")
        oval(d,x,y+.16*s,.15*s,.096*s,"#6f3a3e")
        if name == "cry":
            for u in (-.17,.17):
                oval(d,x+u*s,y+.16*s,.045*s,.17*s,"#39bff6")
                oval(d,x+(u-.027)*s,y+.10*s,.016*s,.045*s,"#98edff")
        if name == "wink":
            oval(d,x+.06*s,y+.215*s,.094*s,.05*s,"#f980b5")
    elif name in {"plum", "drops"}:
        color = "#7b4eb1" if name == "plum" else "#56bbe9"
        oval(d,x,y,.33*s,.43*s,color)
        oval(d,x-.12*s,y-.21*s,.12*s,.10*s,"#9add75" if name == "plum" else "#b1effe")
    else:
        colors={"art":("#dba24d","#76c376"),"boot":("#735c49","#b69469"),"sushi":("#f17c63","#f3dac4")}
        a,b=colors.get(name,("#b581db","#c795ec"))
        d.rounded_rectangle((x-.426*s,y-.36*s,x+.426*s,y+.36*s), radius=max(1,round(s*.13)), fill=a)
        d.rounded_rectangle((x-.30*s,y-.13*s,x+.31*s,y+.23*s), radius=max(1,round(s*.08)), fill=b)


def advance(value, face, size):
    return sum(size for part in re.split(r"(\{\w+\})", value) if part.startswith("{")) + sum(
        face.getlength(part) for part in re.split(r"(\{\w+\})",value) if not part.startswith("{"))


def text(d, x, y, value, size, color="#17171d", weight=400, align="left", *, glyph=pictogram):
    face = font(size, weight)
    if align != "left":
        x -= advance(value, face, size) / (2 if align == "center" else 1)
    for part in re.split(r"(\{\w+\})", value):
        if part.startswith("{"):
            name = part[1:-1]
            offset, scale = (.66, .99) if name == "broken" else (.5, .82)
            glyph(d,name,x + size*offset,y+size*.54,size*scale)
            x += size
        elif part:
            d.text((x,y),part,font=face,fill=color,anchor="lt")
            x += face.getlength(part)


def composite(im, layer, x, y, opacity=1, scale=1):
    if opacity <= 0 or scale <= 0:
        return
    if scale != 1:
        size = tuple(max(1, round(v * scale)) for v in layer.size)
        layer = layer.resize(size, Image.Resampling.BICUBIC)
    if opacity < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda a: a * opacity))
    x, y = round(x), round(y)
    # Clip so large camera pushes do not allocate an image outside the stage.
    w, h = im.size
    a,b=max(0,-x),max(0,-y)
    c,e=min(layer.width,w-x),min(layer.height,h-y)
    if c>a and e>b:
        if (a,b,c,e)!=(0,0,*layer.size):
            layer=layer.crop((a,b,c,e))
        im.alpha_composite(layer,(x+a,y+b))


@lru_cache(maxsize=128)
def gradient(a,b,w,h,axis="y"):
    from PIL import ImageColor
    a=np.array(ImageColor.getrgb(a))
    b=np.array(ImageColor.getrgb(b))
    if axis=="y":
        t=np.linspace(0,1,h)[:,None,None]
        return Image.fromarray(np.broadcast_to((a+t*(b-a)).astype("uint8"),(h,w,3)).copy())
    t=np.linspace(0,1,w)[None,:,None]
    return Image.fromarray(np.broadcast_to((a+t*(b-a)).astype("uint8"),(h,w,3)).copy())


def rounded_gradient(w,h,a,b,r,axis="y"):
    im=gradient(a,b,w,h,axis).convert("RGBA")
    mask=Image.new("L",(w,h))
    ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=r,fill=255)
    im.putalpha(mask)
    return im


@lru_cache(maxsize=64)
def material(color, width, height, highlight):
    """Shade an independently authored ellipsoid and round its silhouette."""
    yy, xx = np.mgrid[-1:1:complex(height), -1:1:complex(width)]
    radius = np.sqrt(xx*xx + yy*yy)
    normal_z = np.sqrt(np.maximum(0, 1-radius*radius))
    key = np.clip(-.31*xx-.39*yy+.86*normal_z, 0, 1)
    gloss = np.maximum(0, normal_z-.36*xx-.44*yy)**7
    base = np.array(ImageColor.getrgb(color),float)
    rgb = base[None,None,:]*(.54+.60*key[:,:,None])+highlight*gloss[:,:,None]
    opacity = np.clip((1-radius)*min(width,height)/2+.5,0,1)*255
    return Image.fromarray(np.dstack((np.clip(rgb,0,255),opacity)).astype(np.uint8))


@lru_cache(maxsize=65)
def sprite_portrait(key, base_color, disk_color, wink):
    """Place a generated head on an editable disk at the chosen shot scale."""
    disk = rounded_gradient(256,256,disk_color or base_color,base_color,128)
    variant = "lisa-wink" if key == "lisa" and wink else key
    path = Path(__file__).parent / "assets" / "portraits" / f"{variant}.png"
    with Image.open(path) as img:
        head = img.convert("RGBA")
    scale = min(188/head.width,198/head.height)
    head = head.resize((round(head.width*scale),round(head.height*scale)), Image.Resampling.LANCZOS)
    composite(disk,head,(256-head.width)/2,133-head.height/2)
    disk.putalpha(rounded_gradient(256,256,base_color,base_color,128).getchannel("A"))
    return disk


@lru_cache(maxsize=90)
def portrait(spec, disk="", neutral=False):
    """Draw a stylized portrait from independent hair, face and expression parameters."""
    bg,skin,hair,blush,clothes,style,face=spec
    if neutral and face=="wink":
        face="smile"
    im=rounded_gradient(256,256,disk or bg,bg,128)
    d=ImageDraw.Draw(im)
    composite(im, material(hair, 153, 193 if style in {"long","braids"} else 166, 35), 51, 24)
    composite(im, material(clothes, 174, 106, 10), 41, 164)
    d.rounded_rectangle((110,150,146,202),12,fill=skin)
    d.arc((57,169,203,261),216,320,fill="#fff2ee",width=3)
    if style in {"long","braids","waves"}:
        for x in (70,183):
            d.rounded_rectangle((x-17,106,x+17,213 if style=="long" else 188),radius=14,fill=hair)
            if style=="braids":
                for y in (159,181,202):
                    oval(d,x+(3 if y==181 else 0),y,12,15,hair,outline=blush,width=1)
    oval(d,78,118,13,15,skin)
    oval(d,178,118,13,15,skin)
    composite(im, material(skin, 115, 130, 22), 70, 49)
    for x in (89, 149):
        spot = material(blush, 20, 12, 0)
        composite(im,spot,x,131,.40)
    if style=="sweep":
        d.polygon([(73,99),(83,52),(110,45),(159,40),(177,56),(189,99),(146,76),(109,73),(86,85)],fill=hair)
        d.arc((86,45,171,90),188,340,fill=skin,width=3)
    else:
        composite(im,material(hair,119,60,27),70,31)
        d.polygon([(73,68),(95,71),(84,119),(76,107)],fill=hair)
        d.polygon([(180,67),(171,71),(175,113),(186,99)],fill=hair)
        d.arc((83,40,178,87),203,341,fill=blush,width=3)
        if style=="waves":
            d.arc((89,49,162,91),199,330,fill=skin,width=3)
    for i,x in enumerate((105,151)):
        tilt=4 if face=="sad" and i==0 else 0
        d.arc((x-13,96+tilt,x+13,111-tilt),200,331,fill=hair,width=4)
        if face=="wink" and i==0:
            d.arc((x-11,112,x+10,125),9,168,fill="#432921",width=4)
        else:
            oval(d,x,116,12,8,"#fff3e9")
            composite(im,material("#554439",13,16,9),x-5,109)
            oval(d,x+2,115,1.7,1.7,"#fffdf9")
    composite(im,material(skin,15,20,19),120,119)
    if face in {"glasses","shades"}:
        for x in (105,151):
            oval(d,x,117,19,15,"#993e61" if face=="shades" else None,outline="#453944",width=3)
            if face=="shades":
                d.line((x-11,113,x+8,108),fill="#ffadc6",width=2)
        d.line((123,115,135,115),fill="#453944",width=3)
    if face=="sad":
        d.arc((115,149,141,164),187,354,fill="#8a4457",width=4)
    else:
        d.pieslice((114,142,144,164),0,180,fill="#783d4f")
        d.line((118,152,140,152),fill="#fff4e9",width=3)
    # Clip clothing and hair to the original portrait disk.
    im.putalpha(rounded_gradient(256,256,bg,bg,128).getchannel("A"))
    return im


@lru_cache(maxsize=16)
def badge(roundness):
    im=rounded_gradient(256,256,"#343536","#30302f",roundness)
    for x,y,angle,col in [(91,126,17,"#f5c69e"),(165,126,-17,"#efb6c1"),(128,110,0,"#f6d28d")]:
        card=rounded_gradient(64,94,col,"#eb9dc8",8)
        d=ImageDraw.Draw(card)
        oval(d,32,23,8,8,"#42352f")
        d.rounded_rectangle((14,34,50,48),6,fill="#42352f")
        d.rounded_rectangle((14,57,51,62),2,fill="#a0617a")
        d.rounded_rectangle((16,69,46,73),1,fill="#a0617a")
        card=card.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
        composite(im,card,x-card.width/2,y-card.height/2)
    d=ImageDraw.Draw(im)
    heart(d,128,167,68,"#6a3457")
    heart(d,128,165,54,"#ffc2eb")
    heart(d,128,166,45,"#f0a6db")
    return im


def stamp(im, layer, x, y, s, opacity=1):
    composite(im,layer,x-s/2,y-s/2,opacity,s/layer.width)


@lru_cache(maxsize=16)
def app_icon(key):
    if key=="red":
        im=rounded_gradient(256,256,"#f32e77","#fa6963",35)
    elif key=="blue":
        im=rounded_gradient(256,256,"#65b5ff","#367ef0",35)
    else:
        im=rounded_gradient(256,256,"#ffffff","#f0f0f9",42)
    d=ImageDraw.Draw(im)
    if key=="red":
        # Editable flame silhouette in local tile coordinates.
        points=[(123,47),(145,69),(163,92),(178,115),(181,137),(179,156),
                (172,172),(153,188),(134,196),(112,197),(94,190),(81,177),
                (74,163),(72,149),(75,131),(84,111),(96,96),(104,124),
                (113,117),(122,107),(128,94),(129,77)]
        d.polygon([(128+(x-128)*1.39,127+(y-127)*1.24) for x,y in points],fill="#fffefe")

    elif key=="blue":
        d.rounded_rectangle((6,8,250,80),25,fill="#69b1fb")
        text(d,128,67,"31",157,"#fff",550,"center")
    elif key=="dark":
        for box in [(56,42,89,217),(151,42,184,217),(78,111,180,145)]:
            d.rounded_rectangle(box,radius=9,fill="#202023")
        d.arc((133,67,225,140),1,82,fill="#212125",width=24)
    else:
        for cx,col in [(93,"#20abc8"),(158,"#a32cb5")]:
            oval(d,cx,127,51,54,None,outline=col,width=11)
    return im
