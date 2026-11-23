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


@lru_cache(maxsize=64)
def messages_font(size, weight=400):
    system_path = Path("/System/Library/Fonts/SFNS.ttf")
    if not system_path.is_file():
        return font(size, weight)
    face = ImageFont.truetype(system_path, max(1, round(size)))
    face.set_variation_by_axes([100, 28, 400, weight])
    return face


def oval(d, x, y, rx, ry, fill, **kw):
    d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=fill, **kw)


def heart(d, x, y, size, color):
    oval(d, x - size * .21, y - size * .15, size * .28, size * .26, color)
    oval(d, x + size * .21, y - size * .15, size * .28, size * .26, color)
    d.polygon([(x - size * .46, y - size * .035), (x, y + size * .48),
               (x + size * .46, y - size * .035)], fill=color)


def curve_polygon(draw, start, curves, color):
    """Fill a silhouette built from cubic segments."""
    points = [np.asarray(start)]
    for left, right, end in curves:
        anchor = points[-1]
        for t in np.linspace(0, 1, 13)[1:]:
            u = 1 - t
            points.append(u**3 * anchor + 3*u*u*t*np.asarray(left)
                          + 3*u*t*t*np.asarray(right) + t**3*np.asarray(end))
    draw.polygon([tuple(point) for point in points], fill=color)


@lru_cache(maxsize=24)
def curved_heart(width, height, tone, dark_tip=0):
    mask = Image.new("L", (300, 300))
    curve_polygon(ImageDraw.Draw(mask), (149, 64), (
        ((110, -4), (7, 5), (3, 97)),
        ((-3, 169), (84, 237), (143, 293)),
        ((147, 297), (153, 297), (157, 292)),
        ((216, 239), (305, 166), (296, 96)),
        ((290, 8), (192, 0), (149, 64)),
    ), 255)
    if dark_tip:
        y, x = np.mgrid[0:1:300j, 0:1:300j]
        rim = np.clip(np.abs(x-.5)*1.36 + (1-y)*.46, 0, 1)
        shade = np.clip((y-.13)/.87, 0, 1)**.94 * dark_tip
        center = np.array(tone)[None, None, :] + rim[..., None]*[2, 74, 11]
        rgb = center * (1-shade[..., None]) + np.array([74, 74, 77])*shade[..., None]
        im = Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).convert("RGBA")
    else:
        im = Image.new("RGBA", mask.size, tone)
    im.putalpha(mask)
    return im.resize((width, height), Image.Resampling.LANCZOS)


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
def sprite_portrait(key, base_color, disk_color, wink, lights=(), head_pose=()):
    """Place a generated head on an editable disk at the chosen shot scale."""
    low,high = (disk_color or base_color,base_color) if not lights else lights[:2]
    disk = rounded_gradient(256,256,low,high,128)
    variant = "lisa-wink" if key == "lisa" and wink else key
    path = Path(__file__).parent / "assets" / "portraits" / f"{variant}.png"
    with Image.open(path) as img:
        head = img.convert("RGBA")
    scale = min(188/head.width,198/head.height)
    if lights:
        scale *= lights[2]
    sx, sy, shift_x, shift_y, rotation = head_pose or (1,1,0,0,0)
    head = head.resize((round(head.width*scale*sx),round(head.height*scale*sy)),
                       Image.Resampling.LANCZOS)
    if rotation:
        head = head.rotate(rotation,Image.Resampling.BICUBIC,expand=True)
    composite(disk,head,(256-head.width)/2+shift_x,133-head.height/2+shift_y)
    if lights and key == "darla":
        d = ImageDraw.Draw(disk)
        for x, y, font_size, color in ((155,154,26,"#125a9c"),(173,133,32,"#136bad"),(193,108,39,"#147cc3")):
            d.text((x,y),"Z",font=messages_font(font_size,610),fill=color,anchor="lt")
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


