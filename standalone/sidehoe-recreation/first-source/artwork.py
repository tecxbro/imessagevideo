"""Original editable vector artwork drawn with Pillow."""
from functools import lru_cache
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont
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
        heart(d, x, y, s, "#ec518a")
        if name == "broken":
            d.line([(x+.09*s,y-.34*s),(x-.10*s,y-.03*s),(x+.06*s,y+.03*s),(x-.065*s,y+.33*s)],
                   fill="#fff2f6", width=max(1,round(.08*s)))
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


def text(d, x, y, value, size, color="#17171d", weight=400, align="left"):
    face = font(size, weight)
    if align != "left":
        x -= advance(value, face, size) / (2 if align == "center" else 1)
    for part in re.split(r"(\{\w+\})", value):
        if part.startswith("{"):
            pictogram(d,part[1:-1],x + size*.5,y+size*.54,size*.82)
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


@lru_cache(maxsize=90)
def portrait(spec, disk="", neutral=False):
    """Draw a stylized portrait from independent hair, face and expression parameters."""
    bg,skin,hair,blush,clothes,style,face=spec
    if neutral and face=="wink":
        face="smile"
    im=rounded_gradient(256,256,disk or bg,bg,128)
    d=ImageDraw.Draw(im)
    d.ellipse((56,27,204,214 if style in {"long","braids"} else 188),fill=hair)
    d.rounded_rectangle((53,168,207,271),36,fill=clothes)
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
    d.rounded_rectangle((81,51,176,174),radius=44,fill=skin)
    d.arc((81,53,176,173),9,157,fill=blush,width=2)
    oval(d,100,138,12,6,blush)
    oval(d,156,138,12,6,blush)
    if style=="sweep":
        d.polygon([(73,99),(83,52),(110,45),(159,40),(177,56),(189,99),(146,76),(109,73),(86,85)],fill=hair)
        d.arc((86,45,171,90),188,340,fill=skin,width=3)
    else:
        d.pieslice((75,31,185,110),180,360,fill=hair)
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
            oval(d,x,117,11,6,"#fff8ef")
            oval(d,x+1,117,5,6,"#372d34")
            oval(d,x+2,115,1.7,1.7,"#fffdf9")
    d.line((126,120,123,133,130,135),fill=blush,width=3,joint="curve")
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
    im=rounded_gradient(256,256,"#414149","#282832",roundness)
    for x,y,angle,col in [(80,123,18,"#edb6be"),(177,123,-18,"#f4bacd"),(128,114,0,"#f5cfac")]:
        card=rounded_gradient(71,88,col,"#eda5d1",11)
        d=ImageDraw.Draw(card)
        oval(d,36,23,9,9,"#443843")
        d.rounded_rectangle((19,36,52,49),6,fill="#443843")
        d.rounded_rectangle((19,56,53,60),2,fill="#7a4e63")
        d.rounded_rectangle((24,66,48,70),2,fill="#7a4e63")
        card=card.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
        composite(im,card,x-card.width/2,y-card.height/2)
    d=ImageDraw.Draw(im)
    heart(d,128,157,64,"#41343e")
    heart(d,128,157,53,"#f695d2")
    return im


def stamp(im, layer, x, y, s, opacity=1):
    composite(im,layer,x-s/2,y-s/2,opacity,s/layer.width)


@lru_cache(maxsize=16)
def app_icon(key):
    if key=="red":
        im=rounded_gradient(256,256,"#fc377a","#fa655f",35)
    elif key=="blue":
        im=rounded_gradient(256,256,"#69b5ff","#386cdb",35)
    else:
        im=rounded_gradient(256,256,"#ffffff","#f0f0f9",42)
    d=ImageDraw.Draw(im)
    if key=="red":
        d.polygon([(122,49),(151,76),(173,107),(180,139),(174,162),(151,188),(124,198),
                   (94,187),(77,169),(73,142),(77,119),(95,94),(104,126),(118,116),(128,89)],
                  fill="#ffffff")
        heart(d,126,164,58,"#ffd9e6")
    elif key=="blue":
        d.rounded_rectangle((45,46,211,82),11,fill="#a9dbff")
        d.line((77,38,77,68),fill="#fff",width=8)
        d.line((177,38,177,68),fill="#fff",width=8)
        text(d,128,94,"31",103,"#fff",620,"center")
    elif key=="dark":
        for box in [(64,55,89,198),(170,55,195,198),(78,118,185,144)]:
            d.rounded_rectangle(box,radius=12,fill="#312b3b")
        oval(d,195,131,8,8,"#af7db4")
    else:
        for cx,col in [(99,"#31bfd2"),(162,"#b05bc9")]:
            oval(d,cx,127,45,47,None,outline=col,width=12)
        oval(d,130,127,5,5,"#fc9cbe")
    return im