@lru_cache(maxsize=2)
def compact_inbox_head(pose):
    """Draw the independently editable contacts used by the small inbox rows."""
    im = Image.new("RGBA",(256,256))
    d = ImageDraw.Draw(im)
    dark = pose == "glasses"
    hair = "#292b2c" if dark else "#686b6a"
    curve_polygon(d,(52,158),(
        ((61,143),(54,114),(58,93)), ((61,65),(85,42),(104,41)),
        ((125,47),(138,26),(157,39)), ((187,51),(185,72),(192,89)),
        ((199,105),(191,129),(195,148)), ((201,158),(201,169),(187,175)),
        ((145,183),(92,170),(70,178)), ((55,187),(46,178),(52,158)),
    ),hair)
    shadow = "#4c4641" if dark else "#8b8c85"
    d.arc((59,42,175,154),193,293,fill=shadow,width=9)
    oval(d,127,131,56,68,"#a57756")
    oval(d,128,127,50,63,"#d8aa83")
    oval(d,120,120,43,53,"#e0b591")
    shape = "#303233" if dark else "#797e7a"
    curve_polygon(d,(66,116),(
        ((62,87),(73,65),(95,55)), ((115,47),(146,55),(163,63)),
        ((184,59),(184,76),(188,91)), ((173,92),(140,89),(112,105)),
        ((89,110),(82,121),(79,148)), ((66,149),(59,142),(66,116)),
    ),shape)
    if dark:
        for x in (103,154):
            oval(d,x,129,26,23,"#332725")
            oval(d,x,128,20,17,"#e4c7ae")
            oval(d,x,129,13,9,"#f9ebdf")
            oval(d,x+1,131,5.2,6.4,"#3e3534")
        d.line((125,122,132,122),fill="#3a2b26",width=7)
    else:
        for x in (105,151):
            d.arc((x-15,108,x+15,135),193,346,fill="#70503f",width=6)
        oval(d,92,142,11,7,"#e8a79a")
        oval(d,164,143,11,7,"#e8a79a")
    oval(d,128,148,9,7,"#c59573")
    curve_polygon(d,(101,160),(
        ((114,167),(142,168),(155,158)),
        ((154,177),(141,184),(128,183)),
        ((116,183),(104,174),(101,160)),
    ),"#5d342b")
    d.arc((103,152,153,172),6,168,fill="#f7e4d3",width=6)
    if not dark:
        curve_polygon(d,(150,63),(
            ((154,62),(171,78),(181,96)), ((184,111),(191,125),(200,139)),
            ((184,140),(172,128),(163,116)), ((148,99),(142,80),(150,63)),
        ),"#a4a6a5")
        d.rounded_rectangle((166,164,203,220),19,fill="#c3946f")
        d.rounded_rectangle((175,135,189,194),7,fill="#d6a881")
        d.rounded_rectangle((190,149,203,192),7,fill="#e4b18b")
        oval(d,183,193,17,18,"#e2b392")
        d.arc((177,175,200,197),102,289,fill="#b18165",width=3)
    return im


@lru_cache(maxsize=40)
def badge(roundness, reveal=1, closing_finish=None, refined=False, raster_width=256, motif_scale=1):
    y, x = np.mgrid[0:1:512j, 0:1:512j]
    reflection = np.exp(-((x-.50)/.45)**2-((y+.11)/.27)**2)
    shine = (16,22,23) if closing_finish is None else closing_finish
    rgb = np.array([51, 51, 51]) + reflection[..., None]*shine
    face = Image.fromarray(np.uint8(rgb)).convert("RGBA")
    mask = Image.new("L", face.size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 511, 511), min(255, roundness*2), fill=255)
    motif = Image.new("RGBA", face.size)
    closing = closing_finish is not None
    ink = "#333333" if refined else "#333131"
    rear = Image.new("L", face.size)
    curve_polygon(ImageDraw.Draw(rear), (104, 197), (
        ((101, 188), (113, 184), (123, 181)),
        ((140, 174), (157, 168), (169, 164)),
        ((173, 163), (175, 166), (175, 171)),
        ((175, 225), (174, 281), (178, 308)),
        ((179, 321), (185, 329), (188, 344)),
        ((174, 340), (161, 333), (150, 325)),
        ((145, 321), (143, 316), (141, 309)),
        ((127, 267), (116, 229), (104, 197)),
    ), 255)
    rear_pigments = ((False, (255,230,195), (239,160,213)),
                     (True, (255,223,195), (244,158,218)))
    if closing:
        rear_pigments = ((False, (250,228,186), (247,173,219)),
                         (True, (251,217,187), (245,166,227)))
    if refined:
        rear = Image.new("L", face.size)
        curve_polygon(ImageDraw.Draw(rear), (104, 201),(
            ((102, 193), (107, 187), (119, 183)),
            ((138, 175), (155, 170), (168, 165)),
            ((172, 163), (177, 165), (177, 171)),
            ((177, 222), (175, 280), (180, 307)),
            ((181, 322), (188, 331), (189, 346)),
            ((174, 340), (160, 332), (151, 325)),
            ((145, 320), (144, 316), (141, 309)),
            ((128, 269), (113, 230), (105, 205)),
            ((104.5, 203.5), (104.1, 202.2), (104, 201)),
        ),255)
        rear_pigments = ((False, (250,231,187), (247,174,222)),
                         (True, (251,219,187), (247,172,229)))
    for right, top, bottom in rear_pigments:
        contour = rear.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if right else rear
        fade = np.clip((y*511-161)/192,0,1)
        rgb = np.array(top) + fade[...,None]*(np.array(bottom)-top)
        card = Image.fromarray(np.uint8(np.rint(rgb))).convert("RGBA")
        d = ImageDraw.Draw(card)
        cx = 351 if right else 159
        if refined:
            oval(d,cx+(.2 if right else .65),213.4,16.5,16.9,ink)
        elif closing:
            oval(d,cx+(1 if right else 1.5),214,16.3,16.4,ink)
        else:
            oval(d,cx,213,17,16,ink)
        side = -1 if right else 1
        shoulder = 5 if closing else 0
        curve_polygon(d,(cx-side*15,268+shoulder),(
            ((cx-side*20,257+shoulder),(cx-side*(17 if refined else 16),234 if refined else 235),(cx+side*22,229 if refined else 230)),
            ((cx+side*31,236),(cx+side*33,247+shoulder),(cx+side*33,252+shoulder)),
            ((cx+side*18,259+shoulder),(cx+side*1,265+shoulder),(cx-side*15,268+shoulder)),
        ),ink)
        card.putalpha(contour)
        if closing:
            # The angled rear cards sit inside the front card's outline.
            transform = (1.003,0,-.77,0,1.005,-.45)
            if refined:
                transform = (.996,0,1.2,0,1.002,-.45) if right else (1.003,0,-.77,0,1.003,-.45)
            scaled=card.transform(card.size,Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC)
            motif.alpha_composite(scaled)
        else:
            motif.alpha_composite(card)
    front = Image.new("RGBA",(160,206))
    ImageDraw.Draw(front).rounded_rectangle((0,0,159,205),25,fill=ink)
    ramp = np.interp(np.arange(195),[0,20,77,125,194],[0,.12,.40,.66,1])
    light = np.exp(-((np.arange(142)-66)/58)**2)
    if closing:
        rows,cols = np.mgrid[0:195,0:142]
        # Warm face illumination and rose at the bottom of the card.
        stops = (0,14,31,54,77,108,136,168,194)
        colors = ((248,237,193),(248,227,178),(248,216,164),
                  (247,203,163),(247,198,176),(247,192,190),
                  (246,179,195),(244,159,198),(244,153,205))
        pigment = np.stack([np.interp(rows,stops,c) for c in zip(*colors)],axis=2)
        if refined:
            pigment += np.exp(-((rows-87)/75)**2)[...,None]*[1.1,2.4,3.2]
        across = (cols-70)/70
        glow = 1-across**2
        depth = rows/194
        rgb = (pigment + across[...,None]*[-.5,-2.8,3.1] + glow[...,None]*[1.2,-1.6,-3.9]
               + (across*depth)[...,None]*[0,-5.6,-2.7] + (glow*depth)[...,None]*[.2,1.2,8.8])
    else:
        rgb = np.array([249,226,177])+ramp[:,None,None]*[-4,-74,34]
        rgb = rgb + light[None,:,None]*(1-ramp[:,None,None])*[6,12,4]
    colored = Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert("RGBA")
    contour = Image.new("L",colored.size)
    ImageDraw.Draw(contour).rounded_rectangle((0,0,141,194),19,fill=255)
    colored.putalpha(contour)
    composite(front,colored,9,4)
    d=ImageDraw.Draw(front)
    if closing:
        if refined:
            oval(d,80.0,49.2,21.65,22.7,ink)
        else:
            oval(d,80.5,49.5,20.9,21.25,ink)
        curve_polygon(d,(44,101),(
            ((50,70),(109,70),(114,101)),
            ((113,103),(84,103),(45,102)),
        ),ink)
        bars = ((109,116,8),(69,135.5,9)) if refined else ((108,116,8),(69,135,8))
        for width,row,height in bars:
            d.rounded_rectangle((26,row,26+width,row+height),4,fill=ink)
    else:
        oval(d,79,50,22,22,ink)
        curve_polygon(d,(43,103),(
            ((46,70),(111,65),(115,103)),
            ((114,105),(83,105),(44,104)),
        ),ink)
        for width, row in ((110,116),(71,135)):
            d.rounded_rectangle((26,row,26+width,row+9),4,fill=ink)
    front=front.rotate(.65,resample=Image.Resampling.BICUBIC,expand=True)
    composite(motif,front,255-front.width/2,230-front.height/2)
    if refined:
        composite(motif,curved_heart(136,118,(51,51,51)),187,280)
    else:
        composite(motif,curved_heart(146,123,(51,49,49)),182,277)
    heart_width = 121 if refined else 124
    heart_height = 118 if closing else 114
    bloom=curved_heart(heart_width,heart_height,(245,130,212))
    hy,hx=np.mgrid[0:1:complex(heart_height),0:1:complex(heart_width)]
    center = np.exp(-((hx-.50)/.36)**2-((hy-.45)/.33)**2)
    pigment_base = [249,161,221] if closing else [249,163,223]
    if refined:
        pigment_base = [249,163,216]
    pink=np.array(pigment_base)+center[...,None]*[-5,-44,-10]
    lower=np.clip((hy-.55)/.40,0,1)**1.45
    lower_glow = [2,35,26] if closing else [3,35,22]
    if refined:
        lower_glow = [2,34,35]
    pink+=lower[...,None]*lower_glow
    if refined:
        edges = abs(hx-.50)*np.exp(-((hy-.53)/.22)**2)
        pink += edges[...,None]*[.5,31,18]
    pigment=Image.fromarray(np.uint8(np.clip(np.rint(pink),0,255))).convert("RGBA")
    pigment.putalpha(bloom.getchannel("A"))
    composite(motif,pigment,(195 if refined else 194) if closing else 193,288)
    if reveal < 1:
        shade = np.interp(y, [.44, .57, .79], [1, 1, reveal])
        motif.putalpha(Image.fromarray(np.uint8(np.asarray(motif.getchannel("A"))*shade)))
    if motif_scale == 1:
        face.alpha_composite(motif)
    else:
        # Scale the editable cards and heart about the badge center.
        shift=(1-motif_scale)*motif.width/2
        composite(face,motif,shift,shift,1,motif_scale)
    face.putalpha(mask)
    return face.resize((raster_width, raster_width), Image.Resampling.LANCZOS)


def stamp(im, layer, x, y, s, opacity=1):
    composite(im,layer,x-s/2,y-s/2,opacity,s/layer.width)


@lru_cache(maxsize=16)
def app_icon(key):
    if key=="red":
        y,x=np.mgrid[0:1:256j,0:1:256j]
        corner=np.clip(y*(1.05-.78*x),0,1)
        colors = np.array([239,27,109]) + x[...,None]*[1,-4,9] + corner[...,None]*[14,78,-28]
        im=Image.fromarray(np.uint8(colors)).convert("RGBA")
        im.putalpha(rounded_gradient(256,256,"white","white",27).getchannel("A"))
    elif key=="blue":
        im=rounded_gradient(256,256,"#65b5ff","#367ef0",35)
    else:
        im=rounded_gradient(256,256,"#fdfdfd","#fdfdfd",53)
    d=ImageDraw.Draw(im)
    if key=="red":
        curve_polygon(d, (132, 30), (
            ((192, 56), (216, 105), (215, 149)),
            ((214, 201), (180, 229), (128, 229)),
            ((80, 228), (48, 195), (47, 154)),
            ((46, 120), (66, 95), (88, 74)),
            ((88, 94), (94, 103), (101, 107)),
            ((128, 99), (134, 62), (132, 30)),
        ), "#fffefe")

    elif key=="blue":
        d.rounded_rectangle((6,8,250,80),25,fill="#69b1fb")
        text(d,128,67,"31",157,"#fff",550,"center")
    elif key=="dark":
        ink = "#19191a"
        d.rectangle((49,37,78,218),fill=ink)
        d.rectangle((152,37,181,218),fill=ink)
        curve_polygon(d, (76, 130), (
            ((121, 78), (185, 138), (217, 92)),
            ((224, 96), (231, 100), (240, 105)),
            ((206, 163), (121, 125), (78, 150)),
            ((77, 144), (76, 137), (76, 130)),
        ), ink)
    else:
        for cx, edge_colors in (
            (99,((12,197,199),(100,27,169))),
            (159,((105,36,175),(207,0,140))),
        ):
            mask=Image.new("L",im.size)
            oval(ImageDraw.Draw(mask),cx,130,59,58,None,outline=255,width=9)
            yy,xx=np.mgrid[:256,:256]
            blend=np.clip(((xx-cx)/59-.45*(yy-130)/58+1)*.5,0,1)
            a,b=np.array(edge_colors)
            strand=Image.fromarray(np.uint8(a+blend[...,None]*(b-a))).convert("RGBA")
            strand.putalpha(mask)
            im.alpha_composite(strand)
    return im
